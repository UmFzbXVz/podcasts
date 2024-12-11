import json

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f, cls=CustomDecoder)

class CustomDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        # Erstatter LINE SEPARATOR-tegnet med et mellemrum før afkodning
        s = s.replace('\u2028', ' ')
        return super().decode(s, **kwargs)
def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_podcast_by_id(podcasts, podcast_id):
    for podcast in podcasts:
        if podcast['id'] == podcast_id:
            return podcast
    return None

def episode_exists(podcast, episode_id):
    for episode in podcast['episodes']:
        if episode['id'] == episode_id:
            return True
    return False

def add_new_episode(podcasts, new_episodes):
    for new_episode in new_episodes:
        podcast_id = new_episode['podcastId']
        podcast = find_podcast_by_id(podcasts, podcast_id)
        if podcast:
            if not episode_exists(podcast, new_episode['id']):
                podcast['episodes'].append(new_episode)
                podcast['episodeCount'] += 1
                print(f"Afsnittet '{new_episode['title']}' tilføjet til podcasten '{podcast['title']}'!")
        else:
            print(f"Ingen podcast fundet med id '{podcast_id}'.")

def main():
    podimo_filename = 'podimo.json'
    new_filename = 'indsætMITMdata.json'

    # Indlæs eksisterende podcastdata
    podcasts = load_json(podimo_filename)

    # Indlæs nye episodedata
    new_data = load_json(new_filename)
    new_episodes = new_data['data']['episodes']

    # Tilføj nye episoder til de tilsvarende podcasts
    add_new_episode(podcasts, new_episodes)

    # Gem de opdaterede data tilbage til filen podimo.json
    save_json(podimo_filename, podcasts)

if __name__ == "__main__":
    main()
