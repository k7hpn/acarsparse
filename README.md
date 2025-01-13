# acarsparse

A Python project to read ACARS/VDL-M2 data from a TCP JSON stream, detect drama, and share it

- Read ACARS/VDLM2 by making a socket connection to an [ACARS Hub](https://github.com/sdr-enthusiasts/docker-acarshub)
- Use a list of keywords of interest (drama) and phrases to exclude
- Facility for computing a "Drama Quotient" value to only publish or give priority to high-drama messages (needs work)
- Output matching messages to a Webhook (currently Discord is supported)

Areas for improvement:

- `WebhookPoster.py` - improve to support more destinations than just Discord (like Mastodon, hi Mike!)
- `DramaDetector.py` - better compute a `.dq` drama value to identify items worth sharing

## Getting Started

1. Clone the repository
2. Optional: set up a virtual environment

   ```bash
   python3 -m venv ~/.venv/acarsparse
   source ~/.venv/acarsparse/bin/activate
   python3 -m pip install --upgrade pip setuptools wheel
   ```

3. Install required libraries: `python3 -m pip install -r requirements.txt`
4. `cd acarsparse`
5. Copy `config-default.json` to `config.json`
6. Edit `config.json` to map to your ACARS Hub ACARS and VDLM2 socket ports
7. Copy `logging-default.yml` to `logging.yml`
8. `python3 AcarsParse.py`

## Configuration details

### config.json

Configuration of ACARS/VDLM2 sources and destination for output.

- Auto-detection of ACARS or VDLM2 source
- Reconnects when disconnected (happens when updating ACARS Hub)
- Supports Discord as an output Webhook

```json
{
  "sources": [
    {
      "host": "127.0.0.1",
      "name": "ACARS",
      "port": 15550
    },
    {
      "host": "127.0.0.1",
      "name": "VDLM2",
      "port": 15555
    }
  ],
  "logconfig": "logging.yml",
  "webhooks": [
    {
      "type": "discord",
      "url": "https://discord.com/api/webhooks/..."
    }
  ]
}
```

### drama.json

- Keywords in messages which increase drama (only single words)
- List of message labels which increase drama
- Exclusions: strings that, when matched, discard the message immediately

```json
{
  "version": 1,
  "keywords": ["COFFEE", "LAV"],
  "labels": [],
  "exclusions": [
    "AIRPORT IDENTIFIERS NOT ENTERED FOR WEATHER REQUEST",
    "ATIS INFO",
    "DATALINK SERVICE SUSPENDED",
    "NO DEPARTURE CLEARANCE"
  ]
}
```

### logging.yml

Configuration file for script logging.

If you wish to log to a [Seq](https://datalust.co/seq) server, add `seq` to your handlers and then add a handler similar to:

```yaml
seq:
  class: seqlog.structured_logging.SeqLogHandler
  formatter: seq

  # Seq-specific settings (add any others you need, they're just kwargs for SeqLogHandler's constructor).
  server_url: "http://seq.local/"
  api_key: "mySECRETapiKEY"

  # Use a custom JSON encoder, if you need to.
  json_encoder_class: json.encoder.JSONEncoder
```
