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
    sound = ObjectProperty(None, allownone=True)
    duration = NumericProperty(0.0)
    volume = NumericProperty(1.0)
    play_button = ObjectProperty(None)
    progress_label = ObjectProperty(None)
    progress_box = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    slider = ObjectProperty(None)
    position = NumericProperty(0.0)
    stop_pressed = StringProperty(None)
    event_list = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stop_pressed = "false"
        for child in self.children:
            object_class = child.__class__.__name__
            if object_class == 'Slider':
                self.slider = child
            if object_class == 'BoxLayout':
                self.progress_box = child
                fl = child.children[0]
                for fl_child in fl.children:
                    if fl_child.children:
                        if fl_child.children[0].__class__.__name__ == 'ProgressBar':
                            self.progress_bar = fl_child.children[0]
            if object_class == 'Label':
                self.progress_label = child
            if object_class == 'Button':
                self.play_button = child

    def get_layout(self):
        for child in self.children:
            object_class = child.__class__.__name__
            logging.info(object_class)
            if object_class == 'Slider':
                self.slider = child
            if object_class == 'BoxLayout':
                self.progress_box = child
                fl = child.children[0]
                for fl_child in fl.children:
                    if fl_child.children:
                        if fl_child.children[0].__class__.__name__ == 'ProgressBar':
                            self.progress_bar = fl_child.children[0]
            if object_class == 'Label':
                self.progress_label = child
            if object_class == 'Button':
                self.play_button = child

    def get_duration(self):
        self.sound = SoundLoader.load(self.audio_file)
        self.sound.bind(on_stop=self.done)
        self.duration = self.sound.length
        return self.duration

    def reset_progress(self):
        if self.sound is None:
            duration = self.get_duration()
        else:
            duration = self.duration
        zeroPos = str(datetime.timedelta(seconds=0))
        endPos = str(datetime.timedelta(seconds=math.floor(duration)))
        return zeroPos + " / " + endPos

    def play_audio(self):
        if len(self.event_list) == 0:
            event = Clock.schedule_interval(partial(self.update_progress), 0.5)
            self.event_list.append(event)
            logging.info("clock created")

        if self.sound is None:
            self.sound = SoundLoader.load(self.audio_file)
            self.sound.bind(on_stop=self.done)

        if self.sound.status != 'stop':
            self.position = self.sound.get_pos()
            self.stop_pressed = "true"
            self.sound.stop()
            if self.play_button is None:
                self.get_layout()
            self.play_button.background_normal = "./img/play_inverse.png"

        else:
            self.sound.volume = self.volume
            self.sound.play()
            self.event_list[0]()
            self.sound.seek(self.position)

            if self.play_button is None:
                self.get_layout()
            self.play_button.background_normal = "./img/stop_inverse.png"

    def done(self, dt):
        self.event_list[0].cancel()
        self.play_button.background_normal = "./img/play_inverse.png"
        if self.stop_pressed == "true":
            self.stop_pressed = "false"
        else:
            self.position = 0.0
            self.progress_label.text = self.reset_progress()
            self.progress_bar.value = 0.0

    def adjust_volume(self, value):
        if self.sound:
            self.sound.volume = value
            self.volume = value

    def update_progress(self, value):
        if self.sound:
            pos = self.sound.get_pos()

            curPos = str(datetime.timedelta(seconds=round(pos)))
            endPos = str(datetime.timedelta(seconds=math.floor(self.sound.length)))
            self.progress_label.text = curPos + " / " + endPos

            self.progress_bar.value = math.ceil(pos)


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

        t = Thread(target=self.iterate_over_files, args=[file_path.decode("utf-8")])
        t.daemon = True
        t.start()
        # self.iterate_over_files(file_path.decode("utf-8"))

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
                    content = AudioPanel(audio_file=file_path)
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
