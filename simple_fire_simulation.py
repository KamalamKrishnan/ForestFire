import time
import os
import copy

# Constants for grid cells
TREE = 'T'
FIRE = 'F'
EMPTY = ' '

# Create a 10x10 forest grid


def create_forest(size=10):
    forest = [[TREE for _ in range(size)] for _ in range(size)]
    # Set initial fire in center
    mid = size // 2
    forest[mid][mid] = FIRE
    return forest

# Display the grid


def display_forest(forest):
    os.system('cls' if os.name == 'nt' else 'clear')
    for row in forest:
        print(' '.join(row))
    print()

# Simulate fire spread


def spread_fire(forest):
    new_forest = copy.deepcopy(forest)
    size = len(forest)

    for i in range(size):
        for j in range(size):
            if forest[i][j] == FIRE:
                # Current burning tree becomes empty
                new_forest[i][j] = EMPTY

                # Spread to neighbors
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < size and 0 <= nj < size:
                        if forest[ni][nj] == TREE:
                            new_forest[ni][nj] = FIRE
    return new_forest


# Run the simulation
forest = create_forest()
steps = 10

for step in range(steps):
    print(f"Step {step + 1}")
    display_forest(forest)
    forest = spread_fire(forest)
    time.sleep(1)
