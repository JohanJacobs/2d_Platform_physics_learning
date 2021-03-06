
# by no means perfect but learning to do physics in 2d platfomers

import pygame
import math

from world import World


def main():
    running = True
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    font = pygame.font.SysFont("monospace", 14)
    w = World()
    #w.add_brick(1, (0, 790), (800, 800), 0)

    # floor bricks
    w.add_brick(w.get_new_brick_id(), (10, 790), (200, 800), 0)
    w.add_brick(w.get_new_brick_id(), (200, 790), (400, 800), 0)
    w.add_brick(w.get_new_brick_id(), (400, 790), (600, 800), 0)
    w.add_brick(w.get_new_brick_id(), (600, 790), (800, 800), 0)
    w.add_brick(w.get_new_brick_id(), (100, 400), (700, 410), 0)
    w.add_brick(w.get_new_brick_id(), (400, 350), (790, 360), 0)

    # wall brick
    w.add_brick(w.get_new_brick_id(), (0, 0), (10, 800), 0)  # left wall
    w.add_brick(w.get_new_brick_id(), (790, 0), (800, 800), 0)  # right wall

    # horizontal bricks
    w.add_brick(w.get_new_brick_id(), (10, 500), (100, 510), 0)
    w.add_brick(w.get_new_brick_id(), (200, 600), (300, 610), 0)
    w.add_brick(w.get_new_brick_id(), (300, 600), (450, 610), 0)
    w.add_brick(w.get_new_brick_id(), (450, 600), (500, 610), 0)
    w.add_brick(w.get_new_brick_id(), (10, 700), (100, 710), 0)

    # slanted bricks

    w.add_brick(w.get_new_brick_id(), (450, 550), (500, 600), -45)
    w.add_brick(w.get_new_brick_id(), (700, 700), (790, 790), -45)
    w.add_brick(w.get_new_brick_id(), (100, 700), (190, 790), -135)
    w.add_brick(w.get_new_brick_id(), (500, 325), (550, 350), -30)
    w.add_brick(w.get_new_brick_id(), (550, 325), (600, 350), -150)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE :
                    w.player.apply_action("SPACE", "DOWN")
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    w.player.apply_action("LEFT", "DOWN")
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    w.player.apply_action("RIGHT", "DOWN")
                if event.key == pygame.K_r:
                    w.reset_player()
                if event.key == pygame.K_t:
                    w.player.set_position(400,100)
                if event.key == pygame.K_y:
                    w.player.position.y = 0

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    w.player.apply_action("SPACE", "UP")
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    w.player.apply_action("LEFT", "UP")
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    w.player.apply_action("RIGHT", "UP")
        # time step
        screen.fill((0, 0, 0))
        w.update(screen, font)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()