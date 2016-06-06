#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Blockstack-client
    ~~~~~
    copyright: (c) 2014 by Halfmoon Labs, Inc.
    copyright: (c) 2015 by Blockstack.org

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
    along with Blockstack-client.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import logging
import traceback
import virtualchain
from binascii import hexlify

from ConfigParser import SafeConfigParser

from version import __version__

DEBUG = True
VERSION = __version__

DEFAULT_BLOCKSTACKD_PORT = '6264'
DEFAULT_BLOCKSTACKD_SERVER = "server.blockstack.org"

DEFAULT_DHT_MIRROR = "mirror.blockstack.org"
DEFAULT_DHT_PORT = '6266'
DEFAULT_API_PORT = 6270

DHT_MIRROR_SERVER = 'mirror.blockstack.org'
DHT_MIRROR_PORT = 6266

RESOLVER_URL = 'http://resolver.onename.com'
RESOLVER_USERS_ENDPOINT = "/v2/users/"

# initialize to default settings
BLOCKSTACKD_SERVER = DEFAULT_BLOCKSTACKD_SERVER
BLOCKSTACKD_PORT = DEFAULT_BLOCKSTACKD_PORT
WALLET_PASSWORD_LENGTH = 15

BLOCKSTACK_METADATA_DIR = os.path.expanduser("~/.blockstack/metadata")
BLOCKSTACK_DEFAULT_STORAGE_DRIVERS = "disk,dht"

DEFAULT_TIMEOUT = 30  # in secs
DEFAULT_BLOCKCHAINS = ['bitcoin', 'ethereum']

# borrowed from Blockstack
FIRST_BLOCK_MAINNET = 373601

# borrowed from Blockstack
# Opcodes
ANNOUNCE = '#'
NAME_PREORDER = '?'
NAME_REGISTRATION = ':'
NAME_UPDATE = '+'
NAME_TRANSFER = '>'
NAME_RENEWAL = NAME_REGISTRATION
NAME_REVOKE = '~'
NAME_IMPORT = ';'
NAMESPACE_PREORDER = '*'
NAMESPACE_REVEAL = '&'
NAMESPACE_READY = '!'

# borrowed from Blockstack
# these never change, so it's fine to duplicate them here
# (instead of make a circular dependency on blockstack-server)
NAME_OPCODES = {
    "NAME_PREORDER": NAME_PREORDER,
    "NAME_REGISTRATION": NAME_REGISTRATION,
    "NAME_UPDATE": NAME_UPDATE,
    "NAME_TRANSFER": NAME_TRANSFER,
    "NAME_RENEWAL": NAME_REGISTRATION,
    "NAME_IMPORT": NAME_IMPORT,
    "NAME_REVOKE": NAME_REVOKE,
    "NAMESPACE_PREORDER": NAMESPACE_PREORDER,
    "NAMESPACE_REVEAL": NAMESPACE_REVEAL,
    "NAMESPACE_READY": NAMESPACE_READY,
    "ANNOUNCE": ANNOUNCE
}

# borrowed from Blockstack
# these never change, so it's fine to duplicate them here
NAMEREC_FIELDS = [
    'name',                 # the name itself
    'value_hash',           # the hash of the name's associated profile
    'sender',               # the scriptPubKey hex that owns this name (identifies ownership)
    'sender_pubkey',        # (OPTIONAL) the public key
    'address',              # the address of the sender

    'block_number',         # the block number when this name record was created (preordered for the first time)
    'preorder_block_number', # the block number when this name was last preordered
    'first_registered',     # the block number when this name was registered by the current owner
    'last_renewed',         # the block number when this name was renewed by the current owner
    'revoked',              # whether or not the name is revoked

    'op',                   # byte sequence describing the last operation to affect this name
    'txid',                 # the ID of the last transaction to affect this name
    'vtxindex',             # the index in the block of the transaction.
    'op_fee',               # the value of the last Blockstack-specific burn fee paid for this name (i.e. from preorder or renew)

    'importer',             # (OPTIONAL) if this name was imported, this is the importer's scriptPubKey hex
    'importer_address',     # (OPTIONAL) if this name was imported, this is the importer's address
]

