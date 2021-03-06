#!/usr/bin/env python3
# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2019 NIWA & British Crown (Met Office) & Contributors.
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

"""cylc [control] trigger [OPTIONS] ARGS

Manually trigger tasks.
  cylc trigger REG - trigger all tasks in a running workflow
  cylc trigger REG TASK_GLOB ... - trigger some tasks in a running workflow

NOTE waiting tasks that are queue-limited will be queued if triggered, to
submit as normal when released by the queue; queued tasks will submit
immediately if triggered, even if that violates the queue limit (so you may
need to trigger a queue-limited task twice to get it to submit immediately).

For single tasks you can use "--edit" to edit the generated job script before
it submits, to apply one-off changes. A diff between the original and edited
job script will be saved to the task job log directory.
"""

import sys

if '--host' in sys.argv[1:] and '--edit' in sys.argv[1:]:
    # Edit runs must always be re-invoked on the suite host.
    if '--use-ssh' not in sys.argv[1:]:
        sys.argv[1:].append('--use-ssh')

if '--use-ssh' in sys.argv[1:]:
    sys.argv.remove('--use-ssh')
    from cylc.flow.remote import remrun
    if remrun(forward_x11=True):
        sys.exit(0)

import re
import os
import time
import shutil
import difflib
from subprocess import call

from cylc.flow.exceptions import CylcError, UserInputError
from cylc.flow.option_parsers import CylcOptionParser as COP
from cylc.flow.network.client import SuiteRuntimeClient
from cylc.flow.cfgspec.glbl_cfg import glbl_cfg
from cylc.flow.task_job_logs import JOB_LOG_DIFF
from cylc.flow.terminal import prompt, cli_function


def get_option_parser():
    parser = COP(
        __doc__, comms=True, multitask=True,
        argdoc=[
            ('REG', 'Suite name'),
            ('[TASK_GLOB ...]', 'Task matching patterns')])

    parser.add_option(
        "-e", "--edit",
        help="Manually edit the job script before running it.",
        action="store_true", default=False, dest="edit_run")

    parser.add_option(
        "-g", "--geditor",
        help="(with --edit) force use of the configured GUI editor.",
        action="store_true", default=False, dest="geditor")

    return parser


@cli_function(get_option_parser)
def main(parser, options, suite, *task_globs):
    """CLI for "cylc trigger"."""
    msg = 'Trigger task(s) %s in %s' % (task_globs, suite)
    prompt(msg, options.force)

    pclient = SuiteRuntimeClient(
        suite, options.owner, options.host, options.port,
        options.comms_timeout)

    aborted = False
    if options.edit_run:
        task_id = task_globs[0]
        # Check that TASK is a unique task.
        success, msg = pclient(
            'ping_task',
            {'task_id': task_id, 'exists_only': True}
        )

        # Get the job filename from the suite server program - the task cycle
        # point may need standardising to the suite cycle point format.
        jobfile_path = pclient(
            'get_task_jobfile_path', {'task_id': task_id})
        if not jobfile_path:
            raise UserInputError('task not found')

        # Note: localhost time and file system time may be out of sync,
        #       so the safe way to detect whether a new file is modified
        #       or is to detect whether time stamp has changed or not.
        #       Comparing the localhost time with the file timestamp is unsafe
        #       and may cause the "while True" loop that follows to sys.exit
        #       with an error message after MAX_TRIES.
        try:
            old_mtime = os.stat(jobfile_path).st_mtime
        except OSError:
            old_mtime = None

        # Tell the suite server program to generate the job file.
        pclient(
            'dry_run_tasks',
            {'task_globs': [task_id], 'check_syntax': False}
        )

        # Wait for the new job file to be written. Use mtime because the same
        # file could potentially exist already, left from a previous run.
        count = 0
        MAX_TRIES = 10
        while True:
            count += 1
            try:
                mtime = os.stat(jobfile_path).st_mtime
            except OSError:
                pass
            else:
                if old_mtime is None or mtime > old_mtime:
                    break
            if count > MAX_TRIES:
                raise CylcError(
                    'no job file after %s seconds' % MAX_TRIES)
            time.sleep(1)

        # Make a pre-edit copy to allow a post-edit diff.
        jobfile_copy_path = "%s.ORIG" % jobfile_path
        shutil.copy(jobfile_path, jobfile_copy_path)

        # Edit the new job file.
        if options.geditor:
            editor = glbl_cfg().get(['editors', 'gui'])
        else:
            editor = glbl_cfg().get(['editors', 'terminal'])
        # The editor command may have options, e.g. 'emacs -nw'.
        command_list = re.split(' ', editor)
        command_list.append(jobfile_path)
        command = ' '.join(command_list)
        try:
            # Block until the editor exits.
            retcode = call(command_list)
            if retcode != 0:
                raise CylcError(
                    'command failed with %d:\n %s' % (retcode, command))
        except OSError:
            raise CylcError('unable to execute:\n %s' % command)

        # Get confirmation after editing is done.
        # Don't allow force-no-prompt in this case.
        if options.geditor:
            # Alert stdout of the dialog window, in case it's missed.
            print("Editing done. I'm popping up a confirmation dialog now.")

        # Save a diff to record the changes made.
        difflog = os.path.join(os.path.dirname(jobfile_path), JOB_LOG_DIFF)
        with open(difflog, 'wb') as diff_file:
            for line in difflib.unified_diff(
                    open(jobfile_copy_path).readlines(),
                    open(jobfile_path).readlines(),
                    fromfile="original",
                    tofile="edited"):
                diff_file.write(line.encode())
        os.unlink(jobfile_copy_path)

        msg = "Trigger edited task %s?" % task_id
        if not prompt(msg, gui=options.geditor, no_force=True, no_abort=True):
            log_dir_symlink = os.path.dirname(jobfile_path)
            real_log_dir = os.path.realpath(log_dir_symlink)
            prev_nn = "%02d" % (int(os.path.basename(real_log_dir)) - 1)
            os.unlink(log_dir_symlink)
            if int(prev_nn) == 0:
                # No previous submit: delete the whole parent directory.
                shutil.rmtree(os.path.dirname(real_log_dir))
            else:
                # Reset to previous NN symlink and delete the log directory.
                dirname = os.path.dirname(real_log_dir)
                os.symlink(prev_nn, os.path.join(dirname, "NN"))
                shutil.rmtree(real_log_dir)
            aborted = True

    # Trigger the task proxy(s).
    pclient(
        'trigger_tasks',
        {'task_globs': task_globs, 'back_out': aborted}
    )


if __name__ == "__main__":
    main()
