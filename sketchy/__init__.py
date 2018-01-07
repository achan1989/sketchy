from enum import Enum
import math
import random

import pygame
from pygame.locals import *


BACKGROUND_GREY = 170
BACKGROUND_VARIANCE = 10
BACKGROUND_ALPHA = 45

CURRENT_RESOLUTION = (0, 0)
TARGET_FRAMERATE = 30

STICK_DEADZONE = 0.2
STICK_SPEED_MULT = 2
X_AXIS_IDX = 0
Y_AXIS_IDX = 1
SHAKE_BUTTON_IDX = 3

# RGBA
LINE_COLOUR = (65, 65, 65, 255)
LINE_WIDTH = 2


def main():
    pygame.init()
    clock = pygame.time.Clock()

    pygame.display.set_caption("Sketchy!")
    # screen = pygame.display.set_mode((800,600))
    screen = pygame.display.set_mode(CURRENT_RESOLUTION, FULLSCREEN)
    bounds = screen.get_size()
    bg_surface = init_background(screen)
    pygame.display.flip()

    # x,y position of the cursor.
    pos = (0,0)

    joysticks = init_joysticks()

    quit = False
    while not quit:
        for evt in pygame.event.get():
            if evt.type == QUIT:
                quit = True
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                quit = True

        for stick in joysticks:
            stick.update()

        new_pos = do_move(pos, joysticks[0], screen, bounds)
        pos = new_pos

        if joysticks[0].shaking == ButtonState.ON:
            do_shake(screen, bg_surface)

        clock.tick(TARGET_FRAMERATE)

def do_move(old_pos, stick, screen, bounds):
    moving = math.sqrt(stick.curr_x**2 + stick.curr_y**2) >= STICK_DEADZONE
    if not moving:
        return old_pos

    old_x, old_y = old_pos
    new_x = old_x + (stick.curr_x * STICK_SPEED_MULT)
    new_y = old_y + (stick.curr_y * STICK_SPEED_MULT)
    bounds_x, bounds_y = bounds
    if new_x < 0:
        new_x = 0
    elif new_x > bounds_x:
        new_x = bounds_x
    if new_y < 0:
        new_y = 0
    elif new_y > bounds_y:
        new_y = bounds_y
    new_pos = (new_x, new_y)

    dirty = pygame.draw.line(screen, LINE_COLOUR, old_pos, new_pos, LINE_WIDTH)
    dirty.inflate_ip(LINE_WIDTH*2, LINE_WIDTH*2)
    pygame.display.update(dirty)
    return new_pos

def do_shake(screen, bg_surface):
    screen.blit(bg_surface, (0,0))
    pygame.display.flip()

def init_background(screen):
    assert screen.get_bitsize() == 32
    scr_w, scr_h = screen.get_size()
    data_len = scr_w * scr_h * screen.get_bytesize()

    def bg_gen():
        for i in range(scr_w * scr_h):
            n = int(random.triangular(
                    BACKGROUND_GREY - BACKGROUND_VARIANCE,
                    BACKGROUND_GREY + BACKGROUND_VARIANCE))
            # RGBA
            yield n
            yield n
            yield n
            yield BACKGROUND_ALPHA

    bg_data = bytes(bg_gen())

    # No alpha (fully opaque) in the initial background...
    bg_surface = pygame.Surface(screen.get_size(), 0, screen)
    bg_surface.get_view().write(bg_data)
    screen.blit(bg_surface, (0,0))

    # ...but have alpha in the background used for shaking.
    bg_surface = pygame.Surface(screen.get_size(), SRCALPHA, screen)
    bg_surface.get_view().write(bg_data)
    return bg_surface

def init_joysticks():
    joysticks = [Joystick(x)
                 for x in range(pygame.joystick.get_count())]
    for stick in joysticks:
        stick.debug_print()
    return joysticks


class Joystick:
    def __init__(self, jid):
        self._stick = pygame.joystick.Joystick(jid)
        self._stick.init()
        self.curr_x = 0.0
        self.curr_y = 0.0
        self.shaking = ButtonState.OFF
        self.update()

    def __getattr__(self, name):
        return getattr(self._stick, name)

    def update(self):
        self.curr_x = self.get_axis(X_AXIS_IDX)
        self.curr_y = self.get_axis(Y_AXIS_IDX)

        shake_on = self.get_button(SHAKE_BUTTON_IDX)
        if shake_on:
            if self.shaking == ButtonState.OFF:
                self.shaking = ButtonState.ON
            elif self.shaking == ButtonState.ON:
                self.shaking = ButtonState.HELD
        else:
            self.shaking = ButtonState.OFF

    def debug_print(self):
        print("stick {}: {}".format(self.get_id(), self.get_name()))
        axes = self.get_numaxes()
        for i in range(axes):
            print("Axis {}: {}".format(i, self.get_axis(i)))
        buttons = [self.get_button(i)
                   for i in range(self.get_numbuttons())]
        print("Buttons: ", buttons)


class ButtonState(Enum):
    ON = 1
    HELD = 2
    OFF = 3


if __name__ == "__main__":
    main()
