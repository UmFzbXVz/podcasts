import json
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re
from email.utils import formatdate
from datetime import datetime, timedelta

# Definer RSS-namespace og version
RSS_NS = "http://www.w3.org/2005/Atom"
RSS_VERSION = "2.0"

# Definer iTunes-namespace
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"

# Definer de datoformater, der skal kontrolleres for
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S %Z",
    "%a, %d %b %Y %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S %Z",
    "%Y-%m-%dT%H:%M:%S.%f"
]

# Iterer gennem alle JSON-filer i den aktuelle mappe
for filename in os.listdir():
    if not filename.endswith(".json"):
        continue

    # Indlæs JSON-data
    with open(filename) as f:
        data = json.load(f)

    # Ekstraher podcastinformation
    alt_text = data[list(data.keys())[0]]["alt_text"]
    image_url = data[list(data.keys())[0]]["image_url"]
    url = data[list(data.keys())[0]]["url"]
    description = data[list(data.keys())[0]]["description"]

    # Opret RSS-elementet
    rss = ET.Element("rss", version=RSS_VERSION)
    rss.set("xmlns:itunes", ITUNES_NS) # Tilføj iTunes-namespace til RSS-elementet

    # Opret channel-elementet
    channel = ET.SubElement(rss, "channel")

    # Tilføj podcastinformation til channel-elementet
    title = ET.SubElement(channel, "title")
    title.text = alt_text

    link = ET.SubElement(channel, "link")
    link.text = url

    atom_link = ET.SubElement(channel, "link")
    atom_link.set("href", url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    description_elem = ET.SubElement(channel, "description")
    description_elem.text = description

    image = ET.SubElement(channel, "itunes:image") # Brug iTunes-namespace for image-elementet
    image.set("href", image_url)

    # Tilføj hver episode til channel-elementet
    for episode_data in data[list(data.keys())[0]]["episodes"].values():
        episode = ET.SubElement(channel, "item")

        title = ET.SubElement(episode, "title")
        title.text = episode_data["title"]

        guid = ET.SubElement(episode, "guid")
        guid.text = episode_data["src"]
        guid.set("isPermaLink", "false")

        enclosure = ET.SubElement(episode, "enclosure")
        enclosure.set("url", episode_data["src"])
        enclosure.set("length", str(episode_data["duration"]))
        enclosure.set("type", "audio/mpeg")

        description = ET.SubElement(episode, "description")
        description.text = episode_data["description"]

        # Analyser datostrengen til et datetime-objekt
        for date_format in DATE_FORMATS:
            try:
                pubdate_datetime = datetime.strptime(episode_data["date"], date_format)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f"Kan ikke analysere datostreng: {episode_data['date']}")

        # Konverter datetime-objektet til Unix-timestamp og formater som RFC-822 datostreng
        pubdate_timestamp = pubdate_datetime.timestamp()
        pubDate = ET.SubElement(episode, "pubDate")
        pubDate.text = formatdate(pubdate_timestamp, localtime=True)
        
        # Beregn varigheden i det ønskede format (HH:MM:SS eller millisekunder)
        duration_milliseconds = episode_data["duration"]
        duration_seconds = duration_milliseconds // 1000

        if duration_seconds >= 86400:
            # Hvis varigheden er mere end 24 timer, formater den i millisekunder
            duration_formatted = str(duration_milliseconds)
        else:
            # Ellers formater den i sekunder
            duration_formatted = str(timedelta(seconds=duration_seconds))

        # Tilføj nøglen duration_formatted til episode_data-dictionary
        episode_data["duration_formatted"] = duration_formatted

        # Tilføj duration og order-tags
        duration = ET.SubElement(episode, "itunes:duration")
        duration.text = episode_data["duration_formatted"]

        order = ET.SubElement(episode, "itunes:order")
        order.text = pubdate_datetime.strftime("%Y%m%d%H%M%S")

    # Pretty-print XML og skriv det til en fil med podcastens titel som filnavn
    filename = re.sub(r'[^\w\s-]', '', alt_text).strip().lower()
    filename = re.sub(r'[-\s]+', '_', filename)

    # Sæt RSS-attributterne
    rss.set("xmlns:atom", RSS_NS)
    rss.set("xmlns:itunes", ITUNES_NS)
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    rss.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    rss.set("xmlns:rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    xml_string = ET.tostring(rss, encoding="unicode")
    xml_string_pretty = minidom.parseString(xml_string).toprettyxml(indent="  ")

    with open(f"{filename}.xml", "w") as f:
        f.write(xml_string_pretty)

