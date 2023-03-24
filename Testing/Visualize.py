from Classes.GameObject import *
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import random

# Constants
ENCLOSURE_SIZE = 500
VELOCITY_CHANGE_RATE = 0.05  # The rate at which the velocity changes
INTERPOLATION_RATE = 0.05  # The rate at which the current velocity approaches the target velocity
MAX_VELOCITY = 300  # Maximum velocity value
MIN_VELOCITY = 10

HAS_INIT = False
VISUALIZE_LOADED = True

def get_color(obj: GameObject):
    if obj.type == ObjectType.ENEMY_ROBOT:
        return pg.mkBrush(255, 0, 0, 255)
    elif obj.type == ObjectType.FRISBEE:
        if obj.score < 0:
            return pg.mkBrush(255, 0, 255, 255)
        elif obj.score >= 0.7:
            return pg.mkBrush(0, 255, 0, max(obj.score, 0.05)*255)
        elif obj.position.norm() < 300:
            return pg.mkBrush(255, 255, 255, max(obj.score, 0.05)*255)
        else:
            return pg.mkBrush(255, 255, 0, max(obj.score, 0.05)*255)
    else:
        return pg.mkBrush(0, 0, 255, 255)

def visualize_game_objects(game_objects):
    global plot
    global win
    global scatter_plot
    global HAS_INIT

    if not HAS_INIT:

        win = pg.GraphicsLayoutWidget(show=True)
        win.setWindowTitle('Real-time plot using PyQtGraph')
        plot = win.addPlot(title="Game Objects")
        plot.setXRange(-500,500)
        plot.setYRange(-500,500)
        scatter_plot = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        plot.addItem(scatter_plot)
        HAS_INIT = True
        return

    x_values = [obj.position.x for obj in game_objects]
    y_values = [obj.position.y for obj in game_objects]
    brushes = [get_color(obj) for obj in game_objects]
    scatter_plot.setData(x=x_values, y=y_values, brush=brushes)

def update_robot_position_and_velocity(robot, dt):
    # Check if the robot has a target_velocity attribute, otherwise create one
    if not hasattr(robot, 'target_velocity'):
        robot.target_velocity = Vec(
            random.uniform(MIN_VELOCITY, MAX_VELOCITY) * random.choice([-1, 1]),
            random.uniform(MIN_VELOCITY, MAX_VELOCITY) * random.choice([-1, 1]),
            0
        )

    # Interpolate the current velocity towards the target velocity
    robot.velocity.x += (robot.target_velocity.x - robot.velocity.x) * INTERPOLATION_RATE
    robot.velocity.y += (robot.target_velocity.y - robot.velocity.y) * INTERPOLATION_RATE

    new_position = Vec(
        robot.position.x + robot.velocity.x * dt,
        robot.position.y + robot.velocity.y * dt,
        robot.position.z
    )

    # Check if the new position is within the enclosure
    if -ENCLOSURE_SIZE <= new_position.x <= ENCLOSURE_SIZE and -ENCLOSURE_SIZE <= new_position.y <= ENCLOSURE_SIZE:
        robot.position = new_position
    else:
        # Reflect the velocity when hitting the enclosure boundary
        if new_position.x < -ENCLOSURE_SIZE or new_position.x > ENCLOSURE_SIZE:
            robot.velocity.x = -robot.velocity.x
        if new_position.y < -ENCLOSURE_SIZE or new_position.y > ENCLOSURE_SIZE:
            robot.velocity.y = -robot.velocity.y

    # Update the target velocity smoothly
    if random.random() < VELOCITY_CHANGE_RATE:
        robot.target_velocity = Vec(
            random.uniform(MIN_VELOCITY, MAX_VELOCITY) * random.choice([-1, 1]),
            random.uniform(MIN_VELOCITY, MAX_VELOCITY) * random.choice([-1, 1]),
            0
        )