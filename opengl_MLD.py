from math import pi, sin, cos
import pyglet
from pyglet.gl import *
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
def create_torus(radius, inner_radius, slices, inner_slices, batch, color='purple'):

	# Create the vertex and normal arrays.
	vertices = []
	normals = []

	u_step = 2 * pi / (slices - 1)
	v_step = 2 * pi / (inner_slices - 1)
	u = 0.
	for i in range(slices):
		cos_u = cos(u)
		sin_u = sin(u)
		v = 0.
		for j in range(inner_slices):
			cos_v = cos(v)
			sin_v = sin(v)

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
		diffuse = [0.5, 0.5, 0.5, 1.0]

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
		self.speed = 2.0

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

	# Translate along x axis
	def translate_x(self, dt, sign):
		self.__translate_vertices(dt * self.speed * sign, 0, 0)

	# Translate along y axis
	def translate_y(self, dt, sign):
		self.__translate_vertices(0, dt * self.speed * sign, 0)

	# Translate along z axis
	def translate_z(self, dt, sign):
		self.__translate_vertices(0, 0, dt * self.speed * sign)


# Setup window and batch
setup()
batch = pyglet.graphics.Batch()

# Initialize global variables
rx = ry = rz = 0
dx = dy = 0
dz = -8

# Generate sample toruses
torus_model_1 = create_torus(radius=0.6, inner_radius=0.2, slices=50, 
							 inner_slices=30, batch=batch)
torus_model_2 = create_torus(radius=1.0, inner_radius=0.2, slices=50, 
							 inner_slices=30, batch=batch)
torus_model_3 = create_torus(radius=1.4, inner_radius=0.2, slices=50, 
							 inner_slices=30, batch=batch)

# Delete a vertex list from batch
torus_model_2.delete()

# Extract torus 1 vertex list
origin_vertices_1 = np.copy(torus_model_1.vertices)
center_vertices_1 = np.zeros(3)


# Update the torus center position
def trans_torus_x(dt, rate):
	global center_vertices_1
	center_vertices_1[0] += dt * rate
	trans_torus()


def trans_torus_y(dt, rate):
	global center_vertices_1
	center_vertices_1[1] += dt * rate
	trans_torus()


