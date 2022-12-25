import pygame
import math
import copy
from HB_Stage import *
from HB_SlidePad import SlidePad

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
        self.loseFrag = False

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
                if self.currentHitPoint <= 0:
                    self.loseFrag = True
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

#以下、ホッケーで使用するプレイヤーのミラー
#うまく継承ができなかったため、ミラー用の処理を新しく作る

#操作キャラオブジェクト全体(全てのパーツを委譲)
class CharacterMirror:
    def __init__(self, initPosition:pygame.Rect):
        self.charaBody = CharaBodyMirror(initPosition)
        self.charaStick = CharaStickMirror(initPosition)
        self.charaShield = CharaShieldMirror(initPosition)
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
class CharaBodyMirror:
    def __init__(self, initCharaPosit:pygame.Rect):
        self.rectList = None
        self.rectRect = pygame.Rect(initCharaPosit.left, initCharaPosit.top, initCharaPosit.width, initCharaPosit.height / 2)
        self.circlePosition = list(initCharaPosit.center)
        self.circleRadius = initCharaPosit.height / 4
        pass

    def update(self, charaPos:pygame.Rect):
        self.rectRect = pygame.Rect(charaPos.left, charaPos.top, charaPos.width, charaPos.height / 2)
        self.circlePosition = list(charaPos.center)

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.rect(screen, (255, 255, 255), self.rectRect, 3))
        self.rectList.append(pygame.draw.circle(screen, (50, 50, 255), self.circlePosition, self.circleRadius))
        return self.rectList

#操作キャラオブジェクト棒
class CharaStickMirror:
    def __init__(self, initCharaPosit:pygame.Rect, size = 70):
        self.rectList = None
        self.stickSize = size
        self.stickRadian = 0
        self.stickRadianList = [0 for i in range(5)]
        self.linePosition = [[initCharaPosit.left + initCharaPosit.width * 0.2, initCharaPosit.top + initCharaPosit.height * 0.8], [initCharaPosit.left + initCharaPosit.width * 0.2 + self.stickSize * math.sin(self.stickRadian), initCharaPosit.top + initCharaPosit.height * 0.8 + self.stickSize * math.cos(self.stickRadian)]]
        self.collisionRect = pygame.Rect(self.linePosition[0][0] - size * math.sin(math.pi / 3), self.linePosition[0][1], 2 * size * math.sin(math.pi / 3), size)
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
        tempX = charaPos.left + charaPos.width * 0.2
        tempY = charaPos.top + charaPos.height * 0.8
        self.linePosition = [[tempX, tempY], [tempX + self.stickSize * math.sin(self.stickRadian), tempY + self.stickSize * math.cos(self.stickRadian)]]
        self.collisionRect = pygame.Rect(self.linePosition[0][0] - self.stickSize * math.sin(math.pi / 3), self.linePosition[0][1], self.collisionRect.width, self.stickSize)

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.line(screen, (255, 0, 0), self.linePosition[0], self.linePosition[1], 3))
        self.rectList.append(pygame.draw.rect(screen, (255, 0, 0), self.collisionRect, 1))
        return self.rectList

#操作キャラオブジェクト盾
class CharaShieldMirror:
    def __init__(self, initCharaPosit:pygame.Rect):
        self.rectList = None
        self.linePosition = [[initCharaPosit.left, initCharaPosit.bottom], [initCharaPosit.right, initCharaPosit.bottom]]
        self.beforeLinePosition = self.linePosition
        self.collisionTimeCounter = 0

    def getCollisionTimeCounter(self, counter):
        self.collisionTimeCounter -= counter
        if self.collisionTimeCounter <= 0:
            self.collisionTimeCounter = 0
        return self.collisionTimeCounter

    def setCollisionTimeCounter(self, counter = 0.5):
        self.collisionTimeCounter = counter
        
    def getPosition(self, isAll = False):
        if isAll:
            return self.linePosition, self.beforeLinePosition
        return self.linePosition

    def update(self, charaPos):
        self.beforeLinePosition = self.linePosition
        self.linePosition = [[charaPos.left, charaPos.bottom], [charaPos.right, charaPos.bottom]]

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.line(screen, (255, 255, 0), self.linePosition[0], self.linePosition[1], 3))
        return self.rectList

