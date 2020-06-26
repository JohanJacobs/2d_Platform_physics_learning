import pygame
from brick import Brick
import math

# offsets identifiers for the 8 sensors around the player
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

        # physics variables
        self.orientation = math.radians(90)
        self.mu = 0.05  # drag / friction coef.
        self.mass = 50
        self.inverse_mass = 1 / self.mass
        self.gravity = pygame.math.Vector2(0, 9.8)

        # player size (bounding box)
        self.width = 20
        self.height = 20
        self.half_width = int(self.width / 2)
        self.half_height = int(self.height / 2)

        # data for the the sensors
        self.on_floor = False
        self.hotspot_offsets = dict()
        self.hotspot_offsets[Hotspots.top_left] = (-(self.half_width + 1), -(self.half_height + 1))
        self.hotspot_offsets[Hotspots.top_mid] = (0, -(self.half_height + 1))
        self.hotspot_offsets[Hotspots.top_right] = (self.half_width + 1, -(self.half_height + 1))
        self.hotspot_offsets[Hotspots.mid_left] = (-(self.half_width + 1), 0)
        self.hotspot_offsets[Hotspots.mid_right] = (self.half_width + 1, 0)
        self.hotspot_offsets[Hotspots.bottom_left] = (-(self.half_width + 1), self.half_height + 1)
        self.hotspot_offsets[Hotspots.bottom_mid] = (0, self.half_height + 1)
        self.hotspot_offsets[Hotspots.bottom_right] = (self.half_width + 1, self.half_height + 1)

        # maximum caps for physics
        self.movement_force = 5
        self.max_vertical_velocity = 3
        self.max_horizontal_velocity = 3

        # state variables for moving left and right
        self.move_left = False
        self.move_right = False
        self.move_angle = 0  # degress (0 right 180 left 90 up

        # variables used for jumping and controlling how to ascend in jump phase
        self.is_jumping = False
        self.can_jump = True
        self.jump_calc_end = 90
        self.jump_calc_count = 0.0
        self.jump_calc_count_inc = 0.03
        self.jump_force = -50

        self.on_slope = False

    def set_position(self, x, y):
        # sets the main player variable (x,y)
        # TODO: check if this is within the work bounds
        self.position.x = x
        self.position.y = y

    def set_mass(self, m):
        # TODO: check for negative mass
        self.mass = m

    def render(self, screen, font):
        # draws the information for the player.

        # draw our character for now its a block
        pygame.draw.rect(screen, (88, 136, 200), (
            self.position.x - self.half_width, self.position.y - self.half_height, self.width, self.height), 0)
        for h in self.hotspot_offsets:
            x = self.hotspot_offsets[h][0]
            y = self.hotspot_offsets[h][1]
            pygame.draw.rect(screen, (255, 0, 0), (self.position.x + x, self.position.y + y, 1, 1), 0)

        # velocity line
        pygame.draw.line(screen, (255, 232, 78), (self.position.x, self.position.y),
                         (self.position.x + self.velocity.x, self.position.y + self.velocity.y), 2)

        # Text for the player states and positions
        text = ""
        if self.can_jump:
            text = "Jump: Yes we can"
        else:
            text = "Jump: No we cant"
        textSurface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(textSurface, (50, 10))

        # player position x
        text = "player x: {}".format(self.position.x)
        textSurface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(textSurface, (50, 30))

        # player position Y
        text = "player y: {}".format(self.position.y)
        textSurface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(textSurface, (50, 50))

        # player on floor
        if self.on_floor:
            text = "on Floor"
        else:
            text = "off floor"
        textSurface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(textSurface, (50, 70))

        # velocity vector text
        text = "Velocity.x: {}".format(self.velocity.x)
        textSurface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(textSurface, (50, 90))
        text = "Velocity.y: {}".format(self.velocity.y)
        textSurface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(textSurface, (50, 110))

    def update_physics(self, t, delta_time, bricks):
        if self.is_jumping:
            # main jumping logic,
            # increase the jump counter, calculate for how much force to apply is based on the COS wave curve
            # force is applied till the COS curve returns 0 (90 degrees) then the jump sequence stops
            # early in jump bigger force is applied the longer we jump the smaller the force becomes

            self.jump_calc_count += self.jump_calc_count_inc
            force = self.jump_force * math.cos(math.radians(self.jump_calc_count))
            #self.apply_force(pygame.Vector2(0, force))
            self.apply_angled_force(force, 90)

            if self.jump_calc_count >= self.jump_calc_end:
                self.is_jumping = False

        # if the states for movement is active , apply the forces
        if self.move_left:
            self.apply_angled_force(self.movement_force, 180)
        if self.move_right:
            self.apply_angled_force(self.movement_force, 0)

        # check if we should do gravity, gravity is only applied if we are "not" on the floor
        if not self.on_floor and not self.is_jumping:
            self.apply_force(self.gravity)

        # friction stuff, only works when velocity is higher than 0, thus , moving
        if self.velocity.magnitude() > 0 and not self.is_jumping:
            friction_vector = pygame.Vector2()
            friction_vector = -(self.velocity.normalize())
            friction_vector.scale_to_length(self.mu * self.mass)  # mass is the normal force
            self.apply_force(friction_vector)

        # velocity is created based on teh various forces from applied_force functions including delta time
        new_velocity = self.velocity + (self.accel * delta_time)
        self.cap_velocity(new_velocity) # cap vertical
        # to fix a weird issue where we have a small velocity but never move
        new_velocity.x = round(new_velocity.x, 4)
        new_velocity.y = round(new_velocity.y, 4)

        desired_position = self.position + (self.velocity * delta_time) # new position
        desired_position.x= round(desired_position.x,2)
        desired_position.y = round(desired_position.y, 2)
        # check if we collide with a block
        # TODO: What if we jump so much in 1 time frame that we end up jumping thru the block?

        self.on_floor = False
        bottom_mid = (desired_position.x + self.hotspot_offsets[Hotspots.bottom_mid][0], desired_position.y + self.hotspot_offsets[Hotspots.bottom_mid][1])
        bottom_right = (desired_position.x + self.hotspot_offsets[Hotspots.bottom_right][0],
                      desired_position.y + self.hotspot_offsets[Hotspots.bottom_right][1])
        bottom_left = (desired_position.x + self.hotspot_offsets[Hotspots.bottom_left][0],
                      desired_position.y + self.hotspot_offsets[Hotspots.bottom_left][1])
        mid_right = (desired_position.x + self.hotspot_offsets[Hotspots.mid_right][0],
                     desired_position.y + self.hotspot_offsets[Hotspots.mid_right][1])
        mid_left = (desired_position.x + self.hotspot_offsets[Hotspots.mid_left][0],
                    desired_position.y + self.hotspot_offsets[Hotspots.mid_left][1])
        top_mid = (desired_position.x + self.hotspot_offsets[Hotspots.top_mid][0],
                   desired_position.y + self.hotspot_offsets[Hotspots.top_mid][1])
        top_right = (desired_position.x + self.hotspot_offsets[Hotspots.top_right][0],
                   desired_position.y + self.hotspot_offsets[Hotspots.top_right][1])
        top_left = (desired_position.x + self.hotspot_offsets[Hotspots.top_left][0],
                   desired_position.y + self.hotspot_offsets[Hotspots.top_left][1])

        collisions = dict()
        collisions[Hotspots.bottom_left] = None
        collisions[Hotspots.bottom_mid] = None
        collisions[Hotspots.bottom_right] = None
        collisions[Hotspots.top_mid] = None
        collisions[Hotspots.top_right] = None
        collisions[Hotspots.top_left] = None
        collisions[Hotspots.mid_left] = None
        collisions[Hotspots.mid_right] = None


        # prioritize floor and wall over slope,
        # prioritise wall over floor
        hitWall = False
        # bottom left, bottom right, bottom mid
        for b in bricks:
            b.clear_player_connected()
            # determine where bricks are
            if b.brick_point_collide(top_mid) and b.angle == 0:
                collisions[Hotspots.top_mid] = b
                b.player_connected = True

            if b.brick_point_collide(bottom_mid):#and b.angle == 0:
                collisions[Hotspots.bottom_mid] = b
                b.player_connected = True

            if b.brick_point_collide(top_right) and b.angle == 0:
                collisions[Hotspots.top_right] = b
                b.player_connected = True

            if b.brick_point_collide(top_left) and b.angle == 0:
                collisions[Hotspots.top_left] = b
                b.player_connected = True

        if collisions[Hotspots.top_mid] is not None:
            desired_position.y = collisions[Hotspots.top_mid].y + collisions[Hotspots.top_mid].height + (self.half_height + 2)
            self.is_jumping = False
            self.on_floor = False
            if new_velocity.y < 0:
                new_velocity.y = 0

        # if you are hitting a wall then stop
        elif collisions[Hotspots.top_right] is not None:
            desired_position.x = collisions[Hotspots.top_right].x - 1 - self.half_width
            if new_velocity.x > 0:
                new_velocity.x = 0
            #self.on_floor = True
        elif collisions[Hotspots.top_left] is not None:
            desired_position.x = collisions[Hotspots.top_left].x + collisions[Hotspots.top_left].width + 1 + self.half_width
            if new_velocity.x < 0:
                new_velocity.x = 0
            #self.on_floor = True

        # hitting a floor type
        if collisions[Hotspots.bottom_mid] is not None:
            # SLOPE
            if collisions[Hotspots.bottom_mid].angle != 0:
                radians_angle = math.radians(collisions[Hotspots.bottom_mid].angle)
                distance = round((desired_position.x - collisions[Hotspots.bottom_mid].x) * math.tan(radians_angle), 2)
                y_feet_pos = 0

                if 0 > collisions[Hotspots.bottom_mid].angle > -90:
                    y_feet_pos = collisions[Hotspots.bottom_mid].y + collisions[Hotspots.bottom_mid].height + distance - self.half_height
                if -90 > collisions[Hotspots.bottom_mid].angle > -180:
                    y_feet_pos = collisions[Hotspots.bottom_mid].y + distance - self.half_height

                if desired_position.y >= y_feet_pos:
                    desired_position.y = y_feet_pos
                    self.on_floor = True
                    if new_velocity.y > 0:
                        new_velocity.y = 0
            else:
            # Normal FLOOR1
                desired_position.y = collisions[Hotspots.bottom_mid].y - 1 - self.half_height
                self.on_floor = True
                if new_velocity.y > 0:
                    new_velocity.y = 0