# Translate existing vertex list
def trans_torus():

	# Reshape vertices into Nx3 array
	length = origin_vertices_1.shape[0]
	reshaped = np.reshape(origin_vertices_1, (length//3, 3))
	reshaped += center_vertices_1
	ravelled = np.ravel(reshaped)

	# Debug
	if origin_vertices_1.shape != ravelled.shape:
		raise ValueError('You messed up sir.')

	# Update the vertices
	torus_model_1.vertices = ravelled


# Update every frame (required to make clock vary smoothly)
def update(dt):
	pass
pyglet.clock.schedule(update)


# Create random torus
def random_torus(dt, color):

	radius = np.random.random() * 2 + 1
	inner = np.random.random() * 0.3 + 0.3
	create_torus(radius=radius, inner_radius=inner, slices=50, 
				 inner_slices=30, batch=batch, color=color)


# Accept keyboard input
from pyglet.window import key

# Translation speeds
cam_rate = 0.7
tor_rate = 0.2
zoom_rate = 0.25


def trans_camera_x(dt, rate):
	global dx
	dx += dt * rate * dz


def trans_camera_y(dt, rate):
	global dy
	dy += dt * rate * dz


@window.event
def on_key_press(symbol, modifiers):

	if symbol == key.SPACE:

		if modifiers & key.MOD_SHIFT:
			random_torus(None, 'red')

		else:
			random_torus(None, 'blue')

	# Translate the camera
	elif symbol == key.UP:
		if keys[key.DOWN]:
			pyglet.clock.unschedule(trans_camera_y)
		pyglet.clock.schedule(trans_camera_y, rate=cam_rate)

	elif symbol == key.DOWN:
		if keys[key.UP]:
			pyglet.clock.unschedule(trans_camera_y)
		pyglet.clock.schedule(trans_camera_y, rate=-cam_rate)

	elif symbol == key.RIGHT:
		if keys[key.LEFT]:
			pyglet.clock.unschedule(trans_camera_x)
		pyglet.clock.schedule(trans_camera_x, rate=cam_rate)

	elif symbol == key.LEFT:
		if keys[key.RIGHT]:
			pyglet.clock.unschedule(trans_camera_x)
		pyglet.clock.schedule(trans_camera_x, rate=-cam_rate)

	# Translate the torus
	elif symbol == key.W:
		if keys[key.S]:
			pyglet.clock.unschedule(trans_torus_y)
		pyglet.clock.schedule(trans_torus_y, rate=tor_rate)

	elif symbol == key.S:
		if keys[key.W]:
			pyglet.clock.unschedule(trans_torus_y)
		pyglet.clock.schedule(trans_torus_y, rate=-tor_rate)

	elif symbol == key.D:
		if keys[key.A]:
			pyglet.clock.unschedule(trans_torus_x)
		pyglet.clock.schedule(trans_torus_x, rate=tor_rate)

	elif symbol == key.A:
		if keys[key.D]:
			pyglet.clock.unschedule(trans_torus_x)
		pyglet.clock.schedule(trans_torus_x, rate=-tor_rate)

	# Translate the fox
	elif symbol == key.I:
		if keys[key.K]:
			pyglet.clock.unschedule(fox_model.translate_y)
		pyglet.clock.schedule(fox_model.translate_y, sign=+1)

	elif symbol == key.K:
		if keys[key.I]:
			pyglet.clock.unschedule(fox_model.translate_y)
		pyglet.clock.schedule(fox_model.translate_y, sign=-1)

	elif symbol == key.L:
		if keys[key.J]:
			pyglet.clock.unschedule(fox_model.translate_x)
		pyglet.clock.schedule(fox_model.translate_x, sign=+1)

	elif symbol == key.J:
		if keys[key.L]:
			pyglet.clock.unschedule(fox_model.translate_x)
		pyglet.clock.schedule(fox_model.translate_x, sign=-1)

@window.event
def on_key_release(symbol, modifiers):

	# Reset the camera
	if symbol == key.UP:
		if not keys[key.DOWN]:
			pyglet.clock.unschedule(trans_camera_y)

	elif symbol == key.DOWN:
		if not keys[key.UP]:
			pyglet.clock.unschedule(trans_camera_y)

	elif symbol == key.RIGHT:
		if not keys[key.LEFT]:
			pyglet.clock.unschedule(trans_camera_x)

	elif symbol == key.LEFT:
		if not keys[key.RIGHT]:
			pyglet.clock.unschedule(trans_camera_x)

	# Reset the torus
	elif symbol == key.W:
		if not keys[key.S]:
			pyglet.clock.unschedule(trans_torus_y)

	elif symbol == key.S:
		if not keys[key.W]:
			pyglet.clock.unschedule(trans_torus_y)

	elif symbol == key.D:
		if not keys[key.A]:
			pyglet.clock.unschedule(trans_torus_x)

	elif symbol == key.A:
		if not keys[key.D]:
			pyglet.clock.unschedule(trans_torus_x)

	# Reset the fox
	elif symbol == key.I:
		if not keys[key.K]:
			pyglet.clock.unschedule(fox_model.translate_y)

	elif symbol == key.K:
		if not keys[key.I]:
			pyglet.clock.unschedule(fox_model.translate_y)

	elif symbol == key.L:
		if not keys[key.J]:
			pyglet.clock.unschedule(fox_model.translate_x)

	elif symbol == key.J:
		if not keys[key.L]:
			pyglet.clock.unschedule(fox_model.translate_x)


# Accept mouse input
from pyglet.window import mouse

# Add keystate handler (breaks if you put this sooner in the code)
keys = key.KeyStateHandler()
window.push_handlers(keys)


@window.event
def on_mouse_press(x, y, button, modifiers):

	if button & mouse.LEFT:

		if keys[key.A]:

			random_torus(None, 'grey')


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global rx, ry

	if buttons & mouse.LEFT:

		rx += -dy
		ry += dx
		rx %= 360
		ry %= 360


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
pyglet.app.run()
