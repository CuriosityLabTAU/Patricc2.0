from pygame import mixer
import time
# Starting the mixer
mixer.init()

# Loading the song
#mixer.music.load("aussom.mp3")
mixer.music.load('/home/gorengordon/PycharmProjects/Patricc2.0/AuthoringTool/sounds/game_1/a avocado.mp3')
# Setting the volume
mixer.music.set_volume(0.7)

# Start playing the song
mixer.music.play()

# infinite loop
while True:

    time.sleep(2)
    mixer.music.play()