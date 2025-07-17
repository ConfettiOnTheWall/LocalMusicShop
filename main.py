import internetarchive
import os

# fetches data and downloads files
def search_album(artist, album, audio_format='FLAC', results_limit=5):
    query = f'title:("{album}") AND creator:("{artist}") AND format:("{audio_format}")'

    try:
        results = internetarchive.search_items(
            query,
            params = {'sort[]': 'downloads desc', 'rows': results_limit}
        )
    except Exception as e:
        print(f"ERROR: Failed to connect to Internet Archive\n{e}")
        return[]

    valid_albums = []
    for item in results:
        identifier = item['identifier']
        try:
            metadata = internetarchive.get_item(identifier).metadata
            title = metadata.get('title', album)

            files = internetarchive.get_files(identifier)
            audio_files = [f for f in files if f.name.lower().endswith(f".{audio_format.lower()}")]

            if audio_files:
                valid_albums.append({
                    "identifier": identifier, 
                    "title": title,
                    "artist": artist, 
                    "tracks": len(audio_files),
                    "format": audio_format, 
                    "files": audio_files
                })
        except Exception:
            continue
    
    return valid_albums

def download_album(album_data):
    safe_title = "".join(c for c in album_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    album_dir = os.path.join("albums", f"{album_data['artist']} - {safe_title}")
    os.makedirs(album_dir, exist_ok=True)
    print(f"\nDownloading {album_data['tracks']} tracks to {album_dir}")

    try:
        for file in album_data['files']:
            output_path = os.path.join(album_dir, os.path.basename(file.name))
            if os.path.exists(output_path):
                print(f"Already exists: {os.path.basename(file.name)}")
                continue
            print(f"Downloading: {os.path.basename(file.name)}")
            file.download(output_path)
        print(f"\nDONE: Album saved to {album_dir}")
        return True
    except Exception as e:
        print(f"ERROR: Occured an error during download\n{e}")
        return False

# displays menu and gets input from user
def prompt_user_to_choose_option(options, album_name):
    print(f"Options found for '{album_name}':")
    for i, option in enumerate(options):
        print(f"[{i + 1}] {option['title']} ({option['tracks']} songs)")
    print("[0] Skip")

    while True:
        try:
            choice = int(input("\n> "))
            if 0 <= choice <= len(options):
                if choice == 0:
                    print("OK: Skipping to the next album")
                    return None
                return options[choice - 1]
            else:
                print("ERROR: Invalid option, try again")
        except ValueError:
            print("ERROR: Only numeric values accepted")

# manages the task list and coordinates the execution flow
def process_album_search(artist, album, audio_format):
    print(f"\n{'='*50}\nSearching for: {album} - {artist}")

    options = search_album(artist, album, audio_format=audio_format)

    if not options:
        print(f"ERROR: No valid download option found")
        return
    
    selected = prompt_user_to_choose_option(options, album)

    if selected:
        download_album(selected)

if __name__ == "__main__":
    os.makedirs("albums", exist_ok=True)

    albums = {
        # e.g. "Eminem": ["The Marshall Mathers LP", "The Eminem Show"],
        "Death Grips": ["Exmilitary"],
    }
    AUDIO_FORMAT = "MP3"

    for artist, album_list in albums.items():
        for album in album_list:
            process_album_search(artist, album, audio_format=AUDIO_FORMAT)

    print(f"\n{'='*50}\nOK: Process finalized")