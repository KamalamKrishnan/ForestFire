import time
import copy
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Constants
TREE = 'T'
FIRE = 'F'
EMPTY = ' '

# Create the forest grid


def create_forest(size=10):
    forest = [[TREE for _ in range(size)] for _ in range(size)]
    mid = size // 2
    forest[mid][mid] = FIRE  # Start fire at center
    return forest

# Simulate one step of fire spread


def spread_fire(forest):
    new_forest = copy.deepcopy(forest)
    size = len(forest)

    for i in range(size):
        for j in range(size):
            if forest[i][j] == FIRE:
                new_forest[i][j] = EMPTY
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < size and 0 <= nj < size:
                        if forest[ni][nj] == TREE:
                            new_forest[ni][nj] = FIRE
    return new_forest

# Convert forest to numeric grid for plotting


def convert_to_numeric(forest):
    mapping = {TREE: 1, FIRE: 2, EMPTY: 0}
    return [[mapping[cell] for cell in row] for row in forest]

# Display forest using matplotlib


def display_forest_plot(forest, step):
    color_map = mcolors.ListedColormap(['lightgray', 'green', 'red'])
    numeric_forest = convert_to_numeric(forest)
    plt.imshow(numeric_forest, cmap=color_map, vmin=0, vmax=2)
    plt.title(f"Forest Fire - Step {step}")
    plt.axis('off')
    plt.pause(0.8)
    plt.clf()


# Run the simulation
forest = create_forest()
steps = 15

plt.figure(figsize=(6, 6))

for step in range(steps):
    display_forest_plot(forest, step)
    forest = spread_fire(forest)

plt.close()
