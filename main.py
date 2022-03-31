# create new levels with different difficulties
# options menu
# how to play menu
# leader board
# level editor


import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")


from GameObjects import *
from GUIShapes import *


background = darkGray


def Quit():
	global running
	running = False


def	QuitToMenu():
	MainMenu.isMainMenuOpen = True
	PauseMenu.isGamePaused = False
	SoundManager.PlayMusic("menu.mp3")


allObjs = []


Y = height - 20


class BoxObj(Box):
	def __init__(self, rect, colors, name="", drawData={}, lists=[allObjs]):
		super().__init__(rect, colors, name, screen, drawData, lists)

	def Move(self, direction):
		pass


class GameObject:
	def __init__(self, rect):
		self.rect = pg.Rect(rect)

		AddToListOrDict([allObjs], self)

	def Move(self, direction):
		if direction[0]:
			if not player.colliding["right"]:
				self.rect.x -= player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 
		elif direction[1]:
			if not player.colliding["left"]:
				self.rect.x += player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 
 

class Image(BoxObj):
	allImages = []

	def __init__(self, rect, imgPath, scaleImg=True, name="", drawData={}, lists=[allImages, allObjs]):
		super().__init__(rect, ((0, 0, 0), (0, 0, 0)), name, drawData=drawData, lists=lists)

		self.imagePath = imgPath

		self.resize = False

		if scaleImg:
			self.ScaleImage(pg.image.load(self.imagePath) if self.imagePath != None else None, (self.rect.w, self.rect.h))
		else:
			if self.imagePath != None:
				self.image = pg.image.load(self.imagePath)
			else:
				self.image = None

	def Draw(self):
		if self.image != None:
			self.surface.blit(self.image, self.rect)

	def ScaleImage(self, image, size):
		if image != None:
			self.image = pg.transform.scale(pg.image.load(self.imagePath), size)
		else:
			self.image = None


class Entity(Box):
	def __init__(self, rect, colors, imgPath=None, data={}, name="", surface=screen, drawData={}, inputData={}, lists=[]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imgPath, lists=[])

		self.ogBorderColor = self.borderColor

		self.colliderRects = [pg.Rect(self.rect.x - 2, self.rect.y, 4, self.rect.h), pg.Rect(self.rect.x + self.rect.w - 2, self.rect.y, 4, self.rect.h), pg.Rect(self.rect.x, self.rect.y - 2, self.rect.w, 4), pg.Rect(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4)]
		self.colliders = [Collider(self.colliderRects[0], "left"), Collider(self.colliderRects[1], "right"), Collider(self.colliderRects[2], "up"), Collider(self.colliderRects[3], "down")]

		self.colliding = {"left": False, "right": False, "up": False, "down": False}

		self.moveSpeed = data.get("moveSpeed", 5)
		self.movementSpeed = self.moveSpeed
		self.gravity = data.get("gravity", 7)
		self.jumpForce = data.get("jumpForce", 10)
		self.dead = False
		self.j = 0

		self.isAffectedByGravity = data.get("isAffectedByGravity", True)
	
	def Draw(self):
		pg.draw.rect(self.surface, self.backgroundColor, self.rect)
		DrawRectOutline(self.borderColor, self.rect)

	def ApplyForce(self, magnitude, direction):
		if not self.dead:
			# left
			if direction[0][0]:
				if not self.colliding["left"]:
					self.rect.x -= magnitude
			
			# right
			if direction[0][1]:
				if not self.colliding["right"]:
					self.rect.x += magnitude
			
			# up 
			if direction[1][0]:
				if not self.colliding["up"]:
					self.rect.y -= magnitude
			
			# down
			if direction[1][1]:
				if not self.colliding["down"]:
					self.rect.y += magnitude

	def ApplyGravity(self):
		if not self.colliding["down"]:
			self.ApplyForce(self.gravity, [[False, False], [False, True]])

	def UpdateColliders(self, colliderRects):
		self.colliderRects = colliderRects

		if len(self.colliders) >= 1:
			self.colliders[0].rect = self.colliderRects[0]
		
		if len(self.colliders) >= 2:
			self.colliders[1].rect = self.colliderRects[1]
		
		if len(self.colliders) >= 3:
			self.colliders[2].rect = self.colliderRects[2]

		if len(self.colliders) >= 4:
			self.colliders[3].rect = self.colliderRects[3]

		self.colliding = {"left": False, "right": False, "up": False, "down": False}
	
	def Kill(self):
		self.dead = True


