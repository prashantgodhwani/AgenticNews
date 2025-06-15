import aiohttp
import logging
import os

async def send_telegram_message(message):
    """Send a message to a Telegram chat using a bot asynchronously."""
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
    data = {"chat_id": os.environ['TELEGRAM_CHAT_ID'], "text": message }
    print(data)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response.raise_for_status()
                logging.info("Telegram message sent.")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
