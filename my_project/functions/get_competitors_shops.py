import requests

def get_competitors_shops():
    # Overpass API URL
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Overpass query to get all grocery stores, supermarkets, convenience stores, and markets in Kyiv
    overpass_query = """
    [out:json];
    area[name="Київ"]->.kyiv;
    (
      node["shop"="supermarket"](area.kyiv);
      way["shop"="supermarket"](area.kyiv);
    );
    out center;
    """

    # node["shop"="grocery"](area.kyiv);
    #   node["shop"="convenience"](area.kyiv);
    #   node["shop"="farm"](area.kyiv);
    #   node["shop"="greengrocer"](area.kyiv);
    # node["shop"="grocery"](area.kyiv);
    # way["shop"="grocery"](area.kyiv);
    #   way["shop"="convenience"](area.kyiv);
    #   way["shop"="farm"](area.kyiv);
    #   way["shop"="greengrocer"](area.kyiv);

    # Send the request to the Overpass API
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    # Extract the relevant information (name, latitude, longitude)
    competitors_stores = []
    # print(data['elements'][1])
    for element in data['elements']:
        if 'tags' in element and ('lat' in element or 'center' in element):
            name = element['tags'].get('name', 'Unnamed')
            if 'lat' in element and 'lon':
                lat, lon = element['lat'], element['lon']
            elif 'center' in element:
                lat, lon = element['center']['lat'], element['center']['lon']
            if name != 'Сільпо':
                competitors_stores.append([name, lat, lon])


    # print('all_stores', len(all_stores))

    # Фільтруємо записи, де назва магазину не дорівнює "Сільпо"

    # print('competitors_stores', len(competitors_stores))
    # print(competitors_stores, 'competitors_stores')

    print('get_competitors_shops competitors_stores :', competitors_stores)

    return competitors_stores
# print(len(get_competitors_shops()))