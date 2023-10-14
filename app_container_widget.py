import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import xml.etree.ElementTree as ET
from app_container_assets import DateButton, TimeButton, DraggableButton, NavigationLayout,top_bar_layout
from functions import get_config_value, sort_buttons_by_rank, cell_distance, get_grid_centers, string_to_array,execute_functions_from_file
from screen_assets import SecondScreen
import screen_assets
from kivy.uix.image import AsyncImage
import alsaaudio
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen
from spring_board import snap_screen_container
import os
import sys
from kivy.core.window import Window


set_cols = int(get_config_value("Appearance", "grid_cols"))
set_rows = int(get_config_value("Appearance", "grid_rows"))
button_color = get_config_value("Appearance", "button_color")
window_configuration = get_config_value("Display", "display_mode")

print("-------" + str(window_configuration))
if window_configuration == "fullscreen":
    
    Window.fullscreen = 'auto'

if button_color != "None":
    button_color = get_config_value("Appearance", "button_color")
    button_color = string_to_array(button_color)
else:
    button_color = [1,1,1,1]
    
background_image_path = get_config_value("Appearance", "background_image")
background_image = Image(source=background_image_path)

button_width = 100
button_height = 100

        
class MyApp(App):
    pid = os.getpid()
    print("PID:", pid)
    # Assume 'kivy_variable' is the variable you want to save
    kivy_variable = str(pid)
    
    # Set the system environment variable
    os.environ["SYSTEM_VARIABLE_NAME"] = str(kivy_variable)
            
    def set_initial_button_positions(self, layout):
        grid_centers = get_grid_centers(layout)
    
        # Reverse the order of the grid centers
        grid_centers = list(reversed(grid_centers))
    
        for i, button in enumerate(layout.children, start=0):
            # Set the initial position of the button
            center_x, center_y = grid_centers[i]
            button.pos = (center_x - button.width / 2, center_y - button.height / 2)
            button.pos_hint = {'x': button.pos[0] / layout.width, 'y': button.pos[1] / layout.height}

    def on_size_change(self, layout, size):
        # Print the main window size
        print(f"Window size: {size}")
        grid_centers = get_grid_centers(layout)
        layout.spacing = ((size[0]-(button_width * set_cols))/ set_cols , (size[1]-(button_height * set_rows)) / set_rows)
        layout.padding = ((size[0]-(button_width * set_cols))/ set_cols / 2 ,(size[1]-(button_height * set_rows))/ set_rows / 2,0,0)
        # update the size and position of the buttons when the window size changes
        for button in layout.children:
            # adjust the button's padding and border to fit within its grid cell
            button.padding = (0, 25)
            button.border = [0, 0, 0, 0]
            button.pos_hint = (1,.5)
        # redraw grid lines
        self.draw_grid_lines(layout)
        self.set_initial_button_positions(layout)
        

    def draw_grid_lines(self, layout):
        layout.canvas.after.clear()
        with layout.canvas.after:
            # draw horizontal grid lines
            #for i in range(1, layout.rows):
            #    Line(points=[0, i * layout.height / layout.rows, layout.width, i * layout.height / layout.rows], width=1)
            # draw vertical grid lines
            #for i in range(1, layout.cols):
            #    Line(points=[i * layout.width / layout.cols, 0, i * layout.width / layout.cols, layout.height], width=1)
            # draw blue circles and counter in the center of each grid cell
            grid_centers = get_grid_centers(layout)
            circle_radius = 10
            total_cells = len(grid_centers)
            #for i, (center_x, center_y) in enumerate(grid_centers):
                #row = layout.rows - 1 - i // layout.cols
                #col = i % layout.cols
                #index = row * layout.cols + col
                #Color(0, 0, 1, 1)  # blue color
                #Ellipse(pos=(center_x - circle_radius, center_y - circle_radius), size=(circle_radius * 2, circle_radius * 2))
                #Label(text=str(index), pos=(center_x - circle_radius, center_y - circle_radius), color=(0, 1, 0, 1), font_size=circle_radius)
    
    

    def snap_screen_container(self, screen_config, screen_manager, carousel):
    
        # set the initial window size
        layout = GridLayout(cols=set_cols, rows=set_rows)
        layout.bind(size=self.on_size_change)

        # read button information from XML file
        tree = ET.parse(screen_config)
        root = tree.getroot()

        # create a list of all the buttons in reverse order
        buttons = []
        
        coord = []
    
        distance = 0
        
        place_holders = []

        for button_elem in reversed(root.findall('button')):
            coord.append(button_elem.find('row').text + "," + button_elem.find('col').text)
        
        button_count = 0
        last_coord =(set_rows, set_cols)
        print(root.findall('button'))
        
        for button_elem in reversed(root.findall('button')):
            try:
                id_ = button_elem.find('id').text
            except:
                id_ = ''
            if id_ == 'time':
                # create time button and add it to the list
                time_button = TimeButton(text='Time', size_hint=(None, None),font_name="DS-Digital.ttf", font_size=36,  background_color = button_color)
                time_button.config_location = screen_config

                buttons.append(time_button)

                try:
                    next_row = coord[button_count + 1][0]
                    next_col = coord[button_count + 1][2]
                    start_row, start_col = 1, 1
                    end_row, end_col = start_row, start_col
                                        # Example usage
                    coord1 = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    coord2 = (int(next_row), int(next_col))
                    
                    distance = int(cell_distance(coord1, coord2, set_cols) -1)
                    for i in range(abs(int(((coord2[0] - coord1[0]) * set_cols) + (coord2[1] - coord1[1]) + 1))):
                        place_holder = Label(size_hint=(None, None))
                        buttons.append(place_holder)
                        place_holders.append(place_holder)
                    
                except:
                    coord = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    distance = int(cell_distance(coord, (1,1), set_cols))
                    for i in range(distance):
                        place_holder = Label(size_hint=(None, None))
                        buttons.append(place_holder)
                        place_holders.append(place_holder)
                        
            elif id_ == 'date':
                # create date button and add it to the list
                
                date_button = DateButton(text='Date', size_hint=(None, None), background_color = button_color)
                date_button.config_location = screen_config
                date_button.carousel = carousel
                buttons.append(date_button)

                try:
                    next_row = coord[button_count + 1][0]
                    next_col = coord[button_count + 1][2]
                    start_row, start_col = 1, 1
                    end_row, end_col = start_row, start_col
                    
       
            
                    # Example usage
                    coord1 = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    coord2 = (int(next_row), int(next_col))

                    for i in range(abs(int(((coord2[0] - coord1[0]) * set_cols) + (coord2[1] - coord1[1]) + 1))):
                        place_holder = Label(size_hint=(None, None))
                        buttons.append(place_holder)
                        place_holders.append(place_holder)
                        

                except:
                    coord = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    distance = int(cell_distance(coord, (1,1), set_cols))
                    for i in range(distance):
                        place_holder = Label(size_hint=(None, None))
                        place_holders.append(place_holder)
                        buttons.append(place_holder)
            else:
                # create regular button and add it to the list
                text = button_elem.find('text').text
                image_path = button_elem.find('image').text
                script_path = button_elem.find('script_path').text

                try:
                    app_name = button_elem.find('application_name').text
                except Exception as e:
                    print(e)
                    app_name = "App Name not Assigned"
                    
                    
                    
                button = DraggableButton(screen_manager = screen_manager, text=text, size_hint=(None, None))
                button.application_name = app_name    
                button.config_location = screen_config
                button.background_normal = image_path
                button.background_color= button_color
                button.carousel = carousel

                buttons.append(button)

                try:
                    next_row = coord[button_count + 1][0]
                    next_col = coord[button_count + 1][2]
                    start_row, start_col = 1, 1
                    end_row, end_col = start_row, start_col
                    
       
            
                    # Example usage
                    coord1 = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    coord2 = (int(next_row), int(next_col))
                    
                    distance = int(cell_distance(coord1, coord2, set_cols) -1)
                    for i in range(abs(int(((coord2[0] - coord1[0]) * set_cols) + (coord2[1] - coord1[1]) + 1))):
                        place_holder = Label(size_hint=(None, None))
                        place_holders.append(place_holder)
                        buttons.append(place_holder)
                except:
                                    # Example usage
                    coord1 = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    coord2 = (int(next_row), int(next_col))
                    coord = (int(button_elem.find('row').text), int(button_elem.find('col').text))
                    distance = int(cell_distance(coord, (1,1), set_cols))
                    for i in range(distance):
                        place_holder = Label(size_hint=(None, None))
                        place_holders.append(place_holder)
                        buttons.append(place_holder)

                
            button_count += 1
            print(button_count)

        # add the buttons to the layout in reverse order
        for button in reversed(buttons):
            if 'PlaceHolder' in button.text:
                layout.add_widget(button)
            else:
                layout.add_widget(button)


        # schedule the initial positioning of the buttons
        self.set_initial_button_positions(layout)

        # draw initial grid lines
        self.draw_grid_lines(layout)
    
        return layout
    
    
    def spring_board_carousel(self, screen_manager):
        carousel = Carousel(direction='right')
        
        directory = '/opt/dash_os/button_layouts'
        extension = '.xml'
        
        # Get a list of all files in the directory
        files = os.listdir(directory)
        
        # Filter files with the specified extension
        xml_files = [file for file in files if file.endswith(extension)]
        
        count = 0
        # Loop through the XML files
        for xml_file in reversed(xml_files):
            count += 1
            xml_file_layout = self.snap_screen_container( directory + "/" + xml_file, screen_manager, carousel)
            carousel.add_widget(xml_file_layout)
        return carousel
    
    

    def build(self):
         # Create a ScreenManager
        screen_manager = ScreenManager()
        
        
        # Create a screen and add the layout to it
        Home_Screen = Screen(name='Home Screen')
        homescreen = self.spring_board_carousel(screen_manager)
        Home_Screen.add_widget(homescreen)

        # Add the screen to the screen manager
        screen_manager.add_widget(Home_Screen)
        
        
        second_screen = SecondScreen(name='Second Screen')
        screen_manager.add_widget(second_screen)
        
        
        # Pass the ScreenManager instance to the function to load screen.
        execute_functions_from_file("/opt/dash_os/screen_assets.py", screen_manager)
                
        # Create the navigation layout
        navigation_layout = NavigationLayout(homescreen, screen_manager, [Home_Screen, second_screen])
        
        outer_root_layout = FloatLayout()

        #Create a layout to hold both the main screen and the navigation layout
        root_layout = GridLayout(cols=1)
        background_image.allow_stretch = True
        background_image.size_hint = (1,1)  # Cover the entire layout
        background_image.pos_hint = {'x': 0, 'y': 0}  # Position at the bottom-left corner
        outer_root_layout.add_widget(background_image)
        root_layout.add_widget(top_bar_layout( pos_hint = {'x': 0, 'y': .95}))
        root_layout.add_widget(screen_manager)
        root_layout.add_widget(navigation_layout)
        
        outer_root_layout.add_widget(root_layout)
        
    

        return outer_root_layout
    
    
if __name__ == '__main__':

    MyApp().run()