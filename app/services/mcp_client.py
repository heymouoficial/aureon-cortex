import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCTool:
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str

class MCPClient:
    def __init__(self):
        self.settings = get_settings()
        self.config = self.settings.get_mcp_config()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.tools: Dict[str, MCTool] = {}

    async def start_server(self, name: str, config: Dict[str, Any]):
        """Starts an MCP server subprocess."""
        command = config.get("command")
        args = config.get("args", [])
        env = os.environ.copy()
        env.update(config.get("env", {}))

        logger.info(f"Starting MCP server: {name} with command: {command} {args}")
        
        try:
            process = subprocess.Popen(
                [command] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=0  # Unbuffered
            )
            self.processes[name] = process
            logger.info(f"MCP server {name} started successfully.")
            return process
        except Exception as e:
            logger.error(f"Failed to start MCP server {name}: {e}")
            return None

    async def initialize_servers(self):
        """Initializes all configured MCP servers."""
        servers = self.config.get("mcpServers", {})
        for name, config in servers.items():
            await self.start_server(name, config)
            # Future: specialized handshake/initialization if needed
            
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Queries a server for its available tools via standard MCP JSON-RPC protocol.
        Note: This is a simplified implementation. Real MCP protocol is more complex.
        For MVP, we assume the server is ready to accept requests.
        """
        process = self.processes.get(server_name)
        if not process:
            logger.error(f"Server {server_name} not running.")
            return []

        # JSON-RPC request for tools/list
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            # Send request
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            # Read response (blocking for simplicity in MVP, should be async)
            response_line = process.stdout.readline()
            if not response_line:
                return []
                
            response = json.loads(response_line)
            if "result" in response and "tools" in response["result"]:
                tools_data = response["result"]["tools"]
                return tools_data
            
            return []
        except Exception as e:
            logger.error(f"Error communicating with {server_name}: {e}")
            return []

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Calls a tool on a specific MCP server."""
        process = self.processes.get(server_name)
        if not process:
            return {"error": "Server not running"}

        request = {
            "jsonrpc": "2.0",
            "id": 2, # UUID in prod
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            response = json.loads(response_line)
            return response.get("result", {})
        except Exception as e:
            return {"error": str(e)}

    def cleanup(self):
        """Terminates all server processes."""
        for name, process in self.processes.items():
            logger.info(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

# Singleton instance
mcp_client = MCPClient()
