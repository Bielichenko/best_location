import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Завантажимо приклад даних
data = px.data.iris()

# Видаляємо текстові колонки перед обчисленням кореляційної матриці
numeric_data = data.select_dtypes(include=[float, int])

# Створюємо окремі графіки
heatmap_fig = px.imshow(numeric_data.corr(), text_auto=True, title="Correlation Heatmap")

sepal_fig = px.scatter(data, x='sepal_length', y='sepal_width', color='species', title="Sepal Length vs Sepal Width")

petal_fig = px.scatter(data, x='petal_length', y='petal_width', color='species', title="Petal Length vs Petal Width")

# Створимо інтерактивний дашборд
fig = go.Figure()

# Додаємо перший графік
fig.add_trace(heatmap_fig.data[0])
# Додаємо другий графік
fig.add_trace(sepal_fig.data[0])
# Додаємо третій графік
fig.add_trace(petal_fig.data[0])

# Додаємо кнопки для перемикання між графіками
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            buttons=list([
                dict(
                    args=[{"visible": [True, False, False]}],
                    label="Heatmap",
                    method="update"
                ),
                dict(
                    args=[{"visible": [False, True, False]}],
                    label="Sepal",
                    method="update"
                ),
                dict(
                    args=[{"visible": [False, False, True]}],
                    label="Petal",
                    method="update"
                )
            ]),
        )
    ]
)

# Відображаємо інтерактивний графік
fig.show()
