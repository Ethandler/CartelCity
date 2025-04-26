"""
Character sprite generation for South Park Canada-inspired characters
This module provides functions for rendering characters with the distinctive
South Park Canada style - flappy heads, simplistic designs, and bright colors.
"""
import pygame
import math
import random

# Standard South Park Canada-style colors
CANADIAN_COLORS = {
    'skin': (255, 223, 196),
    'shirt_colors': [
        (200, 0, 0),       # Red
        (0, 100, 200),     # Blue
        (0, 150, 0),       # Green
        (200, 200, 0),     # Yellow
        (150, 0, 150),     # Purple
        (255, 100, 100),   # Light red
        (100, 100, 255),   # Light blue
        (100, 255, 100),   # Light green
        (255, 255, 100),   # Light yellow
    ],
    'pants_colors': [
        (0, 0, 150),       # Blue jeans
        (40, 40, 40),      # Black pants
        (100, 80, 60),     # Brown pants
        (80, 80, 80),      # Gray pants
    ],
    'shoes': (40, 40, 40),  # Dark shoes
    'eyes': (0, 0, 0),       # Black eyes
    'mouth': (50, 0, 0),    # Dark red mouth
    'outline': (0, 0, 0)     # Black outline
}

def get_random_character_colors():
    """Return a random set of colors for a character"""
    return {
        'skin': CANADIAN_COLORS['skin'],
        'shirt': random.choice(CANADIAN_COLORS['shirt_colors']),
        'pants': random.choice(CANADIAN_COLORS['pants_colors']),
        'shoes': CANADIAN_COLORS['shoes'],
        'eyes': CANADIAN_COLORS['eyes'],
        'mouth': CANADIAN_COLORS['mouth'],
        'outline': CANADIAN_COLORS['outline']
    }

def draw_canadian_head(surface, x, y, size, colors, head_bob=0, direction='down'):
    """
    Draw a South Park Canada-style character head
    
    Args:
        surface: Pygame surface to draw on
        x, y: Center position for the head
        size: Base size of the head
        colors: Dictionary of colors to use
        head_bob: Vertical head bob offset (for animation)
        direction: Character facing direction ('up', 'down', 'left', 'right')
    """
    # Get outline color (use black as fallback if not provided)
    outline_color = colors.get('outline', (0, 0, 0))
    
    # Head outline (slightly larger than the filled head)
    pygame.draw.ellipse(
        surface,
        outline_color,
        (x - size/2 - 1, y - size/2 - 1 + head_bob, size + 2, size + 2)
    )
    
    # Main head shape (filled)
    pygame.draw.ellipse(
        surface,
        colors['skin'],
        (x - size/2, y - size/2 + head_bob, size, size)
    )
    
    # Eyes (black dots)
    eye_spacing = size * 0.3
    eye_size = max(size * 0.12, 2)  # Ensure eyes are at least 2 pixels
    
    # Adjust eye position based on direction
    if direction == 'left':
        # Both eyes on left side
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x - eye_spacing/2), int(y + head_bob)), int(eye_size))
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x - eye_spacing/2), int(y + head_bob - eye_spacing/2)), int(eye_size))
    elif direction == 'right':
        # Both eyes on right side
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x + eye_spacing/2), int(y + head_bob)), int(eye_size))
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x + eye_spacing/2), int(y + head_bob - eye_spacing/2)), int(eye_size))
    elif direction == 'up':
        # Eyes toward top
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x - eye_spacing/2), int(y + head_bob - eye_spacing/3)), int(eye_size))
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x + eye_spacing/2), int(y + head_bob - eye_spacing/3)), int(eye_size))
    else:  # down or default
        # Standard eye position
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x - eye_spacing/2), int(y + head_bob)), int(eye_size))
        pygame.draw.circle(surface, colors['eyes'], 
                         (int(x + eye_spacing/2), int(y + head_bob)), int(eye_size))
    
    # Mouth (distinctive Canadian split mouth)
    mouth_width = size * 0.4
    mouth_height = size * 0.1
    pygame.draw.ellipse(
        surface,
        colors['mouth'],
        (x - mouth_width/2, y + size/4 + head_bob, mouth_width, mouth_height)
    )
    
    # Mouth split line
    outline_color = colors.get('outline', (0, 0, 0))
    pygame.draw.line(
        surface,
        outline_color,
        (x, y + size/4 + head_bob),
        (x, y + size/4 + head_bob + mouth_height),
        max(1, int(size * 0.05))
    )

