import os
import subprocess
import questionary

def main():
    # Looking for media files in the container
    valid_exts = ('.mkv', '.mp4')
    files = [f for f in os.listdir('.') if f.lower().endswith(valid_exts)]
    
    if not files:
        print("No media files found!")
        return

    selected = questionary.select("Select file:", choices=files).ask()
    
    if selected:
        print(f"Playing {selected}...")
        subprocess.run(['mpv', selected])

if __name__ == "__main__":
    main()
