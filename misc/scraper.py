import json
import requests
from tqdm import tqdm

auth_key = "din egen nøgle"

with open('data.json', 'r') as f:
    podcasts = json.load(f)

blacklist = []

# Opret en dictionary til at holde navnet på podcasten og dens episoder
podcast_dict = {}

total_podcasts = len(podcasts.keys())
processed_podcasts = 0

# Brug tqdm til at vise en fremdriftsindikator, mens scraperen kører
with tqdm(total=total_podcasts, dynamic_ncols=True, bar_format='{percentage:3.0f}%|{bar}| {n}/{total}') as pbar:
    # Lav en kopi af nøglerne i podcasts-dictionary'en for at undgå runtime-fejl
    for podcast_id in list(podcasts.keys()):
        pbar.update(1)
        if podcast_id in blacklist:
            continue
        
        podcast_data = podcasts[podcast_id]
        podcast_name = podcast_data['alt_text']
        podcast_data.setdefault('episodes', [])
        num_existing_episodes = len(podcast_data['episodes'])
        page_number = 0
        while True:
            response = requests.get(f"https://app.listentonews.com/api/v4/user/channels/{podcast_id}/items?order_by=newest&filter=&page={page_number}&per=60&auth={auth_key}")
            if not response.json():
                break
            episodes = response.json()
            for episode in episodes:
                # Tjek om episoden allerede eksisterer
                if not any(e['id'] == episode['id'] for e in podcast_data['episodes']):
                    podcast_data['episodes'].append({
                        'id': episode['id'],
                        'uri': episode['uri'],
                        'title': episode['title'],
                        'duration': episode['duration']['formatted'],
                        'publish_time': episode['publish_time'],
                        'description': episode['host_and_speaking_info'],
                        # Tilføj andet du vil scrape fra hjemmesiden via API-kaldet
                    })
            page_number += 1

        # Slå episoder sammen for podcasts med samme navn
        if podcast_name in podcast_dict:
            existing_podcast_data = podcasts[podcast_dict[podcast_name]]
            existing_episode_ids = set([episode['id'] for episode in existing_podcast_data['episodes']])
            new_episode_ids = set([episode['id'] for episode in podcast_data['episodes']])
            unique_new_episodes = [episode for episode in podcast_data['episodes'] if episode['id'] in new_episode_ids - existing_episode_ids]

            if unique_new_episodes:
                existing_podcast_data['episodes'].extend(unique_new_episodes)
                # Fjern andre forekomster af samme podcast
                del podcasts[podcast_id]
        else:
            # Tilføj ny podcast til dictionary
            podcast_dict[podcast_name] = podcast_id

    # Slå dictionary sammen med den originale podcasts-dictionary
    for podcast_name, podcast_id in podcast_dict.items():
        podcasts[podcast_id]['alt_text'] = podcast_name

    with open('data.json', 'w') as f:
        json.dump(podcasts, f, indent=2)
