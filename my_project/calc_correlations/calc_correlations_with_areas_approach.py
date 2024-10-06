import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from my_project.functions import get_competitors_shops, get_haversine_dist_in_km, calculate_azimuth, get_sector
from my_project.global_data import silpo_shops_data, populations_data
import os


def get_dists_from_curr_silpo_shop_to_other_objs(curr_silpo_shop_lon, curr_silpo_shop_lat, other_objs_coords):
    return np.array([
        get_haversine_dist_in_km(curr_silpo_shop_lon, curr_silpo_shop_lat, other_obj_lon, other_obj_lat)
        for other_obj_lat, other_obj_lon in other_objs_coords
    ])


# Функція для обчислення метрик
def calculate_region_metrics(
    silpo_shops_coords, competitors_shops_coords, pops_coords, populations_data, radius_km, n_sectors
):
    """
    Обчислює метрики для кожного магазину в заданому радіусі.
    """
    stores_density = []
    population_density = []
    population_metric_sum = []
    population_metric_avg = []
    population_uniformity = []

    for i, (curr_silpo_shop_lat, curr_silpo_shop_lon) in enumerate(silpo_shops_coords):
        # Відстані до інших магазинів
        dists_to_other_silpo_shops = get_dists_from_curr_silpo_shop_to_other_objs(curr_silpo_shop_lon, curr_silpo_shop_lat, silpo_shops_coords)
        dists_to_competitors_shops = get_dists_from_curr_silpo_shop_to_other_objs(curr_silpo_shop_lon, curr_silpo_shop_lat, competitors_shops_coords)
        # Виключаємо поточний магазин
        dists_to_other_silpo_shops[i] = np.inf
        # Загальні відстані до всіх магазинів
        dists_to_silpo_and_competitors_shops = np.concatenate([dists_to_other_silpo_shops, dists_to_competitors_shops])
        # Кількість магазинів у радіусі
        shops_in_sector = np.sum(dists_to_silpo_and_competitors_shops < radius_km)

        # Відстані до популяційних точок
        pops_dists = get_dists_from_curr_silpo_shop_to_other_objs(curr_silpo_shop_lon, curr_silpo_shop_lat, pops_coords)
        # Популяції в радіусі
        nearby_populations_data = populations_data[pops_dists < radius_km]
        nearby_pops_count = len(nearby_populations_data)
        pop_metric_sum = nearby_populations_data['metric population'].sum()
        pop_metric_avg = nearby_populations_data['metric population'].mean() if nearby_pops_count > 0 else np.nan

        # Обчислення рівномірності популяції по секторах
        if nearby_pops_count > 0:
            sector_population_metrics = np.zeros(n_sectors)
            for _, nearby_pop_row in nearby_populations_data.iterrows():
                nearby_pop_lat, nearby_pop_lon = nearby_pop_row['lat'], nearby_pop_row['lon']
                azimuth = calculate_azimuth(curr_silpo_shop_lon, curr_silpo_shop_lat, nearby_pop_lon, nearby_pop_lat)
                sector = get_sector(azimuth, n_sectors)
                sector_population_metrics[sector] += nearby_pop_row['metric population']
            uniformity_metric = np.std(sector_population_metrics)
        else:
            uniformity_metric = np.nan

        # Додаємо метрики до списків
        stores_density.append(shops_in_sector)
        population_density.append(nearby_pops_count)
        population_metric_sum.append(pop_metric_sum)
        population_metric_avg.append(pop_metric_avg)
        population_uniformity.append(uniformity_metric)

    return (
        stores_density,
        population_density,
        population_metric_sum,
        population_metric_avg,
        population_uniformity
    )

def calc_correlations_with_areas_approach(competitors_shops, radius_km=1, n_sectors=4):
    """
    Обчислює кореляції між різними метриками, використовуючи підхід секторів.

    Параметри:
        radius_km (float): Радіус навколо кожного магазину в кілометрах.
        n_sectors (int): Кількість секторів для поділу окружності навколо магазину.

    Повертає:
        silpo_shops_data (DataFrame): Оновлений DataFrame з доданими метриками.
        correlation_results_df (DataFrame): DataFrame з обчисленими кореляціями та p-значеннями.
    """

    # Перетворюємо список конкурентів на DataFrame, якщо це необхідно
    if isinstance(competitors_shops, list):
        competitors_shops = pd.DataFrame(
            competitors_shops, columns=['Name', 'Latitude', 'Longitude']
        )



    # Отримуємо координати
    silpo_shops_coords = silpo_shops_data[['lat', 'long']].values
    competitors_shops_coords = competitors_shops[['Latitude', 'Longitude']].values
    pops_coords = populations_data[['lat', 'lon']].values



    # Обчислюємо метрики
    (
        stores_density_3km,
        population_density_3km,
        population_metric_sum_3km,
        population_metric_avg_3km,
        population_uniformity_3km
    ) = calculate_region_metrics(
        silpo_shops_coords,
        competitors_shops_coords,
        pops_coords,
        populations_data,
        radius_km,
        n_sectors
    )

    # Додаємо нові метрики до DataFrame
    silpo_shops_data['store_density_3km'] = stores_density_3km
    silpo_shops_data['population_density_3km'] = population_density_3km
    silpo_shops_data['population_metric_sum_3km'] = population_metric_sum_3km
    silpo_shops_data['population_metric_avg_3km'] = population_metric_avg_3km
    silpo_shops_data['population_uniformity_3km'] = population_uniformity_3km

    silpo_shops_data['population_store_ratio_3km'] = silpo_shops_data['population_density_3km'] / \
        silpo_shops_data['store_density_3km'].replace(0, np.nan)
    silpo_shops_data['pop_metric_store_ratio_3km'] = silpo_shops_data['population_metric_sum_3km'] / \
        silpo_shops_data['store_density_3km'].replace(0, np.nan)

    # Список числових колонок для аналізу
    numeric_columns = [
        'Metric Store',
        'store_density_3km',
        'population_density_3km',
        'population_store_ratio_3km',
        'population_metric_sum_3km',
        'population_metric_avg_3km',
        'population_uniformity_3km',
        'pop_metric_store_ratio_3km'
    ]

    # Обчислюємо кореляції та p-значення
    correlation_results = []
    for i, col1 in enumerate(numeric_columns):
        for col2 in numeric_columns[i + 1:]:
            valid_data = silpo_shops_data[[col1, col2]].dropna()
            if len(valid_data) > 2:
                corr, p_value = pearsonr(valid_data[col1], valid_data[col2])
                correlation_results.append({
                    'Metric 1': col1,
                    'Metric 2': col2,
                    'Correlation': corr,
                    'P-value': p_value
                })

    correlation_results_df = pd.DataFrame(correlation_results)

    # Збереження результатів
    output_path = './my_project/corr_search_res/'
    os.makedirs(output_path, exist_ok=True)
    silpo_shops_data.to_excel(
        os.path.join(output_path, 'correlation_sectors_approach_data.xlsx'),
        index=False
    )
    correlation_results_df.to_excel(
        os.path.join(output_path, 'correlation_sectors_approach_result.xlsx'),
        index=False
    )

    print("Збережено результати кореляцій та p-значень між метриками.")

    return silpo_shops_data, correlation_results_df
