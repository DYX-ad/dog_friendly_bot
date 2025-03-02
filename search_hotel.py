import requests


def get_nearby_hotels(location, radius):
    lat, lon = location
    overpass_url = "http://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    node["tourism"="hotel"](around:{radius},{lat},{lon});
    node["pets"="yes"](around:{radius},{lat},{lon});  // Отели, где можно с животными
    out body;
    """

    response = requests.get(overpass_url, params={'data': query})
    places = response.json().get("elements", [])

    nearby_places = set()  # Используем множество для хранения уникальных мест
    for place in places[:3]:  # Берем только первые 3 уникальных места
        name = place.get("tags", {}).get("name", "Без названия")
        lat = place["lat"]
        lon = place["lon"]
        nearby_places.add((name, lat, lon))  # Добавляем место в множество, чтобы избежать дублей

    return list(nearby_places)  # Преобразуем множество обратно в список для работы
