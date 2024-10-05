from .correlation import geomap_visualization
from .visualizations import show_in_tableau
from .correlation import corr_binding_approach
from .correlation import calc_correlations_with_sectors_approach
from .find_best_locations import find_best_locations
from .visualizations import show_best_location, show_best_location_old
from .functions import get_competitors_shops


def main():
    print("Розрахунок успішно запущено...")
    geomap_visualization()
    corr_binding_approach()
    competitors_shops = get_competitors_shops()
    calc_correlations_with_sectors_approach(3)
    show_in_tableau()
    best_location = find_best_locations()
    show_best_location(best_location[1], competitors_shops)
    # show_best_location_old(best_location[1])

# Ви також можете включити ваш основний код для запуску
if __name__ == "__main__":
    main()
