"""
Cheat code system for GTA-style South Park Canadian game
This module implements hidden cheat codes that can be discovered through NPC dialogues
and are activated through specific sequences of actions.
"""
import random
import math
import pygame

class CheatSystem:
    """Manages cheat codes and their activation"""
    def __init__(self, game):
        self.game = game
        self.cheats = []
        self.input_sequence = []
        self.sequence_timer = 0
        self.max_sequence_time = 120  # 2 seconds at 60 fps
        self.last_activated_cheat = None
        self.active_cheats = {}  # cheat_name: time_remaining
        self.cheat_messages = []  # messages to display
        
        # Initialize available cheats
        self.initialize_cheats()
    
    def initialize_cheats(self):
        """Set up available cheat codes"""
        # Speed boost cheat (pigeon punching reference)
        self.cheats.append({
            "name": "Infinite Punch Speed",
            "code": ["up", "up", "down", "down", "space"],
            "description": "Punch super fast, eh!",
            "dialogue_hint": "You ever try punching a pigeon while wearing two hats? Word is, weird stuff happens.",
            "effect": "punch_speed",
            "duration": 1800,  # 30 seconds at 60 fps
            "discovered": False
        })
        
        # Rocket launcher cheat (butter tacos reference)
        self.cheats.append({
            "name": "Rocket Launcher",
            "code": ["up", "down", "left", "right", "space"],
            "description": "Spawn a rocket launcher, buddy!",
            "dialogue_hint": "My cousin swears shouting 'Butter Tacos!' at the old library gives you... *powers.*",
            "effect": "rocket_launcher",
            "duration": 1200,  # 20 seconds at 60 fps
            "discovered": False
        })
        
        # Invincibility cheat (donut park reference)
        self.cheats.append({
            "name": "Invincibility",
            "code": ["left", "right", "left", "right", "space"],
            "description": "Become invincible, friend!",
            "dialogue_hint": "Only real criminals know you gotta spin in place three times at Donut Park.",
            "effect": "invincibility",
            "duration": 900,  # 15 seconds at 60 fps
            "discovered": False
        })
        
        # Car boost cheat
        self.cheats.append({
            "name": "Turbo Boost",
            "code": ["up", "up", "down", "down", "left", "right"],
            "description": "Super fast vehicles, guy!",
            "dialogue_hint": "I heard if you honk four times then stomp the pedal, your car goes faster than the mounties!",
            "effect": "car_boost",
            "duration": 1500,  # 25 seconds at 60 fps
            "discovered": False
        })
        
        # Pedestrian panic cheat
        self.cheats.append({
            "name": "Pedestrian Panic",
            "code": ["down", "down", "down", "left", "right"],
            "description": "Everyone runs around in panic, buddy!",
            "dialogue_hint": "Some guy told me if you yell 'Free healthcare!' downtown, all the Americans panic and run away.",
            "effect": "panic_mode",
            "duration": 1200,  # 20 seconds at 60 fps
            "discovered": False
        })
        
        # Money cheat
        self.cheats.append({
            "name": "Money Shower",
            "code": ["left", "right", "up", "down", "up", "space"],
            "description": "Make it rain money, friend!",
            "dialogue_hint": "My uncle works at the bank and says if you type your PIN backwards at the ATM, money falls from the sky.",
            "effect": "money_boost",
            "duration": 300,  # 5 seconds at 60 fps
            "discovered": False
        })
        
        # Police removal
        self.cheats.append({
            "name": "No Mounties",
            "code": ["down", "down", "left", "left", "right", "right"],
            "description": "Make the police disappear, eh!",
            "dialogue_hint": "There's a trick where if you apologize to a Mountie five times in a row, all the police go on break.",
            "effect": "no_police",
            "duration": 1800,  # 30 seconds at 60 fps
            "discovered": False
        })
        
        # Big head mode
        self.cheats.append({
            "name": "Canadian Big Head Mode",
            "code": ["up", "up", "up", "down", "down", "down"],
            "description": "Extra floppy Canadian heads, buddy!",
            "dialogue_hint": "I saw a guy at the hockey game whose head got really big when he did the wave three times.",
            "effect": "big_head",
            "duration": 2400,  # 40 seconds at 60 fps
            "discovered": False
        })
    
    def process_input(self, key):
        """Process a key press and check for cheat code matches"""
        # Reset sequence if timer expired
        if self.sequence_timer <= 0:
            self.input_sequence = []
        
        # Add key to sequence and reset timer
        self.input_sequence.append(key)
        self.sequence_timer = self.max_sequence_time
        
        # Limit sequence length
        if len(self.input_sequence) > 10:
            self.input_sequence = self.input_sequence[-10:]
            
        # Check for matches
        for cheat in self.cheats:
            # Skip if code is longer than current sequence
            if len(cheat["code"]) > len(self.input_sequence):
                continue
                
            # Check if end of sequence matches the cheat code
            seq_slice = self.input_sequence[-len(cheat["code"]):]
            if seq_slice == cheat["code"]:
                self.activate_cheat(cheat)
                self.input_sequence = []  # Reset after successful activation
                return
    
    def activate_cheat(self, cheat):
        """Activate a cheat code's effect"""
        # Mark as discovered
        cheat["discovered"] = True
        
        # Set as active with duration
        self.active_cheats[cheat["effect"]] = cheat["duration"]
        
        # Store last activated cheat
        self.last_activated_cheat = cheat
        
        # Add message
        message = f"Cheat Activated: {cheat['name']} - {cheat['description']}"
        self.cheat_messages.append({
            "text": message,
            "timer": 180  # Show for 3 seconds
        })
        
        # Apply immediate effects
        self.apply_cheat_effect(cheat)
    
    def apply_cheat_effect(self, cheat):
        """Apply the specific effect of a cheat code"""
        effect = cheat["effect"]
        
        if effect == "punch_speed":
            # Increase player attack speed dramatically
            if hasattr(self.game.player, 'shoot_cooldown'):
                # Store original value if we haven't already
                if not hasattr(self, '_original_shoot_cooldown'):
                    self._original_shoot_cooldown = self.game.player.shoot_cooldown
                
                # Set to very low cooldown
                self.game.player.shoot_cooldown = 5
                
        elif effect == "rocket_launcher":
            # Give player rocket launcher capabilities
            if hasattr(self.game.player, 'bullets'):
                # Store original values
                if not hasattr(self, '_original_bullet_speed'):
                    self._original_bullet_speed = self.game.player.bullet_speed
                
                # Make bullets act like rockets (faster, bigger)
                self.game.player.bullet_speed = 15
                # Additional properties will be handled in update_effects
                
        elif effect == "invincibility":
            # Make player invincible
            # Will be handled in update_effects
            pass
            
        elif effect == "car_boost":
            # Boost car speed
            if hasattr(self.game.player, 'in_vehicle') and self.game.player.in_vehicle:
                if not hasattr(self, '_original_vehicle_speed'):
                    self._original_vehicle_speed = self.game.player.in_vehicle.speed
                
                # Double vehicle speed
                self.game.player.in_vehicle.speed *= 2
            
        elif effect == "panic_mode":
            # Make all pedestrians panic and run
            for ped in self.game.map.pedestrians:
                if hasattr(ped, 'ai_state'):
                    ped.ai_state = "flee"
                    ped.flee_target = self.game.player
                    
        elif effect == "money_boost":
            # Add money if the player has a money attribute
            if hasattr(self.game.player, 'money'):
                self.game.player.money += 500
            else:
                # Add money attribute if it doesn't exist
                self.game.player.money = 500
                
        elif effect == "no_police":
            # Remove police temporarily
            # Store current police to restore later
            if not hasattr(self, '_stored_police'):
                self._stored_police = self.game.map.police_vehicles.copy()
                self.game.map.police_vehicles = []
                
        elif effect == "big_head":
            # Big head mode - affect character rendering scale
            # Set a flag that will be used during rendering
            self.game.big_head_mode = True
    
    def update(self):
        """Update cheat system state"""
        # Update sequence timer
        if self.sequence_timer > 0:
            self.sequence_timer -= 1
            
        # Update active cheats
        to_remove = []
        for effect, duration in self.active_cheats.items():
            self.active_cheats[effect] = duration - 1
            if duration <= 0:
                to_remove.append(effect)
                
        # Remove expired cheats
        for effect in to_remove:
            self.deactivate_cheat(effect)
            
        # Update cheat messages
        messages_to_remove = []
        for i, message in enumerate(self.cheat_messages):
            message["timer"] -= 1
            if message["timer"] <= 0:
                messages_to_remove.append(i)
                
        # Remove expired messages
        for i in sorted(messages_to_remove, reverse=True):
            del self.cheat_messages[i]
            
        # Update special effects
        self.update_effects()
    
    def update_effects(self):
        """Update any ongoing cheat effects"""
        # Rocket launcher effect - modify bullets to be rockets
        if "rocket_launcher" in self.active_cheats and hasattr(self.game.player, 'bullets'):
            # Make bullets explode on impact
            for bullet in self.game.player.bullets:
                # Check if not already a rocket
                if not bullet.get("is_rocket", False):
                    bullet["is_rocket"] = True
                    bullet["size"] = 8  # Bigger bullet
                    bullet["color"] = (255, 100, 0)  # Orange color
                    bullet["damage"] = 3  # More damage
                    
                # Handle explosion for rockets that hit something
                if bullet.get("hit", False) and not bullet.get("exploded", False):
                    bullet["exploded"] = True
                    # Add explosion effect
                    if hasattr(self.game, 'add_explosion'):
                        self.game.add_explosion(bullet["x"], bullet["y"], 100)
                    
                    # Damage everything nearby
                    radius = 100
                    # Check vehicles
                    for vehicle in self.game.map.vehicles + self.game.map.police_vehicles:
                        dx = vehicle.x - bullet["x"]
                        dy = vehicle.y - bullet["y"]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < radius:
                            # Apply damage and knockback
                            if hasattr(vehicle, 'damage'):
                                vehicle.damage(3)
                            
                    # Check pedestrians
                    for ped in self.game.map.pedestrians:
                        dx = ped.x - bullet["x"]
                        dy = ped.y - bullet["y"]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < radius:
                            # Make pedestrian flee
                            ped.ai_state = "flee"
                            ped.flee_target = self.game.player
                            # Damage pedestrian
                            if hasattr(ped, 'health'):
                                ped.health -= 1
        
        # Invincibility effect
        if "invincibility" in self.active_cheats:
            # Store original health if we haven't already
            if hasattr(self.game.player, 'health') and not hasattr(self, '_original_health'):
                self._original_health = self.game.player.health
                
            # Ensure player health stays at maximum
            if hasattr(self.game.player, 'health'):
                self.game.player.health = 1000
    
    def draw(self, screen, font):
        """Draw cheat-related UI elements"""
        # Draw active cheat messages
        y_offset = 100
        for message in self.cheat_messages:
            text = message["text"]
            text_surface = font.render(text, True, (255, 255, 0))
            screen.blit(text_surface, (20, y_offset))
            y_offset += 30
        
        # Draw active cheat status in corner
        if self.active_cheats:
            y_offset = 10
            screen.blit(font.render("Active Cheats:", True, (255, 255, 0)), (10, y_offset))
            y_offset += 20
            
            for effect, time_left in self.active_cheats.items():
                # Find cheat name from effect
                cheat_name = effect
                for cheat in self.cheats:
                    if cheat["effect"] == effect:
                        cheat_name = cheat["name"]
                        break
                
                # Convert frames to seconds
                seconds_left = int(time_left / 60)
                text = f"{cheat_name}: {seconds_left}s"
                text_surface = font.render(text, True, (200, 200, 50))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 20
        
        # Draw input sequence for debug purposes (if enabled)
        if hasattr(self.game, 'show_debug') and self.game.show_debug and self.input_sequence:
            seq_text = "Input: " + " ".join(self.input_sequence)
            seq_surface = font.render(seq_text, True, (200, 200, 200))
            screen.blit(seq_surface, (10, screen.get_height() - 30))
    
    def deactivate_cheat(self, effect):
        """Deactivate a cheat effect and restore original settings"""
        if effect == "punch_speed":
            # Restore original attack speed
            if hasattr(self, '_original_shoot_cooldown'):
                self.game.player.shoot_cooldown = self._original_shoot_cooldown
                delattr(self, '_original_shoot_cooldown')
                
        elif effect == "rocket_launcher":
            # Restore original bullet properties
            if hasattr(self, '_original_bullet_speed'):
                self.game.player.bullet_speed = self._original_bullet_speed
                delattr(self, '_original_bullet_speed')
                
        elif effect == "invincibility":
            # Restore original health
            if hasattr(self, '_original_health'):
                self.game.player.health = self._original_health
                delattr(self, '_original_health')
                
        elif effect == "car_boost":
            # Restore original vehicle speed
            if hasattr(self, '_original_vehicle_speed') and self.game.player.in_vehicle:
                self.game.player.in_vehicle.speed = self._original_vehicle_speed
                delattr(self, '_original_vehicle_speed')
                
        elif effect == "no_police":
            # Restore police
            if hasattr(self, '_stored_police'):
                self.game.map.police_vehicles = self._stored_police
                delattr(self, '_stored_police')
                
        elif effect == "big_head":
            # Turn off big head mode
            self.game.big_head_mode = False
            
        # Remove from active cheats
        if effect in self.active_cheats:
            del self.active_cheats[effect]
            
        # Add expiration message
        for cheat in self.cheats:
            if cheat["effect"] == effect:
                message = f"Cheat Expired: {cheat['name']}"
                self.cheat_messages.append({
                    "text": message,
                    "timer": 120  # Show for 2 seconds
                })
                break
    

            
    def get_random_dialogue_hint(self):
        """Return a random dialogue hint for an undiscovered cheat"""
        # Get all undiscovered cheats
        undiscovered = [cheat for cheat in self.cheats if not cheat["discovered"]]
        
        # If all cheats discovered, return None
        if not undiscovered:
            return None
            
        # Return a random hint
        cheat = random.choice(undiscovered)
        return cheat["dialogue_hint"]

