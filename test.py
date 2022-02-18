class Entity:
	def __init__(self, rect, colors):
		self.rect = rect
		self.colors = colors


class Player(Entity):
	super().__init__(1, 1)

