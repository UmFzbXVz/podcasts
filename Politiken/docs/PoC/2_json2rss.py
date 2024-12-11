import json
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime

ITUNES_NAMESPACE = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ET.register_namespace('itunes', ITUNES_NAMESPACE)

def seconds_to_hhmmss(seconds):
    # Konverter sekunder til HH:MM:SS-format
    hours, remainder = divmod(round(float(seconds)), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0:
        return "{:02d}:{:02d}".format(minutes, seconds)
    else:
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

def datetime_to_rfc822(dt):
    # Konverter datetime til RFC822-format
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')

def generate_rss(podcast_data):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    title = ET.SubElement(channel, "title")
    title.text = podcast_data['name'].strip()
    link = ET.SubElement(channel, "link")
    link.text = podcast_data['sectionUrls'][0].strip()
    description = ET.SubElement(channel, "description")
    description.text = podcast_data['description'].strip()

    # Håndter manglende latestEpisode på en hensigtsmæssig måde
    if podcast_data.get('latestEpisode') and podcast_data['latestEpisode'].get('imageUrlSquareChannel'):
        image_url = podcast_data['latestEpisode']['imageUrlSquareChannel'].strip()
    else:
        image_url = "noimage"  # Standardværdi eller pladsholderbillede-URL

    image = ET.SubElement(channel, "{%s}image" % ITUNES_NAMESPACE)
    image.set("href", image_url)

    existing_guids = set()  # Til at gemme eksisterende GUIDs

    if 'episodes' in podcast_data and podcast_data['episodes']:
        for episode in podcast_data['episodes']:
            episode_guid = str(episode['guid'])

            # Spring episoder over, der allerede er behandlet
            if episode_guid in existing_guids:
                continue

            item = ET.SubElement(channel, "item")
            episode_title = ET.SubElement(item, "title")
            episode_title.text = episode['title'].strip()
            episode_description = ET.SubElement(item, "description")
            episode_description.text = episode['description'].strip()
            pub_date = ET.SubElement(item, "pubDate")
            pub_date.text = datetime_to_rfc822(datetime.strptime(episode['publishDate'], '%Y-%m-%dT%H:%M:%S')).strip()

            guid = ET.SubElement(item, "guid")
            guid.text = episode_guid
            guid.set("isPermaLink", "false")

            enclosure = ET.SubElement(item, "enclosure")
            enclosure.set("url", episode['audioFileLink'].strip())
            enclosure.set("length", str(episode['fileSize']))
            enclosure.set("type", episode['mimeType'].strip())

            itunes_duration = ET.SubElement(item, "{%s}duration" % ITUNES_NAMESPACE)
            itunes_duration.text = seconds_to_hhmmss(episode['durationInSecond']).strip()

            existing_guids.add(episode_guid)
    else:
        # Hvis podcasten ikke har episoder, inkluderes kun kanaloplysninger i RSS-filen
        print(f"Podcast '{podcast_data['name']}' har ingen episoder. RSS-filen vil kun indeholde kanaldetaljer.")

    rss_content = ET.tostring(rss, encoding='utf-8')
    return xml.dom.minidom.parseString(rss_content).toprettyxml(indent="  ")

def generate_rss_files(data_file):
    folder_name = "Politiken/RSS"
    try:
        # Opret mappen, hvis den ikke allerede findes
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(data_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for podcast in data:
                rss_filename = f"{folder_name}/{podcast['id']}.rss"
                rss_content = generate_rss(podcast)
                with open(rss_filename, 'w', encoding='utf-8') as rss_file:
                    rss_file.write(rss_content)
                print(f"RSS-filen '{rss_filename}' blev genereret med succes.")
    except FileNotFoundError:
        # Hvis datafilen ikke findes
        print("Datafilen blev ikke fundet.")
    except Exception as e:
        # Håndter andre fejl
        print(f"Der opstod en fejl: {str(e)}")

if __name__ == "__main__":
    data_file = "politiken.json"
    generate_rss_files(data_file)
