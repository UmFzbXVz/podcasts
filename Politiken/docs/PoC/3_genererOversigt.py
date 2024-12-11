import json
import os

def generate_index(data_file, output_directory, output_file):
    try:
        # Sikrer, at outputmappen eksisterer
        os.makedirs(output_directory, exist_ok=True)
        
        with open(data_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            index = []
            for podcast in data:
                # Håndter manglende 'latestEpisode' på en sikker måde
                if podcast.get('latestEpisode') and podcast['latestEpisode'].get('imageUrlSquareChannel'):
                    image_url = podcast['latestEpisode']['imageUrlSquareChannel']
                else:
                    image_url = "noimage"  # Standardværdi
                
                podcast_info = {
                    "title": podcast['name'],
                    "description": podcast['description'],
                    "image": image_url,
                    "id": podcast['id'],
                    "program_url": podcast['sectionUrls'][0]
                }
                index.append(podcast_info)
            
            output_path = os.path.join(output_directory, output_file)
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(index, outfile, ensure_ascii=False, indent=2)
            
            print(f"Indeksfilen '{output_path}' blev genereret med succes.")
    except FileNotFoundError:
        # Hvis datafilen ikke findes
        print("Datafilen blev ikke fundet.")
    except Exception as e:
        # Håndter andre fejl
        print(f"Der opstod en fejl: {str(e)}")

if __name__ == "__main__":
    data_file = "politiken.json"
    output_directory = "Politiken/docs"
    output_file = "oversigt.json"
    generate_index(data_file, output_directory, output_file)