# borrowed from Blockstack
# these never change, so it's fine to duplicate them here
NAMESPACE_FIELDS = [
    'namespace_id',         # human-readable namespace ID
    'namespace_id_hash',    # hash(namespace_id,sender,reveal_addr) from the preorder (binds this namespace to its preorder)
    'version',              # namespace rules version

    'sender',               # the scriptPubKey hex script that identifies the preorderer
    'sender_pubkey',        # if sender is a p2pkh script, this is the public key
    'address',              # address of the sender, from the scriptPubKey
    'recipient',            # the scriptPubKey hex script that identifies the revealer.
    'recipient_address',    # the address of the revealer
    'block_number',         # block number at which this namespace was preordered
    'reveal_block',         # block number at which this namespace was revealed

    'op',                   # byte code identifying this operation to Blockstack
    'txid',                 # transaction ID at which this namespace was revealed
    'vtxindex',             # the index in the block where the tx occurs

    'lifetime',             # how long names last in this namespace (in number of blocks)
    'coeff',                # constant multiplicative coefficient on a name's price
    'base',                 # exponential base of a name's price
    'buckets',              # array that maps name length to the exponent to which to raise 'base' to
    'nonalpha_discount',    # multiplicative coefficient that drops a name's price if it has non-alpha characters
    'no_vowel_discount',    # multiplicative coefficient that drops a name's price if it has no vowels
]

# borrowed from Blockstack
# these never change, so it's fine to duplicate them here
OPFIELDS = {
    NAME_IMPORT: NAMEREC_FIELDS + [
        'recipient',            # scriptPubKey hex that identifies the name recipient
        'recipient_address'     # address of the recipient
    ],
    NAMESPACE_PREORDER: [
        'namespace_id_hash',    # hash(namespace_id,sender,reveal_addr)
        'consensus_hash',       # consensus hash at the time issued
        'op',                   # bytecode describing the operation (not necessarily 1 byte)
        'op_fee',               # fee paid for the namespace to the burn address
        'txid',                 # transaction ID
        'vtxindex',             # the index in the block where the tx occurs
        'block_number',         # block number at which this transaction occurred
        'sender',               # scriptPubKey hex from the principal that issued this preorder (identifies the preorderer)
        'sender_pubkey',        # if sender is a p2pkh script, this is the public key
        'address'               # address from the scriptPubKey
    ],
    NAMESPACE_REVEAL: NAMESPACE_FIELDS,
    NAMESPACE_READY: NAMESPACE_FIELDS + [
        'ready_block',      # block number at which the namespace was readied
    ],
    NAME_PREORDER: [
         'preorder_name_hash',  # hash(name,sender,register_addr)
         'consensus_hash',      # consensus hash at time of send
         'sender',              # scriptPubKey hex that identifies the principal that issued the preorder
         'sender_pubkey',       # if sender is a pubkeyhash script, then this is the public key
         'address',             # address from the sender's scriptPubKey
         'block_number',        # block number at which this name was preordered for the first time

         'op',                  # blockstack bytestring describing the operation
         'txid',                # transaction ID
         'vtxindex',            # the index in the block where the tx occurs
         'op_fee',              # blockstack fee (sent to burn address)
    ],
    NAME_REGISTRATION: NAMEREC_FIELDS + [
        'recipient',            # scriptPubKey hex script that identifies the principal to own this name
        'recipient_address'     # principal's address from the scriptPubKey in the transaction
    ],
    NAME_REVOKE: NAMEREC_FIELDS,
    NAME_TRANSFER: NAMEREC_FIELDS +  [
        'name_hash128',         # hash(name)
        'consensus_hash',       # consensus hash when this operation was sent
        'keep_data'             # whether or not to keep the profile data associated with the name when transferred
    ],
    NAME_UPDATE: NAMEREC_FIELDS + [
        'name_hash128',         # hash(name,consensus_hash)
        'consensus_hash'        # consensus hash when this update was sent
    ]
}

# borrowed from Blockstack
# never changes, so safe to duplicate
MAXIMUM_NAMES_PER_ADDRESS = 25


MAX_RPC_LEN = 1024 * 1024 * 1024
MAX_DHT_WRITE = (8 * 1024) - 1

MAX_NAME_LENGTH = 37        # taken from blockstack-server

CONFIG_FILENAME = "client.ini"
WALLET_FILENAME = "wallet.json"

if os.environ.get("BLOCKSTACK_TEST", None) == "1":
    # testing 
    CONFIG_PATH = os.environ.get("BLOCKSTACK_CLIENT_CONFIG", None)
    assert CONFIG_PATH is not None, "BLOCKSTACK_CLIENT_CONFIG not set"

    CONFIG_DIR = os.path.dirname(CONFIG_PATH)

