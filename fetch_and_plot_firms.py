import os
import pandas as pd
import requests
import folium
from io import StringIO

# 📌 Replace with your own key
MAP_KEY = "d719b8824223cf19646321db19e7c59b"

# Define source and region (India bounding box)
SOURCE = "VIIRS_SNPP_NRT"
AREA = "68,6,98,36"  # west,south,east,north covering India
DAYS = 3  # last 3 days

URL = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{AREA}/{DAYS}"


def fetch_fire_data(url):
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    return df


def plot_fire_map(df):
    # Center map over India
    m = folium.Map(location=[22, 80], zoom_start=5, tiles="CartoDB positron")

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=3 + row.frp / 10,
            color="red" if row.confidence in ['h', 'n'] else "orange",
            fill=True,
            fill_opacity=0.7,
            popup=(f"{row.acq_date} {row.acq_time}, FRP: {row.frp}")
        ).add_to(m)

    m.save("firms_fire_map_india.html")
    print("Map saved to firms_fire_map_india.html")


def main():
    df = fetch_fire_data(URL)
    print(f"Fetched {len(df)} fire hotspots from last {DAYS} days")
    plot_fire_map(df)


if __name__ == "__main__":
    main()
