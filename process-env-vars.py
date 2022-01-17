#! /usr/bin/env python3

# psutil library required

import argparse
import json
import os
import psutil
from typing import Dict, List

parser = argparse.ArgumentParser(
    description='display the environment variables for one or more processes')
parser.add_argument('--pid',
                    dest='pids',
                    type=int,
                    action='append',
                    help='Process ID')
parser.add_argument('--name',
                    dest='names',
                    action='append',
                    help='find processes by name (exact match)')
parser.add_argument('--user',
                    dest='users',
                    action='append',
                    help='Process user')
parser.add_argument(
    '--filter',
    action='append',
    dest='filter',
    help='filter processes containing the filter value (case sensitive)')
parser.add_argument(
    '--ignore',
    action='append',
    dest='ignore',
    help='ignore processes containing the ignore value (case sensitive)')
parser.add_argument('--json', action='store_true', help='output to JSON')


def get_env_vars(proc) -> Dict[str, str]:
    try:
        if len(proc.environ().items()) == 0:
            return {}
        return proc.environ()
    except psutil.AccessDenied:
        return {'env_vars_error': 'access denied'}
    except psutil.ZombieProcess:
        return {'env_vars_error': 'zombie process'}


def get_command(proc) -> List[str]:
    proc_data = proc.as_dict()

    if proc_data['cmdline'] is None or (type(proc_data['cmdline']) == list
                                        and len(proc_data['cmdline']) == 0):
        return None

    if type(proc_data['cmdline']) == str:
        return [proc_data['cmdline']]

    return proc_data['cmdline']


class Process:
    pid: str
    name: str
    command: List[str]
    env_vars: Dict[str, str]
    username: str

    def __init__(self, proc):
        proc_data = proc.as_dict()
        self.pid = proc_data['pid']
        self.name = proc_data['name']
        self.command = get_command(proc)
        self.env_vars = get_env_vars(proc)
        self.username = proc_data['username']

    def as_dict(self) -> Dict:
        return {
            'pid': self.pid,
            'name': self.name,
            'command': self.command,
            'env_vars': self.env_vars,
            'username': self.username
        }

    def json(self):
        return json.dumps(self.as_dict())

    def __repr__(self) -> str:
        indent = '  '

        def command():
            if self.command is None:
                return 'None'

            return f'{os.linesep}{indent}' + f'{os.linesep}{indent}'.join(
                self.command)

        def env_vars():
            if len(self.env_vars.items()) == 0:
                return 'None'

            if self.env_vars.get('env_vars_error'):
                return f'None ({self.env_vars.get("env_vars_error")})'

            return os.linesep + os.linesep.join([
                f'{indent}{key}={value}'
                for (key, value) in self.env_vars.items()
            ])

        return os.linesep.join([
            f'Process: {self.pid} {self.name} ({self.username})',
            f'Command: {command()}', f'Environment Variables: {env_vars()}'
        ])


class ProcessList:
    processes: List[Process]

    def __init__(self):
        args = parser.parse_args()
        self.processes = []

        for proc in psutil.process_iter(['pid', 'username', 'name']):
            if args.users and proc.info['username'] not in args.users:
                continue

            if args.pids:
                if proc.info['pid'] in args.pids:
                    self.processes.append(Process(proc))

            if args.names:
                if proc.info['name'] in args.names:
                    self.processes.append(Process(proc))

            # Supplying a --pid or --name short-circuits other filters
            if args.pids or args.names:
                continue

            if args.filter and not any(proc_name in proc.info['name']
                                       for proc_name in args.filter):
                continue

            if args.ignore and any(proc_name in proc.info['name']
                                   for proc_name in args.ignore):
                continue

            self.processes.append(Process(proc))

    def as_json(self) -> str:
        return json.dumps([p.as_dict() for p in self.processes])


if __name__ == '__main__':
    process_list = ProcessList()

    if parser.parse_args().json:
        print(process_list.as_json())
    else:
        for process in process_list.processes:
            print(process)
