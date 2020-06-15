import pygame
from brick import Brick
import math


class Hotspots:
    top_left = 1
    top_mid = 2
    top_right = 3
    mid_left = 4
    mid_right = 5
    bottom_left = 6
    bottom_mid = 7
    bottom_right = 8


class Player:
    def __init__(self):
        self.position = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.accel = pygame.Vector2()

        self.orientation = math.radians(90)
        self.mu = 0.025  # drag / friction coef.
        self.mass = 75
        self.inverse_mass = 1 / self.mass
        self.max_vertical_velocity = 35
        self.max_horizontal_velocity = 25

        self.width = 20
        self.height = 20
        self.half_width = int(self.width / 2)
        self.half_height = int(self.height / 2)

        self.on_floor = False
        self.hotspot_offsets = self.create_hotspots()

        self.movement_force = 5
        self.move_left = False
        self.move_right = False
        self.move_angle = 0  # degress (0 right 180 left 90 up

        self.is_jumping = False
        self.can_jump = True
        self.jump_calc_end = 90
        self.jump_calc_count = 0.0
        self.jump_calc_count_inc = 0.2
        self.jump_force = -30

        self.boost = False
        self.boost_check_counter = 0
        self.boost_check_counter_limit = 800
        self.boost_multiplier = 2.5

        self.on_slope = False
        self.can_climb_wall = False

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y

    def set_mass(self, m):
        self.mass = m

    def render(self, screen, font):
        # draw our character for now its a block
        pygame.draw.rect(screen, (88, 136, 200), (
            self.position.x - self.half_width, self.position.y - self.half_height, self.width, self.height), 0)
        for h in self.hotspot_offsets:
            x = self.hotspot_offsets[h][0]
            y = self.hotspot_offsets[h][1]
            pygame.draw.rect(screen, (255, 0, 0), (self.position.x + x, self.position.y + y, 1, 1), 0)
        # velocity vertext
        pygame.draw.line(screen, (255, 232, 78), (self.position.x, self.position.y),
                         (self.position.x + self.velocity.x, self.position.y + self.velocity.y), 2)

    def create_hotspots(self):
        offsets = dict()
        offsets[Hotspots.top_left] = (-(self.half_width + 1), -(self.half_height + 1))
        offsets[Hotspots.top_mid] = (0, -(self.half_height + 1))
        offsets[Hotspots.top_right] = (self.half_width + 1, -(self.half_height + 1))
        offsets[Hotspots.mid_left] = (-(self.half_width + 1), 0)
        offsets[Hotspots.mid_right] = (self.half_width + 1, 0)
        offsets[Hotspots.bottom_left] = (-(self.half_width + 1), self.half_height + 1)
        offsets[Hotspots.bottom_mid] = (0, self.half_height + 1)
        offsets[Hotspots.bottom_right] = (self.half_width + 1, self.half_height + 1)
        return offsets

    def update_physics(self, delta_time, bricks):
        gravity = pygame.Vector2()

        if self.is_jumping:
            self.jump_calc_count += self.jump_calc_count_inc
            force = self.jump_force * math.cos(math.radians(self.jump_calc_count))
            self.apply_force_xy(0, force)
            if self.jump_calc_count >= self.jump_calc_end:
                self.is_jumping = False

        if self.move_left:
            self.apply_angled_force(self.movement_force, 180)
        if self.move_right:
            self.apply_angled_force(self.movement_force, 0)

        # check if we should gravity
        if not self.on_floor and not self.is_jumping:
            self.apply_angled_force(-9.8, 270)
        # if not self.on_floor and not self.is_jumping:
        #    gravity.y = 9.8
        # else:
        #    gravity.y = 0
        # self.apply_force(gravity)

        # so some friction stuff, only works when velocity is higher than nothing
        if self.velocity.magnitude() > 0 and not self.is_jumping:
            friction_vector = pygame.Vector2()
            friction_vector = -(self.velocity.normalize())
            friction_vector.scale_to_length(self.mu * self.mass)  # mass is the normal force
            self.apply_force(friction_vector)

        new_velocity = self.velocity + self.accel

        if new_velocity.x > self.max_horizontal_velocity:
            new_velocity.x = self.max_horizontal_velocity
            if self.on_floor:
                self.boost_check_counter += 1
        elif new_velocity.x < -self.max_horizontal_velocity:
            new_velocity.x = -self.max_horizontal_velocity
            if self.on_floor:
                self.boost_check_counter += 1
        else:
            self.boost_check_counter = 0

        if self.boost_check_counter >= self.boost_check_counter_limit:
            self.boost = True
        else:
            self.boost = False

        if self.boost:
            self.velocity *= delta_time  # apply the "time ratio"
            self.velocity.x *= self.boost_multiplier
        else:
            self.velocity *= delta_time  # apply the "time ratio"

        self.cap_velocity(new_velocity)

        desired_position = self.position + self.velocity

        # check if we collide with a block
        # TODO: What if we jump so much in 1 time frame that we end up jumping thru the block

        self.on_floor = False

        for b in bricks:
            # test for the right hand side
            if b.brick_point_collide((desired_position.x + self.hotspot_offsets[Hotspots.mid_right][0],
                                      desired_position.y + self.hotspot_offsets[Hotspots.mid_right][1])):
                if 0 < b.angle < 90:  # slanted brick on the right
                    self.handle_slope(b, desired_position, new_velocity)
                else:
                    self.handle_wall(b, desired_position, new_velocity)

            elif b.brick_point_collide((desired_position.x + self.hotspot_offsets[Hotspots.mid_left][0],
                                        desired_position.y + self.hotspot_offsets[Hotspots.mid_left][1])):
                # brick below on left side
                if 0 < b.angle < 90:  # slanted brick on the left
                    self.handle_slope(b, desired_position, new_velocity)
                else:
                    self.handle_wall(b, desired_position, new_velocity)

            elif b.brick_point_collide((desired_position.x + self.hotspot_offsets[Hotspots.bottom_mid][0],
                                         desired_position.y + self.hotspot_offsets[Hotspots.bottom_mid][1])) and \
                    not self.is_jumping:  # brick below us
                if 0 < b.angle < 90: # what about other angles?
                    self.handle_slope(b, desired_position, new_velocity)
                else:
                    self.handle_floor(b, desired_position, new_velocity)

            elif (b.brick_point_collide((desired_position.x + self.hotspot_offsets[Hotspots.top_left][0],
                                         desired_position.y + self.hotspot_offsets[Hotspots.top_left][1])) and
                  b.brick_point_collide((desired_position.x + self.hotspot_offsets[Hotspots.top_mid][0],
                                         desired_position.y + self.hotspot_offsets[Hotspots.top_mid][1])) and
                  b.brick_point_collide((desired_position.x + self.hotspot_offsets[Hotspots.top_right][0],
                                         desired_position.y + self.hotspot_offsets[Hotspots.top_right][
                                             1]))):
                self.handle_roof(b, desired_position, new_velocity) # brick above us

        if self.on_floor:
            self.can_jump = True

        self.position = desired_position
        self.velocity = new_velocity
        self.accel.x = 0
        self.accel.y = 0

    def handle_roof(self, b, desired_position, new_velocity):
        desired_position.y = b.get_pygame_rect()[1] + b.height + (self.half_height + 2)
        new_velocity.y = 0
        self.on_slope = False
        self.is_jumping = False
        self.on_floor = False

    def handle_floor(self, b, desired_position, new_velocity):
        desired_position.y = b.get_pygame_rect()[1] - 1 - self.half_height
        if new_velocity.y > 0:
            new_velocity.y = 0
        self.on_floor = True
        self.move_angle = 0

    def handle_wall(self, b, desired_position, new_velocity):
        if self.position.x <= b.get_pygame_rect()[0]:  # we approach wall from left
            desired_position.x = b.get_pygame_rect()[0] - self.half_width - 2
        else:  # from right
            desired_position.x = b.get_pygame_rect()[0] + b.get_pygame_rect()[2] + self.half_width + 2
        new_velocity.x = 0
        self.on_floor = False
        self.can_jump = False

    def handle_slope(self, b, desired_pos, new_velocity):
        # X-plan position in the brick
        px = desired_pos.x
        py = desired_pos.y
        bx = b.get_pygame_rect()[0]
        by = b.get_pygame_rect()[1]
        bw = b.get_pygame_rect()[2]
        bh = b.get_pygame_rect()[3]

        if bx <= px <= (bx + bw + self.half_width):
            if by <= py <= (by + bh):  # we definately are in the brick
                xdiff = px - bx  # how far are we into the brick
                ypos = math.tan(math.radians(b.angle)) * xdiff  # y location in the  brick
                new_y = by + (bh - ypos)
                self.on_floor = False
                if desired_pos.y > new_y:  # we are inside the slop so lets adjust
                    desired_pos.y = new_y
                    # desired_position.y = b.get_pygame_rect()[1] - 1 - self.half_height
                    new_velocity = new_velocity.rotate(b.angle)
                    new_velocity.y = 0
                    if not self.move_left and not self.move_right:
                        new_velocity.x = 0
                    self.on_floor = True
                    self.move_angle = b.angle
                    if self.boost:
                        self.can_climb_wall = True
                    else:
                        self.can_climb_wall = False
                else:
                    pass # adjust here also ?
            else:
                print("err:: handle_slope 1")
        else:
            print("err:: handle_slope 2")

    def cap_velocity(self, v):
        if v.y > self.max_vertical_velocity:
            v.y = self.max_horizontal_velocity
        if v.y < -self.max_vertical_velocity:
            v.y = -self.max_horizontal_velocity

    def apply_force(self, f):
        self.accel += (f * self.inverse_mass)

    def apply_angled_force(self, force, angle):
        tmp = pygame.Vector2()
        tmp.x = round(math.cos(math.radians(angle)) * force, 4)
        tmp.y = round(math.sin(math.radians(angle)) * force, 4)
        self.apply_force(tmp)

    def apply_force_xy(self, x, y):
        new_force = pygame.Vector2()
        new_force.x = x
        new_force.y = y
        self.apply_force(new_force)

    def apply_action(self, identifier, action):
        if identifier == "LEFT" and action == "DOWN":
            self.move_left = True
        if identifier == "RIGHT" and action == "DOWN":
            self.move_right = True

        if identifier == "LEFT" and action == "UP":
            self.move_left = False
        if identifier == "RIGHT" and action == "UP":
            self.move_right = False

        if identifier == "SPACE" and action == "DOWN" and self.can_jump:
            self.is_jumping = True
            self.can_jump = False
            self.on_floor = False
            self.jump_calc_count = 0

        if identifier == "SPACE" and action == "UP":
            self.is_jumping = False
