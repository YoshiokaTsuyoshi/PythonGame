import pygame
import math
import copy
from PlayerTracking import pt2
from HB_Stage import *
from HB_Stage import Stage
from HB_SlidePad import SlidePad

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
        self.linePosition = [[initCharaPosit.left, initCharaPosit.top], [initCharaPosit.right, initCharaPosit.top]]
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
        self.linePosition = [[charaPos.left, charaPos.top], [charaPos.right, charaPos.top]]

    def draw(self, screen):
        self.rectList = []
        self.rectList.append(pygame.draw.line(screen, (255, 255, 0), self.linePosition[0], self.linePosition[1], 3))
        return self.rectList

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
        self.loseFrag = False
        self.slidePad = SlidePad((100, 400), pygame.Rect(self.stageArea.left, self.stageArea.bottom * 0.4, self.stageArea.width, self.stageArea.bottom * 0.6), drawFrag=True)

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
                
                temp1 = abs(enemyChara.enemyBallRectList[i].center[0] - self.character.charaBody.circlePosition[0])
                temp2 = abs(enemyChara.enemyBallRectList[i].center[1] - self.character.charaBody.circlePosition[1])
                if temp1 <= self.character.charaBody.circleRadius + enemyChara.enemyBallRectList[i].width / 4 and temp2 <= self.character.charaBody.circleRadius + enemyChara.enemyBallRectList[i].width / 4:
                    enemyChara.ballList.pop(i)
                    self.currentHitPoint -= 1
                    if self.currentHitPoint <= 0:
                        self.loseFrag = True

        #プレイヤーの棒の処理
        progStick = (self.pt2.beforeData[0][2] - self.pt2.currentData[0][2]) / 0.8
        if self.pt2.currentData[0][4] <= 10 and progStick < 0.02:
            progStick = 0

        #プレイヤーの移動処理
        progPosit = self.slidePad.update(self.character.position, self.pt2)
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
            shieldPosit[0][1] -= tempRadius
            shieldPosit[1][0] += tempRadius
            shieldPosit[1][1] -= tempRadius
            beforeShieldPosit[0][0] -= tempRadius
            #beforeShieldPosit[0][1] -= tempRadius
            beforeShieldPosit[1][0] += tempRadius
            #beforeShieldPosit[1][1] -= tempRadius
            xposJudgeShieldLeftLinear = lambda x, y:x - (beforeShieldPosit[0][0] + (y - beforeShieldPosit[0][1]) * ((shieldPosit[0][0] - beforeShieldPosit[0][0]) / (shieldPosit[0][1] - beforeShieldPosit[0][1]) if shieldPosit[0][1] - beforeShieldPosit[0][1] != 0 else 0))
            xposJudgeShieldRightLinear = lambda x, y:x - (beforeShieldPosit[1][0] + (y - beforeShieldPosit[1][1]) * ((shieldPosit[1][0] - beforeShieldPosit[1][0]) / (shieldPosit[1][1] - beforeShieldPosit[1][1]) if shieldPosit[1][1] - beforeShieldPosit[1][1] != 0 else 0))
            #yposJudgeShieldLinear = lambda x, y:y - shieldPosit[0][1]
            #yposJudgeBeforeShieldLinear = lambda x, y:y - beforeShieldPosit[0][1]
            progPositFragList = [xposJudgeShieldLeftLinear(progPosit[0], progPosit[1]), xposJudgeShieldRightLinear(progPosit[0], progPosit[1]), progPosit[1] - shieldPosit[0][1], progPosit[1] - beforeShieldPosit[0][1]]
            currentPositFragList = [xposJudgeShieldLeftLinear(currentPosit[0], currentPosit[1]), xposJudgeShieldRightLinear(currentPosit[0], currentPosit[1]), currentPosit[1] - shieldPosit[0][1], currentPosit[1] - beforeShieldPosit[0][1]]
            if currentPositFragList[0] >= 0 and currentPositFragList[1] <= 0:
                xposJudgeBallLinear = lambda x, y:x - (currentPosit[0] + (y - currentPosit[1]) * ((progPosit[0] - currentPosit[0]) / (progPosit[1] - currentPosit[1]) if progPosit[1] - currentPosit[1] != 0 else 0))
                if currentPositFragList[2] >= 0 and currentPositFragList[3] <= 0:
                    #始点が平行四辺形内
                    if progPosit[1] >= currentPosit[1]:
                        #反射
                        progPosit[1] = shieldPosit[0][1] * 2 - progPosit[1]
                        tempSpeed[1] *= -1
                    #上乗せ
                    #tempSpeed[1] += (shieldPosit[0][1] - beforeShieldPosit[0][1]) / counter
                    tempSpeed[1] += self.character.speed[1]
                    self.character.charaShield.setCollisionTimeCounter()
                elif currentPositFragList[2] <= 0 and progPositFragList[2] >= 0 and xposJudgeBallLinear(shieldPosit[0][0], shieldPosit[0][1]) <= 0 and xposJudgeBallLinear(shieldPosit[1][0], shieldPosit[1][1]) >= 0:
                    #正面からの縦断
                    progPosit[1] = shieldPosit[0][1] * 2 - progPosit[1]
                    tempSpeed[1] *= -1
                    #tempSpeed[1] += (shieldPosit[0][1] - beforeShieldPosit[0][1]) / counter
                    tempSpeed[1] += self.character.speed[1]
                    self.character.charaShield.setCollisionTimeCounter()
            elif progPositFragList[0] >= 0 and progPositFragList[1] <= 0 and progPositFragList[2] >= 0 and progPositFragList[3] <= 0:
                #終点が平行四辺形内
                if progPosit[1] >= currentPosit[1]:
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
        self.rectList += self.slidePad.draw(screen)
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
                    print("棒左・ボール右・棒右移動")
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
                    print("棒左・ボール左・棒左移動")
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
                    print("棒右・ボール右・棒右移動")
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
                    print("棒右・ボール左・棒左移動")
                else:
                    pass
            pass
        self.character.charaStick.collisionjudgeInfo = [0, 0]
        return tempSpeed