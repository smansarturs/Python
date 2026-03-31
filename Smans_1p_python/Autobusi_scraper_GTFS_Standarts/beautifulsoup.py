import requests
from bs4 import BeautifulSoup

url = "https://www.jap.lv/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

# atrodam visas saites
for a in soup.find_all("a"):
    print(a.get_text(strip=True), a.get("href"))