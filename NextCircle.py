import pygame

class NextCircle:
    def __init__(self, pos: tuple, color:tuple, radius = 1, text = None, limitFrame = 60, thickness = 1):
        self.radius = radius
        radius += 1
        self.circleColor = color
        self.limitFrame = 1. / limitFrame
        self.pos = pos
        self.rect = pygame.Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)
        self.thickness = thickness
        self.counter = 0.
        self.addSurface = None
        self.text = text
        self.textFlash = 5
        self.textColor = 255
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.goNext = False

    def draw(self, screen):
        self.surface.set_colorkey((0, 0, 0))
        screen.blit(self.surface, self.rect)
        return self.rect

    def addSur(self, sur = None):
        self.addSurface = sur

    def addText(self, text = None, flashNum = 5):
        self.text = text
        self.textFlash = flashNum

    def judge(self):
        return self.goNext
    
    def resetFlag(self):
        self.goNext = False
        self.counter = 0

    def update(self, ptWRate, ptHRate, winSize):
        self.surface.fill((0, 0, 0))
        pygame.draw.circle(self.surface, self.circleColor, (self.radius + 1, self.radius + 1), self.radius, self.thickness)
        tempW = ptWRate * winSize[0]
        tempH = ptHRate * winSize[1]
        if (tempW - self.pos[0])**2 + (tempH - self.pos[1])**2 <= self.radius**2:
            self.counter = self.counter + self.limitFrame if self.counter < 1 else 1.
            if self.counter == 1.:
                self.goNext = True
        else:
            self.counter = self.counter - self.limitFrame if self.counter > 0 else 0.
        if self.counter == 0.:
            pass
        else:
            pygame.draw.circle(self.surface, self.circleColor, (self.radius + 1, self.radius + 1), self.radius * self.counter, 0)
        if self.addSurface != None:
            tempW, tempH = self.addSurface.get_size()
            self.surface.blit(self.addSurface, (self.radius + 1 - tempW * 0.5, self.radius + 1 - tempH * 0.5))
        if self.textFlash != None:
            if self.textFlash != None:
                if self.textColor == 255:
                    self.textFlash = abs(self.textFlash) * -1
                elif self.textColor == 0:
                    self.textFlash = abs(self.textFlash)
                self.textColor += self.textFlash
            textSur = pygame.font.SysFont(None, int(self.radius / 3)).render(self.text, True, (self.textColor, self.textColor, self.textColor))
            tempW, tempH = textSur.get_size()
            self.surface.blit(textSur, (self.radius + 1 - tempW * 0.5, self.radius + 1 - tempH * 0.5))