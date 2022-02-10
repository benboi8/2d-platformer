from PIL import Image
import numpy as np
import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")

from fileOps import *


fileName = "map.png"
tempFileName = "temp.png"

workingDir = os.getcwd() + "\\"

screenSize = (1280, 720)


print(workingDir)


with Image.open(workingDir + fileName) as img:
	img.save(workingDir + tempFileName)

	img.close()


with Image.open(workingDir + tempFileName) as img:

	for x in range(img.width - 1):
		for y in range(img.height - 1):
			
			canMoveAcross = img.getpixel((x + 1, y)) == (0, 0, 0, 255)
			canMoveDown = img.getpixel((x, y + 1)) == (0, 0, 0, 255)

			px, py = x, y
			canMoveDown = img.getpixel((x, y + 1)) == (0, 0, 0, 255)
			while canMoveDown:
				py += 1
				canMoveDown = img.getpixel((x, py)) == (0, 0, 0, 255)

				print(x, y, py)



			# while canMoveAcross:
			# 	while canMoveDown:
			# 		canMoveDown = img.getpixel((x, y + 1)) == (0, 0, 0, 255)
			# 		print(x, y, px, py)
			# 		py += 1



			# 	canMoveAcross = img.getpixel((x + 1, y)) == (0, 0, 0, 255)
			# 	px += 1
			# 	print(x, y, px)

	img.close()



RemoveFile(workingDir + tempFileName)