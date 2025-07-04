import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
from io import StringIO

# Constants
EMPTY, TREE, BURNING = 0, 1, 2
GRID_SIZE = 50
STEPS = 30
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/MODIS/3/IND/1"

# Initialize forest


def create_forest():
    forest = np.ones((GRID_SIZE, GRID_SIZE), dtype=int)
    return forest

# Fetch FIRMS fire data


def fetch_firms_data(url):
    resp = requests.get(url)
    df = pd.read_csv(StringIO(resp.text))
    return df[['latitude', 'longitude']]

# Convert lat/lon to grid coords (simple simulated conversion)


def map_to_grid(lat, lon):
    row = int((lat - 5) % 50)  # Adjust as needed
    col = int((lon - 60) % 50)
    return row, col

# Apply FIRMS data to forest


def apply_fire_spots(forest, spots):
    for _, row in spots.iterrows():
        r, c = map_to_grid(row['latitude'], row['longitude'])
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            forest[r][c] = BURNING
    return forest

# Spread fire with wind direction


def spread_fire(forest, wind='N'):
    new_forest = forest.copy()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if forest[r][c] == TREE:
                neighbors = []
                if r > 0:
                    neighbors.append(forest[r-1][c])     # North
                if r < GRID_SIZE-1:
                    neighbors.append(forest[r+1][c])  # South
                if c > 0:
                    neighbors.append(forest[r][c-1])     # West
                if c < GRID_SIZE-1:
                    neighbors.append(forest[r][c+1])  # East

                wind_bonus = {
                    'N': forest[r-1][c] if r > 0 else EMPTY,
                    'S': forest[r+1][c] if r < GRID_SIZE-1 else EMPTY,
                    'E': forest[r][c+1] if c < GRID_SIZE-1 else EMPTY,
                    'W': forest[r][c-1] if c > 0 else EMPTY
                }.get(wind.upper(), EMPTY)

                if BURNING in neighbors or wind_bonus == BURNING:
                    new_forest[r][c] = BURNING
            elif forest[r][c] == BURNING:
                new_forest[r][c] = EMPTY
    return new_forest

# Plot forest grid


def visualize_forest(forest, step):
    colors = {EMPTY: (0.9, 0.9, 0.9), TREE: (0, 0.6, 0), BURNING: (1, 0, 0)}
    rgb_grid = np.array([[colors[cell] for cell in row] for row in forest])
    plt.imshow(rgb_grid)
    plt.title(f"Step {step}")
    plt.axis('off')
    plt.pause(0.3)

# Main simulation


def simulate_fire():
    wind = input("Enter wind direction (N, S, E, W): ").upper()
    forest = create_forest()

    # Load FIRMS data
    print("Fetching FIRMS data...")
    spots = fetch_firms_data(FIRMS_URL)
    print(f"🔥 Found {len(spots)} real hotspots")
    forest = apply_fire_spots(forest, spots)

    plt.figure(figsize=(6, 6))
    burning_history = []

    for step in range(STEPS):
        visualize_forest(forest, step)
        burning_count = np.count_nonzero(forest == BURNING)
        burning_history.append(burning_count)
        forest = spread_fire(forest, wind=wind)
        if burning_count == 0:
            break

    plt.close()
    plt.plot(burning_history, color='red')
    plt.title("Burning Trees Over Time")
    plt.xlabel("Step")
    plt.ylabel("Burning Count")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    simulate_fire()
