import requests
import json
import os
import time

# Basis-URL til at anmode om podcastdata
base_url = "https://politiken.dk/webservice/podcast/channels/"

# Sender en GET-anmodning til basis-URL'en
response = requests.get(base_url)

# Tjekker, om anmodningen var succesfuld
if response.status_code == 200:
    # Pars JSON-svaret
    podcast_data = response.json()
    
    # Udskriv hver podcasts titel, og hent episoder
    for podcast in podcast_data:
        try:
            podcast_id = podcast["id"]
            episodes_url = f"{base_url}{podcast_id}/episodes"
            
            # Sender en GET-anmodning til episoder-URL'en
            episodes_response = requests.get(episodes_url)
            
            # Tjekker, om anmodningen var succesfuld
            if episodes_response.status_code == 200:
                # Pars svaret for episoder
                episodes_data = episodes_response.json()
                
                # Tilføj episodedata til podcastindgangen
                podcast['episodes'] = episodes_data
                print(f"Episoder blev tilføjet succesfuldt til podcast: {podcast['name']}")
            else:
                print(f"Kunne ikke hente episoder for {podcast_id}. Statuskode: {episodes_response.status_code}")
        except Exception as e:
            print(f"Der opstod en fejl under behandling af podcast: {podcast['name']}. Fejl: {e}")
    
    # Gem de opdaterede podcastdata med episoder i en lokal JSON-fil
    with open("politiken.json", "w", encoding='utf-8') as file:
        json.dump(podcast_data, file, indent=2, ensure_ascii=False)
else:
    print(f"Kunne ikke hente data. Statuskode: {response.status_code}")
