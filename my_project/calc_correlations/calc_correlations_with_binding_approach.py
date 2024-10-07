import pandas as pd
from scipy.stats import pearsonr
import numpy as np
from sklearn.neighbors import NearestNeighbors
from my_project.global_data import populations_data, silpo_shops_data


# Оптимізована функція для прив'язки популяцій до найближчого магазину
def assign_populations_to_shop():
    # Створюємо модель NearestNeighbors для швидкого пошуку найближчих магазинів
    nn_model = NearestNeighbors(n_neighbors=1, metric='haversine')

    # Конвертуємо координати в радіани (для моделі NearestNeighbors з haversine)
    populations_coords = np.radians(populations_data[['lat', 'lon']].values)
    store_coords = np.radians(silpo_shops_data[['lat', 'long']].values)

    # Навчаємо модель на координатах магазинів
    nn_model.fit(store_coords)

    # Знаходимо найближчі магазини для кожної популяції
    distances, indices = nn_model.kneighbors(populations_coords)

    populations_data_assigned_with_shops = populations_data.copy()

    # Відстані будуть у радіанах, переводимо їх у кілометри (6371 - радіус Землі)
    populations_data_assigned_with_shops['distance_to_shop'] = distances * 6371
    populations_data_assigned_with_shops['closest_shop'] = indices.flatten()  # Індекси найближчих магазинів

    return populations_data_assigned_with_shops


# Функція для обчислення метрик магазинів
def calculate_shops_metrics(populations_data_assigned_with_shops):
    silpo_shops_data_with_metrics = silpo_shops_data.copy()

    # Створюємо порожні колонки для результатів
    silpo_shops_data_with_metrics['avg_distance_to_pops'] = pd.NA
    silpo_shops_data_with_metrics['sum_pops_metric'] = pd.NA
    silpo_shops_data_with_metrics['avg_pops_metric'] = pd.NA

    # Групуємо дані популяції за найближчим магазином і обчислюємо метрики
    grouped_populations = populations_data_assigned_with_shops.groupby('closest_shop')

    silpo_shops_data_with_metrics['avg_distance_to_pops'] = grouped_populations['distance_to_shop'].mean()
    silpo_shops_data_with_metrics['sum_pops_metric'] = grouped_populations['metric population'].sum()
    silpo_shops_data_with_metrics['avg_pops_metric'] = grouped_populations['metric population'].mean()

    return silpo_shops_data_with_metrics


# Функція для обчислення кореляції та p-value
def calculate_corr_and_pvalue(x, y):
    corr, p_value = pearsonr(x, y)
    return pd.Series({'calc_correlation': corr, 'p_value': p_value})


# Основна функція для обчислення всіх кореляцій та метрик
def calc_correlations_with_binding_approach():
    print("Підрахунок кореляції за допомогою \"Прив'язочного підходу\" запущено!")

    output_dir = './my_project/output_result_data/calc_correlations_result_data'

    # Прив'язка популяцій до найближчого магазину
    populations_data_assigned_with_shops = assign_populations_to_shop()

    # # Збереження даних про популяцію
    # populations_data_assigned_with_shops.to_excel(f'{output_dir}/populations_data_assigned_with_shops.xlsx', index=True)

    # Обчислення метрик для магазинів
    silpo_shops_data_with_metrics = calculate_shops_metrics(populations_data_assigned_with_shops)

    # Обчислення кореляції та p-value між метриками магазинів
    corr_results = pd.DataFrame()

    for col in ['avg_distance_to_pops', 'sum_pops_metric', 'avg_pops_metric']:
        valid_rows = silpo_shops_data_with_metrics[['Metric Store', col]].dropna().astype(float)

        if len(valid_rows) > 1:
            corr_results[col] = calculate_corr_and_pvalue(valid_rows['Metric Store'], valid_rows[col])
        else:
            print(f"Недостатньо даних для обчислення кореляції між {col} та Metric Store")

    # Збереження результатів
    silpo_shops_data_with_metrics.to_excel(f'{output_dir}/corr_binding_approach_shops_data.xlsx', index=False)
    corr_results.to_excel(f'{output_dir}/corr_binding_approach_results.xlsx', index=True)

    print("Збережено результати кореляції та p-value!")

    return silpo_shops_data_with_metrics, corr_results