def draw_canadian_body(surface, x, y, size, colors, walk_offset=0, direction='down'):
    """
    Draw a South Park Canada-style character body
    
    Args:
        surface: Pygame surface to draw on
        x, y: Center position for the body (top of body)
        size: Base size of the character
        colors: Dictionary of colors to use
        walk_offset: Horizontal leg offset for walking animation
        direction: Character facing direction ('up', 'down', 'left', 'right')
    """
    body_width = size * 0.7
    body_height = size * 0.5
    
    # Body (oval shape)
    pygame.draw.ellipse(
        surface,
        colors['shirt'],
        (x - body_width/2, y, body_width, body_height)
    )
    
    # Outline for body
    outline_color = colors.get('outline', (0, 0, 0))
    pygame.draw.ellipse(
        surface,
        outline_color,
        (x - body_width/2, y, body_width, body_height),
        max(1, int(size * 0.05))
    )
    
    # Legs
    leg_width = size * 0.15
    leg_height = size * 0.4
    left_leg_x = x - size * 0.2 + walk_offset
    right_leg_x = x + size * 0.2 - walk_offset
    
    # Left leg with outline
    outline_color = colors.get('outline', (0, 0, 0))
    pygame.draw.rect(
        surface,
        outline_color,
        (left_leg_x - leg_width/2 - 1, y + body_height - 1, leg_width + 2, leg_height + 2)
    )
    pygame.draw.rect(
        surface,
        colors['pants'],
        (left_leg_x - leg_width/2, y + body_height, leg_width, leg_height)
    )
    
    # Right leg with outline
    outline_color = colors.get('outline', (0, 0, 0))
    pygame.draw.rect(
        surface,
        outline_color,
        (right_leg_x - leg_width/2 - 1, y + body_height - 1, leg_width + 2, leg_height + 2)
    )
    pygame.draw.rect(
        surface,
        colors['pants'],
        (right_leg_x - leg_width/2, y + body_height, leg_width, leg_height)
    )
    
    # Shoes
    shoe_size = size * 0.2
    pygame.draw.ellipse(
        surface,
        colors['shoes'],
        (left_leg_x - shoe_size/2, y + body_height + leg_height - shoe_size/2, shoe_size, shoe_size)
    )
    pygame.draw.ellipse(
        surface,
        colors['shoes'],
        (right_leg_x - shoe_size/2, y + body_height + leg_height - shoe_size/2, shoe_size, shoe_size)
    )

def draw_canadian_character(surface, x, y, size, colors, animation_frame=0, moving=False, direction='down'):
    """
    Draw a complete South Park Canada-style character
    
    Args:
        surface: Pygame surface to draw on
        x, y: Center position for the character
        size: Base size of the character
        colors: Dictionary of colors to use
        animation_frame: Current animation frame (0-1 range)
        moving: Whether the character is moving
        direction: Character facing direction ('up', 'down', 'left', 'right')
    """
    # Calculate animation offsets
    walk_offset = math.sin(animation_frame * math.pi) * (size * 0.1) if moving else 0
    head_bob = math.sin(animation_frame * math.pi * 2) * (size * 0.08)  # Exaggerated head bob
    
    # Draw body first (so head overlaps it appropriately)
    body_y = y - size * 0.1  # Adjust body position to connect with head
    draw_canadian_body(surface, x, body_y, size, colors, walk_offset, direction)
    
    # Draw head on top
    head_y = y - size * 0.4  # Position head above body
    draw_canadian_head(surface, x, head_y, size * 0.8, colors, head_bob, direction)
    
    return surface

def draw_dead_canadian(surface, x, y, size, colors, angle=0):
    """Draw a dead South Park Canada-style character"""
    # Create a simplified character lying on the ground
    body_width = size * 1.2
    body_height = size * 0.5
    
    # Draw blood puddle under body
    pygame.draw.ellipse(
        surface,
        (150, 0, 0, 180),  # Semi-transparent red
        (x - body_width/2 - size*0.2, y - body_height/2 - size*0.1, 
         body_width + size*0.4, body_height + size*0.2)
    )
    
    # Body lying down
    pygame.draw.ellipse(
        surface,
        colors['shirt'],
        (x - body_width/2, y - body_height/2, body_width, body_height)
    )
    
    # Head to the side
    pygame.draw.circle(
        surface,
        colors['skin'],
        (int(x - body_width/2 + size*0.3), int(y)),
        int(size * 0.3)
    )
    
    # X eyes
    eye_size = size * 0.1
    eye_x = x - body_width/2 + size*0.3
    eye_y = y
    
    # Draw X eyes (crossed out)
    outline_color = colors.get('outline', (0, 0, 0))
    pygame.draw.line(surface, outline_color, 
                   (eye_x - eye_size, eye_y - eye_size), 
                   (eye_x + eye_size, eye_y + eye_size), 1)
    pygame.draw.line(surface, outline_color, 
                   (eye_x - eye_size, eye_y + eye_size), 
                   (eye_x + eye_size, eye_y - eye_size), 1)
    
    # Rotate the entire surface if needed
    if angle != 0:
        surface = pygame.transform.rotate(surface, angle)
    
    return surface