import PlayerTracking as PT
from PlayerTracking import pt2
import pygame
import math

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

    def init(self):
        self.pt2List = [pt2(), pt2()]
        self.winSize = (600, 600)
        self.gameFrag = 0
        self.clock = pygame.time.Clock()
        self.rectList = []
        self.clearRectList = []
        self.tempList = [0, 0, 0]
        self.counterRate = 1000

        self.stage = Stage((300, 600))
        self.stageBall = StageBall(self.stage, (255, 255, 255), self.stage.stagePos.center, 10, (0, 10))
        self.player = PlayerChara(self.pt2List[0], self.pt2List[1], self.stage, self.stageBall)
        self.enemy = EnemyChara(pygame.Rect(275, 75, 50, 50), self.stage, 10000)
        pygame.display.init()
        pygame.display.set_mode(self.winSize, pygame.RESIZABLE)
        self.pt2List[0].set_color()
        self.pt2List[1].set_color()
        PT.set_capture_read()
        self.clock.tick()
        self.stage.setCharacter(self.player, self.enemy)

    def update(self, events, deltaTime):
        if len(self.rectList) > 0:
            pygame.display.update(self.clearRectList)
            pygame.display.update(self.rectList)
        else:
            pygame.display.update()
        if self.gameFrag < 0:
            pass
        else:
            PT.set_capture_read()
        self.clearRectList = self.rectList
        self.rectList = []

    def draw(self, screen):
        for i in range(len(self.clearRectList)):
            screen.fill((0, 0, 0), rect=self.clearRectList[i])
        
        counter = self.clock.tick() / self.counterRate
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

    def getTitle(self):
        return "HockeyBattle"

    def end(self, width, height):
        pygame.display.set_mode((width, height))


#操作キャラオブジェクト全体(全てのパーツを委譲)
class Character:
    def __init__(self, initPosition:pygame.Rect):
        self.charaBody = CharaBody(initPosition)
        self.charaStick = CharaStick(initPosition)
        self.charaShield = CharaShield(initPosition)
        self.position = initPosition
        self.rectList = None
        self.speed = [0, 0]
    
    def update(self, newPos, stickTranslate, counter):
        self.speed = [(newPos[0] - self.position.center[0]) / counter, (newPos[1] - self.position.center[1]) / counter]
        self.position = pygame.Rect(newPos[0] - self.position.width / 2, newPos[1] - self.position.height / 2, self.position.width, self.position.height)
        self.charaBody.update(self.position)
        self.charaStick.update(self.position, stickTranslate)
        self.charaShield.update(self.position)

    def draw(self, screen):
        self.rectList = []
        self.rectList += self.charaBody.draw(screen)
        self.rectList += self.charaStick.draw(screen)
        self.rectList += self.charaShield.draw(screen)
        return self.rectList

#操作キャラオブジェクト身体
class CharaBody:
    def __init__(self, initCharaPosit:pygame.Rect):
        self.rectList = None
        self.rectRect = pygame.Rect(initCharaPosit.left, initCharaPosit.top + initCharaPosit.height / 2, initCharaPosit.width, initCharaPosit.height / 2)
        self.circlePosition = list(initCharaPosit.center)
        self.circleRadius = initCharaPosit.height / 4
        pass

    def update(self, charaPos:pygame.Rect):
        self.rectRect = pygame.Rect(charaPos.left, charaPos.top + charaPos.height / 2, charaPos.width, charaPos.height / 2)
        self.circlePosition = list(charaPos.center)

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.rect(screen, (255, 255, 255), self.rectRect, 3))
        self.rectList.append(pygame.draw.circle(screen, (200, 200, 200), self.circlePosition, self.circleRadius))
        return self.rectList

