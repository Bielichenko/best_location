import requests


# Використовуємо публічну АПІ для отримання магазинів конкурентів
def get_competitors_shops():
    # API URL
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Запит на всі супермаркети Києва
    overpass_query = """
    [out:json];
    area[name="Київ"]->.kyiv;
    (
      node["shop"="supermarket"](area.kyiv);
      way["shop"="supermarket"](area.kyiv);
    );
    out center;
    """

    # Кидаємо запит на АПІ
    response = requests.get(overpass_url, params={"data": overpass_query})
    data = response.json()

    # Витягуємо всю необхідну інфу про всі супермаркети окрім Сільпо
    competitors_stores = []

    for element in data["elements"]:
        if "tags" in element and ("lat" in element or "center" in element):
            name = element["tags"].get("name", "Unnamed")
            if "lat" in element and "lon":
                lat, lon = element["lat"], element["lon"]
            elif "center" in element:
                lat, lon = element["center"]["lat"], element["center"]["lon"]
            if name != "Сільпо":
                competitors_stores.append([name, lat, lon])

    return competitors_stores
