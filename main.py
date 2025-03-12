import pygame
import math
import sys
import random
import os

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.max_speed = 6
        self.acceleration = 0.2
        self.rotation = 0
        self.size = (32, 16)
        self.rect = pygame.Rect(x - self.size[0]/2, y - self.size[1]/2, self.size[0], self.size[1])
        # More varied and realistic car colors
        self.color = random.choice([
            (200, 0, 0),    # Red
            (0, 0, 200),    # Blue
            (40, 40, 40),   # Dark Gray
            (200, 200, 200),# Silver
            (255, 255, 255),# White
            (0, 100, 0),    # Dark Green
        ])
        self.stolen = False  # Flag to track if vehicle was stolen

    def move(self, forward, turn, walls):
        # Update speed based on acceleration and direction
        if forward != 0:  # Using forward as a value (-1 for reverse, 1 for forward)
            target_speed = forward * self.max_speed
            self.speed = min(max(self.speed + (self.acceleration * forward), -self.max_speed), self.max_speed)
        else:
            # Apply gradual deceleration when no forward/backward input
            if abs(self.speed) > self.acceleration:
                self.speed -= (self.acceleration * (1 if self.speed > 0 else -1))
            else:
                self.speed = 0

        # Update rotation with speed-dependent turning
        if turn:
            # Reduce turn rate at higher speeds
            turn_rate = 3 * (1 - (abs(self.speed) / self.max_speed) * 0.5)
            self.rotation += turn * turn_rate
            self.rotation %= 360

        # Calculate movement vector
        angle = math.radians(self.rotation)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed

        # Update position
        new_x = self.x + dx
        new_y = self.y + dy

        # Update rectangle for collision detection
        new_rect = pygame.Rect(new_x - self.size[0]/2, new_y - self.size[1]/2, self.size[0], self.size[1])

        # Check collision
        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall["rect"]):
                can_move = False
                self.speed = 0
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect = new_rect

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Only draw if vehicle is on screen (with some margin)
        screen_rect = screen.get_rect()
        if (screen_x + self.size[0] < -50 or screen_x - self.size[0] > screen_rect.width + 50 or
            screen_y + self.size[1] < -50 or screen_y - self.size[1] > screen_rect.height + 50):
            return

        # Create a surface for the rotated car with proper alpha
        car_surface = pygame.Surface(self.size, pygame.SRCALPHA)

        # Draw the vehicle body
        pygame.draw.rect(car_surface, self.color, (0, 0, self.size[0], self.size[1]))

        # Add windows (black rectangles with transparency)
        window_color = (30, 30, 30, 200)
        window_width = self.size[0] // 4
        window_height = self.size[1] // 2

        # Front window
        pygame.draw.rect(car_surface, window_color, 
                        (self.size[0] - window_width - 4, 2, window_width, window_height))
        # Back window
        pygame.draw.rect(car_surface, window_color,
                        (4, 2, window_width, window_height))

        # Add headlights and taillights
        light_size = 3
        if self.rotation in [0, 180]:  # Horizontal orientation
            # Headlights (white)
            pygame.draw.rect(car_surface, (255, 255, 200),
                           (self.size[0] - light_size - 1, 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 255, 200),
                           (self.size[0] - light_size - 1, self.size[1] - light_size - 2, light_size, light_size))
            # Taillights (red)
            pygame.draw.rect(car_surface, (255, 0, 0),
                           (1, 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 0, 0),
                           (1, self.size[1] - light_size - 2, light_size, light_size))

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(car_surface, -self.rotation)

        # Draw the rotated vehicle
        screen.blit(rotated_surface, (screen_x - rotated_surface.get_width()/2,
                                    screen_y - rotated_surface.get_height()/2))

