"""
Escalating Event System for GTA-style South Park Canadian game
This module implements random events that trigger when the player lingers,
gradually escalating in chaos and crime.
"""
import random
import math
import pygame

class EventSystem:
    """Manages escalating events that occur around the player"""
    def __init__(self, game):
        self.game = game
        self.active_events = []
        self.event_cooldown = 0
        self.min_cooldown = 600  # 10 seconds at 60 fps
        self.event_regions = []  # Regions where events can trigger
        self.player_time_in_region = {}  # Time spent in each region
        self.hovering_threshold = 300  # 5 seconds before events start triggering
        
        # Initialize event templates
        self.event_templates = self.initialize_event_templates()
        
        # Initialize event regions
        self.initialize_event_regions()
    
    def initialize_event_templates(self):
        """Define templates for different types of escalating events"""
        templates = []
        
        # Suspicious Activity / Police Escalation
        templates.append({
            "name": "Police Escalation",
            "trigger_locations": ["bank", "police_station", "high_value"],
            "stages": [
                {
                    "description": "Suspicious Activity Reported",
                    "duration": 600,  # 10 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "police", "count": 1, "distance": 300},
                        {"type": "message", "text": "Someone reported suspicious activity, eh!"}
                    ]
                },
                {
                    "description": "Police Investigation",
                    "duration": 900,  # 15 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "police", "count": 2, "distance": 250},
                        {"type": "message", "text": "The Mounties are investigating the area!"}
                    ]
                },
                {
                    "description": "SWAT Team Deployed",
                    "duration": 1200,  # 20 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "police", "count": 4, "distance": 200},
                        {"type": "spawn_entity", "entity": "swat", "count": 2, "distance": 350},
                        {"type": "message", "text": "SWAT team has been deployed, buddy!"}
                    ]
                }
            ]
        })
        
        # Cult Gathering
        templates.append({
            "name": "Cult Gathering",
            "trigger_locations": ["alley", "dark_area", "forest"],
            "stages": [
                {
                    "description": "Strange Chanting",
                    "duration": 600,  # 10 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "cultist", "count": 3, "distance": 200},
                        {"type": "message", "text": "You hear strange chanting nearby..."}
                    ]
                },
                {
                    "description": "Cult Ritual",
                    "duration": 900,  # 15 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "cultist", "count": 5, "distance": 180},
                        {"type": "effect", "name": "strange_lights", "duration": 900},
                        {"type": "message", "text": "The cultists are performing some kind of ritual!"}
                    ]
                },
                {
                    "description": "Cult Hunt",
                    "duration": 1200,  # 20 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "cultist", "count": 8, "distance": 150},
                        {"type": "effect", "name": "strange_lights", "duration": 1200},
                        {"type": "message", "text": "The cultists have spotted you! They're coming for you, guy!"}
                    ]
                }
            ]
        })
        
        # Street Performer Revenge
        templates.append({
            "name": "Mime Riot",
            "trigger_locations": ["park", "street_corner", "plaza"],
            "stages": [
                {
                    "description": "Street Performers",
                    "duration": 600,  # 10 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "mime", "count": 2, "distance": 150},
                        {"type": "message", "text": "Street performers are doing their thing..."}
                    ]
                },
                {
                    "description": "Mime Congregation",
                    "duration": 900,  # 15 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "mime", "count": 5, "distance": 130},
                        {"type": "message", "text": "More mimes are silently gathering..."}
                    ]
                },
                {
                    "description": "Silent Riot",
                    "duration": 1200,  # 20 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "mime", "count": 10, "distance": 100},
                        {"type": "effect", "name": "mime_rage", "duration": 1200},
                        {"type": "message", "text": "The mimes are rioting! Silently but deadly!"}
                    ]
                }
            ]
        })
        
        # Road Rage Event
        templates.append({
            "name": "Road Rage",
            "trigger_locations": ["intersection", "highway", "road"],
            "stages": [
                {
                    "description": "Traffic Jam",
                    "duration": 600,  # 10 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "vehicle", "count": 4, "distance": 200},
                        {"type": "message", "text": "Traffic is backing up..."}
                    ]
                },
                {
                    "description": "Angry Drivers",
                    "duration": 900,  # 15 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "vehicle", "count": 6, "distance": 180},
                        {"type": "effect", "name": "honking", "duration": 900},
                        {"type": "message", "text": "Drivers are getting angry, friend!"}
                    ]
                },
                {
                    "description": "Road Rage Chaos",
                    "duration": 1200,  # 20 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "angry_driver", "count": 4, "distance": 150},
                        {"type": "spawn_entity", "entity": "vehicle", "count": 8, "distance": 130},
                        {"type": "effect", "name": "honking", "duration": 1200},
                        {"type": "message", "text": "Full-on road rage! Cars are going crazy, guy!"}
                    ]
                }
            ]
        })
        
        # Gang Activity
        templates.append({
            "name": "Gang Activity",
            "trigger_locations": ["alley", "dark_area", "bad_neighborhood"],
            "stages": [
                {
                    "description": "Gang Members Appear",
                    "duration": 600,  # 10 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "gang_member", "count": 3, "distance": 200},
                        {"type": "message", "text": "Some suspicious characters have spotted you..."}
                    ]
                },
                {
                    "description": "Gang Confrontation",
                    "duration": 900,  # 15 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "gang_member", "count": 5, "distance": 150},
                        {"type": "message", "text": "The gang members are confronting you, buddy!"}
                    ]
                },
                {
                    "description": "Gang War",
                    "duration": 1200,  # 20 seconds
                    "actions": [
                        {"type": "spawn_entity", "entity": "gang_member", "count": 8, "distance": 130},
                        {"type": "spawn_entity", "entity": "rival_gang", "count": 6, "distance": 200},
                        {"type": "message", "text": "A full-on gang war has erupted!"}
                    ]
                }
            ]
        })
        
        return templates
    
    def initialize_event_regions(self):
        """Define regions where events can trigger"""
        # In a real implementation, this would analyze the map
        # For now, we'll create regions based on the map's size
        
        # Get map size
        map_width = getattr(self.game.map, 'width', 2400)
        map_height = getattr(self.game.map, 'height', 1800)
        
        # Create regions in a grid pattern
        region_size = 300
        for x in range(0, map_width, region_size):
            for y in range(0, map_height, region_size):
                region_type = self.determine_region_type(x, y)
                
                self.event_regions.append({
                    "x": x,
                    "y": y,
                    "width": region_size,
                    "height": region_size,
                    "type": region_type
                })
    
    def determine_region_type(self, x, y):
        """Determine the type of region based on location"""
        # This would ideally use map data, but for now we'll randomize
        region_types = [
            "street_corner", "intersection", "alley", "park", 
            "plaza", "bank", "police_station", "dark_area",
            "high_value", "bad_neighborhood", "highway", "road",
            "forest"
        ]
        
        # For banks and police stations, make them less common
        weights = [10, 10, 8, 6, 5, 2, 2, 7, 3, 5, 4, 10, 3]
        
        # Use position to deterministically select type (but still with variety)
        # This ensures the same area always has the same type
        seed = int((x * 127 + y * 311) % 1000)
        random.seed(seed)
        
        # Pick a weighted random type
        region_type = random.choices(region_types, weights=weights, k=1)[0]
        
        # Reset random seed
        random.seed()
        
        return region_type
    
    def update(self, player_x, player_y):
        """Update the event system state"""
        # Update cooldown
        if self.event_cooldown > 0:
            self.event_cooldown -= 1
            
        # Update active events
        events_to_remove = []
        for i, event in enumerate(self.active_events):
            # Update event timing
            event["time_remaining"] -= 1
            
            # Check if event should advance to next stage
            if event["time_remaining"] <= 0:
                if event["current_stage"] < len(event["template"]["stages"]) - 1:
                    # Advance to next stage
                    event["current_stage"] += 1
                    stage = event["template"]["stages"][event["current_stage"]]
                    event["time_remaining"] = stage["duration"]
                    
                    # Execute stage actions
                    self.execute_stage_actions(stage, event["x"], event["y"])
                else:
                    # Event has completed all stages, mark for removal
                    events_to_remove.append(i)
        
        # Remove completed events
        for i in sorted(events_to_remove, reverse=True):
            del self.active_events[i]
            
        # Update player region time
        current_region = self.get_player_region(player_x, player_y)
        
        # Reset all region times if player moved to a new region
        if current_region and current_region.get("id") not in self.player_time_in_region:
            self.player_time_in_region = {current_region.get("id"): 1}
        elif current_region:
            # Increment time in current region
            region_id = current_region.get("id")
            self.player_time_in_region[region_id] = self.player_time_in_region.get(region_id, 0) + 1
            
            # Check if player has been in this region long enough to trigger an event
            if (self.player_time_in_region[region_id] >= self.hovering_threshold and 
                self.event_cooldown <= 0 and len(self.active_events) < 3):
                # Try to trigger an event
                self.try_trigger_event(current_region, player_x, player_y)
    
    def get_player_region(self, player_x, player_y):
        """Determine which region the player is currently in"""
        for i, region in enumerate(self.event_regions):
            if (region["x"] <= player_x < region["x"] + region["width"] and
                region["y"] <= player_y < region["y"] + region["height"]):
                # Add ID for tracking
                region["id"] = i
                return region
        return None
    
    def try_trigger_event(self, region, player_x, player_y):
        """Try to trigger an event in the current region"""
        # Don't trigger if too many events are active
        if len(self.active_events) >= 3:
            return
            
        # Find event templates that can trigger in this region type
        eligible_templates = []
        for template in self.event_templates:
            if region["type"] in template["trigger_locations"]:
                eligible_templates.append(template)
                
        # If no eligible templates, don't trigger anything
        if not eligible_templates:
            return
            
        # Pick a random template
        template = random.choice(eligible_templates)
        
        # Create the event
        event = {
            "template": template,
            "current_stage": 0,
            "time_remaining": template["stages"][0]["duration"],
            "x": player_x,
            "y": player_y,
            "region": region
        }
        
        # Add to active events
        self.active_events.append(event)
        
        # Execute first stage actions
        self.execute_stage_actions(template["stages"][0], player_x, player_y)
        
        # Set cooldown
        self.event_cooldown = self.min_cooldown
        
        # Reset time in region
        self.player_time_in_region[region["id"]] = 0
    
    def execute_stage_actions(self, stage, event_x, event_y):
        """Execute the actions for an event stage"""
        for action in stage["actions"]:
            if action["type"] == "spawn_entity":
                self.spawn_entities(action, event_x, event_y)
            elif action["type"] == "message":
                self.show_message(action["text"])
            elif action["type"] == "effect":
                self.apply_effect(action)
    
    def spawn_entities(self, action, event_x, event_y):
        """Spawn entities around the event location"""
        entity_type = action["entity"]
        count = action["count"]
        distance = action["distance"]
        
        for _ in range(count):
            # Determine spawn position
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(distance * 0.5, distance)
            spawn_x = event_x + math.cos(angle) * radius
            spawn_y = event_y + math.sin(angle) * radius
            
            # Create the entity based on type
            if entity_type == "police":
                self.spawn_police(spawn_x, spawn_y)
            elif entity_type == "swat":
                self.spawn_swat(spawn_x, spawn_y)
            elif entity_type == "vehicle":
                self.spawn_vehicle(spawn_x, spawn_y)
            elif entity_type in ["cultist", "mime", "gang_member", "angry_driver", "rival_gang"]:
                self.spawn_special_pedestrian(spawn_x, spawn_y, entity_type)
    
    def spawn_police(self, x, y):
        """Spawn a police vehicle"""
        if hasattr(self.game.map, 'spawn_police'):
            # Use existing spawn method if available
            self.game.map.spawn_police(1, x, y)
        else:
            # Fallback implementation
            if not hasattr(self.game, 'PoliceVehicle'):
                return
                
            police = self.game.PoliceVehicle(x, y)
            self.game.map.police_vehicles.append(police)
    
    def spawn_swat(self, x, y):
        """Spawn a SWAT-type police vehicle (enhanced police)"""
        if hasattr(self.game.map, 'spawn_police'):
            # Use existing spawn method but make it more aggressive
            police = self.game.map.spawn_police(1, x, y)
            if police and isinstance(police, list) and len(police) > 0:
                police = police[0]
                if hasattr(police, 'aggression'):
                    police.aggression = 2.0  # More aggressive
                if hasattr(police, 'speed'):
                    police.speed *= 1.3  # Faster
        else:
            # Fallback implementation
            if not hasattr(self.game, 'PoliceVehicle'):
                return
                
            police = self.game.PoliceVehicle(x, y)
            if hasattr(police, 'aggression'):
                police.aggression = 2.0
            if hasattr(police, 'speed'):
                police.speed *= 1.3
            self.game.map.police_vehicles.append(police)
    
    def spawn_vehicle(self, x, y):
        """Spawn a regular vehicle"""
        if hasattr(self.game.map, 'spawn_vehicles'):
            # Use existing spawn method if available
            self.game.map.spawn_vehicles(1, x, y)
        else:
            # Fallback implementation
            if not hasattr(self.game, 'Vehicle'):
                return
                
            vehicle = self.game.Vehicle(x, y)
            self.game.map.vehicles.append(vehicle)
    
    def spawn_special_pedestrian(self, x, y, entity_type):
        """Spawn a special type of pedestrian"""
        if not hasattr(self.game, 'Pedestrian'):
            return
            
        ped = self.game.Pedestrian(x, y)
        
        # Customize based on type
        if entity_type == "cultist":
            # Cultists wear dark robes
            ped.colors['shirt'] = (40, 0, 40)  # Dark purple
            ped.colors['pants'] = (20, 0, 20)  # Very dark purple
            ped.ai_state = "aggressive"
            ped.speed = 1.2  # Faster
            ped.type = "cultist"
            
        elif entity_type == "mime":
            # Mimes are black and white
            ped.colors['shirt'] = (255, 255, 255)  # White
            ped.colors['pants'] = (0, 0, 0)  # Black
            ped.colors['skin'] = (255, 255, 255)  # White face paint
            ped.ai_state = "erratic"
            ped.type = "mime"
            
        elif entity_type == "gang_member":
            # Gang members are coordinated colors
            ped.colors['shirt'] = (200, 0, 0)  # Red
            ped.colors['pants'] = (0, 0, 0)  # Black
            ped.ai_state = "aggressive"
            ped.type = "gang_member"
            
        elif entity_type == "rival_gang":
            # Rival gang has different colors
            ped.colors['shirt'] = (0, 0, 200)  # Blue
            ped.colors['pants'] = (0, 0, 0)  # Black
            ped.ai_state = "aggressive"
            ped.type = "rival_gang"
            
        elif entity_type == "angry_driver":
            # Angry driver is ready to fight
            ped.colors['shirt'] = (200, 100, 0)  # Orange
            ped.ai_state = "aggressive"
            ped.type = "angry_driver"
        
        # Set behavior based on type
        if hasattr(ped, 'ai_state') and ped.ai_state == "aggressive":
            ped.flee_target = None
            ped.target = self.game.player
        
        # Add to pedestrians list
        self.game.map.pedestrians.append(ped)
    
    def show_message(self, text):
        """Display a message to the player"""
        # Use game's message system if available
        if hasattr(self.game, 'show_message'):
            self.game.show_message(text)
        elif hasattr(self.game, 'message'):
            self.game.message = text
            self.game.message_timer = 180  # 3 seconds
    
    def apply_effect(self, action):
        """Apply a special effect to the game"""
        effect_name = action["name"]
        duration = action.get("duration", 600)
        
        if effect_name == "strange_lights":
            # Create a visual effect
            if not hasattr(self.game, 'visual_effects'):
                self.game.visual_effects = []
                
            self.game.visual_effects.append({
                "type": "strange_lights",
                "duration": duration,
                "time_remaining": duration
            })
            
        elif effect_name == "mime_rage":
            # Make mimes more aggressive
            for ped in self.game.map.pedestrians:
                if getattr(ped, 'type', '') == 'mime':
                    ped.ai_state = "aggressive"
                    ped.speed *= 1.5
                    ped.target = self.game.player
                    
        elif effect_name == "honking":
            # Add honking sounds to vehicles
            if not hasattr(self.game, 'sound_effects'):
                self.game.sound_effects = []
                
            self.game.sound_effects.append({
                "type": "honking",
                "duration": duration,
                "time_remaining": duration
            })
    
    def draw(self, screen, camera_x, camera_y, font):
        """Draw debug visualization of regions and events"""
        # Only draw in debug mode
        if not getattr(self.game, 'show_debug', False):
            return
            
        # Draw regions
        for region in self.event_regions:
            screen_x = region["x"] - camera_x
            screen_y = region["y"] - camera_y
            
            # Skip if off-screen
            if (screen_x + region["width"] < 0 or screen_x > screen.get_width() or
                screen_y + region["height"] < 0 or screen_y > screen.get_height()):
                continue
                
            # Draw region rectangle
            pygame.draw.rect(
                screen, 
                (100, 100, 100, 50), 
                (screen_x, screen_y, region["width"], region["height"]),
                1
            )
            
            # Draw region type
            if font:
                text = font.render(region["type"], True, (150, 150, 150))
                screen.blit(text, (screen_x + 5, screen_y + 5))
                
        # Draw active events
        for event in self.active_events:
            screen_x = event["x"] - camera_x
            screen_y = event["y"] - camera_y
            
            # Skip if off-screen
            if (screen_x < 0 or screen_x > screen.get_width() or
                screen_y < 0 or screen_y > screen.get_height()):
                continue
                
            # Draw event circle
            stage = event["template"]["stages"][event["current_stage"]]
            pygame.draw.circle(
                screen,
                (255, 0, 0, 150),
                (int(screen_x), int(screen_y)),
                50,
                2
            )
            
            # Draw event info
            if font:
                text = font.render(
                    f"{event['template']['name']} - Stage {event['current_stage'] + 1}: {stage['description']}",
                    True, 
                    (255, 150, 150)
                )
                screen.blit(text, (screen_x - text.get_width() // 2, screen_y - 30))