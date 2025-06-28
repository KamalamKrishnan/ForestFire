import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
from io import StringIO

# Constants
EMPTY, TREE, BURNING = 0, 1, 2
GRID_SIZE = 50
STEPS = 30

# ✅ Replace with your actual API key
API_KEY = "d719b8824223cf19646321db19e7c59b"
SOURCE = "VIIRS_SNPP_NRT"
AREA = "68,6,98,36"  # India's bounding box
DAYS = 3

FIRMS_URL = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{SOURCE}/{AREA}/{DAYS}"

# Initialize forest


def create_forest():
    return np.ones((GRID_SIZE, GRID_SIZE), dtype=int)

# Fetch FIRMS fire data


def fetch_firms_data(url):
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    return df[['latitude', 'longitude']]

# Map lat/lon to grid (simplified)


def map_to_grid(lat, lon):
    # Normalize India lat: 6-36 → 0–GRID_SIZE, lon: 68–98 → 0–GRID_SIZE
    row = int((36 - lat) / 30 * GRID_SIZE)  # latitude goes top to bottom
    col = int((lon - 68) / 30 * GRID_SIZE)
    return row, col

# Place fires into forest grid


def apply_fire_spots(forest, spots):
    for _, row in spots.iterrows():
        r, c = map_to_grid(row['latitude'], row['longitude'])
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            forest[r][c] = BURNING
    return forest

# Spread fire logic


def spread_fire(forest, wind='N'):
    new_forest = forest.copy()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if forest[r][c] == TREE:
                neighbors = []
                if r > 0:
                    neighbors.append(forest[r-1][c])  # N
                if r < GRID_SIZE-1:
                    neighbors.append(forest[r+1][c])  # S
                if c > 0:
                    neighbors.append(forest[r][c-1])  # W
                if c < GRID_SIZE-1:
                    neighbors.append(forest[r][c+1])  # E

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

# Visualize the forest grid


def visualize_forest(forest, step):
    colors = {EMPTY: (0.9, 0.9, 0.9), TREE: (0, 0.6, 0), BURNING: (1, 0, 0)}
    rgb_grid = np.array([[colors[cell] for cell in row] for row in forest])
    plt.imshow(rgb_grid)
    plt.title(f"🔥 Forest Fire Spread - Step {step}")
    plt.axis('off')
    plt.pause(0.3)

# Main simulation loop


def simulate_fire():
    wind = input("Enter wind direction (N, S, E, W): ").upper()
    forest = create_forest()

    print("📡 Fetching FIRMS data...")
    spots = fetch_firms_data(FIRMS_URL)
    print(f"🔥 Found {len(spots)} fire hotspots in last {DAYS} days")
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
    plt.title("🔥 Burning Trees Over Time")
    plt.xlabel("Step")
    plt.ylabel("Burning Count")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    simulate_fire()
