import plotly.express as px
import pandas as pd
from my_project.global_data import silpo_stores_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from my_project.global_data import population_data, silpo_stores_data
import folium
import pandas as pd
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import branca.colormap as cm
import folium
import pandas as pd
import webbrowser
import os
import branca.colormap as cm
import folium
import pandas as pd
import webbrowser
import os
import branca.colormap as cm


def geomap_visualization():
    # Створення карти з центром на середніх координатах популяцій
    map_center = [population_data['lat'].mean(), population_data['lon'].mean()]
    my_map = folium.Map(location=map_center, zoom_start=12)

    # Нормалізація метрики магазинів для динамічного розміру іконок
    min_store_metric = silpo_stores_data['Metric Store'].min()
    max_store_metric = silpo_stores_data['Metric Store'].max()

    # Додавання маркерів для магазинів з іншою іконкою та змінним розміром
    for index, row in silpo_stores_data.iterrows():
        # Нормалізуємо розмір, щоб різниця була більш очевидною
        size = ((row['Metric Store'] - min_store_metric) / (
                    max_store_metric - min_store_metric)) * 20 + 10  # Діапазон 10 до 30
        icon_html = f'<div style="font-size: {size}px; color : red;"><i class="fa fa-star"></i></div>'
        folium.Marker(
            location=[row['lat'], row['long']],
            popup=row['Store'],
            icon=folium.DivIcon(html=icon_html)
        ).add_to(my_map)

    # Мінімальне та максимальне значення метрики популяцій
    min_metric = population_data['metric population'].min()
    max_metric = population_data['metric population'].max()

    # Створення градієнта кольорів від темно-синього до темно-помаранчевого
    colormap = cm.LinearColormap(['darkblue', 'darkorange'], vmin=min_metric, vmax=max_metric)

    # Додавання круглих маркерів для популяцій з кольорами залежно від метрики
    for index, row in population_data.iterrows():
        color = colormap(row['metric population'])  # Отримання кольору з градієнта
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['metric population'] * 2,  # Розмір кола залежить від метрики популяції
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6
        ).add_to(my_map)

    # Додати колірну шкалу до карти
    colormap.add_to(my_map)

    # Збереження карти у файл HTML
    map_file = 'geo_map_folium_dynamic_size_icons.html'
    my_map.save(map_file)

    print("Гео мапа успішно візуалізована!")

    # Відкриття карти автоматично у браузері
    webbrowser.open('file://' + os.path.realpath(map_file))

