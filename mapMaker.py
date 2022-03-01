import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")


from GameObjects import *
from GUIShapes import *

from main import *



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

	for platform in Platform.allPlatforms:
		DrawObj(platform)
	
	for ladder in Ladder.allLadders:
		DrawObj(ladder)

	for coin in Coin.allCoins:
		DrawObj(coin)

	for danger in Danger.allDangers:
		DrawObj(danger)

	DrawAllGUIObjects()

	pg.display.update()


def HandleEvents(event):
	global showFps
	HandleGui(event)


def Update():
	pass


editor_items = Collection([
	TextInputBox((5, 55, 290, 25), (lightBlack, darkWhite, lightBlue), splashText="Level ID: ", lists=[], textData={"fontSize": 15, "alignText": "left"}, drawData={"replaceSplashText": False}, inputData={"allowedKeysFilePath": "input keys\\numbers.txt"}),
	Button((5, 85, 290, 25), (lightBlack, darkWhite, lightBlue), text="Save", lists=[], textData={"fontSize": 15}),
	Button((5, 115, 290, 25), (lightBlack, darkWhite, lightBlue), text="Platform", lists=[], textData={"fontSize": 15}),
	Button((5, 145, 290, 25), (lightBlack, darkWhite, lightBlue), text="Stairs", lists=[], textData={"fontSize": 15}),
	Button((5, 175, 290, 25), (lightBlack, darkWhite, lightBlue), text="Ladder", lists=[], textData={"fontSize": 15}),
	Button((5, 205, 290, 25), (lightBlack, darkWhite, lightBlue), text="Coin", lists=[], textData={"fontSize": 15}),
	Button((5, 235, 290, 25), (lightBlack, darkWhite, lightBlue), text="Water", lists=[], textData={"fontSize": 15}),
	Button((5, 265, 290, 25), (lightBlack, darkWhite, lightBlue), text="Enemy", lists=[], textData={"fontSize": 15}),
	Button((5, 295, 290, 25), (lightBlack, darkWhite, lightBlue), text="End Point", lists=[], textData={"fontSize": 15}),
	])
editor_menu = ExpandableMenu((0, 0, 300, height), (lightBlack, darkWhite, lightBlue), options=editor_items)


while running:
	clock.tick_busy_loop(fps)
	deltaTime = clock.get_time()

	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if not Settings.isChangingKeyBind:
				if event.key == pg.K_ESCAPE:
					running = False

		HandleEvents(event)

	Update()

	DrawLoop()

pg.quit()