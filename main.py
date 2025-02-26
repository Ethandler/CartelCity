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
        self.color = random.choice([
            (200, 0, 0),    # Red
            (0, 0, 200),    # Blue
            (40, 40, 40),   # Dark Gray
            (200, 200, 200),# Silver
            (255, 255, 255),# White
            (0, 100, 0),    # Dark Green
        ])

    def move(self, forward, turn, walls):
        if forward != 0:
            target_speed = forward * self.max_speed
            self.speed = min(max(self.speed + (self.acceleration * forward), -self.max_speed), self.max_speed)
        else:
            if abs(self.speed) > self.acceleration:
                self.speed -= (self.acceleration * (1 if self.speed > 0 else -1))
            else:
                self.speed = 0

        if turn:
            turn_rate = 3 * (1 - (abs(self.speed) / self.max_speed) * 0.5)
            self.rotation += turn * turn_rate
            self.rotation %= 360

        angle = math.radians(self.rotation)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed

        new_x = self.x + dx
        new_y = self.y + dy

        new_rect = pygame.Rect(new_x - self.size[0]/2, new_y - self.size[1]/2, self.size[0], self.size[1])

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

        screen_rect = screen.get_rect()
        if (screen_x + self.size[0] < -50 or screen_x - self.size[0] > screen_rect.width + 50 or
            screen_y + self.size[1] < -50 or screen_y - self.size[1] > screen_rect.height + 50):
            return

        car_surface = pygame.Surface(self.size, pygame.SRCALPHA)

        pygame.draw.rect(car_surface, self.color, (0, 0, self.size[0], self.size[1]))

        window_color = (30, 30, 30, 200)
        window_width = self.size[0] // 4
        window_height = self.size[1] // 2

        pygame.draw.rect(car_surface, window_color, 
                        (self.size[0] - window_width - 4, 2, window_width, window_height))
        pygame.draw.rect(car_surface, window_color,
                        (4, 2, window_width, window_height))

        light_size = 3
        if self.rotation in [0, 180]:
            pygame.draw.rect(car_surface, (255, 255, 200),
                           (self.size[0] - light_size - 1, 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 255, 200),
                           (self.size[0] - light_size - 1, self.size[1] - light_size - 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 0, 0),
                           (1, 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 0, 0),
                           (1, self.size[1] - light_size - 2, light_size, light_size))

        rotated_surface = pygame.transform.rotate(car_surface, -self.rotation)

        screen.blit(rotated_surface, (screen_x - rotated_surface.get_width()/2,
                                    screen_y - rotated_surface.get_height()/2))

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
            'skin': (255, 223, 196),
            'shirt': (200, 0, 0),
            'pants': (0, 0, 150),
            'shoes': (40, 40, 40),
            'eyes': (0, 0, 0)
        }
        self.in_vehicle = None
        self.vehicle_entry_cooldown = 0

    def move(self, dx, dy, walls):
        if dx != 0 or dy != 0:
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            self.moving = True
        else:
            self.moving = False

        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if self.moving:
            self.animation_frame = (self.animation_frame + self.animation_speed) % 4
        else:
            self.animation_frame = 0

        new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)

        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall["rect"]):
                can_move = False
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect = new_rect

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        char_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        walk_offset = math.sin(self.animation_frame * math.pi) * 2 if self.moving else 0
        head_bob = math.sin(self.animation_frame * math.pi * 2) * 1.5

        head_top = self.size - head_bob
        head_bottom = self.size + head_bob
        head_width = self.size * 0.8

        pygame.draw.ellipse(
            char_surface,
            self.colors['skin'],
            (self.size - head_width/2, head_top - head_width/2, head_width, head_width)
        )

        pygame.draw.ellipse(
            char_surface,
            self.colors['skin'],
            (self.size - head_width/2, head_bottom - head_width/2, head_width * 0.8, head_width * 0.4)
        )

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

        body_points = [
            (self.size - self.size * 0.3, self.size + head_width * 0.3),
            (self.size + self.size * 0.3, self.size + head_width * 0.3),
            (self.size + self.size * 0.4, self.size + self.size * 0.6),
            (self.size - self.size * 0.4, self.size + self.size * 0.6)
        ]
        pygame.draw.polygon(char_surface, self.colors['shirt'], body_points)

        if self.moving:
            leg_offset = walk_offset * 1.5
            left_leg = [
                (self.size - self.size * 0.25, self.size + self.size * 0.5),
                (self.size - self.size * 0.15, self.size + self.size * 0.5),
                (self.size - self.size * 0.2 + leg_offset, self.size + self.size * 0.8),
                (self.size - self.size * 0.3 + leg_offset, self.size + self.size * 0.8)
            ]
            right_leg = [
                (self.size + self.size * 0.15, self.size + self.size * 0.5),
                (self.size + self.size * 0.25, self.size + self.size * 0.5),
                (self.size + self.size * 0.3 - leg_offset, self.size + self.size * 0.8),
                (self.size + self.size * 0.2 - leg_offset, self.size + self.size * 0.8)
            ]
            pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
            pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size - self.size * 0.25 + leg_offset, self.size + self.size * 0.8), 3)
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size + self.size * 0.25 - leg_offset, self.size + self.size * 0.8), 3)
        else:
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

            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size - self.size * 0.25, self.size + self.size * 0.8), 3)
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size + self.size * 0.25, self.size + self.size * 0.8), 3)

        if self.direction == 'left':
            char_surface = pygame.transform.flip(char_surface, True, False)

        screen.blit(char_surface, 
                   (screen_x - char_surface.get_width()/2,
                    screen_y - char_surface.get_height()/2))

    def enter_exit_vehicle(self, vehicles):
        if self.vehicle_entry_cooldown > 0:
            return

        if self.in_vehicle:
            self.x = self.in_vehicle.x + math.cos(math.radians(self.in_vehicle.rotation)) * 40
            self.y = self.in_vehicle.y + math.sin(math.radians(self.in_vehicle.rotation)) * 40
            self.rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
            self.in_vehicle = None
            self.vehicle_entry_cooldown = 30
        else:
            for vehicle in vehicles:
                dist = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
                if dist < 50:
                    self.in_vehicle = vehicle
                    self.vehicle_entry_cooldown = 30
                    break

    def update(self):
        if self.vehicle_entry_cooldown > 0:
            self.vehicle_entry_cooldown -= 1

