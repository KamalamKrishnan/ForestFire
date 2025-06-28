import folium
import pandas as pd
import requests
from io import StringIO

# Constants
MAP_KEY = "d719b8824223cf19646321db19e7c59b"
SOURCE = "VIIRS_SNPP_NRT"
AREA = "68,6,98,36"
DAYS = 3
MAP_FILENAME = "firms_fire_map_india.html"
GRID_ROWS = 10
GRID_COLS = 10

# GeoJSON for India's boundary
INDIA_GEOJSON_URL = "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"


def fetch_fire_data(url):
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    return df[['latitude', 'longitude']]


def plot_map_with_grid(spots, lat_range=(6, 36), lon_range=(68, 98)):
    m = folium.Map(
        location=[22, 80],
        zoom_start=5,
        tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
        attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap",
    )

    # Add India's boundary
    india_geojson = requests.get(INDIA_GEOJSON_URL).json()
    folium.GeoJson(
        india_geojson,
        name="India",
        style_function=lambda feature: {
            'fillColor': '#00000000',  # Transparent fill
            'color': 'black',
            'weight': 2,
        }
    ).add_to(m)

    # 🔥 Fire spots
    for _, row in spots.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.8
        ).add_to(m)

    # 🔲 Grid
    lat_start, lat_end = lat_range
    lon_start, lon_end = lon_range
    lat_step = (lat_end - lat_start) / GRID_ROWS
    lon_step = (lon_end - lon_start) / GRID_COLS

    for i in range(GRID_ROWS + 1):
        lat = lat_start + i * lat_step
        folium.PolyLine(
            locations=[[lat, lon_start], [lat, lon_end]],
            color='blue',
            weight=1,
            opacity=0.4
        ).add_to(m)

    for j in range(GRID_COLS + 1):
        lon = lon_start + j * lon_step
        folium.PolyLine(
            locations=[[lat_start, lon], [lat_end, lon]],
            color='blue',
            weight=1,
            opacity=0.4
        ).add_to(m)

    m.save(MAP_FILENAME)
    print(f"✅ Map with India outline + grid saved to {MAP_FILENAME}")


def main():
    print("📡 Fetching FIRMS fire data...")
    df = fetch_fire_data(
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{AREA}/{DAYS}")
    print(f"🔥 Fetched {len(df)} fire hotspots from last {DAYS} days")
    plot_map_with_grid(df)


if __name__ == "__main__":
    main()
