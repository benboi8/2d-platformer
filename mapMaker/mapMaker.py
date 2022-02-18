from PIL import Image
import numpy as np
import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")

from fileOps import *

fileName = "maptest.png"
tempFileName = "temp.png"

workingDir = os.getcwd() + "\\"

screenSize = (1280, 720)


platformColor = (0, 0, 0, 255)
emptyColor = (255, 255, 255, 255)

print(workingDir)


with Image.open(workingDir + fileName) as img:
	img.save(workingDir + tempFileName)

	img.close()


rects = []	
img = Image.open(workingDir + tempFileName)



x, y = 0, 0
img_width, img_height = img.width - 1, img.height - 1
rects = []
while x < img_width:

	while y < img_height:

		pointer_x, pointer_y = x, y

		if img.getpixel((pointer_x, pointer_y)) == platformColor:
			rect_start = [pointer_x, pointer_y]
			rect_end = [100000000, 100000000]

			# loop through x
			reached_end_width = False
			while not reached_end_width:

				# loop through y
				reached_end_height = False
				while not reached_end_height:

					# check y below pixel
					pointer_y += 1
					if pointer_y <= img_width:
						if img.getpixel((pointer_x, pointer_y)) != platformColor:
							reached_end_height = True

							rect_end[1] = min(rect_end[1], pointer_y - 1)

				# check x right of pixel
				pointer_x += 1
				pointer_y = y
				reached_end_height = False
				if pointer_x <= img_width:
					if img.getpixel((pointer_x, pointer_y)) != platformColor:
						reached_end_width = True
						rect_end[0] = pointer_x - 1

			# add rect to list
			if reached_end_width:
				if len(rects) == 0:
					rects.append([rect_start[0], rect_start[1], rect_end[0], rect_end[1]])
					x = rect_start[0]
				else:	
					for r in rects:
						if rect_start[0] >= r[0] and rect_start[1] >= r[1] and rect_end[0] <= r[2] and rect_end[1] <= r[3]:
							rects.append([rect_start[0], rect_start[1], rect_end[0], rect_end[1]])
							x = rect_start[0]

		y += 1

	x += 1
	y = 0


print(rects)

# x, y = -1, -1

# while x <= img.width - 2:
# 	while y <= img.height - 2:
		
# 		px, py = x, y
		
# 		canMoveAcross = img.getpixel((x + 1, y)) == platformColor
# 		canMoveDown = img.getpixel((x, y + 1)) == platformColor

# 		rect = [x + 1, 10000, img.width, img.height]

# 		while canMoveAcross:
# 			while canMoveDown:
# 				py += 1
# 				if py >= img.height:
# 					break
# 				canMoveDown = img.getpixel((x, py)) == platformColor

# 			# fix width and height
# 			rect[1] = min(py, rect[1])
# 			rect[3] = rect[1] - y


# 			px += 1
# 			canMoveAcross = img.getpixel((px, y)) == platformColor

# 		# rect[2] = px
# 		if rect[2] != img.width or rect[3] != img.height:
# 			rects.append(rect)
# 			x = rect[0]

# 		y += 1

# 	x += 1
# 	y = 0

img.close()

RemoveFile(workingDir + tempFileName)

# process output
# print(rects[0])

# data = {
	# "rects": rects
# }
