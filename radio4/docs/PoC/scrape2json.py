import requests
from bs4 import BeautifulSoup
import json

# Funktion til at hente titel, beskrivelse og billede fra et RSS-feed
def fetch_rss_data(rss_url):
    try:
        # Kontroller, om URL'en er gyldig, inden der foretages en forespørgsel
        if not rss_url.startswith('http'):
            raise ValueError(f"Ugyldig URL: {rss_url}")
        
        rss_response = requests.get(rss_url)
        if rss_response.status_code != 200:
            raise Exception(f"Kunne ikke indlæse RSS-feed: {rss_url} med statuskode {rss_response.status_code}")
        
        # Parse RSS-feedet som XML
        rss_soup = BeautifulSoup(rss_response.content, 'xml')

        # Uddrag titel, beskrivelse og billed-URL fra RSS-feedet
        title = rss_soup.find('title').text if rss_soup.find('title') else 'Ingen titel'
        description = rss_soup.find('description').text if rss_soup.find('description') else 'Ingen beskrivelse'

        # Forsøg at finde billed-URL'en (fra itunes:image eller <image><url>)
        image_tag = rss_soup.find('itunes:image')
        image_url = image_tag['href'] if image_tag else None

        if not image_url:
            # Fallback til <image><url>
            image_url_tag = rss_soup.find('image').find('url') if rss_soup.find('image') else None
            image_url = image_url_tag.text if image_url_tag else 'Ingen billed-URL'

        return title, description, image_url
    
    except Exception as e:
        print(f"Fejl ved hentning af data fra {rss_url}: {e}")
        return None, None, None

# URL'en til siden, der indeholder RSS-feed-links
url = 'https://rssfeeds.radio4.dk/'

response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Kunne ikke indlæse siden med statuskode {response.status_code}")

# Parse hovedsidens HTML
soup = BeautifulSoup(response.content, 'html.parser')
rss_feed_data = []

# For at undgå duplikater
seen_urls = set()

# Find alle podcast-indgange
podcast_entries = soup.find_all('div', class_='podcast-entry')

for entry in podcast_entries:
    rssfeed_tag = entry.find('div', class_='podcast-rssfeed')

    if rssfeed_tag:
        rssfeed_url = rssfeed_tag.text.strip()

        # Undgå duplikater ved at kontrollere, om URL'en allerede er behandlet
        if rssfeed_url in seen_urls:
            continue
        seen_urls.add(rssfeed_url)

        # Hent titel, beskrivelse og billede fra RSS-feedet
        title, description, image_url = fetch_rss_data(rssfeed_url)

        if title and description:
            # Forbered data i det nødvendige format
            feed_data = {
                'title': title,
                'content': description,
                'program_url': rssfeed_url,
                'image_url': image_url  # Inkluder image_url i JSON-outputtet
            }
            rss_feed_data.append(feed_data)

# Filnavn til output
output_filename = 'r4dio.json'

# Gem dataene i en JSON-fil
with open(output_filename, 'w', encoding='utf-8') as json_file:
    json.dump(rss_feed_data, json_file, ensure_ascii=False, indent=2)

print(f"Data gemt i {output_filename}")
