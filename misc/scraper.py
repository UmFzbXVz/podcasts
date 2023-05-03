import json
import requests

with open('fil_med_json', 'r') as f:
    podcasts = json.load(f)

for podcast_id, podcast_data in podcasts.items():
    podcast_data.setdefault('episodes', [])
    page_number = 0
    while True:
        response = requests.get(f"https://app.listentonews.com/api/v4/user/channels/{podcast_id}/items?order_by=newest&filter=&page={page_number}&per=60&auth={auth_key}")
        if not response.json():
            break
        episodes = response.json()
        for episode in episodes:
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

with open('fil_med_json', 'w') as f:
    json.dump(podcasts, f, indent=4)