class Map:
    def __init__(self):
        self.width = 3200  
        self.height = 2400  
        self.tile_size = 32
        self.walls = []
        self.roads = []
        self.vehicles = []
        self.window_states = {}
        self.districts = []  
        self.create_detroit_layout()
        self.spawn_vehicles(20)  

    def create_detroit_layout(self):
        major_roads = [
            {"start": (0, 600), "end": (self.width, 600), "width": 128},  
            {"start": (0, 1200), "end": (self.width, 1200), "width": 128},  
            {"start": (0, 1800), "end": (self.width, 1800), "width": 128},  

            {"start": (800, 0), "end": (800, self.height), "width": 128},  
            {"start": (1600, 0), "end": (1600, self.height), "width": 128},  
            {"start": (2400, 0), "end": (2400, self.height), "width": 128},  
        ]

        for road in major_roads:
            road_rect = pygame.Rect(
                road["start"][0],
                road["start"][1],
                road["end"][0] - road["start"][0] if road["start"][1] == road["end"][1] else road["width"],
                road["end"][1] - road["start"][1] if road["start"][0] == road["end"][0] else road["width"]
            )
            self.roads.append({
                "rect": road_rect,
                "horizontal": road["start"][1] == road["end"][1],
                "major": True
            })

        block_size = 200  

        for y in range(0, self.height, block_size):
            if not any(abs(y - road["rect"].y) < 150 for road in self.roads if road.get("major")):
                road = pygame.Rect(0, y, self.width, 64)  
                self.roads.append({"rect": road, "horizontal": True, "major": False})

        for x in range(0, self.width, block_size):
            if not any(abs(x - road["rect"].x) < 150 for road in self.roads if road.get("major")):
                road = pygame.Rect(x, 0, 64, self.height)  
                self.roads.append({"rect": road, "horizontal": False, "major": False})

        district_colors = [
            (120, 120, 120),  
            (180, 100, 100),  
            (100, 130, 150),  
            (150, 150, 130),  
            (140, 110, 120),  
            (130, 140, 110),  
            (110, 120, 140),  
        ]

        for block_x in range(100, self.width - 100, block_size):
            for block_y in range(100, self.height - 100, block_size):
                if any(road["rect"].collidepoint(block_x, block_y) for road in self.roads):
                    continue

                district_index = (block_x // (self.width // 3) + block_y // (self.height // 3)) % len(district_colors)

                for _ in range(random.randint(1, 3)):
                    building_width = random.randint(60, 120)
                    building_height = random.randint(60, 120)
                    x = block_x + random.randint(0, block_size - building_width)
                    y = block_y + random.randint(0, block_size - building_height)

                    building_id = f"building_{x}_{y}"
                    self.walls.append({
                        "rect": pygame.Rect(x, y, building_width, building_height),
                        "color": district_colors[district_index],
                        "windows": {
                            "rows": random.randint(2, 4),
                            "cols": random.randint(3, 5)
                        },
                        "id": building_id
                    })

                    if building_id not in self.window_states:
                        self.window_states[building_id] = [
                            random.random() < 0.3 for _ in range(16)
                        ]

    def draw(self, screen, camera_x, camera_y):
        for road in self.roads:
            road_view = pygame.Rect(
                road["rect"].x - camera_x,
                road["rect"].y - camera_y,
                road["rect"].width,
                road["rect"].height
            )
            if road_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, (50, 50, 50), road_view)

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

        for wall in self.walls:
            wall_view = pygame.Rect(
                wall["rect"].x - camera_x,
                wall["rect"].y - camera_y,
                wall["rect"].width,
                wall["rect"].height
            )
            if wall_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, wall["color"], wall_view)

                window_width = wall["rect"].width // (wall["windows"]["cols"] * 2)
                window_height = wall["rect"].height // (wall["windows"]["rows"] * 2)
                window_index = 0
                for row in range(wall["windows"]["rows"]):
                    for col in range(wall["windows"]["cols"]):
                        if window_index < len(self.window_states[wall["id"]]):
                            window_x = wall_view.x + (col * 2 + 1) * window_width
                            window_y = wall_view.y + (row * 2 + 1) * window_height
                            window_color = (255, 255, 200) if self.window_states[wall["id"]][window_index] else (30, 30, 30)
                            pygame.draw.rect(screen, window_color,
                                           (window_x, window_y, window_width * 0.8, window_height * 0.8))
                            window_index += 1

        for vehicle in self.vehicles:
            vehicle.draw(screen, camera_x, camera_y)

    def draw_minimap(self, screen, player_x, player_y):
        minimap_size = 150
        margin = 10
        scale = minimap_size / max(self.width, self.height)

        minimap_rect = pygame.Rect(screen.get_width() - minimap_size - margin, 
                                 margin, minimap_size, minimap_size)
        pygame.draw.rect(screen, (0, 0, 0), minimap_rect)

        for road in self.roads:
            mini_road = pygame.Rect(
                screen.get_width() - minimap_size - margin + road["rect"].x * scale,
                margin + road["rect"].y * scale,
                road["rect"].width * scale,
                road["rect"].height * scale
            )
            pygame.draw.rect(screen, (100, 100, 100), mini_road)

        player_pos = (
            screen.get_width() - minimap_size - margin + player_x * scale,
            margin + player_y * scale
        )
        pygame.draw.circle(screen, (255, 0, 0), 
                         (int(player_pos[0]), int(player_pos[1])), 3)

    def spawn_vehicles(self, count):
        for _ in range(count):
            if not self.roads:
                return

            road = random.choice(self.roads)

            is_horizontal = road["rect"].width > road["rect"].height

            if is_horizontal:
                x = road["rect"].x + random.randint(0, road["rect"].width - 32)  
                y = road["rect"].y + road["rect"].height // 2  
                rotation = 0 if random.random() > 0.5 else 180  
            else:
                x = road["rect"].x + road["rect"].width // 2  
                y = road["rect"].y + random.randint(0, road["rect"].height - 32)  
                rotation = 90 if random.random() > 0.5 else 270  

            vehicle = Vehicle(x, y)
            vehicle.rotation = rotation  
            self.vehicles.append(vehicle)

