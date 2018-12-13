Cylc 6 Migration Ref
====================

Text here.

\section{Cylc 6 Migration Reference}
\label{cylc-6-migration}

Cylc 6 introduced new date-time-related syntax for the suite.rc file. In
some places, this is quite radically different from the earlier syntax.

\subsection{Timeouts and Delays}
\label{cylc-6-migration-timeout-delays}

Timeouts and delays such as \lstinline=[cylc][[events]]timeout= or
\lstinline=[runtime][[my_task]][[[job]]]execution retry delays= were written in
a purely numeric form before cylc 6, in seconds, minutes (most common), or
hours, depending on the setting.

They are now written in an ISO 8601 duration form, which has the benefit
that the units are user-selectable (use 1 day instead of 1440 minutes)
and explicit.

Nearly all timeouts and delays in cylc were in minutes, except for:\\*
\lstinline=[runtime][[my_task]][[[suite state polling]]]interval= \\*
\lstinline=[runtime][[my_task]][[[simulation mode]]]run time range= \\*
which were in seconds, and\\*
\lstinline=[scheduling]runahead limit=\\*
which was in hours (this is a special case discussed below
in~\ref{cylc-6-migration-runahead-limit}).

See Table \ref{cylc-6-migration-timeout-delays-table}.

\begin{table}[ht]
\caption{Timeout/Delay Syntax Change Examples}
\centering
\begin{tabular}{ l c c }
Setting & Pre-Cylc-6 & Cylc-6+ \\
\hline
\lstinline=[cylc][[events]]timeout= & 180 & PT3H \\
\lstinline=[runtime][[my_task]][[[job]]]execution retry delays= & 2*30, 360, & 2*PT30M, PT6H, \\
 & 1440 & P1D \\
\lstinline=[runtime][[my_task]][[[suite state polling]]]interval= & 2 & PT2S \\
\end{tabular}
\label{cylc-6-migration-timeout-delays-table}
\end{table}

\subsection{Runahead Limit}
\label{cylc-6-migration-runahead-limit}

See~\ref{runahead limit}.

The \lstinline=[scheduling]runahead limit= setting was written as a number of
hours in pre-cylc-6 suites. This is now in ISO 8601 format for date-time
cycling suites, so \lstinline@[scheduling]runahead limit=36@ would be written
\lstinline@[scheduling]runahead limit=PT36H@.

There is a new preferred alternative to \lstinline=runahead limit=,
\lstinline=[scheduling]max active cycle points=. This allows the user to
configure how many cycle points can run at once (default \lstinline=3=). See
\ref{max active cycle points}.

\subsection{Cycle Time/Cycle Point}
\label{cylc-6-migration-cycle-point}

See~\ref{initial cycle point}.

The following suite.rc settings have changed name (Table
\ref{cylc-6-migration-cycle-point-time-table}):

\begin{table}[ht]
\caption{Cycle Point Renaming}
\centering
\begin{tabular}{ l l }
Pre-Cylc-6 & Cylc-6+ \\
\hline
\lstinline=[scheduling]initial cycle time= & \lstinline=[scheduling]initial cycle point= \\
\lstinline=[scheduling]final cycle time= & \lstinline=[scheduling]final cycle point= \\
\lstinline=[visualization]initial cycle time= & \lstinline=[visualization]initial cycle point= \\
\lstinline=[visualization]final cycle time= & \lstinline=[visualization]final cycle point= \\
\end{tabular}
\label{cylc-6-migration-cycle-point-time-table}
\end{table}

This change is to reflect the fact that cycling in cylc 6+ can now be over
e.g.\ integers instead of being purely based on date-time.

Date-times written in \lstinline=initial cycle time= and
\lstinline=final cycle time= were in a cylc-specific 10-digit (or less)
\lstinline=CCYYMMDDhh= format, such as \lstinline=2014021400= for 00:00 on
the 14th of February 2014.

Date-times are now required to be ISO 8601 compatible. This can be achieved
easily enough by inserting a \lstinline=T= between the day and the hour
digits.

\begin{table}[ht]
\caption{Cycle Point Syntax Example}
\centering
\begin{tabular}{ l c c }
Setting & Pre-Cylc-6 & Cylc-6+ \\
\hline
\lstinline=[scheduling]initial cycle time= & 2014021400 & 20140214T00 \\
\end{tabular}
\label{cylc-6-migration-cycle-point-syntax-table}
\end{table}

\subsection{Cycling}
\label{cylc-6-migration-cycling}

Special {\em start-up} and {\em cold-start} tasks have been removed from cylc
6. Instead, use the initial/run-once notation as detailed
in~\ref{initial-non-repeating-r1-tasks} and~\ref{AdvancedStartingUp}.