class LevelManager:
	levelID = 1
	difficulty = "normal"

	isGamePaused = False
	isSettingsOpen = False
	isHowToPlayOpen = False

	folder = "levels\\"
	fileExtension = "LVL"

	def UnloadLevel():
		lists = [Platform.allPlatforms, Ladder.allLadders, Stairs.allStairs, Coin.allCoins, Danger.allDangers, Water.allWater, Enemey.allEnemies, allObjs, Image.allImages]
		objsToRemove = []
		for l in lists:
			for obj in l:
				if type(obj) in [Platform, Ladder, Stairs, Coin, Water, Enemey, EndPoint]:
					if hasattr(obj, "name"):
						if obj.name not in ["floor", "roof", "leftWall", "rightWall"]:
							objsToRemove.append((l, obj))
					else:
						objsToRemove.append((l, obj))

		for obj in objsToRemove:
			obj[0].remove(obj[1])

	def LoadLevel(ID):
		global background

		fileName = f"level_{LevelManager.levelID}_{LevelManager.difficulty}.{LevelManager.fileExtension}"

		if not CheckFileExists(fileName, LevelManager.folder):
			return

		with open(LevelManager.folder + fileName) as file:
			level = file.read()

			file.close()

		platformColors = level[level.find("platformColors[(") + len("platformColors[(") : level.find(")]platformColors")].split("),(")
		ladderColors = level[level.find("ladderColors[(") + len("ladderColors[(") : level.find(")]ladderColors")].split("),(")
		stairColors = level[level.find("stairColors[(") + len("stairColors[(") : level.find(")]stairColors")].split("),(")
		coinColors = level[level.find("coinColors[(") + len("coinColors[(") : level.find(")]coinColors")].split("),(")
		waterColors = level[level.find("waterColors[(") + len("waterColors[(") : level.find(")]waterColors")].split("),(")
		enemyColors = level[level.find("enemyColors[(") + len("enemyColors[(") : level.find(")]enemyColors")].split("),(")
		endPointColors = level[level.find("endPointColors[(") + len("endPointColors[(") : level.find(")]endPointColors")].split("),(")

		def ConvertStringToColor(strColors):
			colors = []

			c = strColors[0].split(",")
			c[0] = int(c[0])
			c[1] = int(c[1])
			c[2] = int(c[2])

			colors.append(c)

			c = strColors[1].split(",")
			c[0] = int(c[0])
			c[1] = int(c[1])
			c[2] = int(c[2])
			
			colors.append(c)

			return colors

		def GetObj(colors, objs, lists):
			for obj in objs.split("\n"):
				rect = obj.split('),"')[0].split(":")[1].strip("(")
				x, y, w, h = rect.split(",")

				if "floor.rect.y" in y:
					y = y.replace("floor.rect.y", str(floor.rect.y))

				if "y" in y:
					y = y.replace("y", str(Y))

				if "-" in y:
					y = int(y.split("-")[0]) - int(y.split("-")[1])

				rect = (int(x), int(y), int(w), int(h))
				
				if "incline" in objs:
					colors = obj.split('),"')[1].split(":")[1].split(",")[0]
					incline = obj.split('),"')[1].split(',"')[1].split(":")[1]

					x, y, w, h = incline.strip("()").split(",")


					colors = allColors[colors.strip()]

					lists.append({"rect": rect, "colors": colors, "incline": (int(x), int(y), int(w), int(h))})
				else:
					colors = obj.split('),"')[1].split(":")[1].split(",")[0]
					

					colors = allColors[colors.strip()]
				
					lists.append({"rect": rect, "colors": colors})

			return lists

		background = level[level.find("background[") + len("background[") : level.find("]background")]
		background = background.split(":")
		if background[0] == "None":
			background = background[1]
			background = background.strip("()").split(",")
			background = (int(background[0]), int(background[1]), int(background[2]))
		else:
			background = Image((0, 0, width, height), background[0].strip('"'), False)

		platformColors = ConvertStringToColor(platformColors)
		ladderColors = ConvertStringToColor(ladderColors)
		stairColors = ConvertStringToColor(stairColors)
		coinColors = ConvertStringToColor(coinColors)
		waterColors = ConvertStringToColor(waterColors)
		enemyColors = ConvertStringToColor(enemyColors)
		endPointColors = ConvertStringToColor(endPointColors)
		allColors = {
			"platformColors": platformColors,
			"ladderColors": ladderColors,
			"stairColors": stairColors,
			"coinColors": coinColors,
			"waterColors": waterColors,
			"enemyColors": enemyColors,
			"endPointColors": endPointColors
		}

		plats = level[level.find("platforms[") + len("platforms[") + 1:level.find("]platforms") - 1]
		platforms = []

		ladds = level[level.find("ladders[") + len("ladders[") + 1:level.find("]ladders") - 1]
		ladders = []

		strs = level[level.find("stairs[") + len("stairs[") + 1:level.find("]stairs") - 1]
		stairs = []

		cs = level[level.find("coins[") + len("coins[") + 1:level.find("]coins") - 1]
		coins = []

		watr = level[level.find("Water[") + len("Water[") + 1:level.find("]Water") - 1]
		water = []

		enemy = level[level.find("Enemy[") + len("Enemy[") + 1:level.find("]Enemy") - 1]
		enemies = []

		endPoint = level[level.find("EndPoint[") + len("EndPoint[") + 1:level.find("]EndPoint") - 1]
		endPoints = []

		for obj in GetObj(platformColors, plats, platforms):
			Platform(obj["rect"], obj["colors"])

		for obj in GetObj(ladderColors, ladds, ladders):
			Ladder(obj["rect"], obj["colors"])

		for obj in GetObj(stairColors, strs, stairs):
			Stairs(obj["rect"], obj["colors"], stepRect=obj["incline"])

		for obj in GetObj(coinColors, cs, coins):
			Coin(obj["rect"], obj["colors"])

		for obj in GetObj(waterColors, watr, water):
			Water(obj["rect"], obj["colors"])

		for obj in GetObj(enemyColors, enemy, enemies):
			Enemey(obj["rect"], obj["colors"])

		obj = GetObj(endPointColors, endPoint, endPoints)[0]
		EndPoint.rect = pg.Rect(obj["rect"])
		EndPoint.backgroundColor, EndPoint.borderColor = obj["colors"]

	def LoadNextLevel():
		fileName = f"level_{LevelManager.levelID + 1}_{LevelManager.difficulty}.{LevelManager.fileExtension}"
		if CheckFileExists(fileName, LevelManager.folder):
			LevelManager.UnloadLevel()
			LevelManager.levelID += 1
			LevelManager.LoadLevel(LevelManager.levelID)
		else:
			Player.Restart()

	def ChangeDifficulty():
		if LevelManager.difficulty == "normal":
			LevelManager.difficulty = "hard"
		elif LevelManager.difficulty == "hard":
			LevelManager.difficulty = "easy"
		else:
			LevelManager.difficulty = "normal"

		for obj in MainMenu.mainMenu.objects:
			if obj.name == "difficulty_btn":
				obj.UpdateText(f"{LevelManager.difficulty[:1].upper()}{LevelManager.difficulty[1:]}")

		if hasattr(MainMenu, "levels"):
			for obj in MainMenu.levels.objects:
				if obj.name == "difficulty_btn_level_manager":
					obj.UpdateText(f"{LevelManager.difficulty[:1].upper()}{LevelManager.difficulty[1:]}")


class Collider:
	def __init__(self, rect, direction):
		self.rect = pg.Rect(rect)
		self.direction = direction

	def CollideCheck(self, rect):
		return self.rect.colliderect(rect)

	def Draw(self, col=blue):
		pg.draw.rect(screen, blue, self.rect)


class Platform(BoxObj):
	allPlatforms = []

	def __init__(self, rect, colors, imgPath=None, name="", drawData={}, lists=[allPlatforms, allObjs]):
		super().__init__(rect, colors, name, drawData, lists)

		self.image = Image(self.rect, imgPath, lists=[])

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		self.image.Draw()


class Stairs:
	allStairs = []
	
	def __init__(self, rect, colors, stepRect=(10, 20, 3, 1), imagePath=None, name="", drawData={}, lists=[allObjs, allStairs]):
		self.rect = pg.Rect(rect)

		self.backgroundColor = colors[0]
		self.borderColor = colors[1]

		self.stepRect = stepRect

		self.name = name

		self.image = Image(self.rect, imagePath)

		AddToListOrDict(lists, self)

		self.steps = [Platform((self.rect.x + (i * self.stepRect[0]), (self.rect.y - (i * self.stepRect[2] * self.stepRect[3])) + (self.rect.h if self.stepRect[3] == 1 else 0), self.stepRect[0], self.stepRect[1]), colors, imagePath, drawData={"borderWidth": 1}) for i in range(self.rect.w // self.stepRect[0])]
		
	def Move(self, direction):
		if direction[0]:
			if not Player.colliding["right"]:
				self.rect.x -= Player.movementSpeed * (Player.sprintSpeedMulti if Player.isSprinting else 1) 
		elif direction[1]:
			if not Player.colliding["left"]:
				self.rect.x += Player.movementSpeed * (Player.sprintSpeedMulti if Player.isSprinting else 1) 

	def Draw(self):
		pg.draw.rect(screen, red, self.rect)
		DrawRectOutline(black, (self.rect.x - 2, self.rect.y - 2, self.rect.w + 4, self.rect.h + 4))
		if self.stepRect[3] == -1:
			pg.draw.aaline(screen, black, (self.rect.x, self.rect.y), (self.rect.x + self.rect.w, self.rect.y + self.rect.h))
		if self.stepRect[3] == 1:
			pg.draw.aaline(screen, black, (self.rect.x, self.rect.y + self.rect.h), (self.rect.x + self.rect.w, self.rect.y))


class Ladder(Box):
	allLadders = []
	
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allLadders, allObjs]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[])

	def Draw(self):
		numOfRungs = self.rect.h // 20
		spacing = self.rect.h // numOfRungs
		self.rungs = [pg.Rect(self.rect.x, self.rect.y + (i * spacing), self.rect.w, 4) for i in range(numOfRungs)]
		self.DrawBackground()
		self.DrawBorder()		
		
		self.image.Draw()

		for rung in self.rungs:
			rung.x = self.rect.x
			pg.draw.rect(self.surface, self.borderColor, rung)


class Coin(Box):
	allCoins = []
	
	def __init__(self, rect, colors, value=1, pickUpSound=None, imagePath=None, name="", surface=screen, drawData={}, lists=[allObjs, allCoins]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.pickUpSound = pickUpSound

		self.value = value

		self.image = Image(self.rect, imagePath, lists=[])

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		self.image.Draw()

	def Collect(self):
		if self in allObjs:
			allObjs.remove(self)
		if self in Coin.allCoins:
			Coin.allCoins.remove(self)
			return self.value
		return 0


class Danger(Box):
	allDangers = []

	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allObjs, allDangers]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(rect, imagePath, lists=[])


