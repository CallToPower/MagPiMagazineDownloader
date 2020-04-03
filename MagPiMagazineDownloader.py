#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2020 Denis Meyer
#
# This file is part of MagPiMagazineDownloader
#
# Usage: python MagPiMagazineDownloader.py --start <StartIssue> --end <EndIssue>
#

"""MagPi magazine Downloader"""

__prog__ = 'MagPiMagazineDownloader'
__version__ = '1.0'

import logging
import argparse
import os
import sys
import requests

from html.parser import HTMLParser

SETTINGS = {
    'nr_of_issues': 92,
    'folder': 'MagPi',
    'url': 'https://magpi.raspberrypi.org/issues/{}/pdf',
    'issue_name': 'MagPi{}.pdf',
    # Logging configuration
    'logging': {
        'loglevel': logging.INFO,
        'date_format': '%Y-%m-%d %H:%M:%S',
        'format': '[%(asctime)s] [%(levelname)-5s] [%(module)-20s:%(lineno)-4s] %(message)s'
    }
}


def initialize_logger(loglevel, frmt, datefmt):
    '''Initializes the logger

    :param loglevel: The log level
    :param frmt: The log format
    :param datefmt: The date format
    '''
    logging.basicConfig(level=loglevel, format=frmt, datefmt=datefmt)


class MyHTMLParser(HTMLParser):

    links = []

    def handle_starttag(self, tag, attrs):
        '''Handles the start tags, in this case only link tags

        :param tag: The HTML tag
        :param attrs: The attributes
        '''
        if tag != 'a':
            return
        attr = dict(attrs)
        for attr in attrs:
            if len(attr) >= 2 and attr[0] == 'href':
                self.links.append(attr[1])


def extract_download_url(html, magazine_name):
    '''Extracts the download URLs of the magazine

    :param html: The HTML string
    :param magazine_name: The magazine name
    '''
    parser = MyHTMLParser()
    parser.links = []
    parser.feed(html)
    for link in parser.links:
        if magazine_name in link:
            return link


def download_issues(start_issue=0, end_issue=SETTINGS['nr_of_issues']):
    '''Downloads MagPi magazines

    :param start_issue: The number of the start issue, starting at 0 for the first one
    :param end_issue: The number of the end issue
    '''
    _start_issue = 0 if start_issue < 0 else start_issue
    _end_issue = _start_issue + 1 if end_issue <= _start_issue else end_issue
    chunk_size_all = 0
    dl_ok = []
    dl_failed = []
    logging.info('Downloading MagPi magazines {} to {}'.format(
        _start_issue + 1, _end_issue))
    for i in range(_start_issue, _end_issue):
        issue_nr = '{}{}'.format('0' if i + 1 < 10 else '', i + 1)
        folder = SETTINGS['folder']
        url = SETTINGS['url'].format(issue_nr)
        magazine_name = SETTINGS['issue_name'].format(issue_nr)
        chunk_size = 1024 * 1024  # in bytes

        logging.info('{:2} | MagPi issue {}'.format(issue_nr, issue_nr))
        try:
            logging.info('{:2} | Downloading metadata'.format(issue_nr))
            r = requests.get(url)
            logging.info('{:2} | Extracting download link'.format(issue_nr))
            download_url = extract_download_url(str(r.content), magazine_name)

            logging.info('{:2} | Downloading file "{}"'.format(
                issue_nr, magazine_name))
            # logging.info('{:2} | Downloading file "{}" from "{}"'.format(
            #    issue_nr, magazine_name, download_url))
            r = requests.get(download_url, stream=True)
            chunk_size_full = 0
            if not os.path.exists(folder):
                os.mkdir(folder)
            full_file_name = '{}/{}'.format(folder, magazine_name)
            with open(full_file_name, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    chunk_size_full += chunk_size
                    fd.write(chunk)
            logging.info('{:2} | Successfully downloaded {} MB'.format(
                issue_nr, chunk_size_full / 1024 / 1024))
            chunk_size_all += chunk_size_full
            logging.info('{:2} | Saved to file "{}"'.format(
                issue_nr, full_file_name))
            dl_ok.append(magazine_name)
        except Exception as exc:
            logging.info('{:2} | Failed to download "{}": {}'.format(
                issue_nr, magazine_name, exc))
            dl_failed.append(magazine_name)

    if chunk_size_all:
        logging.info('Downloaded {} MagPi magazine{} with a total of {} MB'.format(
            len(dl_ok), 's' if len(dl_ok) != 1 else '', chunk_size_all / 1024 / 1024))
        if dl_failed:
            logging.info(
                'Failed to download {} MagPi magazines:'.format(len(dl_failed)))
            for m in dl_failed:
                logging.info('\t- {}'.format(m))


if __name__ == '__main__':
    initialize_logger(SETTINGS['logging']['loglevel'], SETTINGS['logging']
                      ['format'], SETTINGS['logging']['date_format'])

    # Parse command line arguments
    parser = argparse.ArgumentParser(prog=__prog__)
    parser.add_argument('--start', required=False, type=int,
                        help='Start issue (Starts at 1)', default=1)
    parser.add_argument('--end', required=False, type=int,
                        help='End issue (Ends at {}'.format(SETTINGS['nr_of_issues']), default=SETTINGS['nr_of_issues'])
    args = parser.parse_args()

    # Validate arguments
    if args.start < 1:
        logging.info('Invalid start issue "{}"'.format(args.start))
        sys.exit()
    if args.start > SETTINGS['nr_of_issues']:
        logging.info('Invalid start issue "{}": Must be less than nr of issues {}'.format(
            args.end, SETTINGS['nr_of_issues']))
        sys.exit()
    if args.end < args.start:
        logging.info('Invalid end issue "{}": Must be greater than start issue {}'.format(
            args.end, args.start))
        sys.exit()
    if args.end > SETTINGS['nr_of_issues']:
        logging.info('Invalid end issue "{}": Must be less than nr of issues {}'.format(
            args.end, SETTINGS['nr_of_issues']))
        sys.exit()

    download_issues(start_issue=args.start - 1, end_issue=args.end - 1)
