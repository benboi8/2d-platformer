# fix ladders - drawing, physics
# fix crouch/jump climbing up platforms - fixed maybe
# fix collisions - left/right

import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")

from GameObjects import *

allImages = []
allPlaforms = []
allLadders = []

class Image(Box):
	def __init__(self, rect, imagePath, name="", surface=screen, lists=[allImages]):
		super().__init__(rect, ((0, 0, 0), (0, 0, 0)), name, surface, drawData={"drawBackground": False}, lists=lists)

		self.imagePath = imagePath

		self.ScaleImage(pg.image.load(self.imagePath), (self.rect.w, self.rect.h))

	def Draw(self):
		self.surface.blit(self.image, self.rect)

	def ScaleImage(self, image, size):
		self.image = pg.transform.scale(pg.image.load(self.imagePath), size)


class Camera(Button, Image):
	def __init__(self, rect, colors, onClick=None, onClickArgs=[], text="", name="", surface=screen, drawData={}, textData={}, inputData={}, lists=[allButtons]):
		def __init__(self, rect, imagePath, colors, onClick=None, onClickArgs=[], text="", inputData={}, name="", surface=screen)


class Collider:
	def __init__(self, x, y, w, h, direction):
		self.rect = pg.Rect(x, y, w, h)
		self.direction = direction

	def CollideCheck(self, rect):
		return self.rect.colliderect(rect)


class Platform(Box):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allPlaforms]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[]) if imagePath != None else None

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		if self.image != None:
			self.image.Draw()


class Ladder(Box):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, lists=[allLadders]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[]) if imagePath != None else None

		self.rungs = [pg.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.h // 10 - 2, self.rect.w, 4) for i in range(self.rect.h // 20)]

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()		
		
		if self.image != None:
			self.image.Draw()

		for rung in self.rungs:
			pg.draw.rect(self.surface, self.borderColor, rung)


class Player(Box):
	def __init__(self, rect, colors, imagePath=None, name="", surface=screen, drawData={}, inputData={}, lists=[]):
		super().__init__(rect, colors, name, surface, drawData, lists)

		self.image = Image(self.rect, imagePath, lists=[]) if imagePath != None else None

		self.ogBorderColor = self.borderColor

		self.keyBinds = {"right": pg.K_d, "left": pg.K_a, "jump": pg.K_SPACE, "crouch": pg.K_LCTRL, "climbUp": pg.K_w, "climbDown": pg.K_s, "sprint": K_LSHIFT}

		self.colliders = [Collider(self.rect.x - 2, self.rect.y, 4, self.rect.h, "left"), Collider(self.rect.x + self.rect.w - 2, self.rect.y, 4, self.rect.h, "right"), Collider(self.rect.x, self.rect.y - 2, self.rect.w, 4, "up"), Collider(self.rect.x, self.rect.y + self.rect.h - 2, self.rect.w, 4, "down")]

		self.colliding = {"left": False, "right": False, "up": False, "down": False}

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
		self.climbSpeed = 4
		self.climbDirection = -1
		self.j = 0

		self.direction = [False, False]

	def Draw(self):
		self.DrawBackground()
		self.DrawBorder()

		if self.image != None:
			self.image.Draw()

	def HandleEvent(self, event):
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

	def Update(self):
		self.Collide()
		
		if self.direction != None:
			self.Move()

		self.Jump()
		
		if self.holdingJump:
			if self.grounded:
				self.isJumping = True

		if self.climbing:
			if self.ladder != None:
				self.rect.y += self.climbSpeed * self.climbDirection
		else:
			self.Crouch()

		if not self.isJumping:
			if self.ladder == None:
				# gravity
				# [left, right], [up, down] 
				self.ApplyForce(self.gravity, [[False, False], [False, True]])

	def Crouch(self):
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

	def ApplyForce(self, magnitude, direction):
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

	def Move(self):
		if self.direction[0]:
			if not self.colliding["right"]:
				self.rect.x += self.movementSpeed * (self.sprintSpeedMulti if self.isSprinting else 1)
		
		if self.direction[1]:
			if not self.colliding["left"]:
				self.rect.x -= self.movementSpeed * (self.sprintSpeedMulti if self.isSprinting else 1)

	def Collide(self):
		self.colliders[0].rect = pg.Rect(self.rect.x - 2, self.rect.y + self.movementSpeed // 2, 4, self.rect.h - self.movementSpeed)
		self.colliders[1].rect = pg.Rect(self.rect.x + self.rect.w - 2, self.rect.y + self.movementSpeed // 2, 4, self.rect.h - self.movementSpeed)
		self.colliders[2].rect = pg.Rect(self.rect.x + self.movementSpeed // 2, self.rect.y - 2, self.rect.w - self.movementSpeed, 4)
		self.colliders[3].rect = pg.Rect(self.rect.x + self.movementSpeed // 2, self.rect.y + self.rect.h - self.gravity // 2, self.rect.w - self.movementSpeed, self.gravity)

		self.colliding = {"left": False, "right": False, "up": False, "down": False}

		for platform in allPlaforms:
			for collider in self.colliders:
				if collider.CollideCheck(platform.rect):
					self.colliding[collider.direction] = True

					if collider.direction == "up" and self.colliding["up"]:
						self.rect.y = platform.rect.y + platform.rect.h
					
					if collider.direction == "down" and self.colliding["down"]:
						self.rect.y = platform.rect.y - self.rect.h

		if self.colliding["down"]:
			self.grounded = True
		else:
			self.grounded = False

		# ladders
		# self.ladder = None
		# for ladder in allLadders:
		# 	for collider in self.colliders:
		# 		if collider.CollideCheck(ladder.rect):
		# 			self.ladder = ladder
		# 			break


def DrawLoop():
	screen.fill(darkGray)

	DrawAllGUIObjects()

	for image in allImages:
		image.Draw()

	for platforms in allPlaforms:
		platforms.Draw()
	
	for ladder in allLadders:
		ladder.Draw()
	
	player.Draw()

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)

	player.HandleEvent(event)


def Update():
	player.Update()


background = Image((0, 0, width, height), "background.jpg")


floor = Platform((0, height // 2 + 350, width, 100), (lightBlack, darkWhite))
Platform((0, -2, width, 2), (lightBlack, darkWhite))
Platform((-2, 0, 2, height), (lightBlack, darkWhite))
Platform((width, 0, 2, height), (lightBlack, darkWhite))

Platform((200, height // 2 + 300, 100, 50), (lightBlack, darkWhite))
Platform((700, height // 2 + 300 - 20, 200, 70), (lightBlack, darkWhite))
Platform((800, height // 2 + 300 - 70, 100, 50), (lightBlack, darkWhite))
Platform((300, 290 + 300, 200, 20), (lightBlack, darkWhite))
Platform((500, 230 + 300, 150, 20), (lightBlack, darkWhite))
Platform((650, 190 + 300, 150, 20), (lightBlack, darkWhite))
Platform((1100, height // 2 - 150 + 300, 50, 200), (lightBlack, darkWhite))
Platform((900, height // 2 - 10 + 300, 50, 60), (lightBlack, darkWhite))
Platform((1050, height // 2 - 50 + 300, 50, 100), (lightBlack, darkWhite))
Ladder((1150, height // 2 - 150 + 300, 50, 200), (lightBlack, darkWhite))

player = Player((10, height // 2 - 5, 20, 50), (lightBlack, darkWhite))

while running:
	clock.tick_busy_loop(fps)
	deltaTime = clock.get_time()

	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False

		HandleEvents(event)

	Update()

	DrawLoop()