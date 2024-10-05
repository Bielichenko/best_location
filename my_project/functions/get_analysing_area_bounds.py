# Імпортуємо необхідні бібліотеки для роботи з файлами та візуалізації
import geopandas as gpd
from shapely.geometry import Point, box

def get_analysing_area_bounds(coords_data):
    # Створюємо геометричні об'єкти для популяцій
    coords_data['geometry'] = coords_data.apply(lambda row: Point(row['lon'], row['lat']), axis=1)

    # Перетворимо DataFrame на GeoDataFrame для візуалізації на карті
    gdf_population = gpd.GeoDataFrame(coords_data, geometry='geometry')

    # # Визначимо межі для розбиття на квадрати
    # xmin, ymin, xmax, ymax = gdf_population.total_bounds

    return gdf_population.total_bounds
