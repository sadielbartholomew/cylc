CUG tutorial
============

\section{Tutorial}
\label{Tutorial}

This section provides a hands-on tutorial introduction to basic cylc
functionality.

\subsection{User Config File}

Some settings affecting cylc's behaviour can be defined in site and user
{\em global config files}. For example, to choose the text editor invoked by
cylc on suite configurations:

\lstset{language=suiterc}
\begin{lstlisting}
# $HOME/.cylc/$(cylc --version)/global.rc
[editors]
    terminal = vim
    gui = gvim -f
\end{lstlisting}

\begin{myitemize}
\item For more on site and user global config files
  see~\ref{SiteAndUserConfiguration} and~\ref{SiteRCReference}.
\end{myitemize}

\subsubsection{Configure Environment on Job Hosts}
\label{Configure Environment on Job Hosts}

See~\ref{Configure Site Environment on Job Hosts} for information.

\subsection{User Interfaces}
\label{CUI}

You should have access to the cylc command line (CLI) and graphical (GUI) user
interfaces once cylc has been installed as described in
Section~\ref{InstallCylc}.

\subsubsection{Command Line Interface (CLI)}

The command line interface is unified under a single top level
\lstinline=cylc= command that provides access to many sub-commands
and their help documentation.

\lstset{language=transcript}
\begin{lstlisting}
$ cylc help       # Top level command help.
$ cylc run --help # Example command-specific help.
\end{lstlisting}

Command help transcripts are printed in~\ref{CommandReference} and are
available from the GUI Help menu.

Cylc is {\em scriptable} - the error status returned by commands can be
relied on.

\subsubsection{Graphical User Interface (GUI)}

The cylc GUI covers the same functionality as the CLI, but it has more
sophisticated suite monitoring capability. It can start and stop suites, or
connect to suites that are already running; in either case, shutting down the
GUI does not affect the suite itself.

\lstset{language=transcript}
\begin{lstlisting}
$ gcylc & # or:
$ cylc gui & # Single suite control GUI.
$ cylc gscan & # Multi-suite monitor GUI.
\end{lstlisting}

Clicking on a suite in gscan, shown in Figure~\ref{fig-gscan}, opens a gcylc
instance for it.

\subsection{Suite Configuration}

Cylc suites are defined by extended-INI format \lstinline=suite.rc=
files (the main file format extension is section nesting). These reside
in {\em suite configuration directories} that may also contain a
\lstinline=bin= directory and any other suite-related files.

\begin{myitemize}
\item For more on the suite configuration file format, see~\ref{SuiteDefinition}
    and~\ref{SuiteRCReference}.
\end{myitemize}

\subsection{Suite Registration}

Suite registration creates a run directory (under \lstinline=~/cylc-run/= by
default) and populates it with authentication files and a symbolic link to a
suite configuration directory. Cylc commands that parse suites can take
the file path or the suite name as input. Commands that interact with running
suites have to target the suite by name.

\lstset{language=transcript}
\begin{lstlisting}
# Target a suite by file path:
$ cylc validate /path/to/my/suite/suite.rc
$ cylc graph /path/to/my/suite/suite.rc

# Register a suite:
$ cylc register my.suite /path/to/my/suite/

# Target a suite by name:
$ cylc graph my.suite
$ cylc validate my.suite
$ cylc run my.suite
$ cylc stop my.suite
# etc.
\end{lstlisting}

\subsection{Suite Passphrases}
\label{tutPassphrases}

Registration (above) also generates a suite-specific passphrase file under
\lstinline=.service/= in the suite run directory. It is loaded by the suite
server program at start-up and used to authenticate connections from client
programs.

Possession of a suite's passphrase file gives full control over it.
Without it, the information available to a client is determined by the suite's
public access privilege level.

For more on connection authentication, suite passphrases, and public access,
see~\ref{ConnectionAuthentication}.


\subsection{Import The Example Suites}
\label{ImportTheExampleSuites}

Run the following command to copy cylc's example suites and register them for
your own use:

\lstset{language=transcript}
\begin{lstlisting}
$ cylc import-examples /tmp
\end{lstlisting}

\subsection{Rename The Imported Tutorial Suites}

Suites can be renamed by simply renaming (i.e.\ moving) their run directories.
Make the tutorial suite names shorter, and print their locations with
\lstinline=cylc print=:

\begin{lstlisting}
$ mv ~/cylc-run/examples/$(cylc --version)/tutorial ~/cylc-run/tut
$ cylc print -ya tut
tut/oneoff/jinja2  | /tmp/cylc-examples/7.0.0/tutorial/oneoff/jinja2
tut/cycling/two    | /tmp/cylc-examples/7.0.0/tutorial/cycling/two
tut/cycling/three  | /tmp/cylc-examples/7.0.0/tutorial/cycling/three
# ...
\end{lstlisting}

See \lstinline=cylc print --help= for other display options.

\subsection{Suite Validation}

Suite configurations can be validated to detect syntax (and other) errors:

\lstset{language=transcript}
\begin{lstlisting}
# pass:
$ cylc validate tut/oneoff/basic
Valid for cylc-6.0.0
$ echo $?
0
# fail:
$ cylc validate my/bad/suite
Illegal item: [scheduling]special tusks
$ echo $?
1
\end{lstlisting}

\subsection{Hello World in Cylc}

\hilight{ suite: \lstinline=tut/oneoff/basic= }
\vspace{3mm}

Here's the traditional {\em Hello World} program rendered as a cylc
suite:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/basic/suite.rc}
\lstset{language=transcript}

Cylc suites feature a clean separation of scheduling configuration,
which determines {\em when} tasks are ready to run; and runtime
configuration, which determines {\em what} to run (and {\em where} and
{\em how} to run it) when a task is ready. In this example the
\lstinline=[scheduling]= section defines a single task called
\lstinline=hello= that triggers immediately when the suite starts
up. When the task finishes the suite shuts down. That this is a
{\em dependency graph} will be more obvious when more tasks are added.
Under the \lstinline=[runtime]= section the
\lstinline=script= item defines a simple inlined
implementation for \lstinline=hello=: it sleeps for ten seconds,
then prints \lstinline=Hello World!=, and exits. This ends up in a {\em
job script} generated by cylc to encapsulate the task (below) and,
thanks to some defaults designed to allow quick
prototyping of new suites, it is submitted to run as a background job on
the suite host. In fact cylc even provides a default task implementation
that makes the entire \lstinline=[runtime]= section technically optional:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/minimal/suite.rc}
\lstset{language=transcript}
(the resulting {\em dummy task} just prints out some identifying
information and exits).

