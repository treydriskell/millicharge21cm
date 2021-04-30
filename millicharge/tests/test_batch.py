from pkg_resources import resource_filename

from millicharge.batch import SimGroup


def test_initialize():
    test_file = resource_filename('millicharge', 'tests/test.yaml')
    sims = SimGroup(test_file)
    sims.test()
    
