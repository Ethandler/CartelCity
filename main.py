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
                    self.vehicle_entry_cooldown = 30
                    break

    def update(self):
        if self.vehicle_entry_cooldown > 0:
            self.vehicle_entry_cooldown -= 1

class Map:
    def __init__(self):
        self.width = 2400
        self.height = 1800
        self.tile_size = 32
        self.walls = []
        self.roads = []
        self.vehicles = []
        self.window_states = {}  # Store window lighting states
        self.create_city_layout()
        self.spawn_vehicles(15)

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
                            # Use persistent window state
                            window_color = (255, 255, 200) if self.window_states[wall["id"]][window_index] else (30, 30, 30)
                            pygame.draw.rect(screen, window_color,
                                           (window_x, window_y, window_width * 0.8, window_height * 0.8))
                            window_index += 1

        # Draw vehicles
        for vehicle in self.vehicles:
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

class Game:
    def __init__(self):
        # Set SDL variables for Replit environment
        os.environ['SDL_VIDEODRIVER'] = 'x11'

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
        self.dragging = False
        self.last_mouse_pos = None

    def update_camera(self):
        # Camera follows player with some margin
        margin = 200

        # Update camera x position
        if self.player.x - self.camera_x < margin:
            self.camera_x = self.player.x - margin
        elif self.player.x - self.camera_x > self.width - margin:
            self.camera_x = self.player.x - (self.width - margin)

        # Update camera y position
        if self.player.y - self.camera_y < margin:
            self.camera_y = self.player.y - margin
        elif self.player.y - self.camera_y > self.height - margin:
            self.camera_y = self.player.y - (self.height - margin)

        # Keep camera within map bounds
        self.camera_x = max(0, min(self.camera_x, self.map.width - self.width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - self.height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.enter_exit_vehicle(self.map.vehicles)

        # Handle player movement with WASD keys
        if not self.player.in_vehicle:
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            # Simplified movement controls for better responsiveness
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.7071  # 1/√2
                dy *= 0.7071

            self.player.move(dx, dy, self.map.walls)
            self.update_camera()
        else:
            # Vehicle controls
            keys = pygame.key.get_pressed()
            forward = 0
            turn = 0

            # Simplified vehicle controls
            if keys[pygame.K_w]: forward += 1
            if keys[pygame.K_s]: forward -= 1
            if keys[pygame.K_d]: turn += 1
            if keys[pygame.K_a]: turn -= 1

            self.player.in_vehicle.move(forward, turn, self.map.walls)
            # Update player position to match vehicle
            self.player.x = self.player.in_vehicle.x
            self.player.y = self.player.in_vehicle.y
            self.update_camera()

    def draw(self):
        # Clear the screen
        self.screen.fill((34, 139, 34))  # Green background (grass)

        # Draw the map (adjusting for camera position)
        self.map.draw(self.screen, self.camera_x, self.camera_y)

        # Draw the player with animations
        if not self.player.in_vehicle:
            self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Draw minimap
        self.map.draw_minimap(self.screen, self.player.x, self.player.y)

        # Update the display
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.player.update()
            self.handle_events()
            self.draw()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()