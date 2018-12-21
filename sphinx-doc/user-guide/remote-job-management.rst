Remote Job Management
=====================

\section{Remote Job Management}

Managing tasks in a workflow requires more than just job execution: Cylc
performs additional actions with \lstinline=rsync= for file transfer, and
direct execution of \lstinline=cylc= sub-commands over non-interactive
SSH.\footnote{Cylc used to run bare shell expressions over SSH, which required
a bash shell and made whitelisting difficult.}

\subsection{SSH-free Job Management?}

Some sites may want to restrict access to job hosts by whitelisting SSH
connections to allow only \lstinline=rsync= for file transfer, and allowing job
execution only via a local batch system that sees the job hosts.\footnote{A
malicious script could be \lstinline=rsync='d and run from a batch job, but
batch jobs are considered easier to audit.} We are investigating the
feasibility of SSH-free job management when a local batch system is available,
but this is not yet possible unless your suite and job hosts also share a
filesystem, which allows Cylc to treat jobs as entirely local.\footnote{The job ID
must also be valid to query and kill the job via the local batch system. This
is not the case for Slurm, unless the \lstinline=--cluster= option is
explicitly used in job query and kill commands, otherwise the job ID is not
recognized by the local Slurm instance.}

\subsection{SSH-based Job Management}

Cylc does not have persistent agent processes running on job hosts to act on
instructions received over the network\footnote{This would be a more complex
solution, in terms of implementation, administration, and security.} so
instead we execute job management commands directly on job hosts over SSH.
Reasons for this include:
\begin{itemize}
  \item it works equally for batch system and background jobs
  \item SSH is {\em required} for background jobs, and for batch jobs if the
    batch system is not available on the suite host
  \item {\em querying the batch system alone is not sufficient for full job
    polling functionality} because jobs can complete (and then be forgotten by
    the batch system) while the network, suite host, or suite server program is
    down (e.g.\ between suite shutdown and restart)
    \begin{itemize}
      \item to handle this we get the automatic job wrapper code to write
        job messages and exit status to {\em job status files} that are
        interrogated by suite server programs during job polling operations
      \item job status files reside on the job host, so the interrogation
        is done over SSH
    \end{itemize}
  \item job status files also hold batch system name and job ID; this is
    written by the job submit command, and read by job poll and kill commands
    (all over SSH)
\end{itemize}

\subsection{A Concrete Example}

The following suite, registered as \lstinline=suitex=, is used to illustrate
our current SSH-based remote job management. It submits two jobs to a remote,
and a local task views a remote job log then polls and kills the remote jobs.

\lstset{language=suiterc}
\begin{lstlisting}
# suite.rc
[scheduling]
   [[dependencies]]
          graph = "delayer => master & REMOTES"
[runtime]
   [[REMOTES]]
      script = "sleep 30"
       [[[remote]]]
           host = wizard
           owner = hobo
   [[remote-a, remote-b]]
       inherit = REMOTES
   [[delayer]]
      script = "sleep 10"
   [[master]]
       script = """
 sleep 5
 cylc cat-log -m c -f o $CYLC_SUITE_NAME remote-a.1
 sleep 2
 cylc poll $CYLC_SUITE_NAME REMOTES.1
 sleep 2
 cylc kill $CYLC_SUITE_NAME REMOTES.1
 sleep 2
 cylc remove $CYLC_SUITE_NAME REMOTES.1"""
\end{lstlisting}

The {\em delayer} task just separates suite start-up from remote job
submission, for clarity when watching the job host (e.g.\ with
\lstinline=watch -n 1 find ~/cylc-run/suitex=).

Global config specifies the path to the remote Cylc executable, says
to retrieve job logs, and not to use a remote login shell:
\begin{lstlisting}
# global.rc
[hosts]
   [[wizard]]
       cylc executable = /opt/bin/cylc
       retrieve job logs = True
       use login shell = False
\end{lstlisting}

On running the suite, remote job host actions were captured in the transcripts
below by wrapping the \lstinline=ssh=, \lstinline=scp=, and \lstinline=rsync=
executables in scripts that log their command lines before taking action.

% SECOND HALF OF THE SECTION, omitted from HTML copy (formatting errors).

\renewcommand*\DTstylecomment{\normalfont\ttfamily\color{comments}}
\renewcommand*\DTstyle{\bf\ttfamily\textcolor{identifiers}}

\subsubsection{create suite run directory and install source files}

