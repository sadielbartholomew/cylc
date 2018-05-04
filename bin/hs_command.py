#!/usr/bin/env python

"""get-host-metric [HOST]"""

import sys
import os
import re
from subprocess import Popen, PIPE, CalledProcessError
import json

### Test by running 'python bin/hs_command.py && uptime && free && df -Pk'
LOAD_TEMPLATES = ['uptime', (1, 5, 15), r'load average:\s(.+)$',
                  r',\s', r'(\d+\.?\d+)', r'\d+\.?\d+']
MEMORY_TEMPLATES = ['free', r'Mem:\s+(.+)', r'\d+\s+\d+\s+(\d+)']
DISK_TEMPLATES = ['df -Pk', r'\s+(.+)', r'\d+\.?\d+\s+\d+\.?\d+\s+(\d+\.?\d+)']


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
        return first_match.group(1)


def process_load():
    """ describe. """
    cmd, av_times, first_patt, partition, group, non_group = LOAD_TEMPLATES
    av_dict = {}
    pattern_template = '%s' + partition + '%s' + partition + '%s'
    all_data = extract_pattern(first_patt, run_command_string(cmd))
    for index, time in enumerate(av_times):
        order_template = [non_group] * 3
        order_template[index] = group
        second_patt = pattern_template % tuple(order_template)
        av_dict[time] = extract_pattern(re.compile(second_patt), all_data)
    return av_dict


def process_memory():
    """ describe. """
    cmd, first_patt, second_patt = MEMORY_TEMPLATES
    all_memory_data = extract_pattern(first_patt, run_command_string(cmd))
    free_memory = extract_pattern(second_patt, all_memory_data)
    return free_memory


def process_disk(paths_list=[r'/dev/mapper/vgdesktop-tmp']):
    """ describe. """
    cmd, partial_first_patt, second_patt = DISK_TEMPLATES
    cmd_output = run_command_string(cmd)
    path_dict = {}
    for path in paths_list:
        first_patt = path + partial_first_patt
        all_path_data = extract_pattern(first_patt, cmd_output)
        free_space = extract_pattern(second_patt, all_path_data)
        path_dict[path] = free_space
    return path_dict


def get_host_metrics(host=None):
    """ Return a JSON structure containing load, memory & disk space
        data for a specified host. """
    if host is None:
        host = 'localhost'
    # Code to go to specified host.
    metrics = ('load', 'memory', 'disk-space')
    processing = (process_load(), process_memory(), process_disk())
    HOST_METRIC = dict(zip(metrics, processing))
    return json.dumps(HOST_METRIC, indent=4)

if __name__ == "__main__":
    main()
