# - hold ctrl to lock width and height together
# - add camera to expand level design
# - add loading of levels
# - add end point
# - add player start



import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")


from GameObjects import *
from GUIShapes import *

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/2d platformer/")
from main import *


show_types = False
show_rects = False


def DrawObj(obj):
	if obj.rect.colliderect(Camera.rect):
		obj.Draw()


def DrawLoop():
	screen.fill(darkGray)

	for img in Image.allImages:
		img.Draw()

	for platform in Platform.allPlatforms:
		DrawObj(platform)
	
	for ladder in Ladder.allLadders:
		DrawObj(ladder)

	for coin in Coin.allCoins:
		DrawObj(coin)

	for danger in Danger.allDangers:
		DrawObj(danger)
	
	Cursor.Draw()

	if show_types or show_rects:
		for obj in level_objs:
			font = pg.font.SysFont("arial", 15)
			if show_types:
				textSurfaces = [font.render(str(obj.__class__.__name__), True, white, black)]
			
			if show_rects:
				textSurfaces = []
				textSurfaces.append(font.render(f"W: {obj.rect.w}, H: {obj.rect.h}", True, white, black))
				textSurfaces.append(font.render(f"X: {obj.rect.x}, Y: {obj.rect.y}", True, white, black))
			
			if show_types and show_rects:
				textSurfaces = []
				textSurfaces.append(font.render(f"W: {obj.rect.w}, H: {obj.rect.h}", True, white, black))
				textSurfaces.append(font.render(f"X: {obj.rect.x}, Y: {obj.rect.y}", True, white, black))
				textSurfaces.append(font.render(f"Type:{obj.__class__.__name__}", True, white, black))

			for i, textSurface in enumerate(textSurfaces):
				if textSurface.get_width() >= obj.rect.w or textSurface.get_height() >= obj.rect.h:
					rect = (obj.rect.x + obj.rect.w // 2 - textSurface.get_width() // 2, obj.rect.y - textSurface.get_height() - (textSurface.get_height() * i))
				else:
					rect = (obj.rect.x + obj.rect.w // 2 - textSurface.get_width() // 2, obj.rect.y + obj.rect.h // 2 - textSurface.get_height() // 2 - (textSurface.get_height() * i))
				screen.blit(textSurface, rect)

	DrawAllGUIObjects()

	pg.display.update()


def HandleEvents(event):
	global showFps, show_types, show_rects
	HandleGui(event)
	Cursor.HandleEvent(event)

	if event.type == pg.KEYDOWN:
		if event.key == pg.K_LALT:
			show_types = not show_types
		if event.key == pg.K_SPACE:
			show_rects = not show_rects


def Update():
	pass


class Cursor:
	class ResizeButton:
		def __init__(self, radius, colors, directions=""):
			self.pos = None
			self.radius = radius
			self.borderColor = colors[0]
			self.inactiveColor = colors[1]
			self.activeColor = colors[2]
			self.currentColor = self.inactiveColor
			self.directions = directions
			self.is_clicked = False

		def Draw(self):
			if self.pos != None:
				pg.draw.circle(screen, self.borderColor, self.pos, self.radius)
				pg.draw.circle(screen, self.currentColor, self.pos, self.radius - 1)

		def HandleEvent(self, event):
			if self.is_clicked:
				self.ResizeRect()

			if self.pos != None:
				if event.type == pg.MOUSEBUTTONDOWN:
					if Vec2(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]).GetEuclideanDistance(self.pos) <= self.radius:
						self.currentColor = self.activeColor
						self.is_clicked = True
						self.og_rect = Cursor.selected_obj.rect.copy()
						self.start_mouse = pg.mouse.get_pos()
					else:
						self.currentColor = self.inactiveColor
						self.is_clicked = False
				elif event.type == pg.MOUSEBUTTONUP:
					self.currentColor = self.inactiveColor
					self.is_clicked = False

				return self.is_clicked

			return False

		def ResizeRect(self):
			rect = Cursor.selected_obj.rect.copy()

			minSize = 10

			lock = False
			if pg.key.get_mods() == pg.KMOD_LCTRL:
				lock = True

			if "w" in self.directions:
				rect.w = max(pg.mouse.get_pos()[0] - self.start_mouse[0] + self.og_rect.w, minSize)

			if "h" in self.directions:
				rect.h = max(pg.mouse.get_pos()[1] - self.start_mouse[1] + self.og_rect.h, minSize)

			if "x" in self.directions:
				rect.w = max(self.start_mouse[0] - pg.mouse.get_pos()[0] + self.og_rect.w, minSize)
				if rect.w != minSize:
					rect.x = pg.mouse.get_pos()[0]

			if "y" in self.directions:
				rect.h = max(self.start_mouse[1] - pg.mouse.get_pos()[1] + self.og_rect.h, minSize)
				if rect.h != minSize:
					rect.y = pg.mouse.get_pos()[1]

			Cursor.selected_obj.rect = rect
			Cursor.start_mouse = pg.mouse.get_pos()
			Cursor.start_rect = Cursor.selected_obj.rect
			Cursor.reset_start_pos = False

	selected_obj = None
	start_mouse = (0, 0)
	start_rect = None
	reset_start_pos = True
	moving_obj = False
	resize_btn_clicked = False
	copied_obj_data = {}

	r = 8
	resize_btns = [
		# top left
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="xy"),
		# top middle
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="y"),
		# top right
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="wy"),
		# middle left
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="x"),
		# middle right
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="w"),
		# bottom left
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="xh"),
		# bottom middle
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="h"),
		# bottom right
		ResizeButton(r, (darkWhite, lightBlack, lightBlue), directions="wh")
		]

	def HandleEvent(event):
		if Cursor.selected_obj != None:
			Cursor.resize_btn_clicked = False
			for btn in Cursor.resize_btns:
				Cursor.resize_btn_clicked = btn.HandleEvent(event)
				if Cursor.resize_btn_clicked:
					break

			if not Cursor.resize_btn_clicked:
				if event.type == pg.MOUSEBUTTONDOWN:
					if not Cursor.selected_obj.rect.collidepoint(pg.mouse.get_pos()):
						Cursor.selected_obj = None
					else:
						if Cursor.reset_start_pos:
							Cursor.start_mouse = pg.mouse.get_pos()
							Cursor.start_rect = Cursor.selected_obj.rect
							Cursor.reset_start_pos = False

			if Cursor.selected_obj != None:
				if pg.mouse.get_pressed()[0]:
					if Cursor.selected_obj.rect.collidepoint(pg.mouse.get_pos()):
						Cursor.moving_obj = True

					if Cursor.moving_obj:
						if Cursor.start_rect == None:
							Cursor.start_mouse = pg.mouse.get_pos()
							Cursor.start_rect = Cursor.selected_obj.rect
							Cursor.reset_start_pos = False
						
						if not Cursor.reset_start_pos:
							Cursor.selected_obj.rect = MoveRectWithoutCenter(Cursor.start_mouse, Cursor.start_rect)
				else:
					Cursor.moving_obj = False
					Cursor.reset_start_pos = True

				if event.type == pg.KEYDOWN:
					
					if event.key == pg.K_LEFT:
						if event.mod == pg.KMOD_LSHIFT:
							Cursor.selected_obj.rect.w -= 1
						else:
							Cursor.selected_obj.rect.x -= 1
					
					if event.key == pg.K_RIGHT:
						if event.mod == pg.KMOD_LSHIFT:
							Cursor.selected_obj.rect.w += 1
						else:
							Cursor.selected_obj.rect.x += 1
					
					if event.key == pg.K_UP:
						if event.mod == pg.KMOD_LSHIFT:
							Cursor.selected_obj.rect.h -= 1
						else:
							Cursor.selected_obj.rect.y -= 1
					
					if event.key == pg.K_DOWN:
						if event.mod == pg.KMOD_LSHIFT:
							Cursor.selected_obj.rect.h += 1
						else:
							Cursor.selected_obj.rect.y += 1

					if event.mod == pg.KMOD_LCTRL:
						if event.key == pg.K_c:
							Cursor.Copy()

						if event.key == pg.K_v:
							Cursor.Paste()

					if event.key == pg.K_DELETE:
						level_objs.remove(Cursor.selected_obj)
						allObjs.remove(Cursor.selected_obj)
						d = dict(type(Cursor.selected_obj).__dict__)
						for key in d:
							if "all" in key:
								d[key].remove(Cursor.selected_obj)

						if type(Cursor.selected_obj) == Water or type(Cursor.selected_obj) == Enemey:
							Danger.allDangers.remove(Cursor.selected_obj)

						Cursor.selected_obj = None

		if not Cursor.selected_obj != None:
			if event.type == pg.MOUSEBUTTONDOWN:
				for obj in allObjs:
					if obj.rect.collidepoint(pg.mouse.get_pos()):
						Cursor.selected_obj = obj
						Cursor.start_mouse = pg.mouse.get_pos()
						Cursor.start_rect = Cursor.selected_obj.rect
						Cursor.reset_start_pos = False
						return

	def Draw():
		if Cursor.selected_obj != None:
			rect = Cursor.selected_obj.rect

			Cursor.resize_btns[0].pos = (rect.x, rect.y)
			Cursor.resize_btns[1].pos = (rect.x + rect.w // 2, rect.y)
			Cursor.resize_btns[2].pos = (rect.x + rect.w, rect.y)
			Cursor.resize_btns[3].pos = (rect.x, rect.y + rect.h // 2)
			Cursor.resize_btns[4].pos = (rect.x + rect.w, rect.y + rect.h // 2)
			Cursor.resize_btns[5].pos = (rect.x, rect.y + rect.h)
			Cursor.resize_btns[6].pos = (rect.x + rect.w // 2, rect.y + rect.h)
			Cursor.resize_btns[7].pos = (rect.x + rect.w, rect.y + rect.h)

			if not Cursor.moving_obj or Cursor.resize_btn_clicked:
				for btn in Cursor.resize_btns:
					btn.Draw()
			else:
				Cursor.copied_obj_data["times_pasted"] = 0

	def Copy():
		Cursor.copied_obj_data["type"] = type(Cursor.selected_obj)
		Cursor.copied_obj_data["times_pasted"] = 0

	def Paste():
		if Cursor.copied_obj_data["type"] != None:
			obj = CreateObj(Cursor.copied_obj_data["type"])
			Cursor.copied_obj_data["times_pasted"] += 1
			obj.rect.x, obj.rect.y = Cursor.selected_obj.rect.x, Cursor.selected_obj.rect.y
			obj.rect.w, obj.rect.h = Cursor.selected_obj.rect.w, Cursor.selected_obj.rect.h
			obj.rect.x += 10 * (Cursor.copied_obj_data["times_pasted"])
			obj.rect.y += 10 * (Cursor.copied_obj_data["times_pasted"])


class Level:
	difficulty = "normal"

	def ChangeDifficulty():
		if Level.difficulty == "normal":
			Level.difficulty = "hard"
		elif Level.difficulty == "hard":
			Level.difficulty = "easy"
		else:
			Level.difficulty = "normal"
		difficulty_btn.UpdateText(f"{Level.difficulty[0].upper()}{Level.difficulty[1:]}")

	def SaveLevel():
		level_ID = level_ID_txtbox.text.split(":")[1].strip("")
		if level_ID == " ":
			return

		level_ID = int(level_ID)

		file_name = f"level_{level_ID}_{Level.difficulty}.LVL"

		data = f"background[None:(55,55,55)]background\nplatformColors[{colors[Platform][0]}, {colors[Platform][1]}]platformColors\n[{colors[Ladder][0]}, {colors[Ladder][1]}]ladderColors\n[{colors[Stairs][0]}, {colors[Stairs][1]}]stairColors\ncoinColors[{colors[Coin][0]}, {colors[Coin][1]}]coinColors\nwaterColors[{colors[Water][0]}, {colors[Water][1]}]waterColors\nenemyColors[{colors[Enemey][0]}, {colors[Enemey][1]}]enemyColors\nendPointColors[{colors[EndPoint][0]}, {colors[EndPoint][1]}]endPointColors\nplayerColors[{colors[Player][0]}, {colors[Player][1]}]playerColors\n"

		data += "platforms[\n"

		for platform in Platform.allPlatforms:
			data += f'"rect":({platform.rect.x}, {platform.rect.y}, {platform.rect.w}, {platform.rect.h}),"colors":platformColors'

		data += "\n]platforms\n\n"

		data += "ladders[\n"

		for ladder in Ladder.allLadders:
			data += f'"rect":({ladder.rect.x}, {ladder.rect.y}, {ladder.rect.w}, {ladder.rect.h}),"colors":ladderColors'

		data += "\n]ladders\n\n"

		data += "coin[\n"

		for coin in Coin.allCoins:
			data += f'"rect":({coin.rect.x}, {coin.rect.y}, {coin.rect.w}, {coin.rect.h}),"colors":coinColors'

		data += "\n]coin\n\n"

		data += "water[\n"

		for water in Water.allWater:
			data += f'"rect":({water.rect.x}, {water.rect.y}, {water.rect.w}, {water.rect.h}),"colors":waterColors'

		data += "\n]water\n\n"

		data += "enemy[\n"

		for enemy in Enemey.allEnemies:
			data += f'"rect":({enemy.rect.x}, {enemy.rect.y}, {enemy.rect.w}, {enemy.rect.h}),"colors":enemyColors'

		data += "\n]enemy\n\n"

		data += "EndPoint[\n"

		data += '"rect":(),"colors":playerColors'

		data += "\n]EndPoint\n\n"

		data += "Player[\n"

		data += '"rect":(),"colors":playerColors'

		data += "\n]Player\n\n"

		SaveData(file_name, data, "\\levels")

	def LoadLevel():
		pass


level_objs = []
colors = {
	Platform: (lightBlack, darkWhite),
	Ladder: (lightBlack, darkWhite),
	Stairs: (lightBlack, darkWhite),
	Coin: (olive, yellow),
	Water: (lightBlue, lightBlue),
	Enemey: (bloodRed, lightRed),
	EndPoint: (lightBlack, darkWhite),
	Player: (lightBlack, darkWhite)
}
def CreateObj(objType):
	obj = objType((width // 2 - 50, height // 2 - 50, 100, 100), colors[objType])
	level_objs.append(obj)

	return obj


level_ID_txtbox = TextInputBox((55, 5, 140, 45), (lightBlack, darkWhite, lightBlue), splashText="Level ID: ", lists=[], textData={"alignText": "left"}, drawData={"replaceSplashText": False}, inputData={"allowedKeysFilePath": "numbers.txt", "charLimit":2})
difficulty_btn = Button((5, 55, 290, 50), (lightBlack, darkWhite, lightBlue), text=f"{Level.difficulty[0].upper()}{Level.difficulty[1:]}", onClick=Level.ChangeDifficulty, lists=[])
editor_items = Collection([
	level_ID_txtbox,
	Button((200, 5, 45, 45), (lightBlack, darkWhite, lightBlue), text="S", onClick=Level.SaveLevel, lists=[]),
	Button((250, 5, 45, 45), (lightBlack, darkWhite, lightBlue), text="L", onClick=Level.LoadLevel, lists=[]),
	difficulty_btn,
	Button((5, 110, 290, 50), (lightBlack, darkWhite, lightBlue), text="Platform", onClick=CreateObj, onClickArgs=[Platform], lists=[]),
	Button((5, 165, 290, 50), (lightBlack, darkWhite, lightBlue), text="Ladder", onClick=CreateObj, onClickArgs=[Ladder], lists=[]),
	Button((5, 220, 290, 50), (lightBlack, darkWhite, lightBlue), text="Coin", onClick=CreateObj, onClickArgs=[Coin], lists=[]),
	Button((5, 275, 290, 50), (lightBlack, darkWhite, lightBlue), text="Water", onClick=CreateObj, onClickArgs=[Water], lists=[]),
	Button((5, 330, 290, 50), (lightBlack, darkWhite, lightBlue), text="Enemy", onClick=CreateObj, onClickArgs=[Enemey], lists=[]),
	# Button((5, 385, 290, 50), (lightBlack, darkWhite, lightBlue), text="End Point", onClick=CreateObj, onClickArgs=[EndPoint], lists=[]),
	# Button((5, 440, 290, 50), (lightBlack, darkWhite, lightBlue), text="Player", onClick=CreateObj, onClickArgs=[Player], lists=[]),
	])
editor_menu = ExpandableMenu((0, 0, 300, height), (lightBlack, darkWhite, lightBlue), options=editor_items)


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

pg.quit()