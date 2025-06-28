import folium
import pandas as pd
import requests
from io import StringIO
from folium.plugins import TimestampedGeoJson

# Constants
MAP_KEY = "d719b8824223cf19646321db19e7c59b"
SOURCE = "VIIRS_SNPP_NRT"
AREA = "68,6,98,36"  # India bbox (lon_min, lat_min, lon_max, lat_max)
DAYS = 7
MAP_FILENAME = "firms_fire_map_india.html"
GRID_ROWS = 10
GRID_COLS = 10

INDIA_GEOJSON_URL = "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"


def fetch_fire_data(url):
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    return df[['latitude', 'longitude', 'acq_date']]


def convert_to_geojson(df):
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']],
            },
            "properties": {
                "time": row['acq_date'],
                "style": {"color": "red"},
                "icon": "circle",
                "iconstyle": {
                    "fillColor": "red",
                    "fillOpacity": 0.6,
                    "stroke": "true",
                    "radius": 4
                }
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


def plot_map_with_animation(df, lat_range=(6, 36), lon_range=(68, 98)):
    m = folium.Map(
        location=[22, 80],
        zoom_start=5,
        tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
        attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap",
    )

    # India outline
    india_geojson = requests.get(INDIA_GEOJSON_URL).json()
    folium.GeoJson(
        india_geojson,
        name="India",
        style_function=lambda feature: {
            'fillColor': '#00000000',
            'color': 'black',
            'weight': 2,
        }
    ).add_to(m)

    # Grid overlay
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

    # 🔥 Animated fire spread
    fire_geojson = convert_to_geojson(df)
    TimestampedGeoJson(
        data=fire_geojson,
        period="P1D",
        add_last_point=True,
        auto_play=True,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options='YYYY-MM-DD',
        time_slider_drag_update=True,
    ).add_to(m)

    m.save(MAP_FILENAME)
    print(f"✅ Animated fire map saved to {MAP_FILENAME}")


def main():
    print("📡 Fetching FIRMS fire data (last 7 days)...")
    df = fetch_fire_data(
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{AREA}/{DAYS}")
    print(f"🔥 Fetched {len(df)} fire hotspots")
    plot_map_with_animation(df)


if __name__ == "__main__":
    main()
