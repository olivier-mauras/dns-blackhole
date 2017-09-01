#!/usr/bin/env python3.6
# encoding: utf-8
'''
'''
import yaml
import requests
import os
import sys

# Required for correct utf8 formating on python2
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# Default variables
DEFAULT_CONFIG_PATHS = ['/etc/blackhole/blackhole.yml',
                        './blackhole.yml',
                        '{0}/.blackhole.yml'.format(os.getenv("HOME"))
                       ]
CACHE = '/var/cache/blackhole'
LOG = '/var/log/blackhole/blackhole.log'
WHITELIST = '/etc/blackhole/whitelist'
BLACKLIST = '/etc/blackhole/blacklist'


# Load yaml config
def load_config():
    config_file = None

    # Save its path if we find one
    for config in DEFAULT_CONFIG_PATHS:
        if os.path.isfile(config):
            config_file = config
            break

    # Exit if not
    if config_file is None:
        print('Unable to find a config file in: {0}'.format(DEFAULT_CONFIG_PATHS))
        sys.exit()
    else:
        try:
            f = open(config_file, 'r')
        except:
            print('Error opening {0}: {1}'.format(config_file, sys.exc_info()[0]))
            sys.exit()

        try:
            yaml_config = yaml.load(f)
        except yaml.YAMLError as exc:
            print("Error in configuration file: {0}".format(exc))

    return yaml_config


def get_general(config):
    if 'blackhole' in config:
        if 'general' in config['blackhole']:
            if 'cache' in config['blackhole']['general']:
                cache = config['blackhole']['general']['cache']
            else:
                cache = CACHE

            if 'log' in config['blackhole']['general']:
                log = config['blackhole']['general']['log']
            else:
                log = LOG

            if 'whitelist' in config['blackhole']['general']:
                whitelist = config['blackhole']['general']['whitelist']
            else:
                whitelist = WHITELIST

            if 'blacklist' in config['blackhole']['general']:
                blacklist = config['blackhole']['general']['blacklist']
            else:
                blacklist = BLACKLIST
        else:
            print('Missing general section in config file')
            sys.exit()
    else:
        print('Cannot find blackhole section in config file.')
        sys.exit()

    return cache, log, whitelist, blacklist


def get_service(config):
    if 'blackhole' in config:
        if 'config' in config['blackhole']:
            zone_file = config['blackhole']['config']['zone_file']
            zone_data = config['blackhole']['config']['zone_data']
            lists = config['blackhole']['config']['blackhole_lists']
        else:
            print('Cannot find "config" section in config file.')
            sys.exit()
    else:
        print('Cannot find blackhole section in config file.')
        sys.exit()

    return zone_file, zone_data, lists


def process_host_file_url(bh_list, white_list, zone_data, host_file_urls):
    for url in host_file_urls:
        try:
            r = requests.get(url)
        except:
            print('Request to {0} failed: {1}'.format(url, sys.exc_info()[0]))
            sys.exit()

        if r.status_code != 200:
            # Continue to next url
            continue
        else:
            for line in r.iter_lines():
                try:
                    # If utf8 decode fails jumps next item
                    line = line.decode('utf-8')
                except:
                    continue

                if line.startswith('127.0.0.1') or line.startswith('0.0.0.0'):
                    # Remove ip
                    try:
                        n_host = line.split('127.0.0.1')[1]
                    except IndexError:
                        n_host = line.split('0.0.0.0')[1]
                    except:
                        continue

                    # Fix some host lists having \t instead of space
                    if n_host.startswith('\t'):
                        n_host = n_host.lstrip('\t')

                    # Ensure we only keep host as some list add comments
                    n_host = n_host.split('#')[0].rstrip()
                    # Some leave ports
                    n_host = n_host.split(':')[0]
                    # Some leave spaces prefixed
                    n_host = n_host.replace(' ', '')
                    # Some put caps
                    n_host = n_host.lower()

                    # Remove local domains
                    if n_host == 'localhost.localdomain' or n_host == 'localhost':
                        continue

                    # Now add the hosts to the list
                    if n_host not in white_list:
                        bh_list.append(zone_data.format(**{'domain': n_host}))

    return bh_list


