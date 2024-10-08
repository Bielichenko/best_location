# from .calc_correlations import geomap_visualization, geomap_visualization_2
from .calc_correlations import calc_correlations_with_binding_approach
from .calc_correlations import calc_correlations_with_areas_approach
from .find_best_locations import find_best_locations
from .show_visualizations import show_in_geomap, show_in_tableau
from .functions import get_competitors_shops
from .global_data import populations_data


# Налаштування алгоритму (True/False)
# Чи треба для деяких етапів підгружати супермаркети інших мереж?
is_need_to_add_competitors = True


def main():
    print("Алгоритм успішно активовано!")

    show_in_geomap(True)
    calc_correlations_with_binding_approach()
    competitors_shops = get_competitors_shops() if is_need_to_add_competitors else []
    calc_correlations_with_areas_approach(competitors_shops)
    show_in_tableau()
    print('Результати кореляції візуалізовані в твоєму браузері!')

    best_location = find_best_locations(competitors_shops)
    show_in_geomap(False, best_location, competitors_shops)
    print('Найкраща локація додана на гео мапу в твоєму браузері!')

    print("Всі етапи алгоритму пройдені! Дякую за увагу!")

if __name__ == "__main__":
    main()
