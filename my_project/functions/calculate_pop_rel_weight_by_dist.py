import numpy as np


def calculate_pop_rel_weight_by_dist(distances, alpha=1):
    # Використовуємо векторні операції для обчислення всіх значень одночасно
    return 1 / (1 + np.log10(1 + distances) * distances ** alpha)