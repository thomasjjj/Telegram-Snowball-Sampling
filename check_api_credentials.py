#!/usr/bin/env python3
"""
Check and validate Telegram API credentials defined in a .env file.

The script loads the credentials, reports their presence and format, and can optionally
test a connection to the Telegram API.
"""

import os
import asyncio
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_env_file() -> bool:
    """Check if .env file exists and load it"""
    env_path = '.env'

    if not os.path.exists(env_path):
        logger.error("Error: %s file not found!", env_path)
        logger.error("Please create a .env file with your Telegram API credentials.")
        logger.error("Run the main.py script to automatically create one or manually copy example_config.env to .env")
        return False

    # Load environment variables from .env
    load_dotenv(env_path, override=True)
    logger.info("Successfully loaded %s file.", env_path)

    return True


def display_api_credentials() -> bool:
    """Display API credentials from the .env file"""
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')

    logger.info("\n==== Telegram API Credentials ====")

    if not api_id:
        logger.warning("API ID: NOT FOUND")
    else:
        logger.info("API ID: %s", api_id)

    if not api_hash:
        logger.warning("API Hash: NOT FOUND")
    else:
        # Show first 3 and last 3 characters of hash for security
        api_hash_masked = api_hash[:3] + "..." + api_hash[-3:] if len(api_hash) > 6 else "INVALID"
        logger.info("API Hash: %s", api_hash_masked)

    if api_id and api_hash:
        logger.info("\n✅ Both API ID and API Hash are present in the .env file.")
    else:
        logger.error("\n❌ API credentials are missing or incomplete in the .env file.")

    return bool(api_id and api_hash)


def check_api_id_format(api_id: str | None) -> bool:
    """Check if the API ID is in the correct format (numeric)"""
    if not api_id:
        return False

    if not api_id.isdigit():
        logger.warning("\n⚠️ Warning: API ID '%s' is not numeric.", api_id)
        logger.warning("The API ID should be a number. Please check your .env file.")
        return False

    logger.info("\n✅ API ID format is valid (numeric).")
    return True


async def test_telegram_connection() -> bool:
    """Test connection to Telegram API"""
    try:
        # Only import Telethon if needed
        from telethon import TelegramClient

        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')

        if not api_id or not api_hash:
            logger.error("\n❌ Cannot test connection: API credentials missing.")
            return False

        # Convert API ID to integer
        api_id = int(api_id) if api_id.isdigit() else api_id

        logger.info("\nTesting connection to Telegram API...")
        logger.info("(This will create a session file in the current directory)")

        # Create a client
        client = TelegramClient("test_session", api_id, api_hash)

        # Connect without starting a full session
        await client.connect()
        is_connected = await client.is_user_authorized()

        if is_connected:
            logger.info("\n✅ Successfully connected to Telegram API and authorized!")
        else:
            logger.warning("\n⚠️ Connected to Telegram API but not authorized.")
            logger.warning(
                "This is normal if you haven't logged in yet. The main script will handle authorization."
            )

        # Disconnect
        await client.disconnect()
        return True

    except ImportError:
        logger.error("\n❌ Telethon library not installed. Cannot test connection.")
        logger.info("Install it with: pip install telethon")
        return False

    except Exception as e:
        logger.error("\n❌ Error connecting to Telegram API: %s", e)
        logger.error("Please check your API credentials and internet connection.")
        return False


def inspect_env_file() -> None:
    """Inspect the .env file contents (without showing full credentials)"""
    env_path = '.env'

    if not os.path.exists(env_path):
        return

    logger.info("\n==== .env File Content (Masked) ====")
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    logger.info(line)
                elif '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'TELEGRAM_API_ID':
                        logger.info("%s=%s", key, value)
                    elif key == 'TELEGRAM_API_HASH' and value:
                        logger.info("%s=%s", key, value[:3] + '...' + (value[-3:] if len(value) > 3 else ''))
                    else:
                        logger.info("%s=%s", key, value)
                else:
                    logger.info(line)
    except Exception as e:
        logger.error("Error reading .env file: %s", e)


def suggest_fixes() -> None:
    """Suggest fixes for common issues"""
    logger.info("\n==== Suggestions ====")
    logger.info("1. Make sure your .env file is in the correct location (in the project root directory).")
    logger.info("2. Ensure that TELEGRAM_API_ID and TELEGRAM_API_HASH are set correctly in the .env file.")
    logger.info("3. Check that there are no spaces around the '=' sign in your .env file.")
    logger.info("4. Verify that the API ID is a number and the API Hash is a string of letters and numbers.")
    logger.info("5. If you need new API credentials, visit https://my.telegram.org/auth and create a new application.")
    logger.info("6. Run the main.py script to create a new .env file automatically.")


async def main() -> None:
    """Main function"""
    logger.info("=== Telegram API Credentials Checker ===\n")

    # Check .env file
    if not check_env_file():
        return

    # Display API credentials
    has_credentials = display_api_credentials()

    # Check API ID format
    api_id = os.getenv('TELEGRAM_API_ID')
    if api_id:
        check_api_id_format(api_id)

    # Inspect .env file
    inspect_env_file()

    # Ask if user wants to test connection
    if has_credentials:
        test_connection = input("\nDo you want to test the connection to Telegram API? (y/n): ")
        if test_connection.lower() in ('y', 'yes'):
            await test_telegram_connection()

    # Suggest fixes if there are issues
    if not has_credentials or not check_api_id_format(api_id):
        suggest_fixes()

    logger.info("\n=== Check Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