class Water(Danger):
	allWater = []

	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allObjs, Danger.allDangers, allWater]):
		super().__init__(rect, colors, imagePath, name, surface, drawData, lists)

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		self.image.Draw()


class Enemey(Entity):
	allEnemies = []

	def __init__(self, rect, colors, imagePath=None, data={}, name="", surface=screen, drawData={}, inputData={}, lists=[allEnemies, allObjs, Danger.allDangers]):
		super().__init__(rect, colors, imagePath, data, name, surface, drawData, inputData, lists)

		self.isAffectedByGravity = data.get("isAffectedByGravity", False)

		self.isMovingLeft = True
		# score value
		self.value = 1

		#                                          left                                                             right                                                                                      up                                                           down
		self.colliderRects = [pg.Rect(self.rect.x - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x + self.rect.w - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x - 2, self.rect.y - 6, self.rect.w + 4, 12), pg.Rect(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4)]

		self.movementSpeed = data.get("moveSpeed", 2)

		self.mult = 1

	def Move(self):
		if self.isMovingLeft:
			self.ApplyForce(self.movementSpeed, [[True, False], [False, False]])
		else:
			self.ApplyForce(self.movementSpeed, [[False, True], [False, False]])

	def Collide(self):
		self.UpdateColliders([pg.Rect(self.rect.x - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x + self.rect.w - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x + 2, self.rect.y, self.rect.w - 4, 8), pg.Rect(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4)])

		for collider in self.colliders:
			if not Player.dead:
				if collider.direction == "up":
					if collider.CollideCheck(Player.rect):
						if not self.dead:
							Player.EnemeyKilled(self.value)
							self.Kill()
							return

		for collider in self.colliders:
			for platform in Platform.allPlatforms:
				if platform.name != "leftWall" and platform.name != "rightWall":
					if collider.CollideCheck(platform.rect):
						self.colliding[collider.direction] = True

			for enemy in Enemey.allEnemies:
				if enemy != self:
					if collider.CollideCheck(enemy.rect):
						self.colliding[collider.direction] = True
						enemy.isMovingLeft = not enemy.isMovingLeft
						break

			if collider.CollideCheck(Player.rect):
				Player.Kill()

	def Update(self):
		if not self.dead:
			self.Collide()

			if self.colliding["left"]:
				self.isMovingLeft = False

			elif self.colliding["right"]:
				self.isMovingLeft = True

			if self.isAffectedByGravity:
				self.ApplyGravity()

			self.Move()

	def Kill(self):
		self.dead = True

		if self in Danger.allDangers:
			Danger.allDangers.remove(self)
		if self in Enemey.allEnemies:
			Enemey.allEnemies.remove(self)


class EndPoint:
	rect = None
	backgroundColor = None
	borderColor = None

	def Draw():
		if EndPoint.rect != None and EndPoint.backgroundColor != None and EndPoint.borderColor != None:
			pg.draw.rect(screen, black, EndPoint.rect)
			pg.draw.rect(screen, EndPoint.backgroundColor, EndPoint.rect)
			pg.draw.rect(screen, EndPoint.backgroundColor, (EndPoint.rect.x - 5, EndPoint.rect.y, 5, 100))
			DrawRectOutline(EndPoint.borderColor, EndPoint.rect)
			DrawRectOutline(EndPoint.borderColor, pg.Rect(EndPoint.rect.x - 5, EndPoint.rect.y, 5, 100))


