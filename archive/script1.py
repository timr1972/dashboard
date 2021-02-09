from guizero import App
import sys
import os

driver = 'directfb'
if not os.getenv('SDL_VIDEODRIVER'):
    os.putenv('SDL_VIDEODRIVER', driver)

app = App(title="Hello world")
app.display()