class PoliceVehicle(Vehicle):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0, 0, 150)  # Police blue
        self.max_speed = 7  # Slightly faster than regular vehicles
        self.target = None
        self.state = "patrol"  # patrol, chase
        self.patrol_timer = random.randint(50, 150)
        self.patrol_turn = 0
        self.siren_active = False
        self.siren_timer = 0
        self.siren_colors = [(255, 0, 0), (0, 0, 255)]  # Red and blue
        self.current_siren = 0

    def update_ai(self, player, walls, roads):
        # If player committed a crime and is nearby, chase them
        distance_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)

        # Check if player is in a stolen vehicle or has fired a weapon recently
        crime_committed = (player.in_vehicle and player.in_vehicle.stolen) or player.wanted_level > 0

        if crime_committed and distance_to_player < 500:
            self.state = "chase"
            self.target = player
            self.siren_active = True
        elif self.state == "chase" and distance_to_player > 800:
            # Lost the player
            self.state = "patrol"
            self.target = None
            self.siren_active = False

        # Update siren animation
        if self.siren_active:
            self.siren_timer += 1
            if self.siren_timer > 15:  # Switch siren color every 15 frames
                self.siren_timer = 0
                self.current_siren = 1 - self.current_siren  # Toggle between 0 and 1

        # AI Behavior
        if self.state == "chase" and self.target:
            # Calculate angle to target
            target_angle = math.degrees(math.atan2(
                self.target.y - self.y,
                self.target.x - self.x
            )) % 360

            # Determine fastest rotation direction
            angle_diff = (target_angle - self.rotation) % 360
            if angle_diff > 180:
                turn = -1  # Turn left
            else:
                turn = 1   # Turn right

            if abs(angle_diff) < 10 or abs(angle_diff) > 350:
                turn = 0  # Pretty much on target, don't turn

            # Move forward at full speed during chase
            forward = 1

            super().move(forward, turn, walls)
        else:
            # Patrol behavior - follow roads and make occasional turns
            self.patrol_timer -= 1

            if self.patrol_timer <= 0:
                self.patrol_timer = random.randint(50, 150)
                self.patrol_turn = random.choice([-1, 0, 1])

            # Find nearest road and align with it
            on_road = False
            for road in roads:
                if road["rect"].collidepoint(self.x, self.y):
                    on_road = True
                    # Determine if we should align to road direction
                    if road["horizontal"] and (self.rotation < 45 or self.rotation > 315 or 
                                              (self.rotation > 135 and self.rotation < 225)):
                        # Already aligned with horizontal road
                        super().move(0.5, self.patrol_turn, walls)
                    elif not road["horizontal"] and (self.rotation > 45 and self.rotation < 135 or 
                                                   self.rotation > 225 and self.rotation < 315):
                        # Already aligned with vertical road
                        super().move(0.5, self.patrol_turn, walls)
                    else:
                        # Need to align with road
                        if road["horizontal"]:
                            target_angle = 0 if random.random() > 0.5 else 180
                        else:
                            target_angle = 90 if random.random() > 0.5 else 270

                        # Determine turn direction to reach target angle
                        angle_diff = (target_angle - self.rotation) % 360
                        turn = 1 if angle_diff < 180 else -1

                        super().move(0.3, turn, walls)
                    break

            if not on_road:
                # Not on a road, try to find one
                super().move(0.3, random.choice([-1, 0, 1]), walls)

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)

        # Draw siren lights if active
        if self.siren_active:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y

            # Create a surface for the siren with proper alpha
            siren_surface = pygame.Surface((10, 6), pygame.SRCALPHA)

            # Draw the siren lights on top of the car
            pygame.draw.circle(siren_surface, self.siren_colors[self.current_siren], (3, 3), 3)
            pygame.draw.circle(siren_surface, self.siren_colors[1-self.current_siren], (7, 3), 3)

            # Rotate the surface with the car
            rotated_siren = pygame.transform.rotate(siren_surface, -self.rotation)

            # Calculate offset to place siren on top of car
            angle = math.radians(self.rotation)
            offset_x = math.cos(angle+math.pi/2) * 10
            offset_y = math.sin(angle+math.pi/2) * 10

            # Draw the siren
            screen.blit(rotated_siren, (
                screen_x - rotated_siren.get_width()/2 + offset_x,
                screen_y - rotated_siren.get_height()/2 + offset_y
            ))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.size = 16
        self.rect = pygame.Rect(x - self.size/2, y - self.size/2, self.size, self.size)
        self.direction = 'down'
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.colors = {
            'skin': (255, 223, 196),     # Lighter skin tone
            'shirt': (200, 0, 0),        # Red shirt
            'pants': (0, 0, 150),        # Dark blue pants
            'shoes': (40, 40, 40),       # Dark shoes
            'eyes': (0, 0, 0)            # Black eyes
        }
        self.in_vehicle = None
        self.vehicle_entry_cooldown = 0

        # Weapon system
        self.has_weapon = True  # Player starts with a weapon
        self.shooting = False
        self.shoot_cooldown = 0
        self.bullet_speed = 10
        self.bullets = []

        # Wanted system
        self.wanted_level = 0
        self.wanted_cooldown = 0

    def move(self, dx, dy, walls):
        # Update direction based on movement
        if dx != 0 or dy != 0:  # Only update direction if there's movement
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            self.moving = True
        else:
            self.moving = False

        # Calculate new position
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Update animation
        if self.moving:
            self.animation_frame = (self.animation_frame + self.animation_speed) % 4
        else:
            self.animation_frame = 0

        # Update rectangle for collision detection
        new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)

        # Check collision with walls
        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall["rect"]): #Corrected this line
                can_move = False
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect = new_rect

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Create a surface for the character with transparency
        char_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        # Animation offsets
        walk_offset = math.sin(self.animation_frame * math.pi) * 2 if self.moving else 0
        head_bob = math.sin(self.animation_frame * math.pi * 2) * 1.5  # South Park style head bob

        # Draw character from top-down perspective
        # Head (South Park Canadian style)
        head_top = self.size - head_bob
        head_bottom = self.size + head_bob
        head_width = self.size * 0.8

        # Top of head
        pygame.draw.ellipse(
            char_surface,
            self.colors['skin'],
            (self.size - head_width/2, head_top - head_width/2, head_width, head_width)
        )

        # Bottom of head
        pygame.draw.ellipse(
            char_surface,
            self.colors['skin'],
            (self.size - head_width/2, head_bottom - head_width/2, head_width * 0.8, head_width * 0.4)
        )

        # Beady eyes
        eye_size = 2
        eye_spacing = 4
        pygame.draw.circle(
            char_surface,
            self.colors['eyes'],
            (self.size - eye_spacing, self.size),
            eye_size
        )
        pygame.draw.circle(
            char_surface,
            self.colors['eyes'],
            (self.size + eye_spacing, self.size),
            eye_size
        )

        # Body (simple oval shape)
        body_points = [
            (self.size - self.size * 0.3, self.size + head_width * 0.3),    # Top left
            (self.size + self.size * 0.3, self.size + head_width * 0.3),    # Top right
            (self.size + self.size * 0.4, self.size + self.size * 0.6),     # Bottom right
            (self.size - self.size * 0.4, self.size + self.size * 0.6)      # Bottom left
        ]
        pygame.draw.polygon(char_surface, self.colors['shirt'], body_points)

        # Legs with walking animation
        if self.moving:
            leg_offset = walk_offset * 1.5
            # Left leg
            left_leg = [
                (self.size - self.size * 0.25, self.size + self.size * 0.5),
                (self.size - self.size * 0.15, self.size + self.size * 0.5),
                (self.size - self.size * 0.2 + leg_offset, self.size + self.size * 0.8),
                (self.size - self.size * 0.3 + leg_offset, self.size + self.size * 0.8)
            ]
            # Right leg
            right_leg = [
                (self.size + self.size * 0.15, self.size + self.size * 0.5),
                (self.size + self.size * 0.25, self.size + self.size * 0.5),
                (self.size + self.size * 0.3 - leg_offset, self.size + self.size * 0.8),
                (self.size + self.size * 0.2 - leg_offset, self.size + self.size * 0.8)
            ]
            pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
            pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

            # Shoes
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size - self.size * 0.25 + leg_offset, self.size + self.size * 0.8), 3)
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size + self.size * 0.25 - leg_offset, self.size + self.size * 0.8), 3)
        else:
            # Standing still legs
            left_leg = [
                (self.size - self.size * 0.25, self.size + self.size * 0.5),
                (self.size - self.size * 0.15, self.size + self.size * 0.5),
                (self.size - self.size * 0.2, self.size + self.size * 0.8),
                (self.size - self.size * 0.3, self.size + self.size * 0.8)
            ]
            right_leg = [
                (self.size + self.size * 0.15, self.size + self.size * 0.5),
                (self.size + self.size * 0.25, self.size + self.size * 0.5),
                (self.size + self.size * 0.3, self.size + self.size * 0.8),
                (self.size + self.size * 0.2, self.size + self.size * 0.8)
            ]
            pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
            pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

            # Shoes
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size - self.size * 0.25, self.size + self.size * 0.8), 3)
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size + self.size * 0.25, self.size + self.size * 0.8), 3)

        # Draw weapon if player has one and not in vehicle
        if self.has_weapon and not self.in_vehicle:
            # Calculate weapon position based on direction
            if self.direction == 'right':
                weapon_x = self.size + self.size * 0.5
                weapon_y = self.size + self.size * 0.2
                weapon_angle = 0
            elif self.direction == 'left':
                weapon_x = self.size - self.size * 0.5
                weapon_y = self.size + self.size * 0.2
                weapon_angle = 180
            elif self.direction == 'up':
                weapon_x = self.size
                weapon_y = self.size - self.size * 0.4
                weapon_angle = 270
            else:  # down
                weapon_x = self.size
                weapon_y = self.size + self.size * 0.6
                weapon_angle = 90

            # Draw the weapon (simple rectangle)
            weapon_length = 8
            weapon_width = 3
            weapon_surface = pygame.Surface((weapon_length, weapon_width), pygame.SRCALPHA)
            pygame.draw.rect(weapon_surface, (80, 80, 80), (0, 0, weapon_length, weapon_width))

            # Rotate weapon based on direction
            rotated_weapon = pygame.transform.rotate(weapon_surface, -weapon_angle)

            # Draw weapon on character
            char_surface.blit(rotated_weapon, 
                            (weapon_x - rotated_weapon.get_width()/2, 
                             weapon_y - rotated_weapon.get_height()/2))

        # Apply character direction
        if self.direction == 'left':
            char_surface = pygame.transform.flip(char_surface, True, False)

        # Draw the character surface onto the screen
        screen.blit(char_surface, 
                   (screen_x - char_surface.get_width()/2,
                    screen_y - char_surface.get_height()/2))

    def enter_exit_vehicle(self, vehicles):
        if self.vehicle_entry_cooldown > 0:
            return

        if self.in_vehicle:
            # Exit vehicle
            self.x = self.in_vehicle.x + math.cos(math.radians(self.in_vehicle.rotation)) * 40
            self.y = self.in_vehicle.y + math.sin(math.radians(self.in_vehicle.rotation)) * 40
            self.rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
            self.in_vehicle = None
            self.vehicle_entry_cooldown = 30
        else:
            # Try to enter nearest vehicle
            for vehicle in vehicles:
                dist = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
                if dist < 50:  # Entry range
                    self.in_vehicle = vehicle
                    if not isinstance(vehicle, PoliceVehicle):  # Can't steal police cars
                        vehicle.stolen = True
                        self.wanted_level += 1  # Increase wanted level when stealing a car
                    self.vehicle_entry_cooldown = 30
                    break

    def shoot(self):
        if not self.has_weapon or self.in_vehicle or self.shoot_cooldown > 0:
            return

        self.shooting = True
        self.shoot_cooldown = 20  # Cooldown between shots

        # Calculate bullet starting position and velocity based on player direction
        if self.direction == 'right':
            angle = 0
        elif self.direction == 'left':
            angle = 180
        elif self.direction == 'up':
            angle = 270
        else:  # down
            angle = 90

        # Calculate bullet velocity
        bullet_dx = math.cos(math.radians(angle)) * self.bullet_speed
        bullet_dy = math.sin(math.radians(angle)) * self.bullet_speed

        # Create bullet starting slightly away from player in direction they're facing
        start_x = self.x + math.cos(math.radians(angle)) * (self.size + 5)
        start_y = self.y + math.sin(math.radians(angle)) * (self.size + 5)

        # Add bullet to list
        self.bullets.append({
            "x": start_x,
            "y": start_y,
            "dx": bullet_dx,
            "dy": bullet_dy,
            "life": 60  # Bullet disappears after 60 frames
        })

        # Shooting increases wanted level
        self.wanted_level += 0.2

    def update(self):
        if self.vehicle_entry_cooldown > 0:
            self.vehicle_entry_cooldown -= 1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update bullets
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            bullet["life"] -= 1

            if bullet["life"] <= 0:
                self.bullets.remove(bullet)

        # Update wanted level
        if self.wanted_cooldown > 0:
            self.wanted_cooldown -= 1
        elif self.wanted_level > 0:
            self.wanted_level = max(0, self.wanted_level - 0.001)  # Gradually decrease wanted level

    def draw_bullets(self, screen, camera_x, camera_y):
        for bullet in self.bullets:
            screen_x = bullet["x"] - camera_x
            screen_y = bullet["y"] - camera_y

            # Only draw if bullet is on screen
            screen_rect = screen.get_rect()
            if (screen_x < 0 or screen_x > screen_rect.width or
                screen_y < 0 or screen_y > screen_rect.height):
                continue

            # Draw bullet
            pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 2)

    def draw_wanted_level(self, screen):
        if self.wanted_level > 0:
            # Draw wanted stars in top-left corner
            star_count = min(5, int(self.wanted_level))
            for i in range(star_count):
                # Draw a simple star (or just use text for now)
                font = pygame.font.SysFont(None, 30)
                star_text = font.render("★", True, (255, 255, 0))
                screen.blit(star_text, (10 + i * 25, 10))

