import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from my_project.global_data import populations_data, silpo_shops_data, all_population_data
from my_project.functions import calculate_pop_rel_weight_by_dist, get_analysing_map_bounds
from my_project.functions import get_competitors_shops
# from my_project.show_visualizations import show_best_location


# Функція для збереження результатів у Excel
def save_best_locations_to_excel(best_locations, output_path):
    best_locations_df = pd.DataFrame(best_locations, columns=['Total Weighted Demand', 'Coords'])
    best_locations_df.to_excel(output_path + 'new_store_best_locations.xlsx', index=False)
    print(
        'Ура! Файл з найкращими координатами для нових локацій успішно записан! '
        r'Шлях: temabit_test\my_project\output_result_data\new_store_best_locations'
    )


# Функція для обчислення загального зваженого попиту
def calculate_total_location_score(potential_location_coord, pops_coords, other_shops_effects_on_each_pop, alpha):
    lat_diff = (pops_coords[:, 0] - potential_location_coord[0]) * 111
    lon_diff = (pops_coords[:, 1] - potential_location_coord[1]) * 111 * np.cos(np.radians(pops_coords[:, 0]))
    distances_to_store = np.sqrt(lat_diff ** 2 + lon_diff ** 2)

    pops_rel_weight_by_dist_factor = calculate_pop_rel_weight_by_dist(distances_to_store, alpha)
    pops_rel_weight_by_dist_and_other_shops_factor = pops_rel_weight_by_dist_factor * (1 - other_shops_effects_on_each_pop)

    return np.sum(pops_rel_weight_by_dist_and_other_shops_factor)

# Використовуємо попередньо обчислену матрицю відстаней для розрахунку впливу конкурентів
def calculate_other_shops_effect(distance_matrix, silpo_and_other_corps_shops, alpha=1):
    """
    distance_matrix: матриця відстаней
    silpo_and_other_corps_shops: список конкурентів з назвою магазину, широтою та довготою
    alpha: коефіцієнт штрафу за відстань
    """

    # Обчислюємо базовий вплив для всіх магазинів
    other_shops_impact_matrix = calculate_pop_rel_weight_by_dist(distance_matrix, alpha)

    # В рамках розвитку мережі конкуренція з магазином зі своєї ж мережі наносить збиток і потенційно новому магазину і тому, що вже побудован, тому застосовується додатковий штраф:
    # Визначаємо, чи є магазин "Сільпо"
    is_silpo = [shop[0] == "Silpo" for shop in silpo_and_other_corps_shops]  # Якщо назва магазину містить "Сільпо"
    # Збільшуємо вплив для магазинів "Сільпо" за допомогою silpo_boost
    other_shops_impact_matrix[:, is_silpo] *= 2  # Застосовуємо коефіцієнт до колонок, де магазини "Сільпо"

    # Сумуємо впливи по всіх магазинах для кожної популяції
    pops_other_shops_total_impact = np.sum(other_shops_impact_matrix, axis=1)

    # Нормалізуємо значення, якщо максимальний вплив більше за 1
    max_impact = np.max(pops_other_shops_total_impact)
    if max_impact > 1:
        pops_other_shops_total_impact /= max_impact

    return pops_other_shops_total_impact


# Функція для обчислення евклідових відстаней між всіма популяціями та конкурентами
def calculate_distances_matrix(pops_coords, silpo_and_other_shops_coords):
    pops_coords_np_arr = np.array(pops_coords)

    # Якщо конкурентних магазинів немає, повертаємо порожню матрицю відстаней
    if len(silpo_and_other_shops_coords) == 0:
        return np.zeros((len(pops_coords), 0))  # Матриця відстаней з нульовою кількістю колонок

    # Створюємо два масиви (широта і довгота) в одному циклі
    shop_lat, shop_lon = np.array([
        (coord[1], coord[2]) for coord in silpo_and_other_shops_coords
    ], dtype=float).T  # Транспонування для розділення на широти і довготи

    # Обчислення різниці в координатах. Для оптимізації розрахунку використовуються матричні операції
    lat_diff = (pops_coords_np_arr[:, 0, np.newaxis] - shop_lat) * 111
    lon_diff = (pops_coords_np_arr[:, 1, np.newaxis] - shop_lon) * 111 * np.cos(
        np.radians(pops_coords_np_arr[:, 0, np.newaxis]))

    # Обчислення Евклідової відстані
    distances_from_pops_to_shops_matrix = np.sqrt(lat_diff ** 2 + lon_diff ** 2)

    return distances_from_pops_to_shops_matrix


