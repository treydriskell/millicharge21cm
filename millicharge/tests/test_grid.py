from pkg_resources import resource_filename

import numpy as np

from millicharge.grid import SimGroupGrid

test_file = resource_filename("millicharge", "tests/grid_test.yaml")


def test_setup():
    grid = SimGroupGrid(test_file)

    sigma_grid = grid.grid_info["sigma_dmb"]
    m_grid = grid.grid_info["m_dmb"]

    pf_compare = None
    for i, sigma in enumerate(sigma_grid):
        for j, m in enumerate(m_grid):
            name = f"{i}_{j}"
            sim = grid[name]
            assert sim.pf["sigma_dmeff"] == sigma
            assert sim.pf["m_dmeff"] == m
