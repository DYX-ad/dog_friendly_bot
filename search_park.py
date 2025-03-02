import requests


def get_nearby_parks(location, radius):
    lat, lon = location
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Запрос для поиска парков, включая натуральные парки и леса
    query = f"""
    [out:json];
    node["leisure"="park"](around:{radius},{lat},{lon});
    node["natural"="park"](around:{radius},{lat},{lon});
    node["landuse"="forest"](around:{radius},{lat},{lon});
    out body;
    """

    response = requests.get(overpass_url, params={'data': query})
    places = response.json().get("elements", [])

    parks = set()  # Множество для хранения уникальных парков

    for place in places:
        name = place.get("tags", {}).get("name", "Без названия")
        lat = place["lat"]
        lon = place["lon"]

        # Определяем тип парка (парк, лес)
        if "natural" in place["tags"] and place["tags"]["natural"] == "park":
            category = "Натуральный Парк"
        elif "landuse" in place["tags"] and place["tags"]["landuse"] == "forest":
            category = "Лес"
        else:
            category = "Парк"

        # Добавляем уникальные парки
        parks.add((name, category, lat, lon))

    # Ограничиваем до 3 парков
    return list(parks)[:3]
