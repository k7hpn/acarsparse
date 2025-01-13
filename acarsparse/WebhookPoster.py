import json
import logging

import httpx


class WebhookPoster:
    def __init__(self, webhooks, drama_queue):
        self.last = None
        self.log = logging.getLogger(__name__)
        self.dramaq = drama_queue
        self.webhooks = webhooks

    async def post(self):
        while True:
            message = await self.dramaq.get()
            message.text = message.text.replace('\n\n', '\n')
            data = None
            if message != self.last:
                for hook in self.webhooks:
                    if hook.type == "discord":
                        content = f"**{message.type}** via **{message.station}** ({message.freq} MHz) for flight **{message.flight}/{message.tail}** DramaQuotient™ {round(message.dq, 0):.0f}%:```{message.text}```"
                        label_match = (
                            f"{message.label} matched"
                            if message.label_match
                            else "did not match"
                        )
                        if len(message.drama) > 0:
                            drama_content = (
                                f'Words: [{",".join(message.drama)}] - label {label_match}'
                            )
                        else:
                            drama_content = f"No matched words - label {label_match}"
                        data = {
                            "content": content,
                            "embeds": [
                                {
                                    "title": f"Track tail {message.tail}",
                                    "url": f"https://www.flightaware.com/live/flight/{message.tail}",
                                    "fields": [{"name": "Drama", "value": drama_content}],
                                },
                            ],
                        }
                    if data is not None:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                hook.url,
                                data=json.dumps(data),
                                headers={"Content-type": "application/json"},
                            )
                        self.log.info(
                            "Posted to {type}, response {response_code}: {response}",
                            type=hook.type,
                            response_code=response,
                            response=response.text,
                        )
            else:
                self.log.debug("Duplicate message detected")
            self.last = message
