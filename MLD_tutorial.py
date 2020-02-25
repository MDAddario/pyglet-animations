=====================
KEEPING TRACK OF TIME
=====================

# Schedule a periodic function call every 0.1 seconds
>>>> pyglet.clock.schedule_interval(update, 0.1)

# Schedule a function to be called as frequently as possible
>>>> pyglet.clock.schedule(update)

# Schedule a function call once in 5.0 seconds
>>>> pyglet.clock.schedule_once(update, 5.0)

# Unschedule function call 
>>>> pyglet.clock.unschedule(update)

# Pass arguments to function
>>>> pyglet.clock.unschedule(update, arg_1=arg_1, arg_2=arg_2)

def update(dt, arg_1, arg_2):
	pass

"""
Time parameter is in seconds
The parameter `dt` is passed to `update` as first argument
"""

# Make your own clock
>>>> my_clock = pyglet.clock.Clock()

# You need to tick your clock every frame!
>>>> dt = my_clock.tick()

"""
Call all the previous methods on your personal clock all the same
"""

========
GRAPHICS
========

# Remove a vertex list from the batch
>>>> vertex_list.delete()

# Edit the vertex list attributes
>>>> vertex_list.vertices = [3, 4, 5, 6, 7, 8]
>>>> vertex_list.normal   = [3, 4, 5, 6, 7, 8]

# List of other attributes
https://pyglet.readthedocs.io/en/latest/programming_guide/graphics.html#vertex-lists

# Usage modifiers
>>>> "/static"  #Data is never or rarely modified after initialisation
>>>> "/dynamic" #Data is never or rarely modified after initialisation
>>>> "/stream"  #Data is never or rarely modified after initialisation

========
KEYBOARD
========

@window.event
def on_key_press(symbol, modifiers):
    pass

@window.event
def on_key_release(symbol, modifiers):
    pass

# List of keys
>>>> from pyglet.window import key

>>>> key.A
>>>> key.B
>>>> key.C
>>>> ...
>>>> key._1
>>>> key._2
>>>> key._3
>>>> ...
>>>> key.ENTER or key.RETURN
>>>> key.SPACE
>>>> key.BACKSPACE
>>>> key.DELETE
>>>> key.MINUS
>>>> key.EQUAL
>>>> key.BACKSLASH
>>>> ...
>>>> key.LEFT
>>>> key.RIGHT
>>>> key.UP
>>>> key.DOWN
>>>> key.HOME
>>>> key.END
>>>> key.PAGEUP
>>>> key.PAGEDOWN
>>>> ...
>>>> key.F1
>>>> key.F2
>>>> ...
>>>> key.NUM_1
>>>> key.NUM_2
>>>> ...
>>>> key.NUM_EQUAL
>>>> key.NUM_DIVIDE
>>>> key.NUM_MULTIPLY
>>>> key.NUM_SUBTRACT
>>>> key.NUM_ADD
>>>> key.NUM_DECIMAL
>>>> key.NUM_ENTER
>>>> ....

# List of modifiers
>>>> key.MOD_SHIFT
>>>> key.MOD_CTRL
>>>> key.MOD_ALT
>>>> key.MOD_WINDOWS
>>>> key.MOD_CAPSLOCK
>>>> key.MOD_NUMLOCK
>>>> key.MOD_SCROLLLOCK

# List of special modifiers
>>>> key.LCTRL
>>>> key.RCTRL
>>>> key.LSHIFT
>>>> key.RSHIFT
>>>> ...

# Check if 'A' is pressed
>>>> if symbol == key.A:

# Check if shift is held
>>>> if modifiers & key.MOD_SHIFT:

# Setup key handler
>>>> keys = key.KeyStateHandler()
>>>> window.push_handlers(keys)

# Check if the spacebar is currently pressed:
>>>> if keys[key.SPACE]:

=====
MOUSE
=====

@window.event
def on_mouse_motion(x, y, dx, dy):
    pass

@window.event
def on_mouse_press(x, y, button, modifiers):
    pass

@window.event
def on_mouse_release(x, y, button, modifiers):
    pass

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    pass

@window.event
def on_mouse_enter(x, y):
    pass

@window.event
def on_mouse_leave(x, y):
    pass

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    pass

# List of mouse clicks
>>>> from pyglet.window import mouse

>>>> mouse.LEFT
>>>> mouse.MIDDLE
>>>> mouse.RIGHT

# Check if left click is pressed
>>>> if buttons & mouse.LEFT:

# Hide the mouse
>>>> window.set_mouse_visible(False)







