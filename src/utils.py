import random


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def add_screen_noise(position: tuple[int, int], screen_size: tuple[int, int], factor: float = 0.005) -> tuple[int, int]:
    x_rand = int(screen_size[0] * 0.005)
    y_rand = int(screen_size[1] * 0.005)
    x = clamp(random.randint(
        int(position[0]-x_rand), int(position[0]+x_rand)), 0, screen_size[0])
    y = clamp(random.randint(
        int(position[1]-y_rand), int(position[1]+y_rand)), 0, screen_size[1])
    return x, y