#操作キャラオブジェクト棒
class CharaStick:
    def __init__(self, initCharaPosit:pygame.Rect, size = 70):
        self.rectList = None
        self.stickSize = size
        self.stickRadian = 0
        self.stickRadianList = [0 for i in range(5)]
        self.linePosition = [[initCharaPosit.left + initCharaPosit.width * 0.8, initCharaPosit.top + initCharaPosit.height * 0.2], [initCharaPosit.left + initCharaPosit.width * 0.8 - self.stickSize * math.sin(self.stickRadian), initCharaPosit.top + initCharaPosit.height * 0.2 - self.stickSize * math.cos(self.stickRadian)]]
        self.collisionRect = pygame.Rect(self.linePosition[0][0] - size * math.sin(math.pi / 3), self.linePosition[1][1], 2 * size * math.sin(math.pi / 3), size)
        self.ballMerging = False
        self.collisionjudgeInfo = [0, 0]
        self.collisionTimeCounter = 0

    def update(self, charaPos:pygame.Rect, stickTranslate):
        self.stickRadianList.pop(0)
        self.stickRadian = self.stickRadianList[-1] + stickTranslate * 5
        if stickTranslate < 0:
            if self.stickRadian <= -1 * math.pi / 3:
                self.stickRadian = -1 * math.pi / 3
        else:
            if self.stickRadian >= math.pi / 3:
                self.stickRadian = math.pi / 3
        self.stickRadianList.append(self.stickRadian)
        tempX = charaPos.left + charaPos.width * 0.8
        tempY = charaPos.top + charaPos.height * 0.2
        self.linePosition = [[tempX, tempY], [tempX - self.stickSize * math.sin(self.stickRadian), tempY - self.stickSize * math.cos(self.stickRadian)]]
        self.collisionRect = pygame.Rect(self.linePosition[0][0] - self.stickSize * math.sin(math.pi / 3), self.linePosition[0][1] - self.stickSize, self.collisionRect.width, self.stickSize)

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.line(screen, (255, 0, 0), self.linePosition[0], self.linePosition[1], 3))
        self.rectList.append(pygame.draw.rect(screen, (255, 0, 0), self.collisionRect, 1))
        return self.rectList

#操作キャラオブジェクト盾
class CharaShield:
    def __init__(self, initCharaPosit:pygame.Rect):
        self.rectList = None
        self.linePosition = [[initCharaPosit.left, initCharaPosit.top], [initCharaPosit.left + initCharaPosit.width * 0.6, initCharaPosit.top]]

    def update(self, charaPos):
        self.linePosition = [[charaPos.left, charaPos.top], [charaPos.left + charaPos.width * 0.6, charaPos.top]]

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.line(screen, (0, 0, 255), self.linePosition[0], self.linePosition[1], 3))
        return self.rectList

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
        font = pygame.font.SysFont("hgｺﾞｼｯｸe", 50)
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
        return self.progPosit, self.speed, self.radius

    def setClockTick(self, counter):
        self.counter = counter

    def getProgPosit(self):
        progPosit = list(self.position)
        progPosit[0] += self.speed[0] * self.counter
        progPosit[1] += self.speed[1] * self.counter
        self.progPosit = progPosit

    def update(self, counter):
        tempPos, tempSpeed, tempRadius = self.getCalcData()
        self.counter = counter
        self.getProgPosit()
        temp1 = self.stage.stagePos.left + tempRadius
        temp2 = self.stage.stagePos.right - tempRadius
        #以下壁との衝突処理
        if self.progPosit[0] <= temp1:
            self.progPosit[0] = temp1 * 2 - self.progPosit[0]
            if tempSpeed[0] > 50:
                tempSpeed[0] = -0.8 * tempSpeed[0]
            else:
                tempSpeed[0] = -1 * tempSpeed[0]
        elif self.progPosit[0] >= temp2:
            self.progPosit[0] = temp2 * 2 - self.progPosit[0]
            if tempSpeed[0] > 50:
                tempSpeed[0] = -0.8 * tempSpeed[0]
            else:
                tempSpeed[0] = -1 * tempSpeed[0]
        temp1 = self.stage.stagePos.top + tempRadius
        temp2 = self.stage.stagePos.bottom - tempRadius
        if self.progPosit[1] <= temp1:
            self.progPosit[1] = temp1 * 2 - self.progPosit[1]
            if tempSpeed[1] > 50:
                tempSpeed[1] = -0.8 * tempSpeed[1]
            else:
                tempSpeed[1] = -1 * tempSpeed[1]
        elif self.progPosit[1] >= temp2:
            self.progPosit[1] = temp2 * 2 - self.progPosit[1]
            if tempSpeed[1] > 50:
                tempSpeed[1] = -0.8 * tempSpeed[1]
            else:
                tempSpeed[1] = -1 * tempSpeed[1]
        self.position = list(self.progPosit)
        self.speed = list(tempSpeed)

    def draw(self, screen):
        rectList = [pygame.draw.circle(screen, self.color, self.position, self.radius)]
        return rectList