Done by \lstinline=rose suite-run= before suite start-up
(the command will be migrated to Cylc soon though).

\begin{itemize}
  \item with \lstinline=--new= it invokes bash over SSH and a raw shell
    expression, to delete previous-run files
  \item it invokes itself over over SSH to create top level suite directories
    and install source files
    \begin{itemize}
      \item skips installation if server UUID file is found on the job host
        (indicates a shared filesystem)
    \end{itemize}
  \item uses \lstinline=rsync= for suite source file installation
  \item (note the same directory structure is used on suite and job hosts, for
    consistency and simplicity, and because the suite host can also be a job host)
\end{itemize}

\lstset{breaklines=true}
\lstset{language=jobhosts}

\vspace{5mm}
\begin{lstlisting}
# rose suite-run --new only: initial clean-out
ssh -oBatchMode=yes -oConnectTimeout=10 hobo@wizard bash -l -O extglob -c 'cd; echo '"'"'673d7a0d-7816-42a4-8132-4b1ab394349c'"'"'; ls -d -r cylc-run/suitex/work cylc-run/suitex/share/cycle cylc-run/suitex/share cylc-run/suitex; rm -fr cylc-run/suitex/work cylc-run/suitex/share/cycle cylc-run/suitex/share cylc-run/suitex; (cd ; rmdir -p cylc-run/suitex/work cylc-run/suitex/share/cycle cylc-run/suitex/share cylc-run 2>/dev/null || true)'

# rose suite-run: test for shared filesystem and create share/cycle directories
ssh -oBatchMode=yes -oConnectTimeout=10 -n hobo@wizard env ROSE_VERSION=2018.02.0 CYLC_VERSION=7.6.x bash -l -c '"$0" "$@"' rose suite-run -vv -n suitex --run=run --remote=uuid=231cd6a1-6d61-476d-96e1-4325ef9216fc,now-str=20180416T042319Z

# rose suite-run: install suite source directory to job host
rsync -a --exclude=.* --timeout=1800 --rsh=ssh -oBatchMode=yes -oConnectTimeout=10 --exclude=231cd6a1-6d61-476d-96e1-4325ef9216fc --exclude=log/231cd6a1-6d61-476d-96e1-4325ef9216fc --exclude=share/231cd6a1-6d61-476d-96e1-4325ef9216fc --exclude=share/cycle/231cd6a1-6d61-476d-96e1-4325ef9216fc --exclude=work/231cd6a1-6d61-476d-96e1-4325ef9216fc --exclude=/.* --exclude=/cylc-suite.db --exclude=/log --exclude=/log.* --exclude=/state --exclude=/share --exclude=/work ./ hobo@wizard:cylc-run/suitex
   # (internal rsync)
   ssh -oBatchMode=yes -oConnectTimeout=10 -l hobo wizard rsync --server -logDtpre.iLsfx --timeout=1800 . cylc-run/suitex
   # (internal rsync, back from hobo@wizard)
   rsync --server -logDtpre.iLsfx --timeout=1800 . cylc-run/suitex
\end{lstlisting}

\vspace{5mm}
Result:
\lstset{language=sh}
{\scriptsize
\dirtree{%
.1 \textasciitilde/cylc-run/suitex.
.2 log->log.20180418T025047Z\DTcomment{\textbf{LOG DIRECTORIES}}.
.2 log.20180418T025047Z\DTcomment{log directory for current suite run}.
.2 suiter.rc.
.2 xxx\DTcomment{(any suite source sub-dirs or file)}.
.2 work\DTcomment{\textbf{JOB WORK DIRECTORIES}}.
.2 share\DTcomment{\textbf{SUITE SHARE DIRECTORY}}.
.3 cycle.
}
}

\subsubsection{server installs service directory}

\begin{itemize}
  \item server address and credentials, so that clients such as
    \lstinline=cylc message=  executed by jobs can connect
  \item done just before the first job is submitted to a remote, and at
    suite restart for the remotes of jobs running when the suite went
    down (server host, port, etc.\ may change at restart)
  \item uses SSH to invoke \lstinline=cylc remote-init= on 
    job hosts. If the remote command does not find a server-side UUID file
    (which would indicate a shared filesystem) it reads a tar archive of
    the service directory from stdin, and unpacks it to install.
\end{itemize}

\lstset{language=jobhosts}

