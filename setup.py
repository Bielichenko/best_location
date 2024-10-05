from setuptools import setup, find_packages

setup(
    name='temabit_test',  # Назва вашого пакету
    version='0.1.0',  # Версія
    packages=find_packages(),  # Автоматично знаходить усі пакети
    install_requires=[
        # Сюди можна додати зовнішні залежності, наприклад:
        'requests',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'activate=my_project.main:main',  # Команда 'start', яка викликає функцію main з файлу calc_correlations_with_sectors_approach.py
        ]
    },
    author='Ваше ім’я',
    author_email='your.email@example.com',
    description='Короткий опис вашого проекту',
    url='https://github.com/yourusername/my_project',  # URL вашого проекту
)