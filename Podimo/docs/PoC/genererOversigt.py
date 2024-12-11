import json
import os

def generate_index(data_file, output_directory, output_file):
    try:
        # Sikrer, at output-mappen eksisterer
        os.makedirs(output_directory, exist_ok=True)
        
        with open(data_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            index = []
            for podcast in data:
                podcast_info = {
                    "title": podcast.get('title', ''),
                    "description": podcast.get('description', ''),
                    "id": podcast.get('id', ''),
                    "episodeCount": podcast.get('episodeCount', ''),
                    "coverImageUrl": podcast.get('coverImageUrl', '')
                }
                index.append(podcast_info)
            
            output_path = os.path.join(output_directory, output_file)
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(index, outfile, ensure_ascii=True, indent=2)
            
            print(f"Indeksfilen '{output_path}' blev genereret med succes.")
    except FileNotFoundError:
        print("Datafilen blev ikke fundet.")
    except json.JSONDecodeError:
        print("Fejl ved afkodning af JSON fra datafilen.")
    except Exception as e:
        print(f"Der opstod en fejl: {str(e)}")

if __name__ == "__main__":
    data_file = "podimo.json"
    output_directory = "Podimo/docs"
    output_file = "podimo.json"
    generate_index(data_file, output_directory, output_file)
