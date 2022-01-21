import matplotlib.pyplot as plt
import numpy as np

import os
import sys

# os.chdir(sys.path[0])
# sys.path.insert(1, "P://Python Projects/assets/")


from GameObjects import *

ts = []

gravity = 1

class Trajectory:
	def __init__(self, angle, force, start=[100, 100], h=0):
		self.angle = radians(angle)

		self.force = force

		self.height = h

		self.start = start

		self.lines = []
		self.reachedGround = False

		self.t = -1

	def Draw(self):
		self.Calculate()

		if len(self.lines) > 1:
			pg.draw.lines(screen, red, False, self.lines)
			pg.draw.circle(screen, red, self.lines[-1], 3)

	def Calculate(self):
		step = 0.01
	
		vx = (self.force * cos(self.angle))
		vy = (self.force * sin(self.angle))

		if not self.reachedGround:
			vx = (vx * cos(self.angle)) * self.t
			vy = (vy * sin(self.angle)) * self.t - gravity

			x = vx * cos(self.angle)

			y = (vy ** 2) + (0.5 * (gravity ** 2))

			x += self.start[0]
			y += self.start[1]

			self.lines.append((x, y))

			self.t += step

			if self.t >= 1 and y >= self.lines[0][1]:
				self.reachedGround = True

ts.append(Trajectory(0, 60, [100, 100], 0))
ts.append(Trajectory(10, 50, [100, 150], 0))
ts.append(Trajectory(20, 40, [100, 200], 0))
ts.append(Trajectory(30, 30, [100, 250], 0))
ts.append(Trajectory(40, 30, [100, 300], 0))
ts.append(Trajectory(50, 10, [300, 100], 0))
ts.append(Trajectory(60, 10, [600, 100], 0))



def DrawLoop():
	screen.fill(darkGray)
	
	DrawAllGUIObjects()

	for t in ts:
		t.Draw()

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)


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

# # plot
# fig, ax = plt.subplots()


# x = []
# y = []

# for point in t.lines:
# 	x.append(point[0])
# 	y.append(point[1])

# ax.plot(x, y, linewidth=2.0)


# plt.show()