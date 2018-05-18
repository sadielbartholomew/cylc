#!/usr/bin/env python2

# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2018 NIWA & British Crown (Met Office) & Contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Run command on a remote, (i.e. a remote [user@]host)."""

import os
import sys
import shlex
import signal
from time import sleep
from pipes import quote
from posix import WIFSIGNALED
from random import shuffle
import unittest
import json

# CODACY ISSUE:
#   Consider possible security implications associated with Popen module.
# REASON IGNORED:
#   Subprocess is needed, but we use it with security in mind.
from subprocess import Popen, PIPE, CalledProcessError

import cylc.flags
from cylc.cfgspec.glbl_cfg import glbl_cfg
from cylc.version import CYLC_VERSION


def get_proc_ancestors():
    """Return list of parent PIDs back to init."""
    pid = os.getpid()
    ancestors = []
    while True:
        p = Popen(["ps", "-p", str(pid), "-oppid="], stdout=PIPE, stderr=PIPE)
        ppid = p.communicate()[0].strip()
        if not ppid:
            return ancestors
        ancestors.append(ppid)
        pid = ppid


def watch_and_kill(proc):
    """ Kill proc if my PPID (etc.) changed - e.g. ssh connection dropped."""
    gpa = get_proc_ancestors()
    while True:
        sleep(0.5)
        if proc.poll() is not None:
            break
        if get_proc_ancestors() != gpa:
            sleep(1)
            os.kill(proc.pid, signal.SIGTERM)
            break


def remote_cylc_cmd(cmd, user=None, host=None, capture=False, manage=False,
                    ssh_login_shell=None, ssh_cylc=None, stdin=None):
    """Run a given cylc command on another account and/or host.

    Arguments:
        cmd (list): command to run remotely.
        user (string): user ID for the remote login.
        host (string): remote host name. Use 'localhost' if not specified.
        capture (boolean):
            If True, set stdout=PIPE and return the Popen object.
        manage (boolean):
            If True, watch ancestor processes and kill command if they change
            (e.g. kill tail-follow commands when parent ssh connection dies).
        ssh_login_shell (boolean):
            If True, launch remote command with `bash -l -c 'exec "$0" "$@"'`.
        ssh_cylc (string):
            Location of the remote cylc executable.
        stdin (file):
            If specified, it should be a readable file object.
            If None, it will be set to `open(os.devnull)` and the `-n` option
            will be added to the SSH command line.

    Return:
        If capture=True, return the Popen object if created successfully.
        Otherwise, return the exit code of the remote command.
    """
    if host is None:
        host = "localhost"
    if user is None:
        user_at_host = host
    else:
        user_at_host = '%s@%s' % (user, host)

    # Build the remote command
    command = shlex.split(
        str(glbl_cfg().get_host_item('ssh command', host, user)))
    if stdin is None:
        command.append('-n')
        stdin = open(os.devnull)
    command.append(user_at_host)

    # Pass cylc version through.
    command += ['env', r'CYLC_VERSION=%s' % CYLC_VERSION]

    if ssh_login_shell is None:
        ssh_login_shell = glbl_cfg().get_host_item(
            'use login shell', host, user)
    if ssh_login_shell:
        # A login shell will always source /etc/profile and the user's bash
        # profile file. To avoid having to quote the entire remote command
        # it is passed as arguments to bash.
        command += ['bash', '--login', '-c', quote(r'exec "$0" "$@"')]
    if ssh_cylc is None:
        ssh_cylc = glbl_cfg().get_host_item('cylc executable', host, user)
        if not ssh_cylc.endswith('cylc'):
            raise ValueError(
                r'ERROR: bad cylc executable in global config: %s' % ssh_cylc)
    command.append(ssh_cylc)
    command += cmd
    if cylc.flags.debug:
        sys.stderr.write('%s\n' % command)
    if capture:
        stdout = PIPE
    else:
        stdout = None
    # CODACY ISSUE:
    #   subprocess call - check for execution of untrusted input.
    # REASON IGNORED:
    #   The command is read from the site/user global config file, but we check
    #   above that it ends in 'cylc', and in any case the user could execute
    #   any such command directly via ssh.

    proc = Popen(command, stdout=stdout, stdin=stdin)
    if capture:
        return proc
    else:
        if manage:
            watch_and_kill(proc)
        res = proc.wait()
        if WIFSIGNALED(res):
            sys.stderr.write(
                'ERROR: remote command terminated by signal %d\n' % res)
        elif res:
            sys.stderr.write('ERROR: remote command failed %d\n' % res)
        return res


