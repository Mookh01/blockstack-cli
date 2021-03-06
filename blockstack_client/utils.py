#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    Blockstack-client
    ~~~~~
    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2016 by Blockstack.org

    This file is part of Blockstack-client.

    Blockstack-client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Blockstack-client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Blockstack-client. If not, see <http://www.gnu.org/licenses/>.
"""

import json

from config import get_logger
log = get_logger()

def exit_with_error(error_message, help_message=None):

    result = {'error': error_message}

    if help_message is not None:
        result['help'] = help_message
    print_result(result)
    exit(0)


def pretty_dump(data):
    """ format data
    """

    if type(data) is list:

        if len(data) == 0:
            # we got an empty array
            data = {}
        else:
            # Netstring server responds with [{data}]
            log.debug("converting [] to {}")
            data = data[0]

    if type(data) is not dict:
        try:
            data = json.loads(data)
        except Exception as e:
            # data is not valid json, convert to json
            data = {'result': data}

    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


def pretty_print(data):

    try:
        data = data[0]
    except:
        pass

    if type(data) is not dict:
        try:
            data = json.loads(data)
        except Exception as e:
            log.debug("ERROR in pretty print: %s" % e)

    print pretty_dump(data)


def print_result(json_str):
    data = pretty_dump(json_str)

    if data != "{}":
        print data


def satoshis_to_btc(satoshis):

    return satoshis * 0.00000001


def btc_to_satoshis(btc):

    return int(btc / 0.00000001)