#操作プレイヤー(インスタンス化必要)
class PlayerChara:
    def __init__(self, pt1:pt2, pt2:pt2, stage:Stage, stageBall:StageBall, hitPoint = 100):
        self.character = Character(pygame.Rect(275, 325, 50, 50))
        self.pt1 = pt1
        self.pt2 = pt2
        self.stage = stage
        self.stageArea = pygame.Rect(stage.stagePos.left + self.character.position.width / 2, stage.stagePos.top + self.character.position.height / 2, stage.stageSize[0] - self.character.position.width, stage.stageSize[1] - self.character.position.height)
        self.stageBall = stageBall
        self.rectList = None
        self.counter = None
        self.maxHitPoint = hitPoint
        self.currentHitPoint = hitPoint

    def update(self, counter, enemyChara):
        self.counter = counter
        #ptの取得
        self.pt1.get_data()
        self.pt2.get_data()

        #プレイヤーと敵攻撃との衝突処理
        if self.rectList == None or enemyChara.enemyBallRectList == None:
            pass
        else:
            tempListIndex = self.rectList[1].collidelistall(enemyChara.enemyBallRectList)
            for i in tempListIndex[::-1]:
                enemyChara.ballList.pop(i)
                self.currentHitPoint -= 1

        #プレイヤーの棒の処理
        progStick = self.pt2.beforeData[0][2] - self.pt2.currentData[0][2]
        if self.pt2.currentData[0][4] <= 10 and progStick < 0.02:
            progStick = 0

        #プレイヤーの移動処理
        progPosit = [(self.pt1.currentData[0][2] * self.stage.winSize[0] - self.character.position.center[0]) * 0.05 + self.character.position.center[0], (self.pt1.currentData[0][3] * self.stage.winSize[1] - self.character.position.center[1]) * 0.05 + self.character.position.center[1]]
        if progPosit[0] <= self.stageArea.left:
            progPosit[0] = self.stageArea.left
        elif progPosit[0] >= self.stageArea.right:
            progPosit[0] = self.stageArea.right
        if progPosit[1] <= self.stageArea.top:
            progPosit[1] = self.stageArea.top
        elif progPosit[1] >= self.stageArea.bottom:
            progPosit[1] = self.stageArea.bottom
        self.character.update(progPosit, progStick, counter)

        #ボールの移動処理(壁&棒当たり判定含む)
        progPosit, tempSpeed, tempRadius = self.stageBall.getCalcData()
        #以下棒との衝突処理
        tempRectBall = pygame.Rect(progPosit[0] - tempRadius, progPosit[1] - tempRadius, tempRadius * 2, tempRadius * 2)
        if self.character.charaStick.collisionTimeCounter > 0:
            self.character.charaStick.collisionTimeCounter -= self.counter
        elif tempRectBall.colliderect(self.character.charaStick.collisionRect):

            #棒とボールが接触しているかの判定を行い、接触していた場合に、棒の棒とプレイヤーの動きを合算した移動ベクトルを計算し、
            #それをボールのspeedに持たせ、updateを行う

            #棒の根本からボールの中心までのベクトル(以下、ボールの位置ベクトル)の長さ
            circleVectSize = math.sqrt((self.character.charaStick.linePosition[0][0] - progPosit[0])**2 + (self.character.charaStick.linePosition[0][1] - progPosit[1])**2)
            #棒とボールの位置ベクトルとの間のラジアン
            tempRadian = self.character.charaStick.stickRadian - math.asin((self.character.charaStick.linePosition[0][0] - progPosit[0]) / circleVectSize)
            #上のラジアンを用いて、ボールの中心から棒への垂線とボールの半径を比べる
            if abs(circleVectSize * math.sin(tempRadian)) < tempRadius:
                print("通常")
                tempSpeed = self.collisionCalc(circleVectSize, tempRadian, tempSpeed)
                self.stageBall.speed = tempSpeed
            else:
                if self.character.charaStick.ballMerging:
                    if self.character.charaStick.collisionjudgeInfo[0] * tempRadian < 0:
                        #当たった時と同じ処理
                        print("貫通")
                        tempSpeed = self.collisionCalc(circleVectSize, tempRadian, tempSpeed)
                        self.stageBall.speed = tempSpeed
                else:
                    self.character.charaStick.ballMerging = True
                self.character.charaStick.collisionjudgeInfo[0] = tempRadian
                #self.character.charaStick.collisionjudgeInfo[0] = math.asin((self.character.charaStick.linePosition[0][0] - progPosit[0]) / circleVectSize)
        else:
            self.character.charaStick.ballMerging = False
            self.character.charaStick.collisionjudgeInfo = [0, 0]
        
    def draw(self, screen):
        self.rectList = []
        self.rectList += self.character.draw(screen)
        return self.rectList

    def collisionCalc(self, circleVectSize, tempRadian, tempSpeed):
        stickSpeedRate = 3
        self.character.charaStick.collisionTimeCounter = 0.5
        #棒が実際に動いたradian
        stickRealMove = (self.character.charaStick.stickRadianList[-1] - self.character.charaStick.stickRadianList[0]) / (self.counter * len(self.character.charaStick.stickRadianList))
        if abs(stickRealMove) < 0.05:
            stickRealMove = 0
        print(stickRealMove, self.character.speed, tempRadian)

        #棒が左右どちらにあるか
        if self.character.charaStick.stickRadian >= 0:
            #棒は左側

            #座標系回転に使用するラジアン
            coorRotateRadian = math.radians(90) - self.character.charaStick.stickRadian
            #ボールが棒に対して左右どちらから当たっているのか
            ballMoveDirect = True if self.character.charaStick.collisionjudgeInfo[0] > 0 else False
            if self.character.charaStick.collisionjudgeInfo[0] == 0:
                ballMoveDirect = True if tempRadian >= 0 else False

            if ballMoveDirect:
                #ボールは棒より右から来た
                if stickRealMove < 0:
                    #棒は右に動いている
                    progSpeed = [self.character.speed[0] * math.cos(coorRotateRadian) + self.character.speed[1] * math.sin(coorRotateRadian), self.character.speed[1] * math.cos(coorRotateRadian) - self.character.speed[0] * math.sin(coorRotateRadian)]
                    progSpeed[1] -= circleVectSize * math.cos(tempRadian)
                    progSpeed[0] *= stickSpeedRate
                    progSpeed[1] *= stickSpeedRate
                    tempSpeed[0] = progSpeed[0] * math.cos(coorRotateRadian) - progSpeed[1] * math.sin(coorRotateRadian)
                    tempSpeed[1] = progSpeed[0] * math.sin(coorRotateRadian) + progSpeed[1] * math.cos(coorRotateRadian)
                    pass
                else:
                    pass
                pass
            else:
                #ボールは棒より左から来た
                if stickRealMove > 0:
                    #棒は左に動いている
                    progSpeed = [self.character.speed[0] * math.cos(coorRotateRadian) + self.character.speed[1] * math.sin(coorRotateRadian), self.character.speed[1] * math.cos(coorRotateRadian) - self.character.speed[0] * math.sin(coorRotateRadian)]
                    progSpeed[1] -= circleVectSize * math.cos(tempRadian)
                    progSpeed[0] *= stickSpeedRate
                    progSpeed[1] *= stickSpeedRate
                    tempSpeed[0] = progSpeed[0] * math.cos(coorRotateRadian) - progSpeed[1] * math.sin(coorRotateRadian)
                    tempSpeed[1] = progSpeed[0] * math.sin(coorRotateRadian) + progSpeed[1] * math.cos(coorRotateRadian)
                    pass
                else:
                    pass
                pass
        else:
            #棒は右側

            #座標系回転に使用するラジアン
            coorRotateRadian = math.radians(-90) - self.character.charaStick.stickRadian
            #ボールが棒に対して左右どちらから当たっているのか
            ballMoveDirect = True if self.character.charaStick.collisionjudgeInfo[0] >= 0 else False

            if ballMoveDirect:
                #ボールは棒より右から来た
                if stickRealMove < 0:
                    #棒は右に動いている
                    progSpeed = [self.character.speed[0] * math.cos(coorRotateRadian) + self.character.speed[1] * math.sin(coorRotateRadian), self.character.speed[1] * math.cos(coorRotateRadian) - self.character.speed[0] * math.sin(coorRotateRadian)]
                    progSpeed[1] -= circleVectSize * math.cos(tempRadian)
                    progSpeed[0] *= stickSpeedRate
                    progSpeed[1] *= stickSpeedRate
                    tempSpeed[0] = progSpeed[0] * math.cos(coorRotateRadian) - progSpeed[1] * math.sin(coorRotateRadian)
                    tempSpeed[1] = progSpeed[0] * math.sin(coorRotateRadian) + progSpeed[1] * math.cos(coorRotateRadian)
                    pass
                else:
                    pass
            else:
                #ボールは棒より左から来た
                if stickRealMove > 0:
                    #棒は左に動いている
                    progSpeed = [self.character.speed[0] * math.cos(coorRotateRadian) + self.character.speed[1] * math.sin(coorRotateRadian), self.character.speed[1] * math.cos(coorRotateRadian) - self.character.speed[0] * math.sin(coorRotateRadian)]
                    progSpeed[1] -= circleVectSize * math.cos(tempRadian)
                    progSpeed[0] *= stickSpeedRate
                    progSpeed[1] *= stickSpeedRate
                    tempSpeed[0] = progSpeed[0] * math.cos(coorRotateRadian) - progSpeed[1] * math.sin(coorRotateRadian)
                    tempSpeed[1] = progSpeed[0] * math.sin(coorRotateRadian) + progSpeed[1] * math.cos(coorRotateRadian)
                    pass
                else:
                    pass
            pass
        self.character.charaStick.collisionjudgeInfo = [0, 0]
        return tempSpeed

