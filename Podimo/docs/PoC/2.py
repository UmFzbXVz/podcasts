import os
import json
import re
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime

def prettify(elem):
    """Returnerer en pænt formateret XML-streng for Elementet."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

def sanitize_filename(filename):
    """Sanitér filnavn til Windows ved at erstatte ulovlige tegn."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def convert_m3u8_to_mp3(url):
    """Konverter .m3u8-indkapslings-URL til .mp3"""
    url = url.replace('hls-media', 'audios')  # Erstat "hls-media" med "audios"
    url = url.replace('/main.m3u8', '.mp3')   # Fjern "/main.m3u8" og erstat med ".mp3"
    return url


def generate_podcast_rss(podcast):
    rss = Element('rss', attrib={'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd', 'version': '2.0'})
    channel = SubElement(rss, 'channel')

    title = SubElement(channel, 'title')
    title.text = podcast['title']

    description = SubElement(channel, 'description')
    description.text = podcast['description']

    # Generer podcast-URL ved hjælp af podcast-ID
    podcast_url = f"https://podimo.com/dk/shows/{podcast['id']}"
    link = SubElement(channel, 'link')
    link.text = podcast_url

    # Tilføj podcastbillede til hovedkanalen
    image = SubElement(channel, 'image')
    image_url = podcast['coverImageUrl']
    image_url = image_url.replace(" ", "%20")  # Erstat mellemrum med %20 i URL'en
    image_url = image_url.replace("(", "%28").replace(")", "%29")  # Erstat parenteser med %28 og %29 i URL'en
    image_url = image_url.replace("{", "%7B").replace("}", "%7D")  # Erstat krøllede parenteser med %7B og %7D i URL'en
    SubElement(image, 'url').text = image_url
    SubElement(image, 'title').text = podcast['title']
    SubElement(image, 'link').text = podcast_url

    for episode in podcast['episodes']:
        item = SubElement(channel, 'item')
        item_title = SubElement(item, 'title')
        item_title.text = episode['title']

        item_description = SubElement(item, 'description')
        item_description.text = episode['description']

        item_guid = SubElement(item, 'guid', isPermaLink="false")
        item_guid.text = episode['id']

        # Konverter dato og tid til det korrekte format for pubDate
        pub_date = datetime.strptime(episode['datetime'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%a, %d %b %Y %H:%M:%S +0000")
        item_pub_date = SubElement(item, 'pubDate')
        item_pub_date.text = pub_date.strip()  # Fjern mellemrum fra det formaterede pubDate

        # Håndter indkapslings-URL
        enclosure_url = episode['streamMedia']['url']
        if enclosure_url.endswith('.m3u8'):
            enclosure_url = convert_m3u8_to_mp3(enclosure_url)

        enclosure = SubElement(item, 'enclosure')
        enclosure.set('url', enclosure_url)
        enclosure.set('length', '0')  # Sæt længden til 0
        enclosure.set('type', 'audio/mpeg')

        # Konverter varighed til iTunes-kompatibelt format
        duration_seconds = episode['streamMedia']['duration']
        duration_hours = duration_seconds // 3600
        duration_minutes = (duration_seconds % 3600) // 60
        duration_seconds = duration_seconds % 60
        itunes_duration = f"{duration_hours:02}:{duration_minutes:02}:{duration_seconds:02}"
        item_itunes_duration = SubElement(item, 'itunes:duration')
        item_itunes_duration.text = itunes_duration

        item_itunes_image = SubElement(item, 'itunes:image', attrib={'href': episode['imageUrl']})

    rss_xml = prettify(rss)
    rss_filename = sanitize_filename(podcast['title']) + ".rss"
    output_dir = os.path.join('Podimo', 'RSS')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, rss_filename), 'w', encoding='utf-8') as rss_file:
        rss_file.write(rss_xml)

if __name__ == "__main__":
    with open('podimo.json', 'r', encoding='utf-8') as file:
        podcasts = json.load(file)

    # Generer RSS for hver podcast i dataene
    for podcast in podcasts:
        generate_podcast_rss(podcast)
