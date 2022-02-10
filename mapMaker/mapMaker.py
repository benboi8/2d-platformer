from PIL import Image
import numpy as np
import os

from fileOps import *

fileName = "map.png"
tempFileName = "temp.png"

workingDir = os.getcwd() + "\\"

screenSize = (1280, 720)


platformColor = (0, 0, 0, 255)


print(workingDir)


with Image.open(workingDir + fileName) as img:
	img.save(workingDir + tempFileName)

	img.close()


rects = []	
with Image.open(workingDir + tempFileName) as img:

	x, y = -1, -1

	while x <= img.width - 2:
		while y <= img.height - 2:
			
			canMoveAcross = img.getpixel((x + 1, y)) == platformColor
			canMoveDown = img.getpixel((x, y + 1)) == platformColor

			px, py = x, y
			
			canMoveAcross = img.getpixel((x + 1, y)) == platformColor
			canMoveDown = img.getpixel((x, y + 1)) == platformColor

			rect = [x + 1, y, img.width, img.height]

			while canMoveAcross:
				while canMoveDown:
					py += 1
					if py >= img.height:
						break
					canMoveDown = img.getpixel((x, py)) == platformColor

				rect[1] = min(py, rect[1])
				rect[3] = rect[1] - y

				px += 1
				canMoveAcross = img.getpixel((px, y)) == platformColor
			
			if rect[2] != img.width or rect[3] != img.height:
				rects.append(rect)
				x = rect[0]

			y += 1

		x += 1
		y = 0

	img.close()

RemoveFile(workingDir + tempFileName)


data = {
	"rects": rects
}