else:
    CONFIG_DIR = os.path.expanduser("~/.blockstack")
    CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILENAME)

WALLET_PATH = os.path.join(CONFIG_DIR, "wallet.json")
SPV_HEADERS_PATH = os.path.join(CONFIG_DIR, "blockchain-headers.dat")
DEFAULT_QUEUE_PATH = os.path.join(CONFIG_DIR, "queues.db")

BLOCKCHAIN_ID_MAGIC = 'id'

USER_ZONEFILE_TTL = 3600    # cache lifetime for a user's zonefile

SLEEP_INTERVAL = 20  # in seconds

PREORDER_CONFIRMATIONS = 6
PREORDER_MAX_CONFIRMATIONS = 130  # no. of blocks after which preorder should be removed
MAX_TX_CONFIRMATIONS = 130
QUEUE_LENGTH_TO_MONITOR = 50
DEFAULT_POLL_INTERVAL = 600

def get_logger( debug=DEBUG ):
    logger = virtualchain.get_logger("blockstack-client")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger

log = get_logger()


def make_default_config(path=CONFIG_PATH):
    """
    Make a new config file with sane defaults.
    Return True on success
    Return False on failure
    """
    global CONFIG_PATH, BLOCKSTACKD_SERVER, BLOCKSTACKD_PORT

    # try to create
    dirname = os.path.dirname(CONFIG_PATH)
    if not os.path.isdir(dirname):
        try:
            os.makedirs(dirname)
        except:
            traceback.print_exc()
            log.error("Failed to make configuration directory '%s'." % path)
            return False

    if not os.path.exists(path):

        parser = SafeConfigParser()
        parser.add_section('blockstack-client')
        parser.set('blockstack-client', 'server', BLOCKSTACKD_SERVER)
        parser.set('blockstack-client', 'port', BLOCKSTACKD_PORT)
        parser.set('blockstack-client', 'metadata', BLOCKSTACK_METADATA_DIR)
        parser.set('blockstack-client', 'storage_drivers', BLOCKSTACK_DEFAULT_STORAGE_DRIVERS)
        parser.set('blockstack-client', 'blockchain_headers', SPV_HEADERS_PATH)
        parser.set('blockstack-client', 'advanced_mode', 'false')
        parser.set('blockstack-client', 'dht_mirror', DEFAULT_DHT_MIRROR)
        parser.set('blockstack-client', 'dht_mirror_port', DEFAULT_DHT_PORT)
        parser.set('blockstack-client', 'api_endpoint_port', str(DEFAULT_API_PORT))
        parser.set('blockstack-client', 'queue_path', str(DEFAULT_QUEUE_PATH))
        parser.set('blockstack-client', 'poll_interval', str(DEFAULT_POLL_INTERVAL))
        parser.set('blockstack-client', 'extra_servers', "")
        parser.set('blockstack-client', 'rpc_detach', "True")

        rpc_token = os.urandom(32)
        parser.set('blockstack-client', 'rpc_token', hexlify(rpc_token))

        try:
            with open(path, "w") as f:
                parser.write(f)

        except:
            traceback.print_exc()
            log.error("Failed to write default configuration file to '%s'." % path)
            return False

    return True


def find_missing(conf):
    """
    Find and return the list of missing configuration keys.
    """

    missing = []
    for k in ['server', 'port', 'metadata', 'storage_drivers']:
        if k not in conf.keys():
            missing.append(k)

    return missing


def parse_servers( servers ):
   """
   Parse the serialized list of servers.
   Raise on error
   """
   parsed_servers = []
   server_list = servers.split(",")
   for server in server_list:
      server = server.strip()
      if len(server) == 0:
          continue

      server_host, server_port = server.split(":")
      server_port = int(server_port)
      parsed_servers.append( (server_host, server_port) )

   return parsed_servers


