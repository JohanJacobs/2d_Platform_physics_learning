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
        self.previous_time = pygame.time.get_ticks()
        self.physics_counter = 0
        self.physics_timer = 100

    def update(self, screen, font):
        self.update_physics()
        self.update_render(screen, font)

    def update_render(self, screen, font):
        # rendering
        for b in self.bricks:
            b.render(screen)
        self.player.render(screen, font)

    def update_physics(self):
        # physics stuff
        now = pygame.time.get_ticks()
        delta_time = (now - self.previous_time) / self.physics_timer
        self.previous_time = now
        self.player.update_physics(delta_time, self.bricks)

    def add_brick(self, id, p1, p2, angle = 0):
        new_brick = Brick()
        new_brick.set_brick(p1, p2)
        new_brick.id = id
        new_brick.angle = angle
        self.bricks.append(new_brick)

    def add_brick_slanted(self, id, p1, p2, angle ):
        self.add_brick(id, p1, p2)
        self.bricks[id - 1].angle = angle

    def reset_player(self):
        self.player.set_position(250, 550)

    def get_new_brick_id(self):
        return len(self.bricks)