#操作エネミー(インスタンス化必要)
class EnemyChara:
    def __init__(self, initPosition:pygame.Rect, stage:Stage, hitPoint = 100):
        self.position = initPosition
        self.stage = stage
        self.rectList = None
        self.ballList = []
        self.counter = None
        self.maxHitPoint = hitPoint
        self.currentHitPoint = hitPoint
        self.inBallFrag = False
        self.enemyBallRectList = None

    def generateBall(self, initSpeed, color = (255, 255, 0), radius = 10):
        self.ballList.append(EnemyBall(self.stage, color, self.position.center, radius, initSpeed))

    def update(self, counter, stageBall:StageBall):
        self.counter = counter
        clearList = []
        for i in range(len(self.ballList)):
            if self.ballList[i].update(self.counter):
                clearList.append(i)
        for i in clearList[::-1]:
            self.ballList.pop(i)
        #以下enemy自身の動き

        #以下enemyとstageBallの衝突
        temp1 = abs(stageBall.position[0] - self.position.center[0])
        temp2 = abs(stageBall.position[1] - self.position.center[1])
        if temp1 <= self.position.width / 2 + stageBall.radius and temp2 <= self.position.height / 2 + stageBall.radius:
            if not(self.inBallFrag):
                self.currentHitPoint -= math.sqrt(stageBall.speed[0]**2 + stageBall.speed[1]**2)
                self.inBallFrag = True
        else:
            self.inBallFrag = False

    def draw(self, screen):
        self.rectList = []
        self.enemyBallRectList = []
        for i in self.ballList:
            self.enemyBallRectList += i.draw(screen)
        self.rectList += self.enemyBallRectList
        self.rectList.append(pygame.draw.rect(screen, (100, 100, 100), self.position))
        return self.rectList