\subsection{Editing Suites}

The text editor invoked by Cylc on suite configurations is determined
by cylc site and user global config files, as shown above in~\ref{CUI}.
Check that you have renamed the tutorial examples suites as described
just above and open the {\em Hello World} suite in your text editor:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc edit tut/oneoff/basic # in-terminal
$ cylc edit -g tut/oneoff/basic & # or GUI
\end{lstlisting}
Alternatively, start gcylc on the suite:
\lstset{language=transcript}
\begin{lstlisting}
$ gcylc tut/oneoff/basic &
\end{lstlisting}
and choose {\em Suite } \textrightarrow {\em Edit} from the menu.

The editor will be invoked from within the suite configuration directory for easy
access to other suite files (in this case there are none). There are syntax
highlighting control files for several text editors under
\lstinline=<cylc-dir>/etc/syntax/=; see in-file comments for installation
instructions.

\subsection{Running Suites}
\label{RunningSuitesCLI}

\subsubsection{CLI}
Run \lstinline=tut/oneoff/basic= using the \lstinline=cylc run= command.
As a suite runs detailed timestamped information is written to a {\em suite
log} and progress can be followed with cylc's suite monitoring tools (below).
By default a suite server program daemonizes after printing a short message so
that you can exit the terminal or even log out without killing the suite:

\lstset{language=transcript}
\begin{lstlisting}
$ cylc run tut/oneoff/basic
            ._.
            | |                 The Cylc Suite Engine [7.0.0]
._____._. ._| |_____.           Copyright (C) 2008-2018 NIWA & British Crown (Met Office) & Contributors.
| .___| | | | | .___|  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
| !___| !_! | | !___.  This program comes with ABSOLUTELY NO WARRANTY;
!_____!___. |_!_____!  see `cylc warranty`.  It is free software, you
      .___! |           are welcome to redistribute it under certain
      !_____!                conditions; see `cylc conditions`.

*** listening on https://nwp-1:43027/ ***

To view suite server program contact information:
 $ cylc get-suite-contact tut/oneoff/basic

Other ways to see if the suite is still running:
 $ cylc scan -n '\btut/oneoff/basic\b' nwp-1
 $ cylc ping -v --host=nwp-1 tut/oneoff/basic
 $ ps h -opid,args 123456  # on nwp-1

\end{lstlisting}

If you're quick enough (this example only takes 10-15 seconds to run) the
\lstinline=cylc scan= command will detect the running suite:
\begin{lstlisting}
$ cylc scan
tut/oneoff/basic oliverh@nwp-1:43027
\end{lstlisting}

Note you can use the \lstinline=--no-detach= and \lstinline=--debug= options
to \lstinline=cylc-run= to prevent the suite from daemonizing (i.e.\ to make
it stay attached to your terminal until it exits).

When a task is ready cylc generates a {\em job script} to run it, by
default as a background jobs on the suite host.  The job process ID is
captured, and job output is directed to log files in standard
locations under the suite run directory.