\vspace{5mm}
\begin{lstlisting}
# cylc remote-init: install suite service directory
ssh -oBatchMode=yes -oConnectTimeout=10 hobo@wizard env CYLC_VERSION=7.6.x /opt/bin/cylc remote-init '066592b1-4525-48b5-b86e-da06eb2380d9' '$HOME/cylc-run/suitex'
\end{lstlisting}

Result:
{\scriptsize
\dirtree{%
.1 \textasciitilde/cylc-run/suitex.
.2 .service\DTcomment{\textbf{SUITE SERVICE DIRECTORY}}. 
.3 contact\DTcomment{{\color{blue} server address information}}.
.3 passphrase\DTcomment{{\color{blue} suite passphrase}}.
.3 ssl.cert\DTcomment{{\color{blue} suite SSL certificate}}.
.2 log->log.20180418T025047Z\DTcomment{\textbf{LOG DIRECTORIES}}.
.2 log.20180418T025047Z\DTcomment{log directory for current suite run}.
.2 suiter.rc.
.2 xxx\DTcomment{(any suite source sub-dirs or file)}.
.2 work\DTcomment{\textbf{JOB WORK DIRECTORIES}}.
.2 share\DTcomment{\textbf{SUITE SHARE DIRECTORY}}.
.3 cycle.
}
}

\subsubsection{server submits jobs}
\begin{itemize}
  \item done when tasks are ready to run, for multiple jobs at once
  \item uses SSH to invoke \lstinline=cylc jobs-submit= on the
    remote - to read job scripts from stdin, write them to disk, and submit
    them to run
\end{itemize}

\lstset{language=jobhosts}

\vspace{5mm}
\begin{lstlisting}
# cylc jobs-submit: submit two jobs
ssh -oBatchMode=yes -oConnectTimeout=10 hobo@wizard env CYLC_VERSION=7.6.x /opt/bin/cylc jobs-submit '--remote-mode' '--' '$HOME/cylc-run/suitex/log/job' '1/remote-a/01' '1/remote-b/01'
\end{lstlisting}

Result:
{\scriptsize
\dirtree{%
.1 \textasciitilde/cylc-run/suitex.
.2 .service\DTcomment{\textbf{SUITE SERVICE DIRECTORY}}. 
.3 contact\DTcomment{{\color{blue} server address information}}.
.3 passphrase\DTcomment{{\color{blue} suite passphrase}}.
.3 ssl.cert\DTcomment{{\color{blue} suite SSL certificate}}.
.2 log->log.20180418T025047Z\DTcomment{\textbf{LOG DIRECTORIES}}.
.2 log.20180418T025047Z\DTcomment{log directory for current suite run}.
.3 job\DTcomment{job logs (to be distinguished from \lstinline=log/suite/= on the suite host)}.
.4 1\DTcomment{cycle point}.
.5 remote-a\DTcomment{task name}.
.6 01\DTcomment{job submit number}.
.7 job\DTcomment{{\color{blue}job script}}.
.7 job.out\DTcomment{{\color{blue} job stdout}}.
.7 job.err\DTcomment{{\color{blue} job stderr}}.
.7 job.status\DTcomment{{\color{blue} job status}}.
.6 NN->0l\DTcomment{symlink to latest submit number}.
.5 remote-b\DTcomment{task name}.
.6 01\DTcomment{job submit number}.
.7 job\DTcomment{{\color{blue}job script}}.
.7 job.out\DTcomment{{\color{blue} job stdout}}.
.7 job.err\DTcomment{{\color{blue} job stderr}}.
.7 job.status\DTcomment{{\color{blue} job status}}.
.6 NN->0l\DTcomment{symlink to latest submit number}.
.2 suiter.rc.
.2 xxx\DTcomment{(any suite source sub-dirs or file)}.
.2 work\DTcomment{\textbf{JOB WORK DIRECTORIES}}.
.3 1\DTcomment{cycle point}.
.4 remote-a\DTcomment{task name}.
.5 xxx\DTcomment{(any files written by job to PWD)}.
.4 remote-b\DTcomment{task name}.
.5 xxx\DTcomment{(any files written by job to PWD)}.
.2 share\DTcomment{\textbf{SUITE SHARE DIRECTORY}}.
.3 cycle.
.3 xxx\DTcomment{(any job-created sub-dirs and files)}.
}
}

\subsubsection{server tracks job progress}

\begin{itemize}
  \item jobs send messages back to the server program on the suite host
    \begin{itemize}
      \item directly: client-server HTTPS over the network (requires service
        files installed - see above)
      \item indirectly: re-invoke clients on the suite host (requires reverse SSH)
    \end{itemize}
  \item OR server polls jobs at intervals (requires job polling - see below)
