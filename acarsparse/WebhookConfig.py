class WebhookConfig:
    def __init__(self, **kwargs) -> None:
        self.url = kwargs.get("url")
        self.type = kwargs.get("type")
