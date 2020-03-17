# Kivy Audio Player

An audio player application written in Python and Kivy language.
 
## Kivy Installation on Windows

1. Ensure you have **Python 3.7** or previous version installed. Currently Kivy doesn't support Python 3.8.

2. Ensure you have the latest pip and wheel:

```
python -m pip install --upgrade pip wheel setuptools
```
3. Install the dependencies: 

```
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install kivy.deps.gstreamer
```
4. Install Kivy:

```
python -m pip install kivy
```

That’s it. You should now be able to import kivy in Python.

## Installing Other Dependencies

1. Install Librosa for waveform plotting:

```
pip install librosa
```

2. Install matplotlib custom widget. 
Make sure you have Kivy Garden installed: 

```
pip install kivy-garden
```
Install matplotlib garden package:
```
garden install matplotlib
```
3. Ensure you have matplotlib installed:
```
python -m pip install matplotlib
```
## Further Information
* [Kivy Installation Guide](https://kivy.org/doc/stable-1.10.1/installation/installation-windows.html#installation-windows)
* [Librosa Installation Guide](https://librosa.github.io/librosa/install.html)
