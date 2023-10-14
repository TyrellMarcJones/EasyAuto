from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from auto_app_widget import CarScreen
from settings_screen import ConfigWindow
from camera_app import BackupCamera
from headlight_control import HeadlightsControlScreen
from MusicPlayer import MusicPlayer

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        title = kwargs.pop('title', '')
        content_widget = kwargs.pop('content_widget', None)
        super(BaseScreen, self).__init__(**kwargs)
        
        # Create the content for the screen
        self.add_widget(Label(text=title))
        
        if content_widget:
            # Create an instance of the content widget
            content = content_widget()
            content.size_hint_y = 1
            content.clearcolor = (0, 0.6, 0.1, 1.0)
        
            # Set the content widget as the root widget of the screen
            self.add_widget(content)


class SimpleScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(SimpleScreen, self).__init__(title="Simple", content_widget=CarScreen, **kwargs)


class SecondScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(title="New Screen", content_widget=ConfigWindow, **kwargs)


class BackupCameraScreen(Screen):
    def __init__(self, **kwargs):
        super(BackupCameraScreen, self).__init__( **kwargs)
        self.add_widget(BackupCamera())
        
class MusicPlayerScreen(Screen):
    def __init__(self, **kwargs):
        super(MusicPlayerScreen, self).__init__( **kwargs)
        self.add_widget(MusicPlayer())


class LightsScreen(Screen):
    def __init__(self, **kwargs):
        super(LightsScreen, self).__init__( **kwargs)
        self.add_widget(HeadlightsControlScreen())
        
   
   
def import_LightsScreen(sm):
    light_screen = LightsScreen()
    light_screen.name='Light Control Screen'
    sm.add_widget(light_screen)
    
def import_BackupCameraScreen(sm):
    backup_screen = BackupCameraScreen()
    backup_screen.name='Backup Camera Screen'
    sm.add_widget(backup_screen)
    
def import_MusicPlayerScreen(sm):
    music_screen = MusicPlayerScreen()
    music_screen.name='Music Player'
    sm.add_widget(music_screen)


def import_SecondScreen(sm):
    second_screen = SecondScreen()
    second_screen.name='Second Screen'
    sm.add_widget(second_screen)
    
def import_SimpleScreen(sm):
    simple_screen = SimpleScreen()
    simple_screen.name='Simple Screen'
    sm.add_widget(simple_screen)
        


