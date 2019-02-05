import argparse


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", type=str, help='query to execute',
                        choices=['synch', 'trello_to_gc', 'gc_to_trello', 'server_shutdown'])
    parsed_args = parser.parse_args(args)
    return parsed_args
