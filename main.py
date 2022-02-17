# 1 - leader board
# 2 - pause menu
# 3 - goo / water / danger system
# 4 - enemies - event system / left to right collisions for ai
# 5 - sprinting physics
# 6 - level editor


import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")


from GameObjects import *
from GUIShapes import *

allImages = []
allPlaforms = []
allLadders = []
allStairs = []
allCoins = []
allDangers = []
allWater = []
allEnemies = []
allSideWipers = []

allObjs = []


class BoxObj(Box):
	def __init__(self, rect, colors, name="", surface=screen, drawData={}, lists=[allObjs]):
		super().__init__(rect, colors, name, surface, drawData, lists)

	def Move(self, direction):
		if self.name not in ["roof", "leftWall", "rightWall", "floor"]:
			if direction[0]:
				if not player.colliding["right"]:
					self.rect.x -= player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 
			elif direction[1]:
				if not player.colliding["left"]:
					self.rect.x += player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 


class Image(BoxObj):
	def __init__(self, rect, imagePath, name="", surface=screen, lists=[allImages, allObjs]):
		super().__init__(rect, ((0, 0, 0), (0, 0, 0)), name, surface, drawData={"drawBackground": False}, lists=lists)

		self.imagePath = imagePath

		self.resize = False

		self.ScaleImage(pg.image.load(self.imagePath) if self.imagePath != None else None, (self.rect.w, self.rect.h))

	def Draw(self):
		if self.image != None:
			self.surface.blit(self.image, self.rect)

	def ScaleImage(self, image, size):
		if image != None:
			self.image = pg.transform.scale(pg.image.load(self.imagePath), size)
		else:
			self.image = None


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


class Camera(Image):
	def __init__(self, rect, imagePath, borderColor, name="", surface=screen):
		super().__init__(rect, imagePath, name, surface, [])
		self.borderColor = borderColor
		self.isPlayerInCenter = False
		self.defaultPos = (self.rect.x, self.rect.y)

	def Draw(self):
		self.DrawBorder()

	def Move(self, pos):
		self.rect.x = pos[0]
		self.rect.y = pos[1]

	def Update(self, player):
		if player.rect.x >= centerMarker.rect.x:
			self.isPlayerInCenter = True
		elif player.rect.x < centerMarker.rect.x:
			self.isPlayerInCenter = False
		else:
			self.Move(self.defaultPos)

		if self.isPlayerInCenter:
			for obj in allObjs:
				obj.Move(player.direction)


class Collider:
	def __init__(self, rect, direction):
		self.rect = pg.Rect(rect)
		self.direction = direction

	def CollideCheck(self, rect):
		return self.rect.colliderect(rect)

	def Draw(self, col=blue):
		pg.draw.rect(screen, blue, self.rect)


class Platform(BoxObj):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allPlaforms, allObjs]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[])

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		self.image.Draw()


class Stairs:
	def __init__(self, rect, colors, stepRect, imagePath=None, name="", surface=screen, drawData={}, lists=[allObjs, allStairs]):
		self.rect = pg.Rect(rect)

		self.backgroundColor = colors[0]
		self.borderColor = colors[1]

		self.stepRect = stepRect

		AddToListOrDict(lists, self)

		self.steps = [Platform((self.rect.x + (i * self.stepRect[0]), (self.rect.y - (i * self.stepRect[2] * self.stepRect[3])) + (self.rect.h if self.stepRect[3] == 1 else 0), self.stepRect[0], self.stepRect[1]), colors, imagePath, drawData={"borderWidth": 1}) for i in range(self.rect.w // self.stepRect[0])]

	def Move(self, direction):
		if direction[0]:
			if not player.colliding["right"]:
				self.rect.x -= player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 
		elif direction[1]:
			if not player.colliding["left"]:
				self.rect.x += player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 

	def Draw(self):
		pg.draw.rect(screen, red, self.rect)
		if self.stepRect[3] == -1:
			pg.draw.aaline(screen, black, (self.rect.x, self.rect.y), (self.rect.x + self.rect.w, self.rect.y + self.rect.h))
		if self.stepRect[3] == 1:
			pg.draw.aaline(screen, black, (self.rect.x, self.rect.y + self.rect.h), (self.rect.x + self.rect.w, self.rect.y))


class Ladder(BoxObj):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allLadders, allObjs]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[])

		numOfRungs = self.rect.h // 20
		spacing = self.rect.h // numOfRungs
		self.rungs = [pg.Rect(self.rect.x, self.rect.y + (i * spacing), self.rect.w, 4) for i in range(numOfRungs)]

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()		
		
		self.image.Draw()

		for rung in self.rungs:
			rung.x = self.rect.x
			pg.draw.rect(self.surface, self.borderColor, rung)


