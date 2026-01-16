
import fs from 'fs';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- Configuration ---
const PROJECT_ROOT = path.resolve(__dirname, '../../'); // multiversa-lab
const CHUNK_SIZE = 1000;
const DELAY_MS = 500; // Rate limit protection

// Directories to scan (Relative to PROJECT_ROOT)
const SCAN_PATHS = [
    'CalculaTu/src', // Assuming src exists, or we check specific folders
    'CalculaTu/hooks',
    'CalculaTu/services',
    'CalculaTu/types',
    'CalculaTu/conductor',
    'portality/components',
    'portality/hooks',
    'portality/services',
    'portality/types',
    'portality/conductor',
    'portality/marketing', // e.g., funnel docs
    'context',
    'conductor'
];

// Single files to scan
const SCAN_FILES = [
    'README.md',
    'CalculaTu/package.json',
    'portality/package.json',
    'portality/vectorizar/FUNNEL ASESORIA.md',
    'portality/vectorizar/Landing Asesoria.md', 
    'portality/vectorizar/Notion agencia propuesta.md',
    'portality/vectorizar/¿Qué es ÁGORA y cómo funciona.md'
];

// Ignored patterns
const IGNORE_PATTERNS = [
    'node_modules',
    '.git',
    'dist',
    '.DS_Store',
    '.env',
    'pnpm-lock.yaml',
    'yarn.lock',
    'package-lock.json',
    '*.png',
    '*.jpg',
    '*.jpeg',
    '*.gif',
    '*.svg',
    '*.ico',
    '*.woff',
    '*.woff2'
];

// --- Helpers ---

// Manual .env parser
function loadEnv(relativePath: string) {
    const envPath = path.resolve(__dirname, relativePath);
    if (!fs.existsSync(envPath)) return {};
    console.log(`Loading env from ${envPath}`);
    const content = fs.readFileSync(envPath, 'utf-8');
    const env: Record<string, string> = {};
    content.split('\n').forEach(line => {
        const match = line.match(/^([^#=]+)=(.*)$/); // Extract key=value, ignore comments
        if (match) {
            const key = match[1].trim();
            const value = match[2].trim().replace(/^["'](.*)["']$/, '$1'); // Remove quotes
            env[key] = value;
        }
    });
    return env;
}

const env = loadEnv('../.env.local');
const SUPABASE_URL = env.VITE_SUPABASE_URL;
const SUPABASE_KEY = env.SUPABASE_SERVICE_ROLE_KEY || env.VITE_SUPABASE_SERVICE_ROLE_KEY || env.VITE_SUPABASE_ANON_KEY || env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY;
const GEMINI_KEY = env.VITE_GEMINI_API_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY || !GEMINI_KEY) {
    console.error('❌ Missing environment variables in .env.local');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
const genAI = new GoogleGenerativeAI(GEMINI_KEY);
const model = genAI.getGenerativeModel({ model: 'text-embedding-004' });

// --- Logic ---

async function embedText(text: string) {
    try {
        const result = await model.embedContent(text);
        return result.embedding.values;
    } catch (e) {
        console.error('Embedding error:', e);
        return null;
    }
}

function chunkText(text: string): string[] {
    // Simple chunking by paragraph or length
    const chunks: string[] = [];
    let currentChunk = '';
    
    const lines = text.split('\n');
    for (const line of lines) {
        if ((currentChunk.length + line.length) > CHUNK_SIZE) {
            chunks.push(currentChunk);
            currentChunk = '';
        }
        currentChunk += line + '\n';
    }
    if (currentChunk.trim().length > 0) chunks.push(currentChunk);
    
    // Filter too small chunks
    return chunks.filter(c => c.length > 50);
}

async function ingestFile(filePath: string) {
    const relativePath = path.relative(PROJECT_ROOT, filePath);
    console.log(`📄 Processing: ${relativePath}`);
    
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const chunks = chunkText(content);
        
        if (chunks.length === 0) return;

    // 4. Ingest file into Supabase
    // Reverting to 'knowledge_sources' as existing schema enforces FK to it
    // Using simple upsert (ID = relativePath) to satisfy 'text' FK
        
    const sourceId = relativePath; // Using path as ID for simplicity/stability

    const { error: sourceError } = await supabase.from('knowledge_sources').upsert(
      {
        id: sourceId,
        name: path.basename(filePath), // Fixed: 'title' does not exist, trying 'name'
        type: 'file', // 'type' vs 'file_type'
        content: content,
        metadata: {
          path: relativePath,
          last_modified: new Date().toISOString()
        },
        // status: 'active', // REMOVED: Column does not exist
        organization_id: '392ecec2-e769-4db2-810f-ccd5bd09d92a'
      },
      { onConflict: 'id' }
    );

    if (sourceError) {
        console.error(`Error upserting source ${relativePath}:`, sourceError);
        return;
    }

    // 2. Delete old chunks
    await supabase.from('document_chunks').delete().eq('source_id', sourceId);

    // 3. Vectorize Chunks
    for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        const embedding = await embedText(chunk);
        
        if (embedding) {
            const { error: chunkError } = await supabase.from('document_chunks').insert({
                source_id: sourceId,
                organization_id: '392ecec2-e769-4db2-810f-ccd5bd09d92a',
                content: chunk,
                embedding,
                metadata: { index: i, source: relativePath }
            });
                if (chunkError) {
                console.error('Error inserting chunk:', chunkError);
            } else {
                process.stdout.write('.');
            }
        }
        await new Promise(r => setTimeout(r, DELAY_MS));
    }
    console.log(' ✅');

    } catch (e) {
        console.error(`Error reading file ${filePath}:`, e);
    }
}

function shouldIgnore(entryName: string) {
    return IGNORE_PATTERNS.some(pattern => {
        if (pattern.startsWith('*.')) {
            return entryName.endsWith(pattern.slice(1));
        }
        return entryName === pattern;
    });
}

async function scanDirectory(dirPath: string) {
    if (!fs.existsSync(dirPath)) return;
    
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    
    for (const entry of entries) {
        if (shouldIgnore(entry.name)) continue;

        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
            await scanDirectory(fullPath);
        } else if (entry.isFile()) {
            await ingestFile(fullPath);
        }
    }
}

async function main() {
    console.log('🚀 Starting Aureon Ingestion Protocol...');
    console.log(`Root: ${PROJECT_ROOT}`);

    // Process explicit files
    for (const fileRel of SCAN_FILES) {
        const fullPath = path.join(PROJECT_ROOT, fileRel);
        if (fs.existsSync(fullPath)) {
            await ingestFile(fullPath);
        } else {
            console.warn(`⚠️ File not found: ${fileRel}`);
        }
    }

    // Process directories
    for (const dirRel of SCAN_PATHS) {
        const fullPath = path.join(PROJECT_ROOT, dirRel);
        await scanDirectory(fullPath);
    }

    console.log('\n✨ Ingestion Complete.');
}

main().catch(console.error);
