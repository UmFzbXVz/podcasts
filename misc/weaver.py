import json
import xml.etree.ElementTree as ET
from datetime import datetime
import xml.dom.minidom
from xml.sax.saxutils import escape

with open('fil_med_json', 'r') as f:
    podcasts = json.load(f)

# Iterer gennem hver podcast i JSON-filen
for podcast_id, podcast_data in podcasts.items():

    # Opret et RSS-element med version 2.0
    rss = ET.Element('rss', {'version': '2.0'})

    # Opret et kanal-element og tilføj det til RSS-elementet
    channel = ET.SubElement(rss, 'channel')

    # Tilføj titel, link, beskrivelse og sprog til kanal-elementet
    ET.SubElement(channel, 'title').text = escape(podcast_data['alt_text'])
    ET.SubElement(channel, 'link').text = podcast_data['url']
    ET.SubElement(channel, 'description').text = escape(podcast_data['description'])
    ET.SubElement(channel, 'language').text = 'da-DK'

    # Tilføj iTunes-specifikke tags til kanal-elementet
    itunes_ns = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
    ET.register_namespace('itunes', itunes_ns)
    if 'subtitle' in podcast_data:
        ET.SubElement(channel, '{%s}subtitle' % itunes_ns).text = escape(podcast_data['subtitle'])
    if 'summary' in podcast_data:
        ET.SubElement(channel, '{%s}summary' % itunes_ns).text = escape(podcast_data['summary'])
    if 'author' in podcast_data:
        ET.SubElement(channel, '{%s}author' % itunes_ns).text = escape(podcast_data['author'])
    if 'image' in podcast_data:
        image_url = podcast_data['image']
        ET.SubElement(channel, '{%s}image' % itunes_ns, {'href': image_url})
    if 'category' in podcast_data:
        ET.SubElement(channel, '{%s}category' % itunes_ns, {'text': escape(podcast_data['category'])})

    # Hold styr på set af set episode-ID'er
    seen_ids = set()

    # Iterer gennem hver episode for denne podcast
    for episode in podcast_data['episodes']:

        # Spring over duplikerede episoder
        if episode['id'] in seen_ids:
            continue
        seen_ids.add(episode['id'])

        # Opret et item-element og tilføj det til kanal-elementet
        publish_time = episode['publish_time'].replace('Z', '+0000')
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = escape(episode['title'])
        ET.SubElement(item, 'link').text = episode['uri']
        description = ET.SubElement(item, 'description')
        description_text = f"<![CDATA[{escape(episode['description']) if 'description' in episode and episode['description'] is not None else ''}]]>"
        description.text = description_text
        ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = episode['uri']
        pub_date = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%a, %d %b %Y %H:%M:%S %z')
        ET.SubElement(item, 'pubDate').text = pub_date

        # Beregn længden af lydfilen i sekunder
        duration = episode['duration']
        duration_parts = list(map(int, duration.split(':')))
        if len(duration_parts) == 2:
            duration_parts.insert(0, 0)
        length = duration_parts[0] * 3600 + duration_parts[1] * 60 + duration_parts[2]

        # Sæt "enclosure"-tagget med URL'en til lydfilen, længden i sekunder og MIME-typen
        ET.SubElement(item, 'enclosure', {
            'url': episode['uri'],
            'length': str(length),
            'type': 'audio/mpeg'
        })

        # Tilføj iTunes-specifikke tags til hver episode
        duration_formatted = f"{duration_parts[0]:02d}:{duration_parts[1]:02d}:{duration_parts[2]:02d}"
        ET.SubElement(item, '{%s}duration' % itunes_ns).text = duration_formatted
        if 'subtitle' in episode:
            ET.SubElement(item, '{%s}subtitle' % itunes_ns).text = escape(episode['subtitle'])
        if 'summary' in episode:
            ET.SubElement(item, '{%s}summary' % itunes_ns).text = escape(episode['summary'])
        if 'author' in episode:
            ET.SubElement(item, '{%s}author' % itunes_ns).text = escape(episode['author'])
        if 'image' in episode:
            ET.SubElement(item, '{%s}image' % itunes_ns, {'href': episode['image']})

    # Gem RSS-feedet i en fil
    file_name = podcast_data['alt_text'].replace('/', '_').replace('?', '_').replace(' ', '_').lower()
    with open(f"{file_name}.rss", 'w', encoding='utf-8') as feed_file:
        xml_string = xml.dom.minidom.parseString(ET.tostring(rss)).toprettyxml()
        feed_file.write(xml_string)
