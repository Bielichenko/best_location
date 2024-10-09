import pandas as pd

# Можна змінити набір даних для розрахунку кореляцій та найкращої точки в залежнсті від переданих даних
# Щоб це зробити треба підставити назву нового набору в змінну file_path
file_path = "data_sets/3-2-3_dist_effect.xlsx"
populations_data = pd.read_excel(file_path, sheet_name="Population")
silpo_shops_data = pd.read_excel(file_path, sheet_name="Stores")

# Це використовується для побудови меж для області аналізу, змінювати не потрібно
file_path = "data_sets/Test.xlsx"
all_population_data = pd.read_excel(file_path, sheet_name="Population")
