import pygame
from HB_Font import *
from GPIOController import GPIOCo
hbGPIO = GPIOCo()

#ステージ&画面構成(インスタンス化必要)
class Stage:
    def __init__(self, stageSize:tuple or list, winSize = (600, 600)):
        self.stageSize = stageSize
        self.stagePos = pygame.Rect((winSize[0] - stageSize[0]) / 2, (winSize[1] - stageSize[1]) / 2, stageSize[0], stageSize[1])
        self.winSize = winSize
        self.rectList = None
        self.player = None
        self.enemy = None

    def setCharacter(self, player = None, enemy = None):
        self.player = player
        self.enemy = enemy

    def update(self):
        pass

    def draw(self, screen):
        self.rectList = []
        font = pygame.font.SysFont(pygameJaFont, 50)
        if self.player != None:
            fontSur = font.render("自分", False, (255, 255, 255))
            self.rectList.append(screen.blit(fontSur, (1, 550)))
            self.rectList.append(pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(4, 454, 140, 90), 3))
            self.rectList.append(pygame.draw.rect(screen, (255, 20, 20), pygame.Rect(7, 457, 134 * (self.player.currentHitPoint / self.player.maxHitPoint), 84)))
        if self.enemy != None:
            fontSur = font.render("相手", False, (255, 255, 255))
            self.rectList.append(screen.blit(fontSur, (451, 0)))
            self.rectList.append(pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(454, 54, 140, 90), 3))
            self.rectList.append(pygame.draw.rect(screen, (255, 20, 20), pygame.Rect(457, 57, 134 * (self.enemy.currentHitPoint / self.enemy.maxHitPoint), 84)))
        self.rectList.append(pygame.draw.line(screen, (255, 255, 255), self.stagePos.topleft, self.stagePos.topright, 3))
        self.rectList.append(pygame.draw.line(screen, (255, 255, 255), self.stagePos.topright, self.stagePos.bottomright, 3))
        self.rectList.append(pygame.draw.line(screen, (255, 255, 255), self.stagePos.bottomright, self.stagePos.bottomleft, 3))
        self.rectList.append(pygame.draw.line(screen, (255, 255, 255), self.stagePos.bottomleft, self.stagePos.topleft, 3))
        return self.rectList

    def ballReflectCalc(self, progPosit, tempSpeed, radius, threshold = 50, reflectRate = 0.8):
        temp1 = self.stagePos.left + radius
        temp2 = self.stagePos.right - radius
        if progPosit[0] <= temp1:
            hbGPIO.RunBuzzerFrequency(600, 0.1)
            progPosit[0] = temp1 * 2 - progPosit[0]
            if tempSpeed[0] > threshold:
                tempSpeed[0] = -1 * tempSpeed[0] * reflectRate
            else:
                tempSpeed[0] = -1 * tempSpeed[0]
        elif progPosit[0] >= temp2:
            hbGPIO.RunBuzzerFrequency(700, 0.1)
            progPosit[0] = temp2 * 2 - progPosit[0]
            if tempSpeed[0] > threshold:
                tempSpeed[0] = -1 * tempSpeed[0] * reflectRate
            else:
                tempSpeed[0] = -1 * tempSpeed[0]
        temp1 = self.stagePos.top + radius
        temp2 = self.stagePos.bottom - radius
        if progPosit[1] <= temp1:
            hbGPIO.RunBuzzerFrequency(800, 0.1)
            progPosit[1] = temp1 * 2 - progPosit[1]
            if tempSpeed[1] > threshold:
                tempSpeed[1] = -1 * tempSpeed[1] * reflectRate
            else:
                tempSpeed[1] = -1 * tempSpeed[1]
        elif progPosit[1] >= temp2:
            hbGPIO.RunBuzzerFrequency(900, 0.1)
            progPosit[1] = temp2 * 2 - progPosit[1]
            if tempSpeed[1] > threshold:
                tempSpeed[1] = -1 * tempSpeed[1] * reflectRate
            else:
                tempSpeed[1] = -1 * tempSpeed[1]
        return list(progPosit), list(tempSpeed)

