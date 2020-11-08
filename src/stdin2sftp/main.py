#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path, PurePath

import paramiko


def process_args():
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('Required')
    optional = parser.add_argument_group('Optional')

    required.add_argument(
        '-H', '--hostname', action='store', type=str, required=True,
        help="Target hostname or IP address."
    )

    required.add_argument(
        '-f', '--file-path', action='store', type=str, required=True,
        help="File path on remote end that will be written with data from stdin."
    )

    optional.add_argument(
        '-u', '--username', action='store', type=str, required=False,
        help="The username to be used when connecting to remote end."
    )

    optional.add_argument(
        '-p', '--port', action='store', type=str, required=False,
        help="The username to be used when connecting to remote end."
    )

    args, extra_args = parser.parse_known_args()
    if extra_args:
        if extra_args[0] != '--':
            parser.error("Custom arguments are to be passed after '--'.")
        extra_args.remove('--')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args, extra_args


def get_host_config(hostname):
    config = {}

    user_config_file = Path().joinpath(Path().home(), PurePath('.ssh/config'))

    if user_config_file.exists():
        user_config = paramiko.SSHConfig()
        user_config.parse(user_config_file.open())
        user_config_for_host = user_config.lookup(hostname)

        for i in ['user', 'hostname', 'port', 'compression']:
            if i in user_config_for_host:
                if i == 'user':
                    config['username'] = user_config_for_host[i]
                else:
                    config[i] = user_config_for_host[i]

    return config


def einfo(message):
    print(">>> [INFO] {}".format(message))


def stdin2sftp(args):
    config = get_host_config(args.hostname)

    if args.username:
        config['username'] = args.username

    if args.port:
        config['port'] = args.port

    target = args.file_path
    target_tmp = "{}.__tmp_stdin2sftp__".format(target)

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    einfo("Connecting to {} ...".format(config['hostname']))
    ssh_client.connect(**config)
    sftp_client = ssh_client.open_sftp()

    einfo("Uploading {} ...".format(target))
    sftp_client.putfo(sys.stdin.buffer, target_tmp)

    try:
        sftp_client.stat(target)
        sftp_client.remove(target)
    except IOError:
        pass

    sftp_client.rename(target_tmp, target)

    sftp_client.close()
    ssh_client.close()

    einfo('Done.')


def main():
    args, extra_args = process_args()

    stdin2sftp(args)
