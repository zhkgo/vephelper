import pygame, sys
import win32api
import win32con
import win32gui
import math
import argparse
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
        self.rect = pygame.Rect(basepos[0], basepos[1], size * num[0] * 2, size * num[1] * 2) # 指定块的边界矩形

    def draw(self,):
        alpha = max(math.sin(self.freq/self.fps*self .cnt*2*math.pi), 0)
        self.cnt += 1
        alpha = int(alpha*255)
        for i,line in enumerate(self.sufs):
            for j,suf in enumerate(line):
                suf.set_alpha(alpha)
                self.screen.blit(suf, (self.basepos[0] + (2 * i + 1) * self.size, self.basepos[1] + (2 * j + 1) * self.size))
    def move(self, dx, dy):
        self.basepos = (self.basepos[0] + dx, self.basepos[1] + dy)
        self.rect.move_ip(dx, dy)

    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)
def showWindow(transparent=False,size=(900,900)):
    screen = None
    if not transparent:
        screen = pygame.display.set_mode(size, flags= pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode(size, flags=pygame.NOFRAME)
    pygame.display.set_caption("SSVEP")
    # Set window transparency color
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
    fuchsia = (255, 0, 128)  # Transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
    return screen  # 根据bound决定是否显示边框

class SSVEPApp:
    def __init__(self, freqs):
        pygame.init()
        self.screen_size = (500, 300)
        self.transparent = True
        self.screen = showWindow(self.transparent, self.screen_size)
        self.fuchsia = (255, 0, 128)
        self.fps = 120
        self.btns = [SSVEPControl(self.screen, basepos=pos, freq=freq, fps=self.fps, size=4.5) for pos, freq in freqs]
        self.transparency_button = pygame.Rect(10, 10, 100, 30)
        self.start_drag = False
        self.start_pos = (0, 0)
        self.dragging_block = None
        self.fclock = pygame.time.Clock()
        self.hwnd = pygame.display.get_wm_info()["window"]
        self.toggle_transparency(self.transparent)

    def toggle_transparency(self, transparent):
        x, y, width, height = win32gui.GetWindowRect(self.hwnd)
        self.screen = showWindow(transparent, (width - x, height - y))  # 根据透明状态设置边框和大小手柄
        # 恢复窗口位置和大小
        win32gui.SetWindowPos(self.hwnd, 0, x, y, width - x, height - y, 0)
        if transparent:
            win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(*self.fuchsia), 0, win32con.LWA_COLORKEY)
        else:
            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)
    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            background_color = self.fuchsia if self.transparent else (0, 0, 0)
            self.screen.fill(background_color)  # 根据透明状态设置背景颜色
            for btn in self.btns:
                btn.draw()
            # 画一个白色的按钮，带有“C”标签
            pygame.draw.rect(self.screen, (255, 255, 255), self.transparency_button)
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render('C', True, (0, 0, 0))
            self.screen.blit(text_surface, (self.transparency_button.x + 45, self.transparency_button.y + 5))
            pygame.display.update()
            self.fclock.tick(self.fps)
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.transparency_button.collidepoint(x, y):
                self.transparent = not self.transparent
                self.toggle_transparency(self.transparent)
            elif not self.transparent:  # 如果窗口不透明，则允许拖动
                self.start_drag = True
                self.start_pos = x, y
                self.drag_offset = win32gui.GetWindowRect(self.hwnd)[:2]
                for btn in self.btns:
                    if btn.collidepoint(x, y):
                        self.dragging_block = btn
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            self.start_drag = False
            self.dragging_block = None
        elif event.type == pygame.MOUSEMOTION and self.start_drag and not self.transparent:  # 如果窗口不透明，则允许拖动
            x, y = event.pos
            dx, dy = x - self.start_pos[0], y - self.start_pos[1]
            if self.dragging_block:
                self.dragging_block.move(dx, dy)
            self.start_pos = x, y

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SSVEP Control")
    parser.add_argument('--freqs', nargs='*', type=float, default=[15.1, 15.2, 15.3, 15.4], help="Frequencies for SSVEP blocks")
    args = parser.parse_args()
    positions = [(150, 0), (0, 150), (150, 150), (300, 150)]
    freqs = list(zip(positions, args.freqs))
    app = SSVEPApp(freqs)
    app.run()