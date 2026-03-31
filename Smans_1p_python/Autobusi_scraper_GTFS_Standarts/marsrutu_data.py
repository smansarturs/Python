import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.jap.lv/"
ROUTES_PAGE = BASE_URL + "/m/"

def get_routes():
    r = requests.get(ROUTES_PAGE)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    
    routes = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href")
        # parasti maršruti sākas ar ciparu un punktu
        if text and text[0].isdigit() and href:
            routes.append({
                "route_id": text.split(".")[0],
                "route_name": text,
                "url": BASE_URL + href
            })
    return routes

routes = get_routes()
for r in routes:
    print(r)