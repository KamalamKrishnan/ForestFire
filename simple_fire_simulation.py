import matplotlib.pyplot as plt
import numpy as np
import random
import time

# Grid codes: 0 - empty, 1 - tree, 2 - burning
EMPTY, TREE, BURNING = 0, 1, 2

# Wind direction: 'N', 'S', 'E', 'W' (You can change this)
wind_direction = input("Enter wind direction (N, S, E, W): ").strip().upper()
if wind_direction not in ['N', 'S', 'E', 'W']:
    print("Invalid input. Defaulting to East (E).")
    wind_direction = 'E'

# Wind bias: makes spread more likely in wind direction
wind_bias = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1)
}


def initialize_forest(size):
    forest = np.ones((size, size), dtype=int)
    forest[size // 2][size // 2] = BURNING  # Start fire in the center
    return forest


def spread_fire(forest):
    new_forest = forest.copy()
    size = forest.shape[0]
    drc = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E

    for i in range(size):
        for j in range(size):
            if forest[i][j] == BURNING:
                new_forest[i][j] = EMPTY
                for dx, dy in drc:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < size and 0 <= nj < size:
                        if forest[ni][nj] == TREE:
                            # Wind helps in its direction
                            is_wind_dir = (dx, dy) == wind_bias[wind_direction]
                            chance = 0.9 if is_wind_dir else 0.3
                            if random.random() < chance:
                                new_forest[ni][nj] = BURNING
    return new_forest


def visualize_forest(forest, step):
    colors = {EMPTY: (1, 1, 1), TREE: (0, 0.6, 0), BURNING: (1, 0, 0)}
    rgb_grid = np.zeros(forest.shape + (3,))
    for val, color in colors.items():
        rgb_grid[forest == val] = color
    plt.imshow(rgb_grid)
    plt.title(f"Step {step} - Wind: {wind_direction}")
    plt.axis('off')
    plt.pause(0.5)


def simulate_fire(steps=20, size=10):
    forest = initialize_forest(size)
    burning_counts = []  # 📊 Track how many trees are burning each step

    plt.figure(figsize=(5, 5))
    for step in range(steps):
        visualize_forest(forest, step)
        burning_count = np.count_nonzero(forest == BURNING)
        burning_counts.append(burning_count)
        forest = spread_fire(forest)
    plt.show()

    # 📈 Plot burning trees over time
    plt.figure(figsize=(8, 4))
    plt.plot(burning_counts, marker='o', color='orange')
    plt.title("Burning Trees Over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Number of Burning Trees")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    simulate_fire()
