import time
import sys
import asyncio

GPIOInitalized = False
try:
    import RPi.GPIO as GPIO
    GPIOInitalized = True
except:
    GPIOInitalized = False

#a
class GPIOCo:
    def __init__(self):
        ###### GPIO番号の設定 ######
        self.LED = [2, 3, 4]
        self.BUZZER = 17
        self.buzzerPWM = None
        self.buzzerIndex = 0
        if GPIOInitalized == False:
            return
        # GPIO初期化処理
        GPIO.setwarnings(False)
        ###### 初期化 ######
        GPIO.setmode(GPIO.BCM)
        for led in self.LED:
            GPIO.setup(led, GPIO.OUT)
            GPIO.output(led, GPIO.LOW)
        GPIO.setup(self.BUZZER, GPIO.OUT)
        self.buzzerPWM = GPIO.PWM(self.BUZZER, 1)
        self.buzzerPWM.stop()
    # LED
    def ClearLED(self):
        self.BlinkAllLED(False)
    def BlinkLED(self, index : int, blink : bool = True):
        if GPIOInitalized == False:
            return
        GPIO.output(self.LED[index], GPIO.HIGH if blink else GPIO.LOW)
    def BlinkAllLED(self, blink : bool = True):
        for i in range(len(self.LED)):
            self.BlinkLED(i, blink)
    # BUZZER
    def SetBuzzerFrequency(self, frequency : int):
        if GPIOInitalized == False:
            return
        self.buzzerPWM.ChangeFrequency(frequency)
        self.buzzerPWM.start(1)
    def StopBuzzerFrequency(self):
        if GPIOInitalized == False:
            return
        self.buzzerPWM.stop()
    def Test(self):
        # テスト用
        t = 0.2
        self.BlinkAllLED(False)
        self.RunBuzzerFrequency(200, t * 4)
        time.sleep(0.5)
        self.RunBuzzerFrequency(100, t * 2)
        for i in range(len(self.LED)):
            self.BlinkLED(i, True)
            time.sleep(t)
        self.ClearLED()
        for i in range(2):
            time.sleep(t)
            self.BlinkAllLED(True)
            time.sleep(t)
            self.BlinkAllLED(False)
        self.ClearLED()
    def Clear(self):
        if GPIOInitalized == False:
            return
        try:
            self.StopBuzzerFrequency()
            self.ClearLED()
        finally:
            GPIO.cleanup()
    
    def RunBuzzerFrequency(self, frequency : int, seconds : float):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_in_executor(None, self.__CallBuzzerFrequency__, frequency, seconds)
        #print("exec")
    def __CallBuzzerFrequency__(self, frequency : int, seconds : float):
        #print("call")
        self.buzzerIndex += 1
        index = self.buzzerIndex
        self.SetBuzzerFrequency(frequency=frequency)
        time.sleep(seconds)
        if (self.buzzerIndex == index):
            self.StopBuzzerFrequency()

def __main__():
    co = GPIOCo()
    co.Test()
    co.Clear()
if __name__ == '__main__':
    __main__()