class PlayerCharaMirror(EnemyChara):
    def __init__(self, stage:Stage, stageBall:StageBall, hitPoint = 100) -> None:
        self.character = CharacterMirror(pygame.Rect(275, 125, 50, 50))
        super().__init__(self.character.position, Stage, hitPoint)
        self.stage = stage
        self.stageArea = pygame.Rect(stage.stagePos.left + self.character.position.width / 2, stage.stagePos.top + self.character.position.height / 2, stage.stageSize[0] - self.character.position.width, stage.stageSize[1] - self.character.position.height)
        self.stageBall = stageBall
        self.rectList = None
        self.counter = None
        self.maxHitPoint = hitPoint
        self.currentHitPoint = hitPoint
        self.loseFrag = False
        self.slidePad = SlidePad((0, 0), pygame.Rect(self.stageArea.left, self.stageArea.top, self.stageArea.width, self.stageArea.bottom * 0.6))
        self.enemyController = EnemyController(self.stage.winSize)

    def update(self, counter):
        self.counter = counter

        #プレイヤーの棒の処理
        progStick = 0

        #プレイヤーの移動処理
        self.enemyController.set_data(self.character.position, self.stageBall.position[0], self.stageArea.top)
        progPosit = self.slidePad.update(self.character.position, self.enemyController)
        #progPosit = [(positSpeedUpdate[0] * self.stage.winSize[0] - self.character.position.center[0]) * 0.05 + self.character.position.center[0], (positSpeedUpdate[1] * self.stage.winSize[1] - self.character.position.center[1]) * 0.05 + self.character.position.center[1]]
        self.character.update(progPosit, progStick, counter)

        #ボールの移動処理(壁&棒当たり判定含む)
        progPosit, tempSpeed, tempRadius, currentPosit = self.stageBall.getCalcData()
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
            
        #以下シールドとボールの衝突処理(端点内側及び正面からの縦断のみ対応)
        if self.character.charaShield.getCollisionTimeCounter(counter) == 0:
            shieldPosit, beforeShieldPosit = self.character.charaShield.getPosition(True)
            shieldPosit = copy.deepcopy(shieldPosit)
            beforeShieldPosit = copy.deepcopy(beforeShieldPosit)
            shieldPosit[0][0] -= tempRadius
            shieldPosit[0][1] += tempRadius
            shieldPosit[1][0] += tempRadius
            shieldPosit[1][1] += tempRadius
            beforeShieldPosit[0][0] -= tempRadius
            #beforeShieldPosit[0][1] += tempRadius
            beforeShieldPosit[1][0] += tempRadius
            #beforeShieldPosit[1][1] += tempRadius
            xposJudgeShieldLeftLinear = lambda x, y:x - (beforeShieldPosit[0][0] + (y - beforeShieldPosit[0][1]) * ((shieldPosit[0][0] - beforeShieldPosit[0][0]) / (shieldPosit[0][1] - beforeShieldPosit[0][1]) if shieldPosit[0][1] - beforeShieldPosit[0][1] != 0 else 0))
            xposJudgeShieldRightLinear = lambda x, y:x - (beforeShieldPosit[1][0] + (y - beforeShieldPosit[1][1]) * ((shieldPosit[1][0] - beforeShieldPosit[1][0]) / (shieldPosit[1][1] - beforeShieldPosit[1][1]) if shieldPosit[1][1] - beforeShieldPosit[1][1] != 0 else 0))
            #yposJudgeShieldLinear = lambda x, y:y - shieldPosit[0][1]
            #yposJudgeBeforeShieldLinear = lambda x, y:y - beforeShieldPosit[0][1]
            progPositFragList = [xposJudgeShieldLeftLinear(progPosit[0], progPosit[1]), xposJudgeShieldRightLinear(progPosit[0], progPosit[1]), progPosit[1] - shieldPosit[0][1], progPosit[1] - beforeShieldPosit[0][1]]
            currentPositFragList = [xposJudgeShieldLeftLinear(currentPosit[0], currentPosit[1]), xposJudgeShieldRightLinear(currentPosit[0], currentPosit[1]), currentPosit[1] - shieldPosit[0][1], currentPosit[1] - beforeShieldPosit[0][1]]
            if currentPositFragList[0] >= 0 and currentPositFragList[1] <= 0:
                xposJudgeBallLinear = lambda x, y:x - (currentPosit[0] + (y - currentPosit[1]) * ((progPosit[0] - currentPosit[0]) / (progPosit[1] - currentPosit[1]) if progPosit[1] - currentPosit[1] != 0 else 0))
                if currentPositFragList[2] <= 0 and currentPositFragList[3] >= 0:
                    #始点が平行四辺形内
                    if progPosit[1] <= currentPosit[1]:
                        #反射
                        progPosit[1] = shieldPosit[0][1] * 2 - progPosit[1]
                        tempSpeed[1] *= -1
                    #上乗せ
                    #tempSpeed[1] += (shieldPosit[0][1] - beforeShieldPosit[0][1]) / counter
                    tempSpeed[1] += self.character.speed[1]
                    self.character.charaShield.setCollisionTimeCounter()
                elif currentPositFragList[2] >= 0 and progPositFragList[2] <= 0 and xposJudgeBallLinear(shieldPosit[0][0], shieldPosit[0][1]) <= 0 and xposJudgeBallLinear(shieldPosit[1][0], shieldPosit[1][1]) >= 0:
                    #正面からの縦断
                    progPosit[1] = shieldPosit[0][1] * 2 - progPosit[1]
                    tempSpeed[1] *= -1
                    #tempSpeed[1] += (shieldPosit[0][1] - beforeShieldPosit[0][1]) / counter
                    tempSpeed[1] += self.character.speed[1]
                    self.character.charaShield.setCollisionTimeCounter()
            elif progPositFragList[0] >= 0 and progPositFragList[1] <= 0 and progPositFragList[2] <= 0 and progPositFragList[3] >= 0:
                #終点が平行四辺形内
                if progPosit[1] <= currentPosit[1]:
                    #反射
                    progPosit[1] = shieldPosit[0][1] * 2 - progPosit[1]
                    tempSpeed[1] *= -1
                #上乗せ
                #tempSpeed[1] += (shieldPosit[0][1] - beforeShieldPosit[0][1]) / counter
                tempSpeed[1] += self.character.speed[1]
                self.character.charaShield.setCollisionTimeCounter()
            #下の無名関数はボールの軌跡ベクトルが平行四辺形を斜めにまたがった際に使う予定だったもの
            #yposJudgeBallLinear = lambda x, y:y - (progPosit[1] + (x - progPosit[0]) * ((progPosit[1] - currentPosit[1]) / (progPosit[0] - currentPosit[0]))) if progPosit[0] - currentPosit[0] != 0 else 0

    def draw(self, screen):
        self.rectList = []
        self.rectList += self.character.draw(screen)
        return self.rectList

    def updateStageBall(self, stageBall):
        self.stageBall = stageBall

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

class EnemyController:
    def __init__(self, winSize):
        self.beforeData = [[0 for _i in range(7)]]
        self.currentData = [[0 for _i in range(7)]]
        self.winSize = winSize

    def set_data(self, curentPosit:pygame.Rect, x, y):
        if x > curentPosit.right:
            x = self.winSize[0]
        elif x < curentPosit.left:
            x = 0
        else:
            x = self.winSize[0] / 2
        if y >= self.winSize[1]:
            y = self.winSize[1]
        if y <= 0:
            y = 0
        self.beforeData = self.currentData
        self.currentData = []
        tempList = [0 for _i in range(7)]
        tempList[0] = x
        tempList[1] = y
        tempList[2] = x / self.winSize[0]
        tempList[3] = y / self.winSize[1]
        tempList[4] = 100
        self.currentData.append(tempList)