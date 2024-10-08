import numpy as np


def get_haversine_dist_in_km(lon1, lat1, lon2, lat2):
    """
    Обчислює відстань між двома точками на сфері за формулою Гаверсина.
    """
    # Перетворення градусів у радіани
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    # Формула Гаверсина
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Радіус Землі в кілометрах

    return c * r
