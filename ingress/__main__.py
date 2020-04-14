import argparse
from sys import argv
from ingress import command_processor
import configparser
import sqlite3

PARSER = argparse.ArgumentParser(description='Catalyst Ingress - version 0.1')
SUB_PARSERS = PARSER.add_subparsers(dest="commands_parser")
MAKE_PARSER = SUB_PARSERS.add_parser('start')

MAKE_PARSER.add_argument('--account', metavar='L', type=str,
                         help='Account identifier for a given service.')
MAKE_PARSER.add_argument('--service', metavar='S', type=str,
                         help='The service for which the data is being collected.')

ARGS = PARSER.parse_args()

config = configparser.ConfigParser()
config.read('service.cfg')

# Connects to the local SQLite database to store captured tweets.
data_connection = sqlite3.connect(config['Datastore']['Database'])

if config is not None:
    if len(argv) <= 1:
        print('[error] No command line arguments supplied to the CLI. Terminating.')
    else:
        if ARGS.commands_parser == 'start':
            if ARGS.account is not None and ARGS.service is not None:
                print(f'[info] Starting ingress process for {ARGS.service} (user ID: {ARGS.account})')
                command_processor.start_ingress(ARGS.service, ARGS.account, config, data_connection)
            else:
                print('[error] Could not start ingress process. Ensure that the parameters are correct.')
else:
    print('[error] Could not read the configuration file. Make sure that service.cfg is properly set up.')