class EnemyBall:
    def __init__(self, stage:Stage, color, initPosition:list or tuple, radius, initSpeed:list or tuple):
        self.stage = stage
        self.position = initPosition
        self.speed = initSpeed
        self.color = color
        self.radius = radius
        self.rectList = None
        self.counter = None

    def getProgPosit(self):
        progPosit = list(self.position)
        progPosit[0] += self.speed[0] * self.counter
        progPosit[1] += self.speed[1] * self.counter
        self.progPosit = progPosit

    def update(self, counter):
        self.counter = counter
        self.getProgPosit()
        tempSpeed = list(self.speed)
        temp1 = self.stage.stagePos.left + self.radius
        temp2 = self.stage.stagePos.right - self.radius
        #以下壁との衝突処理
        if self.progPosit[0] <= temp1:
            self.progPosit[0] = temp1 * 2 - self.progPosit[0]
            tempSpeed[0] = -1 * tempSpeed[0]
        elif self.progPosit[0] >= temp2:
            self.progPosit[0] = temp2 * 2 - self.progPosit[0]
            tempSpeed[0] = -1 * tempSpeed[0]
        temp1 = self.stage.stagePos.top + self.radius
        temp2 = self.stage.stagePos.bottom - self.radius
        if self.progPosit[1] <= temp1:
            self.progPosit[1] = temp1 * 2 - self.progPosit[1]
            tempSpeed[1] = -1 * tempSpeed[1]
        elif self.progPosit[1] >= temp2:
            return True
        self.position = list(self.progPosit)
        self.speed = tempSpeed
        return False

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.circle(screen, self.color, self.position, self.radius))
        return self.rectList

def main():
    pygame.init()
    pygame.display.set_mode((600, 600), 0, 0)
    screen = pygame.display.get_surface()
    game = HockeyBattle()
    game.init()
    loopFrag = True
    while(loopFrag):
        game.draw(screen)
        game.update(None, 0)
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    loopFrag = False
                
if __name__ == '__main__':
    main()