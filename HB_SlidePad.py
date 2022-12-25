import pygame
import math
from PlayerTracking import pt2

class SlidePad:
    def __init__(self, position:list or tuple, stageArea:pygame.Rect, color = (255, 0, 0), radius = 80, drawFrag = False):
        self.rectList = []
        self.position = position
        self.color = color
        self.radius = radius
        self.drawFrag = drawFrag
        self.padPosition = list(position)
        self.defaultSpeed = 20
        self.stageArea = stageArea

    def update(self, currentPosit:pygame.Rect, pt2:pt2):
        padX = (pt2.beforeData[0][2] - 0.5) / 0.6
        padY = (pt2.beforeData[0][3] - 0.5) / 0.6
        if padX > 0.5:
            padX = 0.5
        elif padX < -0.5:
            padX = -0.5
        if padY > 0.5:
            padY = 0.5
        elif padY < -0.5:
            padY = -0.5
        #temp = math.sqrt(padX**2 + padY**2)
        #radian = math.acos(padX / temp) if temp != 0 else 0
        #self.padPosition[0] = self.position[0] + self.radius / 2 * math.cos(radian) * abs(padX / 0.5)
        #self.padPosition[1] = self.position[1] + self.radius / 2 * math.sin(radian) * abs(padY / 0.5)
        #ベクトルの正規化
        tempVector = math.sqrt(padX**2 + padY**2)
        self.padPosition[0] = self.position[0] + self.radius * 0.5 * padX / tempVector * abs(padX) * 2 if tempVector != 0 else 0
        self.padPosition[1] = self.position[1] + self.radius * 0.5 * padY / tempVector * abs(padY) * 2 if tempVector != 0 else 0
        progPosit = list(currentPosit.center)
        progPosit[0] += padX * self.defaultSpeed
        progPosit[1] += padY * self.defaultSpeed
        if progPosit[0] <= self.stageArea.left:
            progPosit[0] = self.stageArea.left
        elif progPosit[0] >= self.stageArea.right:
            progPosit[0] = self.stageArea.right
        if progPosit[1] <= self.stageArea.top:
            progPosit[1] = self.stageArea.top
        elif progPosit[1] >= self.stageArea.bottom:
            progPosit[1] = self.stageArea.bottom
        return progPosit

    def draw(self, screen):
        if not self.drawFrag:
            return []
        self.rectList = []
        self.rectList.append(pygame.draw.circle(screen, self.color, self.position, self.radius, 1))
        self.rectList.append(pygame.draw.circle(screen, self.color, self.padPosition, self.radius / 2))
        return self.rectList
        