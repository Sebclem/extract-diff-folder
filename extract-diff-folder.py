#!/usr/bin/env python3

"""Copy all file/folder in folder2 that is not in folder1 into the outdir
"""

from logging import log, logMultiprocessing
import os
import sys
import argparse
import filecmp
import shutil
import logging
from distutils.dir_util import copy_tree


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("folder1", help="Firts folder to compare", type=readable_path)
    parser.add_argument(
        "folder2", help="Second folder to compare (with new files)", type=readable_path
    )
    parser.add_argument("outdir", help="Output directory", type=writable_path)
    parser.add_argument('--verbose','-v', help="Show versbose output", action='store_const', const=True, default=False)


    args = parser.parse_args(arguments)

    login_l = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(
        format="[%(asctime)s][%(levelname)s]: %(message)s", level=login_l
    )

    logging.info(f"Comparing {args.folder1} to {args.folder2} ...")
    comp = filecmp.dircmp(args.folder1, args.folder2)
    diff = get_diff(comp, args.folder2)
    logging.debug(f"Diff list: {diff}")
     
    for to_cp in diff:
        destination = to_cp.replace(args.folder2, '')
        if destination.startswith('/'):
            destination = destination[1:]
        destination = os.path.join(args.outdir, destination)
        if os.path.isdir(to_cp):
            logging.info(f'Copying whole folder `{to_cp}` to `{destination}` ...')
            copy_tree(to_cp, destination)
        elif os.path.isfile(to_cp):
            logging.info(f'Copying file `{to_cp}` to `{destination}` ...')
            last_s = destination.rindex('/')
            last_folder = destination[:last_s]
            if not os.path.exists(last_folder):
                os.makedirs(last_folder)
            shutil.copy(to_cp, destination)
    return 0


def get_diff(dcmp: filecmp.dircmp, base_dir: str, to_return: list = None):
    if to_return is None:
        to_return = []

    logging.debug(f"Diff in {base_dir}...")

    for name in dcmp.right_only:
        diff_file = os.path.join(base_dir, name)
        to_return.append(diff_file)
        logging.debug(f"... {diff_file}")

    saved = base_dir
    for sub_dcmp in dcmp.subdirs.values():
        to_return = get_diff(sub_dcmp, sub_dcmp.right, to_return=to_return)
    return to_return


def readable_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir: '{path}' is not a valid path")


def writable_path(path):
    if os.path.isdir(path):
        return path
    else:
        os.makedirs(path)
        return path


if __name__ == "__main__":

    sys.exit(main(sys.argv[1:]))
