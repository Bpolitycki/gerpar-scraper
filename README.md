# gerpar-scraper

A simple Python based scraper, which allows scraping and downloading of the new (truly) XML encoded [plenary protocols](https://www.bundestag.de/services/opendata). It's built around Pythons `asyncio`.  Mainly the following external libraries are used:

- `playwright` for browser automation
- `aiohttp` to request the xml files
- `aiofile` to store files
- `saxonche` for xml processing

This project uses [poetry](https://python-poetry.org) for dependency management and a so called `Taskfile` to execute different workflows. To scrape and download the files execute the following steps:

1. `./Taskfile install` to install dependencies
2. `./Taskfile scrape` to scrape and download – this will create a directory data and store the protocols in the pure xml format as well as in json.

The JSON format is defined be the following Python classes:

```python
class PlenarySpeaker:
    forename: str
    surname: str
    party: str | None
    role: str | None


@dataclass
class PlenarySpeech:
    speech_id: str
    speaker: PlenarySpeaker
    text: str

    def to_dict(self):
        return {
            "id": self.speech_id,
            "speaker": self.speaker.__dict__,
            "text": self.text,
        }


@dataclass
class PlenaryDebate:
    date: str | None
    period: str
    number: int | None
    speeches: list[PlenarySpeech]

    def to_dict(self):
        return {
            "date": self.date,
            "period": self.period,
            "number": self.number,
            "speeches": [s.to_dict() for s in self.speeches],
        }
```

If you want to adjust some default settings just tweak the variables stored in `src/config.py`.

## Author:

- [Bastian Politycki](https://github.com/Bpolitycki) – Swiss Law Sources
