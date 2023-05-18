import argparse
import json 
import xml.etree.ElementTree as ET
from datetime import datetime
import xml.dom.minidom
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def create_rss_feed(podcast_data):
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')

    append_basic_tags(channel, podcast_data)
    append_itunes_tags(channel, podcast_data)

    seen_ids = set()
    for episode in podcast_data['episodes']:
        if episode['id'] not in seen_ids:
            seen_ids.add(episode['id'])
            item = ET.SubElement(channel, 'item')
            append_episode_basic_tags(item, episode)
            append_episode_itunes_tags(item, episode)
            append_enclosure_tag(item, episode)

    write_rss_feed_to_file(rss, podcast_data)

def append_basic_tags(channel, podcast_data):
    ET.SubElement(channel, 'title').text = escape(podcast_data['alt_text'])
    ET.SubElement(channel, 'link').text = podcast_data['url']
    ET.SubElement(channel, 'description').text = escape(podcast_data['description'])
    ET.SubElement(channel, 'language').text = 'da-DK'

def append_itunes_tags(channel, podcast_data):
    itunes_ns = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
    ET.register_namespace('itunes', itunes_ns)

    for tag in ['subtitle', 'summary', 'author']:
        if tag in podcast_data:
            ET.SubElement(channel, '{%s}%s' % (itunes_ns, tag)).text = escape(podcast_data[tag])

    if 'image_url' in podcast_data:
        image_url = podcast_data['image_url']
        ET.SubElement(channel, '{%s}image' % itunes_ns, {'href': image_url})
    if 'category' in podcast_data:
        ET.SubElement(channel, '{%s}category' % itunes_ns, {'text': escape(podcast_data['category'])})

def append_episode_basic_tags(item, episode):
    publish_time = episode['publish_time'].replace('Z', '+0000')
    ET.SubElement(item, 'title').text = escape(episode['title'])
    ET.SubElement(item, 'link').text = episode['uri']
    description_text = get_description_text(episode)
    ET.SubElement(item, 'description').text = description_text
    ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = episode['uri']
    pub_date = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%a, %d %b %Y %H:%M:%S %z')
    ET.SubElement(item, 'pubDate').text = pub_date

def get_description_text(episode):
    description_html = episode.get('description', '')
    if description_html is not None and description_html.strip() != '':
        description_text = BeautifulSoup(description_html, 'html.parser').get_text()
    else:
        description_text = ''
    return description_text

def append_episode_itunes_tags(item, episode):
    itunes_ns = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
    duration_formatted = convert_duration_to_formatted_string(episode['duration'])
    ET.SubElement(item, '{%s}duration' % itunes_ns).text = duration_formatted

    for tag in ['subtitle', 'summary', 'author']:
        if tag in episode:
            ET.SubElement(item, '{%s}%s' % (itunes_ns, tag)).text = escape(episode[tag])

def append_enclosure_tag(item, episode):
    ET.SubElement(item, 'enclosure', {
        'url': episode['uri'],
        'length': '31457280',
        'type': 'audio/mpeg'
    })

def convert_duration_to_formatted_string(duration):
    duration_parts = list(map(int, duration.split(':')))
    if len(duration_parts) == 2:
        duration_parts.insert(0, 0)
    duration_formatted = f"{duration_parts[0]:02d}:{duration_parts[1]:02d}:{duration_parts[2]:02d}"
    return duration_formatted

def write_rss_feed_to_file(rss, podcast_data):
    folder_name = podcast_data['alt_text'][0]
    if folder_name.isdigit():
        folder_name = '0-9'
    file_name = podcast_data['alt_text'].replace('/', '_').replace('?', '_').replace(' ', '_').lower()
    folder_path = os.path.join('podcasts', folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{file_name}.rss")
    with open(file_path, 'w', encoding='utf-8') as feed_file:
        xml_string = xml.dom.minidom.parseString(ET.tostring(rss)).toprettyxml()
        feed_file.write(xml_string)

def parse_args():
    parser = argparse.ArgumentParser(description='Værktøj til at generere RSS-feeds fra podcastinformation i data.json')
    parser.add_argument('-a', '--all', action='store_true', help='Generér RSS-feeds til samtlige podcasts')
    parser.add_argument('-i', '--ids', type=str, help='Komma-separeret liste af podcast-IDs til RSS-generering')
    return parser.parse_args()

def main():
    args = parse_args()

    with open('data.json', 'r') as f:
        podcasts = json.load(f)

    if args.all:
        for podcast_data in podcasts.values():
            create_rss_feed(podcast_data)
    elif args.ids:
        ids = args.ids.split(',')
        for id in ids:
            if id in podcasts:
                podcast_data = podcasts[id]
                create_rss_feed(podcast_data)
            else:
                print(f'Podcast med ID {id} ikke fundet i data.json')

if __name__ == '__main__':
    main()
