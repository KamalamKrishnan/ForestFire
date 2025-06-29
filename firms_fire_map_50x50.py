import datetime
from folium.plugins import TimestampedGeoJson
import pandas as pd
import folium
import requests
from bs4 import BeautifulSoup

# Constants
INDIA_GEOJSON_URL = "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"
MAP_CENTER = [22.0, 80.0]
MAP_FILENAME = 'fire_simulation_map.html'
FIRMS_URL = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_Asia_7d.csv'
GRID_ROWS = 50
GRID_COLS = 50
LAT_RANGE = (6.0, 38.0)
LON_RANGE = (68.0, 98.0)


def fetch_fire_data(url):
    df = pd.read_csv(url)
    df = df[['latitude', 'longitude', 'acq_date']]
    return df


def draw_grid(m, lat_range, lon_range, rows, cols):
    lat_start, lat_end = lat_range
    lon_start, lon_end = lon_range
    lat_step = (lat_end - lat_start) / rows
    lon_step = (lon_end - lon_start) / cols

    for i in range(rows + 1):
        lat = lat_start + i * lat_step
        folium.PolyLine([(lat, lon_start), (lat, lon_end)],
                        color="gray", weight=0.5).add_to(m)

    for j in range(cols + 1):
        lon = lon_start + j * lon_step
        folium.PolyLine([(lat_start, lon), (lat_end, lon)],
                        color="gray", weight=0.5).add_to(m)


def get_fire_grid_cells(df, lat_range, lon_range, rows, cols):
    lat_start, lat_end = lat_range
    lon_start, lon_end = lon_range
    lat_step = (lat_end - lat_start) / rows
    lon_step = (lon_end - lon_start) / cols

    fire_cells = set()
    for _, row in df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        i = int((lat - lat_start) / lat_step)
        j = int((lon - lon_start) / lon_step)
        if 0 <= i < rows and 0 <= j < cols:
            fire_cells.add((i, j))
    return fire_cells


def predict_next_day_fires(fire_cells, rows, cols, wind="E"):
    predicted = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Prioritize wind direction (e.g., wind="E" favors east spread)
    wind_boost = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
    wind_dir = wind_boost.get(wind.upper(), (0, 1))
    directions.insert(0, wind_dir)

    for i, j in fire_cells:
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < rows and 0 <= nj < cols and (ni, nj) not in fire_cells:
                predicted.add((ni, nj))
    return predicted


def add_fire_animation(m, fire_data, predicted_cells, lat_range, lon_range, rows, cols):
    lat_start, lat_end = lat_range
    lon_start, lon_end = lon_range
    lat_step = (lat_end - lat_start) / rows
    lon_step = (lon_end - lon_start) / cols

    features = []

    # 🔥 Group real fire data by date
    grouped = fire_data.groupby("acq_date")
    for date, group in grouped:
        for _, row in group.iterrows():
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['longitude'], row['latitude']],
                },
                "properties": {
                    "time": date,
                    "style": {"color": "red"},
                    "icon": "circle",
                    "popup": f"Confirmed Fire 🔴 ({date})"
                }
            })

    # 🔥 Add predicted fires on the next day after latest real fire date
    if not fire_data.empty:
        last_date = pd.to_datetime(fire_data['acq_date'].max())
        predicted_date = (last_date + pd.Timedelta(days=1)).date().isoformat()
    else:
        predicted_date = datetime.date.today().isoformat()

    for i, j in predicted_cells:
        lat = lat_start + (i + 0.5) * lat_step
        lon = lon_start + (j + 0.5) * lon_step
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "time": predicted_date,
                "style": {"color": "orange"},
                "icon": "circle",
                "popup": f"Predicted Fire 🟠 ({predicted_date})"
            }
        })

    TimestampedGeoJson({
        "type": "FeatureCollection",
        "features": features,
    },
        period="P1D",
        add_last_point=True,
        auto_play=True,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options="YYYY-MM-DD",
        time_slider_drag_update=True
    ).add_to(m)


def main():
    print("📡 Fetching FIRMS fire data...")
    df = fetch_fire_data(FIRMS_URL)
    print(f"🔥 Retrieved {len(df)} fire hotspots.")

    fire_cells = get_fire_grid_cells(
        df, LAT_RANGE, LON_RANGE, GRID_ROWS, GRID_COLS)
    predicted_cells = predict_next_day_fires(
        fire_cells, GRID_ROWS, GRID_COLS, wind="E")

    m = folium.Map(location=MAP_CENTER, zoom_start=5, tiles="cartodbpositron")

    # Add India boundary
    india_geojson = requests.get(INDIA_GEOJSON_URL).json()
    folium.GeoJson(india_geojson, name="India").add_to(m)

    # Draw grid and fire markers
    draw_grid(m, LAT_RANGE, LON_RANGE, GRID_ROWS, GRID_COLS)
    add_fire_animation(m, df, predicted_cells,
                       LAT_RANGE, LON_RANGE, GRID_ROWS, GRID_COLS)

    # Save the map
    m.save(MAP_FILENAME)

    # === 🔥 Inject Animation CSS and JS into HTML ===
    with open(MAP_FILENAME, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # CSS for animation 🔴
    style_tag = soup.new_tag("style")
    style_tag.string = """
    .pulse {
        width: 20px;
        height: 20px;
        background: red;
        border-radius: 50%;
        box-shadow: 0 0 10px red;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }
    """
    soup.head.append(style_tag)

    # JavaScript to create pulsing markers
    script_tag = soup.new_tag("script")
    script_tag.string = """
    function addPulse(lat, lon) {
        const divIcon = L.divIcon({
            className: '',
            html: '<div class="pulse"></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10],
        });

        const marker = L.marker([lat, lon], { icon: divIcon });
        marker.addTo(window._mapInstance || document.querySelector('.leaflet-container')._leaflet_map);
    }

    const fireData = [
        { latitude: 24.5, longitude: 78.4 },
        { latitude: 25.2, longitude: 78.8 },
        { latitude: 22.7, longitude: 80.1 },
        { latitude: 23.9, longitude: 79.5 }
    ];

    fireData.forEach(d => addPulse(d.latitude, d.longitude));
    """
    soup.body.append(script_tag)

    # Write updated HTML back
    with open(MAP_FILENAME, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"✅ Fire simulation map saved to: {MAP_FILENAME} (with animation!)")


if __name__ == '__main__':
    main()
