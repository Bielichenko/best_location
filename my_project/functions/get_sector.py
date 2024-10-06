def get_sector(azimuth, n_sectors):
    """
    Визначає сектор на основі азимуту та кількості секторів.
    """
    sector_angle = 360 / n_sectors
    return int(azimuth // sector_angle)
