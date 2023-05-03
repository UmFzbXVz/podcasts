import json
import xml.etree.ElementTree as ET
from datetime import datetime
import xml.dom.minidom

with open('fil_med_json', 'r') as f:
    podcasts = json.load(f)

for podcast_id, podcast_data in podcasts.items():
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = podcast_data['alt_text']
    ET.SubElement(channel, 'link').text = podcast_data['url']
    ET.SubElement(channel, 'description').text = podcast_data['description']
    ET.SubElement(channel, 'language').text = 'da-DK'

    # Tilføj iTunes-specifikke tags
    itunes_ns = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
    ET.register_namespace('itunes', itunes_ns)
    if 'subtitle' in podcast_data:
        ET.SubElement(channel, '{%s}subtitle' % itunes_ns).text = podcast_data['subtitle']
    if 'summary' in podcast_data:
        ET.SubElement(channel, '{%s}summary' % itunes_ns).text = podcast_data['summary']
    if 'author' in podcast_data:
        ET.SubElement(channel, '{%s}author' % itunes_ns).text = podcast_data['author']
    if 'image' in podcast_data:
        image_url = podcast_data['image']
        ET.SubElement(channel, '{%s}image' % itunes_ns, {'href': image_url})
    if 'category' in podcast_data:
        ET.SubElement(channel, '{%s}category' % itunes_ns, {'text': podcast_data['category']})

    seen_ids = set()  # Hold øje med IDs (for at undgå duplicates)
    for episode in podcast_data['episodes']:
        if episode['id'] in seen_ids:
            continue  # Skip duplicate
        seen_ids.add(episode['id'])

        publish_time = episode['publish_time'].replace('Z', '+0000')
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = episode['title']
        ET.SubElement(item, 'link').text = episode['uri']
        ET.SubElement(item, 'description').text = episode.get('description', '')
        ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = episode['uri']
        pub_date = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%a, %d %b %Y %H:%M:%S %z')
        ET.SubElement(item, 'pubDate').text = pub_date

        # Beregn længden af afsnittet i millisekunder
        duration = episode['duration']
        duration_parts = list(map(int, duration.split(':')))
        if len(duration_parts) == 2:
            duration_parts.insert(0, 0)
        length = duration_parts[0] * 3600 + duration_parts[1] * 60 + duration_parts[2]

        ET.SubElement(item, 'enclosure', {
            'url': episode['uri'],
            'length': str(length),
            'type': 'audio/mpeg'
        })

        # Indsæt iTunes-specifikke sager
        duration_formatted = f"{duration_parts[0]:02d}:{duration_parts[1]:02d}:{duration_parts[2]:02d}"
        ET.SubElement(item, '{%s}duration' % itunes_ns).text = duration_formatted
        if 'subtitle' in episode:
            ET.SubElement(item, '{%s}subtitle' % itunes_ns).text = episode['subtitle']
        if 'summary' in episode:
            ET.SubElement(item, '{%s}summary' % itunes_ns).text = episode['summary']
        if 'author' in episode:
            ET.SubElement(item, '{%s}author' % itunes_ns).text = episode['author']
        ET.SubElement(item, '{%s}explicit' % itunes_ns).text = 'no'
        if 'image' in podcast_data:
            ET.SubElement(item, '{%s}image' % itunes_ns, {'href': image_url})

    tree = ET.ElementTree(rss)
    pretty_xml = xml.dom.minidom.parseString(ET.tostring(rss)).toprettyxml(indent='\t')
    with open(f"{podcast_data['alt_text'].lower().replace(' ', '_')}.rss", 'w', encoding='utf-8') as feed_file:
        feed_file.write(pretty_xml)
