import asyncio
from dataclasses import dataclass

from playwright.async_api import async_playwright


@dataclass
class ProtocolUrls:
    period: str
    urls: list[str]


def split_link(link: str) -> str:
    return link.split("/")[-1]


async def find_protocol_urls(
    base_url: str,
    container: tuple[str, str],
    downlad_link_selector: str = "a.bt-link-dokument",
    next_selector: str = ".slick-next.slick-arrow",
) -> ProtocolUrls:
    result: ProtocolUrls = ProtocolUrls(container[1], [])
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(base_url)
        print(f"Trying to find download links for: {container[1]}")
        protocol_download_container = await page.query_selector(f"#{container[0]}")
        if protocol_download_container is not None:
            download_urls: set[str] = set()
            button_next = await protocol_download_container.query_selector(
                next_selector
            )
            last_reached = False
            while button_next is not None:
                protocol_download_container = await page.query_selector(
                    f"#{container[0]}"
                )
                if protocol_download_container is None:
                    break
                xml_downloads = await protocol_download_container.query_selector_all(
                    downlad_link_selector
                )
                for xml_download in xml_downloads:
                    url: str | None = await xml_download.get_attribute("href")
                    if url is not None:
                        download_urls.add(url)

                if last_reached is True:
                    break

                # toggle next page
                await button_next.click()
                # Wait for the animation to finish
                await asyncio.sleep(0.75)

                button_next = await protocol_download_container.wait_for_selector(
                    next_selector
                )

                if button_next is not None:
                    is_disabled = await button_next.is_disabled()
                    if is_disabled:
                        last_reached = True

            print(f"Found {len(download_urls)} download links for {container[1]}")
            result.urls = sorted(download_urls, key=split_link, reverse=True)

        await browser.close()

    return result


async def find_all_links(
    base_url: str, ids: list[tuple[str, str]]
) -> list[ProtocolUrls]:
    async with asyncio.TaskGroup() as task_group:
        results = [task_group.create_task(find_protocol_urls(base_url, i)) for i in ids]
    return [r.result() for r in results]
