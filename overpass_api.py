import requests


# Функция для получения ближайших мест через OpenStreetMap (Overpass API)
def get_nearby_places(location, place_type):
    lat, lon = location
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Формируем запрос для поиска кафе, отелей или питомников
    if place_type == "cafe":
        query = f"""
        [out:json];
        node["amenity"="cafe"](around:5000,{lat},{lon});
        out body;
        """
    elif place_type == "hotel":
        query = f"""
        [out:json];
        node["tourism"="hotel"](around:5000,{lat},{lon});
        out body;
        """
    elif place_type == "petshop":
        query = f"""
        [out:json];
        node["shop"="pet"](around:5000,{lat},{lon});
        out body;
        """

    response = requests.get(overpass_url, params={'data': query})
    places = response.json().get("elements", [])

    nearby_places = []
    for place in places[:3]:  # Берем только первые 3 места
        name = place.get("tags", {}).get("name", "Без названия")
        lat = place["lat"]
        lon = place["lon"]
        nearby_places.append((name, lat, lon))

    return nearby_places
