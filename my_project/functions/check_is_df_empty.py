def check_is_df_empty(df, stage_name):
    if df.empty:
        print(f'В обраному дата-сеті відсутні необхідні дані. Етап {stage_name} буде пропущений.')
        return True