def remrun(dry_run=False, forward_x11=False, abort_if=None):
    """Short for RemoteRunner().execute(...)"""
    return RemoteRunner().execute(dry_run, forward_x11, abort_if)


class RemoteRunner(object):
    """Run current command on a remote host.

    If owner or host differ from username and localhost, strip the
    remote options from the commandline and reinvoke the command on the
    remote host by non-interactive ssh, then exit; else do nothing.

    To ensure that users are aware of remote re-invocation info is always
    printed, but to stderr so as not to interfere with results.

    """

    def __init__(self, argv=None):
        self.owner = None
        self.host = None
        self.ssh_login_shell = None
        self.ssh_cylc = None
        self.argv = argv or sys.argv
        self.appoint_host = None

        cylc.flags.verbose = '-v' in self.argv or '--verbose' in self.argv

        argv = self.argv[1:]
        self.args = []

        # Detect and replace host and owner options
        while argv:
            arg = argv.pop(0)
            if arg.startswith('--user='):
                self.owner = arg.replace('--user=', '')
            elif arg.startswith('--host='):
                self.host = arg.replace('--host=', '')
            elif arg.startswith('--ssh-cylc='):
                self.ssh_cylc = arg.replace('--ssh-cylc=', '')
            elif arg == '--login':
                self.ssh_login_shell = True
            elif arg == '--no-login':
                self.ssh_login_shell = False
            elif arg == '--host-select':
                self.appoint_host = True
            elif arg == '--no-host-select':
                self.appoint_host = False
            else:
                self.args.append(arg)

        # Manage run host appointment
        if self.host is None and self.appoint_host:
            self.host = HostAppointer().appoint_host()
            if self.host == 'localhost':
                self.host = None  # localhost applied via None by default.

        if self.owner is None and self.host is None:
            self.is_remote = False
        else:
            from cylc.hostuserutil import is_remote
            self.is_remote = is_remote(self.host, self.owner)

    def execute(self, dry_run=False, forward_x11=False, abort_if=None):
        """Execute command on remote host.

        Returns False if remote re-invocation is not needed, True if it is
        needed and executes successfully otherwise aborts.

        """
        if not self.is_remote:
            return False

        if abort_if is not None and abort_if in sys.argv:
            sys.stderr.write(
                "ERROR: option '%s' not available for remote run\n" % abort_if)
            return True

        # Build the remote command
        command = shlex.split(glbl_cfg().get_host_item(
            'ssh command', self.host, self.owner))
        if forward_x11:
            command.append('-Y')

        user_at_host = ''
        if self.owner:
            user_at_host = self.owner + '@'
        if self.host:
            user_at_host += self.host
        else:
            user_at_host += 'localhost'
        command.append(user_at_host)

        # Pass cylc version through.
        command += ['env', quote(r'CYLC_VERSION=%s' % CYLC_VERSION)]
        if os.getenv('CYLC_UTC') in ["True", "true"]:
            command.append(quote(r'CYLC_UTC=True'))
            command.append(quote(r'TZ=UTC'))

        # Use bash -l?
        ssh_login_shell = self.ssh_login_shell
        if ssh_login_shell is None:
            ssh_login_shell = glbl_cfg().get_host_item(
                'use login shell', self.host, self.owner)
        if ssh_login_shell:
            # A login shell will always source /etc/profile and the user's bash
            # profile file. To avoid having to quote the entire remote command
            # it is passed as arguments to the bash script.
            command += ['bash', '--login', '-c', quote(r'exec "$0" "$@"')]

        # 'cylc' on the remote host
        if self.ssh_cylc:
            command.append(self.ssh_cylc)
        else:
            command.append(glbl_cfg().get_host_item(
                'cylc executable', self.host, self.owner))

        # /path/to/cylc-foo => foo
        command.append(os.path.basename(self.argv[0])[5:])

        if cylc.flags.verbose or os.getenv('CYLC_VERBOSE') in ["True", "true"]:
            command.append(r'--verbose')
        if cylc.flags.debug or os.getenv('CYLC_DEBUG') in ["True", "true"]:
            command.append(r'--debug')
        for arg in self.args:
            command.append(quote(arg))
            # above: args quoted to avoid interpretation by the shell,
            # e.g. for match patterns such as '.*' on the command line.

        if cylc.flags.debug:
            sys.stderr.write(' '.join(quote(c) for c in command) + '\n')

        if dry_run:
            return command

        try:
            popen = Popen(command)
        except OSError as exc:
            sys.exit(r'ERROR: remote command invocation failed %s' % exc)

        res = popen.wait()
        if WIFSIGNALED(res):
            sys.exit(r'ERROR: remote command terminated by signal %d' % res)
        elif res:
            sys.exit(r'ERROR: remote command failed %d' % res)
        else:
            return True


