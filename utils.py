import math

def distance_between_points(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def normalize_vector(x, y):
    length = math.sqrt(x*x + y*y)
    if length == 0:
        return (0, 0)
    return (x/length, y/length)

def rect_collision(rect1, rect2):
    return (rect1.x < rect2.x + rect2.w and
            rect1.x + rect1.w > rect2.x and
            rect1.y < rect2.y + rect2.h and
            rect1.y + rect1.h > rect2.y)