class Entity(Box): 
	def __init__(self, rect, colors, imagePath=None, data={}, name="", surface=screen, drawData={}, inputData={}, lists=[]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[])

		self.ogBorderColor = self.borderColor

		#                                       left                                            right                                                                            up                                              down
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


class Player(Entity):
	def __init__(self, rect, colors, imagePath=None, data={}, name="", surface=screen, drawData={}, inputData={}, lists=[]):
		super().__init__(rect, colors, imagePath, data, name, surface, drawData, inputData, lists)
		self.startingRect = rect

		self.keyBinds = {"right": pg.K_d, "left": pg.K_a, "jump": pg.K_SPACE, "crouch": pg.K_LCTRL, "climbUp": pg.K_w, "climbDown": pg.K_s, "sprint": K_LSHIFT}

		# get from player.json file
		self.moveSpeed = 5
		self.sprintSpeedMulti = 2
		self.movementSpeed = self.moveSpeed
		self.isSprinting = False
		self.gravity = 7
		self.jumpForce = 10
		self.grounded = False
		self.isJumping = False
		self.holdingJump = False
		self.climbing = False
		self.crouched = False
		self.crouchData = {"height": self.rect.h // 1.5, "moveSpeed": 3}
		self.height = self.rect.h
		self.ladder = None
		self.climbSpeed = 6
		self.climbFallSpeed = 1
		self.climbDirection = -1
		self.dead = False
		self.won = False
		
		self.enemiesKilled = 0
		self.coins = 0

		self.coinCounter = Label((self.rect.x + self.rect.w // 2 - 15, self.rect.y - 30, 30, 20), colors, "0", textData={"fontSize": 15}, drawData={"drawBackground": True, "drawBorder": False})

		self.deadMessageBox = MessageBox((width // 2 - 200, height // 2 - 100, 400, 200), (lightBlack, darkWhite, lightBlue), confirmButtonData={"text": "Quit", "rect": pg.Rect(width // 2 - 190, height // 2 + 35, 185, 35), "onClick": QuitToMenu}, cancelButtonData={"onClick": self.Restart, "text": "Restart", "rect": pg.Rect(width // 2, height // 2 + 35, 190, 35)}, messageBoxData={"rect": pg.Rect(width // 2 - 190, height // 2 - 90, 380, 100)}, lists=[])
		self.dead = False

		self.winningLabel = MessageBox((width // 2 - 200, height // 2 - 100, 400, 200), (lightBlack, darkWhite, lightBlue), cancelButtonData={"text": "Next Level", "rect": pg.Rect(width // 2, height // 2 + 35, 190, 35), "onClick": LoadNextLevel}, confirmButtonData={"text": "Quit to menu", "onClick": QuitToMenu, "rect": pg.Rect(width // 2 - 190, height // 2 + 35, 185, 35)}, messageBoxData={"rect": pg.Rect(width // 2 - 190, height // 2 - 90, 380, 100)}, lists=[])

		self.direction = [False, False]

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		self.image.Draw()

		self.coinCounter.UpdateRect((self.rect.x + self.rect.w // 2 - 15, self.rect.y - 30, 30, 20))

		if self.dead:
			self.deadMessageBox.Draw()

		if self.won:
			self.winningLabel.Draw()

	def HandleEvent(self, event):
		if not self.dead and not self.won:
			if event.type == pg.KEYDOWN:
				if event.key == self.keyBinds.get("right"):
					self.direction[0] = True
				
				if event.key == self.keyBinds.get("left"):
					self.direction[1] = True

				if event.key == self.keyBinds.get("jump"):
					if self.grounded:
						self.isJumping = True
					self.holdingJump = True

				if event.key == self.keyBinds.get("crouch"):
					self.crouched = True

				if event.key == self.keyBinds.get("climbUp"):
					self.climbing = True
					self.climbDirection = -1
				
				if event.key == self.keyBinds.get("climbDown"):
					self.climbing = True
					self.climbDirection = 1

				if event.key == self.keyBinds.get("sprint"):
					self.isSprinting = True

		if event.type == pg.KEYUP:
			if event.key == self.keyBinds.get("right"):
				self.direction[0] = False
			
			if event.key == self.keyBinds.get("left"):
				self.direction[1] = False

			if event.key == self.keyBinds.get("jump"):
				self.holdingJump = False

			if event.key == self.keyBinds.get("crouch"):
				self.crouched = False

			if event.key == self.keyBinds.get("climbUp"):
				self.climbing = False
			
			if event.key == self.keyBinds.get("climbDown"):
				self.climbing = False

			if event.key == self.keyBinds.get("sprint"):
				self.isSprinting = False

		if self.dead:
			self.deadMessageBox.HandleEvent(event)

		if self.won:
			self.winningLabel.HandleEvent(event)

	def Update(self):
		if not self.dead and not self.won:
			self.Collide()
			
			if self.direction != None:
				self.Move()

			self.Jump()
			
			if self.holdingJump:
				if self.grounded:
					self.isJumping = True

			self.Climb()
			self.Crouch()

			if not self.isJumping:
				if self.ladder == None:
					# gravity
					# [left, right], [up, down]
					if self.isAffectedByGravity:
						self.ApplyGravity()

			if self.rect.x >= ep.rect.x:
				self.Win()

	def Win(self):
		self.won = True
		ts.Stop()
		self.winningLabel.messageBox.UpdateText(f"You have beat the level!")
		self.isJumping = False
		self.direction = [False, False]

	def Climb(self):
		if self.ladder != None:
			if self.climbing:
				canClimb = False
				if self.climbDirection == -1:
					if self.rect.y + self.rect.h > self.ladder.rect.y:
						canClimb = True
				
				if self.climbDirection == 1:
					if self.rect.y + self.rect.h < self.ladder.rect.y + self.ladder.rect.h:
						canClimb = True

				if canClimb:
					# self.rect.y += self.climbSpeed * self.climbDirection
					self.ApplyForce(self.climbSpeed, [[False, False], [True if self.climbDirection == -1 else False, True if self.climbDirection == 1 else False]])

			else:
				# self.rect.y += self.climbFallSpeed
				self.ApplyForce(self.climbFallSpeed, [[False, False], [False, True]])

	def Crouch(self):
		if not self.climbing:
			if self.crouched:
				self.rect.h = self.crouchData["height"]
				self.movementSpeed = self.crouchData["moveSpeed"]
			else:
				if self.rect.h != self.height:
					for i in range(3):
						if not self.colliding["up"]:
							self.rect.h = self.height
							self.movementSpeed = self.moveSpeed
						else:
							self.rect.h = self.crouchData["height"]
							self.movementSpeed = self.crouchData["moveSpeed"]

						self.Collide()

	def Jump(self):
		if self.isJumping:
			self.j += 0.1
			self.ApplyForce(self.jumpForce, [[False, False], [True, False]])

			if self.j >= 1 or self.colliding["up"]:
				self.j = 0
				self.isJumping = False

	def Move(self):
		if not cam.isPlayerInCenter:
			if self.direction[0]:
				if not self.colliding["right"]:
					self.ApplyForce(self.movementSpeed * (self.sprintSpeedMulti if self.isSprinting else 1), [[False, True], [False, False]])
			
			if self.direction[1]:
				if not self.colliding["left"]:
					self.ApplyForce(self.movementSpeed * (self.sprintSpeedMulti if self.isSprinting else 1), [[True, False], [False, False]])

	def Collide(self):
		self.UpdateColliders([pg.Rect(self.rect.x - 2, self.rect.y, 4, self.rect.h), pg.Rect(self.rect.x + self.rect.w - 2, self.rect.y, 4, self.rect.h), pg.Rect(self.rect.x, self.rect.y - 2, self.rect.w, 4), pg.Rect(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4)])

		# platform
		for collider in self.colliders:
			for platform in allPlaforms:
				if collider.CollideCheck(platform.rect):
					self.colliding[collider.direction] = True

					if collider.direction == "up" and self.colliding["up"]:
						self.rect.y = platform.rect.y + platform.rect.h
					
					if collider.direction == "down" and self.colliding["down"]:
						self.rect.y = platform.rect.y - self.rect.h

		# water
			for water in allWater:
				if water.rect.x <= self.rect.x and water.rect.x + water.rect.w >= self.rect.x + self.rect.w:
					if collider.CollideCheck(water.rect):
						self.Kill()

		if self.colliding["down"]:
			self.grounded = True
		else:
			self.grounded = False

		# ladders
		self.ladder = None
		for ladder in allLadders:
			for collider in self.colliders:
				if collider.CollideCheck(ladder.rect):
					self.ladder = ladder
					break

		# stairs
		self.stairs = None
		for stairs in allStairs:
			for collider in self.colliders:
				if collider.CollideCheck(stairs.rect):
					self.stairs = stairs
					break

		if self.stairs != None:
			self.colliding["left"] = False
			self.colliding["right"] = False


		# coins
		for coin in allCoins:
			for collider in self.colliders:
				if collider.CollideCheck(coin.rect):
					self.CollectCoin(coin)

	def Kill(self):
		self.dead = True

		ts.Stop()

		self.deadMessageBox.messageBox.UpdateText("You have died!\nPress the restart button to restart the level.\nPress the quit button to exit.")

	def EnemeyKilled(self, value):
		self.enemiesKilled += 1
		self.CollectCoin(value)

	def Restart(self):
		ts.Stop()
		ts.Reset()
		self.ResetPosition()
		self.dead = False
		self.won = False

	def ResetPosition(self):
		self.rect = pg.Rect(self.startingRect)

	def CollectCoin(self, value=None):
		if type(value) == int:
			self.coins += value
		else:
			self.coins += value.Collect()
		
		self.coinCounter.UpdateText(str(self.coins))


class Coin(BoxObj):
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
		if self in allCoins:
			allCoins.remove(self)
			return self.value
		return 0


class TimeScore:
	def __init__(self):
		self.startTime = dt.datetime.now()

		self.hours = 0
		self.minutes = 0

		self.timer = Label((width - 210, 10, 200, 50), (lightBlack, darkWhite), drawData={"roundedCorners": True, "roundness": 2}, textData={"fontSize": 30})

		self.paused = False
		self.stopped = False

	def Reset(self):
		self.paused = False
		self.stopped = False
		self.startTime = dt.datetime.now()

	def Pause(self):
		self.paused = not self.paused

	def Stop(self):
		self.stopped = True

	def Update(self):
		if not self.paused and not self.stopped:
			self.difference = dt.datetime.now() - self.startTime

			if self.difference.seconds % 60 == 0:
				self.minutes = self.difference.seconds // 60

			if self.difference.seconds % 3600 == 0:
				self.hours = self.difference.seconds // 3600

			msg = f"{self.hours}:{self.minutes}:{self.difference.seconds}:{str(self.difference.microseconds)[0]}"
			self.timer.UpdateText(msg)
			return msg


class EndPoint(BoxObj):
	def __init__(self, rect, colors, imagePath=None):
		super().__init__(rect, colors)
		self.image = Image(rect, imagePath)


	def Draw(self):
		pg.draw.rect(screen, self.backgroundColor, self.rect)
		pg.draw.rect(screen, self.backgroundColor, (self.rect.x - 5, self.rect.y, 5, 100))
		DrawRectOutline(self.borderColor, self.rect)
		DrawRectOutline(self.borderColor, pg.Rect(self.rect.x - 5, self.rect.y, 5, 100))

		self.image.Draw()


class Danger(BoxObj):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allObjs, allDangers]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(rect, imagePath, lists=[])


class Water(Danger):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allObjs, allDangers, allWater]):
		super().__init__(rect, colors, imagePath, name, surface, drawData, lists)

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		self.image.Draw()


class Enemey(Entity):
	def __init__(self, rect, colors, imagePath=None, data={}, name="", surface=screen, drawData={}, inputData={}, lists=[allEnemies, allObjs, allDangers]):
		super().__init__(rect, colors, imagePath, data, name, surface, drawData, inputData, lists)

		self.isAffectedByGravity = data.get("isAffectedByGravity", False)

		self.isMovingLeft = True
		# score value
		self.value = 1

		#                                          left                                                             right                                                                                      up                                                           down
		self.colliderRects = [pg.Rect(self.rect.x - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x + self.rect.w - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x - 2, self.rect.y - 6, self.rect.w + 4, 12), pg.Rect(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4)]

		self.movementSpeed = data.get("moveSpeed", 2)
	
	def Move(self, direction):
		if direction[0]:
			if not player.colliding["right"]:
				self.rect.x -= player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 
		elif direction[1]:
			if not player.colliding["left"]:
				self.rect.x += player.movementSpeed * (player.sprintSpeedMulti if player.isSprinting else 1) 

		if self.isMovingLeft:
			self.ApplyForce(self.movementSpeed, [[True, False], [False, False]])
		else:
			self.ApplyForce(self.movementSpeed, [[False, True], [False, False]])

	def Collide(self):
		self.UpdateColliders([pg.Rect(self.rect.x - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x + self.rect.w - 1, self.rect.y + 6, 2, self.rect.h - 10), pg.Rect(self.rect.x + 2, self.rect.y, self.rect.w - 4, 8), pg.Rect(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4)])

		for collider in self.colliders:
			if not player.dead:
				if collider.direction == "up":
					if collider.CollideCheck(player.rect):
						if not self.dead:
							player.EnemeyKilled(self.value)
							self.Kill()
							return

		for collider in self.colliders:
			for platform in allPlaforms:
				if collider.CollideCheck(platform.rect):
					self.colliding[collider.direction] = True

			for enemey in allEnemies:
				if not enemey == self:
					if collider.CollideCheck(enemey.rect):
						self.colliding[collider.direction] = True

			if collider.CollideCheck(player.rect):
				player.Kill()

	def Update(self):
		if not self.dead:
			self.Collide()

			if self.colliding["left"]:
				self.isMovingLeft = False

			elif self.colliding["right"]:
				self.isMovingLeft = True

			if self.isAffectedByGravity:
				self.ApplyGravity()

			if not cam.isPlayerInCenter:
				self.Move([False, False])

	def Kill(self):
		self.dead = True

		if self in allDangers:
			allDangers.remove(self)
		if self in allEnemies:
			allEnemies.remove(self)


def DrawObj(obj):
	if obj.rect.colliderect(cam.rect):
		obj.Draw()


def DrawLoop():
	screen.fill(darkGray)

	# for stairs in allStairs:
	# 	if stairs.rect.colliderect(cam.rect):
	# 		stairs.Draw()
	
	ep.Draw()

	for image in allImages:
		DrawObj(image)

	for platform in allPlaforms:
		DrawObj(platform)
	
	for ladder in allLadders:
		DrawObj(ladder)

	for coin in allCoins:
		DrawObj(coin)

	for danger in allDangers:
		DrawObj(danger)

	player.Draw()

	
	cam.Draw()

	# pg.draw.rect(screen, red, centerMarker.rect)
	
	DrawAllGUIObjects()

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)

	player.HandleEvent(event)


def Update():
	player.Update()

	cam.Update(player)

	for enemey in allEnemies:
		enemey.Update()

	ts.Update()


def Quit():
	global running
	running = False

# create menu
def QuitToMenu():
	Quit()


def LoadNextLevel():
	print("Next Level")



# background = Image((0, 0, width, height), "background.jpg")

cam = Camera((0, 0, width, height), None, darkWhite)


fpsLbl = Label((0, 0, 100, 50), (lightBlack, darkWhite), str(fps), textData={"fontSize": 12, "alignText": "left-top"}, drawData={"drawBackground": False, "drawBorder": False})

floor = Platform((0, height - 20, width, 20), (lightBlack, darkWhite), name="floor")
Platform((0, -12, width, 12), (lightBlack, darkWhite), name="roof")
Platform((-12, 0, 12, height), (lightBlack, darkWhite), name="leftWall")
Platform((width, 0, 12, height), (lightBlack, darkWhite), name="rightWall")
centerMarker = GameObject((width // 2, 0, 10, 10))

y = height - floor.rect.h

# load with json
# ------------------------------------------ start of level ------------------------------------------
Platform((200, y - 50, 100, 50), (lightBlack, darkWhite))
Platform((700, y - 70, 200, 70), (lightBlack, darkWhite))
Platform((800, y - 120, 100, 50), (lightBlack, darkWhite))
Platform((300, y - 120, 200, 20), (lightBlack, darkWhite))
Platform((510, y - 180, 150, 20), (lightBlack, darkWhite))
Platform((690, y - 260, 150, 20), (lightBlack, darkWhite))
Platform((1100, y - 200, 50, 200), (lightBlack, darkWhite))
Platform((900, y - 60, 50, 60), (lightBlack, darkWhite))
Platform((1050, y - 100, 50, 100), (lightBlack, darkWhite))
Ladder((1150, y - 500, 50, 500), (lightBlack, darkWhite))
Platform((1200, y - 500, 20, 465), (lightBlack, darkWhite))

Stairs((1300, y - 110, 360, 110), (lightBlack, darkWhite), (10, 20, 3, 1))
Platform((1660, y - 110, 20, 110), (lightBlack, darkWhite))

Platform((1200, y - 500, 100, 20), (lightBlack, darkWhite))
Stairs((1300, y - 590, 300, 90), (lightBlack, darkWhite), (10, 20, 3, 1))
Platform((1600, y - 590, 100, 20), (lightBlack, darkWhite))
Stairs((1700, y - 590, 600, 180), (lightBlack, darkWhite), (10, 20, 3, -1))
Platform((2300, y - 410, 300, 20), (lightBlack, darkWhite))
Platform((2600, 0, 20, 310), (lightBlack, darkWhite))

Coin((235, y - 90, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})
Coin((385, y - 160, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})
Coin((565, y - 220, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})
Coin((755, y - 300, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})
Coin((755, y - 110, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})
Coin((1060, y - 145, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})
Coin((1640, y - 630, 30, 35), (ChangeColorBrightness(yellow, 50), yellow), drawData={"borderWidth": 3})

Water((2300, y - 3, 300, 20), (lightBlue, lightBlue))

Enemey((350, floor.rect.y - 50, 20, 50), (ChangeColorBrightness(lightRed, 60), lightRed))
Enemey((380, floor.rect.y - 50, 20, 50), (ChangeColorBrightness(lightRed, 60), lightRed))

ep = EndPoint((2450, y - 510, 30, 30), (lightBlack, darkWhite))
# ------------------------------------------ end of level ------------------------------------------

player = Player((10, y - 55, 20, 50), (lightBlack, darkWhite))

ts = TimeScore()


while running:
	clock.tick_busy_loop(fps)
	deltaTime = clock.get_time()
	fpsLbl.UpdateText(str(round(clock.get_fps(), 1)))

	for event in pg.event.get():
		if event.type == pg.QUIT:
			Quit()
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				Quit()

		HandleEvents(event)

	Update()

	DrawLoop()
