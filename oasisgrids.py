#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
import netCDF4 as nc
import numpy as np

from esmgrids import mom_grid, nemo_grid, t42_grid, fv300_grid, oasis_grid
from esmgrids import mom1_grid

def check_args(args):

    err = None

    if args.model_name in ['MOM', 'MOM1', 'NEMO']:
        if args.model_hgrid is None or args.model_mask is None:
            err = 'Please provide MOM or NEMO grid definition and mask files.'

    return err

def check_file_exist(files):

    err = None

    for f in files:
        if f is not None and not os.path.exists(f):
            err = "Can't find input file {}.".format(f)

    return err

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", help="""
        The the model name. Supported names are:
            - MOM   # 0.25 degree MOM
            - MOM1  # 1 degree MOM
            - NEMO
            - SPE
            - FVO
            """)
    parser.add_argument("--grid_name", default=None, help="""
        The OASIS name for the grid being created.
        """)
    parser.add_argument("--model_hgrid", default=None, help="""
        The model horizonatal grid definition file.
        Only needed for MOM and NEMO grids""")
    parser.add_argument("--model_mask", default=None, help="""
        The model mask file.
        Only needed for MOM and NEMO grids""")
    parser.add_argument("--model_cols", type=int, default=129, help="""
        Number of model columns
        Only needed for atmospheric grids""")
    parser.add_argument("--model_rows", type=int, default=64, help="""
        Number of model rows
        Only needed for atmospheric grids""")
    parser.add_argument("--grids", default="grids.nc",
                        help="The path to output OASIS grids.nc file")
    parser.add_argument("--areas", default="areas.nc",
                        help="The path to output OASIS areas.nc file")
    parser.add_argument("--masks", default="masks.nc",
                        help="The path to output OASIS masks.nc file")

    args = parser.parse_args()

    # The model name needs to be a certain length because OASIS requires that
    # grid names are exactly 4 characters long plus postfix.
    assert len(args.model_name) >= 3

    if args.grid_name is None:
        args.grid_name = args.model_name.lower()
        if args.grid_name == 'mom1':
            # We don't want this to be too similar to MOM 0.25 degree
            args.grid_name = 'mo1'

    args.model_name = args.model_name.upper()

    err = check_args(args)
    if err is not None:
        print(err, file=sys.stderr)
        parser.print_help()
        return 1

    err = check_file_exist([args.model_hgrid, args.model_mask])
    if err is not None:
        print(err, file=sys.stderr)
        parser.print_help()
        return 1

    if args.model_name == 'MOM':
        model_grid = mom_grid.MomGrid(args.model_hgrid, mask_file=args.model_mask)
        cells = ('t', 'u')
    elif args.model_name == 'MOM1':
        model_grid = mom1_grid.Mom1Grid(args.model_hgrid, mask_file=args.model_mask)
        cells = ('t', 'u')
    elif args.model_name == 'NEMO':
        model_grid = nemo_grid.NemoGrid(args.model_hgrid, mask_file=args.model_mask)
        cells = ('t', 'u', 'v')
    elif args.model_name == 'SPE':
        num_lons = args.model_cols
        num_lats = args.model_rows
        model_grid = t42_grid.T42Grid(num_lons, num_lats, 1, args.model_mask,
                                      description='Spectral')
        cells = ('t')
    elif args.model_name == 'FVO':
        num_lons = args.model_cols
        num_lats = args.model_rows
        model_grid = fv300_grid.FV300Grid(num_lons, num_lats, 1, args.model_mask,
                                          description='FV')
        cells = ('t')
    else:
        assert False

    coupling_grid = oasis_grid.OasisGrid(args.grid_name, model_grid, cells)

    coupling_grid.write_grids(args.grids)
    coupling_grid.write_areas(args.areas)
    coupling_grid.write_masks(args.masks)

if __name__ == "__main__":
    sys.exit(main())
