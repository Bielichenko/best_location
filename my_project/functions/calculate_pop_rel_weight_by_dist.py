import numpy as np


def calculate_pop_rel_weight_by_dist(distances, alpha=1):
    # Прийшов к такій не лінійній формулі, вона добре відображає
    # важливість близьких магазинів і робить віддалені магазини майже не привабливими, таким чином вони майже впливають на вибір локації
    return 1 / (1 + np.log10(1 + distances) * distances**alpha)
