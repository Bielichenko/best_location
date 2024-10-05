# Імпортуємо необхідні бібліотеки
import pandas as pd
from scipy.stats import pearsonr
import numpy as np
from sklearn.neighbors import NearestNeighbors
# Імпортуємо дані один раз
from my_project.global_data import population_data, silpo_stores_data


# Оптимізована функція для прив'язки популяцій до найближчого магазину
def assign_population_to_store():
    # Створюємо модель NearestNeighbors для швидкого пошуку найближчих магазинів
    nn_model = NearestNeighbors(n_neighbors=1, metric='haversine')

    # Конвертуємо координати в радіани (для моделі NearestNeighbors з haversine)
    population_coords = np.radians(population_data[['lat', 'lon']].values)
    store_coords = np.radians(silpo_stores_data[['lat', 'long']].values)

    # Навчаємо модель на координатах магазинів
    nn_model.fit(store_coords)

    # Знаходимо найближчі магазини для кожної популяції
    distances, indices = nn_model.kneighbors(population_coords)

    # Відстані будуть у радіанах, переводимо їх у кілометри (6371 - радіус Землі)
    population_data['distance_to_store'] = distances * 6371
    population_data['closest_store'] = indices.flatten()  # Індекси найближчих магазинів

    return population_data


# Функція для обчислення метрик магазинів
def calculate_store_metrics():
    # Створюємо порожні колонки для результатів
    silpo_stores_data['avg_distance'] = pd.NA
    silpo_stores_data['sum_population_metric'] = pd.NA
    silpo_stores_data['avg_population_metric'] = pd.NA

    # Групуємо дані популяції за найближчим магазином і обчислюємо метрики
    grouped_population = population_data.groupby('closest_store')

    silpo_stores_data['avg_distance'] = grouped_population['distance_to_store'].mean()
    silpo_stores_data['sum_population_metric'] = grouped_population['metric population'].sum()
    silpo_stores_data['avg_population_metric'] = grouped_population['metric population'].mean()

    return silpo_stores_data


# Функція для обчислення кореляції та p-value
def calculate_corr_and_pvalue(x, y):
    corr, p_value = pearsonr(x, y)
    return pd.Series({'correlation': corr, 'p_value': p_value})


# Основна функція для обчислення всіх кореляцій та метрик
def corr_binding_approach(output_dir='./my_project/corr_search_res/'):
    print('corr_binding_approach started')

    # Прив'язка популяцій до найближчого магазину
    population_data = assign_population_to_store()

    # Збереження даних про популяцію
    population_data.to_excel(f'{output_dir}/population_data.xlsx', index=True)

    # Обчислення метрик для магазинів
    silpo_stores_data = calculate_store_metrics()

    # Обчислення кореляції та p-value між метриками магазинів
    corr_results = pd.DataFrame()

    for col in ['avg_distance', 'sum_population_metric', 'avg_population_metric']:
        valid_rows = silpo_stores_data[['Metric Store', col]].dropna().astype(float)

        if len(valid_rows) > 1:
            corr_results[col] = calculate_corr_and_pvalue(valid_rows['Metric Store'], valid_rows[col])
        else:
            print(f"Недостатньо даних для обчислення кореляції в колонці {col}")

    # Збереження результатів
    silpo_stores_data[
        ['Store', 'Metric Store', 'avg_distance', 'sum_population_metric', 'avg_population_metric']].to_excel(
        f'{output_dir}/corr_binding_approach_data.xlsx', index=False)
    corr_results.to_excel(f'{output_dir}/corr_binding_approach_result.xlsx', index=True)

    print("Збережено результати кореляції та p-value.")


# Виклик основної функції
if __name__ == "__main__":
    corr_binding_approach()
