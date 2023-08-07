
from pygame import mixer
import time

if __name__ =="__main__":
    mixer.init()
    interior_sound = mixer.Sound("./sound/interior_ambience_10min.mp3")
    tesla_error = mixer.Sound("./sound/tesla_error.mp3")
    interior_sound.set_volume(0.7)
    tesla_error.set_volume(0.3)
    interior_sound.play()
    
    wait = 0
    while True:
        time.sleep(1)
        wait = wait +1
        
        if wait == 10:
            tesla_error.play()
        