#ホッケーモード用ステージ
class HockeyStage(Stage):
    def __init__(self, stageSize:tuple or list, winSize = (600, 600), goalHalfLen = 50, maxPoint = 9):
        super().__init__(stageSize, winSize)
        self.lineList = [[self.stagePos.topleft, [self.stagePos.centerx - goalHalfLen, self.stagePos.top]], [[self.stagePos.centerx + goalHalfLen, self.stagePos.top], self.stagePos.topright], [self.stagePos.topright, self.stagePos.bottomright], [self.stagePos.bottomright, [self.stagePos.centerx + goalHalfLen, self.stagePos.bottom]], [[self.stagePos.centerx - goalHalfLen, self.stagePos.bottom], self.stagePos.bottomleft], [self.stagePos.bottomleft, self.stagePos.topleft], [[self.stagePos.left, self.stagePos.centery], [self.stagePos.right, self.stagePos.centery]]]
        self.enemyLineList = [[[self.stagePos.centerx - goalHalfLen, self.stagePos.top], [self.stagePos.centerx - goalHalfLen, 0]], [[self.stagePos.centerx - goalHalfLen, 0], [self.stagePos.centerx + goalHalfLen, 0]], [[self.stagePos.centerx + goalHalfLen, 0], [self.stagePos.centerx + goalHalfLen, self.stagePos.top]]]
        self.playerLineList = [[[self.stagePos.centerx - goalHalfLen, self.stagePos.bottom], [self.stagePos.centerx - goalHalfLen, winSize[1]]], [[self.stagePos.centerx - goalHalfLen, winSize[1]], [self.stagePos.centerx + goalHalfLen, winSize[1]]], [[self.stagePos.centerx + goalHalfLen, winSize[1]], [self.stagePos.centerx + goalHalfLen, self.stagePos.bottom]]]
        self.goalLineList = []
        self.ballList = []
        self.goalHalfLen = goalHalfLen
        self.goalFrag = 0
        self.goalLineFrag = False
        self.maxPoint = maxPoint
        self.playerPoint = 0
        self.enemyPoint = 0
        font = pygame.font.SysFont(pygameJaFont, 50)
        fonts = pygame.font.SysFont(pygameJaFont, 20)
        self.textList = [[font.render("あいて", False, (255, 255, 255)), (1, 1)], [font.render("あなた", False, (255, 255, 255)), (1, winSize[1] - 50)], [fonts.render(str(maxPoint) + "点先取", False, (200, 200, 200)), (1, winSize[1] / 2 - 10)], [fonts.render("点", False, (255, 255, 255)), (winSize[0] - 20, 20)], [fonts.render("点", False, (255, 255, 255)), (winSize[0] - 20, winSize[1] - 20)]]
        self.pointFont = pygame.font.SysFont(pygameEnFont, 50)
        self.onceRectList = []

    def addBall(self, ball):
        self.ballList.append(ball)

    def addLine(self, line):
        self.lineList.append(line)

    def getGoalFrag(self):
        return self.goalFrag

    def init(self):
        self.goalFrag = 0
        self.goalLineList = []
        self.goalLineFrag = False

    def update(self):
        pass

    def draw(self, screen:pygame.Surface):
        self.rectList = []
        for i in self.textList:
            self.onceRectList.append(screen.blit(i[0], i[1]))
            pygame.display.update(self.onceRectList)
            self.onceRectList = []
            self.textList = []
        for i in self.lineList:
            self.rectList.append(pygame.draw.line(screen, (255, 255, 255), i[0], i[1], 3))
        for i in self.enemyLineList:
            self.rectList.append(pygame.draw.line(screen, (0, 0, 255), i[0], i[1], 3))
        for i in self.playerLineList:
            self.rectList.append(pygame.draw.line(screen, (255, 0, 0), i[0], i[1], 3))
        if self.goalLineFrag:
            for i in self.goalLineList:
                self.rectList.append(pygame.draw.line(screen, (255, 255, 0), i[0], i[1], 3))
        fontSur = None
        if self.playerPoint < self.maxPoint - 1:
            fontSur = self.pointFont.render(str(self.playerPoint), False, (255, 255, 255))
        else:
            fontSur = self.pointFont.render(str(self.playerPoint), False, (255, 255, 0))
        self.rectList.append(screen.blit(fontSur, (self.winSize[0] - 100, self.winSize[1] - 50)))
        if self.enemyPoint < self.maxPoint - 1:
            fontSur = self.pointFont.render(str(self.enemyPoint), False, (255, 255, 255))
        else:
            fontSur = self.pointFont.render(str(self.enemyPoint), False, (50, 50, 255))
        self.rectList.append(screen.blit(fontSur, (self.winSize[0] - 100, 1)))
        return self.rectList

    def ballReflectCalc(self, progPosit, tempSpeed, radius):
        if self.goalFrag != 0:
            temp1 = self.stagePos.centerx - self.goalHalfLen + radius
            temp2 = self.stagePos.centerx + self.goalHalfLen - radius
            if progPosit[0] <= temp1:
                hbGPIO.RunBuzzerFrequency(1000, 0.1)
                progPosit[0] = temp1 * 2 - progPosit[0]
                tempSpeed[0] = -0.8 * tempSpeed[0]
                self.goalLineFrag = True
            elif progPosit[0] >= temp2:
                hbGPIO.RunBuzzerFrequency(1000, 0.1)
                progPosit[0] = temp2 * 2 - progPosit[0]
                tempSpeed[0] = -0.8 * tempSpeed[0]
                self.goalLineFrag = True
            temp1 = 0 + radius
            temp2 = self.winSize[1] - radius
            if progPosit[1] <= temp1:
                hbGPIO.RunBuzzerFrequency(1000, 0.1)
                progPosit[1] = temp1 * 2 - progPosit[1]
                tempSpeed[1] = -0.8 * tempSpeed[1]
                self.goalLineFrag = True
            elif progPosit[1] >= temp2:
                hbGPIO.RunBuzzerFrequency(1000, 0.1)
                progPosit[1] = temp2 * 2 - progPosit[1]
                tempSpeed[1] = -0.8 * tempSpeed[1]
                self.goalLineFrag = True
            if self.goalLineFrag:
                if progPosit[1] < self.stagePos.centery:
                    temp = self.stagePos.top - radius
                    if progPosit[1] >= temp:
                        hbGPIO.RunBuzzerFrequency(1000, 0.1)
                        progPosit[1] = temp * 2 - progPosit[1]
                        tempSpeed[1] = -0.8 * tempSpeed[1]
                else:
                    temp = self.stagePos.bottom + radius
                    if progPosit[1] <= temp:
                        hbGPIO.RunBuzzerFrequency(1000, 0.1)
                        progPosit[1] = temp * 2 - progPosit[1]
                        tempSpeed[1] = -0.8 * tempSpeed[1]
            return list(progPosit), list(tempSpeed)
        if self.stagePos.top + radius >= progPosit[1] or self.stagePos.bottom - radius <= progPosit[1]:
            if self.stagePos.centerx - self.goalHalfLen < progPosit[0] - radius and self.stagePos.centerx + self.goalHalfLen > progPosit[0] + radius:
                if progPosit[1] < self.winSize[1] / 2:
                    self.goalFrag = 1
                    self.playerPoint += 1
                else:
                    self.goalFrag = 2
                    self.enemyPoint += 1
                self.goalLineList.append([[self.stagePos.centerx - self.goalHalfLen, self.stagePos.top], [self.stagePos.centerx + self.goalHalfLen, self.stagePos.top]])
                self.goalLineList.append([[self.stagePos.centerx - self.goalHalfLen, self.stagePos.bottom], [self.stagePos.centerx + self.goalHalfLen, self.stagePos.bottom]])
                return list(progPosit), list(tempSpeed)
        return super().ballReflectCalc(progPosit, tempSpeed, radius)

#ステージボール(インスタンス化必要?)
class StageBall:
    def __init__(self, stage:Stage, color:tuple, initPosition:tuple or list, radius:int or float, initSpeed = (100, 50)):
        self.counter = 0
        self.position = list(initPosition)
        self.progPosit = None
        self.radius = radius
        self.speed = list(initSpeed)
        self.color = tuple(color)
        self.stage = stage

    def getCalcData(self):
        self.getProgPosit()
        return self.progPosit, self.speed, self.radius, self.position

    def setClockTick(self, counter):
        self.counter = counter

    def getProgPosit(self):
        progPosit = list(self.position)
        progPosit[0] += self.speed[0] * self.counter
        progPosit[1] += self.speed[1] * self.counter
        self.progPosit = progPosit

    def update(self, counter):
        tempPos, tempSpeed, tempRadius, currentPosit = self.getCalcData()
        self.counter = counter
        self.getProgPosit()
        #stage壁との衝突判定
        self.position, self.speed = self.stage.ballReflectCalc(self.progPosit, tempSpeed, tempRadius)

    def draw(self, screen):
        rectList = [pygame.draw.circle(screen, self.color, self.position, self.radius)]
        return rectList