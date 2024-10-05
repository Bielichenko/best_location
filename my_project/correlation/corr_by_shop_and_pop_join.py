# Імпортуємо необхідні бібліотеки
import pandas as pd
from scipy.stats import pearsonr
# Завантажимо файл із даними
file_path = '../../data_sets/Test.xlsx'
population_data = pd.read_excel(file_path, sheet_name='Population')
stores_data = pd.read_excel(file_path, sheet_name='Stores')

import pandas as pd
import numpy as np
from geopy.distance import geodesic


# Обчислюємо відстань між двома координатами за допомогою geodesic
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).km


# Створимо функцію для прив'язки популяцій до найближчого магазину
def assign_population_to_store(population_data, stores_data):
    # Створюємо колонки для зберігання інформації про найближчий магазин
    population_data['closest_store'] = None
    population_data['distance_to_store'] = None

    # Для кожної популяції шукаємо найближчий магазин
    for i, pop_row in population_data.iterrows():
        pop_coord = (pop_row['lat'], pop_row['lon'])
        min_distance = np.inf
        closest_store = None

        for j, store_row in stores_data.iterrows():
            store_coord = (store_row['lat'], store_row['long'])
            distance = calculate_distance(pop_coord, store_coord)

            if distance < min_distance:
                min_distance = distance
                closest_store = j  # Індекс найближчого магазину

        # Зберігаємо дані про найближчий магазин і відстань
        population_data.at[i, 'closest_store'] = closest_store
        population_data.at[i, 'distance_to_store'] = min_distance

    return population_data


# Прив'язуємо популяції до магазинів
population_data = assign_population_to_store(population_data, stores_data)


# Створимо функцію для обчислення метрик магазинів
# Обчислюємо метрики для магазинів
def calculate_store_metrics(population_data, stores_data):
    # Створюємо колонки для метрик, використовуючи pd.NA замість 0.0
    stores_data['avg_distance'] = pd.NA
    stores_data['sum_population_metric'] = pd.NA
    stores_data['avg_population_metric'] = pd.NA

    # Проходимо по кожному магазину
    for store_idx, store_row in stores_data.iterrows():
        # Отримуємо всі популяції, які належать до цього магазину
        store_population = population_data[population_data['closest_store'] == store_idx]

        if len(store_population) > 0:
            # Обчислюємо середню відстань
            avg_distance = store_population['distance_to_store'].mean()
            # Сумарна метрика популяції
            sum_population_metric = store_population['metric population'].sum()
            # Середня метрика популяції
            avg_population_metric = store_population['metric population'].mean()

            # Зберігаємо значення для магазинів
            stores_data.at[store_idx, 'avg_distance'] = float(avg_distance) if len(store_population) > 0 else pd.NA
            stores_data.at[store_idx, 'sum_population_metric'] = float(sum_population_metric) if len(
                store_population) > 0 else pd.NA
            stores_data.at[store_idx, 'avg_population_metric'] = float(avg_population_metric) if len(
                store_population) > 0 else pd.NA

    return stores_data


# Обчислюємо метрики для магазинів
stores_data = calculate_store_metrics(population_data, stores_data)

# Функція для обчислення кореляції та p-value
def calculate_corr_and_pvalue(x, y):
    corr, p_value = pearsonr(x, y)
    return pd.Series({'correlation': corr, 'p_value': p_value})

# Обчислюємо кореляцію та p-value між метрикою магазину та знайденими метриками
corr_results = pd.DataFrame()

for col in ['avg_distance', 'sum_population_metric', 'avg_population_metric']:
    # Фільтруємо ряди з непорожніми числовими значеннями у обох стовпцях
    valid_rows = stores_data[['Metric Store', col]].dropna().astype(float)

    # Обчислюємо кореляцію та p-value тільки для непорожніх значень
    if len(valid_rows) > 1:  # Перевіряємо, що є достатньо значень для кореляції
        corr_results[col] = calculate_corr_and_pvalue(valid_rows['Metric Store'], valid_rows[col])
    else:
        print(f"Недостатньо даних для обчислення кореляції в колонці {col}")

# Збереження результатів
stores_data[['Store', 'Metric Store', 'avg_distance', 'sum_population_metric', 'avg_population_metric']].to_excel('save_files/test.xlsx', index=False)
corr_results.to_excel('save_files/test_2.xlsx', index=True)

print("Збережено результати кореляції та p-value.")
