#!/usr/bin/env/python3
import asyncio
import json
import logging
import sys
from pathlib import Path

import aiofiles
import seqlog
from AcarsDecoder import AcarsDecoder
from DramaDetector import DramaDetector
from JSONStreamConnection import JSONStreamConnection
from WebhookConfig import WebhookConfig
from WebhookPoster import WebhookPoster

__version__ = "1.0.0"

CONFIG_FILE_NAME = "config.json"
DRAMA_FILE_NAME = "drama.json"


async def read_config():
    config_path = Path(CONFIG_FILE_NAME)
    if not config_path.exists:
        sys.stderr.write("Fatal error: config.json not found")
        sys.exit(1)
    try:
        async with aiofiles.open(CONFIG_FILE_NAME, mode="r") as file:
            config_json = await file.read()
    except Exception as e:
        sys.stderr.write(f"Fatal error: could not read config file: {e}")
        sys.exit(1)
    if len(config_json) == 0:
        sys.stderr.write("exiting: config.json file is empty")
        sys.exit(1)
    config = None
    try:
        config = json.loads(config_json)
    except Exception as e:
        sys.stderr.write(f"Fatal error: could not decode config files: {e}")
        sys.exit(1)
    if config is None:
        sys.stderr.write(
            "Fatal error: read and parsed config file, found no settings")
        sys.exit(1)
    return config


async def main():
    config = await read_config()

    log_config_path = config.get("logconfig")
    if log_config_path is not None:
        log_config = Path(log_config_path)
        if log_config.is_file():
            seqlog.configure_from_file(log_config)

    log = logging.getLogger(__name__)
    log.info("AcarsParse starting up...")
    json_queue = asyncio.Queue()
    message_queue = asyncio.Queue()
    drama_queue = asyncio.Queue()

    async_routines = []

    acars_sources = []
    for source in config.get("sources"):
        stream_connection = JSONStreamConnection(
            source.get("name"),
            json_queue, source.get("host"), source.get("port")
        )
        acars_sources.append(stream_connection)
        async_routines.append(stream_connection.stream_json())

    if len(acars_sources) == 0:
        sys.stderr.write("No ACARS sources defined in config, exiting...")
        sys.exit(1)

    acars_decoder = AcarsDecoder(json_queue, message_queue)
    async_routines.append(acars_decoder.monitor_queue())

    drama_detector = DramaDetector(DRAMA_FILE_NAME, message_queue, drama_queue)
    async_routines.append(drama_detector.detect())

    webhook_config = []
    for webhook in config.get("webhooks"):
        webhook_config.append(
            WebhookConfig(
                type=webhook.get("type"),
                url=webhook.get("url"),
            )
        )
    if len(webhook_config) > 0:
        webhook_poster = WebhookPoster(webhook_config, drama_queue)
        async_routines.append(webhook_poster.post())

    await asyncio.gather(*async_routines)


if __name__ == "__main__":
    asyncio.run(main())
