import asyncio
import os
import sys
from loguru import logger

# Add the parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.telegram_bot import init_telegram_bot
from app.core.config import get_settings


async def test_telegram_bot():
    """Test Telegram bot startup independently."""
    logger.info("🔧 Testing Telegram bot startup locally...")

    settings = get_settings()

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in settings!")
        return False

    logger.info(f"✅ Token found: {settings.TELEGRAM_BOT_TOKEN[:20]}...")

    try:
        # Test token validity first with HTTP request
        import httpx

        test_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"

        logger.info(f"🔍 Testing token validity: {test_url}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(test_url)
            if response.status_code != 200:
                logger.error(f"❌ Invalid Telegram bot token: {response.text}")
                return False

            bot_info = response.json()
            bot_username = bot_info.get("result", {}).get("username", "Unknown")
            logger.info(f"✅ Telegram bot validated: @{bot_username}")

        # Start the bot
        logger.info("🚀 Starting Telegram bot...")
        application = await init_telegram_bot()
        if application:
            await application.start()
            # In long polling mode (local test), we usually need to start polling
            # but for a simple "init" test, just starting the app is enough.

        if application:
            logger.success("✅ Telegram bot started successfully!")
            logger.info("📱 Bot should now be responding to messages...")

            # Keep it running for testing
            try:
                logger.info("⏰ Keeping bot alive for 60 seconds for testing...")
                await asyncio.sleep(60)
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")

            # Cleanup
            from app.services.telegram_bot import stop_telegram_bot

            await stop_telegram_bot(application)
            logger.info("✅ Bot stopped cleanly")
            return True
        else:
            logger.error("❌ Failed to start Telegram bot")
            return False

    except Exception as e:
        logger.exception(f"❌ Error in test_telegram_bot: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Starting Telegram Bot Local Test...")
    success = asyncio.run(test_telegram_bot())
    if success:
        print("✅ Test completed successfully")
    else:
        print("❌ Test failed")
