
import folium
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import box, Point
from my_project.global_data import silpo_stores_data, population_data, all_population_data
import folium
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import box, Point
from folium.plugins import MarkerCluster
from my_project.global_data import population_data, all_population_data
from my_project.functions import get_analysing_area_bounds
import webbrowser
import tempfile
import branca

def show_best_location(star_coords, competitors_stores):
    print('competitors_stores', competitors_stores)
    """
    Візуалізує популяційні метрики у вигляді квадратної сітки на Folium і відображає спеціальну точку (зірочку).
    Додає на карту магазини "Сільпо" та конкурентів із використанням простих маркерів.

    Args:
        star_coords (tuple): Координати для відображення зірочки (широта, довгота).
        silpo_stores_data (pd.DataFrame): Дані про магазини "Сільпо" з колонками "Store", "lat", "long".
        competitors_stores (list): Лист з підлистів, кожен підлист містить [shop_name, lat, lon].

    Returns:
        None: Функція відображає карту в браузері.
    """

    # Перетворюємо population_data на GeoDataFrame для використання методів GeoPandas
    population_data['geometry'] = population_data.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    gdf_population = gpd.GeoDataFrame(population_data, geometry='geometry')

    # Визначаємо межі для розбиття на квадрати
    xmin, ymin, xmax, ymax = get_analysing_area_bounds(all_population_data)

    # Розмір квадрата (0.5 км ≈ 0.0045 градусів широти і довготи)
    grid_size = 0.0045

    # Створюємо список квадратів
    grid_cells = []
    for x0 in np.arange(xmin, xmax, grid_size):
        for y0 in np.arange(ymin, ymax, grid_size):
            x1 = x0 + grid_size
            y1 = y0 + grid_size
            grid_cells.append(box(x0, y0, x1, y1))

    # Функція для обчислення кількості популяції для кожного квадрата
    def calculate_population_sum_in_square(square, population_data):
        mask = population_data.within(square)
        return population_data[mask]['metric population'].sum()

    # Створюємо список для зберігання результатів
    grid_population = []

    # Обчислюємо суму метрик популяції для кожного квадрата і зберігаємо результат
    for square in grid_cells:
        population_sum = calculate_population_sum_in_square(square, gdf_population)
        grid_population.append({
            'geometry': square,
            'population': population_sum
        })

    # Створюємо GeoDataFrame для збереження даних квадратів
    gdf_grid = gpd.GeoDataFrame(grid_population)

    # Створюємо карту Folium, зосереджену на певній області
    folium_map = folium.Map(location=[(ymin + ymax) / 2, (xmin + xmax) / 2], zoom_start=13)

    # Підготовка колірної шкали
    min_population = gdf_grid['population'].min()
    max_population = gdf_grid['population'].max()
    colormap = branca.colormap.LinearColormap(
        colors=['blue', 'yellow', 'red'],
        vmin=min_population,
        vmax=max_population,
        caption="Population per Square"
    )
    colormap.add_to(folium_map)

    # Додаємо кожен квадрат на карту з відповідним кольором
    for _, row in gdf_grid.iterrows():
        folium.GeoJson(
            row['geometry'].__geo_interface__,
            style_function=lambda x, population=row['population']: {
                'fillColor': colormap(population),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.6
            }
        ).add_to(folium_map)

    # Додаємо зірочку на карту
    folium.Marker(
        location=[float(star_coords[0]), float(star_coords[1])],
        popup="Optimal Location",
        icon=folium.Icon(icon='star', color='orange')
    ).add_to(folium_map)

    # Додаємо магазини "Сільпо" на карту з простими маркерами (червоні маркери)
    for _, store in silpo_stores_data.iterrows():
        folium.CircleMarker(
            location=[float(store['lat']), float(store['long'])],  # Конвертуємо в float
            radius=10,  # Розмір маркера для магазинів "Сільпо"
            popup=f"Silpo Store {store['Store']}",
            color='red',
            fill=False,
            fill_color='gray'
        ).add_to(folium_map)

    # Додаємо конкурентів на карту з простими маркерами (сірі маркери, трохи більші)
    for competitor in competitors_stores:
        shop_name, lat, lon = competitor
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=7,  # Трохи більший розмір маркера для конкурентів
            popup=f"Competitor {shop_name}",
            color='green',
            fill=False,
            fill_color='gray'
        ).add_to(folium_map)

    # Створюємо тимчасовий файл для зберігання HTML-коду
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
        folium_map.save(tmp_file.name)  # Зберігаємо карту в тимчасовий файл
        webbrowser.open(f'file://{tmp_file.name}')  # Відкриваємо карту в браузері


