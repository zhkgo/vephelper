# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search every   where for classes, files, tool windows, actions, and settings.
import pygame, sys
import win32api
import win32con
import win32gui
import math
suf = None
class SSVEPControl:
    def __init__(self, screen,  basepos = (100,100), size = 4, num=(9,9), freq = 10 , fps=200):
        self.screen = screen
        self.sufs = []
        self.size = size
        self.basepos = basepos
        self.num = num
        self.cnt = 0
        self.freq = freq
        self.fps = fps
        color = (255, 255, 255)
        for i in range(num[0]):
            line = []
            for j in range(num[1]):
                line.append(pygame.Surface((size, size)))
                line[-1].fill(color)
            self.sufs.append(line)

    def draw(self,):
        alpha = max(math.sin(self.freq/self.fps*self .cnt*2*math.pi), 0)
        self.cnt += 1
        alpha = int(alpha*255)
        for i,line in enumerate(self.sufs):
            for j,suf in enumerate(line):
                suf.set_alpha(alpha)
                self.screen.blit(suf, (self.basepos[0] + (2 * i + 1) * self.size, self.basepos[1] + (2 * j + 1) * self.size))

def showWindow(bound=False,size=(900,900)):
    screen = None
    if bound:
        screen = pygame.display.set_mode(size)
    else:
        screen = pygame.display.set_mode(size, flags=pygame.NOFRAME)
    pygame.display.set_caption("pyg1ame游戏之旅")
    # Set window transparency color
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
    fuchsia = (255, 0, 128)  # Transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
    return screen
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    pygame.init()
    flag = True
    vinfo = pygame.display.Info()
    size = vinfo.current_w, vinfo.current_h
    size = 500, 300
    screen = showWindow(flag,size)
    fuchsia = (255, 0, 128)  # Transparency color
    fps = 120
    #12.2, 13, 13.8, 14.6
    # freqs = [[(100 , 0), 8], [(0,90), 10], [(100, 90),12], [(200, 90),14]]
    freqs = [[(150, 0), 15.1], [(0, 150), 15.2], [(150, 150), 15.3], [(300, 150), 15.4]]

    # freqs =  [[(100 , 0), 8.2], [(0,90), 8.4], [(100, 90),8.6], [(200, 90),8.8]]
    btns = [SSVEPControl(screen,basepos=pos,freq=freq,fps=fps,size=4.5 ) for pos,freq in freqs]
    fclock = pygame.time.Clock()
    # pygame.event.set_blocked([pygame.KEYUP,pygame.KEYDOWN,pygame.MOUSEMOTION])

    while True:
        # print("h0")
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(fuchsia)  # Transparent background
        for btn in btns:
            btn.draw()
        pygame.display.update()
        fclock.tick(fps)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
