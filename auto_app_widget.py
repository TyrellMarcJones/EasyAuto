import json
import subprocess
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime
from kivy.utils import get_color_from_hex
from kivy_garden.mapview import MapView
from kivy.graphics import RoundedRectangle
from MusicPlayer import MusicPlayer
from kivy.uix.screenmanager import ScreenManager, Screen
import configparser
from main import fscreen
from kivy.graphics import Color, Rectangle


class MenuScreen(Screen):
    pass

class CustomMusicPlayer(BoxLayout):
    def __init__(self, **kwargs):
        super(CustomMusicPlayer, self).__init__(**kwargs)
        music_player = MusicPlayer()  # set is_infotainment flag to True
        self.add_widget(music_player)
        self.size_hint = (1, .5)
        self.minimum_height = 200
        
class CustomButton(Button):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.background_color = (1, 1, 1, 1)
        self.markup = True
        self.border = (1, 1, 1, 1)

class CarScreen(BoxLayout):
    def __init__(self, **kwargs):
        
                # ...
        super(CarScreen, self).__init__(**kwargs)
        
        self.widget_container = GridLayout()

        with self.canvas.before:
            Color(0, 0, 0, .8)  # White color
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
        
        
        with open("/opt/dash_os/button_scripts.json", "r") as f:
            self.button_scripts = json.load(f)
            
        self.orientation = "vertical"

        # Load button images and scripts configuration
        with open("/opt/dash_os/button_images.json", "r") as f:
            self.button_images = json.load(f)
        with open("/opt/dash_os/button_images.json", "r") as f:
            self.button_scripts = json.load(f)

        # Set the background color or image based on the config file
        self.load_config()


        # Create a ScrollView and GridLayout for the upper row of buttons
        scroll_view = ScrollView(
            size_hint=(1, None), height=150, do_scroll_x=True, do_scroll_y=False
        )
        upper_buttons_grid = GridLayout(
            cols=10, size_hint_x=None, padding=[20, 20, 20, 20], spacing=20
        )
        upper_buttons_grid.bind(minimum_width=upper_buttons_grid.setter("width"))

        # Create buttons and add them to the upper GridLayout
        for i in range(10):
            btn_image = self.button_images.get(f"button{i + 1}", "")
            btn = CustomButton(
                text=f"{i + 1}",
                font_size=16,
                size_hint_x=None,
                background_normal="./app_icons/quick_button.png",
            )
            btn.bind(on_release=self.run_script)
            upper_buttons_grid.add_widget(btn)

        scroll_view.add_widget(upper_buttons_grid)
        self.add_widget(scroll_view)
        
        ##backup_camera = BackupCamera()
        ##self.add_widget(backup_camera)
        
        #simple_map = fscreen()
        #self.add_widget(simple_map)
        
        self.widget_container = GridLayout(cols = 2, padding = 20, spacing = 20)
        # Add media player panel
        self.media_player_panel = CustomMusicPlayer(
            padding=[20, 20, 20, 20], size_hint=(1, 0.1), orientation="horizontal"
        )
        self.widget_container.add_widget(self.media_player_panel)
        
        self.simple_map = MapView(zoom=10, lat=36, lon=-115)

        self.widget_container.add_widget(self.simple_map)
        
        self.add_widget(self.widget_container)
        
        
        
                
    def _update_rect(self, instance, value):
        
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        print(Window.size[0])
        
        if Window.size[0] < Window.size[1]:
            print("Vertical")
            self.remove_widget(self.widget_container)
            self.widget_container = GridLayout(cols = 1, padding = 20, spacing = 20)
            # Add media player panel
            self.media_player_panel = CustomMusicPlayer(
                padding=[20, 20, 20, 20], size_hint=(1, 0.1), orientation="horizontal"
            )
            self.widget_container.add_widget(self.media_player_panel)
            
            self.simple_map = MapView(zoom=10, lat=36, lon=-115)

            self.widget_container.add_widget(self.simple_map)
            
            self.add_widget(self.widget_container)
        elif Window.size[0] > Window.size[1]:
            print("Vertical")
            self.remove_widget(self.widget_container)
            self.widget_container = GridLayout(cols = 2, padding = 20, spacing = 20)
            # Add media player panel
            self.media_player_panel = CustomMusicPlayer(
                padding=[20, 20, 20, 20], size_hint=(1, 0.1), orientation="horizontal"
            )
            self.widget_container.add_widget(self.media_player_panel)
            
            self.simple_map = MapView(zoom=10, lat=36, lon=-115)

            self.widget_container.add_widget(self.simple_map)
            
            self.add_widget(self.widget_container)
            
        
    def load_config(self):
        with open("/opt/dash_os/config.json", "r") as f:
            config = json.load(f)
            if "background_color" in config:
                bg_color = config["background_color"]
                Window.clearcolor = get_color_from_hex(bg_color)
            elif "background_image" in config:
                bg_image = config["background_image"]
                self.canvas.before.clear()
                with self.canvas.before:
                    Rectangle(
                        source=bg_image, pos=self.pos, size=self.size
                    )

    def update_time_date(self, *args):
        now = datetime.now()
        self.time_date_label.text = now.strftime("%I:%M %p")

    def start_camera(self):
        self.camera.start()
            
    def run_script(self, instance):
        button_number_str = instance.text.strip()
        if button_number_str:
            button_number = int(button_number_str.split(" ")[-1])
            if button_number <= 10:
                script_path = self.button_scripts.get(f"button{button_number}", "")
                if script_path:
                    print(script_path)

                    #subprocess.Popen(["bash", script_path])
            elif button_number == 16:
                self.start_camera()
                
class CarScreenApp(App):
    def build(self):
        return CarScreen()

if __name__ == "__main__":
    CarScreenApp().run()