class TouchButton:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.pressed = False

    def draw(self, screen):
        # Draw button with lighter color when pressed
        button_color = tuple(min(c + 50, 255) if self.pressed else c for c in self.color)
        pygame.draw.rect(screen, button_color, self.rect, border_radius=self.rect.height // 4)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, width=2, border_radius=self.rect.height // 4)

        # Render text if available
        if self.text:
            font = pygame.font.Font(None, 28)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def check_press(self, pos):
        if self.rect.collidepoint(pos):
            self.pressed = True
            return True
        return False

    def check_release(self, pos):
        was_pressed = self.pressed
        self.pressed = False
        if was_pressed and self.rect.collidepoint(pos):
            return True
        return False

class VirtualJoystick:
    def __init__(self, x, y, radius):
        self.base_pos = (x, y)
        self.radius = radius
        self.stick_pos = (x, y)
        self.active = False
        self.dead_zone = 0.2

    def draw(self, screen):
        # Draw base
        pygame.draw.circle(screen, (80, 80, 80), self.base_pos, self.radius)
        pygame.draw.circle(screen, (200, 200, 200), self.base_pos, self.radius, 2)

        # Draw stick
        pygame.draw.circle(screen, (150, 150, 150), self.stick_pos, self.radius // 2)
        pygame.draw.circle(screen, (200, 200, 200), self.stick_pos, self.radius // 2, 2)

    def get_input(self):
        if not self.active:
            return (0, 0)

        dx = (self.stick_pos[0] - self.base_pos[0]) / self.radius
        dy = (self.stick_pos[1] - self.base_pos[1]) / self.radius

        # Apply dead zone
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < self.dead_zone:
            return (0, 0)

        # Normalize if beyond unit circle
        if distance > 1:
            dx /= distance
            dy /= distance

        return (dx, dy)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if press is within joystick area
            distance = math.sqrt((event.pos[0] - self.base_pos[0])**2 + (event.pos[1] - self.base_pos[1])**2)
            if distance <= self.radius * 1.5:  # Slightly larger detection area
                self.active = True

        elif event.type == pygame.MOUSEMOTION and self.active:
            # Calculate distance from center
            dx = event.pos[0] - self.base_pos[0]
            dy = event.pos[1] - self.base_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)

            # Limit stick position to the joystick radius
            if distance > self.radius:
                dx = dx * self.radius / distance
                dy = dy * self.radius / distance

            self.stick_pos = (self.base_pos[0] + dx, self.base_pos[1] + dy)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                self.stick_pos = self.base_pos

class Game:
    def __init__(self):
        os.environ['SDL_VIDEODRIVER'] = 'x11'

        pygame.init()
        # Try to detect if we're on mobile
        self.is_mobile = False
        try:
            # Get information about display
            display_info = pygame.display.Info()
            # Check screen dimensions and aspect ratio
            if display_info.current_w <= 1280 or display_info.current_h <= 720:
                self.is_mobile = True
        except:
            # If there's an error, default to non-mobile
            pass

        # Set display mode
        if self.is_mobile:
            self.width = 800 
            self.height = 600
            self.screen = pygame.display.set_mode((self.width, self.height))
        else:
            self.width = 800
            self.height = 600
            self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption("GTA Style Game")

        self.map = Map()
        self.player = Player(self.map.width/2, self.map.height/2)

        self.camera_x = self.player.x - self.width/2
        self.camera_y = self.player.y - self.height/2

        self.running = True
        self.dragging = False
        self.last_mouse_pos = None

        # Create virtual controls for mobile
        button_size = 60
        margin = 20
        joystick_radius = 70

        # Create virtual joystick for movement
        self.joystick = VirtualJoystick(margin + joystick_radius, 
                                        self.height - margin - joystick_radius, 
                                        joystick_radius)

        # Create action button (E key equivalent)
        self.action_button = TouchButton(
            self.width - margin - button_size, 
            self.height - margin - button_size,
            button_size, button_size, "E"
        )

        # Create mobile controls flag
        self.show_mobile_controls = True

    def update_camera(self):
        margin = 200

        if self.player.x - self.camera_x < margin:
            self.camera_x = self.player.x - margin
        elif self.player.x - self.camera_x > self.width - margin:
            self.camera_x = self.player.x - (self.width - margin)

        if self.player.y - self.camera_y < margin:
            self.camera_y = self.player.y - margin
        elif self.player.y - self.camera_y > self.height - margin:
            self.camera_y = self.player.y - (self.height - margin)

        self.camera_x = max(0, min(self.camera_x, self.map.width - self.width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - self.height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.enter_exit_vehicle(self.map.vehicles)
                elif event.key == pygame.K_m:  # Toggle mobile controls with M key
                    self.show_mobile_controls = not self.show_mobile_controls

            # Handle touch/mobile controls if enabled
            if self.show_mobile_controls:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.action_button.check_press(event.pos):
                        self.player.enter_exit_vehicle(self.map.vehicles)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.action_button.check_release(event.pos)

                # Handle joystick events
                self.joystick.handle_event(event)

        if not self.player.in_vehicle:
            # Keyboard controls
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1

            # Add joystick input if active
            if self.show_mobile_controls:
                joy_x, joy_y = self.joystick.get_input()
                dx += joy_x
                dy += joy_y

            if dx != 0 and dy != 0:
                dx *= 0.7071  
                dy *= 0.7071

            self.player.move(dx, dy, self.map.walls)
            self.update_camera()
        else:
            # Vehicle keyboard controls
            keys = pygame.key.get_pressed()
            forward = 0
            turn = 0

            if keys[pygame.K_w]: forward += 1
            if keys[pygame.K_s]: forward -= 1
            if keys[pygame.K_d]: turn += 1
            if keys[pygame.K_a]: turn -= 1

            # Add joystick input for vehicle if active
            if self.show_mobile_controls:
                joy_x, joy_y = self.joystick.get_input()
                forward -= joy_y  # Invert Y for forward/backward
                turn += joy_x

            self.player.in_vehicle.move(forward, turn, self.map.walls)
            self.player.x = self.player.in_vehicle.x
            self.player.y = self.player.in_vehicle.y
            self.update_camera()

    def draw(self):
        self.screen.fill((34, 139, 34))  

        self.map.draw(self.screen, self.camera_x, self.camera_y)

        if not self.player.in_vehicle:
            self.player.draw(self.screen, self.camera_x, self.camera_y)

        self.map.draw_minimap(self.screen, self.player.x, self.player.y)

        # Draw mobile controls if enabled
        if self.show_mobile_controls:
            # Draw semi-transparent overlay for control area
            controls_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            controls_overlay.fill((0, 0, 0, 30))  # Very subtle darkening

            # Draw virtual joystick
            self.joystick.draw(controls_overlay)

            # Draw action button
            self.action_button.draw(controls_overlay)

            # Draw control instructions
            font = pygame.font.Font(None, 20)
            hint_text = font.render("Move: Joystick | Action: E Button | Toggle Controls: M", True, (255, 255, 255))
            controls_overlay.blit(hint_text, (self.width // 2 - hint_text.get_width() // 2, 10))

            # Blit the controls overlay
            self.screen.blit(controls_overlay, (0, 0))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.player.update()
            self.handle_events()
            self.draw()
            clock.tick(60)  

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()