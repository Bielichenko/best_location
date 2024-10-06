# from .calc_correlations import geomap_visualization, geomap_visualization_2
from .calc_correlations import calc_correlations_with_binding_approach
from .calc_correlations import calc_correlations_with_sectors_approach
from .find_best_locations import find_best_locations
from .show_visualizations import show_in_geomap
from .functions import get_competitors_shops
from .global_data import populations_data


def main():
    print("Алгоритм успішно активовано!")
    show_in_geomap(True)
    print('populations_data before:', populations_data)
    # calc_correlations_with_binding_approach()
    print('populations_data after:', populations_data)
    # competitors_shops = get_competitors_shops()
    # competitors_shops = []
    # calc_correlations_with_sectors_approach(3)
    # show_in_tableau()
    # best_location = find_best_locations()
    # show_best_location(best_location[1], competitors_shops)
    # show_best_location([], [])

# Ви також можете включити ваш основний код для запуску
if __name__ == "__main__":
    main()
