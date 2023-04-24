from pathlib import Path

# Some paths to store data
DATA_ROOT = Path(__file__).parent.parent.absolute() / "data"
DATA_JSON = DATA_ROOT / "json"
DATA_XML = DATA_ROOT / "xml"

BUNDESTAG_BASE_URL = "https://www.bundestag.de"
BUNDESTAG_OPENDATA_URL = BUNDESTAG_BASE_URL + "/services/opendata"
IDS_PROTOCOL_CONTAINER: list[tuple[str, str]] = [
    ("bt-collapse-866354", "pp20"),
    ("bt-collapse-543410", "pp19"),
]

SPEECH_XPATH = (
    "//p[@klasse => contains('J')][not(preceding-sibling::*[1]/name() = 'name')]/text()"
)
