from millicharge.batch import SimGroup
from millicharge.grid import SimGroupGrid

def main(filename, pool, use_grid=False):
    if use_grid: 
        sims = SimGroupGrid(filename)
    else:
        sims = SimGroup(filename)
    sims.run(pool=pool)
    pool.close()
    
if __name__ == "__main__":
    import schwimmbad

    from argparse import ArgumentParser
    parser = ArgumentParser(description="Batch runner for Global21cm sims")

    parser.add_argument("filename", help="Path to .yaml file")
    parser.add_argument("--use_grid", action="store_true", 
                        help="Calls SimGroupGrid instead of SimGroup")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ncores", dest="n_cores", default=1,
                       type=int, help="Number of processes (uses multiprocessing).")
    group.add_argument("--mpi", dest="mpi", default=False,
                       action="store_true", help="Run with MPI.")
    args = parser.parse_args()

    pool = schwimmbad.choose_pool(mpi=args.mpi, processes=args.n_cores)
    main(args.filename, pool, args.use_grid)