import numpy as np
import cv2
import os


## player manager
class pt2:
    def __init__(self, trackSize = 1):
        self.ct2 = ct2()
        self.trackSize = trackSize
        self.beforeData = [[0 for i in range(6)]]
        self.currentData = [[0 for i in range(6)]]

    def set_color(self, countTime = 5000):
        self.ct2.set_player_color(countTime)

    def set_color_file(self, fileName):
        filePath = "./ColorData/" + fileName + ".csv"
        if not os.path.isfile(filePath):
            return False
        playerData = np.loadtxt(filePath, delimiter=',', dtype=str)
        playerData = playerData.tolist()
        self.ct2.player = [0, 0, 0, 0, 0]
        self.ct2.playerInfo = int(playerData[0])
        for i, j, k, l in zip(range(len(playerData[1::3])), playerData[1::3], playerData[2::3], playerData[3::3]):
            self.ct2.player[i] = np.array([int(j), int(k), int(l)])

    def set_color_dynamic(self):
        self.ct2.set_player_color_dynamic()

    def set_track_size(self, trackSize):
        self.trackSize = trackSize

    def get_data(self):
        self.get_datas(1)
        return self.currentData[0]

    def get_datas(self, num = 0):
        self.beforeData = self.currentData
        if num == 0:
            num = self.trackSize
        retval, labels, stats, centroids = self.ct2.get_player_component()
        indexMax = 0
        if retval == 1:
            return [[0 for i in range(6)]]
        if num >= stats.size:
            num = stats.size - 1
        for i in range(num):
            self.currentData = []
            tempData = []
            height, width = labels.shape
            indexMax = np.argmax(stats[1:, 4]) + 1
            tempData.append(centroids[indexMax, 0])
            tempData.append(centroids[indexMax, 1])
            width = tempData[0] / width if width != 0 else 0
            height = tempData[1] / height if height != 0 else 0
            tempData.append(width)
            tempData.append(height)
            tempData.append(stats[indexMax, 2])
            tempData.append(stats[indexMax, 3])
            tempData.append(stats[indexMax, 4])
            stats = np.delete(stats, indexMax, 0)
            self.currentData.append(tempData)
        # [重心x,　重心y, 左を起点とした横全体を1とする位置xの割合, 上を起点とした縦全体を1とする位置yの割合, 幅, 高さ, トラック領域の大きさ]
        return self.currentData

    def save_color(self, fileName):
        filePath = "./ColorData/" + fileName + ".csv"
        dataStr = ""
        dataStr += str(self.ct2.playerInfo)
        counter = 5 if self.ct2.playerInfo == 4 else 3
        for i in self.ct2.player:
            counter -= 1
            dataStr += ',' + str(i[0]) + ',' + str(i[1]) + ',' + str(i[2])
            if counter == 0:
                break
        with open(filePath, mode='w') as f:
            f.write(dataStr)
        return filePath


