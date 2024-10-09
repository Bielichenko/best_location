import numpy as np

def calculate_azimuth(lon1, lat1, lon2, lat2):
    """
    Обчислює азимут між двома точками.
    """
    # Перетворення градусів у радіани
    lon1_rad, lat1_rad, lon2_rad, lat2_rad = map(
        np.radians, [lon1, lat1, lon2, lat2]
    )
    dlon = lon2_rad - lon1_rad
    x = np.sin(dlon) * np.cos(lat2_rad)
    y = np.cos(lat1_rad) * np.sin(lat2_rad) - \
        np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
    azimuth_rad = np.arctan2(x, y)
    azimuth_deg = np.degrees(azimuth_rad)
    return (azimuth_deg + 360) % 360  # Нормалізація до [0, 360)