class Pedestrian:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.5, 1.5)
        self.size = 16
        self.rect = pygame.Rect(x - self.size/2, y - self.size/2, self.size, self.size)
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.moving = True
        self.animation_frame = random.random() * 4  # Randomize starting frame
        self.animation_speed = random.uniform(0.1, 0.3)  # Randomize animation speed

        # Randomize appearance
        self.colors = {
            'skin': random.choice([
                (255, 223, 196),  # Light skin
                (240, 200, 170),  # Medium skin
                (190, 140, 110),  # Darker skin
            ]),
            'shirt': random.choice([
                (200, 0, 0),      # Red
                (0, 100, 200),    # Blue
                (0, 150, 0),      # Green
                (200, 200, 0),    # Yellow
                (150, 0, 150),    # Purple
                (255, 255, 255),  # White
            ]),
            'pants': random.choice([
                (0, 0, 150),      # Blue jeans
                (40, 40, 40),     # Black pants
                (100, 80, 60),    # Brown pants
                (80, 80, 80),     # Gray pants
            ]),
            'shoes': (40, 40, 40),  # Dark shoes
            'eyes': (0, 0, 0)       # Black eyes
        }

        # AI behavior variables
        self.ai_state = "wander"  # wander, flee, wait
        self.ai_timer = random.randint(30, 120)  # Time before changing direction or behavior
        self.flee_target = None
        self.health = 1  # 0 = dead
        self.is_dead = False
        self.dead_timer = 0

    def check_collision(self, obj_rect):
        return self.rect.colliderect(obj_rect)

    def update_ai(self, player, walls, roads, vehicles, bullets, other_pedestrians):
        if self.is_dead:
            self.dead_timer += 1
            if self.dead_timer > 600:  # Despawn after 10 seconds
                return True  # Signal to remove this pedestrian
            return False

        # Check for bullet hits
        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet["x"] - 2, bullet["y"] - 2, 4, 4)
            if self.rect.colliderect(bullet_rect):
                self.health = 0
                self.is_dead = True
                bullets.remove(bullet)
                # Shooting pedestrians increases wanted level significantly
                player.wanted_level += 2
                return False

        # Check for vehicle collisions (hit by car)
        for vehicle in vehicles:
            if self.rect.colliderect(vehicle.rect):
                if vehicle.speed > 2:  # Only die if car is moving somewhat fast
                    self.health = 0
                    self.is_dead = True
                    # Being run over increases wanted level
                    if vehicle == player.in_vehicle:
                        player.wanted_level += 1
                    return False

        # Update AI state timer
        self.ai_timer -= 1
        if self.ai_timer <= 0:
            if self.ai_state == "wander":
                # Randomly choose a new direction or wait
                self.direction = random.choice(['up', 'down', 'left', 'right'])
                self.ai_state = random.choice(["wander", "wander", "wander", "wait"])
                self.ai_timer = random.randint(30, 120)
            elif self.ai_state == "wait":
                # Resume wandering
                self.ai_state = "wander"
                self.ai_timer = random.randint(30, 120)
            elif self.ai_state == "flee":
                # Continue fleeing or return to wandering if far enough
                if not self.flee_target or random.random() < 0.2:
                    self.ai_state = "wander"
                self.ai_timer = random.randint(20, 60)

        # Check for player with gun or nearby shooting
        if player.has_weapon and not player.in_vehicle and self.distance_to(player) < 150:
            self.ai_state = "flee"
            self.flee_target = player
            self.ai_timer = random.randint(40, 80)

        # Also flee from vehicles moving fast
        for vehicle in vehicles:
            if vehicle.speed > 3 and self.distance_to_pos(vehicle.x, vehicle.y) < 80:
                self.ai_state = "flee"
                self.flee_target = vehicle
                self.ai_timer = random.randint(30,60)

        # Execute behavior based onstate
        if self.ai_state == "wander":
            self.moving = True
            # Try to follow roads if on them
            on_sidewalk = False
            for road in roads:
                road_rect = road["rect"]
                # Check if pedestrian is near road edge (sidewalk)
                sidewalk_width = 10
                road_inner = pygame.Rect(
                    road_rect.x + sidewalk_width, 
                    road_rect.y + sidewalk_width,
                    road_rect.width - sidewalk_width * 2,
                    road_rect.height - sidewalk_width * 2
                )

                if road_rect.collidepoint(self.x, self.y) and not road_inner.collidepoint(self.x, self.y):
                    on_sidewalk = True
                    # Follow road direction
                    if road["horizontal"]:
                        if random.random() < 0.8:  # 80% chance to follow road
                            self.direction = 'left' if random.random() < 0.5 else 'right'
                    else:  # vertical road
                        if random.random() < 0.8:  # 80% chance to follow road
                            self.direction = 'up' if random.random() < 0.5 else 'down'

            # Move in current direction
            if self.direction == 'right':
                new_x = self.x + self.speed
                new_y = self.y
            elif self.direction == 'left':
                new_x = self.x - self.speed
                new_y = self.y
            elif self.direction == 'up':
                new_x = self.x
                new_y = self.y - self.speed
            else:  # down
                new_x = self.x
                new_y = self.y + self.speed

            # Update collision rect
            new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)

            # Check collision with walls
            can_move = True
            for wall in walls:
                if new_rect.colliderect(wall["rect"]):
                    can_move = False
                    # Change direction when hitting wall
                    self.direction = random.choice(['up', 'down', 'left', 'right'])
                    break

            # Check collision with other pedestrians
            for ped in other_pedestrians:
                if ped != self and new_rect.colliderect(ped.rect):
                    can_move = False
                    # Small chance to change direction when colliding with other pedestrians
                    if random.random() < 0.3:
                        self.direction = random.choice(['up', 'down', 'left', 'right'])
                    break

            if can_move:
                self.x = new_x
                self.y = new_y
                self.rect = new_rect

        elif self.ai_state == "wait":
            self.moving = False

        elif self.ai_state == "flee":
            self.moving = True

            if self.flee_target:
                # Calculate vector away from threat
                dx = self.x - self.flee_target.x
                dy = self.y - self.flee_target.y

                # Normalize vector
                length = math.sqrt(dx**2 + dy**2)
                if length > 0:
                    dx /= length
                    dy /= length

                # Determine flee direction
                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'

                # Move in flee direction
                new_x = self.x + dx * self.speed * 1.5  # Flee faster
                new_y = self.y + dy * self.speed * 1.5

                # Update collision rect
                new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)

                # Check collision with walls
                can_move = True
                for wall in walls:
                    if new_rect.colliderect(wall["rect"]):
                        can_move = False
                        # Try another direction when fleeing
                        if abs(dx) > abs(dy):
                            self.direction = random.choice(['up', 'down'])
                        else:
                            self.direction = random.choice(['left', 'right'])
                        break

                if can_move:
                    self.x = new_x
                    self.y = new_y
                    self.rect = new_rect

        # Update animation frame
        if self.moving:
            self.animation_frame = (self.animation_frame + self.animation_speed) % 4

        return False  # Not to be removed

    def distance_to(self, entity):
        return math.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)

    def distance_to_pos(self, x, y):
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Only draw if on screen
        screen_rect = screen.get_rect()
        if (screen_x + self.size < 0 or screen_x - self.size > screen_rect.width or
            screen_y + self.size < 0 or screen_y - self.size > screen_rect.height):
            return

        # Create a surface for the character with transparency
        char_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        if self.is_dead:
            # Draw dead pedestrian (lying on ground)
            pygame.draw.ellipse(
                char_surface,
                self.colors['shirt'],
                (self.size - self.size * 0.8, self.size - self.size * 0.4, self.size * 1.6, self.size * 0.8)
            )
            # Head
            pygame.draw.circle(
                char_surface,
                self.colors['skin'],
                (self.size - self.size * 0.5, self.size),
                self.size * 0.3
            )
            # Blood puddle
            pygame.draw.ellipse(
                char_surface,
                (150, 0, 0, 180),  # Semi-transparent red
                (self.size - self.size * 0.9, self.size - self.size * 0.5, self.size * 1.8, self.size)
            )

            # Rotate randomly for varied death poses
            seed = hash(f"{self.x}_{self.y}") % 360  # Consistent rotation based on position
            char_surface = pygame.transform.rotate(char_surface, seed)

        else:
            # Animation offsets
            walk_offset = math.sin(self.animation_frame * math.pi) * 2 if self.moving else 0
            head_bob = math.sin(self.animation_frame * math.pi * 2) * 1.5  # South Park style head bob

            # Draw character from top-down perspective
            # Head (South Park Canadian style)
            head_top = self.size - head_bob
            head_bottom = self.size + head_bob
            head_width = self.size * 0.7  # Slightly smaller than player

            # Top of head
            pygame.draw.ellipse(
                char_surface,
                self.colors['skin'],
                (self.size - head_width/2, head_top - head_width/2, head_width, head_width)
            )

            # Bottom of head
            pygame.draw.ellipse(
                char_surface,
                self.colors['skin'],
                (self.size - head_width/2, head_bottom - head_width/2, head_width * 0.8, head_width * 0.4)
            )

            # Beady eyes
            eye_size = 2
            eye_spacing = 4
            pygame.draw.circle(
                char_surface,
                self.colors['eyes'],
                (self.size - eye_spacing, self.size),
                eye_size
            )
            pygame.draw.circle(
                char_surface,
                self.colors['eyes'],
                (self.size + eye_spacing, self.size),
                eye_size
            )

            # Body (simple oval shape)
            body_points = [
                (self.size - self.size * 0.3, self.size + head_width * 0.3),    # Top left
                (self.size + self.size * 0.3, self.size + head_width * 0.3),    # Top right
                (self.size + self.size * 0.4, self.size + self.size * 0.6),     # Bottom right
                (self.size - self.size * 0.4, self.size + self.size * 0.6)      # Bottom left
            ]
            pygame.draw.polygon(char_surface, self.colors['shirt'], body_points)

            # Legs with walking animation
            if self.moving:
                leg_offset = walk_offset * 1.5
                # Left leg
                left_leg = [
                    (self.size - self.size * 0.25, self.size + self.size * 0.5),
                    (self.size - self.size * 0.15, self.size + self.size * 0.5),
                    (self.size - self.size * 0.2 + leg_offset, self.size + self.size * 0.8),
                    (self.size - self.size * 0.3 + leg_offset, self.size + self.size * 0.8)
                ]
                # Right leg
                right_leg = [
                    (self.size + self.size * 0.15, self.size + self.size * 0.5),
                    (self.size + self.size * 0.25, self.size + self.size * 0.5),
                    (self.size + self.size * 0.3 - leg_offset, self.size + self.size * 0.8),
                    (self.size + self.size * 0.2 - leg_offset, self.size + self.size * 0.8)
                ]
                pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
                pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

                # Shoes
                pygame.draw.circle(char_surface, self.colors['shoes'],
                                 (self.size - self.size * 0.25 + leg_offset, self.size + self.size * 0.8), 3)
                pygame.draw.circle(char_surface, self.colors['shoes'],
                                 (self.size + self.size * 0.25 - leg_offset, self.size + self.size * 0.8), 3)
            else:
                # Standing still legs
                left_leg = [
                    (self.size - self.size * 0.25, self.size + self.size * 0.5),
                    (self.size - self.size * 0.15, self.size + self.size * 0.5),
                    (self.size - self.size * 0.2, self.size + self.size * 0.8),
                    (self.size - self.size * 0.3, self.size + self.size * 0.8)
                ]
                right_leg = [
                    (self.size + self.size * 0.15, self.size + self.size * 0.5),
                    (self.size + self.size * 0.25, self.size + self.size * 0.5),
                    (self.size + self.size * 0.3, self.size + self.size * 0.8),
                    (self.size + self.size * 0.2, self.size + self.size * 0.8)
                ]
                pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
                pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

                # Shoes
                pygame.draw.circle(char_surface, self.colors['shoes'],
                                 (self.size - self.size * 0.25, self.size + self.size * 0.8), 3)
                pygame.draw.circle(char_surface, self.colors['shoes'],
                                 (self.size + self.size * 0.25, self.size + self.size * 0.8), 3)

            # Apply character direction
            if self.direction == 'left':
                char_surface = pygame.transform.flip(char_surface, True, False)

        # Draw the character surface onto the screen
        screen.blit(char_surface, 
                   (screen_x - char_surface.get_width()/2,
                    screen_y - char_surface.get_height()/2))

    class Map:
        def __init__(self):
            self.width = 2400
            self.height = 1800
            self.tile_size = 32
            self.walls = []
            self.roads = []
            self.vehicles = []
            self.police_vehicles = []
            self.pedestrians = []
            self.window_states = {}  # Store window lighting states
            self.create_city_layout()
            self.spawn_vehicles(15)
            self.spawn_police(3)
            self.spawn_pedestrians(30)

            # Time of day system - 0.0 to 1.0 (0.0 = midnight, 0.5 = noon)
            self.time_of_day = 0.3  # Start in morning
            self.time_speed = 0.0001  # Speed of time passing
            self.sky_colors = {
                0.0: (10, 10, 40),     # Midnight
                0.25: (200, 120, 40),  # Sunrise
                0.5: (100, 150, 255),  # Noon
                0.75: (255, 100, 50),  # Sunset
                1.0: (10, 10, 40)      # Midnight again
            }

        def create_city_layout(self):
            road_width = 96
            block_size = 300

            # Create roads with lane markings
            for y in range(0, self.height, block_size):
                road = pygame.Rect(0, y, self.width, road_width)
                self.roads.append({"rect": road, "horizontal": True})

            for x in range(0, self.width, block_size):
                road = pygame.Rect(x, 0, road_width, self.height)
                self.roads.append({"rect": road, "horizontal": False})

            # Create buildings with varied appearances
            building_colors = [
                (120, 120, 120),  # Gray
                (180, 100, 100),  # Brick Red
                (100, 130, 150),  # Blue Gray
                (150, 150, 130),  # Beige
            ]

            for block_x in range(road_width, self.width - road_width, block_size):
                for block_y in range(road_width, self.height - road_width, block_size):
                    for _ in range(random.randint(2, 3)):
                        building_width = random.randint(80, 160)
                        building_height = random.randint(80, 160)
                        x = block_x + random.randint(0, block_size - building_width - road_width)
                        y = block_y + random.randint(0, block_size - building_height - road_width)

                        # Create building with color and window information
                        building_id = f"building_{x}_{y}"
                        self.walls.append({
                            "rect": pygame.Rect(x, y, building_width, building_height),
                            "color": random.choice(building_colors),
                            "windows": {
                                "rows": random.randint(2, 4),
                                "cols": random.randint(3, 5)
                            },
                            "id": building_id
                        })

                        # Initialize window states for this building
                        if building_id not in self.window_states:
                            self.window_states[building_id] = []
                            for _ in range(16):  # Maximum possible windows
                                self.window_states[building_id].append(random.random() < 0.3)

        def draw(self, screen, camera_x, camera_y):
            # Calculate sky color based on time of day
            sky_color = self.get_sky_color()

            # Fill the background with sky color
            screen.fill(sky_color)

            # Draw grass
            grass_color = (
                max(20, int(34 * self.get_light_level())),
                max(40, int(139 * self.get_light_level())),
                max(20, int(34 * self.get_light_level()))
            )
            pygame.draw.rect(screen, grass_color, (0, 0, screen.get_width(), screen.get_height()))

            # Draw roads with lane markings
            for road in self.roads:
                road_view = pygame.Rect(
                    road["rect"].x - camera_x,
                    road["rect"].y - camera_y,
                    road["rect"].width,
                    road["rect"].height
                )
                if road_view.colliderect(screen.get_rect()):
                    # Draw road base
                    pygame.draw.rect(screen, (50, 50, 50), road_view)

                    # Draw lane markings
                    line_color = (255, 255, 255)
                    if road["horizontal"]:
                        line_y = road_view.centery
                        x = road["rect"].x - camera_x
                        while x < road["rect"].x + road["rect"].width - camera_x:
                            pygame.draw.line(screen, line_color,
                                           (x, line_y),
                                           (x + 20, line_y), 2)
                            x += 40
                    else:
                        line_x = road_view.centerx
                        y = road["rect"].y - camera_y
                        while y < road["rect"].y + road["rect"].height - camera_y:
                            pygame.draw.line(screen, line_color,
                                           (line_x, y),
                                           (line_x, y + 20), 2)
                            y += 40

                    # Draw sidewalks
                    sidewalk_color = (180, 180, 180)
                    sidewalk_width = 10

                    # Outer sidewalk borders
                    if road["horizontal"]:
                        # Top sidewalk
                        pygame.draw.rect(screen, sidewalk_color, 
                                        (road_view.x, road_view.y, road_view.width, sidewalk_width))
                        # Bottom sidewalk
                        pygame.draw.rect(screen, sidewalk_color, 
                                        (road_view.x, road_view.y + road_view.height - sidewalk_width, 
                                         road_view.width, sidewalk_width))
                    else:
                        # Left sidewalk
                        pygame.draw.rect(screen, sidewalk_color, 
                                        (road_view.x, road_view.y, sidewalk_width, road_view.height))
                        # Right sidewalk
                        pygame.draw.rect(screen, sidewalk_color, 
                                        (road_view.x + road_view.width - sidewalk_width, road_view.y, 
                                         sidewalk_width, road_view.height))

            # Draw buildings with windows
            for wall in self.walls:
                wall_view = pygame.Rect(
                    wall["rect"].x - camera_x,
                    wall["rect"].y - camera_y,
                    wall["rect"].width,
                    wall["rect"].height
                )
                if wall_view.colliderect(screen.get_rect()):
                    # Draw building base
                    pygame.draw.rect(screen, wall["color"], wall_view)

                    # Draw windows using persistent states
                    window_width = wall["rect"].width // (wall["windows"]["cols"] * 2)
                    window_height = wall["rect"].height // (wall["windows"]["rows"] * 2)
                    window_index = 0
                    for row in range(wall["windows"]["rows"]):
                        for col in range(wall["windows"]["cols"]):
                            if window_index < len(self.window_states[wall["id"]]):
                                window_x = wall_view.x + (col * 2 + 1) * window_width
                                window_y = wall_view.y + (row * 2 + 1) * window_height
                                # Use persistent window state, but make windows brighter at night
                                light_level = self.get_light_level()
                                if self.window_states[wall["id"]][window_index]:
                                    # Window is lit - brighter at night
                                    brightness = min(255, int(255 * (1.0 - light_level * 0.7)))
                                    window_color = (brightness, brightness, brightness * 0.8)
                                else:
                                    # Window is dark - darker at night
                                    darkness = int(30 * light_level)
                                    window_color = (darkness, darkness, darkness)

                                pygame.draw.rect(screen, window_color,
                                               (window_x, window_y, window_width * 0.8, window_height * 0.8))
                                window_index += 1

            # Draw pedestrians in proper order
            for pedestrian in self.pedestrians:
                pedestrian.draw(screen, camera_x, camera_y)

            # Draw regular vehicles
            for vehicle in self.vehicles:
                vehicle.draw(screen, camera_x, camera_y)

            # Draw police vehicles
            for vehicle in self.police_vehicles:
                vehicle.draw(screen, camera_x, camera_y)

        def draw_minimap(self, screen, player_x, player_y):
            # Draw minimap in top-right corner
            minimap_size = 150
            margin = 10
            scale = minimap_size / max(self.width, self.height)

            # Draw minimap background
            minimap_rect = pygame.Rect(screen.get_width() - minimap_size - margin, 
                                     margin, minimap_size, minimap_size)
            pygame.draw.rect(screen, (0, 0, 0), minimap_rect)

            # Draw roads on minimap
            for road in self.roads:
                mini_road = pygame.Rect(
                    screen.get_width() - minimap_size - margin + road["rect"].x * scale,
                    margin + road["rect"].y * scale,
                    road["rect"].width * scale,
                    road["rect"].height * scale
                )
                pygame.draw.rect(screen, (100, 100, 100), mini_road)

            # Draw player on minimap
            player_pos = (
                screen.get_width() - minimap_size - margin + player_x * scale,
                margin + player_y * scale
            )
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(player_pos[0]), int(player_pos[1])), 3)

            # Draw police vehicles as blue dots
            for police in self.police_vehicles:
                police_pos = (
                    screen.get_width() - minimap_size - margin + police.x * scale,
                    margin + police.y * scale
                )
                pygame.draw.circle(screen, (0, 0, 255), 
                                (int(police_pos[0]), int(police_pos[1])), 2)

        def spawn_vehicles(self, count):
            for _ in range(count):
                # Find a random road
                if not self.roads:  # Safety check
                    return

                road = random.choice(self.roads)

                # Determine if road is horizontal or vertical
                is_horizontal = road["rect"].width > road["rect"].height

                if is_horizontal:
                    # Place vehicle along horizontal road
                    x = road["rect"].x + random.randint(0, road["rect"].width - 32)  # Account for vehicle width
                    y = road["rect"].y + road["rect"].height // 2  # Center in road
                    rotation = 0 if random.random() > 0.5 else 180  # Face left or right
                else:
                    # Place vehicle along vertical road
                    x = road["rect"].x + road["rect"].width // 2  # Center in road
                    y = road["rect"].y + random.randint(0, road["rect"].height - 32)  # Account for vehicle length
                    rotation = 90 if random.random() > 0.5 else 270  # Face up or down

                vehicle = Vehicle(x, y)
                vehicle.rotation = rotation  # Set initial rotation based on road direction
                self.vehicles.append(vehicle)

        def spawn_police(self, count):
            for _ in range(count):
                # Find a random road
                if not self.roads:  # Safety check
                    return

                road = random.choice(self.roads)

                # Determine if road is horizontal or vertical
                is_horizontal = road["rect"].width > road["rect"].height

                if is_horizontal:
                    # Place police along horizontal road
                    x = road["rect"].x + random.randint(0, road["rect"].width - 32)
                    y = road["rect"].y + road["rect"].height // 2
                    rotation = 0 if random.random() > 0.5 else 180
                else:
                    # Place police along vertical road
                    x = road["rect"].x + road["rect"].width // 2
                    y = road["rect"].y + random.randint(0, road["rect"].height - 32)
                    rotation = 90 if random.random() > 0.5 else 270

                police = PoliceVehicle(x, y)
                police.rotation = rotation
                self.police_vehicles.append(police)

        def spawn_pedestrians(self, count):
            for _ in range(count):
                # Find a random position near a road (sidewalk)
                if not self.roads:
                    return

                road = random.choice(self.roads)
                road_rect = road["rect"]

                # Determine sidewalk position
                sidewalk_width = 10
                if road["horizontal"]:
                    # Horizontal road - spawn on top or bottom sidewalk
                    x = road_rect.x + random.randint(0, road_rect.width)
                    if random.random() < 0.5:
                        # Top sidewalk
                        y = road_rect.y + sidewalk_width // 2
                    else:
                        # Bottom sidewalk
                        y = road_rect.y + road_rect.height - sidewalk_width // 2
                else:
                    # Vertical road - spawn on left or right sidewalk
                    y = road_rect.y + random.randint(0, road_rect.height)
                    if random.random() < 0.5:
                        # Left sidewalk
                        x = road_rect.x + sidewalk_width // 2
                    else:
                        # Right sidewalk
                        x = road_rect.x + road_rect.width - sidewalk_width // 2

                pedestrian = Pedestrian(x, y)
                self.pedestrians.append(pedestrian)

        def update(self, player):
            # Update time of day
            self.time_of_day = (self.time_of_day + self.time_speed) % 1.0

            # Update window states occasionally
            if random.random() < 0.001:
                for building_id in self.window_states:
                    for i in range(len(self.window_states[building_id])):
                        # Windows are more likely to be on at night
                        light_level = self.get_light_level()
                        if random.random() < 0.05:  # 5% chance to change state
                            night_factor = 1.0 - light_level  # More windows on at night
                            self.window_states[building_id][i] = random.random() < (0.3 + night_factor * 0.4)

            # Update police AI
            for police in self.police_vehicles:
                police.update_ai(player, self.walls, self.roads)

            # Update pedestrians and remove dead ones that have timed out
            for pedestrian in self.pedestrians[:]:
                should_remove = pedestrian.update_ai(
                    player, self.walls, self.roads, 
                    self.vehicles + self.police_vehicles + ([player.in_vehicle] if player.in_vehicle else []), 
                    player.bullets, self.pedestrians
                )
                if should_remove:
                    self.pedestrians.remove(pedestrian)

            # Respawn pedestrians if needed
            if len(self.pedestrians) < 30:
                self.spawn_pedestrians(1)

        def get_light_level(self):
            # Returns light level between 0.0 (dark) and 1.0 (bright)
            if self.time_of_day < 0.25:  # Midnight to sunrise
                return 0.2 + (self.time_of_day / 0.25) * 0.8
            elif self.time_of_day < 0.75:  # Sunrise to sunset
                return 1.0
            else:  # Sunset to midnight
                return 0.2 + (1.0 - (self.time_of_day - 0.75) / 0.25) * 0.8

        def get_sky_color(self):
            # Find the two closest time points
            times = sorted(self.sky_colors.keys())
            for i in range(len(times)):
                if self.time_of_day <= times[i]:
                    if i == 0:
                        t1, t2 = times[-1], times[0]
                        factor = self.time_of_day / times[0]
                    else:
                        t1, t2 = times[i-1], times[i]
                        factor = (self.time_of_day - t1) / (t2 - t1)
                    break
            else:
                t1, t2 = times[-1], times[0]
                factor = (self.time_of_day - t1) / (1.0 - t1)

            # Interpolate between colors
            c1 = self.sky_colors[t1]
            c2 = self.sky_colors[t2]
            return tuple(int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3))

