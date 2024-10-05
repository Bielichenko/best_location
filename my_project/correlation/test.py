from temabit_project.global_data import population_data
import numpy as np
from temabit_project.functions import calculate_pop_rel_weight_by_dist
np.set_printoptions(suppress=True)
population_coords = population_data[['lat', 'lon']].values
# store_coord_1 = [50.435463, 30.616598]
# store_coord_2 = [ 50.400463, 30.399598]
# store_coord_3 = [50.462463, 30.386598]

stores = np.array([[50.4200, 30.4200], [50.4300, 30.4300]])


# Перетворюємо градуси широти на відстань у км (1 градус ≈ 111 км)
lat_diff = (population_coords[:, 0, np.newaxis] - stores[:, 0]) * 111  # Широта в км

print(lat_diff)

# # Перетворюємо градуси довготи на км з урахуванням широти кожної популяції
lon_diff = (population_coords[:, 1, np.newaxis] - stores[:,  1]) * 111 * np.cos(np.radians(population_coords[:, 0, np.newaxis]))  # Довгота в км
print(lon_diff)
#
# Обчислюємо Евклідову відстань у км
pop_distances_to_stores = np.sqrt(lat_diff ** 2 + lon_diff ** 2)
print('Відстані до магазину в км:', pop_distances_to_stores)
#
# # Зважуємо попит
adjusted_weight = np.array([calculate_pop_rel_weight_by_dist(dist) for dist in pop_distances_to_stores])
print('adjusted_weight', adjusted_weight)
total_weighted_demand = np.sum(adjusted_weight, axis = 1)
print('total_weighted_demand', total_weighted_demand)
# print('Загальний зважений попит:', total_weighted_demand)




# print("Результати:", calculate_pop_rel_weight_by_dist(10))