def process_easylist_url(bh_list, white_list, zone_data, easy_list_url):
    for url in easy_list_url:
        try:
            r = requests.get(url)
        except:
            print('Request to {0} failed: {1}'.format(url, sys.exc_info()[0]))
            sys.exit()

        if r.status_code != 200:
            # Continue to next url
            continue
        else:
            for line in r.iter_lines():
                try:
                    # If utf8 decode fails jumps next item
                    line = line.decode('utf-8')
                except:
                    continue

                if line.startswith('||'):
                    # I don't want to bother with wildcards
                    if '*' in line:
                        continue

                    # Keep domain
                    try:
                        n_host = line.split('^')[0]
                    except:
                        continue

                    # and get rid of those '$'
                    try:
                        n_host = n_host.split('$')[0]
                    except IndexError:
                        pass

                    # Remove leading '||'
                    n_host = n_host.lstrip('||')

                    # Some entries are urls
                    if '/' in n_host:
                        n_host = n_host.split('/')[0]

                    # Some entries are no domains...
                    if '.' not in n_host:
                        continue

                    # Some leave a final '.'
                    n_host = n_host.rstrip('.')

                    # Some put caps
                    n_host = n_host.lower()

                    # Now add the hosts to the list
                    if n_host not in white_list:
                        bh_list.append(zone_data.format(**{'domain': n_host}))

    return bh_list


def process_disconnect_url(bh_list, white_list, zone_data, d_url, d_cat):
    try:
        r = requests.get(d_url)
    except:
        print('Request to {0} failed: {1}'.format(d_url, sys.exc_info()[0]))
        sys.exit()

    if r.status_code == 200:
        try:
            j = r.json()
        except:
            print('Seems like we did not fetch a json dict')
            sys.exit()
    else:
        print('Incorrect return code from {0}: {1}'.format(d_url, r.status_code))
        sys.exit()

    if 'categories' in j:
        for category in j['categories']:
            if category in d_cat:
                for sub_dict in j['categories'][category]:
                    for entity in sub_dict:
                        for main_url in sub_dict[entity]:
                            h_list = sub_dict[entity][main_url]
                            if isinstance(h_list, list):
                                for host in h_list:
                                    if host not in white_list:
                                        bh_list.append(zone_data.format(**{'domain': host}))
    else:
        print('"categories" key not found in dict, nothing to process')
        return bh_list

    # Return the list sorted
    return bh_list


def process_black_list(bh_list, black_list, zone_data):
    for bl_host in black_list:
        bh_list.append(zone_data.format(**{'domain': bl_host}))

    # Return the list sorted
    return sorted(list(set(bh_list)))


def build_bw_lists(bh_whitelist, bh_blacklist):
    white_list = []
    black_list = []
    w = None
    b = None

    # Open whitelist
    try:
        w = open(bh_whitelist, 'r')
    except:
        print('Cannot open {0}: {1}'.format(bh_whitelist, sys.exc_info()[0]))

    # Open blacklist
    try:
        b = open(bh_blacklist, 'r')
    except:
        print('Cannot open {0}: {1}'.format(bh_blacklist, sys.exc_info()[0]))

    # Loop over the line and append them to the the list
    if w:
        for line in w.readlines():
            # If there's a comment
            if '#' in line:
                white_list.append(line.split('#')[0].strip())
            else:
                white_list.append(line.strip())

    if b:
        for line in b.readlines():
            # If there's a comment
            if '#' in line:
                black_list.append(line.split('#')[0].strip())
            else:
                black_list.append(line.strip())

    return white_list, black_list


def make_zone_file(bh_list, zone_file):
    f = open(zone_file, 'w')
    f.write('\n'.join(bh_list))


def main():
    # Get config as dict from yaml file
    config = load_config()

    # Get general settings
    cache, log, bh_white, bh_black = get_general(config)

    # Get service config
    zone_file, zone_data, lists = get_service(config)

    # Build whitelist/blacklist
    white_list, black_list = build_bw_lists(bh_white, bh_black)

    # Now populate bh_list based on our config
    bh_list = []
    # First process host files if set
    if 'hosts' in lists:
        bh_list = process_host_file_url(bh_list, white_list, zone_data, lists['hosts'])

    # Then easylist
    if 'easylist' in lists:
        bh_list = process_easylist_url(bh_list, white_list, zone_data, lists['easylist'])

    # Finally disconnect
    if 'disconnect' in lists:
        d_url = lists['disconnect']['url']
        d_cat = lists['disconnect']['categories']
        bh_list = process_disconnect_url(bh_list,
                                         white_list,
                                         zone_data,
                                         d_url,
                                         d_cat)

    # Add hosts from blacklist and return sorted bh_list
    bh_list = process_black_list(bh_list, black_list, zone_data)

    # Create pdns file
    make_zone_file(bh_list, zone_file)


if __name__ == "__main__":
    main()