class Game:
    def __init__(self):
        # Set SDL variables for Replit environment
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'  # Force software rendering

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("GTA Style Game")

        # Create game objects
        self.map = Map()
        # Start player in center of map
        self.player = Player(self.map.width/2, self.map.height/2)

        # Initialize camera to center on player
        self.camera_x = self.player.x - self.width/2
        self.camera_y = self.player.y - self.height/2

        # Game state
        self.running = True
        self.clock = pygame.time.Clock()

    def update_camera(self):
        # Calculate target camera position (centered on player)
        target_camera_x = self.player.x - self.width/2
        target_camera_y = self.player.y - self.height/2

        # Smooth camera movement
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1

        # Keep camera within map bounds
        self.camera_x = max(0, min(self.camera_x, self.map.width - self.width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - self.height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.enter_exit_vehicle(self.map.vehicles + self.map.police_vehicles)
                elif event.key == pygame.K_SPACE:
                    self.player.shoot()

    def run(self):
        while self.running:
            # Handle events
            self.handle_events()

            # Get keyboard state
            keys = pygame.key.get_pressed()

            # Handle player movement
            if not self.player.in_vehicle:
                dx = 0
                dy = 0
                if keys[pygame.K_w]: dy -= 1
                if keys[pygame.K_s]: dy += 1
                if keys[pygame.K_a]: dx -= 1
                if keys[pygame.K_d]: dx += 1
                self.player.move(dx, dy, self.map.walls)
            else:
                # Vehicle controls
                forward = 0
                turn = 0
                if keys[pygame.K_w]: forward = 1
                if keys[pygame.K_s]: forward = -1
                if keys[pygame.K_a]: turn = -1
                if keys[pygame.K_d]: turn = 1
                self.player.in_vehicle.move(forward, turn, self.map.walls)
                # Update player position to vehicle position
                self.player.x = self.player.in_vehicle.x
                self.player.y = self.player.in_vehicle.y

            # Update game objects
            self.player.update()
            self.map.update(self.player)
            self.update_camera()

            # Draw everything
            self.map.draw(self.screen, self.camera_x, self.camera_y)

            # Draw vehicles
            for vehicle in self.map.vehicles + self.map.police_vehicles:
                vehicle.draw(self.screen, self.camera_x, self.camera_y)

            # Draw pedestrians
            for ped in self.map.pedestrians:
                ped.draw(self.screen, self.camera_x, self.camera_y)

            # Draw player and bullets
            if not self.player.in_vehicle:
                self.player.draw(self.screen, self.camera_x, self.camera_y)
            self.player.draw_bullets(self.screen, self.camera_x, self.camera_y)

            # Draw UI elements
            self.player.draw_wanted_level(self.screen)
            self.map.draw_minimap(self.screen, self.player.x, self.player.y)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

def main():
    # Set up software renderer before initializing pygame
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'

    pygame.init()
    game = Game()
    game.run()

if __name__ == "__main__":
    main()