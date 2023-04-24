import asyncio
import json
import re
from dataclasses import dataclass

from aiofile import async_open
from saxonche import PySaxonProcessor

from src.config import SPEECH_XPATH
from src.scraper import ProtocolResponse, split_link

CSS_RE = re.compile(
    r'<\?xml-stylesheet href="dbtplenarprotokoll.css" type="text/css" charset="UTF-8"\?>'
)
DTD_RE = re.compile(r'<!DOCTYPE dbtplenarprotokoll SYSTEM "dbtplenarprotokoll.dtd">')


@dataclass
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


def remove_dtd_css(xml_text: str) -> str:
    """Removes the included css and dtd from the xml text"""
    return DTD_RE.sub("", CSS_RE.sub("", xml_text))


async def xml_file_writer(xml_text: str, file_name: str, base_path: str) -> str:
    file_path = f"{base_path}/{file_name}"
    async with async_open(f"{base_path}/{file_name}", "w") as file:
        content = remove_dtd_css(xml_text)
        await file.write(content)
    return file_path


async def save_xml_files(
    base_path: str, responses: list[ProtocolResponse]
) -> list[str]:
    async with asyncio.TaskGroup() as task_group:
        saved_files = [
            task_group.create_task(
                xml_file_writer(
                    r.content, split_link(r.url).replace("-data", ""), base_path
                )
            )
            for r in responses
        ]
    return [f.result() for f in saved_files]


def speech_xpath_builder(speech_xpath: str) -> str:
    return (
        "for $speech in //rede return map {'id': $speech/@id/data(.), 'speech': $speech"
        + speech_xpath
        + " => string-join('\n'), 'role': $speech//name//rolle_kurz/text() => head(), 'forename': $speech//name/vorname/text() => distinct-values(), 'surename': $speech//name/nachname/text() => distinct-values(), 'party': $speech//name/fraktion/text() => distinct-values()}"
    )


def extract_infos_from_xml(
    xml_files: list[str], period: str
) -> list[tuple[str, PlenaryDebate]]:
    """Extracts the relevant information from the xml files
    and stores the info in a list of tuples (filename, PlenaryDebate)"""

    debates: list[tuple[str, PlenaryDebate]] = []

    speech_xpath_expression = speech_xpath_builder(SPEECH_XPATH)

    with PySaxonProcessor(license=False) as proc:
        xpath_proc = proc.new_xpath_processor()

        for xml_file in xml_files:
            doc = proc.parse_xml(xml_file_name=xml_file)
            xpath_proc.set_context(xdm_item=doc)  # type: ignore
            date = xpath_proc.evaluate_single("//kopfdaten//datum/@date/data()")
            number = xpath_proc.evaluate_single("//kopfdaten//sitzungsnr/text()")
            speeches = xpath_proc.evaluate(speech_xpath_expression)

            speeches_list: list[PlenarySpeech] = []
            for speech in speeches:
                speeches_list.append(
                    PlenarySpeech(
                        speech_id=speech.get("id").__str__(),  # type: ignore
                        speaker=PlenarySpeaker(
                            forename=speech.get("forename").__str__(),  # type: ignore
                            surname=speech.get("surename").__str__(),  # type: ignore
                            party=speech.get("party").__str__() if speech.get("party") is not None else None,  # type: ignore
                            role=speech.get("role").__str__() if speech.get("role") is not None else None,  # type: ignore
                        ),
                        text=speech.get("speech").__str__(),  # type: ignore
                    )
                )

            debate = PlenaryDebate(
                date=date.__str__() if date is not None else None,
                period=period,
                number=int(number.__str__()) if number is not None else None,
                speeches=speeches_list,
            )

            debates.append((xml_file.replace("xml", "json"), debate))

    return debates


async def save_debate_json(
    debate: PlenaryDebate,
    file: str,
) -> str:
    json_content = json.dumps(debate.to_dict(), indent=4, ensure_ascii=False)

    async with async_open(file, "w") as f:
        await f.write(json_content)

    return file


async def save_debates_as_json(
    debates: list[tuple[str, PlenaryDebate]],
) -> list[str]:
    async with asyncio.TaskGroup() as task_group:
        saved_files = [
            task_group.create_task(save_debate_json(debate=debate, file=file))
            for file, debate in debates
        ]
    return [f.result() for f in saved_files]
