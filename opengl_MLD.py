import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse
import numpy as np
import os

try:
	# Try and create a window with multisampling (antialiasing)
	config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)
	window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
	# Fall back to no multisampling for old hardware
	window = pyglet.window.Window(resizable=True)

# Set window projection to 3D
window.projection = pyglet.window.Projection3D()


# Automatically called each frame
@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glTranslatef(dx, dy, dz)
	glRotatef(rz, 0, 0, 1)
	glRotatef(ry, 0, 1, 0)
	glRotatef(rx, 1, 0, 0)
	batch.draw()


# One time setup
def setup():

	glClearColor(1, 1, 1, 1)
	glColor3f(1, 0, 0)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_CULL_FACE)

	# Wireframe view
	#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

	# Simple light setup
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_LIGHT1)


# Create a torus
def create_torus(radius, inner_radius, slices, inner_slices, batch, color=None):

	# Create the vertex and normal arrays.
	vertices = []
	normals = []

	u_step = 2 * np.pi / (slices - 1)
	v_step = 2 * np.pi / (inner_slices - 1)
	u = 0.
	for i in range(slices):
		cos_u = np.cos(u)
		sin_u = np.sin(u)
		v = 0.
		for j in range(inner_slices):
			cos_v = np.cos(v)
			sin_v = np.sin(v)

			d = (radius + inner_radius * cos_v)
			x = d * cos_u
			y = d * sin_u
			z = inner_radius * sin_v

			nx = cos_u * cos_v
			ny = sin_u * cos_v
			nz = sin_v

			vertices.extend([x, y, z])
			normals.extend([nx, ny, nz])
			v += v_step
		u += u_step

	# Create a list of triangle indices.
	indices = []
	for i in range(slices - 1):
		for j in range(inner_slices - 1):
			p = i * inner_slices + j
			indices.extend([p, p + inner_slices, p + inner_slices + 1])
			indices.extend([p, p + inner_slices + 1, p + 1])

	# Select color
	if color == 'purple':
		diffuse = [0.5, 0.0, 0.3, 1.0]
	elif color == 'red':
		diffuse = [1.0, 0.0, 0.0, 1.0]
	elif color == 'green':
		diffuse = [0.0, 1.0, 0.0, 1.0]
	elif color == 'blue':
		diffuse = [0.0, 0.0, 1.0, 1.0]
	else:
		diffuse = [0.0, 0.0, 0.0, 1.0]

	# Create a Material and Group for the Model
	ambient = [0.5, 0.0, 0.3, 1.0]
	specular = [1.0, 1.0, 1.0, 1.0]
	emission = [0.0, 0.0, 0.0, 1.0]
	shininess = 50
	material = pyglet.model.Material("", diffuse, ambient, specular, emission, shininess)
	group = pyglet.model.MaterialGroup(material=material)

	vertex_list = batch.add_indexed(len(vertices)//3,
									GL_TRIANGLES,
									group,
									indices,
									('v3f/dynamic', vertices),
									('n3f/static', normals))

	return vertex_list


# Class to keep track of model and associated attributes
class CustomModel:

	# Constructor
	def __init__(self, vertex_list):
		self.vertex_list = vertex_list

		# Extract a deepcopy of vertices formatted as Nx3 array
		num_vertices = self.vertex_list.vertices.size // 3
		self.vertices = []
		self.vertices.extend(self.vertex_list.vertices)
		self.vertices = np.reshape(self.vertices, (num_vertices, 3))

		# Define classical mechanics
		self.velocity = np.zeros(3)
		self.max_speed = 2.0

	# Destructor
	def __delete__(self):
		vertex_list.delete()

	# Edit both the real copy and self copy of vertices
	def __scale_vertices(self, scale_x, scale_y, scale_z):
		self.vertices[:,0] *= scale_x
		self.vertices[:,1] *= scale_y
		self.vertices[:,2] *= scale_z
		self.vertex_list.vertices = np.copy(np.ravel(self.vertices))

	# Edit both the real copy and self copy of vertices
	def __translate_vertices(self, trans_x, trans_y, trans_z):
		self.vertices[:,0] += trans_x
		self.vertices[:,1] += trans_y
		self.vertices[:,2] += trans_z
		self.vertex_list.vertices = np.copy(np.ravel(self.vertices))

	# Rescale total object size
	def rescale(self, new_size):

		# Make sure that all coordinates are non-negative
		temp_vertices = np.copy(self.vertices)
		for xi in range(3):
			temp_vertices[:,xi] -= np.min(temp_vertices[:,xi])

		# Determine maximal distance from origin 
		distances = np.sqrt(np.sum(np.square(temp_vertices), axis=1))
		max_dist = np.max(distances)

		# Compute scaling factor and resize
		scaling = new_size / max_dist
		self.__scale_vertices(scaling, scaling, scaling)

	# Set velocity values
	def set_velocity(self, xi, sign):
		self.velocity[xi] = self.max_speed * sign

	# Update model position while velocity is non-zero
	def update(self, dt):
		if not np.allclose(self.velocity, 0):
			self.__translate_vertices(*(dt * self.velocity))

	# Translate model by given input
	def translate(self, dx, dy, dz):
		self.__translate_vertices(dx, dy, dz)


