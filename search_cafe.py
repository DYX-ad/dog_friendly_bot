import requests


def get_nearby_cafes(location, radius):
    lat, lon = location
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Запрос для поиска кафе, ресторанов и баров без фильтров
    query = f"""
    [out:json];
    node["amenity"="cafe"](around:{radius},{lat},{lon});
    node["amenity"="restaurant"](around:{radius},{lat},{lon});
    node["amenity"="bar"](around:{radius},{lat},{lon});
    out body;
    """

    response = requests.get(overpass_url, params={'data': query})
    places = response.json().get("elements", [])

    # Используем списки для категорий, чтобы не смешивать их
    cafes = set()
    restaurants = set()
    bars = set()

    for place in places:
        name = place.get("tags", {}).get("name", "Без названия")
        lat = place["lat"]
        lon = place["lon"]
        amenity = place["tags"].get("amenity", "Unknown")

        # Определяем, к какой категории принадлежит заведение
        if amenity == "cafe" and (lat, lon) not in cafes:
            cafes.add((name, "Кафе", lat, lon))
        elif amenity == "restaurant" and (lat, lon) not in restaurants:
            restaurants.add((name, "Ресторан", lat, lon))
        elif amenity == "bar" and (lat, lon) not in bars:
            bars.add((name, "Бар", lat, lon))

    # Объединяем все уникальные места и ограничиваем их до 3
    unique_places = list(cafes | restaurants | bars)[:3]  # Ограничиваем результат до 3 мест

    return unique_places
