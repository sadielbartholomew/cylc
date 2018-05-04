#!/usr/bin/env python

"""get-host-metric [HOST]"""

import sys
import os
import re
from subprocess import Popen, PIPE, CalledProcessError
import json

RAW_DISK_PATH = r'/dev/mapper/vgdesktop-tmp'  # example for now, add as arg.
COMMAND_TEMPLATES = {
    'LOAD_AVERAGE': ('uptime', r'load average:\s(.+)$',
                     r'\d+\.?\d+,\s\d+\.?\d+,\s(\d+\.?\d+)'),
    'SYSTEM_MEMORY': ('free', r'Mem:\s+(.+)', r'\d+\s+\d+\s+(\d+)'),
    'DISK_SPACE': ('df -Pk', RAW_DISK_PATH + r'\s+(.+)',
                   r'\d+\.?\d+\s+\d+\.?\d+\s+(\d+\.?\d+)')
    }

def main():
    """ Get metrics for a specific host via 'get-host-metric' command. """
    print get_host_metrics()
    sys.exit()

def run_command_string(command_str):
    """ Run a command string in the shell & return the stdout as a string
        if the command was successful, else return None. """
    process = Popen(command_str, shell=True, stdin=open(os.devnull),
                    stdout=PIPE, stderr=PIPE)
    stdoutput = process.communicate()[0]
    process.wait()
    return_code = process.returncode
    if return_code != 0:
        raise CalledProcessError(command_str, return_code)
        process.terminate()
    else:
        return str(stdoutput)

def extract_pattern(data_pattern, raw_string):
    """ Return the full group of a regular expression search on a string,
        or None if no matches are found. """
    first_match = re.search(data_pattern, raw_string)
    if first_match:
        return first_match.group(1)  # change to 0 for whole first pattern

def get_host_metrics(host=None):
    """ Return a JSON structure containing load, memory & disk space
        data for a specified host. """
    if host is None:
        host = 'localhost'
    # Code to go to specified host.
    HOST_METRIC = {}
    for metric, template in COMMAND_TEMPLATES.items():
        cmd_base, first_pattern, second_pattern = template
        full_cmd = cmd_base
        all_data = extract_pattern(first_pattern, run_command_string(full_cmd))
        HOST_METRIC[metric] = extract_pattern(second_pattern, all_data)
    return json.dumps(HOST_METRIC, indent=4)

if __name__ == "__main__":
    main()
