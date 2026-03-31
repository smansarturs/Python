import requests

def geocode(stop_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": stop_name + ", Jelgava, Latvia",
        "format": "json"
    }

    r = requests.get(url, params=params).json()

    if r:
        return r[0]["lat"], r[0]["lon"]

    return None, None