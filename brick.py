import pygame


class Brick:
    def __init__(self):
        self.p1 = pygame.Vector2()
        self.p2 = pygame.Vector2()
        self.width = None
        self.height = None
        self.id = 0
        self.angle = 0
        self.collided = False

    def set_brick(self, p1, p2):
        self.p1.x, self.p1.y = p1[0], p1[1]
        self.p2.x, self.p2.y = p2[0], p2[1]
        self.width = self.p2.x - self.p1.x
        self.height = self.p2.y - self.p1.y

    def render(self, screen):
        color = (110, 102, 93)
        if self.collided:
            color = (229, 156, 27)

        if self.angle % 90 == 0:
            pygame.draw.rect(screen, color, self.get_pygame_rect(), 0)
        elif self.angle != 0:
            if self.angle == 45:
                pygame.draw.line(screen, color, (self.p1.x, self.p2.y), (self.p2.x, self.p1.y), 1)
            elif self.angle == 135:
                pygame.draw.line(screen, color, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 1)

    def get_pygame_rect(self):
        return (int(self.p1.x), int(self.p1.y), int(self.width), int(self.height))

    def brick_point_collide(self, p):
        self.collided = False
        if self.p1.x <= p[0] <= self.p2.x and \
                self.p1.y <= p[1] <= self.p2.y:
            self.collided = True
        return self.collided

    def brick_rect_collide(self, p1, p2):
        self.collided = True
        if self.p1.x >= p2.x or p1.x >= self.p2.x:
            self.collided = False
        if self.p1.y >= p2.y or p1.y >= self.p2.y:
            self.collided = False
        return self.collided
        # return True