class Player:
	playerData = {
		"rect": (10, Y - 65, 20, 50),
		"moveSpeed": 5,
		"sprintSpeedMulti": 1,
		"gravity": 7,
		"jumpForce": 10,
		"climbSpeed": 6,
		"climbFallSpeed": 1,
		"climbDirection": -1,
		"isAffectedByGravity": True
	}
	startingRect = pg.Rect(playerData["rect"])
	rect = pg.Rect(startingRect)

	keyBinds = OpenFile("defaultKeybinds.json")

	moveSpeed = playerData["moveSpeed"]
	sprintSpeedMulti = playerData["sprintSpeedMulti"]
	movementSpeed = moveSpeed
	isSprinting = False
	gravity = playerData["gravity"]
	jumpForce = playerData["jumpForce"]
	grounded = False
	isJumping = False
	holdingJump = False
	climbing = False
	crouched = False
	crouchData = {"height": rect.h, "moveSpeed": moveSpeed}
	ogHeight = rect.h
	ladder = None
	climbSpeed = playerData["climbSpeed"]
	climbFallSpeed = playerData["climbFallSpeed"]
	climbDirection = playerData["climbDirection"]
	isAffectedByGravity = playerData["isAffectedByGravity"]
	dead = False
	won = False

	enemiesKilled = 0
	coins = 0

	backgroundColor = lightBlack
	borderColor = darkWhite

	direction = [False, False]

	colliderRects = [pg.Rect(rect.x - 2, rect.y, 4, rect.h), pg.Rect(rect.x + rect.w - 2, rect.y, 4, rect.h), pg.Rect(rect.x, rect.y - 2, rect.w, 4), pg.Rect(rect.x, rect.y + rect.h - 2, rect.w, 4)]
	colliders = [Collider(colliderRects[0], "left"), Collider(colliderRects[1], "right"), Collider(colliderRects[2], "up"), Collider(colliderRects[3], "down")]
	colliding = {"left": False, "right": False, "up": False, "down": False}

	j = 0

	def Draw():
		if MainMenu.IsMainMenuActive():
			pg.draw.rect(screen, Player.backgroundColor, Player.rect)
			DrawRectOutline(Player.borderColor, Player.rect)
			
			Player.coinCounter.UpdateRect((Player.rect.x + Player.rect.w // 2 - 15, Player.rect.y - 30, 30, 20))
			Player.coinCounter.Draw()

			if Player.dead:
				Player.deadMessageBox.Draw()

			if Player.won:
				Player.winningMessageBox.Draw()

	def HandleEvent(event):
		if not Player.dead and not Player.won:
			if event.type == pg.KEYDOWN:
				if event.key == Player.keyBinds.get("right"):
					Player.direction[0] = True
				
				if event.key == Player.keyBinds.get("left"):
					Player.direction[1] = True

				if event.key == Player.keyBinds.get("jump"):
					if Player.grounded:
						Player.isJumping = True
					Player.holdingJump = True

				if event.key == Player.keyBinds.get("crouch"):
					Player.crouched = True

				if event.key == Player.keyBinds.get("climbUp"):
					Player.climbing = True
					Player.climbDirection = -1
				
				if event.key == Player.keyBinds.get("climbDown"):
					Player.climbing = True
					Player.climbDirection = 1

				if event.key == Player.keyBinds.get("sprint"):
					Player.isSprinting = True

		if event.type == pg.KEYUP:
			if event.key == Player.keyBinds.get("right"):
				Player.direction[0] = False
			
			if event.key == Player.keyBinds.get("left"):
				Player.direction[1] = False

			if event.key == Player.keyBinds.get("jump"):
				Player.holdingJump = False

			if event.key == Player.keyBinds.get("crouch"):
				Player.crouched = False

			if event.key == Player.keyBinds.get("climbUp"):
				Player.climbing = False
			
			if event.key == Player.keyBinds.get("climbDown"):
				Player.climbing = False

			if event.key == Player.keyBinds.get("sprint"):
				Player.isSprinting = False

		if Player.dead:
			Player.deadMessageBox.HandleEvent(event)

		if Player.won:
			Player.winningMessageBox.HandleEvent(event)

	def ApplyForce(magnitude, direction):
		if not Player.dead:
			# left
			if direction[0][0]:
				if not Player.colliding["left"]:
					Player.rect.x -= magnitude

			# right
			if direction[0][1]:
				if not Player.colliding["right"]:
					Player.rect.x += magnitude

			# up
			if direction[1][0]:
				if not Player.colliding["up"]:
					Player.rect.y -= magnitude

			# down
			if direction[1][1]:
				if not Player.colliding["down"]:
					Player.rect.y += magnitude

	def ApplyGravity():
		if not Player.colliding["down"]:
			Player.ApplyForce(Player.gravity, [[False, False], [False, True]])

	def UpdateColliders(colliderRects):
		Player.colliderRects = colliderRects

		if len(Player.colliders) >= 1:
			Player.colliders[0].rect = Player.colliderRects[0]

		if len(Player.colliders) >= 2:
			Player.colliders[1].rect = Player.colliderRects[1]

		if len(Player.colliders) >= 3:
			Player.colliders[2].rect = Player.colliderRects[2]

		if len(Player.colliders) >= 4:
			Player.colliders[3].rect = Player.colliderRects[3]

		Player.colliding = {"left": False, "right": False, "up": False, "down": False}

	def Kill():
		if not Player.dead:
			Player.dead = True
			SoundManager.PlaySound("death.wav")

	def EnemeyKilled(value):
		Player.enemiesKilled += 1
		Player.IncreaseScore(value)

	def Collide():
		Player.UpdateColliders([pg.Rect(Player.rect.x - 2, Player.rect.y, 4, Player.rect.h), pg.Rect(Player.rect.x + Player.rect.w - 2, Player.rect.y, 4, Player.rect.h), pg.Rect(Player.rect.x, Player.rect.y - 2, Player.rect.w, 4), pg.Rect(Player.rect.x, Player.rect.y + Player.rect.h - 2, Player.rect.w, 4)])

		# platform
		for collider in Player.colliders:
			for platform in Platform.allPlatforms:
				if collider.CollideCheck(platform.rect):
					Player.colliding[collider.direction] = True

					if collider.direction == "up" and Player.colliding["up"]:
						Player.rect.y = platform.rect.y + platform.rect.h
					
					if collider.direction == "down" and Player.colliding["down"]:
						Player.rect.y = platform.rect.y - Player.rect.h

		# water
			for water in Water.allWater:
				if water.rect.x <= Player.rect.x and water.rect.x + water.rect.w >= Player.rect.x + Player.rect.w:
					if collider.CollideCheck(water.rect):
						Player.Kill()

		if Player.colliding["down"]:
			Player.grounded = True
		else:
			Player.grounded = False

		# ladders
		Player.ladder = None
		for ladder in Ladder.allLadders:
			for collider in Player.colliders:
				if collider.CollideCheck(ladder.rect):
					Player.ladder = ladder
					break

		# stairs
		Player.stairs = None
		for stairs in Stairs.allStairs:
			for collider in Player.colliders:
				if collider.CollideCheck(stairs.rect):
					Player.stairs = stairs
					break

		if Player.stairs != None:
			Player.colliding["left"] = False
			Player.colliding["right"] = False


		# coins
		for coin in Coin.allCoins:
			for collider in Player.colliders:
				if collider.CollideCheck(coin.rect):
					Player.CollectCoin(coin)

	def IncreaseScore(value=None):
		if type(value) == int:
			Player.coins += value
		else:
			Player.coins += value.Collect()
		
		Player.coinCounter.UpdateText(str(Player.coins))

	def CollectCoin(value):
		Player.IncreaseScore(value)
		SoundManager.PlaySound("collect_coin.wav")

	def Move():
		if not Camera.isPlayerInCenter:
			if Player.direction[0]:
				if not Player.colliding["right"]:
					Player.ApplyForce(Player.movementSpeed * (Player.sprintSpeedMulti if Player.isSprinting else 1), [[False, True], [False, False]])

			if Player.direction[1]:
				if not Player.colliding["left"]:
					Player.ApplyForce(Player.movementSpeed * (Player.sprintSpeedMulti if Player.isSprinting else 1), [[True, False], [False, False]])

	def Jump():
		if Player.isJumping:
			Player.j += 0.1
			Player.ApplyForce(Player.jumpForce, [[False, False], [True, False]])

			if Player.j >= 1 or Player.colliding["up"]:
				Player.j = 0
				Player.isJumping = False

	def Climb():
		if Player.ladder != None:
			if Player.climbing:
				canClimb = False
				if Player.climbDirection == -1:
					if Player.rect.y + Player.rect.h > Player.ladder.rect.y:
						canClimb = True
				
				if Player.climbDirection == 1:
					if Player.rect.y + Player.rect.h < Player.ladder.rect.y + Player.ladder.rect.h:
						canClimb = True

				if canClimb:
					# Player.rect.y += Player.climbSpeed * Player.climbDirection
					Player.ApplyForce(Player.climbSpeed, [[False, False], [True if Player.climbDirection == -1 else False, True if Player.climbDirection == 1 else False]])

			else:
				# Player.rect.y += Player.climbFallSpeed
				Player.ApplyForce(Player.climbFallSpeed, [[False, False], [False, True]])

	def Crouch():
		if not Player.climbing:
			if Player.crouched:
				Player.rect.h = Player.crouchData["height"]
				Player.movementSpeed = Player.crouchData["moveSpeed"]
			else:
				if Player.rect.h != Player.ogHeight:
					for i in range(3):
						if not Player.colliding["up"]:
							Player.rect.h = Player.ogHeight
							Player.movementSpeed = Player.moveSpeed
						else:
							Player.rect.h = Player.crouchData["height"]
							Player.movementSpeed = Player.crouchData["moveSpeed"]

						Player.Collide()

	def Win():
		Player.won = True
		gameTimer.Stop()
		Player.winningMessageBox.messageBox.UpdateText(f"You have beat the level!")
		Player.isJumping = False
		Player.direction = [False, False]
		SoundManager.PlaySound("victory sound.mp3")

	def Update():
		if not Player.dead or not Player.won and MainMenu.IsMainMenuActive() and not PauseMenu.isGamePaused:
			Player.Collide()
			
			if Player.direction != None:
				Player.Move()

			Player.Jump()
			
			if Player.holdingJump:
				if Player.grounded:
					Player.isJumping = True

			Player.Climb()
			Player.Crouch()

			if not Player.isJumping:
				if Player.ladder == None:
					# gravity
					# [left, right], [up, down]
					if Player.isAffectedByGravity:
						Player.ApplyGravity()

			if EndPoint.rect != None:
				if Player.rect.x >= EndPoint.rect.x:
					Player.Win()

	def Restart():
		Player.dead = False
		Player.won = False
		Player.ResetPos()
		LevelManager.UnloadLevel()
		LevelManager.LoadLevel(LevelManager.levelID)
		Player.enemiesKilled = 0
		Player.coins = 0
		Player.coinCounter.UpdateText("0")
		gameTimer.Reset()

	def ResetPos():
		Player.rect = pg.Rect(Player.startingRect)
		centerMarker.rect.x = width // 3

	def LoadNextLevel():
		LevelManager.LoadNextLevel()
		Player.Restart()

	coinCounter = Label((rect.x + rect.w // 2 - 15, rect.y - 30, 30, 20), (lightBlack, darkWhite), "0", textData={"fontSize": 15}, drawData={"drawBackground": True, "drawBorder": False}, lists=[])

	deadMessageBox = MessageBox((width // 2 - 200, height // 2 - 100, 400, 200), (lightBlack, darkWhite, lightBlue), confirmButtonData={"text": "Quit", "rect": pg.Rect(width // 2 - 190, height // 2 + 35, 185, 35), "onClick": QuitToMenu}, cancelButtonData={"onClick":Restart, "text": "Restart", "rect": pg.Rect(width // 2, height // 2 + 35, 190, 35)}, messageBoxData={"text": "You have died!\nPress the restart button to restart the level.\nPress the quit button to exit.", "rect": pg.Rect(width // 2 - 190, height // 2 - 90, 380, 100)}, lists=[])
	
	winningMessageBox = MessageBox((width // 2 - 200, height // 2 - 100, 400, 200), (lightBlack, darkWhite, lightBlue), cancelButtonData={"onClick":LoadNextLevel, "text": "Next Level", "rect": pg.Rect(width // 2, height // 2 + 35, 190, 35), "onClick": LevelManager.LoadNextLevel}, confirmButtonData={"text": "Quit to menu", "onClick": QuitToMenu, "rect": pg.Rect(width // 2 - 190, height // 2 + 35, 185, 35)}, messageBoxData={"rect": pg.Rect(width // 2 - 190, height // 2 - 90, 380, 100)}, lists=[])


class Camera(BoxObj):
	rect = pg.Rect(0, 0, width, height)
	isPlayerInCenter = False
	defaultPos = (rect.x, rect.y)

	def Move(self, pos):
		Camera.rect.x = pos[0]
		Camera.rect.y = pos[1]

	def Update():
		if Player.rect.x >= centerMarker.rect.x:
			Camera.isPlayerInCenter = True
		elif Player.rect.x < centerMarker.rect.x:
			Camera.isPlayerInCenter = False
		else:
			Camera.Move(Camera.defaultPos)

		if Camera.isPlayerInCenter:
			for obj in allObjs:
				Camera.MoveObj(obj, Player.direction)
		
			Camera.MoveObj(EndPoint, Player.direction)

	def MoveObj(obj, direction):
		if hasattr(obj, "name"):
			if obj.name in ["roof", "leftWall", "rightWall", "floor"]:
				return 

		if direction[0]:
			if not Player.colliding["right"]:
				obj.rect.x -= Player.movementSpeed * (Player.sprintSpeedMulti if Player.isSprinting else 1)
		elif direction[1]:
			if not Player.colliding["left"]:
				obj.rect.x += Player.movementSpeed * (Player.sprintSpeedMulti if Player.isSprinting else 1)


class GameTimer:
	def __init__(self):
		self.startTime = dt.datetime.now()

		self.hours = 0
		self.minutes = 0

		self.timer = Label((width - 210, 10, 200, 50), (lightBlack, darkWhite), drawData={"roundedCorners": True, "roundness": 2}, textData={"fontSize": 30}, lists=[])

		self.paused = False
		self.stopped = False

		self.pauseOffSet = dt.timedelta(0)

	def Reset(self):
		self.paused = False
		self.stopped = False
		self.startTime = dt.datetime.now()

	def Pause(self):
		self.paused = True
		self.pausedAt = dt.datetime.now()

	def Resume(self):
		self.pauseOffSet += (dt.datetime.now() - self.pausedAt)
		self.paused = False

	def Stop(self):
		self.stopped = True

	def GetDiff(self):
		return (dt.datetime.now() - self.startTime) - self.pauseOffSet

	def Update(self):
		if not self.paused and not self.stopped:
			self.difference = self.GetDiff()

			if self.difference.seconds % 60 == 0:
				self.minutes = self.difference.seconds // 60

			if self.difference.seconds % 3600 == 0:
				self.hours = self.difference.seconds // 3600

			msg = f"{self.hours}:{self.minutes}:{self.difference.seconds % 60}:{str(self.difference.microseconds)[0]}"
			self.timer.UpdateText(msg)
			return msg


class SoundManager:
	master = 0.1
	sfx = 1
	music = 0.6

	musicFolder = "music/"
	sfxFolder = "sounds/"

	menuFile = "menu.mp3"

	musicChannel = pg.mixer.Channel(0)
	if __name__ == "__main__":
		musicChannel.play(pg.mixer.Sound(musicFolder + menuFile), loops=-1)
	musicChannel.set_volume(master * music)

	sfxChannels = [pg.mixer.Channel(i) for i in range(1, 5)]

	def ChangeMasterVolume(value):
		SoundManager.master = min(1, max(0, value))
		SoundManager.ChangeVolume()

	def ChangeSFXVolume(value):
		SoundManager.sfx = min(1, max(0, value))
		SoundManager.ChangeVolume()

	def ChangeMusicVolume(value):
		SoundManager.music = min(1, max(0, value))
		SoundManager.ChangeVolume()

	def ChangeVolume():
		SoundManager.musicChannel.set_volume(max(0, min(1, SoundManager.master * SoundManager.music)))
		for sfx in SoundManager.sfxChannels:
			sfx.set_volume(max(0, min(1, SoundManager.master * SoundManager.sfx)))

	def PlayMusic(fileName):
		if CheckFileExists(fileName, SoundManager.musicFolder):
			SoundManager.musicChannel.stop()
			SoundManager.musicChannel.play(pg.mixer.Sound(SoundManager.musicFolder + fileName), loops=-1)
			SoundManager.musicChannel.set_volume(max(0, min(1, SoundManager.master * SoundManager.music)))

	def PlaySound(fileName):
		if CheckFileExists(fileName, SoundManager.sfxFolder):
			for sfx in SoundManager.sfxChannels:
				if sfx.get_busy() == False:
					sfx.play(pg.mixer.Sound(SoundManager.sfxFolder + fileName))
					sfx.set_volume(max(0, min(1, SoundManager.master * SoundManager.sfx)))
					break


class Settings:
	def GetKeyName(key):
		key = str(key)
		keyBindNames = OpenFile("allowedKeyBinds.json")
		if key in keyBindNames:
			return keyBindNames[key]
		return "UNDEFINED"

	isChangingKeyBind = False
	keyName = None

	def StartChangeKeyBind(keyName):
		Settings.isChangingKeyBind = True
		Settings.keyName = keyName

		keybindsMessage = "Waiting for keyboard input.\nPress ESCAPE to cancel."
		if MainMenu.isMainMenuOpen:
			MainMenu.changingKeyBindMessage.UpdateText(keybindsMessage)
		else:
			PauseMenu.changingKeyBindMessage.UpdateText(keybindsMessage)

	def ChangeKeyBind(event):
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				Settings.StopChangeKeyBind()
			else:
				if Settings.GetKeyName(event.key) != "UNDEFINED":
					for key in Player.keyBinds:
						if Player.keyBinds[key] == event.key:
							Settings.StopChangeKeyBind()
							break
					
					if Settings.isChangingKeyBind:
						Player.keyBinds[Settings.keyName] = event.key
						for obj in MainMenu.mainMenuSettingsMenu.objects:
							if obj.name == "keyBinds":
								for elem in obj.objects:
									if elem.name == Settings.keyName:
										elem.UpdateText(Settings.GetKeyName(event.key))
						
						for obj in PauseMenu.settingsMenu.objects:
							if obj.name == "keyBinds":
								for elem in obj.objects:
									if elem.name == Settings.keyName:
											elem.UpdateText(Settings.GetKeyName(Player.keyBinds[elem.name]))

					Settings.StopChangeKeyBind()

	def StopChangeKeyBind():
		Settings.isChangingKeyBind = False
		if MainMenu.isMainMenuOpen:
			MainMenu.changingKeyBindMessage.UpdateText("")
		else:
			PauseMenu.changingKeyBindMessage.UpdateText("")

	def ResetKeybinds():
		Player.keyBinds = OpenFile("defaultKeybinds.json")
		Settings.UpdateText()

	def UpdateText():
		for obj in MainMenu.mainMenuSettingsMenu.objects:
			if obj.name == "keyBinds":
				for elem in obj.objects:
					if elem.name in Player.keyBinds:
						elem.UpdateText(Settings.GetKeyName(Player.keyBinds[elem.name]))

		for obj in PauseMenu.settingsMenu.objects:
			if obj.name == "keyBinds":
				for elem in obj.objects:
					if elem.name in Player.keyBinds:
						elem.UpdateText(Settings.GetKeyName(Player.keyBinds[elem.name]))


class MainMenu:
	isMainMenuOpen = True
	isMainMenuSettingsOpen = False
	isMainMenuHowToPlayOpen = False
	isMainMenuSelectLevelOpen = False

	def Draw():
		if MainMenu.isMainMenuSettingsOpen:
			MainMenu.mainMenuSettingsMenu.Draw()
		else:
			if MainMenu.isMainMenuSelectLevelOpen:
				MainMenu.mainMenuSelectLevelMenu.Draw()
				MainMenu.levels.Draw()
			else:
				if MainMenu.isMainMenuHowToPlayOpen:
					MainMenu.mainMenuHowToPlayMenu.Draw()
				else:
					if MainMenu.isMainMenuOpen:
						MainMenu.mainMenu.Draw()

	def HandleEvent(event):
		if MainMenu.isMainMenuSettingsOpen:
			MainMenu.mainMenuSettingsMenu.HandleEvent(event)
		else:
			if MainMenu.isMainMenuHowToPlayOpen:
				MainMenu.mainMenuHowToPlayMenu.HandleEvent(event)
			else:
				if MainMenu.isMainMenuSelectLevelOpen:
					MainMenu.mainMenuSelectLevelMenu.HandleEvent(event)
					MainMenu.levels.HandleEvent(event)
				else:
					if MainMenu.isMainMenuOpen:
						MainMenu.mainMenu.HandleEvent(event)

	def IsMainMenuActive():
		return not MainMenu.isMainMenuOpen and not MainMenu.isMainMenuSettingsOpen and not MainMenu.isMainMenuSelectLevelOpen and not MainMenu.isMainMenuHowToPlayOpen

	def OpenMainMenuSettings():
		MainMenu.isMainMenuSettingsOpen = True
		for obj in MainMenu.mainMenuSettingsMenu.objects:
			if obj.name == "master":
				obj.SetValue(SoundManager.master)
			if obj.name == "sfx":
				obj.SetValue(SoundManager.sfx)
			if obj.name == "music":
				obj.SetValue(SoundManager.music)

	def CloseMainMenuSettings():
		MainMenu.isMainMenuSettingsOpen = False

	def OpenMainMenuHowToPlay():
		MainMenu.isMainMenuHowToPlayOpen = True

	def CloseMainMenuHowToPlay():
		MainMenu.isMainMenuHowToPlayOpen = False

	def OpenSelectLevelMenu():
		MainMenu.isMainMenuSelectLevelOpen = True

		MainMenu.levels = Collection([
			Box((10, 140, width - 20, height - 230), (lightBlack, darkWhite), lists=[]),
			Label((10, height - 70, 110, 50), (lightBlack, darkWhite), text="Difficulty: ", lists=[]),
			Button((125, height - 70, 100, 50), (lightBlack, darkWhite, lightBlue), text=f"{LevelManager.difficulty[:1].upper()}{LevelManager.difficulty[1:]}", onClick=LevelManager.ChangeDifficulty, name="difficulty_btn_level_manager", lists=[]),
			])
		files = GetAllFilesInFolder(LevelManager.folder)
		x = 20
		index = 8
		for i in range(len(files) // 3):
			if i % index == 0 and i != 0:
				x += 120

			MainMenu.levels.Add(Button((x, 150 + ((i % index) * 60), 110, 50), (lightBlack, darkWhite, lightBlue), text=f"Level {i + 1}", onClick=MainMenu.LoadLevel, onClickArgs=[i + 1], lists=[]))

	def LoadLevel(levelID):
		MainMenu.CloseSelectLevelMenu()
		MainMenu.isMainMenuOpen = False
		LevelManager.UnloadLevel()
		LevelManager.LoadLevel(levelID)

	def CloseSelectLevelMenu():
		MainMenu.isMainMenuSelectLevelOpen = False

	def StartGame():
		MainMenu.isMainMenuOpen = False
		LevelManager.UnloadLevel()
		LevelManager.LoadLevel(LevelManager.levelID)
		SoundManager.PlayMusic(f"level_{LevelManager.levelID}.mp3")

		for obj in PauseMenu.settingsMenu.objects:
			if obj.name == "master":
				obj.SetValue(SoundManager.master)
				SoundManager.ChangeMasterVolume(obj.GetValue())
			if obj.name == "sfx":
				obj.SetValue(SoundManager.sfx)
				SoundManager.ChangeSFXVolume(obj.GetValue())
			if obj.name == "music":
				obj.SetValue(SoundManager.music)
				SoundManager.ChangeMusicVolume(obj.GetValue())

		SoundManager.ChangeVolume()

	mainMenu = Collection([
		Box((0, 0, width, height), (ChangeColorBrightness(darkGray, 40), ChangeColorBrightness(darkGray, 40)), lists=[]),
		Label((400, 50, width - 800, 75), (lightBlack, darkWhite), text="Title", textData={"fontSize": 40}, drawData={"roundedCorners": True, "roundness": 0}, lists=[]),
		Button((width // 2 - 200, 175, 400, 75), (lightBlack, darkWhite, lightBlue), onClick=StartGame, text="Start Game", textData={"fontSize": 35}, drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		Button((width // 2 - 200, 275, 400, 75), (lightBlack, darkWhite, lightBlue), onClick=OpenSelectLevelMenu, text="Select Level", textData={"fontSize": 35}, drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		Button((width // 2 - 200, 375, 400, 75), (lightBlack, darkWhite, lightBlue), onClick=OpenMainMenuSettings, text="Settings", textData={"fontSize": 35}, drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		Button((width // 2 - 200, 475, 400, 75), (lightBlack, darkWhite, lightBlue), onClick=OpenMainMenuHowToPlay, text="How To Play", textData={"fontSize": 35}, drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		Button((width // 2 - 200, 575, 400, 75), (lightBlack, darkWhite, lightBlue), onClick=Quit, text="Exit", textData={"fontSize": 35}, drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		Label((width - 405, 175, 110, 50), (lightBlack, darkWhite), text="Difficulty: ", lists=[]),
		Button((width - 290, 175, 100, 50), (lightBlack, darkWhite, lightBlue), text=f"{LevelManager.difficulty[:1].upper()}{LevelManager.difficulty[1:]}", onClick=LevelManager.ChangeDifficulty, name="difficulty_btn", lists=[]),
		HyperLink((width - 110, height - 35, 100, 25), (lightBlack, darkWhite, lightBlue), text="Music", url="https://www.FesliyanStudios.com", textData={"fontSize": 15}, lists=[])
		])

	changingKeyBindMessage = Label((50, 510, 400, 50), (lightBlack, darkWhite), lists=[], textData={"fontSize": 18, "alignText": "top"})
	mainMenuSettingsMenu = Collection([
		Box((0, 0, width, height), (ChangeColorBrightness(darkGray, 40), ChangeColorBrightness(darkGray, 40)), lists=[]),
		Label((400, 50, width - 800, 75), (lightBlack, darkWhite), text="Settings", lists=[], drawData={"roundedCorners": True, "roundness": 0}, textData={"fontSize": 40}),
		Label((50, 150, 400, 50), (lightBlack, darkWhite), text="Key Binds", drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		changingKeyBindMessage,
		Collection([
			Label((50, 210, 195, 50), (lightBlack, darkWhite), text="Move Left", lists=[]),
			Button((255, 210, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["left"]), name="left", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["left"]),
			Label((50, 270, 195, 50), (lightBlack, darkWhite), text="Move Right", lists=[]),
			Button((255, 270, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["right"]), name="right", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["right"]),
			Label((50, 330, 195, 50), (lightBlack, darkWhite), text="Jump", lists=[]),
			Button((255, 330, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["jump"]), name="jump", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["jump"]),
			Label((50, 390, 195, 50), (lightBlack, darkWhite), text="Climb Up", lists=[]),
			Button((255, 390, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["climbUp"]), name="climbUp", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["climbUp"]),
			Label((50, 450, 195, 50), (lightBlack, darkWhite), text="Climb Down", lists=[]),
			Button((255, 450, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["climbDown"]), name="climbDown", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["climbDown"]),
			], name="keyBinds"),
		Button((50, 570, 195, 50), (lightBlack, darkWhite, lightBlue), text="Reset keybinds", onClick=Settings.ResetKeybinds, lists=[]),
		Slider((500, 200, 400, 50), (lightBlack, darkWhite), name="master", buttonData={"backgroundColor": darkGray, "inactiveColor": darkWhite, "activeColor": lightBlue}, lists=[], drawData={"header": "Master Volume", "roundedCorners": True, "roundness": 10}, inputData={"startingValue": SoundManager.master, "onValueChange": SoundManager.ChangeMasterVolume}),
		Slider((500, 320, 400, 50), (lightBlack, darkWhite), name="sfx", buttonData={"backgroundColor": darkGray, "inactiveColor": darkWhite, "activeColor": lightBlue}, lists=[], drawData={"header": "SFX Volume", "roundedCorners": True, "roundness": 10}, inputData={"startingValue": SoundManager.sfx, "onValueChange": SoundManager.ChangeSFXVolume}),
		Slider((500, 440, 400, 50), (lightBlack, darkWhite), name="music", buttonData={"backgroundColor": darkGray, "inactiveColor": darkWhite, "activeColor": lightBlue}, lists=[], drawData={"header": "Music Volume", "roundedCorners": True, "roundness": 10}, inputData={"startingValue": SoundManager.music, "onValueChange": SoundManager.ChangeMusicVolume}),
		Button((width - 150, height - 75, 100, 50), (lightBlack, darkWhite, lightBlue), text="Close", lists=[], drawData={"roundedCorners": True, "roundness": 5}, onClick=CloseMainMenuSettings)
		])

	mainMenuSelectLevelMenu = Collection([
		Box((0, 0, width, height), (ChangeColorBrightness(darkGray, 40), ChangeColorBrightness(darkGray, 40)), lists=[]),
		Label((400, 50, width - 800, 75), (lightBlack, darkWhite), text="Select Level", lists=[], drawData={"roundedCorners": True, "roundness": 0}, textData={"fontSize": 40}),
		Button((width - 150, height - 75, 100, 50), (lightBlack, darkWhite, lightBlue), text="Close", lists=[], drawData={"roundedCorners": True, "roundness": 5}, onClick=CloseSelectLevelMenu)
		])

	howToPlayDescText = OpenFile("howToPlayDescText.txt")
	mainMenuHowToPlayMenu = Collection([
		Box((0, 0, width, height), (ChangeColorBrightness(darkGray, 40), ChangeColorBrightness(darkGray, 40)), lists=[]),
		Label((400, 50, width - 800, 75), (lightBlack, darkWhite), text="How To Play", lists=[], drawData={"roundedCorners": True, "roundness": 0}, textData={"fontSize": 40}),
		Button((width - 150, height - 75, 100, 50), (lightBlack, darkWhite, lightBlue), text="Close", lists=[], drawData={"roundedCorners": True, "roundness": 5}, onClick=CloseMainMenuHowToPlay),
		Label((width // 2 - 300, height // 2 - 200, 600, 400), (lightBlack, darkWhite), text=howToPlayDescText, drawData={"roundedCorners": True, "roundness": 20}, textData={"fontSize": 25, "alignText": "left-top"}, lists=[]),
		])


class PauseMenu:
	isGamePaused = False
	isSettingsOpen = False
	isHowToPlayOpen = False

	def Pause():
		PauseMenu.isGamePaused = True
		gameTimer.Pause()

	def Resume():
		PauseMenu.isGamePaused = False
		gameTimer.Resume()

	def	OpenSettings():
		PauseMenu.isSettingsOpen = True
	
	def	CloseSettings():
		PauseMenu.isSettingsOpen = False

	def	OpenHowToPlay():
		PauseMenu.isHowToPlayOpen = True
	
	def	CloseHowToPlay():
		PauseMenu.isHowToPlayOpen = False

	def Draw():
		if not MainMenu.isMainMenuOpen:
			PauseMenu.pauseButton.Draw()

		if PauseMenu.isGamePaused:
			if PauseMenu.isHowToPlayOpen:
				PauseMenu.howToPlayMenu.Draw()
			
			if PauseMenu.isSettingsOpen:
				PauseMenu.settingsMenu.Draw()

			if not PauseMenu.isSettingsOpen and not PauseMenu.isHowToPlayOpen:
				PauseMenu.pauseMenu.Draw()

	def HandleEvent(event):
		PauseMenu.pauseButton.HandleEvent(event)

		if PauseMenu.isGamePaused:
			if PauseMenu.isHowToPlayOpen:
				PauseMenu.howToPlayMenu.HandleEvent(event)
			
			if PauseMenu.isSettingsOpen:
				PauseMenu.settingsMenu.HandleEvent(event)

			if not PauseMenu.isSettingsOpen and not PauseMenu.isHowToPlayOpen:
				PauseMenu.pauseMenu.HandleEvent(event)
				return

	pauseButton = Collection([
		Button((10, 20, 30, 30), (lightBlack, darkWhite, lightBlue), onClick=Pause, drawData={"drawBackground": False, "drawBorder": False}, lists=[]),
		Image((10, 20, 30, 30), "pause_btn.png", lists=[]),
		])

	pauseMenu = Collection([
		Image((0, 0, width, height), "pause.png", lists=[]),
		Label((width // 2 - 200, 50, 400, 100), (lightBlack, darkWhite), text="Game is paused", textData={"fontSize": 50}, drawData={"roundedCorners": True, "roundness": 4}, lists=[]),
		Box((width // 2 - 200, 200, 400, 290), (ChangeColorBrightness(black, 50), darkWhite), drawData={"roundedCorners": True, "roundness": 24}, lists=[]),
		Button((width // 2 - 190, 220, 380, 50), (lightBlack, darkWhite, lightBlue), text="Resume", drawData={"roundedCorners": True, "roundness":8}, onClick=Resume, lists=[]),
		Button((width // 2 - 190, 285, 380, 50), (lightBlack, darkWhite, lightBlue), text="Settings", drawData={"roundedCorners": True, "roundness":8}, onClick=OpenSettings, lists=[]),
		Button((width // 2 - 190, 350, 380, 50), (lightBlack, darkWhite, lightBlue), text="How To Play", drawData={"roundedCorners": True, "roundness":8}, onClick=OpenHowToPlay, lists=[]),
		Button((width // 2 - 190, 415, 380, 50), (lightBlack, darkWhite, lightBlue), text="Quit To Menu", drawData={"roundedCorners": True, "roundness":8}, onClick=QuitToMenu, lists=[]),
		])

	howToPlayDescText = OpenFile("howToPlayDescText.txt")
	howToPlayMenu = Collection([
		Box((10, 10, width - 20, height - 20), (ChangeColorBrightness(darkGray, 40), darkWhite), drawData={"roundedCorners": True, "roundness": 24}, lists=[]),
		Label((width // 2 - 200, 20, 400, 100), (lightBlack, darkWhite), text="How To Play", textData={"fontSize": 50}, drawData={"roundedCorners": True, "roundness": 4}, lists=[]),
		Label((width // 2 - 300, height // 2 - 200, 600, 400), (lightBlack, darkWhite), text=howToPlayDescText, drawData={"roundedCorners": True, "roundness": 20}, textData={"fontSize": 25, "alignText": "left-top"}, lists=[]),
		Button((width - 145, height - 85, 120, 60), (lightBlack, darkWhite, lightBlue), text="Close", drawData={"roundedCorners": True, "roundness": 8}, onClick=CloseHowToPlay, lists=[]),
		])

	changingKeyBindMessage = Label((50, 510, 400, 50), (lightBlack, darkWhite), lists=[], textData={"fontSize": 18, "alignText": "top"})
	settingsMenu = Collection([
		Box((10, 10, width - 20, height - 20), (ChangeColorBrightness(darkGray, 40), darkWhite), drawData={"roundedCorners": True, "roundness": 24}, lists=[]),
		Label((width // 2 - 200, 20, 400, 100), (lightBlack, darkWhite), text="Settings", textData={"fontSize": 50}, drawData={"roundedCorners": True, "roundness": 4}, lists=[]),
		Label((50, 150, 400, 50), (lightBlack, darkWhite), text="Key Binds", drawData={"roundedCorners": True, "roundness": 5}, lists=[]),
		changingKeyBindMessage,
		Collection([
			Label((50, 210, 195, 50), (lightBlack, darkWhite), text="Move Left", lists=[]),
			Button((255, 210, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["left"]), name="left", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["left"]),
			Label((50, 270, 195, 50), (lightBlack, darkWhite), text="Move Right", lists=[]),
			Button((255, 270, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["right"]), name="right", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["right"]),
			Label((50, 330, 195, 50), (lightBlack, darkWhite), text="Jump", lists=[]),
			Button((255, 330, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["jump"]), name="jump", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["jump"]),
			Label((50, 390, 195, 50), (lightBlack, darkWhite), text="Climb Up", lists=[]),
			Button((255, 390, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["climbUp"]), name="climbUp", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["climbUp"]),
			Label((50, 450, 195, 50), (lightBlack, darkWhite), text="Climb Down", lists=[]),
			Button((255, 450, 195, 50), (lightBlack, darkWhite, lightBlue), text=Settings.GetKeyName(Player.keyBinds["climbDown"]), name="climbDown", lists=[], onClick=Settings.StartChangeKeyBind, onClickArgs=["climbDown"]),
			], name="keyBinds"),
		Button((50, 570, 195, 50), (lightBlack, darkWhite, lightBlue), text="Reset keybinds", onClick=Settings.ResetKeybinds, lists=[]),
		Slider((500, 200, 400, 50), (lightBlack, darkWhite), name="master", buttonData={"backgroundColor": darkGray, "inactiveColor": darkWhite, "activeColor": lightBlue}, lists=[], drawData={"header": "Master Volume", "roundedCorners": True, "roundness": 10}, inputData={"startingValue": SoundManager.master, "onValueChange": SoundManager.ChangeMasterVolume}),
		Slider((500, 320, 400, 50), (lightBlack, darkWhite), name="sfx", buttonData={"backgroundColor": darkGray, "inactiveColor": darkWhite, "activeColor": lightBlue}, lists=[], drawData={"header": "SFX Volume", "roundedCorners": True, "roundness": 10}, inputData={"startingValue": SoundManager.sfx, "onValueChange": SoundManager.ChangeSFXVolume}),
		Slider((500, 440, 400, 50), (lightBlack, darkWhite), name="music", buttonData={"backgroundColor": darkGray, "inactiveColor": darkWhite, "activeColor": lightBlue}, lists=[], drawData={"header": "Music Volume", "roundedCorners": True, "roundness": 10}, inputData={"startingValue": SoundManager.music, "onValueChange": SoundManager.ChangeMusicVolume}),
		Button((width - 145, height - 85, 120, 60), (lightBlack, darkWhite, lightBlue), text="Close", drawData={"roundedCorners": True, "roundness": 8}, onClick=CloseSettings, lists=[]),
		])


def DrawObj(obj):
	if not MainMenu.isMainMenuOpen:
		if obj.rect.colliderect(Camera.rect):
			obj.Draw()


def DrawLoop():
	screen.fill(darkGray)

	if not isinstance(background, Image):
		pg.draw.rect(screen, background, (0, 0, width, height))
	
	for img in Image.allImages:
		img.Draw()

	for stair in Stairs.allStairs:
		stair.Draw()

	for platform in Platform.allPlatforms:
		DrawObj(platform)
	
	for ladder in Ladder.allLadders:
		DrawObj(ladder)

	for coin in Coin.allCoins:
		DrawObj(coin)

	for danger in Danger.allDangers:
		DrawObj(danger)

	if not MainMenu.isMainMenuOpen:
		gameTimer.timer.Draw()

	EndPoint.Draw()

	Player.Draw()

	MainMenu.Draw()

	PauseMenu.Draw()

	DrawAllGUIObjects()

	if showFps:
		fpsLbl.Draw()

	pg.display.update()


def HandleEvents(event):
	global showFps
	HandleGui(event)

	MainMenu.HandleEvent(event)
	if Settings.isChangingKeyBind:
		Settings.ChangeKeyBind(event)

	PauseMenu.HandleEvent(event)

	Player.HandleEvent(event)

	if event.type == pg.KEYDOWN:
		if event.key == pg.K_F3:
			showFps = not showFps


def Update():
	if not PauseMenu.isGamePaused and MainMenu.IsMainMenuActive():
		for enemey in Enemey.allEnemies:
			enemey.Update()
		
		Camera.Update()
		Player.Update()

		gameTimer.Update()


if __name__ == "__main__":
	floor = Platform((0, Y, width, 20), (lightBlack, darkWhite), name="floor")
	Platform((0, -12, width, 12), (lightBlack, darkWhite), name="roof")
	Platform((-12, 0, 12, height), (lightBlack, darkWhite), name="leftWall")
	Platform((width, 0, 12, height), (lightBlack, darkWhite), name="rightWall")
	centerMarker = GameObject((width // 3, 0, 10, 10))

	gameTimer = GameTimer()
	showFps = False
	fpsLbl = Label((0, 0, 100, 50), (lightBlack, darkWhite), str(fps), textData={"fontSize": 12, "alignText": "left-top"}, drawData={"drawBackground": False, "drawBorder": False}, lists=[])

	while running:
		clock.tick_busy_loop(fps)
		deltaTime = clock.get_time()
		fpsLbl.UpdateText(f"{round(clock.get_fps())}")

		for event in pg.event.get():
			if event.type == pg.QUIT:
				Quit()
			if event.type == pg.KEYDOWN:
				if not Settings.isChangingKeyBind:
					if event.key == pg.K_ESCAPE:
						Quit()

			HandleEvents(event)

		Update()

		DrawLoop()

	pg.quit()