from pkg_resources import resource_filename

from millicharge.batch import SimGroup

test_file = resource_filename('millicharge', 'tests/test.yaml')

def test_initialize():
    sims = SimGroup(test_file)
    sims.test()
    

def test_sims():
    sims = SimGroup(test_file)

    from multiprocessing import Pool

    pool = Pool(3)
    sims.run(pool=pool)

    plot = sims.global_signature()

    for name in sims.analysis.keys():
        assert sims.history_df(name).isnull().sum().sum() == 0
