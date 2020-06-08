import logging
import argparse
import sys
import Gui.gui as GUI

LOGGER = logging.getLogger(__name__)

RUN_CONFIG = {}
DEFAULT_RC = 10


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-rows', required=False, default=DEFAULT_RC, help='The desired number of rows in the application\'s grid Default: {r}'.format(r=DEFAULT_RC))
    parser.add_argument(
        '-cols', required=False, default=DEFAULT_RC, help='The desired number of columns in the application\'s grid. Default: {c}'.format(c=DEFAULT_RC))
    parser.add_argument('--noop', dest='noop', action='store_true',
                        help="Provide flag --noop if you want the operation to be a no-op")
    parser.set_defaults(noop=False)

    args = parser.parse_args()
    RUN_CONFIG['ROWS'] = args.rows
    RUN_CONFIG['COLS'] = args.cols
    RUN_CONFIG['NOOP'] = args.noop

    logging.basicConfig(
        format='%(asctime)s %(message)s', level=logging.DEBUG)

    if args.noop:
        LOGGER.debug(
            'NO-OP run specified, dumping configuration parameters...')
        for k, v in RUN_CONFIG.items():
            print(k, v)
        exit(0)

    try:
        LOGGER.debug('Creating GUI object...')
        my_gui = GUI.GUI(int(RUN_CONFIG['ROWS']), int(RUN_CONFIG['COLS']))
        LOGGER.debug('Rendering GUI object...')
        my_gui.render()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        LOGGER.debug(message)


if __name__ == '__main__':
    main()