# NPC dialogue system for revealing cheat hints
class DialogueSystem:
    """Manages NPC dialogue including cheat hints"""
    def __init__(self, game, cheat_system):
        self.game = game
        self.cheat_system = cheat_system
        self.active = False
        self.current_npc = None
        self.dialogue_lines = []
        self.current_line = 0
        self.dialogue_timer = 0
        self.dialogue_speed = 2  # characters per frame
        self.revealed_text = ""
        self.dialogue_font = None
        self.dialogue_box_rect = None
        
        # Create dialogue prompts
        self.generic_dialogue = [
            "Hey there, buddy!",
            "How's it going, friend?",
            "Nice day, eh?",
            "Watch where you're going, guy!",
            "You're not from around here, are you?",
            "The Mounties are out in force today.",
            "I heard there's trouble downtown.",
            "Did you see the hockey game last night?",
            "Sorry about that!",
            "Excuse me, just passing through.",
            "What's the hurry, eh?",
            "You look like you're up to no good.",
            "I'm not your friend, buddy!",
            "I'm not your buddy, guy!",
            "I'm not your guy, friend!",
            "Free healthcare is the best, eh?",
        ]
    
    def setup_font(self, size=24):
        """Initialize the font for dialogue"""
        if pygame.font.get_init():
            self.dialogue_font = pygame.font.SysFont('Arial', size)
    
    def start_dialogue(self, npc):
        """Start a dialogue with an NPC"""
        if self.dialogue_font is None:
            self.setup_font()
            
        self.active = True
        self.current_npc = npc
        self.dialogue_lines = []
        self.current_line = 0
        self.revealed_text = ""
        self.dialogue_timer = 0
        
        # Generate dialogue
        self.generate_dialogue(npc)
    
    def generate_dialogue(self, npc):
        """Generate dialogue lines for an NPC interaction"""
        # First line is always a generic greeting
        self.dialogue_lines.append(random.choice(self.generic_dialogue))
        
        # Decide if we should give a cheat hint (30% chance if NPC is not fleeing)
        if npc.ai_state != "flee" and random.random() < 0.3:
            hint = self.cheat_system.get_random_dialogue_hint()
            if hint:
                self.dialogue_lines.append(hint)
        
        # Add a closing line
        closing_lines = [
            "Anyway, I should get going.",
            "Well, see you around, eh?",
            "I'm late for the hockey game.",
            "I need to get more maple syrup.",
            "Time to get back to work.",
            "Watch out for the Mounties!",
            "Stay out of trouble, buddy!",
        ]
        self.dialogue_lines.append(random.choice(closing_lines))
    
    def update(self):
        """Update the dialogue state"""
        if not self.active:
            return
            
        # Check if NPC is still valid
        if self.current_npc is None or getattr(self.current_npc, 'is_dead', False):
            self.active = False
            return
            
        # Update the text reveal animation
        if self.current_line < len(self.dialogue_lines):
            full_text = self.dialogue_lines[self.current_line]
            if len(self.revealed_text) < len(full_text):
                # Add character by character
                self.dialogue_timer += 1
                if self.dialogue_timer >= self.dialogue_speed:
                    self.dialogue_timer = 0
                    self.revealed_text = full_text[:len(self.revealed_text) + 1]
        
    def advance_dialogue(self):
        """Move to the next line of dialogue"""
        if not self.active:
            return
            
        # If text is still revealing, show it all instantly
        current_text = self.dialogue_lines[self.current_line]
        if len(self.revealed_text) < len(current_text):
            self.revealed_text = current_text
            return
            
        # Move to next line
        self.current_line += 1
        self.revealed_text = ""
        
        # End dialogue if no more lines
        if self.current_line >= len(self.dialogue_lines):
            self.active = False
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the dialogue UI"""
        if not self.active or self.dialogue_font is None:
            return
            
        # Draw dialogue box
        box_width = min(screen.get_width() - 60, 800)
        box_height = 100
        box_x = screen.get_width() // 2 - box_width // 2
        box_y = screen.get_height() - box_height - 20
        
        # Store box rect for reference
        self.dialogue_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Draw semi-transparent background
        s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))  # Black with alpha
        screen.blit(s, (box_x, box_y))
        
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)
        
        # Draw NPC name or label
        npc_name = getattr(self.current_npc, 'name', 'Canadian')
        name_surface = self.dialogue_font.render(npc_name, True, (255, 255, 0))
        screen.blit(name_surface, (box_x + 10, box_y - name_surface.get_height() - 5))
        
        # Draw current text being revealed
        if self.current_line < len(self.dialogue_lines):
            # Calculate text positioning (with word wrap)
            max_width = box_width - 20
            text = self.revealed_text
            words = text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                text_width = self.dialogue_font.size(test_line)[0]
                
                if text_width < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            
            lines.append(current_line)
            
            # Draw each line
            line_height = self.dialogue_font.get_height()
            for i, line in enumerate(lines):
                text_surface = self.dialogue_font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (box_x + 10, box_y + 10 + i * line_height))
                
            # Draw continue indicator
            if len(self.revealed_text) == len(self.dialogue_lines[self.current_line]):
                indicator_text = "Press E to continue"
                indicator_surface = pygame.font.SysFont('Arial', 18).render(indicator_text, True, (200, 200, 200))
                screen.blit(indicator_surface, (box_x + box_width - indicator_surface.get_width() - 10, 
                                              box_y + box_height - indicator_surface.get_height() - 10))
                
        # Draw NPC portrait (if we have one)
        if hasattr(self.current_npc, 'draw_portrait'):
            self.current_npc.draw_portrait(screen, box_x + 20, box_y + box_height // 2)
        else:
            # Draw a colored circle as fallback
            portrait_color = getattr(self.current_npc, 'colors', {}).get('shirt', (200, 0, 0))
            pygame.draw.circle(screen, portrait_color, (box_x + 30, box_y + 30), 20)
            
        # Draw arrow pointing to NPC
        if self.current_npc:
            npc_screen_x = self.current_npc.x - camera_x
            npc_screen_y = self.current_npc.y - camera_y
            
            # Only draw if on screen
            if (0 <= npc_screen_x < screen.get_width() and 
                0 <= npc_screen_y < screen.get_height()):
                # Draw arrow above NPC
                arrow_points = [
                    (npc_screen_x, npc_screen_y - 30),
                    (npc_screen_x - 10, npc_screen_y - 40),
                    (npc_screen_x + 10, npc_screen_y - 40)
                ]
                pygame.draw.polygon(screen, (255, 255, 0), arrow_points)