import pandas as pd
from temabit_project.global_data import population_data, silpo_stores_data
from temabit_project.functions import calculate_pop_rel_weight_by_dist
import numpy as np

# Приведення даних до числових значень і перетворення в списки координат
population_data['lat'] = pd.to_numeric(population_data['lat'], errors='coerce')
population_data['lon'] = pd.to_numeric(population_data['lon'], errors='coerce')
silpo_stores_data['lat'] = pd.to_numeric(silpo_stores_data['lat'], errors='coerce')
silpo_stores_data['long'] = pd.to_numeric(silpo_stores_data['long'], errors='coerce')

# Фільтрація рядків без координат і одночасно витягуємо метрику популяції
population_data = population_data.dropna(subset=['lat', 'lon'])
population_coords = population_data[['lat', 'lon']].values

metric_population = population_data['metric population'].values

# Фільтруємо дані про магазини
silpo_stores_data = silpo_stores_data.dropna(subset=['lat', 'long'])
competitor_coords = silpo_stores_data[['lat', 'long']].values

all_population_data = pd.read_excel('save/Test.xlsx', sheet_name='Population')
all_population_coords = all_population_data[['lat', 'lon']].values


# Обчислення евклідових відстаней між всіма популяціями та конкурентами
def calculate_distance_matrix(population_coords, competitor_coords):
    pop_coords_array = np.array(population_coords)
    comp_coords_array = np.array(competitor_coords)

    # Використовуємо NumPy для обчислення відстаней між кожною популяцією та кожним конкурентом
    distance_matrix = np.linalg.norm(pop_coords_array[:, np.newaxis] - comp_coords_array, axis=2)
    return distance_matrix


# Використовуємо попередньо обчислену матрицю відстаней для розрахунку впливу конкурентів
def calculate_competitor_impact(distance_matrix, alpha=2):
    # Використовуємо згасання впливу на основі відстані
    impact_matrix = 1 / distance_matrix ** alpha
    total_impact = np.sum(impact_matrix, axis=1)  # Сума впливів всіх конкурентів на кожну популяцію

    # Знаходимо мінімальний і максимальний вплив, щоб зсунути і нормалізувати значення
    min_impact = np.min(total_impact)

    if min_impact < 0:
        # Якщо мінімальне значення від'ємне, зсуваємо всі значення так, щоб мінімальний вплив був нульовим
        total_impact = total_impact - min_impact

    # Нормалізуємо впливи, зберігаючи відносні відмінності
    max_impact = np.max(total_impact)

    if max_impact > 0:
        total_impact = total_impact / max_impact  # Нормалізуємо в межах від 0 до 1, зберігаючи різниці
    else:
        print(f"Error: not max_impact > 0")

    return total_impact


# Функція для обчислення загального зваженого попиту
def calculate_total_weighted_demand(store_coord, population_coords, distance_matrix, competitor_impact, alpha=2):
    # Векторизація обчислення відстані між магазином і популяціями
    # store_coord = np.array(store_coord)
    # print(population_coords, 'population_coords')
    # print(store_coord, 'store_coord')
    # distances_to_store = np.linalg.norm(population_coords - store_coord, axis=1)
    # print(distances_to_store, 'distances_to_store')
    # Перетворюємо градуси широти на відстань у км (1 градус ≈ 111 км)
    lat_diff = (population_coords[:, 0] - store_coord[0]) * 111  # Широта в км
    # Перетворюємо градуси довготи на км з урахуванням широти (косинус широти)
    lon_diff = (population_coords[:, 1] - store_coord[1]) * 111 * np.cos(np.radians(population_coords[:, 0]))   # Довгота в км
    # Обчислюємо Евклідову відстань у км
    distances_to_store = (np.sqrt(lat_diff ** 2 + lon_diff ** 2))

    # Векторизація розрахунку попиту
    # adjusted_weight = (1 / distances_to_store ** alpha) * (1 - competitor_impact)
    # adjusted_weight = (metric_population / (distances_to_store ** 2))
    adjusted_weight = np.array([calculate_pop_rel_weight_by_dist(dist) for dist in distances_to_store])
    # Обмежуємо значення так, щоб кожне значення не перевищувало 1
    # adjusted_weight = np.minimum(adjusted_weight, 1)
    # adjusted_weight = 1
    # adjusted_weight = distances_to_store
    # adjusted_weight = 1
    total_weighted_demand = np.sum(adjusted_weight)
    # print(total_weighted_demand, 'total_weighted_demand')

    return total_weighted_demand


# Паралельний пошук оптимальної локації
def find_optimal_location(population_coords, competitor_coords, alpha=2, step_size=0.001):
    # Визначаємо межі області
    x_min = min(coord[0] for coord in all_population_coords)
    x_max = max(coord[0] for coord in all_population_coords)
    y_min = min(coord[1] for coord in all_population_coords)
    y_max = max(coord[1] for coord in all_population_coords)

    print(x_min, x_max, y_min, y_max, 'x_min, x_max, y_min, y_max')

    # Попередньо обчислюємо матрицю відстаней і вплив конкурентів для всіх популяцій
    distance_matrix = calculate_distance_matrix(population_coords, competitor_coords)
    competitor_impact = calculate_competitor_impact(distance_matrix, alpha)

    # Масив для збереження результатів попиту і координат
    results = []

    # Обчислюємо попит для кожної пари координат
    for y in np.arange(y_max, y_min, -step_size):
        for x in np.arange(x_min, x_max, step_size):
            store_coord = (x, y)
            # Обчислюємо попит для поточної точки
            try:
                total_weighted_demand = calculate_total_weighted_demand(store_coord, population_coords,
                                                                        distance_matrix, competitor_impact, alpha)
                # Додаємо координати та попит у масив результатів
                results.append([total_weighted_demand, store_coord])

            except Exception as e:
                print(f"Error in task: {e}")

    # Сортуємо масив результатів від найвищого попиту до найнижчого
    results_sorted = sorted(results, key=lambda x: x[0], reverse=True)
    print(results_sorted[0], 'results_sorted')

    return results_sorted[:10]


# Виклик функції для знаходження найкращої локації
optimal_locations = find_optimal_location(population_coords, competitor_coords, 50)



def print_optimal_locations(optimal_locations):
    print("Топ 10 найкращих локацій:")
    for idx, location in enumerate(optimal_locations, 1):
        demand = round(location[0])
        lat, lon = location[1]
        print(f"{idx}. Попит: {demand}, Координати: (Широта: {lat:.6f}, Довгота: {lon:.6f})")

# Виклик функції виведення
print_optimal_locations(optimal_locations)