{\em Repeating asynchronous tasks} have also been removed because non date-time
workflows can now be handled more easily with integer cycling. See for instance
the satellite data processing example documented in~\ref{IntegerCycling}.

For repeating tasks with hour-based cycling the syntax has only minor changes:

Pre-cylc-6:
\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    ...
    [[dependencies]]
        [[[0,12]]]
            graph = foo[T-12] => foo & bar => baz
\end{lstlisting}
\lstset{language=transcript}

\lstset{language=suiterc}
\begin{lstlisting}
[scheduling]
    ...
    [[dependencies]]
        [[[T00,T12]]]
            graph = foo[-PT12H] => foo & bar => baz
\end{lstlisting}
\lstset{language=transcript}

Hour-based cycling section names are easy enough to convert, as seen in Table
\ref{cylc-6-migration-cycling-hours-table}.

\begin{table}[ht]
\caption{Hourly Cycling Sections}
\centering
\begin{tabular}{ l l }
Pre-Cylc-6 & Cylc-6+ \\
\hline
\lstinline=[scheduling][[dependencies]][[[0]]]= & \lstinline=[scheduling][[dependencies]][[[T00]]]= \\
\lstinline=[scheduling][[dependencies]][[[6]]]= & \lstinline=[scheduling][[dependencies]][[[T06]]]= \\
\lstinline=[scheduling][[dependencies]][[[12]]]= & \lstinline=[scheduling][[dependencies]][[[T12]]]= \\
\lstinline=[scheduling][[dependencies]][[[18]]]= & \lstinline=[scheduling][[dependencies]][[[T18]]]= \\
\end{tabular}
\label{cylc-6-migration-cycling-hours-table}
\end{table}

The graph text in hour-based cycling is also easy to convert, as seen in
Table \ref{cylc-6-migration-cycling-hours-offset-table}.

\begin{table}[ht]
\caption{Hourly Cycling Offsets}
\centering
\begin{tabular}{ l l }
Pre-Cylc-6 & Cylc-6+ \\
\hline
\lstinline=my_task[T-6]= & \lstinline=my_task[-PT6H]= \\
\lstinline=my_task[T-12]= & \lstinline=my_task[-PT12H]= \\
\lstinline=my_task[T-24]= & \lstinline=my_task[-PT24H]= or even \lstinline=my_task[-P1D]= \\
\end{tabular}
\label{cylc-6-migration-cycling-hours-offset-table}
\end{table}

\subsection{No Implicit Creation of Tasks by Offset Triggers}
\label{cylc-6-migration-implicit-cycling}

Prior to cylc-6 intercycle offset triggers implicitly created task instances at
the offset cycle points. For example, this pre cylc-6 suite automatically
creates instances of task \lstinline=foo= at the offset hours
\lstinline=3,9,15,21= each day, for task \lstinline=bar= to trigger off at
\lstinline=0,6,12,18=:
\lstset{language=suiterc}
\begin{lstlisting}
# Pre cylc-6 implicit cycling.
[scheduling]
   initial cycle time = 2014080800
   [[dependencies]]
      [[[00,06,12,18]]]
         # This creates foo instances at 03,09,15,21:
         graph = foo[T-3] => bar
\end{lstlisting}

Here's the direct translation to cylc-6+ format:
\lstset{language=suiterc}
\begin{lstlisting}
# In cylc-6+ this suite will stall.
[scheduling]
   initial cycle point = 20140808T00
   [[dependencies]]
      [[[T00,T06,T12,T18]]]
         # This does NOT create foo instances at 03,09,15,21:
         graph = foo[-PT3H] => bar
\end{lstlisting}

This suite fails validation with
\lstinline=ERROR: No cycling sequences defined for foo=,
and at runtime it would stall with \lstinline=bar= instances waiting on
non-existent offset \lstinline=foo= instances (note that these
appear as ghost nodes in graph visualisations).

To fix this, explicitly define the cycling of with an offset cycling sequence:
\lstinline=foo=:
\lstset{language=suiterc}
\begin{lstlisting}
# Cylc-6+ requires explicit task instance creation.
[scheduling]
   initial cycle point = 20140808T00
   [[dependencies]]
      [[[T03,T09,T15,T21]]]
         graph = foo
      [[[T00,T06,T12,T18]]]
         graph = foo[-PT3H] => bar
\end{lstlisting}

Implicit task creation by offset triggers is no longer allowed because it is
error prone: a mistaken task cycle point offset should cause a failure
rather than automatically creating task instances on the wrong cycling
sequence.
