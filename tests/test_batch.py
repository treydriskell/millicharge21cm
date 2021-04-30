from millicharge.batch import SimGroup


def test_initialize():
    sims = SimGroup('test.yaml')
    sims.test()
    