class EmptyHostList(Exception):
    """Exception to be raised if there are no hosts considered valid for
       appointment given the 'run hosts' and 'run host select' global
       configuration specifications."""

    def __str__(self):
        return "No hosts currently compatible with the global configuration."


class HostAppointer(object):
    """Determine the one host most suitable to (re-)run a suite on from all
       'run hosts' and given the 'run host selection' ranking options
       as specified (else taken as default) in the global configuration.
    """

    CMD_BASE = "get-host-metric"  # 'cylc' prepended by remote_cylc_cmd.
    try:
        HOSTS = glbl_cfg().get(['suite servers', 'run hosts'])
        RANK_METHOD = glbl_cfg().get(
            ['suite servers', 'run host select', 'rank'])
        THRESHOLDS = glbl_cfg().get(
            ['suite servers', 'run host select', 'thresholds'])
    except KeyError:  # Catch for unittest which updates these internally.
        HOSTS = []
        RANK_METHOD = 'random'
        THRESHOLDS = None

    def __init__(self):
        self.use_disk_path = "/"
        self.opt_mapping = {
            "load:1": ("--load", ["load", "1 min"]),
            "load:5": ("--load", ["load", "5 min"]),
            "load:15": ("--load", ["load", "15 min"]),
            "memory": ("--memory", ["memory"]),
            "disk-space": ("--disk-space=" + self.use_disk_path,
                           ["disk-space", self.use_disk_path])
        }
        self.PARSED_THRESHOLDS = self.parse_thresholds(self.THRESHOLDS)

    @staticmethod
    def parse_thresholds(raw_thresholds_spec):
        if not raw_thresholds_spec:
            return {}
        valid_thresholds = {}
        for threshold in raw_thresholds_spec.split(';'):
            threshold = threshold.strip()
            try:
                measure, cutoff = threshold.split(' ')
            except (AttributeError, ValueError):
                print "Invalid threshold component '%s'." % threshold
                raise
            try:
                if measure in ("load:1", "load:5", "load:15"):
                    cutoff = float(cutoff)
                elif measure in ("memory", "disk-space"):
                    cutoff = int(cutoff)
                else:
                    raise AttributeError("Invalid threshold measure '%s'." %
                                         measure)
            except ValueError:
                print "Threshold value '%s' of wrong type." % cutoff
                raise
            else:
                valid_thresholds[measure] = cutoff
        return valid_thresholds

    @staticmethod
    def selection_complete(host_list):
        """Check length of a list (of hosts); for zero items raise an error,
           for one return that item, else (for multiple items) return False."""
        if len(host_list) == 0:
            raise EmptyHostList()
        elif len(host_list) == 1:
            return host_list[0]
        else:
            return False

    @staticmethod
    def access_datum(nested_data, ordered_keylist):
        """Return a non-dictionary value from a nested dictionary or loaded
           JSON structure (constructed from associative arrays only i.e. with
           no sequences) given a list of keys of arbitrary length, ordered for
           valid lookup. For invalid keys or dict end value return None."""
        data_level = nested_data
        for key in ordered_keylist:
            try:
                if isinstance(data_level[key], dict):
                    if key == ordered_keylist[-1]:
                        raise ValueError("ERROR: end value is a dict:\n%s."
                                         % data_level[key])
                    data_level = data_level[key]
                    continue
                else:
                    return data_level[key]
            except KeyError:
                print "ERROR: invalid list of keys %s for structure:\n%s." % (
                    key, nested_data)
                raise

    def trivial_choice(self, host_list, ignore_if_thresholds_prov=False):
        """Test if a list of hosts has length zero or one, else if the ranking
           method is random (optionally testing these only if no thresholds
           are provided); if so return a host selected appropriately."""
        if ignore_if_thresholds_prov and self.PARSED_THRESHOLDS:
            return False
        if self.selection_complete(host_list):
            return self.selection_complete(host_list)
        elif self.RANK_METHOD == 'random':
            shuffle(host_list)
            return host_list[0]
        else:
            return False

    def process_get_host_metric_cmd(self):
        """Return the command string to run 'cylc get host metric' with (only)
           the required options given rank method and thresholds specified."""
        cmd = self.CMD_BASE
        if self.RANK_METHOD != 'random':
            cmd = " ".join((cmd, self.opt_mapping[self.RANK_METHOD][0]))
        if self.PARSED_THRESHOLDS:
            for measure in self.PARSED_THRESHOLDS.keys():
                if measure != self.RANK_METHOD:
                    cmd = " ".join((cmd, self.opt_mapping[measure][0]))
        return cmd

    def remove_bad_hosts(self, cmd_with_opts, mock_stats=False):
        """Run 'get-host-metric' on each host & store extracted stats for
           'good' hosts only. Ignore 'bad' hosts whereby either metric data
           cannot be accessed from the command or at least one metric value
           does not pass a specified threshold."""
        host_stats = {}
        if mock_stats:  # Create fake data for unittest purposes (only).
            host_stats = mock_stats
        else:
            for host in self.HOSTS:
                if host == 'localhost':
                    process = remote_cylc_cmd(cmd_with_opts.split(),
                                              capture=True)
                else:
                    process = remote_cylc_cmd(cmd_with_opts.split(),
                                              capture=True, host=host)
                metric = process.communicate()[0]
                process.wait()
                ret_code = process.returncode
                if ret_code:
                    # Can't access data => designate as 'bad' host & ignore.
                    print "Can't obtain metric data from host '%s'." % host
                    raise CalledProcessError(ret_code, cmd_with_opts.split())
                else:
                    host_stats[host] = json.loads(metric)

        bad_hosts = []  # Get errors if alter dict during iteration. Use list.
        for host in host_stats:
            for measure, cutoff in self.PARSED_THRESHOLDS.items():
                datum = self.access_datum(host_stats[host],
                                          self.opt_mapping[measure][1])
                # Cutoff is a minimum or maximum depending on measure context.
                if ((measure in ("memory", "disk-space") and
                    datum < cutoff) or
                    (measure in ("load:1", "load:5", "load:15")
                     and datum > cutoff)):
                    bad_hosts.append(host)
                    continue
        return dict((host, metr) for host, metr in
                    host_stats.items() if host not in bad_hosts)

    def rank_good_hosts(self, all_host_stats):
        """Take a dictionary of hosts and corresponding metric data and rank
           hosts via the specified rank method, returning the most suitable."""
        hosts_with_values_to_rank = dict((
            host, self.access_datum(
                metric, self.opt_mapping[self.RANK_METHOD][1])) for
            host, metric in all_host_stats.items())
        # Create list of hosts sorted (ascending order) by value in above dict.
        sort_asc_hosts = [tupl[0] for item, tupl in sorted((item[1], item) for
                          item in hosts_with_values_to_rank.items())]
        if self.RANK_METHOD in ("memory", "disk-space"):
            # Want 'most free' i.e. highest => final host in asc. list.
            return sort_asc_hosts[-1]
        else:  # A load av. is only poss. left; 'random' dealt with earlier.
            return sort_asc_hosts[0]  # Want lowest => first host in asc. list.

    def appoint_host(self, override_stats=False):
        """Appoint the most suitable host to (re-)run a suite on."""

        # Check if immediately 'trivial': no thresholds and zero or one hosts.
        # Must copy self.HOSTS list else it gets shuffled even when unwanted.
        initial_check = self.trivial_choice(
            list(self.HOSTS), ignore_if_thresholds_prov=True)
        if initial_check:
            return initial_check

        good_host_stats = self.remove_bad_hosts(
            self.process_get_host_metric_cmd(), mock_stats=override_stats)

        # Re-check for triviality after bad host removal; otherwise must rank.
        pre_rank_check = self.trivial_choice(good_host_stats.keys())
        if pre_rank_check:
            return pre_rank_check

        return self.rank_good_hosts(good_host_stats)


