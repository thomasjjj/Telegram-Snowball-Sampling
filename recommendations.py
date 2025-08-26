from telethon.tl.functions.channels import GetChannelRecommendationsRequest
from telethon.errors import FloodWaitError
import asyncio
import os
import re
import logging
from config import Config

logger = logging.getLogger(__name__)


async def get_channel_recommendations(client, channel_entity, initial_channel=None, depth=0, max_depth=2,
                                      processed_channels=None, edge_list_writer=None):
    """
    Recursively fetches Telegram channel recommendations starting from a given channel.

    Args:
        client (TelegramClient): The initialized Telegram client.
        channel_entity (str/Channel): The channel entity to process.
        initial_channel (str): The original channel used for naming files.
        depth (int): Current recursion depth.
        max_depth (int): Maximum recursion depth.
        processed_channels (set): Set of processed channel usernames/IDs.
        edge_list_writer (function): Function to write edge list entries.

    Returns:
        set: Set of newly discovered channel entities.
    """
    if processed_channels is None:
        processed_channels = set()

    if initial_channel is None:
        initial_channel = channel_entity

    if depth > max_depth:
        return set()

    # Extract channel attributes safely
    try:
        current_channel_username = getattr(channel_entity, 'username', None)
        current_channel_id = getattr(channel_entity, 'id', None)
        current_channel_title = getattr(channel_entity, 'title', None)

        # Convert to string to avoid type issues
        if current_channel_id is not None:
            current_channel_id = str(current_channel_id)

        # Use string representation if attributes not found
        if current_channel_username is None:
            current_channel_username = str(channel_entity)
        if current_channel_id is None:
            current_channel_id = str(channel_entity)
        if current_channel_title is None:
            current_channel_title = str(channel_entity)
    except:
        # Fallback to string representation if any error occurs
        current_channel_id = str(channel_entity)
        current_channel_username = str(channel_entity)
        current_channel_title = str(channel_entity)

    logger.info(
        f"Fetching recommendations for channel: {current_channel_title} (@{current_channel_username}), Depth: {depth}/{max_depth}")

    new_channels = set()
    recommendation_tasks = []

    try:
        recommendations = await client(GetChannelRecommendationsRequest(channel=channel_entity))

        if hasattr(recommendations, 'chats'):
            for recommended_channel in recommendations.chats:
                # Extract attributes safely
                try:
                    username = getattr(recommended_channel, 'username', None)
                    channel_id = getattr(recommended_channel, 'id', None)
                    title = getattr(recommended_channel, 'title', 'Unknown')

                    # Convert to string if not None
                    if channel_id is not None:
                        channel_id = str(channel_id)

                    if not username and not channel_id:
                        continue

                    channel_identifier = username if username else channel_id

                    if channel_identifier not in processed_channels:
                        processed_channels.add(channel_identifier)
                        new_channels.add(channel_identifier)

                        logger.info(f"Depth {depth}: Recommendation - Title: {title}, Username: @{username}")

                        # Write to edge list if writer function exists
                        if edge_list_writer and current_channel_id and channel_id:
                            edge_list_writer(
                                current_channel_id,
                                current_channel_title,
                                current_channel_username,
                                channel_id,
                                title,
                                username,
                                connection_type="recommendation"
                            )

                        # Only continue if we haven't reached max depth
                        if depth < max_depth:
                            # Schedule retrieval of recommendations for the next depth level
                            recommendation_tasks.append(
                                get_channel_recommendations(
                                    client,
                                    recommended_channel,
                                    initial_channel,
                                    depth + 1,
                                    max_depth,
                                    processed_channels,
                                    edge_list_writer
                                )
                            )
                except Exception as ex:
                    logger.warning(f"Error processing recommended channel: {ex}")
                    continue

        # Process recommendations concurrently
        if recommendation_tasks:
            results = await asyncio.gather(*recommendation_tasks)
            for result in results:
                new_channels.update(result)

    except FloodWaitError as e:
        logger.warning(f"Flood wait error for channel {current_channel_username}. Sleeping for {e.seconds} seconds.")
        await asyncio.sleep(e.seconds)
        # Retry after the wait period
        additional_channels = await get_channel_recommendations(
            client, channel_entity, initial_channel, depth, max_depth,
            processed_channels, edge_list_writer
        )
        new_channels.update(additional_channels)

    except Exception as e:
        logger.error(f"Error retrieving recommendations for channel {current_channel_username}: {e}")
        if Config.DEBUG:
            import traceback
            logger.error(traceback.format_exc())

    return new_channels


async def extract_urls_from_message(message):
    """Extract all URLs from a message."""
    if message and message.message:
        return re.findall(r'(https?://\S+)', message.message)
    return []


async def process_urls(client, channel_entity, edge_list_writer, url_file=None):
    """
    Process messages in a channel to extract and log outbound URLs.

    Args:
        client (TelegramClient): The initialized Telegram client.
        channel_entity (str/Channel): The channel entity to process.
        edge_list_writer (function): Function to write edge list entries.
        url_file (file): Open file handle to write URLs to.

    Returns:
        set: Set of extracted URLs.
    """
    # Extract channel attributes safely
    try:
        current_channel_id = getattr(channel_entity, 'id', None)
        current_channel_title = getattr(channel_entity, 'title', None)
        current_channel_username = getattr(channel_entity, 'username', None)

        # Convert ID to string
        if current_channel_id is not None:
            current_channel_id = str(current_channel_id)

        # Use string representation if attributes not found
        if current_channel_id is None:
            current_channel_id = str(channel_entity)
        if current_channel_title is None:
            current_channel_title = str(channel_entity)
        if current_channel_username is None:
            current_channel_username = str(channel_entity)
    except:
        # Fallback to string representation
        current_channel_id = str(channel_entity)
        current_channel_title = str(channel_entity)
        current_channel_username = str(channel_entity)

    url_set = set()

    try:
        async for message in client.iter_messages(channel_entity, limit=Config.DEFAULT_MAX_POSTS):
            urls = await extract_urls_from_message(message)

            for url in urls:
                url_set.add(url)

                # Write to edge list if writer function exists and IDs are valid
                if edge_list_writer and current_channel_id:
                    # For URLs, use the URL as the target ID and "External URL" as the target name
                    edge_list_writer(
                        current_channel_id,
                        current_channel_title,
                        current_channel_username,
                        url,  # URL as ID
                        "External URL",  # Generic name
                        None,  # No username for external URLs
                        connection_type="outbound_link"
                    )

                # Write to URL file if provided
                if url_file:
                    url_file.write(f"{url}\n")
                    url_file.flush()

    except Exception as e:
        logger.error(f"Error processing URLs for channel {current_channel_username}: {e}")
        if Config.DEBUG:
            import traceback
            logger.error(traceback.format_exc())

    return url_set