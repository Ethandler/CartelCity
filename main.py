import pygame
import math
import sys
import random
import os
import procedural_map  # Import our procedural map generator

class Map:
    def __init__(self):
        # Set default size first
        self.width = 2400  # Fixed size for consistent gameplay
        self.height = 1800

        # Initialize lists for game objects
        self.walls = []        # Collision walls (buildings, obstacles)
        self.roads = []        # Road areas for AI navigation
        self.buildings = []    # Visual buildings with metadata
        self.curbs = []        # Visual curbs along roads

        try:
            # First try to use our procedural map generator
            print("Generating procedural GTA-style map...")
            self.map_image, building_rects = procedural_map.generate_city_map(self.width, self.height)

            # Add the buildings to our walls for collision detection
            for rect in building_rects:
                self.walls.append({"rect": rect})

            # Generate roads for AI navigation based on grid pattern
            self.generate_roads_from_grid_pattern()

            print(f"Procedural map generated with {len(building_rects)} building collision areas and {len(self.roads)} road segments")

        except Exception as proc_error:
            print(f"Error generating procedural map: {proc_error}")
            print("Falling back to image loading...")

            # Try to load an existing map image as fallback
            try:
                # Load and scale the map image - try multiple possible paths
                image_paths = [
                    'attached_assets/IMG_7818.jpeg',  
                    '/home/runner/workspace/attached_assets/IMG_7818.jpeg',
                    './attached_assets/IMG_7818.jpeg',
                    '/tmp/attached_assets/IMG_7818.jpeg',
                    'IMG_7818.jpeg'
                ]

                loaded = False
                for path in image_paths:
                    try:
                        print(f"Trying to load image from: {path}")
                        self.map_image = pygame.image.load(path).convert()
                        self.map_image = pygame.transform.scale(self.map_image, (self.width, self.height))
                        print(f"Successfully loaded map image from {path}")
                        loaded = True
                        break
                    except Exception as path_error:
                        print(f"Could not load from {path}: {path_error}")

                if not loaded:
                    raise Exception("Could not load image from any path")

            except Exception as e:
                print(f"Error loading map image: {e}")
                print("Creating fallback surface...")
                # Create fallback surface if both procedural generation and image loading fail
                self.map_image = pygame.Surface((self.width, self.height))
                self.map_image.fill((60, 60, 60))  # Dark gray for streets
                # Draw some road grid pattern for visibility
                road_color = (50, 50, 50)
                for x in range(0, self.width, 200):
                    pygame.draw.line(self.map_image, road_color, (x, 0), (x, self.height), 20)
                for y in range(0, self.height, 200):
                    pygame.draw.line(self.map_image, road_color, (0, y), (self.width, y), 20)
                print("Fallback surface created.")

        self.tile_size = 32
        # Only initialize these lists if they don't already exist
        # (the procedural generator already fills the walls list)
        if not hasattr(self, 'vehicles'):
            self.vehicles = []
        if not hasattr(self, 'police_vehicles'):
            self.police_vehicles = []
        if not hasattr(self, 'pedestrians'):
            self.pedestrians = []

        # Create game objects if needed
        # Only use create_city_layout if we don't already have walls from procedural generator
        if not self.walls:
            print("No collision walls found - creating layout from analysis")
            self.create_city_layout()
        else:
            print(f"Using existing {len(self.walls)} collision walls from procedural generator")

        # Spawn game entities
        self.spawn_vehicles(15)
        self.spawn_police(3)
        self.spawn_pedestrians(30)

        # Time of day system
        self.time_of_day = 0.3  # Starting at mid-morning
        self.time_speed = 0.00005  # Slower time progression for more realistic day/night cycles
        self.sky_colors = {
            0.0: (10, 10, 40),     # Midnight
            0.25: (200, 120, 40),  # Sunrise
            0.5: (100, 150, 255),  # Noon
            0.75: (255, 100, 50),  # Sunset
            1.0: (10, 10, 40)      # Midnight again
        }

    def create_city_layout(self):
        try:
            # Create roads based on image analysis
            surface_array = pygame.surfarray.array3d(self.map_image)
            road_threshold = 100  # Adjust based on your image

            # Initialize buildings list if it doesn't exist
            if not hasattr(self, 'buildings'):
                self.buildings = []

            # Sample points in the image to detect roads
            step = 32  # Sample every 32 pixels
            for x in range(0, self.width, step):
                for y in range(0, self.height, step):
                    # Get average brightness of area
                    area = surface_array[x:min(x+step, self.width), 
                                      y:min(y+step, self.height)]
                    brightness = area.mean()

                    if brightness < road_threshold:
                        # Dark area - likely a road
                        is_horizontal = True if area.shape[1] > area.shape[0] else False
                        road = pygame.Rect(x, y, step, step)
                        self.roads.append({"rect": road, "horizontal": is_horizontal})

                        # Add walls along road edges (curbs) - these should be visible but not block movement
                        wall_width = 8

                        # Instead of adding curbs as walls (which block movement),
                        # we'll create a separate list for visual curbs if it doesn't exist
                        if not hasattr(self, 'curbs'):
                            self.curbs = []

                        if is_horizontal:
                            # Add curbs above and below road (visual only)
                            self.curbs.append({"rect": pygame.Rect(x, y - wall_width, step, wall_width)})
                            self.curbs.append({"rect": pygame.Rect(x, y + step, step, wall_width)})
                        else:
                            # Add curbs to left and right of road (visual only)
                            self.curbs.append({"rect": pygame.Rect(x - wall_width, y, wall_width, step)})
                            self.curbs.append({"rect": pygame.Rect(x + step, y, wall_width, step)})
                    else:
                        # Light area - likely a building or empty space
                        # Add some buildings in non-road areas with probability
                        if random.random() < 0.2:  # 20% chance for a building
                            building_size = random.randint(step//2, step)
                            building_rect = pygame.Rect(
                                x + random.randint(0, step-building_size), 
                                y + random.randint(0, step-building_size),
                                building_size, building_size
                            )
                            # Add building as a wall for collision
                            self.walls.append({"rect": building_rect})

                            # Also keep it in buildings list for drawing
                            self.buildings.append({
                                "rect": building_rect, 
                                "height": random.randint(1, 3),
                                "color": random.choice([(200, 200, 200), (180, 180, 180), (160, 160, 160)])
                            })
        except Exception as e:
            print(f"Error creating city layout: {e}")
            import traceback
            traceback.print_exc()
            # Create fallback layout
            self.create_fallback_layout()

    def create_fallback_layout(self):
        # Create a basic grid layout if image analysis fails
        road_width = 96
        block_size = 300

        # Initialize buildings list if needed
        if not hasattr(self, 'buildings'):
            self.buildings = []

        # Initialize curbs list if needed
        if not hasattr(self, 'curbs'):
            self.curbs = []

        # Define wall width
        wall_width = 8

        # Create horizontal and vertical roads
        for y in range(0, self.height, block_size):
            # Add road itself (not a wall)
            self.roads.append({"rect": pygame.Rect(0, y, self.width, road_width), "horizontal": True})

            # Add visual curbs above and below roads (but don't make them blocking walls)
            if y > 0:  # Don't add curb at top of map
                self.curbs.append({"rect": pygame.Rect(0, y - wall_width, self.width, wall_width)})
            self.curbs.append({"rect": pygame.Rect(0, y + road_width, self.width, wall_width)})

        for x in range(0, self.width, block_size):
            # Add road itself (not a wall)
            self.roads.append({"rect": pygame.Rect(x, 0, road_width, self.height), "horizontal": False})

            # Add visual curbs to left and right of roads (but don't make them blocking walls)
            if x > 0:  # Don't add curb at left edge of map
                self.curbs.append({"rect": pygame.Rect(x - wall_width, 0, wall_width, self.height)})
            self.curbs.append({"rect": pygame.Rect(x + road_width, 0, wall_width, self.height)})

        # Add buildings in non-road areas
        for x in range(road_width + 20, self.width, block_size):
            for y in range(road_width + 20, self.height, block_size):
                # Skip if too close to a road
                too_close = False
                for road in self.roads:
                    road_rect = road["rect"]
                    if (abs(x - road_rect.centerx) < road_width * 1.5 or
                        abs(y - road_rect.centery) < road_width * 1.5):
                        too_close = True
                        break

                if not too_close and random.random() < 0.7:  # 70% chance of building
                    building_size = random.randint(50, 150)
                    building_rect = pygame.Rect(
                        x, y, building_size, building_size
                    )

                    # Add building as a wall for collision
                    self.walls.append({"rect": building_rect})

                    # Also keep it in buildings list for drawing
                    self.buildings.append({
                        "rect": building_rect, 
                        "height": random.randint(1, 3),
                        "color": random.choice([(200, 200, 200), (180, 180, 180), (160, 160, 160)])
                    })

    def draw(self, screen, camera_x, camera_y):
        try:
            # Draw the map image
            if not hasattr(self, 'map_image') or self.map_image is None:
                print("WARNING: Map image is missing, drawing fallback grid")
                # Draw a placeholder grid
                for x in range(0, self.width, 100):
                    for y in range(0, self.height, 100):
                        rect = pygame.Rect(
                            x - camera_x, 
                            y - camera_y,
                            100, 100
                        )
                        pygame.draw.rect(screen, (50, 50, 50), rect, 1)
            else:
                # Draw a solid color background first to ensure something is visible
                screen.fill((100, 100, 100))  # Medium gray background

                # Draw the map with fixed positioning (no view_rect)
                map_pos = (-camera_x, -camera_y)
                screen.blit(self.map_image, map_pos)

                if not hasattr(self, '_first_draw'):
                    print("Map drawn successfully")
                    self._first_draw = True
                    print(f"Drawing map at position: {map_pos}")
                    print(f"Camera position: ({camera_x}, {camera_y})")
                    print(f"Map dimensions: {self.map_image.get_size()}")

            # Draw a debug grid to help with positioning
            grid_size = 100
            grid_color = (200, 200, 200, 30)  # Very light gray, semi-transparent

            # Create transparent surface for grid
            grid_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

            # Draw vertical grid lines
            for x in range(0, self.width, grid_size):
                screen_x = x - camera_x
                if 0 <= screen_x < screen.get_width():
                    pygame.draw.line(grid_surface, grid_color, 
                                   (screen_x, 0), 
                                   (screen_x, screen.get_height()))

            # Draw horizontal grid lines
            for y in range(0, self.height, grid_size):
                screen_y = y - camera_y
                if 0 <= screen_y < screen.get_height():
                    pygame.draw.line(grid_surface, grid_color, 
                                   (0, screen_y), 
                                   (screen.get_width(), screen_y))

            # Draw center markers
            center_x = self.width/2 - camera_x
            center_y = self.height/2 - camera_y
            if 0 <= center_x < screen.get_width() and 0 <= center_y < screen.get_height():
                pygame.draw.circle(grid_surface, (255, 0, 0, 100), (int(center_x), int(center_y)), 10)

            # Draw visual curbs (if they exist)
            if hasattr(self, 'curbs'):
                for curb in self.curbs:
                    curb_rect = pygame.Rect(
                        curb["rect"].x - camera_x,
                        curb["rect"].y - camera_y,
                        curb["rect"].width,
                        curb["rect"].height
                    )
                    if (curb_rect.right >= 0 and curb_rect.left <= screen.get_width() and
                        curb_rect.bottom >= 0 and curb_rect.top <= screen.get_height()):
                        pygame.draw.rect(grid_surface, (120, 120, 100, 150), curb_rect)

            # Draw buildings for better visibility
            if hasattr(self, 'buildings'):
                for building in self.buildings:
                    building_rect = pygame.Rect(
                        building["rect"].x - camera_x,
                        building["rect"].y - camera_y,
                        building["rect"].width,
                        building["rect"].height
                    )
                    if (building_rect.right >= 0 and building_rect.left <= screen.get_width() and
                        building_rect.bottom >= 0 and building_rect.top <= screen.get_height()):
                        pygame.draw.rect(grid_surface, building["color"], building_rect)

            # Draw traffic lights at intersections
            if hasattr(self, 'traffic_lights'):
                for light in self.traffic_lights:
                    # Calculate screen position
                    light_x, light_y = light['position']
                    screen_x = light_x - camera_x
                    screen_y = light_y - camera_y

                    # Skip if not on screen
                    if (screen_x < -20 or screen_x > screen.get_width() + 20 or
                        screen_y < -20 or screen_y > screen.get_height() + 20):
                        continue

                    # Draw traffic light pole
                    pygame.draw.rect(grid_surface, (50, 50, 50), 
                                  (screen_x - 3, screen_y - 3, 6, 6))

                    # Draw signal housings
                    light_box_size = 10

                    # Horizontal traffic light (controlling east-west traffic)
                    h_light_color = (0, 200, 0) if light['horizontal_green'] else (200, 0, 0)
                    pygame.draw.rect(grid_surface, (80, 80, 80), 
                                  (screen_x - light_box_size - 5, screen_y - light_box_size//2, 
                                   light_box_size, light_box_size))
                    pygame.draw.circle(grid_surface, h_light_color,
                                    (int(screen_x - light_box_size - 5 + light_box_size//2), 
                                     int(screen_y)), 
                                    light_box_size//2 - 1)

                    # Vertical traffic light (controlling north-south traffic)
                    v_light_color = (200, 0, 0) if light['horizontal_green'] else (0, 200, 0)
                    pygame.draw.rect(grid_surface, (80, 80, 80), 
                                  (screen_x - light_box_size//2, screen_y - light_box_size - 5, 
                                   light_box_size, light_box_size))
                    pygame.draw.circle(grid_surface, v_light_color,
                                    (int(screen_x), 
                                     int(screen_y - light_box_size - 5 + light_box_size//2)), 
                                    light_box_size//2 - 1)

            # Blit grid to screen
            screen.blit(grid_surface, (0, 0))

            # Apply time of day lighting effect
        except Exception as e:
            print(f"Error in Map.draw(): {e}")
            import traceback
            traceback.print_exc()
        light_level = self.get_light_level()
        if light_level < 1.0:
            # Create a semi-transparent dark overlay for night time
            darkness = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            alpha = int(255 * (1.0 - light_level))
            darkness.fill((0, 0, 0, alpha))
            screen.blit(darkness, (0, 0))

        # Draw other game objects (vehicles, pedestrians, etc.)
        # Draw pedestrians in proper order
        for pedestrian in self.pedestrians:
            pedestrian.draw(screen, camera_x, camera_y)

        # Draw regular vehicles
        for vehicle in self.vehicles:
            vehicle.draw(screen, camera_x, camera_y)

        # Draw police vehicles
        for vehicle in self.police_vehicles:
            vehicle.draw(screen, camera_x, camera_y)

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

        # Update traffic lights every 3 seconds (180 frames at 60fps)
        if hasattr(self, 'traffic_lights') and hasattr(self, 'traffic_light_timer'):
            self.traffic_light_timer += 1
            if self.traffic_light_timer >= 180:  # 3 seconds at 60 fps
                self.traffic_light_timer = 0
                # Update all traffic lights
                for light in self.traffic_lights:
                    light['timer'] += 1
                    if light['timer'] >= 180:  # Individual light changes every 3 seconds
                        light['timer'] = 0
                        light['horizontal_green'] = not light['horizontal_green']

        # Update regular vehicles with traffic light awareness
        for vehicle in self.vehicles:
            # Check if vehicle is near any traffic light
            at_traffic_light = False
            should_stop = False

            if hasattr(self, 'traffic_lights'):
                for light in self.traffic_lights:
                    # Calculate distance to traffic light
                    light_x, light_y = light['position']
                    distance = math.sqrt((vehicle.x - light_x)**2 + (vehicle.y - light_y)**2)

                    # If vehicle is close to traffic light (within 60 pixels)
                    if distance < 60:
                        at_traffic_light = True
                        # Determine if vehicle is moving horizontally or vertically
                        is_horizontal = vehicle.rotation in [0, 180]  # Horizontal if facing left/right

                        # Check if vehicle should stop based on light color and direction
                        if is_horizontal and not light['horizontal_green']:
                            should_stop = True  # Horizontal traffic has red light
                        elif not is_horizontal and light['horizontal_green']:
                            should_stop = True  # Vertical traffic has red light

                        break  # Only consider the closest traffic light

            # Simple AI behavior with traffic light awareness
            if should_stop:
                # Stop at red light
                vehicle.move(0, 0, self.walls)  # No forward movement, no turning
            else:
                # Basic AI - randomly change direction occasionally
                if random.random() < 0.01:  # 1% chance to change direction each frame
                    vehicle.rotation = random.choice([0, 90, 180, 270])  # Choose a cardinal direction

                # Move forward at normal speed
                vehicle.move(0.5, 0, self.walls)  # Move forward at half speed, no turning

        # Update police AI (override traffic lights when in chase mode)
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

    def generate_roads_from_grid_pattern(self):
        """Create road segments for AI navigation based on a grid pattern similar to GTA"""
        # This method is called when using the procedural map generator
        # It creates road segments that vehicles can follow

        # If roads are already defined, keep them
        if hasattr(self, 'roads') and self.roads:
            print(f"Using existing {len(self.roads)} road segments")
            return

        # Initialize roads list if not already done
        if not hasattr(self, 'roads'):
            self.roads = []

        # Initialize traffic lights if not already done
        if not hasattr(self, 'traffic_lights'):
            self.traffic_lights = []

        # Time for traffic lights
        if not hasattr(self, 'traffic_light_timer'):
            self.traffic_light_timer = 0

        # GTA-style city parameters
        block_size = 320  # Same as in procedural map generator
        road_width = 120  # Width of roads

        # Create horizontal roads
        for y in range(road_width // 2, self.height, block_size):
            # Skip if too close to edge
            if y >= self.height - road_width // 2:
                continue

            # Add a complete road from left to right
            self.roads.append({
                "rect": pygame.Rect(0, y - road_width // 2, self.width, road_width),
                "horizontal": True
            })

        # Create vertical roads
        for x in range(road_width // 2, self.width, block_size):
            # Skip if too close to edge
            if x >= self.width - road_width // 2:
                continue

            # Add a complete road from top to bottom
            self.roads.append({
                "rect": pygame.Rect(x - road_width // 2, 0, road_width, self.height),
                "horizontal": False
            })

        # Create traffic lights at intersections
        for x in range(road_width // 2, self.width, block_size):
            for y in range(road_width // 2, self.height, block_size):
                # Create a traffic light at each intersection
                self.traffic_lights.append({
                    "position": (x, y),
                    "horizontal_green": True,  # Start with horizontal roads having green light
                    "timer": random.randint(0, 180)  # Randomize initial timers to prevent all lights changing at once
                })

        print(f"Generated {len(self.roads)} road segments for AI navigation")
        print(f"Added {len(self.traffic_lights)} traffic lights at intersections")

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


class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.max_speed = 3.5  # Reduced max speed for more authentic GTA1/2 pace
        self.acceleration = 0.1  # Reduced for better acceleration curve
        self.deceleration = 0.15  # Added deceleration for natural slowing
        self.rotation = 0
        # GTA1/2 style: vehicles take up exactly one lane width (40 pixels)
        self.size = (40, 20)  # Increased to match GTA style (wider, proportionally longer)
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
            if abs(self.speed) > self.deceleration:
                self.speed -= (self.deceleration * (1 if self.speed > 0 else -1))
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
        self.max_speed = 4  # Faster than regular vehicles but more realistic for GTA1/2
        self.acceleration = 0.12  # Slightly better acceleration than civilian cars
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
        self.speed = 2.2  # Reduced for more realistic movement
        self.size = 16  # Reduced to match pedestrian size for proper GTA1/2 scaling
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

        # Check collision with walls - but try horizontal and vertical movements separately to allow sliding
        can_move_x = True
        can_move_y = True

        # Create collision detection rectangles
        player_rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
        new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)
        x_rect = pygame.Rect(new_x - self.size/2, self.y - self.size/2, self.size, self.size)
        y_rect = pygame.Rect(self.x - self.size/2, new_y - self.size/2, self.size, self.size)


        # First check X-axis movement only
        if dx != 0:
            x_collision = False
            # Check wall collisions
            for i, wall in enumerate(walls):
                wall_rect = wall["rect"]
                if x_rect.colliderect(wall_rect):
                    x_collision = True
                    can_move_x = False
                    break

            if not x_collision:
                # Ensure we're on a valid road for movement
                # We'll use map directly from walls instead, since walls comes from the map
                # Skip road validation for now to focus on collision detection
                pass

        # Then check Y-axis movement only
        if dy != 0:
            y_collision = False
            # Check wall collisions
            for i, wall in enumerate(walls):
                wall_rect = wall["rect"]
                if y_rect.colliderect(wall_rect):
                    y_collision = True
                    can_move_y = False
                    break

            if not y_collision:
                # We'll use map directly from walls instead, since walls comes from the map
                # Skip road validation for now to focus on collision detection
                pass

        # Apply movement based on what's allowed
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y

        # Update player rectangle after movement
        self.rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

    def draw(self, screen, camera_x, camera_y):
        try:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y

            # Debug output on first draw
            if not hasattr(self, '_first_draw'):
                print(f"Player drawing: world pos ({self.x}, {self.y}), screen pos ({screen_x}, {screen_y})")
                print(f"Camera position: ({camera_x}, {camera_y})")
                self._first_draw = True

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

            # Add debug outline to make character more visible
            pygame.draw.rect(char_surface, (255, 255, 0, 100), (0, 0, self.size * 2, self.size * 2), 1)

            # Top of head (bigger for visibility)
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

            # Draw the rest of the character
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
                # Draw standing legs
                left_leg = [
                    (self.size - self.size * 0.25, self.size + self.size * 0.5),
                    (self.size- self.size * 0.15, self.size + self.size * 0.5),
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
                # Draw weapon with bright highlight for visibility
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

                # Draw the weapon (simple rectangle with glow for visibility)
                weapon_length = 10  # Slightly bigger
                weapon_width = 3
                weapon_surface = pygame.Surface((weapon_length, weapon_width), pygame.SRCALPHA)
                pygame.draw.rect(weapon_surface, (255, 100, 0), (0, 0, weapon_length, weapon_width))  # Bright orange

                # Add glow effect
                glow_surface = pygame.Surface((weapon_length+4, weapon_width+4), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 255, 0, 100), (0, 0, weapon_length+4, weapon_width+4))  # Yellow glow

                # Rotate weapon based on direction
                rotated_weapon = pygame.transform.rotate(weapon_surface, -weapon_angle)
                rotated_glow = pygame.transform.rotate(glow_surface, -weapon_angle)

                # Draw weapon glow on character
                char_surface.blit(rotated_glow, 
                                (weapon_x - rotated_glow.get_width()/2, 
                                 weapon_y - rotated_glow.get_height()/2))

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
        except Exception as e:
            print(f"Error in player.draw(): {e}")
            import traceback
            traceback.print_exc()

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
        self.speed = random.uniform(0.5, 1.1)  # Reduced speed range for more authentic movement
        self.size = 16  # Matches the player's size for consistent scaling
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

        # Alsoflee from vehicles moving fast
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
                    (self.size- self.size * 0.15, self.size + self.size * 0.5),
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
            try:
                # Load and scale the map image
                self.map_image = pygame.image.load('attached_assets/IMG_7818.jpeg').convert()
                # Scale image to a reasonable size
                self.width = 2400  # Fixed size for consistent gameplay
                self.height = 1800
                self.map_image = pygame.transform.scale(self.map_image, (self.width, self.height))
            except pygame.error as e:
                print(f"Error loading map image: {e}")
                # Create fallback surface if image fails to load
                self.map_image = pygame.Surface((self.width, self.height))
                self.map_image.fill((100, 100, 100))  # Gray background

            self.tile_size = 32
            self.walls = []
            self.roads = []
            self.vehicles = []
            self.police_vehicles = []
            self.pedestrians = []

            # Create game objects
            self.create_city_layout()
            self.spawn_vehicles(15)
            self.spawn_police(3)
            self.spawn_pedestrians(30)

            # Time of day system
            self.time_of_day = 0.3
            self.time_speed = 0.0001
            self.sky_colors = {
                0.0: (10, 10, 40),     # Midnight
                0.25: (200, 120, 40),  # Sunrise
                0.5: (100, 150, 255),  # Noon
                0.75: (255, 100, 50),  # Sunset
                1.0: (10, 10, 40)      # Midnight again
            }

        def create_city_layout(self):
            try:
                # Create roads based on image analysis
                surface_array = pygame.surfarray.array3d(self.map_image)
                road_threshold = 100  # Adjust based on your image

                # Sample points in the image to detect roads
                step = 32  # Sample every 32 pixels
                for x in range(0, self.width, step):
                    for y in range(0, self.height, step):
                        # Get average brightness of area
                        area = surface_array[x:min(x+step, self.width), 
                                          y:min(y+step, self.height)]
                        brightness = area.mean()

                        if brightness < road_threshold:
                            # Dark area - likely a road
                            is_horizontal = True if area.shape[1] > area.shape[0] else False
                            road = pygame.Rect(x, y, step, step)
                            self.roads.append({"rect": road, "horizontal": is_horizontal})

                            # Add walls along road edges
                            wall_width = 8
                            if is_horizontal:
                                # Add walls above and below road
                                self.walls.append({"rect": pygame.Rect(x, y - wall_width, step, wall_width)})
                                self.walls.append({"rect": pygame.Rect(x, y + step, step, wall_width)})
                            else:
                                # Add walls to left and right of road
                                self.walls.append({"rect": pygame.Rect(x - wall_width, y, wall_width, step)})
                                self.walls.append({"rect": pygame.Rect(x + step, y, wall_width, step)})
            except Exception as e:
                print(f"Error creating city layout: {e}")
                # Create fallback layout
                self.create_fallback_layout()

        def create_fallback_layout(self):
            # Create a basic grid layout if image analysis fails
            road_width = 96
            block_size = 300

            # Create horizontal and vertical roads
            for y in range(0, self.height, block_size):
                self.roads.append({"rect": pygame.Rect(0, y, self.width, road_width), "horizontal": True})

            for x in range(0, self.width, block_size):
                self.roads.append({"rect": pygame.Rect(x, 0, road_width, self.height), "horizontal": False})

        def draw(self, screen, camera_x, camera_y):
            # Draw the map image
            view_rect = pygame.Rect(camera_x, camera_y, screen.get_width(), screen.get_height())
            screen.blit(self.map_image, (0, 0), view_rect)

            # Apply time of day lighting effect
            light_level = self.get_light_level()
            if light_level < 1.0:
                # Create a semi-transparent dark overlay for night time
                darkness = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                alpha = int(255 * (1.0 - light_level))
                darkness.fill((0, 0, 0, alpha))
                screen.blit(darkness, (0, 0))

            # Draw other game objects (vehicles, pedestrians, etc.)
            # Draw pedestrians in proper order
            for pedestrian in self.pedestrians:
                pedestrian.draw(screen, camera_x, camera_y)

            # Draw regular vehicles
            for vehicle in self.vehicles:
                vehicle.draw(screen, camera_x, camera_y)

            # Draw police vehicles
            for vehicle in self.police_vehicles:
                vehicle.draw(screen, camera_x, camera_y)

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


class Game:
    def __init__(self):
        # Only set SDL variables for Replit environment
        if os.environ.get('REPL_ID'):
            os.environ['SDL_VIDEODRIVER'] = 'x11'
            os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'  # Force software rendering
            print("Running in Replit environment, using x11 driver")

        # Don't re-initialize pygame if already done
        if not pygame.get_init():
            pygame.init()

        # Print detailed screen information
        print("Creating display...")

        self.width = 800
        self.height = 600

        try:
            # Use resizable window for desktop mode
            is_desktop = not os.environ.get('REPL_ID') and not detect_mobile()

            if is_desktop:
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                pygame.display.set_caption("GTA-Style Game - Desktop Mode (Resizable)")
                print("Desktop mode detected, using resizable window")
            else:
                self.screen = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("GTA-Style Game")

            print(f"Display mode set: {self.width}x{self.height}")
        except Exception as e:
            print(f"Error setting display mode: {e}")
            raise

        # Print control instructions
        print("=== GAME CONTROLS ===")
        print("WASD: Move character")
        print("E: Enter/exit vehicle")
        print("SPACE: Shoot (if you have a weapon)")
        print("P or ESC: Pause game")
        print("====================")

        # Create game objects
        self.map = Map()

        # Find a valid spawn point on a road
        spawn_x = self.map.width // 2
        spawn_y = self.map.height // 2
        for road in self.map.roads:
            if road["rect"].collidepoint(spawn_x, spawn_y):
                break

        self.player = Player(spawn_x, spawn_y)
        self.player.game = self  # Add reference to game object

        # Initialize camera centered on player
        self.camera_x = self.player.x - self.width/2
        self.camera_y = self.player.y - self.height/2

        # Force camera to valid position
        self.camera_x = max(0, min(self.camera_x, self.map.width - self.width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - self.height))

        print(f"Initial player position: ({self.player.x}, {self.player.y})")
        print(f"Initial camera position: ({self.camera_x}, {self.camera_y})")

        # Game state
        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()
        self.frame_count = 0  # Add frame counter for timing events

        # Debug info
        self.show_debug = False
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)

        # Mobile touch controls
        self.touch_enabled = True
        self.touch_buttons = {}
        
        # Auto control settings for VNC/keyboard issues
        self.auto_control_enabled = True  # Set to True to enable automatic movement
        self.auto_control_type = "rotate4"  # Options: "rotate4", "random", "none"
        self.auto_control_timer = 0
        self.auto_control_duration = 60  # How many frames to hold each direction
        self.show_auto_control_info = True  # Show the info screen on startup
        self.touch_button_radius = 40
        self.touch_button_margin = 20
        self.touch_button_alpha = 180  # Semi-transparent
        self.touch_active = {}  # Track which buttons are being pressed

        # Initialize touch controls
        self.init_touch_controls()

        # Create pause menu button
        self.pause_button = {
            "pos": (self.width - 40, 40),
            "radius": 30,
            "color": (100, 100, 100),
            "label": "II",
        }
        self.pause_active = False

    def draw_debug_info(self):
        if not self.show_debug:
            return

        debug_info = [
            f"FPS: {int(self.clock.get_fps())}",
            f"Player Pos: ({int(self.player.x)}, {int(self.player.y)})",
            f"In Vehicle: {self.player.in_vehicle is not None}",
            f"Wanted Level: {self.player.wanted_level:.1f}",
            f"Pedestrians: {len(self.map.pedestrians)}",
            f"Police: {len(self.map.police_vehicles)}",
            f"Auto-control: {hasattr(self, 'auto_control_enabled') and self.auto_control_enabled}",
            f"Auto-timer: {hasattr(self, 'auto_control_timer') and self.auto_control_timer}"
        ]

        y = 10
        for info in debug_info:
            text = self.font.render(info, True, (255, 255, 255))
            self.screen.blit(text, (10, y))
            y += 20
            
    def draw_auto_control_info(self):
        """Draw the auto-control information overlay"""
        if not hasattr(self, 'auto_control_enabled') or not self.auto_control_enabled:
            return
            
        # Show auto-control status in the top right corner
        if hasattr(self, 'auto_control_timer') and self.auto_control_timer > 0:
            # Draw semi-transparent background
            overlay = pygame.Surface((300, 80), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Black with alpha
            self.screen.blit(overlay, (self.width - 310, 10))
            
            # Draw auto-control text
            auto_text = self.font.render("AUTO-CONTROL ACTIVE", True, (255, 255, 0))
            self.screen.blit(auto_text, (self.width - 300, 20))
            
            # Show more details about current auto control state
            if not self.player.in_vehicle:
                mode_text = self.font.render("Mode: Pedestrian", True, (200, 200, 200))
            else:
                mode_text = self.font.render("Mode: Vehicle", True, (200, 200, 200))
            self.screen.blit(mode_text, (self.width - 300, 45))
            
            # Show a hint about keyboard controls
            hint_text = self.font.render("Press any movement key to take control", True, (200, 200, 200))
            self.screen.blit(hint_text, (self.width - 300, 70))

    def draw_controls_help(self):
        controls = [
            "WASD: Move",
            "E: Enter/Exit Vehicle",
            "SPACE: Shoot",
            "F3: Toggle Debug Info"
        ]

        y = self.height - len(controls) * 20 - 10
        for control in controls:
            text = self.font.render(control, True, (255, 255, 255))
            self.screen.blit(text, (10, y))
            y += 20

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Debug output for key presses to help diagnose issues
                print(f"Key pressed: {pygame.key.name(event.key)} (key code: {event.key})")
                
                # Update our custom key states for KEYDOWN events
                if event.key == pygame.K_w:
                    self.key_states['w'] = True
                    print("W key pressed - state set to True")
                elif event.key == pygame.K_a:
                    self.key_states['a'] = True
                    print("A key pressed - state set to True")
                elif event.key == pygame.K_s:
                    self.key_states['s'] = True
                    print("S key pressed - state set to True")
                elif event.key == pygame.K_d:
                    self.key_states['d'] = True
                    print("D key pressed - state set to True")
                elif event.key == pygame.K_UP:
                    self.key_states['up'] = True
                    print("UP key pressed - state set to True")
                elif event.key == pygame.K_DOWN:
                    self.key_states['down'] = True
                    print("DOWN key pressed - state set to True")
                elif event.key == pygame.K_LEFT:
                    self.key_states['left'] = True
                    print("LEFT key pressed - state set to True")
                elif event.key == pygame.K_RIGHT:
                    self.key_states['right'] = True
                    print("RIGHT key pressed - state set to True")
                elif event.key == pygame.K_SPACE:
                    self.key_states['space'] = True
                    if not self.paused:
                        self.player.shoot()
                elif event.key == pygame.K_e:
                    self.key_states['e'] = True
                    if not self.paused:
                        self.player.enter_exit_vehicle(self.map.vehicles + self.map.police_vehicles)
                elif event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_ESCAPE:
                    # Toggle pause state with ESC key
                    self.paused = not self.paused
                # Add a quick exit key for PC testing
                elif event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    print("Ctrl+Q pressed - exiting game")
                    self.running = False
                    
            elif event.type == pygame.KEYUP:
                # Update our custom key states for KEYUP events
                if event.key == pygame.K_w:
                    self.key_states['w'] = False
                elif event.key == pygame.K_a:
                    self.key_states['a'] = False
                elif event.key == pygame.K_s:
                    self.key_states['s'] = False
                elif event.key == pygame.K_d:
                    self.key_states['d'] = False
                elif event.key == pygame.K_UP:
                    self.key_states['up'] = False
                elif event.key == pygame.K_DOWN:
                    self.key_states['down'] = False
                elif event.key == pygame.K_LEFT:
                    self.key_states['left'] = False
                elif event.key == pygame.K_RIGHT:
                    self.key_states['right'] = False
                elif event.key == pygame.K_SPACE:
                    self.key_states['space'] = False
                elif event.key == pygame.K_e:
                    self.key_states['e'] = False
            # Handle window resize events for PC mode
            elif event.type == pygame.VIDEORESIZE:
                # Only handle resize events when not on Replit
                if not os.environ.get('REPL_ID'):
                    print(f"Window resized to {event.w}x{event.h}")
                    self.width = event.w
                    self.height = event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

            # Touch support for mobile
            elif event.type == pygame.MOUSEBUTTONDOWN and self.touch_enabled:
                # Check for pause button press
                pos = pygame.mouse.get_pos()
                pause_pos = self.pause_button["pos"]
                pause_distance = math.sqrt((pos[0] - pause_pos[0])**2 + (pos[1] - pause_pos[1])**2)
                if pause_distance <= self.pause_button["radius"]:
                    # Toggle pause state
                    self.paused = not self.paused
                    self.pause_active = True
                    continue  # Skip other button checks when pause is pressed

                # Only process other buttons when not paused
                if not self.paused:
                    # Check if any touch buttons were pressed
                    for name, button in self.touch_buttons.items():
                        # Check if touch is within button radius
                        button_pos = button["pos"]
                        distance = math.sqrt((pos[0] - button_pos[0])**2 + (pos[1] - button_pos[1])**2)

                        if distance <= button["radius"]:
                            self.touch_active[name] = True

                            # Perform action immediately for action buttons
                            if name == "action":
                                self.player.enter_exit_vehicle(self.map.vehicles + self.map.police_vehicles)
                            elif name == "shoot":
                                self.player.shoot()

            elif event.type == pygame.MOUSEBUTTONUP and self.touch_enabled:
                # Reset all touch buttons and pause button
                for name in self.touch_active:
                    self.touch_active[name] = False
                self.pause_active = False

            # Track touch movement for continuous control (only when not paused)
            elif event.type == pygame.MOUSEMOTION and self.touch_enabled and pygame.mouse.get_pressed()[0] and not self.paused:
                # Check if a direction button is being touched
                pos = pygame.mouse.get_pos()
                for name, button in self.touch_buttons.items():
                    # Only check directional buttons
                    if name not in ["up", "down", "left", "right"]:
                        continue

                    # Check if touch is within button radius
                    button_pos = button["pos"]
                    distance = math.sqrt((pos[0] - button_pos[0])**2 + (pos[1] - button_pos[1])**2)

                    if distance <= button["radius"]:
                        self.touch_active[name] = True
                    else:
                        self.touch_active[name] = False

    def draw_pause_button(self):
        """Draw the pause button in the corner of the screen"""
        if not self.touch_enabled:
            return

        # Create semi-transparent surface
        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Get button properties
        color = list(self.pause_button["color"])
        if self.pause_active or self.paused:
            # Brighten when active or paused
            color = [min(c + 70, 255) for c in color]

        # Add alpha
        color.append(self.touch_button_alpha)

        # Draw button
        pygame.draw.circle(button_surface, color, self.pause_button["pos"], self.pause_button["radius"])

        # Add label
        font = pygame.font.SysFont(None, 36)
        if self.paused:
            label = font.render("▶", True, (255, 255, 255))  # Play symbol when paused
        else:
            label = font.render(self.pause_button["label"], True, (255, 255, 255))
        label_rect = label.get_rect(center=self.pause_button["pos"])
        button_surface.blit(label, label_rect)

        # Blit to screen
        self.screen.blit(button_surface, (0, 0))

    def draw_pause_menu(self):
        """Draw the pause menu with map overview"""
        if not self.paused:
            return

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark semi-transparent background
        self.screen.blit(overlay, (0, 0))

        # Draw title
        title = self.big_font.render("GAME PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width/2, 50))
        self.screen.blit(title, title_rect)

        # Draw full map at reduced scale
        map_scale = 0.25  # Scale to fit on screen
        map_width = int(self.map.width * map_scale)
        map_height = int(self.map.height * map_scale)

        # Create scaled map surface
        scaled_map = pygame.transform.scale(self.map.map_image, (map_width, map_height))

        # Calculate position to center map
        map_x = self.width/2 - map_width/2
        map_y = self.height/2 - map_height/2 + 20  # +20 to account for title

        # Draw scaled map
        self.screen.blit(scaled_map, (map_x, map_y))

        # Draw player position on map
        player_map_x = map_x + (self.player.x * map_scale)
        player_map_y = map_y + (self.player.y * map_scale)
        pygame.draw.circle(self.screen, (255, 0, 0), (int(player_map_x), int(player_map_y)), 5)

        # Draw resume instructions
        instr = self.font.render("Touch pause button or press ESC to resume", True, (255, 255, 255))
        instr_rect = instr.get_rect(center=(self.width/2, self.height - 50))
        self.screen.blit(instr, instr_rect)

    def init_touch_controls(self):
        """Initialize touch control buttons and their positions"""
        # D-pad positions (bottom left)
        center_x = self.touch_button_margin + self.touch_button_radius * 3
        center_y = self.height - self.touch_button_margin - self.touch_button_radius * 3

        # Direction buttons (D-pad style)
        self.touch_buttons["up"] = {
            "pos": (center_x, center_y - self.touch_button_radius * 2),
            "radius": self.touch_button_radius,
            "color": (150, 150, 150),
            "label": "↑",
            "key": pygame.K_w
        }
        self.touch_buttons["down"] = {
            "pos": (center_x, center_y + self.touch_button_radius * 2),
            "radius": self.touch_button_radius,
            "color": (150, 150, 150),
            "label": "↓",
            "key": pygame.K_s
        }
        self.touch_buttons["left"] = {
            "pos": (center_x - self.touch_button_radius * 2, center_y),
            "radius": self.touch_button_radius,
            "color": (150, 150, 150),
            "label": "←",
            "key": pygame.K_a
        }
        self.touch_buttons["right"] = {
            "pos": (center_x + self.touch_button_radius * 2, center_y),
            "radius": self.touch_button_radius,
            "color": (150, 150, 150),
            "label": "→",
            "key": pygame.K_d
        }

        # Action buttons (bottom right)
        # Enter/exit vehicle
        self.touch_buttons["action"] = {
            "pos": (self.width - self.touch_button_margin - self.touch_button_radius * 3, 
                   self.height - self.touch_button_margin - self.touch_button_radius * 2),
            "radius": self.touch_button_radius,
            "color": (0, 180, 0),
            "label": "E",
            "key": pygame.K_e
        }

        # Shoot
        self.touch_buttons["shoot"] = {
            "pos": (self.width - self.touch_button_margin - self.touch_button_radius, 
                   self.height - self.touch_button_margin - self.touch_button_radius * 4),
            "radius": self.touch_button_radius,
            "color": (180, 0, 0),
            "label": "🔫",
            "key": pygame.K_SPACE
        }

        # Initialize active state for all buttons
        for button in self.touch_buttons:
            self.touch_active[button] = False

    def draw_touch_controls(self):
        """Draw on-screen touch controls"""
        if not self.touch_enabled:
            return

        # Create a surface for the semi-transparent controls
        control_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw each button
        for name, button in self.touch_buttons.items():
            # Draw the button circle
            color = list(button["color"])

            # Make active buttons brighter
            if self.touch_active[name]:
                # Brighten the color
                color = [min(c + 70, 255) for c in color]

            # Set alpha transparency
            color.append(self.touch_button_alpha)

            # Draw the button
            pygame.draw.circle(control_surface, color, button["pos"], button["radius"])

            # Add button label
            font = pygame.font.SysFont(None, 36)
            label = font.render(button["label"], True, (255, 255, 255))
            label_rect = label.get_rect(center=button["pos"])
            control_surface.blit(label, label_rect)

        # Blit the control surface onto the screen
        self.screen.blit(control_surface, (0, 0))

    def update_camera(self):
        # Use a much tighter zoom level for authentic GTA1/2 view
        # This creates a very zoomed-in view focused primarily on the player and immediate surroundings
        zoom_factor = 0.4  # Much smaller number for much closer zoom (GTA1/2 style)

        # Calculate target camera position (centered on player with zoom)
        target_camera_x = self.player.x - (self.width * zoom_factor)
        target_camera_y = self.player.y - (self.height * zoom_factor)

        # Smooth camera movement with faster response time
        camera_speed = 0.2  # Higher value = faster camera tracking
        self.camera_x += (target_camera_x - self.camera_x) * camera_speed
        self.camera_y += (target_camera_y - self.camera_y) * camera_speed

        # Keep camera within map bounds with a margin to prevent seeing beyond the map edge
        margin = 50
        self.camera_x = max(margin, min(self.camera_x, self.map.width - self.width - margin))
        self.camera_y = max(margin, min(self.camera_y, self.map.height - self.height - margin))

    def run(self):
        print("Game.run() started")
        
        # Define direct keyboard state variables that bypass pygame.key.get_pressed()
        # This will help with environments where key presses aren't properly detected
        self.key_states = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'w': False,
            'a': False,
            's': False,
            'd': False,
            'space': False,
            'e': False
        }
        
        # Reset auto-control timer for this game session
        self.auto_control_timer = 0
        
        while self.running:
            # Handle events and update our custom key state tracking
            self.handle_events()

            # Get keyboard state - force refresh before checking
            pygame.event.pump()  # Process event queue to ensure key state is current
            keys = pygame.key.get_pressed()
            
            # Update our custom key tracking from pygame's key states
            # This gives us two layers of key tracking for robustness
            self.key_states['up'] = keys[pygame.K_UP]
            self.key_states['down'] = keys[pygame.K_DOWN]
            self.key_states['left'] = keys[pygame.K_LEFT]
            self.key_states['right'] = keys[pygame.K_RIGHT]
            self.key_states['w'] = keys[pygame.K_w]
            self.key_states['a'] = keys[pygame.K_a]
            self.key_states['s'] = keys[pygame.K_s]
            self.key_states['d'] = keys[pygame.K_d]
            self.key_states['space'] = keys[pygame.K_SPACE]
            self.key_states['e'] = keys[pygame.K_e]

            # Clear screen for each frame
            self.screen.fill((0, 0, 0))

            # Print debug once to see if we're getting here
            if hasattr(self, '_first_run') == False:
                print("First frame rendering...")
                self._first_run = True

            # Only update game state if not paused
            if not self.paused:
                if not self.player.in_vehicle:
                    dx = 0
                    dy = 0
                    # Add a much clearer key press debug
                    print(f"DEBUG: Key states - W:{keys[pygame.K_w]} A:{keys[pygame.K_a]} S:{keys[pygame.K_s]} D:{keys[pygame.K_d]}")
                    print(f"DEBUG: Arrow keys - UP:{keys[pygame.K_UP]} LEFT:{keys[pygame.K_LEFT]} DOWN:{keys[pygame.K_DOWN]} RIGHT:{keys[pygame.K_RIGHT]}")
                    print(f"DEBUG: Custom key tracking - W:{self.key_states['w']} A:{self.key_states['a']} S:{self.key_states['s']} D:{self.key_states['d']}")
                    print(f"DEBUG: Custom arrow tracking - UP:{self.key_states['up']} LEFT:{self.key_states['left']} DOWN:{self.key_states['down']} RIGHT:{self.key_states['right']}")

                    # First check our custom key state tracking
                    if self.key_states['w'] or self.key_states['up']: 
                        dy -= 3  # Faster movement
                        print("UP control active - Moving UP FAST")
                    if self.key_states['s'] or self.key_states['down']: 
                        dy += 3  # Faster movement
                        print("DOWN control active - Moving DOWN FAST")
                    if self.key_states['a'] or self.key_states['left']: 
                        dx -= 3  # Faster movement
                        print("LEFT control active - Moving LEFT FAST")
                    if self.key_states['d'] or self.key_states['right']: 
                        dx += 3  # Faster movement
                        print("RIGHT control active - Moving RIGHT FAST")
                    
                    # Fallback to normal pygame key detection if our custom tracking fails
                    if dx == 0 and dy == 0:
                        if keys[pygame.K_w] or keys[pygame.K_UP]: 
                            dy -= 3
                            print("Fallback UP key detected")
                        if keys[pygame.K_s] or keys[pygame.K_DOWN]: 
                            dy += 3
                            print("Fallback DOWN key detected")
                        if keys[pygame.K_a] or keys[pygame.K_LEFT]: 
                            dx -= 3
                            print("Fallback LEFT key detected")
                        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: 
                            dx += 3
                            print("Fallback RIGHT key detected")

                    # Touch input
                    if self.touch_enabled:
                        # Make sure touch_active dictionary is initialized
                        if not hasattr(self, 'touch_active') or self.touch_active is None:
                            self.touch_active = {}

                        # Debug touch button states
                        print(f"Touch states: UP:{self.touch_active.get('up', False)} DOWN:{self.touch_active.get('down', False)} LEFT:{self.touch_active.get('left', False)} RIGHT:{self.touch_active.get('right', False)}")

                        if self.touch_active.get("up", False): 
                            dy -= 3  # Faster movement to match keyboard
                            print("Touch UP active - Moving UP FAST")
                        if self.touch_active.get("down", False): 
                            dy += 3  # Faster movement to match keyboard
                            print("Touch DOWN active - Moving DOWN FAST")
                        if self.touch_active.get("left", False): 
                            dx -= 3  # Faster movement to match keyboard
                            print("Touch LEFT active - Moving LEFT FAST")
                        if self.touch_active.get("right", False): 
                            dx += 3  # Faster movement to match keyboard
                            print("Touch RIGHT active - Moving RIGHT FAST")

                        # VNC auto-control for players when keyboard isn't working
                        # For players in VNC or other environments where keyboard might not work
                        if dx == 0 and dy == 0 and self.auto_control_enabled:
                            # Update the auto-control timer
                            self.auto_control_timer += 1
                            
                            # Determine current phase of movement based on timer
                            if self.auto_control_type == "rotate4":
                                # Cycle through 4 directions: left, up, right, down
                                phase = (self.auto_control_timer // self.auto_control_duration) % 4
                                
                                # Only start auto-control after a delay to let real input take precedence
                                if self.auto_control_timer > 120:  # Wait 2 seconds (120 frames at 60fps)
                                    if phase == 0:
                                        dx = -3  # left (faster)
                                        dy = 0
                                        # Set key states for visual feedback in debug
                                        self.key_states['left'] = True
                                        self.key_states['a'] = True
                                        print("AUTO: Moving LEFT")
                                    elif phase == 1:
                                        dx = 0 
                                        dy = -3  # up (faster)
                                        self.key_states['up'] = True
                                        self.key_states['w'] = True
                                        print("AUTO: Moving UP")
                                    elif phase == 2:
                                        dx = 3  # right (faster)
                                        dy = 0
                                        self.key_states['right'] = True
                                        self.key_states['d'] = True
                                        print("AUTO: Moving RIGHT")
                                    else:
                                        dx = 0
                                        dy = 3  # down (faster)
                                        self.key_states['down'] = True
                                        self.key_states['s'] = True
                                        print("AUTO: Moving DOWN")
                                    
                                    # After each movement cycle, trigger a random action
                                    if self.auto_control_timer % (self.auto_control_duration * 4) == 0:
                                        # Press E to try to enter/exit vehicles
                                        print("AUTO: Trying to enter/exit vehicle")
                                        self.key_states['e'] = True
                                        self.player.enter_exit_vehicle(self.map.vehicles + self.map.police_vehicles)
                                    
                                    # Fire weapon occasionally
                                    if self.auto_control_timer % (self.auto_control_duration * 7) == 0:
                                        print("AUTO: Firing weapon")
                                        self.key_states['space'] = True
                                        self.player.shoot()
                            
                            # Reset auto-control states after every 4000 frames to avoid potential issues
                            if self.auto_control_timer > 4000:
                                self.auto_control_timer = 0

                    # Debug info about input values
                    if dx != 0 or dy != 0:
                        print(f"Movement input values: dx={dx}, dy={dy}")

                    self.player.move(dx, dy, self.map.walls)
                else:
                    # Vehicle controls
                    forward = 0
                    turn = 0
                    
                    # Print debugging info for keyboard states
                    print(f"DEBUG: Vehicle - Custom key states - W:{self.key_states['w']} S:{self.key_states['s']} A:{self.key_states['a']} D:{self.key_states['d']}")
                    print(f"DEBUG: Vehicle - Custom arrow states - UP:{self.key_states['up']} DOWN:{self.key_states['down']} LEFT:{self.key_states['left']} RIGHT:{self.key_states['right']}")
                    
                    # First try custom key state tracking
                    if self.key_states['w'] or self.key_states['up']: forward = 1
                    if self.key_states['s'] or self.key_states['down']: forward = -1
                    if self.key_states['a'] or self.key_states['left']: turn = -1
                    if self.key_states['d'] or self.key_states['right']: turn = 1
                    
                    # If no input from custom tracking, try standard pygame key detection
                    if forward == 0 and turn == 0:
                        if keys[pygame.K_w] or keys[pygame.K_UP]: forward = 1
                        if keys[pygame.K_s] or keys[pygame.K_DOWN]: forward = -1
                        if keys[pygame.K_a] or keys[pygame.K_LEFT]: turn = -1
                        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: turn = 1
                    
                    # Debug output for vehicle controls
                    if forward != 0 or turn != 0:
                        print(f"Vehicle controls: forward={forward}, turn={turn}")

                    # Touch input
                    if self.touch_enabled:
                        if self.touch_active["up"]: forward = 1
                        if self.touch_active["down"]: forward = -1
                        if self.touch_active["left"]: turn = -1
                        if self.touch_active["right"]: turn = 1
                    
                    # Auto-control for vehicle if no input detected
                    if forward == 0 and turn == 0 and self.auto_control_enabled:
                        # Update auto-control timer
                        self.auto_control_timer += 1
                        
                        # Only start auto-control after a delay
                        if self.auto_control_timer > 180:  # Wait 3 seconds (180 frames)
                            phase = (self.auto_control_timer // self.auto_control_duration) % 6
                            
                            # More complex vehicle behavior - drive forward with occasional turns
                            if phase == 0:
                                forward = 1  # Drive forward
                                turn = 0
                                self.key_states['w'] = True
                                self.key_states['up'] = True
                                print("AUTO VEHICLE: Driving forward")
                            elif phase == 1:
                                forward = 1  # Turn right while moving
                                turn = 1
                                self.key_states['w'] = True
                                self.key_states['d'] = True
                                print("AUTO VEHICLE: Turning right")
                            elif phase == 2:
                                forward = 1  # Drive forward again
                                turn = 0
                                self.key_states['w'] = True
                                self.key_states['up'] = True
                                print("AUTO VEHICLE: Driving forward")
                            elif phase == 3:
                                forward = 1  # Turn left while moving
                                turn = -1
                                self.key_states['w'] = True
                                self.key_states['a'] = True
                                print("AUTO VEHICLE: Turning left")
                            elif phase == 4:
                                forward = 1  # More forward
                                turn = 0
                                self.key_states['w'] = True
                                self.key_states['up'] = True
                                print("AUTO VEHICLE: Driving forward")
                            else:
                                forward = -1  # Occasional reverse
                                turn = 0
                                self.key_states['s'] = True
                                self.key_states['down'] = True
                                print("AUTO VEHICLE: Reversing")
                            
                            # Occasionally exit the vehicle
                            if self.auto_control_timer % (self.auto_control_duration * 12) == 0:
                                print("AUTO: Trying to exit vehicle")
                                self.key_states['e'] = True
                                self.player.enter_exit_vehicle(self.map.vehicles + self.map.police_vehicles)

                    self.player.in_vehicle.move(forward, turn, self.map.walls)
                    # Update player position to vehicle position
                    self.player.x = self.player.in_vehicle.x
                    self.player.y = self.player.in_vehicle.y

                # Update game objects
                self.player.update()
                self.map.update(self.player)
                self.update_camera()

            # Draw everything
            self.screen.fill(self.map.get_sky_color())  # Clear screen with sky color
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
            
            # Draw auto-control information if active
            self.draw_auto_control_info()

            # Only show controls help when not paused
            if not self.paused:
                self.draw_controls_help()

            self.draw_debug_info()

            # Draw touch controls if not paused
            if self.touch_enabled and not self.paused:
                self.draw_touch_controls()

            # Always draw pause button
            if self.touch_enabled:
                self.draw_pause_button()

            # Draw pause menu if paused
            if self.paused:
                self.draw_pause_menu()

            # Ensure the display is updated
            try:
                # Use both update and flip to ensure rendering
                pygame.display.update()
                pygame.display.flip()

                if not hasattr(self, '_display_updated'):
                    print("First display update successful")
                    self._display_updated = True
            except Exception as e:
                print(f"Error updating display: {e}")

            # Increment frame counter
            self.frame_count += 1

            # Control frame rate
            self.clock.tick(60)

def detect_mobile():
    """Try to detect if we're running on a mobile device"""
    try:
        # On Replit, this can help determine if we're on a mobile browser
        user_agent = os.environ.get('HTTP_USER_AGENT', '').lower()
        return any(term in user_agent for term in ['android', 'iphone', 'ipad', 'mobile'])
    except:
        # Fallback - assume desktop
        return False

def main():
    # Allow separate window for PC users
    # Don't force specific video driver, let Python choose the best available
    # Detect if we're on Replit and only use x11 if we are
    if os.environ.get('REPL_ID'):
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'

    # Only set mobile mode if we're actually on mobile
    is_mobile = detect_mobile()

    try:
        pygame.init()
        print("Pygame initialized successfully")

        # Print display info
        print(f"Display driver: {pygame.display.get_driver()}")
        print(f"Display info: {pygame.display.Info()}")

        game = Game()

        # Set touch mode based on device
        game.touch_enabled = is_mobile

        # If we're on mobile, adjust display settings
        if is_mobile:
            print("Mobile device detected, enabling touch controls")
            # Could adjust other settings here like UI scaling

        game.run()
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()