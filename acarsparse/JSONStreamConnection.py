import asyncio
import logging

# https://stackoverflow.com/questions/44196522/how-to-handle-tcp-client-socket-auto-reconnect-in-python-asyncio

class JSONStreamConnection:
    def __init__(self, name, json_queue, host, port):
        self.cache = ""
        self.close = None
        self.host = host
        self.log = logging.getLogger(__name__)
        self.name = name
        self.port = port
        self.q = json_queue
        self.sock = None
        self.messages = 0
        self.empty_string = False

    async def stream_json(self):
        self.log.info(
            "{name} performing intial connection to {host}:{port}...",
            name=self.name,
            host=self.host,
            port=self.port,
        )
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.log.info(
            "{name} connected to {host}:{port}, awaiting data...",
            name=self.name,
            host=self.host,
            port=self.port,
        )
        while self.close is None:
            data = None
            try:
                data = await self.reader.read(256)
            except Exception as e:
                self.log.error(
                    "{name} unable to read from stream: {error}", name=self.name, error=e)
            if data is not None:
                decoded = data.decode()
                if len(decoded) > 0:
                    if self.empty_string:
                        self.log.info(
                            "{name} recovered from empty string, back to normal!", name=self.name)
                        self.empty_string = False
                    if decoded[-1] == "\n":
                        await self.q.put("".join([self.cache, decoded]))
                        self.log.debug(
                            "{name} complete, pushing to queue: {json}",
                            name=self.name, json="".join(
                                [self.cache, repr(decoded)])
                        )
                        self.messages += 1
                        if self.messages % 50 == 0:
                            self.log.info(
                                "{name} parsed {messages} messages", name=self.name, messages=self.messages)
                        self.cache = ""
                    else:
                        self.cache = "".join([self.cache, decoded])
                        self.log.debug("{name} segment: {json}",
                                       name=self.name, json=repr(decoded))
                else:
                    if not self.empty_string:
                        self.log.info(
                            "{name} empty string decoded, possible connection issue?", name=self.name)
                        self.empty_string = True
