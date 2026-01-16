import asyncio
import io
import os
import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from typing import Optional
from loguru import logger
from app.core.config import get_settings
import edge_tts

settings = get_settings()

# Import the Multi-Agent Router
from app.agentes import aureon_cortex


def escape_markdown(text: str) -> str:
    """
    Helper to escape characters for Telegram Markdown (legacy style).
    This is less strict than MarkdownV2 but still risky. 
    However, most LLMs generate standard markdown which works well with 'Markdown' mode
    as long as we handle major breakers. 
    
    Actually, for simple formatting like **bold** and *italic*, 'Markdown' mode is often safer 
    than 'MarkdownV2' without heavy escaping. We will trust the LLM output for now and fallback.
    """
    return text


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command, including Deep Linking for Group Onboarding."""
    if not update or not update.message or not update.effective_user:
        return

    user = update.effective_user
    chat = update.effective_chat
    args = context.args

    # 1. Group Onboarding Logic (via Deep Linking)
    if chat.type in ["group", "supergroup"]:
        # Check if user is Admin/Whitelisted to authorize group
        if settings.ALLOWED_TELEGRAM_IDS and user.id in settings.ALLOWED_TELEGRAM_IDS:
             # Authorization Logic (Simplified: If Admin adds me, I stay)
             logger.info(f"🟢 Aureon añadido a grupo {chat.title} ({chat.id}) por Admin {user.username}")
             await update.message.reply_text(
                 f"🧠 **Modo Grupo Activado**\n\nHola equipo. Soy Aureon.\nEstoy listo para asistir en {chat.title}.",
                 parse_mode="Markdown"
             )
             # TODO: Persist Group ID in whitelist/database
             return
        else:
             # Unauthorized start in group
             logger.warning(f"🔴 Intento de start en grupo por usuario no autorizado: {user.id}")
             # We might stay silent or leave. For now, silent.
             return

    # 2. Private Chat Logic (Strict Whitelist)
    user_id = update.effective_user.id
    if settings.ALLOWED_TELEGRAM_IDS and user_id not in settings.ALLOWED_TELEGRAM_IDS:
        logger.warning(f"Unauthorized user {user_id} tried to use /start command.")
        await update.message.reply_text("⛔ Acceso denegado. Sistema Privado de Elevate Marketing.")
        return

    logger.info(f"User {user.username} started Aureon (Private).")

    try:
        await update.message.reply_html(
            rf"Hola {user.mention_html()}! 🤙"
            "\n\nSoy <b>Aureon</b>. Estoy listo para ayudarte con todo:"
            "\n📧 Correos y Agendas"
            "\n🧠 Estrategia e Ideas"
            "\n🔎 Datos de Clientes (RAG)"
            "\n\n¿Por dónde empezamos hoy?"
        )
    except Exception as e:
        logger.exception(f"Error sending start message: {e}")
        await update.message.reply_text("Hola! Soy Aureon. ¿En qué te ayudo?")


async def handle_multimodal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text, voice, and image messages with improved UX."""
    if not update or not update.message or not update.effective_user:
        logger.warning("Invalid update received in handle_multimodal")
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    status_msg = None

    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        text_content = update.message.text or update.message.caption or ""

        # 🔒 SECURITY CHECK (WHITELIST & GROUPS)
        is_private = update.effective_chat.type == "private"
        allowed_ids = getattr(settings, 'ALLOWED_TELEGRAM_IDS', [])
        is_authorized_user = allowed_ids and user_id in allowed_ids
        
        if is_private and not is_authorized_user:
            logger.warning(f"⛔ Acceso denegado: Usuario {username} ({user_id}) intentó usar el bot privado.")
            return

        # In groups, we reply if:
        # A) Mentioned directly (@botname) OR
        # B) Replying to a message from the bot OR
        # C) User is whitelisted Admin (Optional: allows seamless chat for Admins in groups)
        # For now, let's keep it simple: If in group, strict whitelist check on WHO is talking?
        # User constraint: "Solo recibirás mensajes que sean comandos o que mencionen explícitamente..." via BotFather.
        # So we process everything we RECEIVE.
        
        # Security: In a group, we should only process if the SPEAKER is whitelisted? 
        # Or if the GROUP is trusted?
        # Current Logic: Only Whitelisted USERS can interact, anywhere.
        if not is_authorized_user:
            # Silent ignore in groups to avoid spamming "Access Denied"
            return

        logger.info(f"📩 Mensaje de {username} ({user_id}): {text_content[:50]}...")

        # Send status message for better UX
        status_msg = await context.bot.send_message(
            chat_id=chat_id, 
            text="🧠 Aureon está procesando tu solicitud..."
        )

        text = update.message.text or update.message.caption or ""
        attachments = []

        # 1. Handle Photos
        if update.message.photo:
            photo = update.message.photo[-1]  # Highest resolution
            file = await context.bot.get_file(photo.file_id)
            img_bytes = io.BytesIO()
            await file.download_to_memory(img_bytes)
            attachments.append({
                "type": "image",
                "data": img_bytes.getvalue(),
                "mime_type": "image/jpeg",
            })
            logger.info(f"Image received from {username}")

        # 2. Handle Voice
        if update.message.voice:
            file = await context.bot.get_file(update.message.voice.file_id)
            voice_bytes = io.BytesIO()
            await file.download_to_memory(voice_bytes)
            attachments.append({
                "type": "audio",
                "data": voice_bytes.getvalue(),
                "mime_type": "audio/ogg",
            })
            logger.info(f"Voice note received from {username}")

        # 3. Process through Aureon Cortex (Multi-Agent Router)
        wants_voice_response = bool(update.message.voice)

        ctx = {"userName": username, "source": "telegram", "user_id": user_id}
        
        # Route through Aureon Cortex
        answer_text = await aureon_cortex.route(text, context=ctx, attachments=attachments)

        # 4. Delete status message and reply with actual response
        if status_msg:
            await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)

        if wants_voice_response:
            try:
                # Generate Audio using Edge-TTS (Neutral Deep Male)
                voice_name = "es-US-AlonsoNeural"
                communicate = edge_tts.Communicate(answer_text, voice_name)

                # Use a unique name for concurrent requests
                temp_audio = f"voice_{user_id}.mp3"
                await communicate.save(temp_audio)

                with open(temp_audio, "rb") as voice_file:
                    await update.message.reply_voice(
                        voice=voice_file, 
                        caption=escape_markdown(answer_text[:1000]),
                        parse_mode="Markdown"
                    )

                os.remove(temp_audio)
            except Exception as e:
                logger.error(f"TTS error: {e}")
                await update.message.reply_text(answer_text, parse_mode="Markdown")
        else:
            # Smart Markdown Reply
            try:
                await update.message.reply_text(answer_text, parse_mode="Markdown")
            except Exception as e:
                # Fallback to plain text if Markdown fails (common with unescaped chars)
                logger.warning(f"Markdown failed, falling back to plain text: {e}")
                await update.message.reply_text(answer_text)

    except Exception as e:
        error_str = str(e)
        logger.exception(f"Error in handle_multimodal: {e}")
        
        # Determine error message based on type
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            error_text = "🚀 ¡Demasiada energía! Mis llaves de IA necesitan un respiro. Reintenta en 30s."
        else:
            error_text = "😔 Tuve un problema procesando tu mensaje. Por favor intenta de nuevo."
        
        # Edit status message or send new message
        if status_msg:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg.message_id,
                    text=error_text
                )
            except:
                await update.message.reply_text(error_text)
        elif update.message:
            await update.message.reply_text(error_text)