\end{itemize}

\subsubsection{user views job logs}

\begin{itemize}
  \item command \lstinline=cylc cat-log= via CLI or GUI, invokes itself over
    SSH to the remote
  \item suites will serve job logs in future, but this will still be needed
    (e.g.\ if the suite is down)
\end{itemize}

\vspace{5mm}
\begin{lstlisting}
# cylc cat-log: view a job log
ssh -oBatchMode=yes -oConnectTimeout=10 -n hobo@wizard env CYLC_VERSION=7.6.x /opt/bin/cylc cat-log --remote-arg='$HOME/cylc-run/suitex/log/job/1/remote-a/NN/job.out' --remote-arg=cat --remote-arg='tail -n +1 -F %(filename)s' suitex
\end{lstlisting}


\subsubsection{server cancels or kills jobs}

\begin{itemize}
  \item done automatically or via user command \lstinline=cylc kill=, for
    multiple jobs at once
  \item uses SSH to invoke \lstinline=cylc jobs-kill= on the
    remote, with job log paths on the command line. Reads job ID from the
    job status file.
\end{itemize}

\vspace{5mm}
    \begin{lstlisting}
# cylc jobs-kill: kill two jobs
ssh -oBatchMode=yes -oConnectTimeout=10 hobo@wizard env CYLC_VERSION=7.6.x /opt/bin/cylc jobs-kill '--' '$HOME/cylc-run/suitex/log/job' '1/remote-a/01' '1/remote-b/01'
    \end{lstlisting}

\subsubsection{server polls jobs}

\begin{itemize}
  \item done automatically or via user command \lstinline=cylc poll=, for
    multiple jobs at once
  \item uses SSH to invoke \lstinline=cylc jobs-poll= on the
    remote, with job log paths on the command line. Reads job ID from the
    job status file.
\end{itemize}

\vspace{5mm}
    \begin{lstlisting}
# cylc jobs-poll: poll two jobs
ssh -oBatchMode=yes -oConnectTimeout=10 hobo@wizard env CYLC_VERSION=7.6.x /opt/bin/cylc jobs-poll '--' '$HOME/cylc-run/suitex/log/job' '1/remote-a/01' '1/remote-b/01'
    \end{lstlisting}


\subsubsection{server retrieves jobs logs}

\begin{itemize}
  \item done at job completion, according to global config
  \item uses \lstinline=rsync=
\end{itemize}

\vspace{5mm}
    \begin{lstlisting}
# rsync: retrieve two job logs
rsync -a --rsh=ssh -oBatchMode=yes -oConnectTimeout=10 --include=/1 --include=/1/remote-a --include=/1/remote-a/01 --include=/1/remote-a/01/** --include=/1/remote-b --include=/1/remote-b/01 --include=/1/remote-b/01/** --exclude=/** hobo@wizard:$HOME/cylc-run/suitex/log/job/ /home/vagrant/cylc-run/suitex/log/job/
   # (internal rsync)
   ssh -oBatchMode=yes -oConnectTimeout=10 -l hobo wizard rsync --server --sender -logDtpre.iLsfx . $HOME/cylc-run/suitex/log/job/
   # (internal rsync, back from hobo@wizard)
   rsync --server --sender -logDtpre.iLsfx . /home/hobo/cylc-run/suitex/log/job/
    \end{lstlisting}

\subsubsection{server tidies job remote at shutdown}

\begin{itemize}
  \item removes \lstinline=.service/contact= so that clients won't repeatedly
    try to connect
\end{itemize}

\vspace{5mm}
    \begin{lstlisting}
# cylc remote-tidy: remove the remote suite contact file
ssh -oBatchMode=yes -oConnectTimeout=10 hobo@wizard env CYLC_VERSION=7.6.x /opt/bin/cylc remote-tidy '$HOME/cylc-run/suitex'
    \end{lstlisting}

\subsection{Other Use of SSH in Cylc}

\begin{itemize}
  \item see if a suite is running on another host with a shared
    filesystem - see \lstinline=detect_old_contact_file()= in
    \lstinline=lib/cylc/suite_srv_files_mgr.py=
  \item cat content of a remote service file over SSH, if possible, for
    clients on that do not have suite credentials installed - see
    \lstinline=_load_remote_item()= in \lstinline=suite_srv_files_mgr.py=
\end{itemize}
