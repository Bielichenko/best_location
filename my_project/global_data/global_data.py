import pandas as pd

file_path = "data_sets/Test.xlsx"
populations_data = pd.read_excel(file_path, sheet_name='Population')
silpo_shops_data = pd.read_excel(file_path, sheet_name='Stores')

file_path = "data_sets/Test.xlsx"
all_population_data = pd.read_excel(file_path, sheet_name='Population')

# populations_data = regulate_source_data(population_data_source, (30.50, 30.55, 50.40, 50.55))
