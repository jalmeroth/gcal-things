#!/usr/bin/python
import sys
import logging
import argparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


from oauth2.auth import Authenticator
from helpers import load, save


def main():
    """docstring for main"""
    # initialize Arg-parser
    parser = argparse.ArgumentParser()
    # setup Arg-parser
    parser.add_argument('-u', '--users', type=str, nargs='*', help='User ID(s)')
    parser.add_argument('-c', '--config', type=str, default="default", help='Config')
    # initialize args
    args = sys.argv[1:]
    # parse arguments
    args, unknown = parser.parse_known_args(args)
    logger.debug("args: " + str(args) + " unknown: " + str(unknown))
    
    json_file = "credentials.json"
    prefs = load(json_file)
    
    client_id = prefs.get('client_id') or raw_input('Please enter your client ID: ')
    client_secret = prefs.get('client_secret') or getpass.getpass('Please enter your client SECRET: ')
    user_ids = args.users or raw_input('Please enter your user ID(s): ').split()
    
    if client_id and client_secret and user_ids:
        
        prefs.update({
            "client_id": client_id,
            "client_secret": client_secret
        })
        
        scope = ['https://www.googleapis.com/auth/calendar.readonly']
        tokens = prefs.get('tokens')
        
        auth = Authenticator(client_id, client_secret, scope, tokens)
        
        for user_id in user_ids:
            auth.authorize(user_id)
        
        configs = prefs.get("configs", {})
        
        config = configs.get(args.config)
        
        if config:
            config.update({
                "users": user_ids
            })
        else:
            configs[args.config] = {
                "users": user_ids
            }
        
        print(configs)
        prefs["configs"] = configs
        
        prefs['tokens'] = auth.tokens
        save(prefs, json_file)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print "Quitting."