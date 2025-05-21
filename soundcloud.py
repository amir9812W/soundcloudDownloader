import tkinter
import customtkinter
from sclib import SoundcloudAPI, Track, Playlist
import threading
import os  # For filename sanitization
# i guess this is the end of the project fr fr


customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('blue')

app = customtkinter.CTk()
app.geometry("720x480")
app.title('SoundCloud Downloader')

# Global variables
progress = None
status_label = None
track_playList = "Track"
download_active = False

def update_progress(progress_value, message=""):
    progress.set(progress_value)
    if status_label:
        status_label.configure(text=message)
    app.update_idletasks()

def download_track(url_var, progress_callback):
    global download_active
    try:
        download_active = True
        api = SoundcloudAPI()
        soundcloud_url = url_var.get().strip()
        
        if not soundcloud_url:
            progress_callback(0, "Error: Please enter a URL")
            return

        progress_callback(0.1, "Connecting to SoundCloud...")
        
        if track_playList == 'Track':
            track = api.resolve(soundcloud_url)
            
            if not isinstance(track, Track):
                progress_callback(0, "Error: Not a valid track URL")
                return

            filename = f'./{sanitize_filename(f"{track.artist} - {track.title}")}.mp3'
            
            progress_callback(0.3, "Downloading track...")
            with open(filename, 'wb+') as file:
                track.write_mp3_to(file)
            
            progress_callback(1.0, "Download complete!")
            
        elif track_playList == 'Playlist':
            playlist = api.resolve(soundcloud_url)
            
            if not isinstance(playlist, Playlist):
                progress_callback(0, "Error: Not a valid playlist URL")
                return

            total_tracks = len(playlist.tracks)
            for i, track in enumerate(playlist.tracks):
                if not download_active:  # Allow cancellation
                    break
                    
                progress = 0.3 + (i / total_tracks) * 0.7
                progress_callback(progress, f"Downloading track {i+1}/{total_tracks}...")
                
                filename = f'./{sanitize_filename(f"{track.artist} - {track.title}")}.mp3'
                try:
                    with open(filename, 'wb+') as file:
                        track.write_mp3_to(file)
                except Exception as e:
                    progress_callback(progress, f"Error on track {i+1}: {str(e)}")
                    continue
            
            if download_active:
                progress_callback(1.0, f"Downloaded {total_tracks} tracks!")
                
    except Exception as e:
        progress_callback(0, f"Error: {str(e)}")
    finally:
        download_active = False

def startDownload():
    global progress, status_label
    
    if download_active:
        return
        
    # Reset UI
    progress.set(0)
    if status_label:
        status_label.configure(text="Starting download...")
    
    download_thread = threading.Thread(
        target=download_track,
        args=(url_var, update_progress),
        daemon=True
    )
    download_thread.start()

def changer(choice):
    global track_playList
    track_playList = choice
    print(f"Download mode set to: {track_playList}")

# UI Elements
title = customtkinter.CTkLabel(app, text='Insert a SoundCloud link')
title.pack(padx=10, pady=10)

# Link input
url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack(pady=10)

# Download type selector
option_var = customtkinter.StringVar(value="Track")
option = customtkinter.CTkOptionMenu(
    app, 
    values=["Track", "Playlist"], 
    command=changer,
    variable=option_var
)
option.pack(pady=10)

# Progress bar
progress = customtkinter.CTkProgressBar(app, width=400)
progress.set(0)
progress.pack(pady=10)

# Status label
status_label = customtkinter.CTkLabel(app, text="Waiting for download...")
status_label.pack()

# Download button
download = customtkinter.CTkButton(app, text='Download', command=startDownload)
download.pack(pady=20)

app.mainloop()
