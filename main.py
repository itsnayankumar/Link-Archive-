import os
import subprocess
import questionary

def interactive_player():
    valid_extensions = ('.mkv', '.mp4', '.avi', '.webm')
    media_files = [f for f in os.listdir('.') if f.lower().endswith(valid_extensions)]

    if not media_files:
        print("No media files found in this directory!")
        return

    selected_file = questionary.select(
        "🍿 Select a file to play:",
        choices=media_files,
        use_indicator=True
    ).ask()

    if selected_file:
        print(f"\n▶️ Launching MPV for: {selected_file}")
        try:
            # Runs the file in MPV
            subprocess.run(['mpv', selected_file])
        except FileNotFoundError:
            print("Error: MPV is not installed in the system environment.")

if __name__ == "__main__":
    interactive_player()
