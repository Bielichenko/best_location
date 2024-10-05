# Імпортуємо необхідні бібліотеки для роботи з файлами та візуалізації

# Імпортуємо необхідні бібліотеки для роботи з файлами та візуалізації

# Імпортуємо необхідні бібліотеки для роботи з файлами та візуалізації
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, box
from my_project.global_data import population_data, silpo_stores_data, all_population_data
from my_project.functions import get_analysing_area_bounds
from my_project.find_best_locations.find_best_locations import find_optimal_location


def show_best_location_old(star_coords):
    """
    Візуалізує популяційні метрики у вигляді сітки, відображає магазини і спеціальну точку (зірочку).

    Args:
        star_coords (tuple): Координати для відображення зірочки (широта, довгота).

    Returns:
        None: Функція відображає карту з візуалізацією.
    """

    # Створюємо геометричні об'єкти для популяцій
    population_data['geometry'] = population_data.apply(lambda row: Point(row['lon'], row['lat']), axis=1)

    # Перетворимо DataFrame на GeoDataFrame для візуалізації на карті
    gdf_population = gpd.GeoDataFrame(population_data, geometry='geometry')

    # Створимо геометричні об'єкти для магазинів
    silpo_stores_data['geometry'] = silpo_stores_data.apply(lambda row: Point(row['long'], row['lat']), axis=1)

    # Перетворимо DataFrame магазинів на GeoDataFrame
    gdf_stores = gpd.GeoDataFrame(silpo_stores_data, geometry='geometry')

    # Визначимо межі для розбиття на квадрати
    xmin, ymin, xmax, ymax = get_analysing_area_bounds(all_population_data)

    # Розмір квадрата (1 км ≈ 0.009 градусів широти і довготи)
    grid_size = 0.0045

    # Створимо список квадратів
    grid_cells = []
    for x0 in np.arange(xmin, xmax, grid_size):
        for y0 in np.arange(ymin, ymax, grid_size):
            x1 = x0 + grid_size
            y1 = y0 + grid_size
            grid_cells.append(box(x0, y0, x1, y1))

    # Створюємо GeoDataFrame для квадратів
    grid = gpd.GeoDataFrame(grid_cells, columns=['geometry'])

    # Функція для обчислення суми метрик популяції для кожного квадрата
    def calculate_population_sum_in_square(square, population_data):
        mask = population_data.within(square)
        return population_data[mask]['metric population'].sum()

    # Обчислюємо суму метрик популяції для кожного квадрата
    grid['population_sum'] = grid.apply(lambda row: calculate_population_sum_in_square(row['geometry'], gdf_population),
                                        axis=1)

    # Створимо GeoDataFrame для зірочки
    gdf_star = gpd.GeoDataFrame(geometry=[Point(star_coords[1], star_coords[0])], crs=gdf_population.crs)

    # Створюємо графік
    fig, ax = plt.subplots(figsize=(10, 10))

    # Візуалізуємо квадрати з кольоровою шкалою на основі суми метрик популяції
    norm = plt.Normalize(vmin=grid['population_sum'].min(), vmax=grid['population_sum'].max())
    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=norm)

    # Відображаємо квадрати
    grid.plot(ax=ax, edgecolor='black', facecolor=sm.to_rgba(grid['population_sum']))

    # Відображаємо зірочку на зазначеній парі координат
    gdf_star.plot(ax=ax, marker='*', color='gold', markersize=200, label='Star')

    # Відображаємо магазини на карті (червоні кружки)
    gdf_stores.plot(ax=ax, marker='o', color='red', markersize=25, label='Stores')

    # Додаємо легенду
    plt.colorbar(sm, ax=ax, label='Total Population Metric in Square')
    plt.title('Population Density by Grid with Highlighted Star and Stores')

    plt.legend()
    plt.show()