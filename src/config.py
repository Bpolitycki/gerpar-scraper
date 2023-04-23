from pathlib import Path

# Some paths to store data
DATA_ROOT = Path(__file__).parent.parent / "data"
DATA_TEXT = DATA_ROOT / "text"
DATA_XML = DATA_ROOT / "xml"

BUNDESTAG_OPENDATA_URL = "https://www.bundestag.de/services/opendata"
IDS_PROTOCOL_CONTAINER: list[tuple[str, str]] = [
    ("bt-collapse-866354", "pp20"),
    ("bt-collapse-543410", "pp19"),
]
