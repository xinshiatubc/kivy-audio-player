from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse, Rectangle
from functools import partial
from threading import Thread
from kivy.uix.stencilview import StencilView
from kivy.uix.progressbar import ProgressBar

import librosa
import librosa.display
import logging
import os
import datetime
import math
import matplotlib


class LoadDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Dialog(FloatLayout):
    cancel = ObjectProperty(None)
    message = StringProperty(None)


class AudioPanel(BoxLayout):
    audio_file = ObjectProperty(None)


class Root(BoxLayout):

    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Window.bind(on_dropfile=self._on_file_drop)

    def _on_file_drop(self, window, file_path):
        dir_input = self.ids['dir_input']
        dir_input.text = file_path
        # clear old input
        audio_list = self.ids['audio_list']
        audio_list.clear_widgets()

        self.iterate_over_files(file_path.decode("utf-8"))

    def dismiss_popup(self):
        self._popup.dismiss()

    def show(self):
        content = LoadDialog(save=self.save, cancel=self.dismiss_popup)

        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename, is_search):
        dir_input = self.ids['dir_input']

        dir_input.text = filename
        self.iterate_over_files(str(filename))
        self.dismiss_popup()

    def showDialogBox(self):
        content = Dialog(cancel=self.dismiss_popup, message="Please drop in a folder.")
        self._popup = Popup(title="Please Double Check",
                            content=content,
                            size_hint=(0.5, 0.3))
        self._popup.open()

    def iterate_over_files(self, root_dir):
        logging.info("Iterating through " + root_dir)

        # first calculate number of files to process
        file_count = 0
        app = App.get_running_app()
        audio_list = self.ids['audio_list']
        audio_list.bind(minimum_height=audio_list.setter('height'))

        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                file_path = subdir + os.sep + file
                if is_audio_file(file):
                    file_count += 1
                    content = AudioPanel()
                    audio_list.add_widget(content)

        count_label = app.root.ids['file_count_label']
        count_label.text = str(file_count) + " audio files found"
        logging.info(str(file_count) + " audio files found")

        if file_count == 0 and os.path.isfile(root_dir):
            self.showDialogBox()


def is_audio_file(filename):
    if filename.endswith(".wav") or filename.endswith(".WAV"):
        return True
    else:
        return False


class AudioPlayer(App):
    pass


if __name__ == '__main__':
    AudioPlayer().run()
