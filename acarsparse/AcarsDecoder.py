import json
import logging

from AcarsMessage import AcarsMessage


class AcarsDecoder:
    def __init__(self, json_queue, message_queue):
        self.errors = 0
        self.jsonq = json_queue
        self.log = logging.getLogger(__name__)
        self.msgq = message_queue
        self.parsed = 0

    async def monitor_queue(self):
        self.log.info("Monitoring queue...")
        while True:
            item = await self.jsonq.get()
            try:
                data = json.loads(item)
                self.parsed += 1
            except Exception as e:
                self.log.warning(
                    "Unable to parse JSON: {error}, {json}", error=e, json=item
                )
                self.errors += 1
                continue
            message = AcarsMessage()
            if "vdl2" in data:
                vdl2 = data.get("vdl2")
                message.type = "VDLM2"
                message.freq = vdl2.get("freq")
                while message.freq > 999:
                    message.freq = message.freq / 1000
                message.station = vdl2.get("station")
                if "avlc" in vdl2:
                    avlc = vdl2.get("avlc")
                    if "acars" in avlc:
                        acars = avlc.get("acars")
                        message.flight = acars.get("flight")
                        tail = acars.get("reg")
                        if tail is not None:
                            message.tail = tail[1:]
                        message.label = acars.get("label")
                        message.text = acars.get("msg_text")
            else:
                message.type = "ACARS"
                message.flight = data.get("flight")
                message.tail = data.get("tail")
                message.label = data.get("label")
                message.text = data.get("text")
                message.freq = data.get("freq")
                message.station = data.get("station_id")

            await self.msgq.put(message)
