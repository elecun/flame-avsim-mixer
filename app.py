
from pygame import mixer
from dataclasses import dataclass
import time

@dataclass
class soundbase:
    sound:object = None
    filepath:str = None
    playing:bool = False

if __name__ =="__main__":
    mixer.init()
    
    #a = soundbase(sound = mixer.Sound("./sound/interior_ambience_10min.mp3"), filepath="./sound/interior_ambience_10min.mp3", playing=False)
    
    mixer.init()
    #a.sound.play()
    
    interior_sound = mixer.Sound("./sound/interior_ambience_10min.mp3")
    interior_sound.
    # tesla_error = mixer.Sound("./sound/tesla_error.mp3")
    # interior_sound.set_volume(0.7)
    # tesla_error.set_volume(0.3)
    # interior_sound.play()
    
    wait = 0
    while True:
        time.sleep(1)
        wait = wait +1
        