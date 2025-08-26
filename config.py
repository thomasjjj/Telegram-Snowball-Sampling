import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuration variables with defaults
class Config:
    # Load environment variables from .env file
    @classmethod
    def reload_env(cls):
        """Reload environment variables from .env file"""
        # Load .env file explicitly, ensuring we get fresh values
        if os.path.exists('.env'):
            logger.info("Loading configuration from .env file")
            # Force reload by setting override=True
            load_dotenv('.env', override=True)
        else:
            logger.warning("No .env file found")

        cls._load_config()
        return cls

    @classmethod
    def _load_config(cls):
        """Load configuration values from environment variables"""
        # Telegram API credentials
        cls.API_ID = os.getenv('TELEGRAM_API_ID')
        cls.API_HASH = os.getenv('TELEGRAM_API_HASH')
        cls.SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'session_name')

        # Log API values for debugging (partial, for security)
        if cls.API_ID:
            logger.info(f"Loaded API_ID from environment: {cls.API_ID}")
        if cls.API_HASH:
            api_hash_masked = cls.API_HASH[:3] + '...' + cls.API_HASH[-3:] if len(cls.API_HASH or '') > 6 else "None"
            logger.info(f"Loaded API_HASH from environment: {api_hash_masked}")

        # Snowball sampling configuration
        cls.DEFAULT_MIN_MENTIONS = int(os.getenv('DEFAULT_MIN_MENTIONS', 5))
        cls.DEFAULT_ITERATIONS = int(os.getenv('DEFAULT_ITERATIONS', 3))
        cls.DEFAULT_MAX_POSTS = os.getenv('DEFAULT_MAX_POSTS', None)
        if cls.DEFAULT_MAX_POSTS and str(cls.DEFAULT_MAX_POSTS).isdigit():
            cls.DEFAULT_MAX_POSTS = int(cls.DEFAULT_MAX_POSTS)
        else:
            cls.DEFAULT_MAX_POSTS = None

        # Channel recommendations configuration
        cls.DEFAULT_INCLUDE_RECOMMENDATIONS = os.getenv('DEFAULT_INCLUDE_RECOMMENDATIONS', 'True').lower() in ('true',
                                                                                                               '1', 't')
        cls.DEFAULT_RECOMMENDATIONS_DEPTH = int(os.getenv('DEFAULT_RECOMMENDATIONS_DEPTH', 2))

        # URL extraction configuration
        cls.DEFAULT_INCLUDE_URLS = os.getenv('DEFAULT_INCLUDE_URLS', 'True').lower() in ('true', '1', 't')

        # File paths and directories
        cls.RESULTS_FOLDER = os.getenv('RESULTS_FOLDER', 'results')
        cls.MERGED_FOLDER = os.getenv('MERGED_FOLDER', 'merged')
        cls.EDGE_LIST_FOLDER = os.getenv('EDGE_LIST_FOLDER', 'EdgeList')
        cls.EDGE_LIST_FILENAME = os.getenv('EDGE_LIST_FILENAME', 'Edge_List.csv')
        cls.MERGED_FILENAME = os.getenv('MERGED_FILENAME', 'merged_channels.csv')
        cls.API_DETAILS_FILE = os.getenv('API_DETAILS_FILE', 'api_values.txt')

        # Debug mode
        cls.DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

    @classmethod
    def validate(cls):
        """Validate the configuration and log warnings for missing values"""
        if not cls.API_ID or not cls.API_HASH:
            logger.warning("API credentials not found in .env file")
            return False

        # Convert API_ID to int if it's a string
        if isinstance(cls.API_ID, str) and cls.API_ID.isdigit():
            cls.API_ID = int(cls.API_ID)
            logger.info("Converted API_ID from string to integer")

        # Log the configuration (excluding sensitive data)
        logger.info(f"Configuration validated successfully")
        logger.info(f"Session name: {cls.SESSION_NAME}")
        logger.info(f"Default iterations: {cls.DEFAULT_ITERATIONS}")
        logger.info(f"Default min mentions: {cls.DEFAULT_MIN_MENTIONS}")
        logger.info(f"Default max posts: {cls.DEFAULT_MAX_POSTS}")
        logger.info(f"Include recommendations: {cls.DEFAULT_INCLUDE_RECOMMENDATIONS}")
        logger.info(f"Recommendations depth: {cls.DEFAULT_RECOMMENDATIONS_DEPTH}")
        logger.info(f"Include URLs: {cls.DEFAULT_INCLUDE_URLS}")
        logger.info(f"Results folder: {cls.RESULTS_FOLDER}")
        logger.info(f"Merged folder: {cls.MERGED_FOLDER}")
        logger.info(f"Edge list folder: {cls.EDGE_LIST_FOLDER}")
        logger.info(f"Debug mode: {cls.DEBUG}")

        return True


# Initial load of configuration
Config.reload_env()