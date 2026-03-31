def parse_schedule(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    trips = []

    rows = soup.select("table tr")

    for row in rows:
        cols = [c.text.strip() for c in row.find_all("td")]

        if len(cols) > 3:
            trips.append(cols)

    return trips