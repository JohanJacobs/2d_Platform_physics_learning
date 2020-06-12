import pygame


class physics_object:
    def __init__(self):
        self.position = pygame.Vector2()
        self.previous_position = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.acceleration = pygame.vector2()
        self.mass = 75

    def apply_force(self, force):
        self.acceleration += force * (1/self.mass)

    def update(self):
        self.previous_position = self.position

        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration.scale_to_length(0)