# Setup window and batch
setup()
batch = pyglet.graphics.Batch()

# Initialize global variables
rx = ry = rz = 0
dx = dy = 0
dz = -8

# Generate sample toruses
torus_model = create_torus(radius=0.6, inner_radius=0.2, slices=50, 
						   inner_slices=30, batch=batch, color='red')


# Update every frame (required to make clock vary smoothly)
def update(dt):
	fox_model.update(dt)


pyglet.clock.schedule(update)


# Translation speeds
cam_rate = 0.7
zoom_rate = 0.25


def translate_camera_x(dt, rate):
	global dx
	dx += dt * rate * dz


def translate_camera_y(dt, rate):
	global dy
	dy += dt * rate * dz


@window.event
def on_key_press(symbol, modifiers):

	# Translate the camera
	if symbol == key.UP:
		if keys[key.DOWN]:
			pyglet.clock.unschedule(translate_camera_y)
		pyglet.clock.schedule(translate_camera_y, rate=cam_rate)

	elif symbol == key.DOWN:
		if keys[key.UP]:
			pyglet.clock.unschedule(translate_camera_y)
		pyglet.clock.schedule(translate_camera_y, rate=-cam_rate)

	elif symbol == key.RIGHT:
		if keys[key.LEFT]:
			pyglet.clock.unschedule(translate_camera_x)
		pyglet.clock.schedule(translate_camera_x, rate=cam_rate)

	elif symbol == key.LEFT:
		if keys[key.RIGHT]:
			pyglet.clock.unschedule(translate_camera_x)
		pyglet.clock.schedule(translate_camera_x, rate=-cam_rate)

	# Translate the fox
	elif symbol == key.W:
		if keys[key.S]:
			fox_model.set_velocity(1, 0)
		fox_model.set_velocity(1, +1)

	elif symbol == key.S:
		if keys[key.W]:
			fox_model.set_velocity(1, 0)
		fox_model.set_velocity(1, -1)

	elif symbol == key.D:
		if keys[key.A]:
			fox_model.set_velocity(0, 0)
		fox_model.set_velocity(0, +1)

	elif symbol == key.A:
		if keys[key.D]:
			fox_model.set_velocity(0, 0)
		fox_model.set_velocity(0, -1)


@window.event
def on_key_release(symbol, modifiers):

	# Reset the camera
	if symbol == key.UP:
		if not keys[key.DOWN]:
			pyglet.clock.unschedule(translate_camera_y)

	elif symbol == key.DOWN:
		if not keys[key.UP]:
			pyglet.clock.unschedule(translate_camera_y)

	elif symbol == key.RIGHT:
		if not keys[key.LEFT]:
			pyglet.clock.unschedule(translate_camera_x)

	elif symbol == key.LEFT:
		if not keys[key.RIGHT]:
			pyglet.clock.unschedule(translate_camera_x)

	# Reset the fox
	elif symbol == key.W:
		if not keys[key.S]:
			fox_model.set_velocity(1, 0)

	elif symbol == key.S:
		if not keys[key.W]:
			fox_model.set_velocity(1, 0)

	elif symbol == key.D:
		if not keys[key.A]:
			fox_model.set_velocity(0, 0)

	elif symbol == key.A:
		if not keys[key.D]:
			fox_model.set_velocity(0, 0)


# Rotate the window
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global rx, ry, rz

	if buttons & mouse.LEFT:

		if modifiers & key.MOD_SHIFT:

			rz += dy
			rz %= 360

		else:

			rx += -dy
			ry += dx
			rx %= 360
			ry %= 360


# Zoom the window
@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
	global dz
	dz -= scroll_y * dz * zoom_rate
	dz = min(dz, 0)


# Include 3D models
os.chdir('fox/')
fox = pyglet.model.load("low-poly-fox-by-pixelmannen.obj", batch=batch)
fox_model = CustomModel(fox.vertex_lists[0])
fox_model.rescale(4)
fox_model.translate(0, -1.18, 0)

# Add keystate handler (breaks if you put this sooner in the code)
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Run the animation!
pyglet.app.run()
