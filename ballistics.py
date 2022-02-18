import matplotlib.pyplot as plt
import numpy as np

import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")


from GameObjects import *

ts = []

gravity = 0.1


class Gun:
	def __init__(self, rect, color):
		self.rect = pg.Rect(rect)
		self.color = color

		self.center = Vec2(self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2)

	def Draw(self):
		pg.draw.rect(screen, self.color, self.rect)
		pg.draw.line(screen, red, (self.center.x, self.center.y), pg.mouse.get_pos())

		p1 = (self.center.x, self.center.y)
		p2 = (self.center.x + self.rect.w // 2, self.center.y)
		p3 = pg.mouse.get_pos()

		a = Vec2(p2[0] - p1[0], p2[1] - p1[1])
		b = Vec2(p3[0] - p2[0], p3[1] - p2[1])

		self.theta = acos(a.Dot(b) / abs(a.Magnitude() * b.Magnitude()))

		if pg.mouse.get_pos()[1] <= self.center.y:
			pg.draw.arc(screen, blue, self.rect, radians(0), self.theta, 4)
		else:
			pg.draw.arc(screen, blue, self.rect, radians(0), -self.theta, 4)

	def HandleEvents(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				self.Shoot()

	def Shoot(self):
		force = self.center.GetEuclideanDistance(pg.mouse.get_pos())
		self.theta = degrees(self.theta) - 90
		ts.append(Trajectory(self.theta, force, start=[self.center.x, self.center.y]))

		print(self.theta)



class Trajectory:
	def __init__(self, angle, force, start=[100, 100], h=0, color=red):
		self.angle = radians(angle)
		self.color = color

		self.force = force

		self.height = h

		self.start = start

		self.lines = []
		self.reachedGround = False
		self.y = 0

		self.t = -1

	def Draw(self):
		self.Calculate()

		if len(self.lines) > 1:
			pg.draw.lines(screen, self.color, False, self.lines)
			pg.draw.circle(screen, self.color, self.lines[-1], 2)

	def Calculate(self):
		step = 0.01
	
		vx = (self.force * cos(self.angle))
		vy = (self.force * sin(self.angle))

		if not self.reachedGround:
			vx = (vx * cos(self.angle)) * self.t
			vy = (vy * sin(self.angle)) * self.t - gravity

			x = vx * 10

			y = ((vy ** 2) + (0.5 * (gravity ** 2))) / 5

			x += self.start[0]
			y += self.start[1]

			self.lines.append((x, y))

			self.t += step

			if self.t > 0 and y >= self.lines[0][1]:
				self.reachedGround = True


g = Gun((width // 2 - 10, height // 2 - 10, 20, 20), black)


def DrawLoop():
	screen.fill(darkGray)
	
	DrawAllGUIObjects()

	for t in ts:
		t.Draw()

	g.Draw()

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)

	g.HandleEvents(event)

while running:
	clock.tick_busy_loop(fps)
	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False

		HandleEvents(event)

	DrawLoop()
