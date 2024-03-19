import argparse
import asyncio
import inspect
import logging
from importlib import import_module

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


async def run_main(obj, **kwargs):
    try:
        await obj.run(**kwargs)
    except Exception as e:
        logging.exception(e)

    if hasattr(obj, 'after_run'):
        await obj.after_run()

    if hasattr(obj, 'close'):
        await obj.close()


def script_main(params):
    _client = params.pop('client')
    module = import_module('.'.join(['clients', _client]))
    for name, client in inspect.getmembers(module):
        if inspect.isclass(client) and str(client).find('clients') != -1:
            return asyncio.run(run_main(client(), **params), debug=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client')
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    params = vars(args)
    params['headless'] = True if not params['headless'] else False
    script_main(params)


if __name__ == '__main__':
    main()
