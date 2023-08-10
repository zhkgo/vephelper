import json

import pygame, sys
import win32api
import win32con
import win32gui
import math
import argparse
suf = None
import pygame.freetype

class SSVEPControl:
    def __init__(self, screen,  basepos = (100,100), size = 4, num=(9,9), freq = 10 , fps=60):
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
        alpha = max(math.sin(self.freq/self.fps*self.cnt*2*math.pi), 0)
        self.cnt += 1
        alpha = int(alpha*255)
        for i,line in enumerate(self.sufs):
            for j,suf in enumerate(line):
                suf.set_alpha(alpha)
                self.screen.blit(suf, (self.basepos[0] + (2 * i + 1) * self.size, self.basepos[1] + (2 * j + 1) * self.size))
    def move(self, dx, dy):
        self.basepos = (self.basepos[0] + dx, self.basepos[1] + dy)
        self.rect.move_ip(dx, dy)
    def reset_cnt(self):
        self.cnt = 0

    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)
def showWindow(transparent=False,size=(900,900)):
    screen = None
    if not transparent:
        screen = pygame.display.set_mode(size, flags= pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode(size, flags=pygame.NOFRAME)
    pygame.display.set_caption("SSVEP(made by zhkgo)")
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
        self.transparent = False
        self.screen = showWindow(self.transparent, self.screen_size)
        self.fuchsia = (255, 0, 128)
        self.fps = 60
        self.btns = [SSVEPControl(self.screen, basepos=pos, freq=freq, fps=self.fps, size=4.5) for pos, freq in freqs]
        self.transparency_button = pygame.Rect(10, 10, 30, 30)
        self.button_image = pygame.image.load('resources/trans.png')
        self.button_image = pygame.transform.scale(self.button_image, (30, 30))
        self.add_button = pygame.Rect(120, 10, 100, 30)
        self.remove_button = pygame.Rect(230, 10, 100, 30)
        self.start_drag = False
        self.start_pos = (0, 0)
        self.dragging_block = None
        self.fclock = pygame.time.Clock()
        self.hwnd = pygame.display.get_wm_info()["window"]
        self.toggle_transparency(self.transparent)
        self.adding_frequency = False
        self.removing_frequency = False
        self.input_text = ""
        font_path = "resources/SourceHanSerifCN-SemiBold-7.otf"
        self.font = pygame.freetype.Font(font_path, 18)
        self.save_button = pygame.Rect(340, 10, 100, 30)
        self.load_button = pygame.Rect(450, 10, 100, 30)
        self.show_save_success = False
        # 尝试自动加载配置
        self.load_configuration()
    def reset_all_cnt(self):
        for btn in self.btns:
            btn.reset_cnt()
    def toggle_transparency(self, transparent):
        # 获取当前窗口位置和大小
        x, y, width, height = win32gui.GetWindowRect(self.hwnd)
        # 根据透明状态更新窗口
        self.screen = showWindow(transparent, (width - x, height - y))
        # 恢复窗口位置
        win32gui.SetWindowPos(self.hwnd, 0, x, y, 0, 0, win32con.SWP_NOSIZE)
        if transparent:
            win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(*self.fuchsia), 0, win32con.LWA_COLORKEY)
        else:
            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            background_color = self.fuchsia if self.transparent else (0, 0, 0)
            self.screen.fill(background_color)
            for btn in self.btns:
                btn.draw()
            if not self.transparent:  # 在非透明时绘制闪烁块并显示频率
                for btn in self.btns:
                    text_surface, _ = self.font.render(str(btn.freq) + ' Hz', (255, 255, 255))
                    self.screen.blit(text_surface, (btn.basepos[0] + 5, btn.basepos[1] - 25))
                # 在非透明时绘制增加和删除按钮
                pygame.draw.rect(self.screen, (0, 255, 0), self.add_button)
                pygame.draw.rect(self.screen, (255, 0, 0), self.remove_button)
                self.screen.blit(self.font.render('Add', (0, 0, 0))[0], (self.add_button.x + 35, self.add_button.y + 5))
                self.screen.blit(self.font.render('Remove', (0, 0, 0))[0], (self.remove_button.x + 25, self.remove_button.y + 5))
                if self.adding_frequency or self.removing_frequency:
                    prompt = "Enter frequency to add: " if self.adding_frequency else "Enter frequency to remove: "
                    text_surface, _ = self.font.render(prompt + self.input_text, (255, 255, 255))
                    self.screen.blit(text_surface, (50, 250))
                # 绘制保存和加载按钮
                pygame.draw.rect(self.screen, (0, 0, 255), self.save_button)
                pygame.draw.rect(self.screen, (255, 165, 0), self.load_button)
                self.screen.blit(self.font.render('Save', (0, 0, 0))[0],
                                 (self.save_button.x + 30, self.save_button.y + 5))
                self.screen.blit(self.font.render('Load', (0, 0, 0))[0],
                                 (self.load_button.x + 30, self.load_button.y + 5))
                if self.show_save_success:
                    pygame.draw.rect(self.screen, (0, 255, 0), (200, 130, 100, 40))
                    text_surface, _ = self.font.render('Saved!', (0, 0, 0))
                    self.screen.blit(text_surface, (215, 145))
                    pygame.display.update()
                    pygame.time.delay(1000)
                    self.show_save_success = False

            fps = self.fclock.get_fps()

            # Update the window title with the current frame rate
            pygame.display.set_caption(f"Frame Rate: {fps:.2f} FPS")
            self.screen.blit(self.button_image, (10, 10))
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
                if self.add_button.collidepoint(x, y):
                    self.adding_frequency = True
                    self.input_text = ""
                elif self.remove_button.collidepoint(x, y) and self.btns:
                    self.removing_frequency = True
                    self.input_text = ""

                if self.save_button.collidepoint(x, y):
                    self.save_configuration()
                elif self.load_button.collidepoint(x, y):
                    self.load_configuration()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.start_drag = False
            self.dragging_block = None
        elif event.type == pygame.MOUSEMOTION and self.start_drag and not self.transparent:  # 如果窗口不透明，则允许拖动
            x, y = event.pos
            dx, dy = x - self.start_pos[0], y - self.start_pos[1]
            if self.dragging_block:
                self.dragging_block.move(dx, dy)
            self.start_pos = x, y
        elif event.type == pygame.KEYDOWN and (self.adding_frequency or self.removing_frequency):
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                freq = float(self.input_text)
                if self.adding_frequency:
                    self.btns.append(SSVEPControl(self.screen, basepos=(200, 200), freq=freq, fps=self.fps, size=4.5))
                elif self.removing_frequency:
                    self.btns = [btn for btn in self.btns if btn.freq != freq]
                self.reset_all_cnt()  # 重置所有刺激块的cnt
                self.adding_frequency = self.removing_frequency = False
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode

    def save_configuration(self):
        x, y, width, height = win32gui.GetWindowRect(self.hwnd)
        config = {
            'window_position': (x, y),
            'window_size': (width - x, height - y),
            'blocks': [{'basepos': btn.basepos, 'freq': btn.freq} for btn in self.btns]
        }
        with open('config.json', 'w') as file:
            json.dump(config, file)
        self.show_save_success = True

    def load_configuration(self):
        try:
            with open('config.json', 'r') as file:
                config = json.load(file)
            x, y = config['window_position']
            self.screen_size = config['window_size']
            self.screen = showWindow(self.transparent, self.screen_size)
            win32gui.SetWindowPos(self.hwnd, 0, x, y, *self.screen_size, 0)
            self.btns = [SSVEPControl(self.screen, **block) for block in config['blocks']]
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SSVEP Control")
    parser.add_argument('--freqs', nargs='*', type=float, default=[15.1, 15.2, 15.3, 15.4], help="Frequencies for SSVEP blocks")
    args = parser.parse_args()
    positions = [(150, 0), (0, 150), (150, 150), (300, 150)]
    freqs = list(zip(positions, args.freqs))
    app = SSVEPApp(freqs)
    app.run()