# Функція для пошуку оптимальних локацій
def get_locations_with_best_score(pops_coords, silpo_and_other_shops_coords, alpha=1, step_size=0.001, max_workers=8):
    all_pops_coords = all_population_data[['lat', 'lon']].values
    x_min, x_max, y_min, y_max = get_analysing_map_bounds(all_pops_coords)

    distances_from_pops_to_shops_matrix = calculate_distances_matrix(pops_coords, silpo_and_other_shops_coords)
    other_shops_effects_on_each_pop = calculate_other_shops_effect(distances_from_pops_to_shops_matrix, silpo_and_other_shops_coords, alpha)

    all_potential_locations_score = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_location = {}
        for y in np.arange(y_max, y_min, -step_size):
            for x in np.arange(x_min, x_max, step_size):
                potential_location_coord = (x, y)
                future = executor.submit(calculate_total_location_score, potential_location_coord, pops_coords, other_shops_effects_on_each_pop, alpha)
                future_to_location[future] = potential_location_coord

        for future in as_completed(future_to_location):
            try:
                potential_location_score = future.result()
                potential_location_coord = future_to_location[future]
                all_potential_locations_score.append([potential_location_score, potential_location_coord])
            except Exception as e:
                print(f"Error in task: {e}")

    all_potential_locations_score_sorted = sorted(all_potential_locations_score, key=lambda x: x[0], reverse=True)
    return all_potential_locations_score_sorted[:100]

# Функція для завантаження та підготовки даних
def load_and_prepare_data(competitors_shops_prepared):
    # Приведення даних до числових значень і перетворення в списки координат
    populations_data['lat'] = pd.to_numeric(populations_data['lat'], errors='coerce')
    populations_data['lon'] = pd.to_numeric(populations_data['lon'], errors='coerce')
    silpo_shops_data['lat'] = pd.to_numeric(silpo_shops_data['lat'], errors='coerce')
    silpo_shops_data['long'] = pd.to_numeric(silpo_shops_data['long'], errors='coerce')

    # Фільтрація рядків без координат
    populations_data_filtered = populations_data.dropna(subset=['lat', 'lon'])
    pops_coords = populations_data_filtered[['lat', 'lon']].values
    # pops_metrics = populations_data_filtered['metric population'].values

    # Фільтруємо дані про магазини
    silpo_shops_data_filtered = silpo_shops_data.dropna(subset=['lat', 'long'])
    silpo_shops_coords = silpo_shops_data_filtered[['lat', 'long']].values
    silpo_shops_coords_with_corp_name = [["Silpo", lat, lon,] for lat, lon in silpo_shops_coords]

    silpo_and_other_shops_coords = silpo_shops_coords_with_corp_name + competitors_shops_prepared

    return pops_coords, silpo_and_other_shops_coords

# Основна функція для виклику з основного файлу проекту
def find_best_locations(competitors_shops, is_need_to_add_competitors=True):
    competitors_shops_prepared = competitors_shops if is_need_to_add_competitors else []

    # Завантаження і підготовка даних
    pops_coords, silpo_and_other_shops_coords = load_and_prepare_data(competitors_shops_prepared)

    # Пошук оптимальних локацій
    best_locations = get_locations_with_best_score(pops_coords, silpo_and_other_shops_coords, alpha=1, step_size=0.001, max_workers=os.cpu_count())

    # Збереження результатів
    output_path = './my_project/output_result_data/new_store_best_locations/'
    save_best_locations_to_excel(best_locations, output_path)

    return best_locations[0]


# Виклик основної функції
if __name__ == "__main__":
    find_best_locations()