class TestHostAppointer(unittest.TestCase):
    """Unit tests for the HostAppointer class."""

    def setUp(self):
        """Create variables and templates to use in tests."""
        self.app = HostAppointer()

    def create_custom_metric(self, disk_int, mem_int, load_floats):
        """Non-test method to create dummy metrics for testing. 'disk_int' and
           'mem_int' should be integers and 'load_floats' a list of 3 floats.
           Use 'None' instead to not add associated top-level key to metric."""
        metric = {}
        if disk_int is not None:  # Distinguish None from '0', value to insert.
            metric["disk-space"] = {self.app.use_disk_path: disk_int}
        if mem_int is not None:
            metric["memory"] = mem_int
        if load_floats is not None:
            load_1min, load_5min, load_15min = load_floats
            load_data = {
                "1 min": load_1min,
                "5 min": load_5min,
                "15 min": load_15min
            }
            metric["load"] = load_data
        return json.dumps(metric)

    def create_mock_hosts(self, N_hosts, initial_values, increments, load_var):
        """Non-test method to create a list of tuples of mock hosts, 'N_hosts'
           in number, with their associated metrics. Metric data values are
           incremented across the metrics to create known data variation. The
           list is shuffled to remove ordering by sequence position; name label
           numbers (lower for lower values) indicate the data ordering."""
        mock_host_data = []
        for label in range(1, N_hosts + 1):
            val = []
            # Indices {0,1,2} refer to {disk, memory, load} data respectively.
            for index in range(3):
                val.append(
                    initial_values[index] + (label - 1) * increments[index])
            # Load is special as it needs 3 values and they are floats not ints
            val[2] = (val[2], float(val[2]) + load_var,
                      float(val[2]) + 2 * load_var)
            metric = self.create_custom_metric(val[0], val[1], val[2])
            mock_host_data.append(('HOST_' + str(label), json.loads(metric)))
        shuffle(mock_host_data)
        return mock_host_data

    def mock_global_config(self, set_hosts=None, set_rank_method='random',
                           set_thresholds=None):
        """Non-test method to change the global config read in and processed
           by the test instance of HostAppointer()."""
        if set_hosts is None:
            set_hosts = []
        self.app.HOSTS = set_hosts
        self.app.RANK_METHOD = set_rank_method
        self.app.PARSED_THRESHOLDS = self.app.parse_thresholds(set_thresholds)

    def setup_test_rank_good_hosts(self, num, init, incr, var):
        """Non-test method to setup routine tests for the 'rank_good_hosts'
           method test. Note:
           * Host list input as arg so not reading from 'self.app.HOSTS' =>
             only 'set_rank_method' arg to 'mock_global_config' is relevant.
           * RANK_METHOD 'random' dealt with before this method is called;
             'rank_good_hosts' not written to cater for it, so not tested.
           * Mock set {HOST_X} created so that lower X host has lower data
             values (assuming positive 'incr') so for X = {1, ..., N} HOST_1
             or HOST_N is always 'best', depending on rank method context.
        """
        self.mock_global_config(set_rank_method='memory')
        self.assertEqual(
            self.app.rank_good_hosts(dict(
                self.create_mock_hosts(num, init, incr, var))),
            'HOST_' + str(num)
        )
        self.mock_global_config(set_rank_method='disk-space')
        self.assertEqual(
            self.app.rank_good_hosts(dict(
                self.create_mock_hosts(num, init, incr, var))),
            'HOST_' + str(num)
        )
        # Use 'load:5' as test case of load averages. No need to test all.
        self.mock_global_config(set_rank_method='load:5')
        self.assertEqual(
            self.app.rank_good_hosts(dict(
                self.create_mock_hosts(num, init, incr, var))),
            'HOST_1'
        )

    def test_parse_thresholds(self):
        """Test the 'parse_thresholds' method."""
        self.mock_global_config()
        self.assertEqual(
            self.app.parse_thresholds(None),
            {}
        )
        self.assertEqual(
            self.app.parse_thresholds("load:5 0.5; load:15 1.0; memory" +
                                      " 100000; disk-space 9999999"),
            {
                "load:5": 0.5,
                "load:15": 1.0,
                "memory": 100000,
                "disk-space": 9999999
            }
        )
        self.assertRaises(
            AttributeError,
            self.app.parse_thresholds,
            "memory 300000; gibberish 1.0"
        )
        self.assertRaises(
            ValueError,
            self.app.parse_thresholds,
            "load:5 rogue_string"
        )
        self.assertRaises(
            ValueError,
            self.app.parse_thresholds,
            "disk-space 888 memory 300000"
        )

    def test_access_datum(self):
        """Test the 'access_datum' method. Start with the simplest dictionary
           structure and gradually add complexity with nested levels, testing
           each time the structure is updated."""
        self.mock_global_config()

        # Test plain and nested dicts.
        struct = {}
        # Use single-quoted strings, as this is invalid JSON. Test JSON later.
        self.assertRaises(
            KeyError,
            self.app.access_datum,
            struct, ['KEY_1']
        )
        for label in list(range(1, 6)):
            struct['KEY_' + str(label)] = 'VALUE_' + str(label)
        self.assertEqual(
            self.app.access_datum(struct, ['KEY_3']),
            'VALUE_3'
        )
        root_key = 'KEY_3'  # Choose KEY_3 to create nested dict levels within.
        outer_key = root_key
        struct_level = struct
        for label in list(range(1, 6)):
            inner_key = 'NESTLVL_' + str(label) + '_' + root_key
            struct_level[outer_key] = {inner_key: 'NESTEND_VALUE_3'}
            struct_level = struct_level[outer_key]
            outer_key = inner_key
        self.assertEqual(
            self.app.access_datum(
                struct, ['KEY_3', 'NESTLVL_1_KEY_3', 'NESTLVL_2_KEY_3',
                         'NESTLVL_3_KEY_3', 'NESTLVL_4_KEY_3',
                         'NESTLVL_5_KEY_3']),
            'NESTEND_VALUE_3'
        )
        self.assertRaises(
            KeyError,
            self.app.access_datum,
            struct, ['KEY_3', 'NESTLVL_1_KEY_3', 'NESTLVL_2_KEY_3',
                     'NESTLVL_4_KEY_3', 'NESTLVL_3_KEY_3']
        )
        self.assertRaises(
            ValueError,
            self.app.access_datum,
            struct, ['KEY_3', 'NESTLVL_1_KEY_3', 'NESTLVL_2_KEY_3',
                     'NESTLVL_3_KEY_3']
        )

        # Finally test JSON equivalent.
        json_struct = json.loads(json.dumps(struct))  # Single -> double quotes
        self.assertEqual(
            self.app.access_datum(
                json_struct, ["KEY_3", "NESTLVL_1_KEY_3", "NESTLVL_2_KEY_3",
                              "NESTLVL_3_KEY_3", "NESTLVL_4_KEY_3",
                              "NESTLVL_5_KEY_3"]),
            "NESTEND_VALUE_3"
        )

    def test_trivial_choice(self):
        """Test the 'trivial_choice' (and by extension the
           'selection_complete') method."""
        self.mock_global_config()  # Case with defaults.
        # assertIn not introduced until Python 2.7, so can't use.
        self.assertTrue(
            self.app.trivial_choice(['HOST_1', 'HOST_2', 'HOST_3'],
                                    ignore_if_thresholds_prov=True) in
            ('HOST_1', 'HOST_2', 'HOST_3')
        )

        # Case of defaults except with RANK_METHOD as anything but 'random';
        # really tests 'selection_complete' method (via 'trivial_choice').
        self.mock_global_config(set_rank_method='memory')
        self.assertEqual(
            self.app.trivial_choice(['HOST_1', 'HOST_2', 'HOST_3']),
            False
        )
        self.assertEqual(
            self.app.trivial_choice(['HOST_1']),
            'HOST_1'
        )
        self.assertRaises(
            EmptyHostList,
            self.app.trivial_choice, []
        )

        # Case with (any) valid thresholds and ignore_if_thresholds_prov=True.
        self.mock_global_config(set_thresholds='memory 10000')
        self.assertEqual(
            self.app.trivial_choice(['HOST_1', 'HOST_2', 'HOST_3'],
                                    ignore_if_thresholds_prov=True),
            False
        )

    def test_process_get_host_metric_cmd(self):
        """Test the 'process_get_host_metric_cmd' method."""
        self.mock_global_config()
        self.assertEqual(
            self.app.process_get_host_metric_cmd(),
            'get-host-metric'
        )
        self.mock_global_config(set_thresholds='memory 1000')
        self.assertEqual(
            self.app.process_get_host_metric_cmd(),
            'get-host-metric --memory'
        )
        self.mock_global_config(set_rank_method='memory')
        self.assertEqual(
            self.app.process_get_host_metric_cmd(),
            'get-host-metric --memory'
        )
        self.mock_global_config(set_rank_method='disk-space',
                                set_thresholds='load:1 1000')
        self.assertEqual(
            self.app.process_get_host_metric_cmd(),
            'get-host-metric --disk-space=' + self.app.use_disk_path +
            ' --load'
        )
        self.mock_global_config(
            set_rank_method='memory',
            set_thresholds='disk-space 1000; memory 1000; load:15 1.0')
        # self.PARSED_THRESHOLDS a dict => unordered keys: opts order may vary.
        self.assertTrue(
            self.app.process_get_host_metric_cmd() in
            ('get-host-metric --memory --disk-space=/ --load',
             'get-host-metric --memory --load --disk-space=/')
        )

    def test_remove_bad_hosts(self):
        """Test the 'remove_bad_hosts' method. Test using 'localhost' only
           since remote host functionality is contained only inside
           remote_cylc_cmd() so is outside of the scope of HostAppointer."""
        self.mock_global_config(set_hosts=['localhost'])
        self.failUnless(
            self.app.remove_bad_hosts(
                self.app.CMD_BASE).get('localhost', False)
        )
        self.mock_global_config(set_hosts=['localhost', 'FAKE_HOST'])
        self.assertRaises(
            CalledProcessError,
            self.app.remove_bad_hosts,
            self.app.CMD_BASE
        )
        self.mock_global_config(set_hosts=['localhost'])
        self.assertRaises(
            CalledProcessError,
            self.app.remove_bad_hosts,
            self.app.CMD_BASE + ' --nonsense'
        )

        # Apply thresholds impossible to pass; check results in host removal.
        self.mock_global_config(
            set_hosts=['localhost'], set_thresholds='load:15 0.0')
        self.assertEqual(
            self.app.remove_bad_hosts(self.app.CMD_BASE + " --load"),
            {}
        )
        self.mock_global_config(
            set_hosts=['localhost'], set_thresholds='memory 1000000000')
        self.assertEqual(
            self.app.remove_bad_hosts(self.app.CMD_BASE + " --memory"),
            {}
        )

    def test_rank_good_hosts(self):
        """Test the 'rank_good_hosts' method."""

        # Considering special cases:
        # Case with 0 or 1 hosts filtered out before method called, so ignore.
        # Variation in load averages is irrelevant; no need to test lack of.

        # Case with no increments => same stats for all hosts. Random result.
        self.mock_global_config(set_rank_method='memory')  # Any except random.
        self.assertTrue(
            self.app.rank_good_hosts(dict(
                self.create_mock_hosts(
                    5, [100, 100, 1.0], [0, 0, 0.0], 0.1))) in
            ('HOST_1', 'HOST_2', 'HOST_3', 'HOST_4', 'HOST_5')
        )

        # Test a selection of routine cases; only requirements are for types:
        # init and incr in form [int, int, float] and int var, and for size:
        # num > 1, all elements of init > 0(.0) and incr >= 0(.0), var >= 0.0.
        self.setup_test_rank_good_hosts(
            2, [100, 100, 1.0], [100, 100, 1.0], 0.2)
        self.setup_test_rank_good_hosts(
            10, [500, 200, 0.1], [100, 10, 10.0], 0.0)
        self.setup_test_rank_good_hosts(
            10, [103870, 52139, 3.19892], [5348, 45, 5.2321], 0.52323)
        self.setup_test_rank_good_hosts(
            50, [10000, 20000, 0.00000001], [400, 1000000, 1.1232982], 0.11)

    def test_appoint_host(self):
        """Test the 'appoint_host' method. This method calls all other methods
           in the class directly or indirectly, hence this is essentially
           a full-class test. The following phase space is covered:

               1. Number of hosts: none, one or multiple.
               2. Rank method: random, load (use just 5 min average case),
                               memory or disk space.
               3. Thresholds: without or with, including all measures.
        """

        # Define phase space.
        hosts_space = ([], ['HOST_1'],
                       ['HOST_1', 'HOST_2', 'HOST_3', 'HOST_4', 'HOST_5'])
        rank_method_space = ('random', 'load:5', 'memory', 'disk-space')
        thresholds_space = (None, 'load:1 2.0; load:5 1.10; load:15' +
                            ' 1.31; memory 31000; disk-space 1000')

        # Enumerate all (24) correct results required to test equality with.
        # Correct results deduced individually based on mock host set. Note
        # only HOST_2 and HOST_3 pass all thresholds for thresholds_space[1].
        correct_results = (8 * [EmptyHostList] +
                           4 * ['HOST_1', EmptyHostList] +
                           ['HOST_X', 'HOST_Y', 'HOST_1', 'HOST_2', 'HOST_5',
                            'HOST_3', 'HOST_5', 'HOST_3'])

        for index, (host_list, method, thresholds) in enumerate(
                [(hosts, meth, thr) for hosts in hosts_space for meth in
                 rank_method_space for thr in thresholds_space]):

            # Use same group of mock hosts each time, but ensure compatible
            # number (at host_list changeover only; avoid re-creating same).
            if index in (0, 8, 16):
                mock_hosts = dict(self.create_mock_hosts(
                    len(host_list), [400000, 30000, 0.05], [50000, 1000, 0.2],
                    0.4))

            self.mock_global_config(
                set_hosts=host_list, set_rank_method=method,
                set_thresholds=thresholds)

            if correct_results[index] == 'HOST_X':  # random, any X={1..5} fine
                self.assertTrue(
                    self.app.appoint_host(override_stats=mock_hosts) in
                    host_list
                )
            elif correct_results[index] == 'HOST_Y':  # random + thr, X={2,3}
                self.assertTrue(
                    self.app.appoint_host(override_stats=mock_hosts) in
                    host_list[1:3]
                )
            elif isinstance(correct_results[index], str):
                self.assertEqual(
                    self.app.appoint_host(override_stats=mock_hosts),
                    correct_results[index]
                )
            else:
                self.assertRaises(
                    correct_results[index],
                    self.app.appoint_host,
                    override_stats=mock_hosts
                )


if __name__ == "__main__":
    unittest.main()
