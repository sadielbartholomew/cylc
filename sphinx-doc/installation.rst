Installation
============

\section{Installation}
\label{Requirements}

Cylc runs on Linux. It is tested quite thoroughly on modern RHEL and Ubuntu
distros. Some users have also managed to make it work on other Unix variants
including Apple OS X, but they are not officially tested and supported.

\subsection{Third-Party Software Packages}

{\bf Python 2 \lstinline@>=@ 2.6} is required.
{\bf Python 2 \lstinline@>=@ 2.7.9} is recommended for the best security.
Python 2 should already be installed in your Linux system.
\url{https://python.org/}.

For Cylc's HTTPS communications layer:
\begin{myitemize}
  \item {\bf OpenSSL} - \url{https://www.openssl.org/}
  \item {\bf pyOpenSSL} - \url{http://www.pyopenssl.org/}
  \item {\bf python-requests} - \url{http://docs.python-requests.org/}
  \item ({\bf python-urllib3} - should be bundled with python-requests)
\end{myitemize}

The following packages are highly recommended, but are technically optional as
you can construct and run suites without dependency graph visualisation or
the Cylc GUIs:

\begin{myitemize}
  \item {\bf PyGTK} - GUI toolkit \url{http://www.pygtk.org}.  {\em Note PyGTK
    typically comes with your system Python. It is allegedly quite
    difficult to install if you need to do so for another Python version.}
    \item {\bf Graphviz} - graph layout engine (tested 2.36.0):
      \url{http://www.graphviz.org}.
    \item {\bf Pygraphviz} - Python Graphviz interface (tested 1.2):
       \url{http://pygraphviz.github.io/}. To build this you may need some {\em
       devel} packages too:
          \begin{myitemize}
              \item python-devel
              \item graphviz-devel
          \end{myitemize}
\end{myitemize}

The Cylc Review service does not need any further packages to those
already required (Python 2) and bundled with Cylc (CherryPy and Jinja2).

The following packages are necessary for running all the tests in Cylc:

\begin{myitemize}
  \item {\bf mock} - \url{https://mock.readthedocs.io}
\end{myitemize}

The User Guide is generated from \LaTeX source files by running
\lstinline=make= in the top level Cylc directory. The specific packages
required may vary by distribution, e.g.:

\begin{myitemize}
    \item texlive
    \item texlive-tocloft
    \item texlive-framed
    \item texlive-preprint (for \lstinline=fullpage.sty=)
    \item texlive-tex4ht
    \item texlive-generic-extra (for \lstinline=dirtree.sty=)
\end{myitemize}

To generate the HTML User Guide {\bf ImageMagick} is also needed.

In most modern Linux distributions all of the software above can be installed
via the system package manager. Otherwise download packages manually and follow
their native installation instructions. To check that all (non \LaTeX packages)
are installed properly:

\lstset{language=transcript}
\begin{lstlisting}
$ cylc check-software
Checking your software...

Individual results:

.. code-block:: none

	=============================================================================
	Package (version requirements)                        Outcome (version found)
	=============================================================================
								*REQUIRED SOFTWARE*                                 
	Python (2.6+, <3)...................FOUND & min. version MET (2.7.12.final.0)

	  *OPTIONAL SOFTWARE for the GUI & dependency graph visualisation*           
	Python:pygtk (2.0+).........................FOUND & min. version MET (2.24.0)
	graphviz (any).................................................FOUND (2.38.0)
	Python:pygraphviz (any).........................................FOUND (1.3.1)

					*OPTIONAL SOFTWARE for the HTML User Guide*                     
	ImageMagick (any).............................................FOUND (6.8.9-9)

			   *OPTIONAL SOFTWARE for the HTTPS communications layer*                
	Python:urllib3 (any)...........................................FOUND (1.13.1)
	Python:OpenSSL (any)...........................................FOUND (17.2.0)
	Python:requests (2.4.2+).....................FOUND & min. version MET (2.9.1)

					*OPTIONAL SOFTWARE for the LaTeX User Guide*                     
	TeX:framed (any)..................................................FOUND (n/a)
	TeX (3.0+)..............................FOUND & min. version MET (3.14159265)
	TeX:preprint (any)................................................FOUND (n/a)
	TeX:tex4ht (any)..................................................FOUND (n/a)
	TeX:tocloft (any).................................................FOUND (n/a)
	TeX:texlive (any).................................................FOUND (n/a)
	=============================================================================

Summary:
                        ****************************                             
                           Core requirements: ok                                
                           Full-functionality: ok                                
                        **************************** 
\end{lstlisting}

If errors are reported then the packages concerned are either not installed or
not in your Python search path. (Note that \lstinline=cylc check-software= has
become quite trivial as we've removed or bundled some former dependencies, but
in future we intend to make it print a comprehensive list of library versions
etc.\ to include in with bug reports.)

To check for specific packages only, supply these as arguments to the
\lstinline=check-software= command, either in the form used in the output of
the bare command, without any parent package prefix and colon, or
alternatively all in lower-case, should the given form contain capitals. For
example:

\begin{lstlisting}
$ cylc check-software Python graphviz imagemagick
\end{lstlisting}

With arguments, check-software provides an exit status indicating a
collective pass (zero) or a failure of that number of packages to satisfy
the requirements (non-zero integer).

\subsection{Software Bundled With Cylc}

Cylc bundles several third party packages which do not need to be installed
separately.

\begin{myitemize}
  \item {\bf cherrypy 6.0.2} (slightly modified): a pure Python HTTP framework
    that we use as a web server for communication between server processes
    (suite server programs) and client programs (running tasks, GUIs, CLI commands).
    Client communication is via the Python {\bf requests} library if available
    (recommended) or else pure Python via {\bf urllib2}.
\newline \url{http://www.cherrypy.org/}
\newline \url{http://docs.python-requests.org/}
  \item {\bf Jinja2 2.10}: a full featured template engine for Python, and its
    dependency {\bf MarkupSafe 0.23}; both BSD licensed.
\newline \url{http://jinja.pocoo.org/}
\newline \url{http://www.pocoo.org/projects/markupsafe/}
  \item the {\bf xdot} graph viewer (modified), LGPL licensed:
    \newline \url{https://github.com/jrfonseca/xdot.py}
\end{myitemize}

\subsection{Installing Cylc}
\label{InstallCylc}

Cylc releases can be downloaded from \url{https://cylc.github.io/cylc}.

The wrapper script \lstinline=usr/bin/cylc= should be installed to
the system executable search path (e.g.\ \lstinline=/usr/local/bin/=) and
modified slightly to point to a location such as \lstinline=/opt= where
successive Cylc releases will be unpacked side by side.

To install Cylc, unpack the release tarball in the right location, e.g.\
\lstinline=/opt/cylc-7.7.0=, type \lstinline=make= inside the release
directory, and set site defaults - if necessary - in a site global config file
(below).

Make a symbolic link from \lstinline=cylc= to the latest installed version:
\lstinline=ln -s /opt/cylc-7.7.0 /opt/cylc=. This will be invoked by the
central wrapper if a specific version is not requested. Otherwise, the
wrapper will attempt to invoke the Cylc version specified in
\lstinline@$CYLC_VERSION@, e.g.\ \lstinline@CYLC_VERSION=7.7.0@. This variable
is automatically set in task job scripts to ensure that jobs use the same Cylc
version as their parent suite server program.  It can also be set by users,
manually or in login scripts, to fix the Cylc version in their environment.

Installing subsequent releases is just a matter of unpacking the new tarballs
next to the previous releases, running \lstinline=make= in them, and copying
in (possibly with modifications) the previous site global config file.

\subsubsection{Local User Installation}
\label{LocalInstall}

It is easy to install Cylc under your own user account if you don't have
root or sudo access to the system: just put the central Cylc wrapper in
\lstinline=$HOME/bin/= (making sure that is in your \lstinline=$PATH=) and
modify it to point to a directory such as \lstinline=$HOME/cylc/= where you
will unpack and install release tarballs. Local installation of third party
dependencies like Graphviz is also possible, but that depends on the particular
installation methods used and is outside of the scope of this document.

\subsubsection{Create A Site Config File}

Site and user global config files define some important parameters that affect
all suites, some of which may need to be customized for your site.
See~\ref{SiteAndUserConfiguration} for how to generate an initial site file and
where to install it. All legal site and user global config items are defined
in~\ref{SiteRCReference}.

\subsubsection{Configure Site Environment on Job Hosts}
\label{Configure Site Environment on Job Hosts}

If your users submit task jobs to hosts other than the hosts they use to run
their suites, you should ensure that the job hosts have the correct environment
for running cylc. A cylc suite generates task job scripts that normally invoke
\lstinline=bash -l=, i.e. it will invoke bash as a login shell to run the job
script. Users and sites should ensure that their bash login profiles are able
to set up the correct environment for running cylc and their task jobs.

Your site administrator may customise the environment for all task jobs by adding
a \lstinline=<cylc-dir>/etc/job-init-env.sh= file and populate it with the
appropriate contents. If customisation is still required, you can add your own
\lstinline=${HOME}/.cylc/job-init-env.sh= file and populate it with the
appropriate contents.

\begin{myitemize}
\item \lstinline=${HOME}/.cylc/job-init-env.sh=
\item \lstinline=<cylc-dir>/etc/job-init-env.sh=
\end{myitemize}

The job will attempt to source the first of these files it finds to set up its
environment.

\subsection{Automated Tests}
\label{RTAST}

The cylc test battery is primarily intended for developers to check that
changes to the source code don't break existing functionality. Note that
some test failures can be expected to result from suites timing out,
even if nothing is wrong, if you run too many tests in parallel. See
\lstinline=cylc test-battery --help=.
