import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from my_project.global_data import population_data, silpo_stores_data
from my_project.functions import calculate_pop_rel_weight_by_dist
from my_project.functions import get_competitors_shops
# from my_project.visualizations import show_best_location


# Функція для завантаження та підготовки даних
def load_and_prepare_data():
    # Приведення даних до числових значень і перетворення в списки координат
    population_data['lat'] = pd.to_numeric(population_data['lat'], errors='coerce')
    population_data['lon'] = pd.to_numeric(population_data['lon'], errors='coerce')
    silpo_stores_data['lat'] = pd.to_numeric(silpo_stores_data['lat'], errors='coerce')
    silpo_stores_data['long'] = pd.to_numeric(silpo_stores_data['long'], errors='coerce')

    other_competitors_shops = get_competitors_shops()

    # Фільтрація рядків без координат
    population_data_filtered = population_data.dropna(subset=['lat', 'lon'])
    population_coords = population_data_filtered[['lat', 'lon']].values
    metric_population = population_data_filtered['metric population'].values

    # Фільтруємо дані про магазини
    silpo_stores_data_filtered = silpo_stores_data.dropna(subset=['lat', 'long'])
    silpo_stores_coords = silpo_stores_data_filtered[['lat', 'long']].values
    silpo_stores_coords_with_corp_name = [["Silpo", lat, lon,] for lat, lon in silpo_stores_coords]

    silpo_and_other_corps_shops = silpo_stores_coords_with_corp_name + other_competitors_shops

    all_population_data = pd.read_excel('./data_sets/Test.xlsx', sheet_name='Population')
    all_population_coords = all_population_data[['lat', 'lon']].values

    return population_coords, silpo_and_other_corps_shops, all_population_coords, metric_population


# Функція для обчислення евклідових відстаней між всіма популяціями та конкурентами
def calculate_distance_matrix(population_coords, competitor_coords):
    pop_coords_array = np.array(population_coords)

    # Якщо конкурентних магазинів немає, повертаємо порожню матрицю відстаней
    if len(competitor_coords) == 0:
        return np.zeros((len(population_coords), 0))  # Матриця відстаней з нульовою кількістю колонок

    # Створюємо два масиви (широта і довгота) в одному циклі
    comp_latitudes, comp_longitudes = np.array([
        (coord[1], coord[2]) for coord in competitor_coords
    ], dtype=float).T  # Транспонування для розділення на широти і довготи

    # Обчислення різниці в координатах
    lat_diff = (pop_coords_array[:, 0, np.newaxis] - comp_latitudes) * 111
    lon_diff = (pop_coords_array[:, 1, np.newaxis] - comp_longitudes) * 111 * np.cos(
        np.radians(pop_coords_array[:, 0, np.newaxis]))

    # Обчислення Евклідової відстані
    distance_matrix = np.sqrt(lat_diff ** 2 + lon_diff ** 2)

    return distance_matrix


# Використовуємо попередньо обчислену матрицю відстаней для розрахунку впливу конкурентів
def calculate_other_shops_effect(distance_matrix, silpo_and_other_corps_shops, alpha=1, silpo_boost=2):
    """
    distance_matrix: матриця відстаней
    silpo_and_other_corps_shops: список конкурентів з назвою магазину, широтою та довготою
    alpha: коефіцієнт згасання
    silpo_boost: коефіцієнт збільшення впливу для магазинів "Сільпо"
    """

    # Визначаємо, чи є магазин "Сільпо"
    is_silpo = [shop[0] == "Silpo" for shop in silpo_and_other_corps_shops]  # Якщо назва магазину містить "Сільпо"

    # Обчислюємо базовий вплив для всіх магазинів
    impact_matrix = 1 / (1 + np.log10(1 + distance_matrix) * distance_matrix ** alpha)

    # Збільшуємо вплив для магазинів "Сільпо" за допомогою silpo_boost
    impact_matrix[:, is_silpo] *= 2  # Застосовуємо коефіцієнт до колонок, де магазини "Сільпо"

    # Сумуємо впливи по всіх конкурентних магазинах для кожної популяції
    pop_total_impact = np.sum(impact_matrix, axis=1)

    # Нормалізуємо значення, якщо максимальний вплив більше за 1
    max_impact = np.max(pop_total_impact)
    if max_impact > 1:
        pop_total_impact /= max_impact

    return pop_total_impact



