#!/usr/bin/python
import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import argparse
import sys

from oauth2.auth import Authenticator
from helpers import load, save


def main():
    """docstring for main"""
    # initialize Arg-parser
    parser = argparse.ArgumentParser()
    # setup Arg-parser
    parser.add_argument('-u', '--user', type=str, help='User ID')
    # initialize args
    args = sys.argv[1:]
    # parse arguments
    args, unknown = parser.parse_known_args(args)
    logger.debug("args: " + str(args) + " unknown: " + str(unknown))
    
    json_file = "credentials.json"
    prefs = load(json_file)
    
    client_id = prefs.get('client_id')
    client_secret = prefs.get('client_secret')
    scope = ['https://www.googleapis.com/auth/calendar.readonly']
    tokens = prefs.get('tokens')
    
    auth = Authenticator(client_id, client_secret, scope, tokens)
    
    if args.user:
        auth.authorize(args.user)
        prefs['tokens'] = auth.tokens
        save(prefs, json_file)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print "Quitting."