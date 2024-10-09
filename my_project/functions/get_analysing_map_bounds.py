# Імпортуємо необхідні бібліотеки для роботи з файлами та візуалізації
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point


def get_analysing_map_bounds(some_type_coords):
    if isinstance(some_type_coords, pd.DataFrame):
        # Створюємо геометричні об'єкти для популяцій
        some_type_coords['geometry'] = some_type_coords.apply(lambda row: Point(row['lon'], row['lat']), axis=1)

        # Перетворимо DataFrame на GeoDataFrame для візуалізації на карті
        gdf_population = gpd.GeoDataFrame(some_type_coords, geometry='geometry')

        return gdf_population.total_bounds

    if isinstance(some_type_coords, np.ndarray):
        x_min = min(coord[0] for coord in some_type_coords)
        x_max = max(coord[0] for coord in some_type_coords)
        y_min = min(coord[1] for coord in some_type_coords)
        y_max = max(coord[1] for coord in some_type_coords)

        return x_min, x_max, y_min, y_max