#            if b.brick_point_collide(bottom_left):
#                if collisions[Hotspots.bottom_left] is None:  # its empty so lets store our brick
#                    collisions[Hotspots.bottom_left] = b
#                    b.player_connected = True
#                else:  # There is a brick if its angle and our brick is not angled, then that takes priority
#                    # check if this is a wall brick
#                    if b.brick_point_collide(mid_left) and b.slope == 0:
#                        # bottom and mid collided, its a wall it takes priority
#                        collisions[Hotspots.bottom_left] = b
#                        collisions[Hotspots.mid_left] = b
#                        b.player_connected= True
#                    elif b.angle == 0 and collisions[Hotspots.bottom_left].angle != 0 and collisions[Hotspots.mid_left] is None:
#                        collisions[Hotspots.bottom_left] = b
#                        b.player_connected = True
#
#            if b.brick_point_collide(bottom_mid):
#                if collisions[Hotspots.bottom_mid] is None:
#                    collisions[Hotspots.bottom_mid] = b
#                    b.player_connected = True
#                else:
#                    if collisions[Hotspots.bottom_mid].angle == 0 and b.angle != 0: # slopes get priority
#                        collisions[Hotspots.bottom_mid] = b
#                        b.player_connected = True
#
#            if b.brick_point_collide(bottom_right):
#                if collisions[Hotspots.bottom_right] is None:  # its empty so lets store our brick
#                    collisions[Hotspots.bottom_right] = b
#                    b.player_connected = True
#                else:  # There is a brick if its angle and our brick is not angled, then that takes priority
#                    if b.brick_point_collide(mid_right):
#                        collisions[Hotspots.bottom_right] = b
#                        b.player_connected = True
#                    elif b.angle == 0 and collisions[Hotspots.bottom_right].angle != 0:
#                        collisions[Hotspots.bottom_right] = b
#                        b.player_connected = True

