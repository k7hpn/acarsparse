import json
import logging

import aiofiles


class DramaDetector:
    def __init__(self, drama_config, message_queue, drama_queue):
        self.drama_config = drama_config
        self.dramaq = drama_queue
        self.log = logging.getLogger(__name__)
        self.msgq = message_queue

    async def detect(self):
        drama = None
        self.log.info("Loading drama...")
        async with aiofiles.open(self.drama_config, mode="r") as file:
            drama_json = await file.read()

        try:
            drama = json.loads(drama_json)
        except Exception as e:
            self.log.error(
                "Drama parsing your drama JSON: {error}, {json}",
                error=e,
                json=drama_json,
            )
            return

        keywords = set(drama["keywords"])
        exclusions = set(drama["exclusions"])

        self.log.info(
            "Drama loaded: {keyword_count} keywords, {exclusion_count} exclusions, {label_count} labels",
            keyword_count=len(keywords),
            exclusion_count=len(exclusions),
            label_count=len(drama["labels"]),
        )

        self.log.info("Detecting drama...")

        while True:
            message = await self.msgq.get()
            if message.text is not None:
                exclusion_found = False
                for ex in exclusions:
                    if ex in message.text:
                        exclusion_found = True
                        self.log.debug("Exclusion {ex} sighted in {text}",
                                       ex=ex,
                                       text=message.text)
                        break
                if exclusion_found:
                    continue
                words = set(message.text.split())
                drama_match = words.intersection(keywords)
                label_match = message.label in drama["labels"]
                if len(drama_match) > 0 or label_match:
                    message.drama = drama_match
                    message.label_match = label_match
                    message.dq = (
                        (len(drama_match) + (1 if label_match else 0))
                        * 100
                        / (len(keywords) + 1)
                    )
                    self.log.info(
                        "DQ calc: matches = {matches}, label = {label_match}, keywords = {keyword_count}",
                        matches=len(drama_match),
                        label_match=label_match,
                        keyword_count=len(keywords),
                    )
                    self.log.info(
                        "Drama detected {drama_quotient} ({drama_match_count}/{label_match}) [{drama_matches}]: {text}",
                        drama_quotient=message.dq,
                        drama_match_count=len(drama_match),
                        label_match=label_match,
                        drama_matches=",".join(drama_match),
                        text=message.text,
                    )
                    await self.dramaq.put(message)
