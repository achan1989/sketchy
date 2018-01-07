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

JOY_DEADZONE = 0.2
JOY_SPEED_MULT = 2
JOY_X_AXIS_IDX = 0
JOY_Y_AXIS_IDX = 1
JOY_SHAKE_BUTTON_IDX = 3

MOUSE_SPEED_MULT = 0.5

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

    controls = Controls(bounds)
    quit = False

    while not quit:
        for evt in pygame.event.get():
            if evt.type == QUIT:
                quit = True
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                quit = True

        controls.update()
        if controls.changed:
            draw_move(controls, screen)
            if controls.shaking == ButtonState.ON:
                do_shake(screen, bg_surface)

        clock.tick(TARGET_FRAMERATE)

def draw_move(controls, screen):
    dirty = pygame.draw.line(
        screen, LINE_COLOUR, controls.old_pos, controls.pos, LINE_WIDTH)
    dirty.inflate_ip(LINE_WIDTH*2, LINE_WIDTH*2)
    pygame.display.update(dirty)

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

def clamp(n, low, high):
    if n < low:
        n = low
    elif n > high:
        n = high
    return n


class Controls:
    def __init__(self, bounds):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        # Reset relative counters.
        pygame.mouse.get_rel()

        self.joysticks = [
            pygame.joystick.Joystick(jid)
            for jid in range(pygame.joystick.get_count())]
        for stick in self.joysticks:
            stick.init()

        self.bounds_x, self.bounds_y = bounds
        self.old_pos = (self.bounds_x/2, self.bounds_y/2)
        self.pos = self.old_pos
        self._m_shaking = ButtonState.OFF
        self._j_shaking = ButtonState.OFF
        self.shaking = ButtonState.OFF
        self.changed = False

    def update(self):
        got_input = False
        mouse_input = False
        joy_input = False

        m_dx, m_dy = pygame.mouse.get_rel()
        _l, _m, m_shake_input = pygame.mouse.get_pressed()
        m_shaking_change = self.shaking_change(m_shake_input, self._m_shaking)
        if m_shaking_change is not None:
            self._m_shaking = m_shaking_change
        if (m_dx, m_dy) != (0, 0) or m_shake_input or m_shaking_change is not None:
            mouse_input = True

        for stick in self.joysticks:
            j_dx = stick.get_axis(JOY_X_AXIS_IDX)
            j_dy = stick.get_axis(JOY_Y_AXIS_IDX)
            j_shake_input = stick.get_button(JOY_SHAKE_BUTTON_IDX)
            j_shaking_change = self.shaking_change(j_shake_input, self._j_shaking)
            if j_shaking_change is not None:
                self._j_shaking = j_shaking_change
            moving = math.sqrt(j_dx**2 + j_dy**2) >= JOY_DEADZONE
            if not moving:
                j_dx = 0
                j_dy = 0
            if moving or j_shake_input or j_shaking_change is not None:
                joy_input = True
                break

        if mouse_input:
            dx = m_dx
            dy = m_dy
            shaking = self._m_shaking
            move_mult = MOUSE_SPEED_MULT
        elif joy_input:
            dx = j_dx
            dy = j_dy
            shaking = self._j_shaking
            move_mult = JOY_SPEED_MULT

        if mouse_input or joy_input:
            old_x, old_y = self.pos
            new_x = clamp(old_x + (dx * move_mult), 0, self.bounds_x)
            new_y = clamp(old_y + (dy * move_mult), 0, self.bounds_y)
            self.old_pos = self.pos
            self.pos = (new_x, new_y)

            self.shaking = shaking
            self.changed = True
        else:
            self.changed = False

    @staticmethod
    def shaking_change(shake_input, last_state):
        if shake_input:
            if last_state == ButtonState.OFF:
                state_change = ButtonState.ON
            elif last_state == ButtonState.ON:
                state_change = ButtonState.HELD
            else:
                state_change = None
        else:
            if last_state in (ButtonState.ON, ButtonState.HELD):
                state_change = ButtonState.OFF
            else:
                state_change = None
        return state_change


def joy_debug_print(stick):
        print("stick {}: {}".format(stick.get_id(), stick.get_name()))
        axes = stick.get_numaxes()
        for i in range(axes):
            print("Axis {}: {}".format(i, stick.get_axis(i)))
        buttons = [stick.get_button(i)
                   for i in range(stick.get_numbuttons())]
        print("Buttons: ", buttons)


class ButtonState(Enum):
    ON = 1
    HELD = 2
    OFF = 3


if __name__ == "__main__":
    main()
