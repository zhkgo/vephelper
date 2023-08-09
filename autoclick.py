import pyautogui

while True:
    eventicon1 = pyautogui.locateOnScreen("C:/Users/m1526/Desktop/hongbao.png")
    # eventicon2 = pyautogui.locateOnScreen("C:/Users/m1526/Desktop/target2.png")
    print(eventicon1)
    if eventicon1 is not None:
        pyautogui.leftClick(eventicon1)
    # if eventicon2 is not None:
    #     pyautogui.leftClick(eventicon2, )
    # pyautogui.sleep(0.3)
# pyautogui.leftClick(910,223,0.3)