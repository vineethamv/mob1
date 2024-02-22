from kivy.graphics import Rectangle, Color
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import webbrowser
import pandas as pd
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload
from kivy.core.text import Label as CoreLabel
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineAvatarListItem, ImageLeftWidget
from kivy.uix.label import Label

# Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'electrocare-414304-048244022b46.json'  # Update with your service account file

homescreen_helper = """
ScreenManager:
    HomeScreen:       
    SearchScreen:
    DetailScreen:

<HomeScreen>:
    name:'home'
    BoxLayout:
        orientation: 'horizontal'         
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1  # White background color
            Rectangle:
                pos: self.pos
                size: self.size

        MDBottomNavigation:
            panel_color: 0.90,0.93,1, 1
            text_color_active: [0, 0, 1, 1] 
            text_color_normal: [0, 0, 0, 1]
            #size_hint_y: None  # Set the height to a fixed value
            #height: 100

            MDBottomNavigationItem:
                name: 'screen 1'
                text: 'Home'
                icon: 'home'  
                on_tab_press: root.go_to_home()
                ripple_behavior:True
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1  # White background color
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    AsyncImage:
                        source: 'assets/favicon1.jpg'
                        size_hint: (None, 1.2)
                        pos_hint: {'center_x': 0.5,'center_y': 0.2}

                    Label:
                        text: 'Welcome To Electro Care App'
                        color: 1, 0, 0, 1  # Text color (Red)
                        font_size: '40sp'
                        pos_hint: {'center_x': 0.5,'center_y': 1}
                        halign:'center'
                        size_hint_y: 1   # Allow vertical resizing
                        height: self.texture_size[1]  # Set the height to fit the content
                        text_size: self.width, None


            MDBottomNavigationItem:
                name: 'screen 2'
                text: 'Register'
                icon: 'account-plus'
                on_tab_press: root.open_registration_link()
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1  # White background color
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    AsyncImage:
                        source: 'assets/favicon1.jpg'
                        size_hint: (None, 1.2)
                        pos_hint: {'center_x': 0.5,'center_y': 0.2}

                    Label:
                        text: 'Your Application will be reviewed and add to Elecro Care app soon!'
                        color: 1, 0, 0, 1  # Text color (Red)
                        font_size: '40sp'
                        pos_hint: {'center_x': 0.5,'center_y': 1}
                        halign:'center'
                        size_hint_y: 1   # Allow vertical resizing
                        height: self.texture_size[1]  # Set the height to fit the content
                        text_size: self.width, None


            MDBottomNavigationItem:
                name: 'screen 3'
                text: 'Search'
                icon: 'magnify'
                on_tab_press:root.retrieve_data()
                BoxLayout:
                    orientation: 'vertical'
                    padding: (0,0,0,20)
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1  # White background color
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    ScrollView:
                        MDList:
                            id: data_layout
                            pos_hint: {'top': 1}


            MDBottomNavigationItem:
                name: 'screen 4'
                text: 'Close'
                icon: 'exit-to-app' 
                on_tab_press: root.close_app()
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1  # White background color
                        Rectangle:
                            pos: self.pos
                            size: self.size



<SearchScreen>:
    name:'search'

<DetailScreen>:
    name:'detail' 
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1  # White background color
            Rectangle:
                pos: self.pos
                size: self.size
        
        ScrollView:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1  # White background color
                Rectangle:
                    pos: self.pos
                    size: self.size
            MDList:
                id: detail_layout
                #pos_hint: {'top': 1} 
                size_hint_y: None  # Ensure that MDList doesn't expand vertically
                height: self.minimum_height  # Allow MDList to expand vertically as needed
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                
        MDBottomNavigation:
            panel_color: 0.90,0.93,1, 1
            text_color_active: [0, 0, 1, 1] 
            text_color_normal: [0, 0, 0, 1]          

            MDBottomNavigationItem:
                name: 'screen 3'
                text: 'Search'
                icon: 'magnify'
                on_tab_press:root.go_to_home_screen()
                

            MDBottomNavigationItem:
                name: 'screen 4'
                text: 'Close'
                icon: 'exit-to-app' 
                on_tab_press: root.close_app1()
"""


class WrappedLabel(Label):
    def __init__(self, **kwargs):
        self.bind(
            width=lambda instance, value: self.setter('text_size')(self, (value, None))
        )
        self.bind(texture_size=self.setter('size'))
        super(WrappedLabel, self).__init__(**kwargs)

    def texture_update(self):
        if self._label is None:
            self._label = CoreLabel()
            self._label.refresh()
        self._label.text = self.text
        self._label.refresh()
        self.texture = self._label.texture

