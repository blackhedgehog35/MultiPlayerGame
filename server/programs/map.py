import numpy as np
import noise
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random


def generate_map(seed, width=50, height=50, scale=10.0, octaves=6, persistence=0.5, lacunarity=2.0):
    np.random.seed(seed)
    random.seed(seed)
    world_map = np.zeros((height, width))

    for i in range(height):
        for j in range(width):
            world_map[i][j] = noise.pnoise2(i / scale,
                                            j / scale,
                                            octaves=octaves,
                                            persistence=persistence,
                                            lacunarity=lacunarity,
                                            repeatx=width,
                                            repeaty=height,
                                            base=seed)

    # Normalize to 0-1
    min_val = np.min(world_map)
    max_val = np.max(world_map)
    world_map = (world_map - min_val) / (max_val - min_val)

    # Convert to discrete values
    discrete_map = np.zeros((height, width), dtype=int)
    for i in range(height):
        for j in range(width):
            value = world_map[i][j]
            if value < 0.2:
                discrete_map[i][j] = 1  # Water
            elif value < 0.5:
                discrete_map[i][j] = 0  # Land
            elif value < 0.6:
                discrete_map[i][j] = 2  # Path
            else:
                discrete_map[i][j] = 0  # Ensure more land for potential houses and chests

    # Ensure chests are isolated
    for _ in range(10):  # Let's place 10 chests
        while True:
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            if discrete_map[y][x] == 0:  # Place chest only on land
                discrete_map[y][x] = 4
                break

    # Place houses in clusters
    house_clusters = 10
    for _ in range(house_clusters):
        while True:
            x_start = random.randint(0, width - 6)
            y_start = random.randint(0, height - 6)
            if all(discrete_map[y][x] == 0 for x in range(x_start, x_start + 5) for y in range(y_start, y_start + 5)):
                for x in range(x_start, x_start + 4):
                    for y in range(y_start, y_start + 4):
                        discrete_map[y][x] = 3
                # Create paths around the cluster
                for x in range(x_start - 1, x_start + 5):
                    if 0 <= x < width:
                        if 0 <= y_start - 1 < height:
                            discrete_map[y_start - 1][x] = 2
                        if 0 <= y_start + 4 < height:
                            discrete_map[y_start + 4][x] = 2
                for y in range(y_start - 1, y_start + 5):
                    if 0 <= y < height:
                        if 0 <= x_start - 1 < width:
                            discrete_map[y][x_start - 1] = 2
                        if 0 <= x_start + 4 < width:
                            discrete_map[y][x_start + 4] = 2

                # Add a small probability to create extra paths around the cluster
                for _ in range(4):
                    nx, ny = x_start + random.randint(-1, 4), y_start + random.randint(-1, 4)
                    if 0 <= nx < width and 0 <= ny < height and discrete_map[ny][nx] == 0:
                        discrete_map[ny][nx] = 2
                break

    return discrete_map


def display_map(map_data):
    color_map = {
        0: "green",  # Land
        1: "blue",  # Water
        2: "gray",  # Path
        3: "brown",  # Houses
        4: "yellow"  # Chests
    }

    # Create a colormap
    cmap = mcolors.ListedColormap([color_map[i] for i in range(len(color_map))])
    bounds = list(color_map.keys()) + [max(color_map.keys()) + 1]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    plt.figure(figsize=(10, 10))
    plt.imshow(map_data, cmap=cmap, norm=norm, interpolation='nearest')
    plt.colorbar(ticks=bounds[:-1])
    plt.grid(False)
    plt.show()


# Example usage
seed = 51931
map_data = generate_map(seed)
display_map(map_data)