async def init_telegram_bot() -> Optional[Application]:
    """Initialize the Telegram bot application without starting polling."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not found. Telegram bot will not start.")
        return None

    # Ensure ALLOWED_TELEGRAM_IDS is treated safely
    allowed_ids = getattr(settings, 'ALLOWED_TELEGRAM_IDS', [])
    if not isinstance(allowed_ids, list):
        allowed_ids = []
        logger.warning("ALLOWED_TELEGRAM_IDS configured incorrectly. Defaulting to empty whitelist.")
    
    if not allowed_ids:
        logger.warning("ALLOWED_TELEGRAM_IDS is empty. No user whitelist will be enforced.")
    else:
        logger.info(f"Telegram bot will only respond to IDs: {allowed_ids}")

    try:
        # Build the application
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("id", id_command))
        
        # Unified handler for Text, Photo, Voice
        multimodal_filter = (
            filters.TEXT | filters.PHOTO | filters.VOICE | filters.CAPTION
        )
        application.add_handler(
            MessageHandler(multimodal_filter & (~filters.COMMAND), handle_multimodal)
        )
        
        # Initialize the app (loads plugins, etc.)
        await application.initialize()
        
        logger.info("🤖 Telegram Bot Initialized (Ready for Webhooks/Polling)")
        return application

    except Exception as e:
        logger.exception(f"❌ Failed to initialize Telegram bot: {e}")
        return None

async def set_telegram_webhook(application: Application, webhook_url: str):
    """Set the webhook for the Telegram bot."""
    if not application:
        return
    try:
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"🔗 Webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")

async def process_webhook_update(application: Application, data: dict):
    """Process an update received via webhook."""
    try:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"❌ Error processing webhook update: {e}")


async def stop_telegram_bot(application):
    """Stop the Telegram bot."""
    if application and hasattr(application, "updater"):
        try:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            logger.info("✅ Telegram Bot stopped successfully.")
        except Exception as e:
            logger.exception(f"❌ Error stopping Telegram bot: {e}")
