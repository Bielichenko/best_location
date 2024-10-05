# Імпортуємо необхідні бібліотеки для роботи з файлами та візуалізації
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import requests
import pandas as pd
from temabit_project.find_best_location.best_location_model import optimal_locations

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

# Send the request to the Overpass API
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Extract the relevant information (name, latitude, longitude)
all_stores = []
for element in data['elements']:
    if 'tags' in element and ('lat' in element or 'center' in element):
        name = element['tags'].get('name', 'Unnamed')
        if 'lat' in element and 'lon':
            lat, lon = element['lat'], element['lon']
        elif 'center' in element:
            lat, lon = element['center']['lat'], element['center']['lon']
        all_stores.append([name, lat, lon])

# Фільтруємо записи, де назва магазину не дорівнює "Сільпо"
competitors_stores = [store for store in all_stores if store[0] != "Сільпо"]

# Перетворюємо на DataFrame
competitors_stores_df = pd.DataFrame(competitors_stores, columns=['Name', 'Latitude', 'Longitude'])

# Завантажимо файл із даними
file_path = 'Test.xlsx'
population_data = pd.read_excel(file_path, sheet_name='Population')
stores_data = pd.read_excel(file_path, sheet_name='Stores')

# Створюємо геометричні об'єкти для магазинів і популяцій
population_data['geometry'] = population_data.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
stores_data['geometry'] = stores_data.apply(lambda row: Point(row['long'], row['lat']), axis=1)

# Перетворимо DataFrame на GeoDataFrame для візуалізації на карті
gdf_population = gpd.GeoDataFrame(population_data, geometry='geometry')
gdf_stores = gpd.GeoDataFrame(stores_data, geometry='geometry')

# Створюємо конкурентів із даних Overpass API
# competitors_stores_df['geometry'] = competitors_stores_df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
# gdf_competitors = gpd.GeoDataFrame(competitors_stores_df, geometry='geometry')

# ---- Додавання координат для зірочок ----
# Координати, які ви хочете візуалізувати як зірочки
print(optimal_locations[0][1])
star_coords = [(optimal_locations[0][1])]  # Приклад координат, додайте свої

# Створюємо GeoDataFrame для зірочок
gdf_stars = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lat, lon in star_coords])

# Створюємо графік
fig, ax = plt.subplots(figsize=(10, 10))

# Візуалізуємо популяції з кольоровою шкалою на основі метрики популяцій
norm = plt.Normalize(vmin=population_data['metric population'].min(), vmax=population_data['metric population'].max())
sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
gdf_population.plot(ax=ax, marker='o', color=sm.to_rgba(population_data['metric population']), markersize=5)

# Нормалізуємо метрику магазину для більш очевидної різниці в розмірах хрестиків
norm_store_metric = (stores_data['Metric Store'] - stores_data['Metric Store'].min()) / (stores_data['Metric Store'].max() - stores_data['Metric Store'].min())

# Візуалізуємо магазини хрестиками, розмір яких залежить від нормалізованої метрики магазину
gdf_stores.plot(ax=ax, marker='x', color='red', markersize=norm_store_metric * 50, label='Silpo')

# Візуалізуємо конкуренти як рожеві хрестики
# gdf_competitors.plot(ax=ax, marker='x', color='magenta', markersize=30, label='Competitors')

# ---- Візуалізуємо зірочки ----
gdf_stars.plot(ax=ax, marker='*', color='gold', markersize=100, label='Stars')

# Додаємо легенду
plt.colorbar(sm, ax=ax, label='Population Metric')
plt.title('Stores, Competitors, and Population Metrics in Kyiv')
plt.legend()

plt.show()