#            if b.brick_point_collide(top_mid):
#                collisions[Hotspots.top_mid] = b


#        # handle the bricks now
#        if collisions[Hotspots.top_mid] is not None and b.angle == 0:
#            self.handle_roof(collisions[Hotspots.top_mid], desired_position, new_velocity)
#        elif collisions[Hotspots.bottom_right] is not None:
#            if collisions[Hotspots.bottom_right].angle == 0:
#                self.handle_brick(collisions[Hotspots.bottom_right], desired_position, new_velocity)
#            else:
#                self.handle_slope(collisions[Hotspots.bottom_right], desired_position, new_velocity)
#        elif collisions[Hotspots.bottom_left] is not None:
#            if collisions[Hotspots.bottom_left].angle ==0:
#                self.handle_brick(collisions[Hotspots.bottom_left], desired_position, new_velocity)
#            else:
#                self.handle_slope(collisions[Hotspots.bottom_left], desired_position, new_velocity)
#        elif collisions[Hotspots.bottom_mid] is not None:
#            self.handle_brick(collisions[Hotspots.bottom_mid],desired_position,new_velocity)
#

#            if b.brick_point_collide(bottom_left) or b.brick_point_collide(bottom_right): # our feet sensors hit something
#                b.player_connected = True
#                if b.brick_point_collide(top_left) or b.brick_point_collide(top_right): # this is a wall
#                    if b.angle == 135 or b.angle == 45:
#                        self.handle_slope(b, desired_position, new_velocity)
#                    else:
#                        self.handle_wall(b, desired_position, new_velocity)
#                else:
#                    if b.angle == 135 or b.angle == 45:
#                        self.handle_slope(b,desired_position,new_velocity)
#                    else:
#                        self.handle_floor(b,desired_position,new_velocity)
#            elif b.brick_point_collide(top_right) or b.brick_point_collide(top_left) or b.brick_point_collide(top_mid):
#                b.player_connected = True
#                self.handle_roof(b,desired_position,new_velocity)

            #if b.brick_point_collide(bottom_mid):  # hit a brick below us : floor (sensor)
            #    if b.angle == 0:
            #        self.handle_floor(b, desired_position, new_velocity)
            #    elif b.angle == 45 or b.angle == 135:
            #        self.handle_slope(b, desired_position, new_velocity)
            ## brick on the left or right of us (sensor based )
            #elif (b.brick_point_collide(mid_right) or b.brick_point_collide(mid_left)) and (b.angle % 90 == 0):
            #    self.handle_wall(b, desired_position, new_velocity)
            ## bricks above us.
            #elif b.brick_point_collide(top_mid):
            #    self.handle_roof(b, desired_position, new_velocity)  # roof above us

        # enable jumping if player is on asurface (floor)
        if self.on_floor:
            self.can_jump = True
        else:
            self.can_jump = False

        # updated the player position with the new modified positions
        self.position = desired_position
        self.velocity = new_velocity

        # reset acceleration
        self.accel.x = 0
        self.accel.y = 0

    def handle_brick(self, b, desired_position, new_velocity):
        # check if this is a wall (same brick will touch mid
        self.on_floor = True
        mid_right = (desired_position.x + self.hotspot_offsets[Hotspots.mid_right][0],
                     desired_position.y + self.hotspot_offsets[Hotspots.mid_right][1])
        mid_left = (desired_position.x + self.hotspot_offsets[Hotspots.mid_left][0],
                    desired_position.y + self.hotspot_offsets[Hotspots.mid_left][1])

        if b.brick_point_collide(mid_right):
                # we are hitting a wall on the right
                new_velocity.x = 0
                desired_position.x = b.get_pygame_rect()[0] - self.half_width - 1
                print("wall")
        elif b.brick_point_collide(mid_left):
                new_velocity.x = 0
                desired_position.x = b.get_pygame_rect()[0] + b.get_pygame_rect()[2] + self.half_width + 1
                print("Wall")
        else:
            # we are on a floor do the floor routine
            self.handle_floor(b, desired_position, new_velocity)

    def handle_roof(self, b, desired_position, new_velocity):
        # a roof brick  was triggered for the player,
        # check if the position + top offset is inside the brick and move the player back outside
        if b is None:
            return

        desired_position.y = b.get_pygame_rect()[1] + b.height + (self.half_height + 2)
        new_velocity.y = 0
        self.is_jumping = False
        self.on_floor = False

    def handle_floor(self, b, desired_position, new_velocity):
        # handle_floor: Cap the Y location to the floor and remove all y-Axis velocity if it is positive to avoid moving further into the brick
        # inputs:
        # b: is a brick data structure to extract the "clamp" too y location
        # desired_position: the tested sensor location to be modified
        # new_velocity: velocity vector to be modified
        if b is None:
            return
        desired_position.y = b.get_pygame_rect()[1] - 1 - self.half_height
        if new_velocity.y > 0:
            new_velocity.y = 0
        self.on_floor = True

    def handle_wall(self, b, desired_position, new_velocity):
        # handle_wall: cap the x location against the wall and remove velocity in the x direction
        # inputs:
        #   b: the brick structure which is the wall that was collided with
        #   desired_position: the sensor location that needs to be modified.
        #   new_velocity: the velocity vector data  that needs to be modified
        if b is None:
            return
        if new_velocity.x > 0:  # we approach wall from left
            desired_position.x = b.get_pygame_rect()[0] - self.half_width - 2
        else:  # from right
            desired_position.x = b.get_pygame_rect()[0] + b.get_pygame_rect()[2] + self.half_width + 2
        new_velocity.x = 0
        self.on_floor = False
        self.can_jump = False

    def handle_slope(self, b, desired_pos, new_velocity):
        if b is None:
            return
        # X-plan position in the brick
        feetOffset = self.hotspot_offsets[Hotspots.bottom_mid][1] + 1
        px = desired_pos.x
        py = desired_pos.y + feetOffset  # location of the feet
        bx = b.get_pygame_rect()[0]
        by = b.get_pygame_rect()[1]
        bw = b.get_pygame_rect()[2]
        bh = b.get_pygame_rect()[3]

        # calculate the Y axis value we can't cross as its a slope
        # for 45 degress
        xdiff = 0
        if b.angle == 45:
            xdiff = px - bx  # how deep are we in the block
        elif b.angle == 135:
            xdiff = (bx+bw) - px

        angle = 45
        radians_angle = math.radians(angle)  # the angle
        y_offset = math.tan(radians_angle) * xdiff
        ylimit = round(by + (bh - y_offset), 0)

        if (py) > ylimit:
            self.on_floor = True
            desired_pos.y = ylimit - feetOffset + 1
            self.move_angle = b.angle
            new_velocity.y = 0

    def cap_velocity(self, v):
        # check that velocity is within the predefined parameters
        # inputs
        #   v : a vector2 representing the x/y velocity of the character.

        if v.x > self.max_horizontal_velocity:
            v.x = self.max_horizontal_velocity
        elif v.x < -self.max_horizontal_velocity:
            v.x = -self.max_horizontal_velocity

        if v.y > self.max_vertical_velocity:
            v.y = self.max_vertical_velocity
        if v.y < -self.max_vertical_velocity:
            v.y = -self.max_vertical_velocity

        if abs(v.x) >0 and abs(v.x) < 0.001:
            v.x = 0
        if abs(v.y) >0 and abs(v.y) < 0.001:
            v.y = 0

    def apply_force(self, f):
        # applies a force to the acceleration vector . using F=ma thus a = F*(1/m)
        self.accel += (f * self.inverse_mass)

    def apply_angled_force(self, force, angle):
        # applies a force at an angle to the acceleration vector . using F=ma thus a = F*(1/m)
        tmp = pygame.Vector2()
        tmp.x = round(math.cos(math.radians(angle)) * force, 4)
        tmp.y = round(math.sin(math.radians(angle)) * force, 4)
        self.apply_force(tmp)

    def apply_action(self, identifier, action):
        # actions are pushed to the character through this function to keep it all in one place.
        # ##Not sure if this is a good idea.

        if identifier == "LEFT" and action == "DOWN":
            self.move_left = True
            return
        if identifier == "RIGHT" and action == "DOWN":
            self.move_right = True
            return
        if identifier == "LEFT" and action == "UP":
            self.move_left = False
            return
        if identifier == "RIGHT" and action == "UP":
            self.move_right = False
            return

        if identifier == "SPACE" and action == "DOWN" and self.can_jump:
            self.is_jumping = True
            self.can_jump = False
            self.on_floor = False
            self.jump_calc_count = 0
            return

        if identifier == "SPACE" and action == "UP":
            self.is_jumping = False
            return