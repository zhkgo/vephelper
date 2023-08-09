import random
import time
from algorithm.AlgorithmImplementSSVEP import AlgorithmImplementSSVEP
from parses.dsi import DSIDevice
import threading
import pyautogui
class Task:
    def __init__(self):
        self.ops_name = ["up", "left", "space", "right"]
    def report(self, result):
        print(result)
        if result == 0:
            return None
        result -= 1
        op = self.ops_name[result]
        print(op)
        pyautogui.press(op)

algor = AlgorithmImplementSSVEP()
algor.tcp = DSIDevice("127.0.0.1", 8844, "dsi")
algor.tcp.create_batch()
algor.task=Task()
thread = threading.Thread(target=algor.tcp.parse_data)
thread.start()
print("系统初始化中")
time.sleep(2)
algor.tcp.addmark()
algor.run()
# import pyautogui
#
# while True:
#     eventicon1 = pyautogui.locateOnScreen("C:/Users/m1526/Desktop/target1.png")
#     # eventicon2 = pyautogui.locateOnScreen("C:/Users/m1526/Desktop/target2.png")
#     if eventicon1 is not None:
#         pyautogui.leftClick(eventicon1,)
    # if eventicon2 is not None:
    #     pyautogui.leftClick(eventicon2, )
        # pyautogui.sleep(0.5)
# pyautogui.leftClick(910,223,0.3)


