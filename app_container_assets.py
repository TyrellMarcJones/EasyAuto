from kivy.uix.button import Button
from datetime import datetime, date
from kivy.utils import rgba
import xml.etree.ElementTree as ET
from functions import get_config_value, update_config_value, remove_button_by_text
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
import alsaaudio
from kivy.graphics import Color, Rectangle
from kivy.uix.carousel import Carousel
from kivy.core.window import Window

print(get_config_value('Appearance', 'grid_cols'))
set_cols = int(get_config_value('Appearance', 'grid_cols'))
set_rows = int(get_config_value('Appearance', 'grid_rows'))
config_location = '/opt/dash_os/button_layouts/buttons.xml'

button_width = 100
button_height = 100



def sort_buttons_by_rank(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    errorFlag = 0

    # Define a function to calculate the ranking system
    def calculate_rank(row, col):
        return row * 100 + col

    # Calculate the rankings for all buttons
    #Storage Array
    occupiedSpaces = []
    
    buttons = root.findall('button')
    for button in buttons:
        row = int(button.find('row').text)
        col = int(button.find('col').text)
        rank = calculate_rank(row, col)
        button.set('rank', str(rank))
        if ((row,col) not in occupiedSpaces):
            print("Already added")
            try:
                # Sort the buttons based on their rankings
                buttons.sort(key=lambda x: int(x.get('rank')))

                # Rewrite the XML file with the sorted buttons
                tree.write(filename)
            except Exception as e:
                print(e)
        else:
            errorFlag = 1

        occupiedSpaces.append((row,col))

    
    return errorFlag


class DraggableButton(Button):
    ...
    
class DateButton(DraggableButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = date.today().strftime('%d\n%B')
        self.font_size ='20sp'
        self.halign = 'center'
        self.valign = 'middle'
        self.color = [1, 1, 1, 1]
        self.markup = True
        self.is_dragging = False
        self.config_location = ""
        self.application_name = ""
        self.script_path = ""
        self.id = 'date'
        self.carousel = ""

    def update_date(self):
        self.text = datetime.date.today().strftime('%Y-%m-%d')
        
    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        self.update_date()
        print(self.application_name)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.border = [4, 4, 4, 4]
            print(self.config_location)
            print(self.application_name)
            print(self.script_path)

            return True

    def on_touch_move(self, touch):
        if self.is_dragging:
            self.pos = touch.pos

            # Get the window width
            window_width = Window.width

            # Calculate the threshold value (3% of the window width)
            threshold = 0.98
            print(self.pos[0]/int(window_width))

            # Check if the button is within the threshold of the right side
            if self.pos[0]/int(window_width) > threshold:
                percentage = (self.right - window_width + threshold) / threshold * 100
                print("Window Width: ", window_width, "pos: " , self.pos[0])
                print(self.carousel)
                self.carousel.load_next()


                

    def on_touch_up(self, touch):
        if self.is_dragging:
            self.is_dragging = False
            self.border = [0, 0, 0, 0]
            print(str("Before Droooop: ") + str(self.pos))
            # Get the window width
            window_width = Window.width


        
                
            print(self.pos[0])
            # calculate the row and column of the grid location
            if (self.pos[0] > window_width):
                x = self.pos[0] - window_width
                y = self.pos[1]

            else:
                x, y = self.pos
                
            grid_size = self.parent.size[0] / set_cols, self.parent.size[1] / set_rows
            col = int(x // grid_size[0])
            row = int(y // grid_size[1])

            # clamp the row and column values to the valid range
            col = max(min(col, set_cols-1), 0)
            row = max(min(row, set_rows-1), 0)

            # update the button's row and column values
            self.row = (set_rows - row)
            self.col = col + 1
            
                
            if (self.pos[0] > window_width): 
                # place the button in the center of the nearest valid grid location
                self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2 ,
                            row * grid_size[1] + grid_size[1]/2 - self.height/2)
                self.carousel.current_slide.add_widget(DateButton(text="Button", pos= self.pos))
            else:
                # place the button in the center of the nearest valid grid location
                self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2 ,
                            row * grid_size[1] + grid_size[1]/2 - self.height/2)
            
            print(self.pos[0])
            print(self.pos[1])

            # update the file with the locations of all the buttons and their order
            tree = ET.parse(self.config_location)
            root = tree.getroot()

            # find the existing element for this button
            button_elem = root.find(f"button[id='{self.id}']")
            if button_elem is not None:
                # remove the existing element
                root.remove(button_elem)

            # create a new element with the updated information
            button_elem = ET.Element('button')
            ET.SubElement(button_elem, 'image').text = self.background_normal
            ET.SubElement(button_elem, 'row').text = str(self.row)
            ET.SubElement(button_elem, 'col').text = str(self.col)
            ET.SubElement(button_elem, 'id').text = str(self.id)
            ET.SubElement(button_elem, 'application_name').text = str(self.application_name)
            ET.SubElement(button_elem, 'script_path').text = str(self.script_path)
            print(ET.SubElement(button_elem, 'script_path').text)
            root.append(button_elem)

            # write the updated XML to the file
            tree.write(self.config_location)

            # update the pos_hint property with the new position
            self.pos_hint = {'x': self.pos[0] / self.parent.width, 'y': self.pos[1] / self.parent.height}

            # apply padding to the button
            self.padding = [25, 25]

            # Parse the XML file
            tree = ET.parse(self.config_location)
            root = tree.getroot()

            # Create a list of buttons sorted by row and column
            buttons = sorted(root.findall('button'), key=lambda b: (int(b.find('row').text), int(b.find('col').text)))
            
            # Remove existing buttons from the root element
            for button in root.findall('button'):
                root.remove(button)
            
            # Add the sorted buttons back to the root element in order
            for button in buttons:
                root.append(button)
            
            # Write the sorted XML to a file
            tree.write(self.config_location, encoding='utf-8')
            
            # Example usage of the function
            sort_buttons_by_rank(self.config_location)


class TimeButton(DraggableButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = datetime.now().strftime('%H:%M')
        self.is_time_button = True
        self.is_dragging = False
        self.id = 'time'
        self.config_location = ""
        self.application_name = ""


        Clock.schedule_interval(self.update_time, 1)
    
    def update_time(self, dt):
        self.text = datetime.now().strftime('%H:%M')
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.border = [4, 4, 4, 4]
            return True

    def on_touch_move(self, touch):
        if self.is_dragging:
            self.pos = touch.pos

    def on_touch_up(self, touch):
        if self.is_dragging:
            self.is_dragging = False
            self.border = [0, 0, 0, 0]
            # calculate the row and column of the grid location
            x, y = self.pos
            grid_size = self.parent.size[0] / set_cols, self.parent.size[1] / set_rows
            col = int(x // grid_size[0])
            row = int(y // grid_size[1])

            # clamp the row and column values to the valid range
            col = max(min(col, set_cols-1), 0)
            row = max(min(row, set_rows-1), 0)

            # update the button's row and column values
            self.row = (set_rows - row)
            self.col = col + 1

            # place the button in the center of the nearest valid grid location
            self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2,
                        row * grid_size[1] + grid_size[1]/2 - self.height/2)

            # update the file with the locations of all the buttons and their order
            tree = ET.parse(self.config_location)
            root = tree.getroot()

            # find the existing element for this button
            button_elem = root.find(f"button[id='{self.id}']")
            if button_elem is not None:
                # remove the existing element
                root.remove(button_elem)

            # create a new element with the updated information
            button_elem = ET.Element('button')
            ET.SubElement(button_elem, 'image').text = self.background_normal
            ET.SubElement(button_elem, 'script').text = ''
            ET.SubElement(button_elem, 'row').text = str(self.row)
            ET.SubElement(button_elem, 'col').text = str(self.col)
            ET.SubElement(button_elem, 'id').text = 'time'
            ET.SubElement(button_elem, 'application_name').text = str(self.application_name)

            root.append(button_elem)

            # write the updated XML to the file
            tree.write(self.config_location)

            # update the pos_hint property with the new position
            self.pos_hint = {'x': self.pos[0] / self.parent.width, 'y': self.pos[1] / self.parent.height}

            # apply padding to the button
            self.padding = [25, 25]

            # Parse the XML file
            tree = ET.parse(self.config_location)
            root = tree.getroot()

            # Create a list of buttons sorted by row and column
            buttons = sorted(root.findall('button'), key=lambda b: (int(b.find('row').text), int(b.find('col').text)))
            
            # Remove existing buttons from the root element
            for button in root.findall('button'):
                root.remove(button)
            
            # Add the sorted buttons back to the root element in order
            for button in buttons:
                root.append(button)
            
            # Write the sorted XML to a file
            tree.write(self.config_location, encoding='utf-8')
            sort_buttons_by_rank(self.config_location)



class DraggableButton(DraggableButton):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.screens = []
        self.is_dragging = False
        self.row = None
        self.col = None
        self.pos_hint = {'x': 0, 'y': 0}
        self.config_location = ""
        self.application_name = ""
        self.script_path = ''
        self.initial_pos = ""
        self.carousel = ""
        self.active_screen = ""
                #Get current screen

    def update_button_width(self):
        grid_size = self.parent.size[0] / set_cols, self.parent.size[1] / set_rows
        cell_size = min(grid_size[0], grid_size[1])
        self.width = cell_size 
        self.height = cell_size 
        print("Updating")

        # adjust the button's position based on its new size
        col = int(self.pos[0] // grid_size[0])
        row = int(self.pos[1] // grid_size[1])
        self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2,
                    row * grid_size[1] + grid_size[1]/2 - self.height/2)


    def on_release(self):
        # Call the on_drag_release method of the app
        App.get_running_app().on_drag_release(self)
        
    def on_touch_down(self, touch):
        self.initial_index = self.carousel.index
        print("Index Before Move")
        print(self.carousel.index)
        print(" ----- ")

        self.initial_pos = touch.pos
        if self.collide_point(*touch.pos):
            print(self.application_name)
            print(self.script_path)

            self.is_dragging = True
            try:
                self.screen_manager.current = self.application_name
            except Exception as e:
                print(e)
                
            self.border = [4, 4, 4, 4]
            return True

    def on_touch_move(self, touch):
        if self.is_dragging:
            # move the button with the touch
            self.pos = touch.pos
            print(self.pos)


            # Get the window width
            window_width = Window.width

            # Calculate the threshold value (3% of the window width)
            threshold = 0.95
            min_threshold = 0.05

            print(self.pos[0]/int(window_width))

            # Check if the button is within the threshold of the right side
            if self.pos[0]/int(window_width) > threshold:
                percentage = (self.right - window_width + threshold) / threshold * 100
                print("Window Width: ", window_width, "pos: " , self.pos[0])
                print(self.carousel)
                self.carousel.load_next()
                self.active_screen = self.carousel.index
                print(self.active_screen)
            elif self.pos[0]/int(window_width) < min_threshold:
                percentage = (self.right - window_width + threshold) / threshold * 100
                print("Window Width: ", window_width, "pos: " , self.pos[0])
                print(self.carousel)
                self.carousel.load_previous()
                self.active_screen = self.carousel.index
                print(self.active_screen)



    def on_touch_up(self, touch):
        print("Inital Location")
        print(self.initial_pos)
        print("Button Released")

        if self.is_dragging:
            self.is_dragging = False
            #self.border = [0, 0, 0, 0]
            #print(self.background_normal)
            # calculate the row and column of the grid location            
            window_width = Window.width
            #print(self.pos[0])
            # calculate the row and column of the grid location
            if (self.pos[0] > window_width):
                #print("Button In New Window")
                x = self.pos[0] - window_width
                y = self.pos[1]
            else:
                x, y = self.pos
                
                
            grid_size = self.parent.size[0] / set_cols, self.parent.size[1] / set_rows
            col = int(x // grid_size[0])
            row = int(y // grid_size[1])
            # clamp the row and column values to the valid range
            col = max(min(col, set_cols-1), 0)
            row = max(min(row, set_rows-1), 0)

            # update the button's row and column values
            self.row = (set_rows - row)
            self.col = col + 1
            
            print("new row: " + str(self.row))
            print("new Col: " + str(self.col))

            try:
                print(self.carousel.children[self.initial_index])
            except Exception as e:
                print(e)
                
            if (self.pos[0] < 0):
                
                self.pos[0] = self.pos[0] + Window.width
                print(self.pos)
                # place the button in the center of the nearest valid grid location
                self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2 ,
                            row * grid_size[1] + grid_size[1]/2 - self.height/2)
                
                print(self.pos)
                new_button = DraggableButton(background_normal = self.background_normal, text=self.text, pos= self.pos, screen_manager = self.screen_manager)
                new_button.config_location = self.config_location
                print(self.config_location)
                
                self.carousel.current_slide.add_widget(new_button)
                parent_widget = self.parent
                parent_widget.remove_widget(self)
                    # Specify the XML file and the text to match
                xml_file_path = self.config_location
                text_to_remove = self.text
                
                # Remove the button and rewrite the XML file
                remove_button_by_text(xml_file_path, text_to_remove)
                
            if (self.pos[0] > window_width): 
                # place the button in the center of the nearest valid grid location
                self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2 ,
                            row * grid_size[1] + grid_size[1]/2 - self.height/2)
    
                new_button = DraggableButton(background_normal = self.background_normal, text=self.text, pos= self.pos, screen_manager = self.screen_manager)
                new_button.config_location = self.config_location
                
                self.carousel.current_slide.add_widget(new_button)
                parent_widget = self.parent
                parent_widget.remove_widget(self)
                    # Specify the XML file and the text to match
                xml_file_path = self.config_location
                text_to_remove = self.text
                
                # Remove the button and rewrite the XML file
                remove_button_by_text(xml_file_path, text_to_remove)
                print(self.carousel.index)
                
                
            else:
                # place the button in the center of the nearest valid grid location
                self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2 ,
                            row * grid_size[1] + grid_size[1]/2 - self.height/2)
            

            # update the file with the locations of all the buttons and their order
            button_layout_array = self.config_location.split("/")[:-1]

            try:
                button_layout_array.append("buttons" + str(self.carousel.index) + ".xml")
                config_location = ""
                for path in button_layout_array:
                    if path != "":
                        config_location += ("/" + path )
                self.config_location = config_location
                new_button.config_location = config_location
            except Exception as e:
                print(e)
                
            try:
                tree = ET.parse(self.config_location)
                root = tree.getroot()

            except Exception as e:
                print("Error")
                print(e)
            
        

            # find the existing element for this button
            try:
                button_elem = root.find(f"button[text='{self.text}']")
                root.remove(button_elem)

            except Exception as e:
                print(e)
            

            # create a new element with the updated information
            button_elem = ET.Element('button')
            ET.SubElement(button_elem, 'text').text = self.text
            ET.SubElement(button_elem, 'image').text = self.background_normal
            ET.SubElement(button_elem, 'script').text = ''
            ET.SubElement(button_elem, 'row').text = str(self.row)
            ET.SubElement(button_elem, 'col').text = str(self.col)
            ET.SubElement(button_elem, 'application_name').text = str(self.application_name)
            ET.SubElement(button_elem, 'script_path').text = str(self.script_path)
            print(str(self.script_path))
            
            
            root.append(button_elem)

            # write the updated XML to the file
            tree.write(self.config_location)

            # update the pos_hint property with the new position
            try:
                self.pos_hint = {'x': self.pos[0] / self.parent.width, 'y': self.pos[1] / self.parent.height}
            except:
                pass
            # apply padding to the button
            self.padding = [25, 25]
            
            # Parse the XML file
            tree = ET.parse(self.config_location)
            root = tree.getroot()
            
            # Create a list of buttons sorted by row and column
            buttons = sorted(root.findall('button'), key=lambda b: (int(b.find('row').text), int(b.find('col').text)))
            
            # Remove existing buttons from the root element
            for button in root.findall('button'):
                root.remove(button)
            
            # Add the sorted buttons back to the root element in order
            for button in buttons:
                root.append(button)
            
            # Write the sorted XML to a file
            tree.write(self.config_location , encoding='utf-8')
            if sort_buttons_by_rank(self.config_location) == 0:
                print("Success")
            else:
                print("Error Duplicate")
                
                self.pos = self.initial_pos
                
                col = int(self.pos[0] // grid_size[0])
                row = int(self.pos[1] // grid_size[1])
        
                               # place the button in the center of the nearest valid grid location
                self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2 ,
                            row * grid_size[1] + grid_size[1]/2 - self.height/2)
                
            
            
    #not being used?
    def update_position(self):
        # update the button's row and column values when it is moved programmatically
        grid_size = self.parent.size[0] / set_cols, self.parent.size[1] / set_rows
        col = int(self.pos[0] // grid_size[0])
        row = int(self.pos[1] // grid_size[1])
    
        # clamp the row and column values to the valid range
        col = max(min(col, 3), 0)
        row = max(min(row, 2), 0)
    
        self.row = 3 - row
        self.col = col + 1
    
        # set the button's size based on the minimum of the grid cell width and height
        cell_size = min(grid_size[0], grid_size[1])
        self.width = cell_size - 50
        self.height = cell_size - 50
    
        # adjust the button's position based on its new size and grid cell
        self.pos = (col * grid_size[0] + grid_size[0]/2 - self.width/2,
                    row * grid_size[1] + grid_size[1]/2 - self.height/2)
    
        # adjust the button's position based on its new size and grid cell
        self.pos = (self.pos[0] + (grid_size[0] - self.width) / 2,
                    self.pos[1] + (grid_size[1] - self.height) / 2)
    
        # update the pos_hint property with the new position
        self.pos_hint = {'x': self.pos[0] / self.parent.width, 'y': self.pos[1] / self.parent.height}
    
        # adjust the button's padding and border to fit within its grid cell
        self.padding = [25, 25]
        self.border = [0, 0, 0, 0]
        if self.parent.size[0] / self.parent.size[1] < set_cols / set_rows:
            self.padding[0] = (self.parent.width / set_cols - self.width) / 2
        else:
            self.padding[1] = (self.parent.height / set_rows - self.height) / 2
        sort_buttons_by_rank(self.config_location)
        print("Sorted Sucka")



class NavigationLayout(GridLayout):
    def __init__(self,carousal, screen_manager, screens, **kwargs):
        super(NavigationLayout, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.carousal = carousal
        self.screens = screens
        self.cols = 4
        self.rows = 1
        self.size_hint_y = .1
        with self.canvas.before:
            Color(0, 0, 0, .8)  # White color
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
        
        
        #Get current screen
        self.current_screen =  ""
        
    

        # Create the slider
        self.slider = Slider(min=0, max=100, value=10,size_hint_y = 0.4)
        self.slider.bind(value=self.print_slider_value)
        self.add_widget(self.slider)
        

        # Create the toggle button 1
        self.button1 = Button(background_normal = '/opt/dash_os/app_icons/Back.png',text="",size_hint_x = 0.2, on_press=self.toggle_content1)
        self.add_widget(self.button1)

        # Create the toggle button 2
        self.button2 = Button(background_normal = '/opt/dash_os/app_icons/Home.png', text="",size_hint_x = 0.2, on_press=self.toggle_content2)
        self.add_widget(self.button2)

        # Create the toggle button 3
        self.button3 = Button(background_normal = '/opt/dash_os/app_icons/Menu.png', text="",size_hint_x = 0.2, on_press=self.toggle_content3)
        self.add_widget(self.button3)

        # Create the content layout
        self.content_layout = GridLayout(cols=1)

        # Create the toggle grid layout
        self.toggle_layout = GridLayout(cols=1)

        # Add the toggle button and content layout to the toggle layout
        self.toggle_layout.add_widget(self.content_layout)
        


    def toggle_content1(self, instance):
        #If the current screeen isnt the settings screen. Capture the screen and open the sttings
        if self.screen_manager.current != 'Simple Screen':
            self.current_screen =  self.screen_manager.current
            self.screen_manager.current = 'Simple Screen'
            print(f"{self.current_screen} Closed")
            print("Simple Open")
 
    def toggle_content2(self, instance):
                
        #If the current screeen isnt the settings screen. Capture the screen and open the sttings
        if (self.screen_manager.current != 'Home Screen') or self.carousal.current_slide != self.carousal.slides[0]:
                 # Print the widgets in the carousel

            self.current_screen =  self.screen_manager.current
            self.carousal.load_slide(self.carousal.slides[0])
            self.screen_manager.current = 'Home Screen'
            print(f"{self.current_screen} Closed")
            print("Settings Open")
 

    def toggle_content3(self, instance):
    

        
        #If the current screeen isnt the settings screen. Capture the screen and open the sttings
        if self.screen_manager.current != 'Second Screen':
            self.current_screen =  self.screen_manager.current
            self.screen_manager.current = 'Second Screen'
            print(f"{self.current_screen} Closed")
            print("Settings Open")
        #If the current screen is the settings screen, get the current screen that was open and set it back. 
        elif self.screen_manager.current == 'Second Screen':
            print("Settings Closing opening")
            print(f"{self.current_screen} Closed")
            self.screen_manager.current = self.current_screen
            current_screen = ''
        
        
    def print_slider_value(self, instance, value):
        print("Volume Change:", value)
        m = alsaaudio.Mixer()
        current_volume = m.getvolume() # Get the current Volume
        m.setvolume(int(value)) # Set the volume to 70%.


        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class top_bar_layout(GridLayout):
    
    def update_time_date(self, *args):
        now = datetime.now()
        self.time_date_label.text = now.strftime("%I:%M %p")



    def __init__(self, **kwargs):
        super(top_bar_layout, self).__init__(**kwargs)
        self.cols = 3
        self.rows = 1
        self.size_hint_y = .05
        with self.canvas.before:
            Color(0, 0, 0, .8)  # White color
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
        

        # Add time and date above the car photo
        self.time_date_label = Label(
            text="", font_size=24, size_hint=(1, 0.05)) #font_name="DS-Digital.ttf"
        
        
        self.update_time_date()
        Clock.schedule_interval(self.update_time_date, 1)
        self.add_widget(self.time_date_label)



        # Create the toggle button 2
        self.button2 = Image(source="/opt/dash_os/bt_s_icon.png")
        self.add_widget(self.button2)

        # Create the toggle button 3
        self.button3 = Label(text="Connection")
        self.add_widget(self.button3)

        # Create the content layout
        self.content_layout = GridLayout(cols=1)

        # Create the toggle grid layout
        self.toggle_layout = GridLayout(cols=1)

        # Add the toggle button and content layout to the toggle layout
        self.toggle_layout.add_widget(self.content_layout)


    def toggle_content2(self, instance):
        self.toggle_content(self.button2)

    def toggle_content3(self, instance):
        self.toggle_content(self.button3)

    def toggle_content(self, button):
        # Calculate the target x position for the content layout
        target_x = 0 if self.content_layout.x > 0 else self.width

        # Animate the content layout's position
        anim = Animation(x=target_x, duration=0.3)
        anim.start(self.content_layout)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size