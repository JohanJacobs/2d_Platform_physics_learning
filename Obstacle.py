import pygame
import math


class GameObstacle:
    def __init__(self):
        self.point_list = list()
        self.position = pygame.Vector2()
        self.color = (137, 140, 148)
        self.debug_color = (229, 156, 27)
        self.angle = 0
        self.collide = False

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y

    def render(self, screen):
        color = self.color
        if self.collide:
            color = self.debug_color

        for i in range(len(self.point_list)-1):
            pygame.draw(screen, color, self.point_list[i], self.point_list[i+1], 5)
        pygame.draw(screen, color, self.point_list[0], self.point_list[len(self.point_list)], 5)