"""
Side Activities for GTA-style South Park Canadian game
This module implements various criminal-themed side activities and missions
in the style of GTA 1/2 with South Park Canadian characters.
"""
import random
import math
import pygame

class SideActivity:
    """Base class for all side activities"""
    def __init__(self, game, activity_type, name, description):
        self.game = game
        self.type = activity_type
        self.name = name
        self.description = description
        self.active = False
        self.completed = False
        self.failed = False
        self.timer = 0
        self.max_time = 0
        self.progress = 0
        self.required_progress = 100
        self.reward = 100
        self.stage = 0
        self.message = ""
        self.message_timer = 0
        self.trigger_points = []  # [(x, y, radius), ...] locations where activity can be triggered
        self.target_markers = []  # [(x, y, type), ...] markers for objectives

    def can_trigger(self, player_x, player_y):
        """Check if player is near a trigger point"""
        if self.active or self.completed:
            return False
            
        for x, y, radius in self.trigger_points:
            if math.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < radius:
                return True
        return False
    
    def trigger(self):
        """Start the activity"""
        self.active = True
        self.stage = 0
        self.timer = 0
        self.progress = 0
        self.message = f"Started: {self.name}"
        self.message_timer = 180
        
    def update(self, player, walls, vehicles, pedestrians):
        """Update activity state - override in subclasses"""
        if not self.active:
            return
            
        if self.message_timer > 0:
            self.message_timer -= 1
            
        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0 and self.max_time > 0:
                self.fail("Time's up, eh! You couldn't finish, buddy!")
                
        if self.progress >= self.required_progress:
            self.complete()
            
    def draw(self, screen, camera_x, camera_y, font):
        """Draw activity elements and UI"""
        if not self.active:
            return
            
        # Draw target markers
        for x, y, marker_type in self.target_markers:
            screen_x = x - camera_x
            screen_y = y - camera_y
            
            # Skip if off-screen
            if (screen_x < -50 or screen_x > screen.get_width() + 50 or 
                screen_y < -50 or screen_y > screen.get_height() + 50):
                continue
                
            # Draw different marker types
            if marker_type == "pickup":
                pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y)), 10)
                pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 12, 2)
            elif marker_type == "dropoff":
                pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 10)
                pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 12, 2)
            elif marker_type == "checkpoint":
                pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 8)
                pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 10, 2)
                
        # Draw current message if timer is active
        if self.message_timer > 0:
            message_surface = font.render(self.message, True, (255, 255, 255))
            screen.blit(message_surface, (screen.get_width() // 2 - message_surface.get_width() // 2, 50))
            
        # Draw progress bar if activity is active
        if self.active:
            progress_width = 200
            progress_height = 20
            progress_x = screen.get_width() // 2 - progress_width // 2
            progress_y = 80
            
            # Draw background
            pygame.draw.rect(screen, (50, 50, 50), (progress_x, progress_y, progress_width, progress_height))
            
            # Draw progress
            progress_amount = int((self.progress / self.required_progress) * progress_width)
            pygame.draw.rect(screen, (0, 255, 0), (progress_x, progress_y, progress_amount, progress_height))
            
            # Draw border
            pygame.draw.rect(screen, (255, 255, 255), (progress_x, progress_y, progress_width, progress_height), 2)
            
            # Draw timer if applicable
            if self.max_time > 0 and self.timer > 0:
                timer_text = f"Time: {self.timer // 60}:{self.timer % 60:02d}"
                timer_surface = font.render(timer_text, True, (255, 255, 255))
                screen.blit(timer_surface, (progress_x + progress_width + 10, progress_y))
    
    def complete(self):
        """Mark activity as completed"""
        self.active = False
        self.completed = True
        self.message = f"Completed: {self.name}! Reward: ${self.reward}"
        self.message_timer = 180
        
        # Add reward to player's money if the game supports it
        if hasattr(self.game.player, 'money'):
            self.game.player.money += self.reward
    
    def fail(self, reason="Activity failed"):
        """Mark activity as failed"""
        self.active = False
        self.failed = False  # Reset fail state to allow retrying
        self.message = f"Failed: {reason}"
        self.message_timer = 180

class IllegalTaxi(SideActivity):
    """Illegal taxi service activity - steal a car and pick up shady fares"""
    def __init__(self, game):
        super().__init__(
            game,
            "illegal_taxi",
            "Illegal Taxi Hustle",
            "Steal a car and pick up shady fares avoiding police checkpoints"
        )
        self.max_time = 3600  # 60 seconds at 60 fps
        self.reward = 250
        self.passenger = None
        self.has_passenger = False
        self.destination = None
        self.fare_count = 0
        self.required_fares = 3
        
        # Set trigger points at road intersections
        for x in range(400, game.map.width, 800):
            for y in range(400, game.map.height, 800):
                self.trigger_points.append((x, y, 150))
    
    def trigger(self):
        super().trigger()
        
        # Check if player is in a vehicle
        if not self.game.player.in_vehicle:
            self.message = "You need a car first, buddy! Steal one to start!"
            self.active = False
            return
            
        self.generate_passenger()
        
    def generate_passenger(self):
        """Generate a random passenger waiting for pickup"""
        # Find a random road position away from player
        road_pos = None
        while road_pos is None:
            candidate_road = random.choice(self.game.map.roads)
            rect = candidate_road["rect"]
            road_x = rect.x + random.randint(0, rect.width)
            road_y = rect.y + random.randint(0, rect.height)
            
            # Make sure it's not too close to player
            dx = road_x - self.game.player.x
            dy = road_y - self.game.player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 500 and distance < 1200:
                road_pos = (road_x, road_y)
        
        self.passenger = road_pos
        self.has_passenger = False
        self.target_markers = [(road_pos[0], road_pos[1], "pickup")]
        self.message = "Pick up the shady passenger, eh!"
        
        # Create destination but don't reveal it yet
        self.generate_destination()
        
    def generate_destination(self):
        """Generate a random destination for the current passenger"""
        # Find a different road position from passenger for dropoff
        road_pos = None
        if self.passenger:
            while road_pos is None:
                candidate_road = random.choice(self.game.map.roads)
                rect = candidate_road["rect"]
                road_x = rect.x + random.randint(0, rect.width)
                road_y = rect.y + random.randint(0, rect.height)
                
                # Make sure it's far enough from pickup point
                dx = road_x - self.passenger[0]
                dy = road_y - self.passenger[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 800:
                    road_pos = (road_x, road_y)
        
        self.destination = road_pos
    
    def update(self, player, walls, vehicles, pedestrians):
        super().update(player, walls, vehicles, pedestrians)
        
        if not self.active:
            return
        
        # If player was in a vehicle but got out, fail the mission
        if not player.in_vehicle:
            self.fail("You left your taxi, eh! The passenger is stranded!")
            return
            
        # If passenger is set and we don't have them yet, check if we're close enough to pick up
        if self.passenger and not self.has_passenger:
            dx = player.x - self.passenger[0]
            dy = player.y - self.passenger[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 50:
                self.has_passenger = True
                self.message = "Take your passenger to the marked destination, buddy!"
                self.target_markers = [(self.destination[0], self.destination[1], "dropoff")]
        
        # If we have a passenger and destination, check if we're at the destination
        elif self.has_passenger and self.destination:
            dx = player.x - self.destination[0]
            dy = player.y - self.destination[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 50:
                self.fare_count += 1
                self.progress = (self.fare_count / self.required_fares) * 100
                
                if self.fare_count >= self.required_fares:
                    self.complete()
                else:
                    # Generate the next fare
                    self.message = f"Fare complete! {self.fare_count}/{self.required_fares}"
                    self.message_timer = 120
                    self.generate_passenger()

class GarbageTruckRace(SideActivity):
    """Race in a stolen garbage truck through narrow alleys"""
    def __init__(self, game):
        super().__init__(
            game,
            "garbage_race",
            "Garbage Truck Race",
            "Race against the clock in a garbage truck through narrow alleys"
        )
        self.max_time = 5400  # 90 seconds at 60 fps
        self.reward = 350
        self.checkpoints = []
        self.current_checkpoint = 0
        self.truck_color = (120, 140, 80)  # Garbage truck color
        
        # Set trigger points in industrial areas
        for x in range(600, game.map.width, 1000):
            for y in range(600, game.map.height, 1000):
                self.trigger_points.append((x, y, 150))
    
    def trigger(self):
        super().trigger()
        self.timer = self.max_time
        
        # Set up race checkpoints
        self.generate_checkpoints()
        self.current_checkpoint = 0
        self.update_checkpoint_markers()
        
        # Check if player is in a vehicle
        if self.game.player.in_vehicle:
            # Override vehicle color to garbage truck color
            self.game.player.in_vehicle.color = self.truck_color
            self.message = "Hit all the checkpoints before time runs out, buddy!"
        else:
            # Spawn a "garbage truck" (reskinned vehicle) nearby
            self.spawn_garbage_truck()
            self.message = "Get in the garbage truck to start the race, guy!"
            self.timer = 0  # Pause timer until they get in
            
    def spawn_garbage_truck(self):
        """Spawn a garbage truck near the player"""
        # Find a clear spot near the player
        clear_spot = False
        truck_x, truck_y = self.game.player.x, self.game.player.y
        
        for _ in range(10):  # Try 10 times to find a clear spot
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(100, 200)
            test_x = self.game.player.x + math.cos(angle) * dist
            test_y = self.game.player.y + math.sin(angle) * dist
            
            # Check if spot is clear (no collisions with walls)
            collides = False
            test_rect = pygame.Rect(test_x - 20, test_y - 20, 40, 40)
            
            for wall in self.game.map.walls:
                if test_rect.colliderect(wall["rect"]):
                    collides = True
                    break
            
            if not collides:
                truck_x, truck_y = test_x, test_y
                clear_spot = True
                break
        
        # Create "garbage truck" - special vehicle with unique appearance
        truck = self.game.Vehicle(truck_x, truck_y)
        truck.color = self.truck_color
        truck.size = 30  # Slightly larger
        truck.speed_multiplier = 0.8  # Slower but more powerful
        truck.label = "Garbage Truck"
        
        self.game.map.vehicles.append(truck)
    
    def generate_checkpoints(self):
        """Generate a series of checkpoints for the race"""
        self.checkpoints = []
        
        # Start with player position
        last_x, last_y = self.game.player.x, self.game.player.y
        
        # Generate 10 checkpoints, each progressively further from the start
        for i in range(10):
            # Get a random road segment that's a certain distance from last checkpoint
            found = False
            attempts = 0
            min_dist = 200 + i * 50  # Progressively further
            max_dist = 400 + i * 50
            
            while not found and attempts < 50:
                road = random.choice(self.game.map.roads)
                rect = road["rect"]
                cp_x = rect.x + random.randint(0, rect.width)
                cp_y = rect.y + random.randint(0, rect.height)
                
                dx = cp_x - last_x
                dy = cp_y - last_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Check if appropriate distance
                if min_dist < dist < max_dist:
                    # Ensure it doesn't collide with walls
                    collides = False
                    check_rect = pygame.Rect(cp_x - 30, cp_y - 30, 60, 60)
                    
                    for wall in self.game.map.walls:
                        if check_rect.colliderect(wall["rect"]):
                            collides = True
                            break
                    
                    if not collides:
                        self.checkpoints.append((cp_x, cp_y))
                        last_x, last_y = cp_x, cp_y
                        found = True
                
                attempts += 1
            
            # If we couldn't find a good checkpoint, just place one
            if not found:
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(min_dist, max_dist)
                cp_x = last_x + math.cos(angle) * dist
                cp_y = last_y + math.sin(angle) * dist
                
                self.checkpoints.append((cp_x, cp_y))
                last_x, last_y = cp_x, cp_y
    
    def update_checkpoint_markers(self):
        """Update target markers to show current checkpoint"""
        if self.current_checkpoint < len(self.checkpoints):
            cp = self.checkpoints[self.current_checkpoint]
            self.target_markers = [(cp[0], cp[1], "checkpoint")]
    
    def update(self, player, walls, vehicles, pedestrians):
        super().update(player, walls, vehicles, pedestrians)
        
        if not self.active:
            return
        
        # If timer was paused because player needed to get in the truck
        if self.timer == 0 and not player.in_vehicle:
            return
        elif self.timer == 0 and player.in_vehicle:
            # Player just got in the truck, start the timer
            self.timer = self.max_time
            self.message = "Race started! Hit all checkpoints before time runs out, guy!"
            
        # If player was in a vehicle but got out, fail the mission
        if not player.in_vehicle:
            self.fail("You left your garbage truck, eh! Race over!")
            return
            
        # Check if player hit the current checkpoint
        if self.current_checkpoint < len(self.checkpoints):
            cp_x, cp_y = self.checkpoints[self.current_checkpoint]
            dx = player.x - cp_x
            dy = player.y - cp_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 50:
                self.current_checkpoint += 1
                self.progress = (self.current_checkpoint / len(self.checkpoints)) * 100
                
                if self.current_checkpoint < len(self.checkpoints):
                    self.message = f"Checkpoint {self.current_checkpoint}/{len(self.checkpoints)} hit!"
                    self.message_timer = 120
                    self.update_checkpoint_markers()
                else:
                    self.complete()

class ParkingLotFightClub(SideActivity):
    """Enter underground fight club in parking lots"""
    def __init__(self, game):
        super().__init__(
            game,
            "fight_club",
            "Parking Lot Fight Club",
            "Compete in dirty fist fights behind gas stations for cash"
        )
        self.max_time = 3600  # 60 seconds at 60 fps
        self.reward = 400
        self.arena_center = None
        self.arena_radius = 100
        self.opponents = []
        self.current_opponent = None
        self.fight_stage = 0  # 0: approaching, 1: fighting, 2: finished round
        self.rounds_won = 0
        self.required_rounds = 3
        
        # Set trigger points in various locations
        for x in range(500, game.map.width, 900):
            for y in range(500, game.map.height, 900):
                # Try to place it near buildings
                found_building = False
                for building in game.map.buildings:
                    bx = building["rect"].centerx
                    by = building["rect"].centery
                    
                    if math.sqrt((x - bx)**2 + (y - by)**2) < 300:
                        found_building = True
                        break
                
                if found_building:
                    self.trigger_points.append((x, y, 150))
    
    def trigger(self):
        super().trigger()
        
        # If player is in a vehicle, they need to exit
        if self.game.player.in_vehicle:
            self.message = "You can't fight from a car, buddy! Get out first!"
            self.active = False
            return
            
        # Set up the arena
        self.arena_center = (self.game.player.x, self.game.player.y)
        self.arena_radius = 100
        
        # Generate opponents
        self.generate_opponents()
        self.fight_stage = 0
        self.rounds_won = 0
        
        self.message = "Welcome to Fight Club, guy! First rule: Don't tell anyone aboot it!"
    
    def generate_opponents(self):
        """Generate a series of progressively tougher opponents"""
        self.opponents = []
        
        for i in range(self.required_rounds):
            # Create opponent with increasing health and damage
            health = 2 + i  # 2, 3, 4 health
            damage = 1 + i * 0.5  # 1, 1.5, 2 damage
            
            opponent = {
                "health": health,
                "max_health": health,
                "damage": damage,
                "x": 0,
                "y": 0,
                "timer": 0,
                "knockback": 0,
                "direction": "down",
                "colors": {
                    'skin': random.choice([
                        (255, 223, 196),  # Light skin
                        (240, 200, 170),  # Medium skin
                        (190, 140, 110),  # Darker skin
                    ]),
                    'shirt': random.choice([
                        (200, 0, 0),      # Red
                        (0, 100, 200),    # Blue
                        (0, 150, 0),      # Green
                        (150, 0, 150),    # Purple
                    ]),
                    'pants': random.choice([
                        (0, 0, 150),      # Blue jeans
                        (40, 40, 40),     # Black pants
                    ]),
                    'shoes': (40, 40, 40),  # Dark shoes
                    'eyes': (0, 0, 0)       # Black eyes
                }
            }
            
            self.opponents.append(opponent)
    
    def spawn_next_opponent(self):
        """Spawn the next opponent in the arena"""
        if self.rounds_won < len(self.opponents):
            opponent = self.opponents[self.rounds_won]
            
            # Set position opposite of player, relative to arena center
            dx = self.game.player.x - self.arena_center[0]
            dy = self.game.player.y - self.arena_center[1]
            
            # Ensure minimum distance
            dist = max(math.sqrt(dx*dx + dy*dy), 10)
            
            # Normalize and invert direction, then multiply by arena radius * 0.7
            opponent["x"] = self.arena_center[0] - dx/dist * self.arena_radius * 0.7
            opponent["y"] = self.arena_center[1] - dy/dist * self.arena_radius * 0.7
            
            # Set direction facing player
            angle = math.atan2(self.game.player.y - opponent["y"], 
                              self.game.player.x - opponent["x"])
            
            if -math.pi/4 <= angle < math.pi/4:
                opponent["direction"] = "right"
            elif math.pi/4 <= angle < 3*math.pi/4:
                opponent["direction"] = "down"
            elif -3*math.pi/4 <= angle < -math.pi/4:
                opponent["direction"] = "up"
            else:
                opponent["direction"] = "left"
            
            self.current_opponent = opponent
            self.fight_stage = 1
            self.message = f"Round {self.rounds_won + 1}: FIGHT!"
            self.message_timer = 120
            
    def update(self, player, walls, vehicles, pedestrians):
        super().update(player, walls, vehicles, pedestrians)
        
        if not self.active:
            return
        
        # If player is in a vehicle, fail the mission
        if self.game.player.in_vehicle:
            self.fail("You got in a vehicle! Fight club is over, guy!")
            return
            
        # Check if player is too far from the arena
        dx = player.x - self.arena_center[0]
        dy = player.y - self.arena_center[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.arena_radius * 1.5:
            self.fail("You left the arena! Get back here, friend!")
            return
            
        # Handle the different fight stages
        if self.fight_stage == 0:
            # Starting - spawn first opponent
            self.spawn_next_opponent()
            
        elif self.fight_stage == 1 and self.current_opponent:
            # Active fight
            opponent = self.current_opponent
            
            # If opponent has a knockback timer, apply it
            if opponent["knockback"] > 0:
                opponent["knockback"] -= 1
            else:
                # Update opponent AI
                
                # Move toward player
                dx = player.x - opponent["x"]
                dy = player.y - opponent["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Only move if not too close
                if dist > 30:
                    speed = 1
                    opponent["x"] += dx/dist * speed
                    opponent["y"] += dy/dist * speed
                    
                    # Update direction
                    angle = math.atan2(dy, dx)
                    if -math.pi/4 <= angle < math.pi/4:
                        opponent["direction"] = "right"
                    elif math.pi/4 <= angle < 3*math.pi/4:
                        opponent["direction"] = "down"
                    elif -3*math.pi/4 <= angle < -math.pi/4:
                        opponent["direction"] = "up"
                    else:
                        opponent["direction"] = "left"
                
                # Attack if close and timer is up
                if dist < 40 and opponent["timer"] <= 0:
                    # Deal damage to player
                    if hasattr(player, 'health'):
                        player.health -= opponent["damage"]
                    
                    # Set cooldown
                    opponent["timer"] = 30
                    
                    # Apply knockback to player
                    knockback_dist = 10
                    if dx != 0 or dy != 0:
                        player.x += dx/dist * knockback_dist
                        player.y += dy/dist * knockback_dist
                
            # Decrease opponent's attack timer
            if opponent["timer"] > 0:
                opponent["timer"] -= 1
                
            # Check if player is attacking (shooting)
            if player.shooting and not hasattr(player, 'shoot_cooldown') or player.shoot_cooldown <= 0:
                # Check if player is facing opponent
                player_dir = player.direction
                hit = False
                
                if player_dir == "right" and opponent["x"] > player.x:
                    hit = True
                elif player_dir == "left" and opponent["x"] < player.x:
                    hit = True
                elif player_dir == "up" and opponent["y"] < player.y:
                    hit = True
                elif player_dir == "down" and opponent["y"] > player.y:
                    hit = True
                
                # Distance check
                if hit and dist < 50:
                    # Deal damage to opponent
                    opponent["health"] -= 1
                    
                    # Knockback opponent
                    knockback_dist = 20
                    if dx != 0 or dy != 0:
                        opponent["x"] += dx/dist * knockback_dist
                        opponent["y"] += dy/dist * knockback_dist
                        opponent["knockback"] = 10
                    
                    # Check if opponent is defeated
                    if opponent["health"] <= 0:
                        self.fight_stage = 2
                        self.rounds_won += 1
                        self.progress = (self.rounds_won / self.required_rounds) * 100
                        
                        if self.rounds_won >= self.required_rounds:
                            self.complete()
                        else:
                            self.message = f"Opponent defeated! Round {self.rounds_won}/{self.required_rounds} complete!"
                            self.message_timer = 120
                            # Give a breather before next opponent
                            self.timer = 180
                            self.fight_stage = 0
        
    def draw(self, screen, camera_x, camera_y, font):
        super().draw(screen, camera_x, camera_y, font)
        
        if not self.active:
            return
            
        # Draw arena circle
        if self.arena_center:
            arena_x = self.arena_center[0] - camera_x
            arena_y = self.arena_center[1] - camera_y
            pygame.draw.circle(screen, (150, 150, 150), (int(arena_x), int(arena_y)), 
                             self.arena_radius, 2)
            
        # Draw current opponent
        if self.current_opponent and self.fight_stage == 1:
            opponent = self.current_opponent
            opp_x = opponent["x"] - camera_x
            opp_y = opponent["y"] - camera_y
            
            # Only draw if on screen
            if (0 <= opp_x < screen.get_width() and 
                0 <= opp_y < screen.get_height()):
                
                # Draw a simple representation of opponent
                size = 16
                
                # Use character_sprites if available
                if hasattr(self.game, 'draw_canadian_character'):
                    self.game.draw_canadian_character(
                        screen, opp_x, opp_y, size, opponent["colors"], 
                        0, True, opponent["direction"]
                    )
                else:
                    # Fallback - draw simple colored rectangle
                    pygame.draw.rect(
                        screen, opponent["colors"]["shirt"], 
                        (opp_x-size/2, opp_y-size/2, size, size)
                    )
                
                # Draw health bar
                health_width = 30
                health_height = 5
                health_x = opp_x - health_width/2
                health_y = opp_y - size/2 - 10
                
                # Draw background
                pygame.draw.rect(screen, (50, 50, 50), 
                               (health_x, health_y, health_width, health_height))
                
                # Draw health amount
                health_amount = int((opponent["health"] / opponent["max_health"]) * health_width)
                pygame.draw.rect(screen, (255, 0, 0), 
                               (health_x, health_y, health_amount, health_height))
                
                # Draw border
                pygame.draw.rect(screen, (255, 255, 255), 
                               (health_x, health_y, health_width, health_height), 1)