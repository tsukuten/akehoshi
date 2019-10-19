#!/usr/bin/env python3

__version__ = '0.0.1'
__author__ = 'Kenjiro Mimura'

import sys
import argparse

from ApiServer import run as api_server_run
import logging

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help='the hostname to listen on', type=str, default='0.0.0.0')
    parser.add_argument("--port", "-p", help='the port number to listen on', type=int, default=3000)
    parser.add_argument("--vervose", "-v", help='produce varvose output'                        , action='store_true')
    parser.add_argument("--version", help='print version of akehoshi and planetproj, and exit'  , action='store_true')
    parser.add_argument("--dryrun",  help='start without using i2c interface'                   , action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.version:
        print('akehoshi {}'.format(__version__))
        # print('planetproj {}'.format(planetproj.__version__))
        sys.exit()
    if args.vervose:
        logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(threadName)s:%(name)s:%(levelname)s:%(message)s')
    else:
        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s:(threadName)s:%(name)s:%(levelname)s:%(message)s')

    api_server_run(args.host, args.port, dry_run=args.dryrun)

if __name__ == '__main__':
  main()

