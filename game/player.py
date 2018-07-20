# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = "Fireclaw the Fox"

__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

# Panda3D imoprts
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM # 在播放器脚本中使用 FSM 类
from panda3d.core import KeyboardButton

class Player(FSM): # 让 Player 类继承 FSM 类
    def __init__(self, charId, charNr, controls): # 参数 controls 是一个字符串变量，我们等待 p# 之类的值，其中 # 必须是 1 或 2 ，因为我们只有两个游戏玩家

        # 使用字符编号调用 init 函数，因此我们可以将该类用于我们存储在资产中的任何字符模型，而不需要为每个字符编写一个类以的字符ID
        FSM.__init__(self, "FSM-Player{}".format(charNr)) # 初始化 FSM 类

        self.charId = charId
        charPath = "characters/character{}/".format(charNr) # 使用存储在 charNr 中的字符编号来选择玩家所选字符的文件夹
        self.character = Actor(
            charPath + "char", {
                "Idle":charPath + "idle",
                "walk":charPath + "walk",
                "punch_l":charPath + "punch_l",
                "punch_r":charPath + "punch_r",
                "kick_l":charPath + "kick_l",
                "kick_r":charPath + "kick_r",
                "Hit":charPath + "hit",
                "defend":charPath + "defend"
            }) # 告诉Panda3D引擎加载动画模型，演员是由引擎设置的全局功能。这个函数的第一个参数是我们角色的主要模型，第二个是名称和路径字符串的映射。名称将用于稍后选择应播放哪个动画，另一个字符串确定 .egg 文件的路径，该文件包含属于主模型的动画。请注意，不需要也不应该将.egg 扩展名添加到路径中，因为稍后鸡蛋文件将转换为bam文件格式，我们将在后面的部分中对其进行描述。
        # self.character.setH(90) # 将字符围绕其向上指向轴旋转90度，在这种情况下，该轴是Z轴。

        # 告诉引擎它应该将字符添加到渲染节点。必须对应该在引擎创建的3D空间中呈现的任何对象执行此操作。
        self.character.reparentTo(render) # render 是由引擎设置的全局变量
        self.character.hide() # 直接调用 hide 函数，因为我们不希望角色在加载后直接显示。

        # 使用一组预定义的运动变量为角色添加键盘交互
        self.walkSpeed = 2.0 # units per second

        if controls == "p1":
            self.character.setH(90)
            self.leftButton = KeyboardButton.asciiKey(b"d")
            self.rightButton = KeyboardButton.asciiKey(b"f") # 使用'D'和'F'键分别让角色左右移动
            self.punchLButton = KeyboardButton.asciiKey(b"q")
            self.punchRButton = KeyboardButton.asciiKey(b"w")
            self.kickLButton = KeyboardButton.asciiKey(b"a")
            self.kickRButton = KeyboardButton.asciiKey(b"s")
            self.defendButton = KeyboardButton.asciiKey(b"e")
        
        elif controls == "p2":
            self.character.setH(-90)
            self.leftButton = KeyboardButton.right()
            self.rightButton = KeyboardButton.left()
            self.punchLButton = KeyboardButton.asciiKey(b"i")
            self.punchRButton = KeyboardButton.asciiKey(b"o")
            self.kickLButton = KeyboardButton.asciiKey(b"k")
            self.kickRButton = KeyboardButton.asciiKey(b"l")
            self.defendButton = KeyboardButton.asciiKey(b"p")
        
    def start(self, startPos):
        self.character.setPos(startPos) # 将角色在 3D 空间中的位置设置为 startPos 变量中给出的位置。
        self.character.show() # 让角色出现在应用程序中，与我们之前调用的 hide 函数相反。
        self.request("Idle")

        taskMgr.add(self.moveTask, "move task {}".format(self.charId))
        
    def stop(self):
        # 在想要完全停止播放器时使用 stop 方法，例如，如果稍后将游戏留在菜单屏幕或者将有一个暂停屏幕。
        self.character.hide() # 隐藏了玩家模型
        taskMgr.remove("move task {}".format(self.charId))
    
    def moveTask(self, task): # 额外参数 task 的类型为 direct.task.Task ，包含一些用于任务处理的重要事项
        # Player类的主要工作函数。只要玩家处于活动状态并且处理玩家可以做的所有动作，它就会一直运行。目前它只能在没有限制的情况下在x轴上左右移动播放器，因此您也可以移出屏幕

        if self.attackAnimationPlaying(): return task.cont # 检查角色是否已经播放了攻击动画。如果一个攻击动画正在播放，玩家不能做任何事情
        speed = 0.0 # 设置角色的移动速度
        isDown = base.mouseWatcherNode.isButtonDown

        # 关于角色的"防守状态"
        if isDown(self.defendButton):
            # 如果玩家改变到防守状态，角色将播放"防御动画"，并且只要玩家按下"防守键"，他将保持该状态并且如果它播放则停留在动画的最后一帧。
            if self.state != "Defend":
                self.request("Defend")
            return task.cont
            
        # Check for attack keys 攻击密钥
        # 只检查按下哪个攻击键并进入相应的状态
        # 我们不希望通过播放之后添加的可能的移动函数来"干扰"攻击动画。
        isAction = False
        if isDown(self.punchLButton):
            isAction = True # 每当按下一个攻击键时，检查变量 isAction 总是设置为true
            self.request("Punch_l")
        elif isDown(self.punchRButton):
            isAction = True
            self.request("Punch_r")
        elif isDown(self.kickLButton):
            isAction = True
            self.request("Kick_l")
        elif isDown(self.kickRButton):
            isAction = True
            self.request("Kick_r")
        if isAction: # 检查变量，检查玩家是否某一攻击状态
            return task.cont

        if isDown(self.leftButton):
            speed += self.walkSpeed
        if isDown(self.rightButton):
            speed -= self.walkSpeed
        yDelta = speed * globalClock.getDt() # 全局变量 globalClock 可以在应用程序的任何位置使用，并且最重要的是用于任务。
        self.character.setY(self.character, yDelta)

        # 通过在演员移动或停止移动时更改它们来利用我们的新状态
        if speed != 0.0 and self.state != "Walk" and self.state != "Walk_back":
            if speed < 0:
                self.request("Walk")
            else:
                self.request("Walk_back")
        elif speed == 0.0 and self.state != "Idle":
            self.request("Idle")

        return task.cont
    
    def enterIdle(self):
        # 只要 Player 类的 FSM 进入名为 Idle 的状态，就会调用此函数
        self.character.loop("Idle") # 状态区分大小写
    def exitIdle(self):
        self.character.stop()
    
    def enterWalk(self):
        self.character.loop("Walk")
    def exitWalk(self):
        self.character.stop()
    
    def enterWalk_back(self):
        self.character.loop("Walk_back")
    def exitWalk_back(self):
        self.character.stop()

    def enterPunch_l(self):
        self.character.play("Punch_l")
    def exitPunch_l(self):
        self.character.stop()

    def enterPunch_r(self):
        self.character.play("Punch_r")
    def exitPunch_r(self):
        self.character.stop()

    def enterKick_l(self):
        self.character.play("Kick_l")
    def exitKick_l(self):
        self.character.stop()

    def enterKick_r(self):
        self.character.play("Kick_r")
    def exitKick_r(self):
        self.character.stop()
    
    def enterDefend(self):
        self.character.play("Defend")
    def exitDefend(self):
        self.character.stop()
    
    def enterHit(self):
        self.character.play("Hit")
    def exitHit(self):
        self.character.stop()
    
    def enterDefeated(self):
        self.character.play("Defeated")
    def exitDefeated(self):
        self.character.stop()
    
    def attackAnimationPlaying(self):
        # 创建一个列表变量，其中包含玩家可以使用的攻击动画的所有名称
        actionAnimations = [
            "Punch_l",
            "Punch_r",
            "Kick_l",
            "Kick_r",
            "Hit"]
        
        # 根据 getCurrentAnim 函数返回的值进行检查，该函数将返回包含当前播放动画的字符串
        if self.character.getCurrentAnim() in actionAnimations: return True