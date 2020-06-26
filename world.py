import pygame
import math
from brick import Brick
from player import Player


class World:
    def __init__(self):
        self.width = 800
        self.height = 600

        self.player = Player()
        self.reset_player()
        self.bricks = list()
        self.brick_counter = 0

        # for timing
        self.new_time = 0.0
        self.frame_time = 0.0
        self.current_time = 0.0
        self.accumulator = 0.0
        self.dt = 0.01
        self.t = 0.0
        self.current_ups = 0
        self.last_ups_time = pygame.time.get_ticks()

    def update(self, screen, font):

        # delta time from https://gafferongames.com/post/fix_your_timestep/
        self.new_time = pygame.time.get_ticks()
        self.frame_time = self.new_time - self.current_time
        if self.frame_time > 0.25:
            self.frame_time = 0.25
        self.current_time = self.new_time
        self.accumulator += self.frame_time
        while self.accumulator >= self.dt:
            self.update_physics(self.t, self.dt)
            self.t += self.dt
            self.accumulator -= self.dt

        # for some Updates per second (ups) measures
        self.update_render(screen, font)

    def update_render(self, screen, font):
        # rendering
        for b in self.bricks:
            b.render(screen)
        self.player.render(screen, font)

    def update_physics(self, t, dt):
        self.player.update_physics(t, dt, self.bricks)

    def add_brick(self, id, p1, p2, angle = 0):
        new_brick = Brick()
        new_brick.set_brick(p1, p2, angle)
        new_brick.id = id
        self.bricks.append(new_brick)

    def add_brick_slanted(self, id, p1, p2, angle):
        self.add_brick(id, p1, p2)
        self.bricks[id - 1].angle = angle

    def reset_player(self):
        self.player.set_position(250, 550)

    def get_new_brick_id(self):
        return len(self.bricks)
