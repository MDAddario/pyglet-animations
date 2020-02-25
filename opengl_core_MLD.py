import os
import pyglet
from pyglet.gl import *

# Setup the window
width = 600
height = 600
window = pyglet.window.Window(width=width, height=height, resizable=True)

# Use only one batch
batch = pyglet.graphics.Batch()

# Create sample text element
label = pyglet.text.Label("INSERT YOUR TEXT HERE", x=0, y=0, dpi=200, batch=batch)

# Retrieve pyglet sprite
img = pyglet.image.load("pyglet.png")
img.anchor_x = img.width // 2
img.anchor_y = img.height // 2

# Setup rotating sprites
sprites = [pyglet.sprite.Sprite(img=img, x=3*width/4, y=3*height/8, batch=batch),
		   pyglet.sprite.Sprite(img=img, x=3*width/4, y=4*height/8, batch=batch),
		   pyglet.sprite.Sprite(img=img, x=3*width/4, y=5*height/8, batch=batch),
		   pyglet.sprite.Sprite(img=img, x=3*width/4, y=6*height/8, batch=batch)]

# Setup sprite opacity
for sprite in sprites:
	sprite.opacity = 220


# Zoom sprites by scrolling
@window.event
def on_mouse_scroll(x, y, mouse, direction):
	for spr in sprites:
		spr.scale += direction / 10


# Setup square textures
red   = pyglet.image.SolidColorImagePattern((255, 0, 0, 255)).create_image(50, 50)
green = pyglet.image.SolidColorImagePattern((0, 255, 0, 255)).create_image(50, 50)
blue  = pyglet.image.SolidColorImagePattern((0, 0, 255, 255)).create_image(50, 50)
white = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(50, 50)

# Draw squares
sprite2 = pyglet.sprite.Sprite(img=red,   x=width/4, y=3*height/8, batch=batch)
sprite3 = pyglet.sprite.Sprite(img=green, x=width/4, y=4*height/8, batch=batch)
sprite4 = pyglet.sprite.Sprite(img=blue,  x=width/4, y=5*height/8, batch=batch)
sprite5 = pyglet.sprite.Sprite(img=white, x=width/4, y=6*height/8, batch=batch)


# Called every frame
@window.event
def on_draw():

	# Clear image
	window.clear()

	# Draw sprites
	batch.draw()


def update(dt):
	# Rotate the sprites
	for sprite in sprites:
		sprite.rotation += 100 * dt % 360


if __name__ == "__main__":
	pyglet.gl.glClearColor(0.2, 0.3, 0.3, 1)
	pyglet.clock.schedule_interval(update, 1/60)
	pyglet.app.run()