def get_config(path=CONFIG_PATH):

    """
    Read our config file.
    Create an empty one with sane defaults if it does not exist.

    Return our configuration (as a dict) on success.
    Return None on error
    """

    global BLOCKSTACKD_SERVER, BLOCKSTACKD_PORT

    if not os.path.exists(path):
        rc = make_default_config()
        if not rc:
            log.error("No configuration file loaded from '%s'.  Cannot proceed." % path)
            return None

    # defaults
    config = {
        "server": BLOCKSTACKD_SERVER,
        "port": BLOCKSTACKD_PORT,
        "storage_drivers": BLOCKSTACK_DEFAULT_STORAGE_DRIVERS,
        "metadata": BLOCKSTACK_METADATA_DIR,
        "blockchain_headers": SPV_HEADERS_PATH,
        "advanced_mode": False,
        'dht_mirror': DEFAULT_DHT_MIRROR,
        'dht_mirror_port': DEFAULT_DHT_PORT,
        "api_endpoint_port": DEFAULT_API_PORT,
        "queue_path": str(DEFAULT_QUEUE_PATH),
        "poll_interval": str(DEFAULT_POLL_INTERVAL),
        "extra_servers": "",
        "rpc_detach": True
    }

    parser = SafeConfigParser()

    try:
        parser.read(path)
    except Exception, e:
        log.exception(e)
        return None

    if parser.has_section("blockstack-client"):

        # blockstack client section!
        if parser.has_option("blockstack-client", "server"):
            config['server'] = parser.get("blockstack-client", "server")

        if parser.has_option("blockstack-client", "port"):
            try:
                config['port'] = int(parser.get("blockstack-client", "port"))
            except:
                log.error("Invalid 'port=' setting.  Please use an integer")

        if parser.has_option("blockstack-client", "storage_drivers"):
            config['storage_drivers'] = parser.get("blockstack-client", "storage_drivers")

        if parser.has_option("blockstack-client", "metadata"):
            config['metadata'] = parser.get("blockstack-client", "metadata")

        if parser.has_option("blockstack-client", "blockchain_headers"):
            config['blockchain_headers'] = parser.get("blockstack-client", "blockchain_headers")

        if parser.has_option("blockstack-client", "advanced_mode"):
            config['advanced_mode'] = parser.get("blockstack-client", "advanced_mode")
            if config['advanced_mode'].upper() in ["TRUE", "1", "ON"]:
                config['advanced_mode'] = True
            else:
                config['advanced_mode'] = False

        if parser.has_option("blockstack-client", "dht_mirror"):
            config['dht_mirror'] = parser.get("blockstack-client", "dht_mirror")

        if parser.has_option("blockstack-client", "dht_mirror_port"):
            config['dht_mirror_port'] = parser.get("blockstack-client", "dht_mirror_port")

        if parser.has_option("blockstack-client", "api_endpoint_port"):
            config['api_endpoint_port'] = int(parser.get("blockstack-client", "api_endpoint_port"))

        if parser.has_option("blockstack-client", "rpc_token"):
            config['rpc_token'] = parser.get("blockstack-client", "rpc_token")

        if parser.has_option("blockstack-client", "queue_path"):
            config['queue_path'] = parser.get("blockstack-client", "queue_path")

        if parser.has_option("blockstack-client", "poll_interval"):
            config['poll_interval'] = int(parser.get("blockstack-client", "poll_interval"))

        if parser.has_option("blockstack-client", "extra_servers"):
            config['extra_servers'] = parse_servers( parser.get("blockstack-client", "extra_servers") )

        if parser.has_option("blockstack-client", "rpc_detach"):
            if parser.get('blockstack-client', 'rpc_detach').lower() in ['true', 'on', '1']:
                config['rpc_detach'] = True
            else:
                config['rpc_detach'] = False

    # import blockchain-specific options, if there are any
    for blockchain_name in DEFAULT_BLOCKCHAINS:
        blockchain_config = virtualchain.get_blockchain_config(blockchain_name, path)
        config.update(blockchain_config)

    if not os.path.isdir(config['metadata']):
        if config['metadata'].startswith(CONFIG_DIR):
            try:
                os.makedirs(config['metadata'])
            except:
                log.error("Failed to make directory '%s'" % (config['metadata']))
                return None

        else:
            log.error("Directory '%s' does not exist" % (config['metadata']))
            return None

    # pass along the config path and dir
    config['path'] = path
    config['dir'] = os.path.dirname(path)

    return config


def update_config(section, option, value, config_path=CONFIG_PATH):

    parser = SafeConfigParser()

    try:
        parser.read(config_path)
    except Exception, e:
        log.exception(e)
        return None

    if parser.has_option(section, option):
        parser.set(section, option, value)

        with open(config_path, 'wb') as configfile:
            parser.write(configfile)