class SearchScreen(Screen):
    pass


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.rect = None
        self.md_bg_color = [1, 1, 1, 1]  # White background color

    @staticmethod
    def close_app():
        MDApp.get_running_app().stop()

    def go_to_home(self):
        self.manager.current = 'home'

    def go_to_search(self):
        self.manager.current = 'search'

    def open_registration_link(self):
        url = "https://forms.gle/iTfEYy8Na2giQwFd6"  # Replace this URL with your registration link
        webbrowser.open(url)

    def retrieve_data(self):
        self.ids.data_layout.clear_widgets()

        # Authenticate with Google Drive API using service account credentials
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        # ID of the Excel file in Google Drive
        file_id = '1SM0T9tlLnRLEJAWIFfatChLumh5X1fY73qu2B97VJz4'

        # Download the Excel file
        request = service.files().export_media(fileId=file_id,
                                               mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")

        # Read the downloaded Excel file using pandas
        fh.seek(0)  # Move to the beginning of the file
        try:
            data = pd.read_excel(fh, engine="openpyxl",
                                 sheet_name="KSESTA Registered Members")  # Change "Sheet1" to your desired sheet name
        except Exception as e:
            print("Error reading Excel file:", e)
            data = pd.DataFrame()

        if data.empty:
            # Handle the case where the data is empty
            self.ids.data_layout.add_widget(
                MDLabel(
                    text="No data available",
                    halign="center",
                    valign="middle",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),  # White text color
                )
            )
            self.ids.data_layout.canvas.before.clear()  # Clear any previous background
            with self.ids.data_layout.canvas.before:
                Color(0, 0, 0, 1)  # Black background color
                self.rect = Rectangle(size=self.ids.data_layout.size, pos=self.ids.data_layout.pos)
        else:
            # Display data in the summary list
            for _, row in data.iterrows():
                primary_text = str(row.iloc[1]) if len(row) > 0 else ""
                secondary_text = str(row.iloc[2]) if len(row) > 1 else ""

                item = ThreeLineAvatarListItem(text=primary_text, secondary_text=secondary_text)

                # Change font style and theme text color
                item.theme_text_color = "Error"
                item.primary_font_style = "Caption"

                icon = ImageLeftWidget(source="assets/favicon2.jpg", pos_hint={'center_x': 0, 'center_y': 0.2},
                                       size_hint=(None, None), size=(dp(36), dp(36)))

                # Add the icon to the left of the item
                item.add_widget(icon)

                # Bind the on_release event
                item.bind(on_release=lambda x, service=dict(row): self.on_item_press(service))
                self.ids.data_layout.add_widget(item)

    def on_item_press(self, data):
        # Navigate to the DetailScreen and pass the data
        self.manager.get_screen('detail').set_data(data)
        self.manager.current = 'detail'


class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super(DetailScreen, self).__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]  # White background color

    def go_to_home_screen(self):
        home_screen = self.manager.get_screen('home')
        self.manager.current = 'home'

    @staticmethod
    def close_app1():
        MDApp.get_running_app().stop()

    def open_registration_link1(self):
        url = "https://forms.gle/iTfEYy8Na2giQwFd6"  # Replace this URL with your registration link
        webbrowser.open(url)

    def set_data(self, data):
        # Clear existing widgets
        self.ids.detail_layout.clear_widgets()

        # Define titles for each field
        titles = {
            'Office Address': '',
            'Service Items': '',
            'Service Areas': ' Service Areas ',
            'Name': '  Contact ',
            'Contact Number': '  Phone ',
            'WhatsApp Number': '  WhatsApp ',
            'Email Address': '  Email '
        }
        y_position = 1
        # Create labels for each field title
        for key, title in titles.items():
            # Skip displaying the ID field
            if key.lower() == 'id':
                continue

            # Get the value for the current field
            value = data.get(key, '')

            # Format the label text
            if key == 'Office Address':
                label_text = f"\n\n{title} {value}\n" if value else ""
            elif key == 'Service Items':
                label_text = f"\n\n{title} {value}\n" if value else ""
            elif key == 'Service Areas':
                label_text = f"\n\n{title}: {value}\n" if value else ""
            else:
                label_text = f"\n\n\n{title}:: {value}\n" if value else ""

            # Create the label widget
            label = MDLabel(
                text=label_text,
                halign='left',
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(20),
                markup=True
            )

            if key == 'Office Address':
                label.font_style = 'H6'
                label.bold = True
                label.theme_text_color = 'Error'
            if key == 'Service Items':
                label.font_style = 'Caption'
                label.bold = False
                label.color = (0, 0, 0, 1)
            if key == 'Service Areas':
                label.font_style = 'Caption'
                label.bold = True
                label.color = (0, 0, 0, 1)

            if key == 'Email Address':
                # Bind the email address to the label
                label.email = value
                label.underline = False  # Add underline
                label.color = (0, 0, 1, 1)
                label.bind(on_touch_up=self.on_email_touch_up)
            elif key == 'Contact Number':
                # Bind the phone number to the label
                label.phone_number = value
                label.color = (0, 0, 1, 1)
                label.italic = True
                label.bind(on_touch_up=self.on_phone_number_press)
            elif key == 'WhatsApp Number':
                label.wno_number = value
                label.italic = True
                label.color = (0, 0, 1, 1)
                label.bind(on_touch_up=self.on_wno_number_press)

            self.ids.detail_layout.add_widget(label)

            # Add spacing between labels
            self.ids.detail_layout.add_widget(MDLabel(size_hint_y=None, height=dp(10)))

    def on_phone_number_press(self, instance, touch):
        # Ensure that the phone_number attribute exists in the label instance
        if instance.collide_point(*touch.pos):
            webbrowser.open(f'tel:{instance.phone_number}')

    def on_wno_number_press(self, instance, touch):
        # Ensure that the phone_number attribute exists in the label instance
        if instance.collide_point(*touch.pos):
            # Replace with the desired phone number
            whatsapp_link = f"https://wa.me/{instance.wno_number}"
            webbrowser.open(whatsapp_link)

    def on_email_touch_up(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Open default email application with the specified email address
            webbrowser.open(f'mailto:{instance.email}')


class ElectroCareApp(MDApp):
    def build(self):
        # Initialize the theme_cls and other configurations here
        # Window.size = (310, 500)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = 'Red'

        # Create and set up the widgets
        sm = ScreenManager()
        home_screen = HomeScreen(name='home')
        search_screen = SearchScreen(name='search')
        detail_screen = DetailScreen(name='detail')

        sm.add_widget(home_screen)
        sm.add_widget(search_screen)
        sm.add_widget(detail_screen)

        screen = Builder.load_string(homescreen_helper)
        return screen


ElectroCareApp().run()
