import PlayerTracking as PT
from PlayerTracking import pt2
from NextCircle import NextCircle
from HB_Stage import *
from HB_Player import *
from HB_Enemy import *
import pygame
import math
import sys


argv = None
try:
    argv = sys.argv[1]
except:
    pass

class HockeyBattle:

    def __init__(self):
        #ゲームに最低限必要
        self.pt2List = None
        self.winSize = None
        self.gameFrag = None
        self.clock = None
        self.counterRate = None
        #描画処理に必要
        self.rectList = None
        self.clearRectList = None
        #ゲームアセット
        self.stage = None
        self.player = None
        self.enemy = None
        self.stageBall = None
        self.tempList = None
        #その他
        self.colorName = "HBmasterColor"

    def init(self, masterSelf):
        self.pt2List = [pt2(), pt2()]
        if argv == "debug":
            self.pt2List = [DebugMouse((600, 600)), DebugMouse((600, 600))]
        elif masterSelf != "debug":
            masterSelf.getMasterPt2().save_color(self.colorName)
            self.pt2List[0].set_color_file(self.colorName)
            self.pt2List[1].set_color_file(self.colorName)
        else:
            self.pt2List[0].set_color()
            self.pt2List[1].set_color()
        self.winSize = (600, 600)
        self.gameFrag = "opset"
        self.clock = pygame.time.Clock()
        self.rectList = []
        self.clearRectList = []
        self.tempList = []
        self.counterRate = 1000

        
        pygame.display.init()
        pygame.display.set_mode(self.winSize, pygame.RESIZABLE)
        #self.pt2List[1].set_color()
        PT.set_capture_read()
        self.clock.tick()

    def update(self, masterSelf, events, deltaTime):
        if len(self.rectList) > 0:
            pygame.display.update(self.clearRectList)
            pygame.display.update(self.rectList)
        else:
            pygame.display.update()
        if self.gameFrag == None:
            pass
        else:
            PT.set_capture_read()
        self.clearRectList = self.rectList
        self.rectList = []

    def draw(self, screen:pygame.Surface):
        #前フレームの描画をクリア(once描画を実装)
        for i in range(len(self.clearRectList)):
            screen.fill((0, 0, 0), rect=self.clearRectList[i])
        
        counter = self.clock.tick() / self.counterRate

        if self.gameFrag == "opset":
            self.pt2List[0].get_data()
            font = pygame.font.SysFont(pygameEnFont, 50)
            fontSur = font.render(self.getTitle(), False, (255, 255, 255))
            tempW, tempH = fontSur.get_size()
            self.tempList.append(fontSur)
            self.tempList.append(((self.winSize[0] - tempW) * 0.5, self.winSize[1] * 0.2 - tempH * 0.5))
            self.tempList.append(NextCircle((self.winSize[0] / 2, self.winSize[1] / 2), (255, 255, 255), 150, "Game Start", 60, 5))
            self.tempList[2].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.rectList.append(pygame.draw.circle(screen, (255, 100, 100), (self.pt2List[0].currentData[0][2] * self.winSize[0], self.pt2List[0].currentData[0][3] * self.winSize[1]), 5))
            self.rectList.append(screen.blit(self.tempList[0], self.tempList[1]))
            self.rectList.append(self.tempList[2].draw(screen))
            self.gameFrag = "opening"
        elif self.gameFrag == "opening":
            self.pt2List[0].get_data()
            self.tempList[2].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.rectList.append(screen.blit(self.tempList[0], self.tempList[1]))
            self.rectList.append(self.tempList[2].draw(screen))
            
            self.rectList.append(pygame.draw.circle(screen, (255, 100, 100), (self.pt2List[0].currentData[0][2] * self.winSize[0], self.pt2List[0].currentData[0][3] * self.winSize[1]), 5))
            if self.tempList[2].judge():
                self.gameFrag = "gmsset"
        elif self.gameFrag == "gmsset":
            self.tempList = []
            self.pt2List[0].get_data()
            font = pygame.font.SysFont(pygameJaFont, 25)
            fontSur = font.render("↑ゲームモードを選んでください↑", False, (255, 255, 255))
            tempW, tempH = fontSur.get_size()
            self.tempList.append(fontSur)
            self.tempList.append(((self.winSize[0] - tempW) * 0.5, self.winSize[1] * 0.8 - tempH * 0.5))
            self.tempList.append(NextCircle((self.winSize[0] * 0.25, self.winSize[1] * 0.3), (255, 255, 0), 100, "Hockey Game", 50, 5))
            self.tempList.append(NextCircle((self.winSize[0] * 0.75, self.winSize[1] * 0.3), (0, 0, 255), 100, "Battle Game", 50, 5))
            self.tempList[2].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.tempList[3].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.rectList.append(screen.blit(self.tempList[0], self.tempList[1]))
            self.rectList.append(self.tempList[2].draw(screen))
            self.rectList.append(self.tempList[3].draw(screen))
            self.rectList.append(pygame.draw.circle(screen, (255, 100, 100), (self.pt2List[0].currentData[0][2] * self.winSize[0], self.pt2List[0].currentData[0][3] * self.winSize[1]), 5))
            self.gameFrag = "gamemodeselect"
        elif self.gameFrag == "gamemodeselect":
            self.pt2List[0].get_data()
            self.tempList[2].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.tempList[3].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.rectList.append(screen.blit(self.tempList[0], self.tempList[1]))
            self.rectList.append(self.tempList[2].draw(screen))
            self.rectList.append(self.tempList[3].draw(screen))
            self.rectList.append(pygame.draw.circle(screen, (255, 100, 100), (self.pt2List[0].currentData[0][2] * self.winSize[0], self.pt2List[0].currentData[0][3] * self.winSize[1]), 5))
            if self.tempList[2].judge():
                self.gameFrag = "hockeygame"
                self.tempList = [0]
                self.tempList.append(("PLAYER GOAL!", [255, 255, 0]))
                self.tempList.append(("ENEMY GOAL", [50, 50, 255]))
                self.stage = HockeyStage((300, 500), self.winSize, 50, 9)
                self.stageBall = StageBall(self.stage, (255, 255, 255), self.stage.stagePos.center, 10, (0, 0))
                self.player = PlayerChara(self.pt2List[0], self.pt2List[1], self.stage, self.stageBall)
                self.enemy = PlayerCharaMirror(self.stage, self.stageBall)
                self.stage.setCharacter(self.player, self.enemy)
                self.stage.addBall(self.stageBall)
                self.tempList.append(pygame.Rect(self.stage.stagePos.left, self.stage.stagePos.centery - 25, self.stage.stagePos.width, 50))
            elif self.tempList[3].judge():
                self.gameFrag = "battlegame"
                self.tempList = [0]
                self.stage = Stage((300, 600))
                self.stageBall = StageBall(self.stage, (255, 255, 255), self.stage.stagePos.center, 10, (0, 10))
                self.player = PlayerChara(self.pt2List[0], self.pt2List[1], self.stage, self.stageBall)
                self.enemy = EnemyChara(pygame.Rect(275, 75, 50, 50), self.stage, 10000)
                self.stage.setCharacter(self.player, self.enemy)
        elif self.gameFrag == "battlegame":
            self.stage.update()
            self.stageBall.update(counter)
            self.player.update(counter, self.enemy)
            self.enemy.update(counter, self.stageBall)
            self.rectList += self.stage.draw(screen)
            self.rectList += self.stageBall.draw(screen)
            self.rectList += self.player.draw(screen)
            self.rectList += self.enemy.draw(screen)

            if self.tempList[0] % 10 == 0:
                self.enemy.generateBall((50 * math.sin(math.radians(self.tempList[0])), 50 * math.cos(math.radians(self.tempList[0]))))
            self.tempList[0] = self.tempList[0] + 1 if self.tempList[0] < 60 else -60

            if self.player.loseFrag:
                self.gameFrag = "playerlose"
            elif self.enemy.loseFrag:
                self.gameFrag = "playerwin"
        elif self.gameFrag == "hockeygame":
            self.stage.update()
            self.stageBall.update(counter)
            self.player.update(counter, self.enemy)
            self.enemy.update(counter)
            #self.enemy.update(counter, [math.sin(self.tempList[0]), math.sin(self.tempList[0])], [math.cos(self.tempList[0]), math.cos(self.tempList[0])])
            self.rectList += self.stage.draw(screen)
            self.rectList += self.stageBall.draw(screen)
            self.rectList += self.player.draw(screen)
            self.rectList += self.enemy.draw(screen)

            self.tempList[0] += 0.1
            if self.stage.getGoalFrag() != 0:
                self.gameFrag = "hockeygamegoal"
                self.tempList[0] = 0
        elif self.gameFrag == "hockeygamegoal":
            self.stage.update()
            self.stageBall.update(counter)
            self.rectList += self.stage.draw(screen)
            self.rectList += self.stageBall.draw(screen)
            self.rectList.append(pygame.draw.rect(screen, (0, 0, 0), self.tempList[3]))
            tempGoal = self.tempList[self.stage.getGoalFrag()]
            tempColor = [i * self.tempList[0] for i in tempGoal[1]]
            font = pygame.font.SysFont(pygameEnFont, 25)
            fontSur = font.render(tempGoal[0], False, tempColor)
            tempW, tempH = fontSur.get_size()
            self.rectList.append(screen.blit(fontSur, (self.tempList[3].centerx - tempW / 2, self.tempList[3].centery - tempH / 2)))
            self.tempList[0] += 0.01
            if self.tempList[0] >= 1:
                self.gameFrag = "hockeygame"
                self.stage.init()
                self.stageBall = StageBall(self.stage, (255, 255, 255), self.stage.stagePos.center, 10, (0, 0))
                self.player.updateStageBall(self.stageBall)
                self.enemy.updateStageBall(self.stageBall)
                if self.stage.enemyPoint == self.stage.maxPoint:
                    self.gameFrag = "result"
                    self.tempList = [0]
                    font = pygame.font.SysFont(pygameEnFont, 50)
                    self.tempList.append(font.render("YOU LOSE", False, (50, 50, 255)))
                    self.clearRectList.append(screen.fill((0, 0, 0)))
                elif self.stage.playerPoint == self.stage.maxPoint:
                    self.gameFrag = "result"
                    self.tempList = [0]
                    font = pygame.font.SysFont(pygameEnFont, 50)
                    self.tempList.append(font.render("YOU WIN!", False, (255, 255, 0)))
                    self.clearRectList.append(screen.fill((0, 0, 0)))
        elif self.gameFrag == "result":
            tempW, tempH = self.tempList[1].get_size()
            self.rectList.append(screen.blit(self.tempList[1], ((self.winSize[0] - tempW) / 2, (self.winSize[1] - tempH) / 2)))
            self.tempList[0] += 0.01
            if self.tempList[0] >= 1:
                self.gameFrag = "ending"
                self.tempList = []
                font = pygame.font.SysFont(pygameJaFont, 20)
                self.tempList.append(font.render("次の動作を選択してください", False, (255, 255, 255)))
                self.tempList.append(NextCircle((self.winSize[0] * 0.3, self.winSize[1] * 0.7), (255, 255, 0), 100, "GameMode Select"))
                self.tempList.append(NextCircle((self.winSize[0] * 0.7, self.winSize[1] * 0.7), (50, 100, 255), 100, "Exit"))
        elif self.gameFrag == "ending":
            self.pt2List[0].get_data()
            self.tempList[1].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            self.tempList[2].update(self.pt2List[0].currentData[0][2], self.pt2List[0].currentData[0][3], self.winSize)
            tempW, tempH = self.tempList[0].get_size()
            self.rectList.append(screen.blit(self.tempList[0], ((self.winSize[0] - tempW) / 2, self.winSize[1] * 0.3 - tempH / 2)))
            self.rectList.append(self.tempList[1].draw(screen))
            self.rectList.append(self.tempList[2].draw(screen))
            self.rectList.append(pygame.draw.circle(screen, (255, 100, 100), (self.pt2List[0].currentData[0][2] * self.winSize[0], self.pt2List[0].currentData[0][3] * self.winSize[1]), 5))
            if self.tempList[1].judge():
                self.gameFrag = "gmsset"
            elif self.tempList[2].judge():
                self.gameFrag = "exit"
        elif self.gameFrag == "exit":
            termEvent = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
            pygame.event.post(termEvent)

    def getTitle(self):
        return "HockeyBattle"

    def end(self, width, height):
        pygame.display.set_mode((width, height))

    def requestPt2Num(self):
        return 1


class DebugMouse:
    def __init__(self, winSize):
        self.beforeData = [[0 for _i in range(7)]]
        self.currentData = [[0 for _i in range(7)]]
        self.winSize = winSize

    def get_data(self):
        self.beforeData = self.currentData
        self.currentData = []
        tempList = [0 for _i in range(7)]
        x, y = pygame.mouse.get_pos()
        tempList[0] = x
        tempList[1] = y
        tempList[2] = x / self.winSize[0]
        tempList[3] = y / self.winSize[1]
        tempList[4] = 100
        self.currentData.append(tempList)

def main():
    pygame.init()
    pygame.display.set_mode((600, 600), 0, 0)
    screen = pygame.display.get_surface()
    game = HockeyBattle()
    game.init("debug")
    loopFrag = True
    while(loopFrag):
        game.draw(screen)
        game.update(None, None, 0)
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    loopFrag = False
                
if __name__ == '__main__':
    main()