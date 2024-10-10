from setuptools import setup, find_packages

setup(
    name='temabit_test',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'activate=my_project.main:main',
        ]
    },
    author='Ваше ім’я',
    author_email='your.email@example.com',
    description='Короткий опис вашого проекту',
    url='https://github.com/yourusername/my_project',
)