## color tracking
class ct2:
    camera = cv2.VideoCapture(0)
    defaultCameraResolution = [camera.get(cv2.CAP_PROP_FRAME_WIDTH), camera.get(cv2.CAP_PROP_FRAME_HEIGHT)]
    defaultFrame = 0
    classFrame = 0
    def __init__(self):
        if self.camera.get(cv2.CAP_PROP_FRAME_WIDTH) == self.defaultCameraResolution[0] and self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT) == self.defaultCameraResolution[1]:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.defaultCameraResolution[0] / 4)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.defaultCameraResolution[1] / 4)
            print("解像度変更")
        self.camera.read()
        self.player = [0, 0, 0, 0, 0]
        self.playerInfo = 0
        self.mask = 0

    def get_camera_resolution(self):
        return [self.camera.get(cv2.CAP_PROP_FRAME_WIDTH), self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)]

    def set_player_color(self, countTime = 5000):
        while(self.camera.isOpened()):
            _ret, frame = self.camera.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (int(ct2.defaultCameraResolution[0]), int(ct2.defaultCameraResolution[1])))
            gbrTemp = np.copy(frame)
            height, width, _rgb = frame.shape
            height = int(height / 2)
            width = int(width / 2)
            frame[height - 10:height + 10, width - 1:width + 1] = 0
            frame[height - 1:height + 1, width - 10:width + 10] = 0
            cv2.putText(frame, str(countTime / 1000.), (int(width * 0.8), int(height * 0.8)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
            cv2.imshow("set_player_color", frame)
            if cv2.waitKey(100) == ord(' '):
                countTime = 0
            countTime -= 100
            if countTime < 0:
                height = height - 5
                width = width - 5
                hsvTemp0 = cv2.cvtColor(gbrTemp, cv2.COLOR_BGR2HSV)
                self.player[0] = np.array([int(np.average(hsvTemp0[height:height + 10, width:width + 10, 0])), int(np.average(hsvTemp0[height:height + 10, width:width + 10, 1])), int(np.average(hsvTemp0[height:height + 10, width:width + 10, 2]))])
                if self.player[0][2] <= 50:
                    self.playerInfo = 2
                elif self.player[0][1] <= 30 and self.player[0][2] >= 200 + self.player[0][1]:
                    self.playerInfo = 3
                break
        cv2.destroyWindow("set_player_color")
        self.player_color_range_judge()
        return True

    def set_player_color_dynamic(self):
        while(self.camera.isOpend()):
            pass

    def player_color_range_judge(self):
        if self.playerInfo == 2:
            #hsvBrack
            self.player[1] = np.array([0, 0, 0])
            self.player[2] = np.array([180, 255, 50])
        elif self.playerInfo == 3:
            #hsvWhite
            self.player[1] = np.array([0, 0, 200])
            self.player[2] = np.array([180, 30, 255])
        else:
            #small or wide
            hsvTemp = self.player[0]
            if hsvTemp[1] >= 128:
                widthH = 5
                if hsvTemp[0] < widthH:
                    self.playerInfo = 4
                    self.player[1] = np.array([0, 128, 0])
                    self.player[2] = np.array([hsvTemp[0] + widthH, 255, 255])
                    self.player[3] = np.array([180 + hsvTemp[0] - widthH, 128, 0])
                    self.player[4] = np.array([180, 255, 255])
                elif hsvTemp[0] > 180 - widthH:
                    self.playerInfo = 4
                    self.player[1] = np.array([hsvTemp[0] - widthH, 128, 0])
                    self.player[2] = np.array([180, 255, 255])
                    self.player[3] = np.array([0, 128, 0])
                    self.player[4] = np.array([hsvTemp[0] + widthH - 180, 255, 255])
                else:
                    self.playerInfo = 1
                    self.player[1] = np.array([hsvTemp[0] - widthH, 128, 0])
                    self.player[2] = np.array([hsvTemp[0] + widthH, 255, 255])
            else:
                widthH, widthS, widthV = 10, 20, 80
                hsvMin = [0, 0, 0]
                hsvMax = [0, 0, 0]
                if hsvTemp[0] < widthH or hsvTemp[0] > 180 - widthH:
                    self.playerInfo = 4
                    tempBool = hsvTemp[0] < widthH
                    hsvMin2 = [0, 0, 0]
                    hsvMax2 = [0, 0, 0]
                    hsvMin[0] = 0 if tempBool else hsvTemp[0] - widthH
                    hsvMax[0] = hsvTemp[0] + widthH if tempBool else 180
                    hsvMin2[0] = hsvTemp[0] + 180 - widthH if tempBool else 0
                    hsvMax2[0] = 180 if tempBool else hsvTemp[0] + widthH - 180
                    tempBool = hsvTemp[1] < widthS
                    hsvMin[1] = int(hsvTemp[1] / 2) if tempBool else hsvTemp[1] - widthS
                    hsvMin2[1] = hsvMin[1]
                    tempBool = hsvTemp[1] > 255 - widthS
                    hsvMax[1] = int((hsvTemp[1] + 255) / 2) if tempBool else hsvTemp[1] + widthS
                    hsvMax2[1] = hsvMax[1]
                    tempBool = hsvTemp[2] < widthV
                    hsvMin[2] = int(hsvTemp[2] / 2) if tempBool else hsvTemp[2] - widthV
                    hsvMin2[2] = hsvMin[2]
                    tempBool = hsvTemp[2] > 255 - widthV
                    hsvMax[2] = int((hsvTemp[2] + 255) / 2) if tempBool else hsvTemp[2] + widthV
                    hsvMax2[2] = hsvMax[2]
                    self.player[3] = np.array(hsvMin2)
                    self.player[4] = np.array(hsvMax2)
                else:
                    self.playerInfo = 1
                    hsvMin[0] = hsvTemp[0] - widthH
                    hsvMax[0] = hsvTemp[0] + widthH
                    hsvMin[1] = int(hsvTemp[1] / 2) if hsvTemp[1] < widthS else hsvTemp[1] - widthS
                    hsvMax[1] = int((255 + hsvTemp[1]) / 2) if hsvTemp[1] > 255 - widthS else hsvTemp[1] + widthS
                    hsvMin[2] = int(hsvTemp[2] / 2) if hsvTemp[2] < widthV else hsvTemp[2] - widthV
                    hsvMax[2] = int((255 + hsvTemp[2]) / 2) if hsvTemp[2] > 255 - widthV else hsvTemp[2] + widthV
                self.player[1] = np.array(hsvMin)
                self.player[2] = np.array(hsvMax)

    def get_player_component(self):
        if self.playerInfo == 4:
            mask1 = cv2.inRange(self.classFrame, self.player[1], self.player[2])
            mask2 = cv2.inRange(self.classFrame, self.player[3], self.player[4])
            self.mask = mask1 + mask2
        else:
            self.mask = cv2.inRange(self.classFrame, self.player[1], self.player[2])
        return cv2.connectedComponentsWithStats(self.mask)

## ct2 static method
def set_capture_read() -> bool:
    ret, ct2.defaultFrame = ct2.camera.read()
    ct2.defaultFrame = cv2.flip(ct2.defaultFrame, 1)
    ct2.classFrame = cv2.cvtColor(ct2.defaultFrame, cv2.COLOR_BGR2HSV)
    return ret

def set_camera_resolution(width:int, height:int) -> bool:
    return ct2.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width) and ct2.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

## test program
def main():
    global tempFrame, HSVdata
    def mouse_event_main(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            global HSVdata
            temp = tempFrame[y, x]
            HSVdata = "H:" + str(int(temp[0])) + ", S:" + str(int(temp[1])) + ", V:" + str(int(temp[2]))
        pass

    def mouse_event_edit(event, x, y, flags, param):
        pass

    HSVdata = "Left mouse button down"
    mainWin = "main"
    editWin = "edit"
    cv2.namedWindow(mainWin)
    cv2.namedWindow(editWin)
    cv2.setMouseCallback(mainWin, mouse_event_main)
    cv2.setMouseCallback(editWin, mouse_event_edit)
    camera = cv2.VideoCapture(0)
    aski = 0
    mask1 = np.array([105,128,0])
    mask2 = np.array([115,255,255])
    mask1Index = 0
    mask2Index = 0
    while camera.isOpened():
        edit = np.zeros([400, 400], dtype="uint8")
        cv2.putText(edit, "HSV_UPLIMIT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, "HSV_DOWNLIMIT", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, str(mask2[0]), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, str(mask2[1]), (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, str(mask2[2]), (300, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, str(mask1[0]), (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, str(mask1[1]), (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(edit, str(mask1[2]), (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        _ret, frame = camera.read()
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, HSVdata, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.imshow(mainWin, frame)
        tempFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(tempFrame, mask1, mask2)
        cv2.imshow("mask", mask)
        cv2.imshow(editWin, edit)
        aski = cv2.waitKey(100)
        if aski == ord('w'):
            mask1Index = mask1Index + 1 if mask1Index < 2 else 2
        elif aski == ord('a'):
            mask1[mask1Index] = mask1[mask1Index] - 1 if mask1[mask1Index] > 0 else 0
        elif aski == ord('s'):
            mask1Index = mask1Index - 1 if mask1Index > 0 else 0
        elif aski == ord('d'):
            if mask1Index == 0:
                mask1[mask1Index] = mask1[mask1Index] + 1 if mask1[mask1Index] < 180 else 180
            else:
                mask1[mask1Index] = mask1[mask1Index] + 1 if mask1[mask1Index] < 255 else 255
        elif aski == ord('u'):
            mask2Index = mask2Index + 1 if mask1Index < 2 else 2
        elif aski == ord('h'):
            mask2[mask2Index] = mask2[mask2Index] - 1 if mask2[mask2Index] > 0 else 0
        elif aski == ord('j'):
            mask2Index = mask2Index - 1 if mask1Index > 0 else 0
        elif aski == ord('k'):
            if mask2Index == 0:
                mask2[mask2Index] = mask2[mask2Index] + 1 if mask2[mask2Index] < 180 else 180
            else:
                mask2[mask2Index] = mask2[mask2Index] + 1 if mask2[mask2Index] < 255 else 255
        elif aski == ord('q'):
            print(mask1, mask2)
            print(tempFrame)
            print(mask)
            break
    cv2.destroyAllWindows()
    



if __name__ == '__main__':
    main()