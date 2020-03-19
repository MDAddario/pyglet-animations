import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse
import numpy as np
from scipy.spatial.transform import Rotation as R
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


# Create two floating triangles
def triangle_practice(batch):

	size = 1.5

	# Create the vertex and normal arrays.
	vertices = []
	normals = []
	
	# Populate the vertices array
	vertices.extend([-size, +size, 0])
	vertices.extend([-size, -size, 0])
	vertices.extend([-0, -0, 0])
	
	vertices.extend([+size, -size, 0])
	vertices.extend([+size, +size, 0])
	vertices.extend([+0, +0, 0])
	
	# Populate the normals array
	z_normal = [0.1, 0.1, 0.98]
	
	for i in range(6):
		normals.extend(z_normal)
	
	# Create a list of triangle indices.
	indices = []
	indices.extend([0, 1, 2])
	indices.extend([3, 4, 5])
	indices.extend([0, 2, 1])
	indices.extend([3, 5, 4])

	# Create a Material and Group for the Model
	diffuse = [0.5, 0.0, 0.3, 1.0]
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
									('v3f/static', vertices),
									('n3f/static', normals))

	return vertex_list


# Create floating rectanles
def box_creator(size, center, batch):
	
	# Convert to array objects
	size = np.asarray(size)
	center = np.asarray(center)
	
	# Error check
	if np.any(size <= 0):
		raise ValueError("Size values must be strictly positive")
	if size.shape != (3,):
		raise ValueError("Size must be a 1D array, 3 in length")
	if center.shape != (3,):
		raise ValueError("Center must be a 1D array, 3 in length")
	
	# Offset parameter
	offset = center - size / 2
	
	# Create the vertex and normal arrays
	vertices = []
	normals = []
	
	# Have some standard normals
	x_normal = np.array([0.98, 0.1, 0.1])
	y_normal = np.array([0.1, 0.98, 0.1])
	z_normal = np.array([0.1, 0.1, 0.98])
	
	# Front face
	vertices.extend(np.array([0, 0, 1] * size + offset))
	vertices.extend(np.array([1, 0, 1] * size + offset))
	vertices.extend(np.array([1, 1, 1] * size + offset))
	vertices.extend(np.array([0, 1, 1] * size + offset))
	
	for i in range(4):
		normals.extend(z_normal)
	
	# Back face
	vertices.extend(np.array([0, 0, 0] * size + offset))
	vertices.extend(np.array([0, 1, 0] * size + offset))
	vertices.extend(np.array([1, 1, 0] * size + offset))
	vertices.extend(np.array([1, 0, 0] * size + offset))
	
	for i in range(4):
		normals.extend(-z_normal)
	
	# Top face
	vertices.extend(np.array([0, 1, 0] * size + offset))
	vertices.extend(np.array([0, 1, 1] * size + offset))
	vertices.extend(np.array([1, 1, 1] * size + offset))
	vertices.extend(np.array([1, 1, 0] * size + offset))
	
	for i in range(4):
		normals.extend(y_normal)
	
	# Bot face
	vertices.extend(np.array([0, 0, 0] * size + offset))
	vertices.extend(np.array([1, 0, 0] * size + offset))
	vertices.extend(np.array([1, 0, 1] * size + offset))
	vertices.extend(np.array([0, 0, 1] * size + offset))
	
	for i in range(4):
		normals.extend(-y_normal)
	
	# Right face
	vertices.extend(np.array([1, 0, 0] * size + offset))
	vertices.extend(np.array([1, 1, 0] * size + offset))
	vertices.extend(np.array([1, 1, 1] * size + offset))
	vertices.extend(np.array([1, 0, 1] * size + offset))
	
	for i in range(4):
		normals.extend(x_normal)
	
	# Left face
	vertices.extend(np.array([0, 0, 0] * size + offset))
	vertices.extend(np.array([0, 0, 1] * size + offset))
	vertices.extend(np.array([0, 1, 1] * size + offset))
	vertices.extend(np.array([0, 1, 0] * size + offset))
	
	for i in range(4):
		normals.extend(-x_normal)
		
	# Do the indices too
	indices = []
	for i in range(len(vertices)):
		indices.append(i)

	# Create a Material and Group for the Model
	diffuse = [0.0, 0.4, 0.9, 1.0]
	ambient = [0.5, 0.0, 0.3, 1.0]
	specular = [1.0, 1.0, 1.0, 1.0]
	emission = [0.0, 0.0, 0.0, 1.0]
	shininess = 50
	material = pyglet.model.Material("", diffuse, ambient, specular, emission, shininess)
	group = pyglet.model.MaterialGroup(material=material)

	vertex_list = batch.add_indexed(len(vertices)//3,
									GL_QUADS,
									group,
									indices,
									('v3f/static', vertices),
									('n3f/static', normals))

	return vertex_list


