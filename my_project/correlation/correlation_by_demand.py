from temabit_project.global_data import population_data, silpo_stores_data
from temabit_project.functions import calculate_pop_rel_weight_by_dist

import pandas as pd
import numpy as np

# Приведення даних до числових значень і перетворення в списки координат
population_data['lat'] = pd.to_numeric(population_data['lat'], errors='coerce')
population_data['lon'] = pd.to_numeric(population_data['lon'], errors='coerce')
silpo_stores_data['lat'] = pd.to_numeric(silpo_stores_data['lat'], errors='coerce')
silpo_stores_data['long'] = pd.to_numeric(silpo_stores_data['long'], errors='coerce')

# Фільтрація рядків без координат і витягування метрики популяції
population_data = population_data.dropna(subset=['lat', 'lon'])
population_coords = population_data[['lat', 'lon']].values
metric_population = population_data['metric population'].values  # Витягуємо метрику популяції

# Фільтруємо дані про магазини
silpo_stores_data = silpo_stores_data.dropna(subset=['lat', 'long'])
competitor_coords = silpo_stores_data[['lat', 'long']].values


# Обчислення евклідових відстаней між всіма популяціями та конкурентами
def calculate_distance_matrix(population_coords, competitor_coords):
    pop_coords_array = np.array(population_coords)
    comp_coords_array = np.array(competitor_coords)

    # Перетворюємо градуси широти на відстань у км (1 градус ≈ 111 км)
    lat_diff = (pop_coords_array[:, 0, np.newaxis] - comp_coords_array[:, 0]) * 111

    # Перетворюємо градуси довготи на км з урахуванням широти для кожної пари
    lon_diff = (pop_coords_array[:, 1, np.newaxis] - comp_coords_array[:, 1]) * 111 * np.cos(
        np.radians(pop_coords_array[:, 0, np.newaxis]))

    # Обчислюємо Евклідову відстань у км
    distance_matrix = np.sqrt(lat_diff ** 2 + lon_diff ** 2)

    return distance_matrix


# Використовуємо матрицю відстаней для розрахунку впливу конкурентів (без поточного магазину)
def calculate_other_shops_effect(distance_matrix, exclude_index=None, alpha=1):
    if exclude_index is not None:
        # Обнуляємо вплив поточного магазину, щоб виключити його вплив на популяцію
        distance_matrix[:, exclude_index] = np.inf  # Встановлюємо нескінченну відстань

    impact_matrix = 1 / (1 + np.log10(1 + distance_matrix) * distance_matrix ** alpha)
    pop_total_impact = np.sum(impact_matrix, axis=1)

    max_impact = np.max(pop_total_impact)
    if max_impact > 1:
        pop_total_impact = pop_total_impact / max_impact

    return pop_total_impact


# Функція для обчислення загального зваженого попиту з урахуванням метрики популяції
def calculate_total_weighted_demand(store_coord, population_coords, distance_matrix, competitor_impact,
                                    metric_population, alpha=1):
    lat_diff = (population_coords[:, 0] - store_coord[0]) * 111  # Широта в км
    lon_diff = (population_coords[:, 1] - store_coord[1]) * 111 * np.cos(
        np.radians(population_coords[:, 0]))  # Довгота в км
    distances_to_store = np.sqrt(lat_diff ** 2 + lon_diff ** 2)  # Евклідова відстань у км

    # Розраховуємо вагу популяції в залежності від відстані
    pop_weight_by_dist_eff = calculate_pop_rel_weight_by_dist(distances_to_store)

    # Враховуємо метрику популяції
    pop_weight_by_dist_and_metric = pop_weight_by_dist_eff * metric_population

    # Враховуємо вплив інших магазинів
    pop_weight_final = pop_weight_by_dist_eff * (1 - pop_weight_by_dist_and_metric)

    # Загальний зважений попит
    total_weighted_demand = np.sum(pop_weight_final)

    return total_weighted_demand


# Функція для обчислення попиту по всіх магазинах
def calculate_demand_for_all_stores(population_coords, competitor_coords, stores_data, metric_population, alpha=1):
    # Обчислюємо відстані між популяціями і магазинами
    distance_matrix = calculate_distance_matrix(population_coords, competitor_coords)

    # Масив для збереження результатів попиту і координат
    store_results = []

    # Перебираємо всі магазини і обчислюємо попит для кожного
    for index, store_row in stores_data.iterrows():
        store_coord = [store_row['lat'], store_row['long']]
        print('store_coord: ', store_coord)

        # Оновлюємо вплив конкурентів, виключаючи поточний магазин
        competitor_impact = calculate_other_shops_effect(distance_matrix, exclude_index=index, alpha=alpha)

        total_weighted_demand = calculate_total_weighted_demand(store_coord, population_coords, distance_matrix,
                                                                competitor_impact, metric_population, alpha)

        # Додаємо метрику магазину та сумарний попит у результати
        store_metric = store_row['Metric Store']  # Припускаємо, що є стовпець з метрикою магазину
        store_results.append({
            'Store Metric': store_metric,
            'Store Coordinates': store_coord,
            'Total Weighted Demand': total_weighted_demand
        })

    return store_results


# Функція для розрахунку кореляції між попитом та метрикою магазину
def calculate_correlation(store_demand_results):
    # Створюємо DataFrame з результатами
    results_df = pd.DataFrame(store_demand_results)

    # Обчислюємо кореляцію між "Store Metric" і "Total Weighted Demand"
    correlation = results_df['Store Metric'].corr(results_df['Total Weighted Demand'])

    return correlation


# Виклик функції для розрахунку попиту для кожного магазину
store_demand_results = calculate_demand_for_all_stores(population_coords, competitor_coords, silpo_stores_data,
                                                       metric_population)

# Виклик функції для розрахунку кореляції
correlation = calculate_correlation(store_demand_results)


# Функція виведення результатів
def print_store_demand_results(store_demand_results):
    print("Попит по кожному магазину:")
    for idx, result in enumerate(store_demand_results, 1):
        print(
            f"{idx}. Магазин: {result['Store Coordinates']}, Метрика: {result['Store Metric']}, Попит: {result['Total Weighted Demand']:.3f}")
    print(f"\nКореляція між метрикою магазину та попитом: {correlation:.3f}")


# Виклик функції для виведення результатів
print_store_demand_results(store_demand_results)

