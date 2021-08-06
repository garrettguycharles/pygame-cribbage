import math
from globals import *
import pygame


def get_sign(num):
    if (num < 0):
        return -1
    else:
        return 1

def get_distance(start_pos, end_pos):
    dx = abs(start_pos[0] - end_pos[0])
    dy = abs(start_pos[1] - end_pos[1])
    return math.sqrt((dx * dx) + (dy * dy))

def get_rect_kept_on_screen(rect):
    to_return = pygame.rect.Rect(rect.x, rect.y, rect.width, rect.height)
    if to_return.left < 0:
        to_return.left = 0
    if to_return.top < 0:
        to_return.top = 0
    if to_return.right > WIDTH:
        to_return.right = WIDTH
    if to_return.bottom > HEIGHT:
        to_return.bottom = HEIGHT

    return to_return

def load_image(filename):
    to_return = pygame.image.load(os.path.join(img_folder, filename))
    return to_return

def get_color_from_name(name):
    if name == "red":
        return (0x76, 0x00, 0x00)
    if name == "green":
        return (0x00, 0x5a, 0x00)
    if name == "blue":
        return (0x00, 0x1b, 0x35)
    if name == "tan":
        return (0x68, 0x53, 0x00)

    return (0x00, 0x00, 0x00)

def float_to_alpha(in_float):
    if in_float >= 1:
        return 0xff
    if in_float <= 0:
        return 0x00
    return int(in_float * float(0xff))

def add_coords(pos1, pos2):
    return (pos1[0] + pos2[0], pos1[1] + pos2[1])

def scale_coord(pos, scale):
    return (pos[0] * scale, pos[1] * scale)

def move_step(distance, start, towards):
    ratio = distance / (1 + get_distance(start, towards))
    if ratio >= 1:
        return towards

    step = add_coords(towards, scale_coord(start, -1))
    step = scale_coord(step, ratio)
    return add_coords(start, step)


def distance_in_direction(theta, distance):
    theta += 90

    x = -math.cos(math.radians(theta))
    y = math.sin(math.radians(theta))
    to_return = scale_coord((x,y), distance)
    return to_return





def clamp(_min, _val, _max):
    return min(max(_min, _val), _max)

class VarsBox:
    None