import keyboard
from PIL import ImageGrab

def activateBot():

    while True:
        screen = ImageGrab.grab (bbox=(800, 299, 850, 309))
        grayScreen = screen.convert('L')
        pixels = grayScreen.load()

        for i in range(0, 50):
            for j in range (0, 10):
                if pixels [i, j] < 100:
                    keyboard.press('space')
                    break

if __name__ == "__main__":
    activateBot()