# Функція для обчислення загального зваженого попиту
def calculate_total_weighted_demand(store_coord, population_coords, distance_matrix, competitor_impact, alpha=1):
    lat_diff = (population_coords[:, 0] - store_coord[0]) * 111
    lon_diff = (population_coords[:, 1] - store_coord[1]) * 111 * np.cos(np.radians(population_coords[:, 0]))
    distances_to_store = np.sqrt(lat_diff ** 2 + lon_diff ** 2)

    pop_rel_weight_by_dist = calculate_pop_rel_weight_by_dist(distances_to_store)
    weighted_pop_demand = pop_rel_weight_by_dist * (1 - competitor_impact)

    return np.sum(weighted_pop_demand)


# Функція для пошуку оптимальних локацій
def find_optimal_location(population_coords, competitor_coords, all_population_coords, alpha=1, step_size=0.001, max_workers=8):
    x_min = min(coord[0] for coord in all_population_coords)
    x_max = max(coord[0] for coord in all_population_coords)
    y_min = min(coord[1] for coord in all_population_coords)
    y_max = max(coord[1] for coord in all_population_coords)

    distance_matrix = calculate_distance_matrix(population_coords, competitor_coords)
    competitor_impact = calculate_other_shops_effect(distance_matrix, competitor_coords, alpha)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_location = {}
        for y in np.arange(y_max, y_min, -step_size):
            for x in np.arange(x_min, x_max, step_size):
                store_coord = (x, y)
                future = executor.submit(calculate_total_weighted_demand, store_coord, population_coords, distance_matrix, competitor_impact, alpha)
                future_to_location[future] = store_coord

        for future in as_completed(future_to_location):
            try:
                total_weighted_demand = future.result()
                store_coord = future_to_location[future]
                results.append([total_weighted_demand, store_coord])
            except Exception as e:
                print(f"Error in task: {e}")

    results_sorted = sorted(results, key=lambda x: x[0], reverse=True)
    return results_sorted[:100]


# Функція для збереження результатів у Excel
def save_optimal_locations_to_excel(optimal_locations, output_path):
    optimal_locations_df = pd.DataFrame(optimal_locations, columns=['Total Weighted Demand', 'Coords'])
    optimal_locations_df.to_excel(output_path + 'new_store_best_locations.xlsx', index=False)
    print('Файл з координатами успішно записан!')


# Функція для виведення результатів
def print_optimal_locations(optimal_locations):
    print("Топ 10 найкращих локацій:")
    for idx, location in enumerate(optimal_locations[:10], 1):
        demand = round(location[0], 3)
        lat, lon = location[1]
        print(f"{idx}. Попит: {demand}, Координати: (Широта: {lat:.6f}, Довгота: {lon:.6f})")


# Основна функція для виклику з основного файлу проекту
def find_best_locations():
    # Завантаження і підготовка даних
    population_coords, competitor_coords, all_population_coords, metric_population = load_and_prepare_data()

    # Пошук оптимальних локацій
    optimal_locations = find_optimal_location(population_coords, competitor_coords, all_population_coords, alpha=1, step_size=0.001, max_workers=os.cpu_count())

    # Збереження результатів
    output_path = './my_project/output_result_data/new_store_best_locations/'
    save_optimal_locations_to_excel(optimal_locations, output_path)

    # Виведення результатів
    print_optimal_locations(optimal_locations)

    return optimal_locations[0]


# Виклик основної функції
if __name__ == "__main__":
    find_best_locations()
