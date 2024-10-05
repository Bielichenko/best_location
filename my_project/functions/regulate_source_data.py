import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon


# Функція для видалення популяції у певному секторі
def regulate_source_data(population_data, sector_coords):
    print(len(population_data), 'before')
    """
    Видаляє популяцію, яка знаходиться в заданому секторі, за допомогою геометричних операцій.

    Parameters:
    population_data: DataFrame - дані про популяцію
    sector_coords: tuple - координати сектору у форматі (lat_min, lat_max, lon_min, lon_max)

    Returns:
    population_data: DataFrame - оновлені дані про популяцію
    """

    lat_min, lat_max, lon_min, lon_max = sector_coords
    print(lat_min, lat_max, lon_min, lon_max, 'lat_min, lat_max, lon_min, lon_max')

    # Створюємо полігон для сектора
    sector_polygon = Polygon([
        (lon_min, lat_min),  # нижній лівий кут
        (lon_max, lat_min),  # нижній правий кут
        (lon_max, lat_max),  # верхній правий кут
        (lon_min, lat_max),  # верхній лівий кут
        (lon_min, lat_min)  # замкнути полігон
    ])

    # Створюємо геометричні точки для кожної популяції
    population_data['geometry'] = population_data.apply(lambda row: Point(row['lon'], row['lat']), axis=1)

    # Перетворюємо DataFrame в GeoDataFrame
    gdf_population = gpd.GeoDataFrame(population_data, geometry='geometry')

    # Фільтруємо тільки ті точки, що не знаходяться в секторі (видаляємо популяцію всередині сектора)
    population_filtered = gdf_population[~gdf_population.within(sector_polygon)]

    # Повертаємо DataFrame без геометричної колонки
    print(len(population_data), 'after')
    return population_filtered.drop(columns='geometry')