# Функція для обчислення кордонів сектора з відступами
def get_analysing_sector_bounds(population_data, indent_km=3):
    """
    Обчислює кордони сектора на основі координат популяції та додає відступи, щоб об'єкти не знаходились занадто близько до країв.

    Parameters:
    populations_data (pd.DataFrame): Дані про популяцію з колонками 'lat' та 'lon'.
    indent_km (float): Відступ у кілометрах (за замовчуванням 3 км).

    Returns:
    tuple: Кордони сектора у вигляді (x_min, x_max, y_min, y_max).
    """
    # Константи
    km_per_lat = 111  # Приблизний коефіцієнт для переведення широти в кілометри
    km_per_lon_at_50_lat = 71  # Приблизний коефіцієнт для переведення довготи в кілометри на широті 50 градусів

    # Конвертуємо відступ у кілометрах в градуси
    indent_lat = indent_km / km_per_lat
    indent_lon = indent_km / km_per_lon_at_50_lat

    # Знаходимо мінімальні та максимальні координати і додаємо відступ
    x_min = population_data['lat'].min() - indent_lat
    x_max = population_data['lat'].max() + indent_lat
    y_min = population_data['lon'].min() - indent_lon
    y_max = population_data['lon'].max() + indent_lon

    return x_min, x_max, y_min, y_max
