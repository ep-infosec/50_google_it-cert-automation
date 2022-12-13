#!/usr/bin/env python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import logging
import os
import sys

from concurrent import futures

import PIL
import PIL.Image


def process_options():

    kwargs = {
        'format': '[%(levelname)s] %(message)s',
    }

    parser = argparse.ArgumentParser(
        description='Thumbnail generator',
        fromfile_prefix_chars='@'
    )
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')

    parser.add_argument('--jobs', '-j', type=int, default=0,
                        help='Number of jobs to run in parallel (0 for auto)')

    options = parser.parse_args()

    if options.debug:
        kwargs['level'] = logging.DEBUG
    elif options.verbose:
        kwargs['level'] = logging.INFO
    elif options.quiet:
        kwargs['level'] = logging.ERROR
    else:
        kwargs['level'] = logging.WARN

    logging.basicConfig(**kwargs)

    return options


def process_file(filename):
    name, extension = os.path.splitext(filename)
    size = (128, 128)
    new_name = f'{name}.thumbnail'
    image = PIL.Image.open(filename)
    image.thumbnail(size)
    image.save(new_name, "JPEG")
    return new_name


def main():

    options = process_options()

    kwargs = {}
    if options.jobs:
        kwargs['max_workers'] = options.jobs

    nproc = os.cpu_count()
    tasks = []
    for _ in range(nproc):
        tasks.append([])

    i = 0
    for root, _, files in os.walk('images'):
        for basename in files:
            if not basename.endswith('.jpg'):
                continue
            filename = f'{root}/{basename}'

            tasks[i % nproc].append(filename)
            i += 1

    pids = set()
    for process_tasks in tasks:
        new_pid = os.fork()
        if new_pid:
            pids.add(new_pid)
            continue
        for filename in process_tasks:
            # new_name =
            process_file(filename)
            # print(f'Filename: {new_name}')
        sys.exit(0)

    for pid in pids:
        os.waitpid(pid, 0)

    return 0


if __name__ == "__main__":
    sys.exit(main())