Log file locations relative to the suite run directory look like
\lstinline=job/1/hello/01/= where the first digit is the {\em cycle point} of
the task \lstinline=hello= (for non-cycling tasks this is just `1'); and the
final \lstinline=01= is the {\em submit number} (so that job logs do not get
overwritten if a job is resubmitted for any reason).

The suite shuts down automatically once all tasks have succeeded.

\subsubsection{GUI}

The cylc GUI can start and stop suites, or (re)connect to suites that
are already running:
\begin{lstlisting}
$ cylc gui tut/oneoff/basic &
\end{lstlisting}
Use the tool bar {\em Play} button, or the {\em Control}
\textrightarrow {\em Run} menu item, to run the suite again.
You may want to alter the suite configuration slightly to make the task
take longer to run. Try right-clicking on the \lstinline=hello= task
to view its output logs. The relative merits of the three {\em suite
views} - dot, text, and graph - will be more apparent later when we
have more tasks. Closing the GUI does not affect the suite itself.

\subsection{Remote Suites}
\label{RemoteSuites}

Suites can run on {\em localhost} or on a {\em remote} host.

To start up a suite on a given host, specify it explicitly via the
\lstinline@--host=@ option to a \lstinline=run= or \lstinline=restart=
command.

Otherwise, Cylc selects the best host to start up on from allowed
\lstinline=run hosts= as specified in the global config under
\lstinline=[suite servers]=, which defaults to localhost. Should there be
more than one allowed host set, the {\em most suitable} is determined
according to the settings specified under \lstinline=[[run host select]]=,
namely exclusion of hosts not meeting suitability {\em thresholds}, if
provided, then ranking according to the given {\em rank} method.

\subsection{Discovering Running Suites}

Suites that are currently running can be detected with command line or
GUI tools:
\begin{lstlisting}
# list currently running suites and their port numbers:
$ cylc scan
tut/oneoff/basic oliverh@nwp-1:43001

# GUI summary view of running suites:
$ cylc gscan &
\end{lstlisting}

The scan GUI is shown in Figure~\ref{fig-gscan}; clicking on a suite in it
opens gcylc.

\subsection{Task Identifiers}

At run time, task instances are identified by {\em name}, which is
determined entirely by the suite configuration, and a {\em cycle point} which is
usually a date-time or an integer:
\lstset{language=transcript}
\begin{lstlisting}
foo.20100808T00Z   # a task with a date-time cycle point
bar.1              # a task with an integer cycle point (could be non-cycling)
\end{lstlisting}
Non-cycling tasks usually just have the cycle point \lstinline=1=, but this
still has to be used to target the task instance with cylc commands.

\subsection{Job Submission: How Tasks Are Executed}

\hilight{ suite: \lstinline=tut/oneoff/jobsub= }
\vspace{3mm}

Task {\em job scripts} are generated by cylc to wrap the task implementation
specified in the suite configuration (environment, script, etc.) in
error trapping code, messaging calls to report task progress back to the suite
server program, and so forth. Job scripts are written to the {\em suite job log
directory} where they can be viewed alongside the job output logs. They
can be accessed at run time by right-clicking on the task in the cylc GUI, or
printed to the terminal:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc cat-log tut/oneoff/basic hello.1
\end{lstlisting}
This command can also print the suite log (and stdout and stderr for suites
in daemon mode) and task stdout and stderr logs (see
\lstinline=cylc cat-log --help=).
A new job script can also be generated on the fly for inspection:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc jobscript tut/oneoff/basic hello.1
\end{lstlisting}

Take a look at the job script generated for \lstinline=hello.1= during
the suite run above. The custom scripting should be clearly visible
toward the bottom of the file.

The \lstinline=hello= task in the first tutorial suite defaults to
running as a background job on the suite host. To submit it to the Unix
\lstinline=at= scheduler instead, configure its job submission settings
as in \lstinline=tut/oneoff/jobsub=:

\lstset{language=suiterc}
\begin{lstlisting}
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
        [[[job]]]
            batch system = at
\end{lstlisting}

Run the suite again after checking that \lstinline=atd= is running on your
system.

Cylc supports a number of different batch systems. Tasks
submitted to external batch queuing systems like \lstinline=at=,
\lstinline=PBS=, \lstinline=SLURM=, \lstinline=Moab=, or
\lstinline=LoadLeveler=, are displayed as {\em submitted} in the cylc GUI until
they start executing.

\begin{myitemize}
\item For more on task job scripts, see~\ref{JobScripts}.
\item For more on batch systems, see~\ref{AvailableMethods}.
\end{myitemize}

\subsection{Locating Suite And Task Output}

If the \lstinline=--no-detach= option is not used, suite stdout and
stderr will be directed to the suite run directory along with the
time-stamped suite log file, and task job scripts and job logs
(task stdout and stderr). The default suite run directory location is
\lstinline=$HOME/cylc-run=:

\lstset{language=transcript}
\begin{lstlisting}
$ tree $HOME/cylc-run/tut/oneoff/basic/
|-- .service              # location of run time service files
|    |-- contact          # detail on how to contact the running suite
|    |-- db               # private suite run database
|    |-- passphrase       # passphrase for client authentication
|    |-- source           # symbolic link to source directory
|    |-- ssl.cert         # SSL certificate for the suite server
|    `-- ssl.pem          # SSL private key
|-- cylc-suite.db         # back compat symlink to public suite run database
|-- share                 # suite share directory (not used in this example)
|-- work                  # task work space (sub-dirs are deleted if not used)
|    `-- 1                   # task cycle point directory (or 1)
|        `-- hello              # task work directory (deleted if not used)
|-- log                   # suite log directory
|   |-- db                   # public suite run database
|   |-- job                  # task job log directory
|   |   `-- 1                   # task cycle point directory (or 1)
|   |       `-- hello              # task name
|   |           |-- 01                # task submission number
|   |           |   |-- job              # task job script
|   |           |   `-- job-activity.log # task job activity log
|   |           |   |-- job.err          # task stderr log
|   |           |   |-- job.out          # task stdout log
|   |           |   `-- job.status       # task status file
|   |           `-- NN -> 01          # symlink to latest submission number
|   `-- suite                # suite server log directory
|       |-- err                 # suite server stderr log (daemon mode only)
|       |-- out                 # suite server stdout log (daemon mode only)
|       `-- log                 # suite server event log (timestamped info)
\end{lstlisting}
The suite run database files, suite environment file,
and task status files are used internally by cylc. Tasks execute in
private \lstinline=work/= directories that are deleted automatically
if empty when the task finishes. The suite
\lstinline=share/= directory is made available to all tasks (by
\lstinline=$CYLC_SUITE_SHARE_DIR=) as a common share space. The task submission
number increments from 1 if a task retries; this is used as a sub-directory of
the log tree to avoid overwriting log files from earlier job submissions.

The top level run directory location can be changed in site and user
config files if necessary, and the suite share and work locations can be
configured separately because of the potentially larger disk space
requirement.

Task job logs can be viewed by right-clicking on tasks in the gcylc
GUI (so long as the task proxy is live in the suite), manually
accessed from the log directory (of course), or printed to the terminal
with the \lstinline=cylc cat-log= command:
\lstset{language=transcript}
\begin{lstlisting}
# suite logs:
$ cylc cat-log    tut/oneoff/basic           # suite event log
$ cylc cat-log -o tut/oneoff/basic           # suite stdout log
$ cylc cat-log -e tut/oneoff/basic           # suite stderr log
# task logs:
$ cylc cat-log    tut/oneoff/basic hello.1   # task job script
$ cylc cat-log -o tut/oneoff/basic hello.1   # task stdout log
$ cylc cat-log -e tut/oneoff/basic hello.1   # task stderr log
\end{lstlisting}
\begin{myitemize}
    \item For a web-based interface to suite and task logs (and much more),
        see {\em Rose} in~\ref{SuiteStorageEtc}.
    \item For more on environment variables supplied to tasks,
    such as \lstinline=$CYLC_SUITE_SHARE_DIR=, see~\ref{TaskExecutionEnvironment}.
\end{myitemize}

\subsection{Viewing Suite Logs via Web Browser: Cylc Review}

Cylc provides a utility for viewing the status and logs of suites called
Cylc Review. It displays suite information in web pages, as shown in
Figure~\ref{fig-review-screenshot}.

\begin{figure}
    \begin{center}
        \includegraphics[width=0.5\textwidth]{graphics/png/orig/cylc-review-screenshot.png}
    \end{center}
    \caption{Screenshot of a Cylc Review web page}
\label{fig-review-screenshot}
\end{figure}

If a Cylc Review server is provided at your site, you can open the Cylc
Review page for a suite by running the \lstinline=cylc review= command.
See~\ref{HostsforCylcReview} for requirements and~\ref{ConfiguringCylcReview}
for configuration steps for setting up a host to run the service at your site.

Otherwise an ad-hoc web server can be set up using the
\lstinline=cylc review start= command argument.

\subsubsection{Hosts For Running Cylc Review}
\label{HostsforCylcReview}

Connectivity requirements:

\begin{myitemize}

\item Must be able to access the home directories of users' Cylc run
directories.

\end {myitemize}

\subsubsection{Configuring Cylc Review}
\label{ConfiguringCylcReview}

Cylc Review can provide an intranet web service at your site for users to
view their suite logs using a web browser. Depending on settings at your
site, you may or may not be able to set up this service
(see~\ref{HostsforCylcReview}).

You can start an ad-hoc Cylc Review web server by running:

\hilight{\lstinline=setsid /path/to/../cylc review start 0</dev/null 1>/dev/null 2>\&1 \&=}

You will find the access and error logs under \lstinline=~/.cylc/cylc-review*=.

Alternatively you can run the Cylc Review web service under Apache
\lstinline=mod_wsgi=. To do this you will need to set up an Apache module
configuration file (typically in
\lstinline=/etc/httpd/conf.d/rose-wsgi.conf=) containing the following (with
the paths set appropriately):

\lstset{language=bash}
\begin{lstlisting}
WSGIPythonPath /path/to/rose/lib/python
WSGIScriptAlias /cylc-review /path/to/lib/cylc/review.py
\end{lstlisting}

Use the Apache log at e.g. \lstinline=/var/log/httpd/= to debug problems.

\subsection{Remote Tasks}
\label{RemoteTasks}

\hilight{ suite: \lstinline=tut/oneoff/remote= }
\vspace{3mm}

The \lstinline=hello= task in the first two tutorial suites defaults to
running on the suite host~\ref{RemoteSuites}. To make it run on a different host instead
change its runtime configuration as in \lstinline=tut/oneoff/remote=:
\lstset{language=suiterc}
\begin{lstlisting}
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
        [[[remote]]]
            host = server1.niwa.co.nz
\end{lstlisting}

In general, a {\em task remote} is a user account, other than the account
running the suite server program, where a task job is submitted to run. It can
be on the same machine running the suite or on another machine.

A task remote account must satisfy several requirements:
\begin{myitemize}

\item Non-interactive ssh must be enabled from the account running the suite
server program to the account for submitting (and managing) the remote task job.

\item Network settings must allow communication {\em back} from the remote task
job to the suite, either by network ports or ssh, unless the last-resort one
way {\em task polling} communication method is used.

\item Cylc must be installed and runnable on the task remote account. Other
software dependencies like graphviz are not required there.

\item Any files needed by a remote task must be installed on the task
host. In this example there is nothing to install because the
implementation of \lstinline=hello= is inlined in the suite configuration
and thus ends up entirely contained within the task job script.

\end{myitemize}

If your username is different on the task host, you can add a \lstinline=User=
setting for the relevant host in your \lstinline=~/.ssh/config=.
If you are unable to do so, the \lstinline=[[[remote]]]= section also supports an
\lstinline@owner=username@ item.

If you configure a task account according to the requirements cylc will invoke
itself on the remote account (with a login shell by default) to create log
directories, transfer any essential service files, send the task job script
over, and submit it to run there by the configured batch system.

Remote task job logs are saved to the suite run directory on the task remote,
not on the account running the suite. They can be retrieved by right-clicking
on the task in the GUI, or to have cylc pull them back to the suite account
automatically do this:

\lstset{language=suiterc}
\begin{lstlisting}
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
        [[[remote]]]
            host = server1.niwa.co.nz
            retrieve job logs = True
\end{lstlisting}

This suite will attempt to \lstinline=rsync= job logs from the remote
host each time a task job completes.

Some batch systems have considerable delays between the time when the job
completes and when it writes the job logs in its normal location. If this is
the case, you can configure an initial delay and retry delays for job log
retrieval by setting some delays. E.g.:

\lstset{language=suiterc}
\begin{lstlisting}
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
        [[[remote]]]
            host = server1.niwa.co.nz
            retrieve job logs = True
            # Retry after 10 seconds, 1 minute and 3 minutes
            retrieve job logs retry delays = PT10S, PT1M, PT3M
\end{lstlisting}

Finally, if the disk space of the suite host is limited, you may want to set
\lstinline@[[[remote]]]retrieve job logs max size=SIZE@. The value of SIZE can
be anything that is accepted by the \lstinline@--max-size=SIZE@ option of the
\lstinline=rsync= command. E.g.:

\lstset{language=suiterc}
\begin{lstlisting}
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
        [[[remote]]]
            host = server1.niwa.co.nz
            retrieve job logs = True
            # Don't get anything bigger than 10MB
            retrieve job logs max size = 10M
\end{lstlisting}

It is worth noting that cylc uses the existence of a job's \lstinline=job.out=
or \lstinline=job.err= in the local file system to indicate a successful job
log retrieval. If \lstinline=retrieve job logs max size=SIZE= is set and both
\lstinline=job.out= and \lstinline=job.err= are bigger than \lstinline=SIZE=
then cylc will consider the retrieval as failed. If retry delays are specified,
this will trigger some useless (but harmless) retries. If this occurs
regularly, you should try the following:

\begin{myitemize}
\item Reduce the verbosity of STDOUT or STDERR from the task.
\item Redirect the verbosity from STDOUT or STDERR to an alternate log file.
\item Adjust the size limit with tolerance to the expected size of STDOUT or STDERR.
\end{myitemize}

\begin{myitemize}
\item For more on remote tasks see~\ref{RunningTasksOnARemoteHost}

\item For more on task communications, see~\ref{TaskComms}.

\item For more on suite passphrases and authentication,
    see~\ref{tutPassphrases} and~\ref{ConnectionAuthentication}.
\end{myitemize}


\subsection{Task Triggering}

\hilight{ suite: \lstinline=tut/oneoff/goodbye= }
\vspace{3mm}

To make a second task called \lstinline=goodbye= trigger after
\lstinline=hello= finishes successfully, return to the original
example, \lstinline=tut/oneoff/basic=, and change the suite graph
as in \lstinline=tut/oneoff/goodbye=:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = "hello => goodbye"
\end{lstlisting}
or to trigger it at the same time as \lstinline=hello=,
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = "hello & goodbye"
\end{lstlisting}
and configure the new task's behaviour under \lstinline=[runtime]=:
\lstset{language=suiterc}
\begin{lstlisting}
[runtime]
    [[goodbye]]
        script = "sleep 10; echo Goodbye World!"
\end{lstlisting}

Run \lstinline=tut/oneoff/goodbye= and check the output from the new
task:
\lstset{language=transcript}
\begin{lstlisting}
$ cat ~/cylc-run/tut/oneoff/goodbye/log/job/1/goodbye/01/job.out
  # or
$ cylc cat-log -o tut/oneoff/goodbye goodbye.1
JOB SCRIPT STARTING
cylc (scheduler - 2014-08-14T15:09:30+12): goodbye.1 started at 2014-08-14T15:09:30+12
cylc Suite and Task Identity:
  Suite Name  : tut/oneoff/goodbye
  Suite Host  : oliverh-34403dl.niwa.local
  Suite Port  : 43001
  Suite Owner : oliverh
  Task ID     : goodbye.1
  Task Host   : nwp-1
  Task Owner  : oliverh
  Task Try No.: 1

Goodbye World!
cylc (scheduler - 2014-08-14T15:09:40+12): goodbye.1 succeeded at 2014-08-14T15:09:40+12
JOB SCRIPT EXITING (TASK SUCCEEDED)
\end{lstlisting}

\subsubsection{Task Failure And Suicide Triggering}

\hilight{ suite: \lstinline=tut/oneoff/suicide= }
\vspace{3mm}

Task names in the graph string can be qualified with a state indicator
to trigger off task states other than success:
\lstset{language=suiterc}
\lstset{language=suiterc}
\begin{lstlisting}
    graph = """
 a => b        # trigger b if a succeeds
 c:submit => d # trigger d if c submits
 e:finish => f # trigger f if e succeeds or fails
 g:start  => h # trigger h if g starts executing
 i:fail   => j # trigger j if i fails
            """
\end{lstlisting}

A common use of this is to automate recovery from known modes of failure:
\lstset{language=suiterc}
\begin{lstlisting}
    graph = "goodbye:fail => really_goodbye"
\end{lstlisting}
i.e.\ if task \lstinline=goodbye= fails, trigger another task that
(presumably) really says goodbye.

Failure triggering generally requires use of {\em suicide triggers} as
well, to remove the recovery task if it isn't required (otherwise it
would hang about indefinitely in the waiting state):
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = """hello => goodbye
            goodbye:fail => really_goodbye
         goodbye => !really_goodbye # suicide"""
\end{lstlisting}
This means if \lstinline=goodbye= fails, trigger
\lstinline=really_goodbye=; and otherwise, if \lstinline=goodbye=
succeeds, remove \lstinline=really_goodbye= from the suite.

Try running \lstinline=tut/oneoff/suicide=, which also configures
the \lstinline=hello= task's runtime to make it fail, to see how this
works.
\begin{myitemize}
    \item For more on suite dependency graphs see~\ref{ConfiguringScheduling}.
    \item For more on task triggering see~\ref{TriggerTypes}.
\end{myitemize}

\subsection{Runtime Inheritance}

\hilight{ suite: \lstinline=tut/oneoff/inherit= }
\vspace{3mm}

The \lstinline=[runtime]= section is actually a {\em multiple
inheritance} hierarchy. Each subsection is a {\em namespace} that
represents a task, or if it is inherited by other namespaces, a {\em
family}. This allows common configuration to be factored out of related
tasks very efficiently.
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/inherit/suite.rc}
The \lstinline=[root]= namespace provides defaults for all tasks in the suite.
Here both tasks inherit \lstinline=script= from \lstinline=root=, which they
customize with different values of the environment variable
\lstinline=$GREETING=. Note that inheritance from \lstinline=root= is
implicit; from other parents an explicit \lstinline@inherit = PARENT@
is required, as shown below.

\begin{myitemize}
\item For more on runtime inheritance, see~\ref{NIORP}.
\end{myitemize}

\subsection{Triggering Families}

\hilight{ suite: \lstinline=tut/oneoff/ftrigger1= }
\vspace{3mm}

Task families defined by runtime inheritance can also be used as
shorthand in graph trigger expressions. To see this, consider two
``greeter'' tasks that trigger off another task \lstinline=foo=:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = "foo => greeter_1 & greeter_2"
\end{lstlisting}
If we put the common greeting functionality of \lstinline=greeter_1=
and \lstinline=greeter_2= into a special \lstinline=GREETERS= family,
the graph can be expressed more efficiently like this:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = "foo => GREETERS"
\end{lstlisting}
i.e.\ if \lstinline=foo= succeeds, trigger all members of
\lstinline=GREETERS= at once. Here's the full suite with runtime
hierarchy shown:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/ftrigger1/suite.rc}

(Note that we recommend given ALL-CAPS names to task families to help
distinguish them from task names. However, this is just a convention).

Experiment with the \lstinline=tut/oneoff/ftrigger1= suite to see
how this works.

\subsection{Triggering Off Of Families}

\hilight{ suite: \lstinline=tut/oneoff/ftrigger2= }
\vspace{3mm}

Tasks (or families) can also trigger {\em off} other families, but
in this case we need to specify what the trigger means in terms of
the upstream family members. Here's how to trigger another task
\lstinline=bar= if all members of \lstinline=GREETERS= succeed:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = """foo => GREETERS
            GREETERS:succeed-all => bar"""
\end{lstlisting}
Verbose validation in this case reports:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc val -v tut/oneoff/ftrigger2
...
Graph line substitutions occurred:
  IN: GREETERS:succeed-all => bar
  OUT: greeter_1:succeed & greeter_2:succeed => bar
...
\end{lstlisting}
Cylc ignores family member qualifiers like \lstinline=succeed-all= on
the right side of a trigger arrow, where they don't make sense, to
allow the two graph lines above to be combined in simple cases:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = "foo => GREETERS:succeed-all => bar"
\end{lstlisting}

Any task triggering status qualified by \lstinline=-all= or
\lstinline=-any=, for the members, can be used with a family trigger.
For example, here's how to trigger \lstinline=bar= if all members
of \lstinline=GREETERS= finish (succeed or fail) and any of them
succeed:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        graph = """foo => GREETERS
    GREETERS:finish-all & GREETERS:succeed-any => bar"""
\end{lstlisting}
(use of \lstinline@GREETERS:succeed-any@ by itself here would trigger
\lstinline=bar= as soon as any one member of \lstinline=GREETERS=
completed successfully). Verbose validation now begins to show how
family triggers can simplify complex graphs, even for this tiny
two-member family:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc val -v tut/oneoff/ftrigger2
...
Graph line substitutions occurred:
  IN: GREETERS:finish-all & GREETERS:succeed-any => bar
  OUT: ( greeter_1:succeed | greeter_1:fail ) & \
       ( greeter_2:succeed | greeter_2:fail ) & \
       ( greeter_1:succeed | greeter_2:succeed ) => bar
...
\end{lstlisting}

Experiment with \lstinline=tut/oneoff/ftrigger2= to see how this
works.

\begin{myitemize}
\item For more on family triggering, see~\ref{FamilyTriggers}.
\end{myitemize}

\subsection{Suite Visualization}

\lstset{language=suiterc}
You can style dependency graphs with an optional
\lstinline=[visualization]= section, as shown in
\lstinline=tut/oneoff/ftrigger2=:
\lstset{language=suiterc}
\begin{lstlisting}
[visualization]
    default node attributes = "style=filled"
    [[node attributes]]
        foo = "fillcolor=#6789ab", "color=magenta"
        GREETERS = "fillcolor=#ba9876"
        bar = "fillcolor=#89ab67"
\end{lstlisting}

To display the graph in an interactive viewer:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc graph tut/oneoff/ftrigger2 &    # dependency graph
$ cylc graph -n tut/oneoff/ftrigger2 & # runtime inheritance graph
\end{lstlisting}
It should look like Figure~\ref{fig-tut-hello-multi} (with the
GREETERS family node expanded on the right).
\begin{figure}
    \begin{center}
        \includegraphics[height=0.3\textheight]{graphics/png/orig/tut-hello-multi-1.png}
        \hspace{20mm}
        \includegraphics[height=0.3\textheight]{graphics/png/orig/tut-hello-multi-2.png}
        \hspace{20mm}
        \includegraphics[height=0.3\textheight]{graphics/png/orig/tut-hello-multi-3.png}
    \end{center}
    \caption{The {\em tut/oneoff/ftrigger2} dependency and runtime inheritance graphs}
\label{fig-tut-hello-multi}
\end{figure}

Graph styling can be applied to entire families at once, and custom
``node groups'' can also be defined for non-family groups.


\subsection{External Task Scripts}

\hilight{ suite: \lstinline=tut/oneoff/external= }
\vspace{3mm}

The tasks in our examples so far have all had inlined implementation, in
the suite configuration, but real tasks often need to call external
commands, scripts, or executables. To try this, let's return to the
basic Hello World suite and cut the implementation of the task
\lstinline=hello= out to a file \lstinline=hello.sh= in the suite
bin directory:
\lstset{language=bash}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/external/bin/hello.sh}
Make the task script executable, and change the \lstinline=hello= task
runtime section to invoke it:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/external/suite.rc}

If you run the suite now the new greeting from the external task script
should appear in the \lstinline=hello= task stdout log. This works
because cylc automatically adds the suite bin directory to
\lstinline=$PATH= in the environment passed to tasks via their job
scripts. To execute scripts (etc.) located elsewhere you can
refer to the file by its full file path, or set \lstinline=$PATH=
appropriately yourself (this could be done via
\lstinline=$HOME/.profile=, which is sourced at the top of the task job
script, or in the suite configuration itself).

Note the use of \lstinline=set -e= above to make the script abort on
error. This allows the error trapping code in the task job script to
automatically detect unforeseen errors.

\subsection{Cycling Tasks}

\hilight{ suite: \lstinline=tut/cycling/one= }
\vspace{3mm}

So far we've considered non-cycling tasks, which finish without spawning
a successor.

Cycling is based around iterating through date-time or integer sequences. A
cycling task may run at each cycle point in a given sequence (cycle). For
example, a sequence might be a set of date-times every 6 hours starting from a
particular date-time. A cycling task may run for each date-time item (cycle
point) in that sequence.

There may be multiple instances of this type of task running in parallel, if
the opportunity arises and their dependencies allow it. Alternatively, a
sequence can be defined with only one valid cycle point - in that case, a task
belonging to that sequence may only run once.

Open the \lstinline=tut/cycling/one= suite:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/cycling/one/suite.rc}
The difference between cycling and non-cycling suites is all in the
\lstinline=[scheduling]= section, so we will leave the
\lstinline=[runtime]= section alone for now (this will result in
cycling dummy tasks). Note that the graph is now defined under a new
section heading that makes each task under it have a succession of cycle points
ending in $00$ or $12$ hours, between specified initial and final cycle
points (or indefinitely if no final cycle point is given), as shown in
Figure~\ref{fig-tut-one}.

\begin{figure}
    \begin{center}
        %Q Image out of date now
        \includegraphics[width=0.5\textwidth]{graphics/png/orig/tut-one.png}
    \end{center}
    \caption{The \lstinline=tut/cycling/one= suite}
\label{fig-tut-one}
\end{figure}

\lstset{language=transcript}

If you run this suite instances of \lstinline=foo= will spawn in parallel out
to the {\em runahead limit}, and each \lstinline=bar= will trigger off the
corresponding instance of \lstinline=foo= at the same cycle point. The
runahead limit, which defaults to a few cycles but is configurable, prevents
uncontrolled spawning of cycling tasks in suites that are not constrained by
clock triggers in real time operation.

Experiment with \lstinline=tut/cycling/one= to see how cycling tasks work.

\subsubsection{ISO 8601 Date-Time Syntax}

The suite above is a very simple example of a cycling date-time workflow. More
generally, cylc comprehensively supports the ISO 8601 standard for date-time
instants, intervals, and sequences. Cycling graph sections can be specified
using full ISO 8601 recurrence expressions, but these may be simplified
by assuming context information from the suite - namely initial and final cycle
points. One form of the recurrence syntax looks like
\lstinline=Rn/start-date-time/period= (\lstinline=Rn= means run
\lstinline=n= times). In the example above, if the initial cycle point
is always at 00 or 12 hours then \lstinline=[[[T00,T12]]]= could be
written as \lstinline=[[[PT12H]]]=, which is short for
\lstinline=[[[R/initial-cycle-point/PT12H/]]]= - i.e.\ run every 12 hours
indefinitely starting at the initial cycle point. It is possible to add
constraints to the suite to only allow initial cycle points at 00 or 12 hours
e.g.

\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    initial cycle point = 20130808T00
    initial cycle point constraints = T00, T12
\end{lstlisting}
\lstset{language=transcript}

\begin{myitemize}
    %Q Runahead factor now
    \item For a comprehensive description of ISO 8601 based date-time cycling,
        see~\ref{AdvancedCycling}
    \item For more on runahead limiting in cycling suites,
        see~\ref{RunaheadLimit}.
\end{myitemize}

\subsubsection{Inter-Cycle Triggers}
\label{TutInterCyclePointTriggers}

\hilight{ suite: \lstinline=tut/cycling/two= }
\vspace{3mm}

The \lstinline=tut/cycling/two= suite adds inter-cycle dependence
to the previous example:
\begin{lstlisting}
[scheduling]
    [[dependencies]]
        # Repeat with cycle points of 00 and 12 hours every day:
        [[[T00,T12]]]
            graph = "foo[-PT12H] => foo => bar"
\end{lstlisting}
For any given cycle point in the sequence defined by the
cycling graph section heading, \lstinline=bar= triggers off
\lstinline=foo= as before, but now \lstinline=foo= triggers off its own
previous instance \lstinline=foo[-PT12H]=. Date-time offsets in
inter-cycle triggers are expressed as ISO 8601 intervals (12 hours
in this case). Figure~\ref{fig-tut-two} shows how this connects the cycling
graph sections together.
\begin{figure}
    \begin{center}
        \includegraphics[width=0.5\textwidth]{graphics/png/orig/tut-two.png}
    \end{center}
    \caption{The \lstinline=tut/cycling/two= suite}
\label{fig-tut-two}
\end{figure}

Experiment with this suite to see how inter-cycle triggers work.
Note that the first instance of \lstinline=foo=, at suite start-up, will
trigger immediately in spite of its inter-cycle trigger, because cylc
ignores dependence on points earlier than the initial cycle point.
However, the presence of an inter-cycle trigger usually implies something
special has to happen at start-up. If a model depends on its own previous
instance for restart files, for example, then some special process has to
generate the initial set of restart files when there is no previous cycle point
to do it. The following section shows one way to handle this in cylc suites.

\subsubsection{Initial Non-Repeating (R1) Tasks}
\label{initial-non-repeating-r1-tasks}
\hilight{ suite: \lstinline=tut/cycling/three= }
\vspace{3mm}

Sometimes we want to be able to run a task at the initial cycle point, but
refrain from running it in subsequent cycles. We can do this by writing an
extra set of dependencies that are only valid at a single date-time cycle
point. If we choose this to be the initial cycle point, these will only apply
at the very start of the suite.

The cylc syntax for writing this single date-time cycle point occurrence is
\lstinline=R1=, which stands for
\lstinline=R1/no-specified-date-time/no-specified-period=.
This is an adaptation of part of the ISO 8601 date-time standard's recurrence
syntax (\lstinline=Rn/date-time/period=) with some special context information
supplied by cylc for the \lstinline=no-specified-*= data.

The \lstinline=1= in the \lstinline=R1= means run once. As we've specified
no date-time, Cylc will use the initial cycle point date-time by default,
which is what we want. We've also missed out specifying the period - this is
set by cylc to a zero amount of time in this case (as it never
repeats, this is not significant).

For example, in \lstinline=tut/cycling/three=:
\lstset{language=suiterc}
\begin{lstlisting}
[cylc]
    cycle point time zone = +13
[scheduling]
    initial cycle point = 20130808T00
    final cycle point = 20130812T00
    [[dependencies]]
        [[[R1]]]
            graph = "prep => foo"
        [[[T00,T12]]]
            graph = "foo[-PT12H] => foo => bar"
\end{lstlisting}
\lstset{language=transcript}
This is shown in Figure~\ref{fig-tut-three}.

Note that the time zone has been set to \lstinline=+1300= in this case,
instead of UTC (\lstinline=Z=) as before. If no time zone or UTC mode was
set, the local time zone of your machine will be used in the cycle points.


At the initial cycle point, \lstinline=foo= will depend on
\lstinline=foo[-PT12H]= and also on \lstinline=prep=:
\lstset{language=suiterc}
\begin{lstlisting}
prep.20130808T0000+13 & foo.20130807T1200+13 => foo.20130808T0000+13
\end{lstlisting}
\lstset{language=transcript}

Thereafter, it will just look like e.g.:
\lstset{language=suiterc}
\begin{lstlisting}
foo.20130808T0000+13 => foo.20130808T1200+13
\end{lstlisting}
\lstset{language=transcript}

However, in our initial cycle point example, the dependence on
\lstinline=foo.20130807T1200+13= will be ignored, because that task's cycle
point is earlier than the suite's initial cycle point and so it cannot run.
This means that the initial cycle point dependencies for \lstinline=foo=
actually look like:
\lstset{language=suiterc}
\begin{lstlisting}
prep.20130808T0000+13 => foo.20130808T0000+13
\end{lstlisting}
\lstset{language=transcript}

\begin{figure}
    \begin{center}
        \includegraphics[width=0.5\textwidth]{graphics/png/orig/tut-three.png}
    \end{center}
    \caption{The \lstinline=tut/cycling/three= suite}
\label{fig-tut-three}
\end{figure}

\begin{myitemize}
    \item \lstinline=R1= tasks can also be used to make something special
        happen at suite shutdown, or at any single cycle point throughout the
        suite run. For a full primer on cycling syntax,
        see~\ref{AdvancedCycling}.
\end{myitemize}


\subsubsection{Integer Cycling}
\label{TutInteger}
\hilight{ suite: \lstinline=tut/cycling/integer= }
\vspace{3mm}

Cylc can do also do integer cycling for repeating workflows that are not
date-time based.

Open the \lstinline=tut/cycling/integer= suite, which is plotted in
Figure~\ref{fig-tut-int}.
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/cycling/integer/suite.rc}

\begin{figure}
    \begin{center}
        \includegraphics[width=0.65\textwidth]{graphics/png/orig/tut-cyc-int.png}
    \end{center}
    \caption{The \lstinline=tut/cycling/integer= suite}
\label{fig-tut-int}
\end{figure}

The integer cycling notation is intended to look similar to the ISO 8601
date-time notation, but it is simpler for obvious reasons. The example suite
illustrates two recurrence forms,
\lstinline=Rn/start-point/period= and
\lstinline=Rn/period/stop-point=, simplified somewhat using suite context
information (namely the initial and final cycle points). The first form is
used to run one special task called \lstinline=start= at start-up, and for the
main cycling body of the suite; and the second form to run another special task
called \lstinline=stop= in the final two cycles. The \lstinline=P= character
denotes period (interval) just like in the date-time notation.
\lstinline=R/1/P2= would generate the sequence of points \lstinline=1,3,5,...=.

\begin{myitemize}
    \item For more on integer cycling, including a more realistic usage example
        see ~\ref{IntegerCycling}.
\end{myitemize}

\subsection{Jinja2}
\hilight{ suite: \lstinline=tut/oneoff/jinja2= }
\vspace{3mm}

Cylc has built in support for the Jinja2 template processor, which
allows us to embed code in suite configurations to generate the
final result seen by cylc.

The \lstinline=tut/oneoff/jinja2= suite illustrates two common
uses of Jinja2: changing suite content or structure based on the value
of a logical switch; and iteratively generating dependencies and runtime
configuration for groups of related tasks:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/jinja2/suite.rc}

To view the result of Jinja2 processing with the Jinja2 flag
\lstinline@MULTI@ set to \lstinline=False=:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc view --jinja2 --stdout tut/oneoff/jinja2
\end{lstlisting}
\lstset{language=suiterc}
\begin{lstlisting}
[meta]
    title = "A Jinja2 Hello World! suite"
[scheduling]
    [[dependencies]]
        graph = "hello"
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
\end{lstlisting}

And with \lstinline=MULTI= set to \lstinline=True=:
\lstset{language=transcript}
\begin{lstlisting}
$ cylc view --jinja2 --stdout tut/oneoff/jinja2
\end{lstlisting}
\lstset{language=suiterc}
\begin{lstlisting}
[meta]
    title = "A Jinja2 Hello World! suite"
[scheduling]
    [[dependencies]]
        graph = "hello => BYE"
[runtime]
    [[hello]]
        script = "sleep 10; echo Hello World!"
    [[BYE]]
        script = "sleep 10; echo Goodbye World!"
    [[ goodbye_0 ]]
        inherit = BYE
    [[ goodbye_1 ]]
        inherit = BYE
    [[ goodbye_2 ]]
        inherit = BYE
\end{lstlisting}

\subsection{Task Retry On Failure}

\hilight{ suite: \lstinline=tut/oneoff/retry= }
\vspace{3mm}

Tasks can be configured to retry a number of times if they fail.
An environment variable \lstinline=$CYLC_TASK_TRY_NUMBER= increments
from $1$ on each successive try, and is passed to the task to allow
different behaviour on the retry:
\lstset{language=suiterc}
\lstinputlisting{../../../etc/examples/tutorial/oneoff/retry/suite.rc}

If a task with configured retries fails, it goes into the {\em retrying} state
until the next retry delay is up, then it resubmits. It only enters the {\em
failed} state on a final definitive failure.

If a task with configured retries is {\em killed} (by \lstinline=cylc kill= or
via the GUI) it goes to the {\em held} state so that the operator can decide
whether to release it and continue the retry sequence or to abort the retry
sequence by manually resetting it to the {\em failed} state.

Experiment with \lstinline=tut/oneoff/retry= to see how this works.

\subsection{Other Users' Suites}

If you have read access to another user's account (even on another host)
it is possible to use \lstinline=cylc monitor= to look at their suite's
progress without full shell access to their account. To do this, you
will need to copy their suite passphrase to
\lstset{language=transcript}
\begin{lstlisting}
    $HOME/.cylc/SUITE_OWNER@SUITE_HOST/SUITE_NAME/passphrase
\end{lstlisting}
(use of the host and owner names is optional here - see~\ref{passphrases})
{\em and} also retrieve the port number of the running suite from:
\begin{lstlisting}
    ~SUITE_OWNER/cylc-run/SUITE_NAME/.service/contact
\end{lstlisting}
Once you have this information, you can run
\begin{lstlisting}
$ cylc monitor --user=SUITE_OWNER --port=SUITE_PORT SUITE_NAME
\end{lstlisting}
to view the progress of their suite.

Other suite-connecting commands work in the same way; see~\ref{RemoteControl}.

\subsection{Other Things To Try}

Almost every feature of cylc can be tested quickly and easily with a
simple dummy suite. You can write your own, or start from one of the
example suites in \lstinline=/path/to/cylc/examples= (see use of
\lstinline=cylc import-examples= above) - they all run ``out the box''
and can be copied and modified at will.

\begin{myitemize}

\item Change the suite runahead limit in a cycling suite.

\item Stop a suite mid-run with \lstinline=cylc stop=, and restart
it again with \lstinline=cylc restart=.

\item Hold (pause) a suite mid-run with \lstinline=cylc hold=,
    then modify the suite configuration and \lstinline=cylc reload= it
    before using \lstinline=cylc release= to continue (you can also
    reload without holding).

\item Use the gcylc View menu to show the task state color key and
watch tasks in the \lstinline=task-states= example evolve
as the suite runs.

\item Manually re-run a task that has already completed or failed,
    with \lstinline=cylc trigger=.

\item Use an {\em internal queue} to prevent more than an alotted number
    of tasks from running at once even though they are ready -
   see~\ref{InternalQueues}.

\item Configure task event hooks to send an email, or shut the suite down,
    on task failure.

\end{myitemize}
