import numpy as np
import math
from scipy.stats import pearsonr
import pandas as pd
from my_project.functions import get_competitors_shops
from my_project.global_data import silpo_stores_data, population_data

def calc_correlations_with_sectors_approach(radius_km=1, n_sectors=4):
    # Завантажуємо необхідні дані з глобальних змінних
    competitors_stores_data = get_competitors_shops()

    # Перетворюємо список конкурентів на DataFrame, якщо це необхідно
    if isinstance(competitors_stores_data, list):
        competitors_stores_data = pd.DataFrame(competitors_stores_data, columns=['Name', 'Latitude', 'Longitude'])

    # Функція для обчислення відстані за формулою Гаверсина
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Радіус Землі в кілометрах
        return c * r

    # Функція для обчислення азимута (куту)
    def calculate_azimuth(lon1, lat1, lon2, lat2):
        dlon = lon2 - lon1
        x = math.cos(lat2) * math.sin(dlon)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        azimuth = np.degrees(np.arctan2(x, y))
        return (azimuth + 360) % 360  # Повертає значення від 0 до 360

    # Функція для визначення сектора
    def get_sector(azimuth, n_sectors):
        sector_angle = 360 / n_sectors
        return int(azimuth // sector_angle)

    # Об'єднуємо координати магазинів з основного файлу і додаткових магазинів
    silpo_stores_coords = silpo_stores_data[['lat', 'long']].values
    region_competitors_stores_coords = competitors_stores_data[['Latitude', 'Longitude']].values
    pop_coords = population_data[['lat', 'lon']].values

    # Функція для обчислення метрик для регіону
    def calculate_region_metrics(target_stores_coords, competitors_stores_coords, pop_coords, population_data, radius_km, n_sectors):
        stores_density = []
        population_density = []
        population_metric_sum = []
        population_metric_avg = []
        population_uniformity = []

        for i, target_store in enumerate(target_stores_coords):
            target_store_distances_to_other_target_stores = np.array(
                [haversine(target_store[1], target_store[0], other_store[1], other_store[0])
                 for other_store in target_stores_coords]
            )

            target_store_distances_to_competitors_stores = np.array(
                [haversine(target_store[1], target_store[0], other_store[1], other_store[0]) for other_store in
                 competitors_stores_coords]
            )

            all_target_store_distances = np.concatenate(
                [target_store_distances_to_other_target_stores, target_store_distances_to_competitors_stores])

            stores_count = np.sum(all_target_store_distances < radius_km)

            pop_distances = np.array([haversine(target_store[1], target_store[0], pop[1], pop[0]) for pop in pop_coords])
            nearby_populations = population_data[pop_distances < radius_km]
            pop_count = len(nearby_populations)
            pop_metric_sum = nearby_populations['metric population'].sum()
            pop_metric_avg = nearby_populations['metric population'].mean() if pop_count > 0 else None

            if pop_count > 0:
                sector_population_counts = np.zeros(n_sectors)

                for j, pop in nearby_populations.iterrows():
                    azimuth = calculate_azimuth(target_store[1], target_store[0], pop['lon'], pop['lat'])
                    sector = get_sector(azimuth, n_sectors)
                    sector_population_counts[sector] += pop['metric population']  # Кількість у секторі

                uniformity_metric = np.std(sector_population_counts)
            else:
                uniformity_metric = None

            stores_density.append(stores_count)
            population_density.append(pop_count)
            population_metric_sum.append(pop_metric_sum)
            population_metric_avg.append(pop_metric_avg)
            population_uniformity.append(uniformity_metric)

        return stores_density, population_density, population_metric_sum, population_metric_avg, population_uniformity

    # Обчислюємо метрики для радіусу radius_km
    (store_density_3km,
     population_density_3km,
     population_metric_sum_3km,
     population_metric_avg_3km,
     population_uniformity) = calculate_region_metrics(
        silpo_stores_coords,
        region_competitors_stores_coords,
        pop_coords,
        population_data,
        radius_km,
        n_sectors)

    # Додаємо нові показники до таблиці магазинів
    silpo_stores_data['store_density_3km'] = store_density_3km
    silpo_stores_data['population_density_3km'] = population_density_3km
    silpo_stores_data['population_metric_sum_3km'] = population_metric_sum_3km
    silpo_stores_data['population_metric_avg_3km'] = population_metric_avg_3km
    silpo_stores_data['population_uniformity_3km'] = population_uniformity

    silpo_stores_data['population_store_ratio_3km'] = silpo_stores_data['population_density_3km'] / silpo_stores_data[
        'store_density_3km'].replace(0, np.nan)
    silpo_stores_data['pop_metric_store_ratio_3km'] = silpo_stores_data['population_metric_sum_3km'] / silpo_stores_data[
        'store_density_3km'].replace(0, np.nan)

    # Вибираємо лише числові колонки для аналізу
    numeric_columns = ['Metric Store', 'store_density_3km', 'population_density_3km',
                       'population_store_ratio_3km', 'population_metric_sum_3km',
                       'population_metric_avg_3km', 'population_uniformity_3km', 'pop_metric_store_ratio_3km']

    # Створюємо DataFrame для збереження результатів кореляцій та p-value
    correlation_results = pd.DataFrame(columns=['Metric 1', 'Metric 2', 'Correlation', 'P-value'])

    # Обчислюємо кореляцію та p-value для кожної пари метрик
    for i, col1 in enumerate(numeric_columns):
        for col2 in numeric_columns[i:]:
            if col1 != col2:
                valid_data = silpo_stores_data[[col1, col2]].dropna()
                if len(valid_data) > 2:
                    corr, p_value = pearsonr(valid_data[col1], valid_data[col2])
                    result_row = pd.DataFrame(
                        {'Metric 1': [col1], 'Metric 2': [col2], 'Correlation': [corr], 'P-value': [p_value]})
                    correlation_results = pd.concat([correlation_results, result_row], ignore_index=True)

    # Збереження результатів
    output_path = './my_project/corr_search_res/'
    silpo_stores_data.to_excel(output_path + 'correlation_sectors_approach_data.xlsx', index=False)
    correlation_results.to_excel(output_path + 'correlation_sectors_approach_result.xlsx', index=False)

    print("Збережено результати кореляцій та p-value між усіма метриками.")

    return silpo_stores_data, correlation_results
