import os
import time
import threading

def getimg():
        os.system('sudo fswebcam -r 640*480 faceimage.jpg')
        time.sleep(1)
        getimg()
t1 = threading.Thread(target=getimg)
t1.start()