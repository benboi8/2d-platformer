import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from math import *

g = 9.81
launchSpeed = 10
launchAngle = 30
initialHeight = 0

t = 0
step = 0.01

Vx = launchSpeed * cos(launchAngle)
Vy = launchSpeed * sin(launchAngle)
x, y1, y2 = 0, 0, 0

xs, ys1, ys2 = [], [], []

while t <= 1:

	x = Vx * t
	y1 = (initialHeight + x * tan(launchAngle) - (g * x ** 2)) / ((2 * launchSpeed ** 2) * (cos(launchAngle) ** 2))
	y2 = x * tan(launchAngle) - (g * (x ** 2) / 2 * (launchSpeed ** 2) * (cos(launchAngle) ** 2))

	xs.append(x)
	ys1.append(y1)
	ys2.append(y2)

	t += step

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(xs, ys1);  # Plot some data on the axes.
ax.plot(xs, ys2);  # Plot some data on the axes.


plt.show()


