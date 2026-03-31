import requests
from bs4 import BeautifulSoup
import pandas as pd
import zipfile

# AUTOBUSU PARKA BASE URL
BASE_URL = "https://www.jap.lv/"

# ---- Maršrutu iegūšana ----
def get_routes():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    routes = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href")
        if text and text[0].isdigit() and href:
            routes.append({
                "route_id": text.split(".")[0],
                "route_name": text,
                "url": "https://www.jap.lv/" + href
            })
    return routes

# ---- Grafika parsing ----
def parse_route(route):
    r = requests.get(route["url"])
    soup = BeautifulSoup(r.text, "html.parser")
    trips = []
    trip_counter = 0
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        stop_names = []
        time_matrix = []
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) > 1:
                stop_names.append(cols[0])
                time_matrix.append(cols[1:])
        if not time_matrix:
            continue
        num_trips = len(time_matrix[0])
        for col in range(num_trips):
            trip_id = f"{route['route_id']}_{trip_counter}"
            seq = 1
            for i, stop in enumerate(stop_names):
                try:
                    time_val = time_matrix[i][col]
                except:
                    continue
                if ":" in time_val:
                    trips.append({
                        "trip_id": trip_id,
                        "stop_name": stop,
                        "arrival_time": format_time(time_val),
                        "departure_time": format_time(time_val),
                        "stop_sequence": seq
                    })
                    seq += 1
            trip_counter += 1
    return trips

def format_time(t):
    h, m = t.split(":")
    return f"{int(h):02}:{m}:00"

# ---- GTFS builder ----
def build_gtfs(routes, all_trips):
    routes_df = pd.DataFrame([{
        "route_id": r["route_id"],
        "route_short_name": r["route_id"],
        "route_long_name": r["route_name"],
        "route_type": 3
    } for r in routes])

    stop_names = sorted(set(t["stop_name"] for t in all_trips))
    stops_df = pd.DataFrame([{
        "stop_id": f"S{i}",
        "stop_name": name,
        "stop_lat": 0.0,
        "stop_lon": 0.0
    } for i, name in enumerate(stop_names)])
    stop_map = dict(zip(stops_df.stop_name, stops_df.stop_id))

    stop_times_df = pd.DataFrame([{
        "trip_id": t["trip_id"],
        "arrival_time": t["arrival_time"],
        "departure_time": t["departure_time"],
        "stop_id": stop_map[t["stop_name"]],
        "stop_sequence": t["stop_sequence"]
    } for t in all_trips])

    trip_ids = set(t["trip_id"] for t in all_trips)
    trips_df = pd.DataFrame([{
        "route_id": tid.split("_")[0],
        "service_id": "WEEKDAY",
        "trip_id": tid
    } for tid in trip_ids])

    calendar_df = pd.DataFrame([{
        "service_id": "WEEKDAY",
        "monday": 1,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 0,
        "sunday": 0,
        "start_date": 20260101,
        "end_date": 20261231
    }])

    return routes_df, stops_df, stop_times_df, trips_df, calendar_df

# ---- Saglabā GTFS ZIP ----
def save_gtfs(files):
    names = ["routes.txt", "stops.txt", "stop_times.txt", "trips.txt", "calendar.txt"]
    for df, name in zip(files, names):
        df.to_csv(name, index=False)
    with zipfile.ZipFile("gtfs.zip", "w") as z:
        for name in names:
            z.write(name)

# ---- Main ----
def main():
    routes = get_routes()
    all_trips = []
    for r in routes:
        print("Parsing:", r["route_name"])
        trips = parse_route(r)
        all_trips.extend(trips)
    gtfs_files = build_gtfs(routes, all_trips)
    save_gtfs(gtfs_files)
    print("✅ GTFS gatavs: gtfs.zip")

if __name__ == "__main__":
    main()