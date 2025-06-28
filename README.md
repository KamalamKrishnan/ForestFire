# 🔥 Forest Fire Simulation using FIRMS Data (ISRO Hackathon)

A real-time forest fire spread simulation system integrated with NASA FIRMS fire hotspot data for India.

## 📌 Features

- ✅ Fetches live fire hotspots from FIRMS API
- ✅ Visualizes fires spreading over a simulated forest grid
- ✅ Simulates wind-based fire spread logic
- ✅ Graphs number of trees burned over time
- ✅ Interactive HTML map (folium) with real FIRMS fire points

## 🛰️ Real-time Fire Map

- The map (`firms_fire_map_india.html`) shows fire hotspots in India from the last 3 days using NASA FIRMS data.

## 🧠 How It Works

1. Fetch fire data from FIRMS API
2. Convert fire locations to grid points
3. Simulate spread based on wind direction and neighbors
4. Animate using matplotlib
5. Overlay real hotspots on a live map


## ⚙️ How to Run

```bash
python fetch_and_plot_firms.py     # To fetch latest data & generate map
python simulate_fire_spread.py     # To run the simulation

