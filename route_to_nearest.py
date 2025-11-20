import csv
import requests
from math import radians, cos, sin, sqrt, atan2

ORS_URL = "http://localhost:8080/ors/v2/matrix/driving-car"

def haversine(lon1, lat1, lon2, lat2):
    R = 6371
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

centroids = []
hospitals = []

with open("centroids_points.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        centroids.append((float(row["X"]), float(row["Y"])))

with open("hospitals_points.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        hospitals.append((float(row["X"]), float(row["Y"])))

results = []

for i, (cx, cy) in enumerate(centroids):
    print(f"Processing centroid {i+1}/{len(centroids)}")

    # Find 20 nearest hospitals (by straight-line distance)
    distances = []
    for hx, hy in hospitals:
        d = haversine(cx, cy, hx, hy)
        distances.append((d, hx, hy))

    distances.sort()
    nearest = distances[:20]

    coords = [[cx, cy]] + [[hx, hy] for _, hx, hy in nearest]

    body = {
        "locations": coords,
        "metrics": ["duration"]
    }

    r = requests.post(ORS_URL, json=body)
    data = r.json()

    if "durations" not in data:
        print("ORS error for centroid", i)
        continue

    times = data["durations"][0][1:]
    min_time = min(times)

    results.append((cx, cy, min_time))

with open("travel_time_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["X", "Y", "min_time_sec"])
    writer.writerows(results)
