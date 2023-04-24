import asyncio
from pathlib import Path

from src.config import (
    BUNDESTAG_BASE_URL,
    BUNDESTAG_OPENDATA_URL,
    DATA_JSON,
    DATA_XML,
    IDS_PROTOCOL_CONTAINER,
)
from src.parser import extract_infos_from_xml, save_debates_as_json, save_xml_files
from src.scraper import bulk_download, find_all_links


async def main():
    resource_link_groups = await find_all_links(
        base_url=BUNDESTAG_OPENDATA_URL, ids=IDS_PROTOCOL_CONTAINER
    )

    for group in resource_link_groups:
        dir_name = f"{DATA_XML}/{group.period}"
        # create xml path if not exists
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        # download all xml files
        download_links = [BUNDESTAG_BASE_URL + link for link in group.urls]
        download_results = await bulk_download(download_links)
        # save all xml files
        xml_file_list = await save_xml_files(
            base_path=dir_name, responses=download_results
        )
        print(f"Saved {len(xml_file_list)} xml files for {group.period}")

        # create json path if not exists
        Path(f"{DATA_JSON}/{group.period}").mkdir(parents=True, exist_ok=True)

        print(f"Starting to convert {group.period} xml files to a json representation")
        # convert to json like representation
        debates = extract_infos_from_xml(xml_file_list, period=group.period)

        json_file_list = await save_debates_as_json(debates=debates)

        print(f"Saved {len(json_file_list)} json files for {group.period}")


if __name__ == "__main__":
    asyncio.run(main())
