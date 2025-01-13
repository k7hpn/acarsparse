class AcarsMessage:
    def __init__(self, **kwargs) -> None:
        self.flight = kwargs.get("flight")
        self.freq = kwargs.get("freq")
        self.label = kwargs.get("label")
        self.station = kwargs.get("station")
        self.tail = kwargs.get("tail")
        self.text = kwargs.get("text")
        self.type = kwargs.get("type")

    def __repr__(self) -> str:
        return f"{self.type} from flight {self.flight} ({self.tail}) label {self.label}: {self.text}"
