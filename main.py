import json
import time

import cv2
import numpy
import win32api
import win32con
import win32gui
import win32print
import win32ui


class Window:
    def __init__(self, name, cls=None):
        hDesktopDC = win32gui.GetDC(0)
        self.scale = win32print.GetDeviceCaps(hDesktopDC, win32con.DESKTOPHORZRES) \
            / win32print.GetDeviceCaps(hDesktopDC, win32con.HORZRES)
        win32gui.ReleaseDC(None, hDesktopDC)

        self.hWnd = win32gui.FindWindow(cls, name)
        assert self.hWnd

        self.hWndDC = win32gui.GetDC(self.hWnd)
        self.hMfcDc = win32ui.CreateDCFromHandle(self.hWndDC)
        self.hMemDc = self.hMfcDc.CreateCompatibleDC()

    def capture(self):
        width, height = [round(i*self.scale)
                         for i in win32gui.GetClientRect(self.hWnd)[2:]]
        hBmp = win32ui.CreateBitmap()
        hBmp.CreateCompatibleBitmap(self.hMfcDc, width, height)
        self.hMemDc.SelectObject(hBmp)
        self.hMemDc.BitBlt((0, 0), (width, height),
                           self.hMfcDc, (0, 0), win32con.SRCCOPY)
        result = numpy.frombuffer(hBmp.GetBitmapBits(
            True), dtype='uint8').reshape(height, width, 4)[..., :3]
        win32gui.DeleteObject(hBmp.GetHandle())
        return result

    def click(self, hold=0):
        win32api.PostMessage(self.hWnd, win32con.WM_LBUTTONDOWN, 0, 0)
        time.sleep(hold)
        win32api.PostMessage(self.hWnd, win32con.WM_LBUTTONUP, 0, 0)

    def show(self):
        cv2.imshow('Is the screenshot correct?', cv2.resize(
            self.capture(),(640,360)))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def __del__(self):
        self.hMemDc.DeleteDC()
        self.hMfcDc.DeleteDC()
        win32gui.ReleaseDC(self.hWnd, self.hWndDC)


window = Window('原神')

FRONT = cv2.imread('image/front.png')
FRONTMASK = cv2.imread('image/frontmask.png')
BACK = cv2.imread('image/back.png')
BACKMASK = cv2.imread('image/backmask.png')
CUR = cv2.imread('image/cur.png')
CURMASK = cv2.imread('image/curmask.png')

def check():
    im = cv2.resize(window.capture(), (1280, 720))
    CUR_loc = cv2.minMaxLoc(cv2.matchTemplate(im[55:160, 470:810], CUR, cv2.TM_SQDIFF_NORMED, mask=CURMASK))
    FRONT_loc = cv2.minMaxLoc(cv2.matchTemplate(im[55:160, 470:810], FRONT, cv2.TM_SQDIFF_NORMED, mask=FRONTMASK))
    BACK_loc = cv2.minMaxLoc(cv2.matchTemplate(im[55:160, 470:810], BACK, cv2.TM_SQDIFF_NORMED, mask=BACKMASK))

    rank = 0
    if CUR_loc[0] < 0.02:
        rank += 1
    if FRONT_loc[0] < 0.02:
        rank += 1
    if BACK_loc[0] < 0.02:
        rank += 1

    # print(str(CUR_loc[0]) + "  " + str(FRONT_loc[0]) + "  " + str(BACK_loc[0]))
    # return None

    if rank >= 2:
        return (FRONT_loc[2][0], BACK_loc[2][0], CUR_loc[2][0])
    else:
        return None

startKey = 0x77
endKey = 0x78

if __name__ == '__main__':
    print('钓鱼工具启动')

    count = 0
    while True:

        while True:
            if win32api.GetAsyncKeyState(startKey) != 0:
                print("打开自动钓鱼开关")
                time.sleep(0.5)
                break
            time.sleep(0.5)

        last_middle = 0
        persis_click = 0
        while True:
            if (win32api.GetAsyncKeyState(startKey) != 0):
                print("关闭自动钓鱼开关")
                time.sleep(0.5)
                break

            pos = check()
            if pos is None:
                # print("未检测到光标")
                time.sleep(0.1)
            else:
                front, back, cur = pos

                middle = (front+back)/2
                cur = cur + persis_click*10
                if cur < middle:
                    window.click(0.08)
                    persis_click += 1
                else:
                    if persis_click>2:
                        time.sleep(0.1)
                    persis_click = 0


