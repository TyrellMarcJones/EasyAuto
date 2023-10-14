import os
import tempfile
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from build_playlist import create_music_config
from functions import get_config_value

current_song_var = ""

from kivy.core.window import Window
from kivy.config import Config

Config.set('graphics', 'window_state', 'maximized')
Config.set('graphics', 'borderless', True)
Config.set('graphics', 'window_background_color', '#cacaca') # set to transparent

default_music_folder = get_config_value("Audio", "music_folder")

print(default_music_folder)

Builder.load_file('./musicplayer.kv')

mp3_files = []


class MusicPlayer(BoxLayout):
    playlist = ObjectProperty(None)
    current_song_label = ObjectProperty(None)
    song_position_label = ObjectProperty(None)
    song_duration_label = ObjectProperty(None)
    sound = None
    song_duration = NumericProperty(0)
    song_position = NumericProperty(0)
    is_playing = BooleanProperty(False)
    playlist_image = StringProperty('/opt/dash_os/app_icons/Menu.png')
    play_pause_image = StringProperty('/opt/dash_os/app_icons/play_icon.png')
    next_icon_image = StringProperty('/opt/dash_os/app_icons/next_icon.png')
    previous_icon_image = StringProperty('/opt/dash_os/app_icons/previous_icon.png')
    last_player_state = BooleanProperty(False)
    

    def __init__(self, **kwargs):
        super(MusicPlayer, self).__init__(**kwargs)
       
        # Load songs from the music folder
        self.load_songs()
        self.stop_song()
        self.size_hint_x=1

        # Play the last song in the list
        if mp3_files:
            last_song_path = mp3_files[-1]

            
    def load_songs(self):
    
                
        # Set the path to the directory containing the music files
        music_dir = "/home/pi/Music"
        
        
        # Initialize an empty list to store the MP3 filenames
        

        # Get a list of all the filenames in the music directory
        file_names = os.listdir(music_dir)
        
        # Set the path to the output file
        output_file = "music_files.txt"
        
        # Open the output file for writing
        with open(output_file, "w") as f:
            # Write each file name to a new line in the output file
            for file_name in file_names:
                if file_name.endswith(".mp3") and ("/home/pi/Music/" + file_name) not in mp3_files:
                    f.write("/home/pi/Music/" + file_name + "\n")
                    mp3_files.append("/home/pi/Music/" + file_name)
        
        
        # Create a temporary file for storing the list of songs
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp_file:
            # Write the list of songs to the temporary file
            music_folder = '/home/pi/Music'
            for song in os.listdir(music_folder):
                if song.endswith('.mp3'):
                    create_music_config(song)
                    temp_file.write(f"{os.path.join(music_folder, song)}\n")
            temp_file.flush()
            temp_file.seek(0)
            # Read the list of songs from the temporary file
            for song_path in temp_file:
                song_path = song_path.strip()
          

        if len(self.ids.playlist_box.children) > 0:
            self.playlist = self.ids.playlist_box.children[0]
            
    def play_song(self, btn=None, path=None):
        music_folder = '/home/pi/Music'
        if path is not None:
            song_path = path
            song_name = os.path.basename(path)
        else:
            song_path = os.path.join(music_folder, btn.text)
            song_name = btn.text
            
            
        if self.sound is not None:
            self.sound.stop()
            self.song_position = 0
            
        self.sound = SoundLoader.load(song_path)
        self.sound.bind(on_load=self.set_song_duration)
        
        if self.sound:
            self.set_song_duration(self.sound)
            self.song_duration = self.sound.length
            self.current_song_label.font_name = "/opt/dash_os/fonts/Roboto-Black.ttf"
            self.current_song_label.size = self.current_song_label.texture_size
            self.current_song_label.padding_x: 100
            
            hex_color = "#808080"
            red = int(hex_color[1:3], 16) / 255.0
            green = int(hex_color[3:5], 16) / 255.0
            blue = int(hex_color[5:7], 16) / 255.0
            alpha = 1.0  # You can adjust the alpha value if needed
            
            # Create the RGBA color tuple
            text_color = (red, green, blue, alpha)


            self.current_song_label.color = text_color
            self.current_song_label.text = song_name
            self.current_song_var = os.path.join('/home/pi/Music', song_name)
            with open("currentSong.txt", "w") as f:
                f.write(self.current_song_var + "\n")
                       
            self.current_song = song_name  # Store the current playing song
            
            if self.last_player_state:
                self.is_playing = False
                self.stop_song()
            else:
                self.is_playing = True
                self.sound.play()
                Clock.schedule_interval(self.update_song_position, 1 / 60)
                self.update_song_duration_label()
                self.update_play_pause_button()

    def set_song_duration(self, sound):
        self.song_duration = sound.length
                
    def update_song_position(self, dt):
        if self.sound is not None:
            self.song_position = self.sound.get_pos()
            self.update_song_position_label()
            self.update_song_duration_label()


    def update_song_duration_label(self):
        minutes = int(self.song_duration // 60)
        seconds = int(self.song_duration % 60)
        self.song_duration_label.color = [0,2,3,2]
        self.song_duration_label.text = f"{minutes:02d}:{seconds:02d}"

    def update_song_position_label(self):
        minutes = int(self.song_position // 60)
        seconds = int(self.song_position % 60)
        self.song_position_label.color = [0,2,3,2]
    
        self.song_position_label.text = f"{minutes:02d}:{seconds:02d}"
        
    def stop_song(self):
        if self.sound is not None:
            if self.is_playing:
                self.sound.stop()
                self.is_playing = False
                self.last_player_state = True
            else:
                self.sound.play()
                self.is_playing = True
                self.last_player_state = False
        self.update_play_pause_button()
        
    def next_song(self):
        if len(mp3_files) > 0:
            # Get the current song index
            current_song_index = mp3_files.index(self.current_song_var)
            # Get the previous song index, wrapping around to the end if necessary
            if current_song_index == len(mp3_files) -1:
                next_song_index = 0
            else:
                next_song_index = current_song_index + 1
            
            
            
            # Get the path to the previous song
            next_song_path = mp3_files[next_song_index]
            
            # Play the previous song
            self.play_song(path=next_song_path)
            
    def previous_song(self):
        if len(mp3_files) > 0:
            # Get the current song index
            current_song_index = mp3_files.index(self.current_song_var)
            # Get the previous song index, wrapping around to the end if necessary
            if current_song_index == 0:
                previous_song_index = len(mp3_files) - 1
            else:
                previous_song_index = current_song_index - 1
            
            # Get the path to the previous song
            previous_song_path = mp3_files[previous_song_index]
            
            # Play the previous song
            self.play_song(path=previous_song_path)

    def on_touch_up(self, touch):
        if self.sound is not None and self.ids.song_progress.collide_point(*touch.pos):
            progress = (touch.pos[0] - self.ids.song_progress.x) / self.ids.song_progress.width
            self.sound.seek(progress * self.sound.length)

    def update_play_pause_button(self):
        if self.is_playing:
            self.play_pause_image = '/opt/dash_os/app_icons/pause_icon.png'
        else:
            self.play_pause_image = '/opt/dash_os/app_icons/play_icon.png'
            
    def open_second_screen(self):
        try:
            second_screen = BoxLayout(orientation='vertical')
            ss_playlist_box = GridLayout(cols=1, size_hint=(1, 0.8))
            print("-----------------")
            for song in mp3_files:
                print(song)
                btn = Button(text=song, size_hint_y=None, height=40)
                btn.bind(on_release=self.play_song)
                ss_playlist_box.add_widget(btn)
            second_screen.add_widget(ss_playlist_box)
            close_button = Button(text='Close', size_hint=(1, 0.1))
            close_button.bind(on_release=self.close_second_screen)
            second_screen.add_widget(close_button)
            self.popup_window = Popup(title='Songs', content=second_screen, size_hint=(0.8, 0.8))
            self.popup_window.open()
        except Exception as e:
               print(e)

    def close_second_screen(self, instance):
        self.popup_window.dismiss()
        
class MusicApp(App):
    def build(self):
        return MusicPlayer()

if __name__ == '__main__':

    MusicApp().run()