# Create a set of vertex lists for battlefield stage
def battlefield_creator(batch):
	
	# Keep track of all platforms
	vertex_lists = []

	# Platform dimensions
	base_size    = [16.0, 0.8, 3.0]
	base_center  = [ 0.0, 0.0, 0.0]
	plat_size    = [ 4.0, 0.3, 2.5]
	left_center  = [-5.0, 3.0, 0.0]
	right_center = [ 5.0, 3.0, 0.0]
	top_center   = [ 0.0, 5.0, 0.0]
	
	# Create all platforms
	vertex_lists.append(box_creator(base_size, base_center,  batch))
	vertex_lists.append(box_creator(plat_size, left_center,  batch))
	vertex_lists.append(box_creator(plat_size, right_center, batch))
	vertex_lists.append(box_creator(plat_size, top_center,   batch))
	
	return vertex_lists


# Class to keep track of model and associated attributes
class CharacterModel:

	# Constructor
	def __init__(self, vertex_list, center=None):
		
		# Store as instance attribute
		self.vertex_list = vertex_list

		# Extract a deepcopy of vertices formatted as Nx3 array
		num_vertices = self.vertex_list.vertices.size // 3
		self.vertices = []
		self.vertices.extend(self.vertex_list.vertices)
		self.vertices = np.reshape(self.vertices, (num_vertices, 3))

		# Define classical mechanics
		self.velocity = np.zeros(3)
		self.max_speed = 10.0
		
		# Include the center of all coordinate transforms
		if center is not None:
			self.center = center
		else:
			self.center = np.mean(self.vertices, axis=0)
	
	# Destructor
	def __delete__(self):
		vertex_list.delete()

	# Scale both the real, local vertices
	def __scale_vertices(self, scaling):
		self.vertices *= scaling
		self.vertex_list.vertices = np.copy(np.ravel(self.vertices))
	
	# Rotate both the real, local vertices
	def __rotate_vertices(self, rotation):
		self.vertices = rotation.apply(self.vertices)
		self.vertex_list.vertices = np.copy(np.ravel(self.vertices))

	# Translate both the real, local vertices, and the transformation center
	def __translate_vertices(self, translation):
		self.center += translation
		self.vertices += translation
		self.vertex_list.vertices = np.copy(np.ravel(self.vertices))

	# Rescale total object size about center
	def rescale(self, new_size):

		# Determine maximal distance of vertices from center
		distances = np.sqrt(np.sum(np.square(self.vertices - self.center), axis=1))
		max_dist = np.max(distances)
		scaling = new_size / max_dist

		# Keep track of old center position
		old_center = np.copy(self.center)

		# Slide to origin, rescale, slide back
		self.__translate_vertices(-old_center)
		self.__scale_vertices(scaling)
		self.__translate_vertices(old_center)

	# Rotate object about center
	def rotate_degrees(self, axis, angle):

		# Check axis makes sense
		if axis not in "xyz":
			raise ValueError("Rotation axis must be 'x', 'y', or 'z'.")

		# Build rotation object
		r = R.from_euler(axis, angle, degrees=True)

		# Keep track of old center position
		old_center = np.copy(self.center)

		# Slide to origin, rescale, slide back
		self.__translate_vertices(-old_center)
		self.__rotate_vertices(r)
		self.__translate_vertices(old_center)

	# Update model position while velocity is non-zero
	def update(self, dt):
		if not np.allclose(self.velocity, 0):
			self.__translate_vertices(dt * self.velocity)

	# Set velocity values
	def set_velocity(self, xi, sign):
		self.velocity[xi] = self.max_speed * sign

	# Set the position of the model
	def set_position(self, position):
		self.__translate_vertices(position - self.center)


# Setup window and batch
setup()
batch = pyglet.graphics.Batch()

# Initialize global variables
rx = ry = rz = 0
dx = dy = 0
dz = -8

# Generate sample polygons
triangle_model = triangle_practice(batch=batch)
battlefield_lists = battlefield_creator(batch)


# Update every frame
def update(dt):
	fox_model.update(dt)


# Schedule the ever-important update function
pyglet.clock.schedule(update)

# Translation speeds
cam_rate = 0.7


# Take care of camera movement
def translate_camera_x(dt, rate):
	global dx
	dx += dt * rate * dz


def translate_camera_y(dt, rate):
	global dy
	dy += dt * rate * dz


@window.event
def on_key_press(symbol, modifiers):

	# Delete the torus
	if symbol == key.SPACE:
		
		# Wireframe view
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

	# Translate the camera
	elif symbol == key.UP:
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
	dz -= scroll_y * dz * 0.25
	dz = min(dz, 0)


# Load 3D fox model
os.chdir('fox/')
fox = pyglet.model.load("low-poly-fox-by-pixelmannen.obj", batch=batch)
fox_model = CharacterModel(fox.vertex_lists[0])

# Configure initial conditions for fox model
fox_model.rescale(2)
fox_model.set_position([-5, 1.2, 0])
fox_model.rotate_degrees('y', 90)

# Add keystate handler (breaks if you put this sooner in the code)
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Run the animation!
pyglet.app.run()
