#!/usr/bin/env python3
"""
Telegram API Credentials Checker

This script checks if your Telegram API credentials are correctly set up in the .env file.
It will attempt to load the credentials, display their values, and optionally test a connection
to the Telegram API.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_env_file():
    """Check if .env file exists and load it"""
    env_path = '.env'

    if not os.path.exists(env_path):
        print(f"Error: {env_path} file not found!")
        print("Please create a .env file with your Telegram API credentials.")
        print("Run the main.py script to automatically create one or manually copy example.env to .env")
        return False

    # Load environment variables from .env
    load_dotenv(env_path, override=True)
    print(f"Successfully loaded {env_path} file.")

    return True


def display_api_credentials():
    """Display API credentials from the .env file"""
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')

    print("\n==== Telegram API Credentials ====")

    if not api_id:
        print("API ID: NOT FOUND")
    else:
        print(f"API ID: {api_id}")

    if not api_hash:
        print("API Hash: NOT FOUND")
    else:
        # Show first 3 and last 3 characters of hash for security
        api_hash_masked = api_hash[:3] + "..." + api_hash[-3:] if len(api_hash) > 6 else "INVALID"
        print(f"API Hash: {api_hash_masked}")

    if api_id and api_hash:
        print("\n✅ Both API ID and API Hash are present in the .env file.")
    else:
        print("\n❌ API credentials are missing or incomplete in the .env file.")

    return api_id and api_hash


def check_api_id_format(api_id):
    """Check if the API ID is in the correct format (numeric)"""
    if not api_id:
        return False

    if not api_id.isdigit():
        print(f"\n⚠️ Warning: API ID '{api_id}' is not numeric.")
        print("The API ID should be a number. Please check your .env file.")
        return False

    print(f"\n✅ API ID format is valid (numeric).")
    return True


async def test_telegram_connection():
    """Test connection to Telegram API"""
    try:
        # Only import Telethon if needed
        from telethon import TelegramClient

        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')

        if not api_id or not api_hash:
            print("\n❌ Cannot test connection: API credentials missing.")
            return False

        # Convert API ID to integer
        api_id = int(api_id) if api_id.isdigit() else api_id

        print("\nTesting connection to Telegram API...")
        print("(This will create a session file in the current directory)")

        # Create a client
        client = TelegramClient("test_session", api_id, api_hash)

        # Connect without starting a full session
        await client.connect()
        is_connected = await client.is_user_authorized()

        if is_connected:
            print("\n✅ Successfully connected to Telegram API and authorized!")
        else:
            print("\n⚠️ Connected to Telegram API but not authorized.")
            print("This is normal if you haven't logged in yet. The main script will handle authorization.")

        # Disconnect
        await client.disconnect()
        return True

    except ImportError:
        print("\n❌ Telethon library not installed. Cannot test connection.")
        print("Install it with: pip install telethon")
        return False

    except Exception as e:
        print(f"\n❌ Error connecting to Telegram API: {e}")
        print("Please check your API credentials and internet connection.")
        return False


def inspect_env_file():
    """Inspect the .env file contents (without showing full credentials)"""
    env_path = '.env'

    if not os.path.exists(env_path):
        return

    print("\n==== .env File Content (Masked) ====")
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    print(line)
                elif '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'TELEGRAM_API_ID':
                        print(f"{key}={value}")
                    elif key == 'TELEGRAM_API_HASH' and value:
                        print(f"{key}={value[:3]}...{value[-3:] if len(value) > 3 else ''}")
                    else:
                        print(f"{key}={value}")
                else:
                    print(line)
    except Exception as e:
        print(f"Error reading .env file: {e}")


def suggest_fixes():
    """Suggest fixes for common issues"""
    print("\n==== Suggestions ====")
    print("1. Make sure your .env file is in the correct location (in the project root directory).")
    print("2. Ensure that TELEGRAM_API_ID and TELEGRAM_API_HASH are set correctly in the .env file.")
    print("3. Check that there are no spaces around the '=' sign in your .env file.")
    print("4. Verify that the API ID is a number and the API Hash is a string of letters and numbers.")
    print("5. If you need new API credentials, visit https://my.telegram.org/auth and create a new application.")
    print("6. Run the main.py script to create a new .env file automatically.")


async def main():
    """Main function"""
    print("=== Telegram API Credentials Checker ===\n")

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

    print("\n=== Check Complete ===")


if __name__ == "__main__":
    asyncio.run(main())