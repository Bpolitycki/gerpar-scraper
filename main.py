import asyncio

from src.config import BUNDESTAG_OPENDATA_URL, IDS_PROTOCOL_CONTAINER
from src.scraper import find_all_links

if __name__ == "__main__":
    links = asyncio.run(
        find_all_links(base_url=BUNDESTAG_OPENDATA_URL, ids=IDS_PROTOCOL_CONTAINER)
    )
    print(links)
