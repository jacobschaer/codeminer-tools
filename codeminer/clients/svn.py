import os
import subprocess
from typing import Dict, List, Optional, Union, Tuple

from codeminer.clients.commandline import CommandLineClient

class SVNException(Exception):
    pass

class SVNClient(CommandLineClient):
    def __init__(self, binary='svn', cwd=None):
        self.cwd = cwd
        self.name = 'SVN'
        env = os.environ.copy()
        super().__init__(binary, env=env)

    def cat(self, target, revision=None, ignore_keywords=False, cwd=None, *args, **kwargs):
        """Output the content of specified files or URLs."""
        options = {}
        flags = []
        arguments = []

        if type(target) == str:
            arguments.append(target)
        else:
            arguments += target
        if revision is not None:
            options['r'] = revision
        if ignore_keywords:
            flags.append('ignore-keywords')
        if cwd is None:
            cwd = self.cwd
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('cat', *arguments, flags=flags,
            cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            return out, errs

    def log(self, path=None, revision=None, change=None, quiet=False, verbose=False, use_merge_history=False,
            targets=None, stop_on_copy=False, incremental=False, xml=False, limit=None, all_props=False,
            no_revprops=False, revprop=None, depth=None, diff=False, diff_cmd = None, internal_diff=False,
            extension=None, search=None, search_and=None, cwd=None, *args, **kwargs):
        """  -r [--revision] ARG      : ARG (some commands also take ARG1:ARG2 range)
                                         A revision argument can be one of:
                                            NUMBER       revision number
                                            '{' DATE '}' revision at start of the date
                                            'HEAD'       latest in repository
                                            'BASE'       base rev of item's working copy
                                            'COMMITTED'  last commit at or before BASE
                                            'PREV'       revision just before COMMITTED
              -c [--change] ARG        : the change made in revision ARG
              -q [--quiet]             : do not print the log message
              -v [--verbose]           : also print all affected paths
              -g [--use-merge-history] : use/display additional information from merge
                                         history
              --targets ARG            : pass contents of file ARG as additional args
              --stop-on-copy           : do not cross copies while traversing history
              --incremental            : give output suitable for concatenation
              --xml                    : output in XML
              -l [--limit] ARG         : maximum number of log entries
              --with-all-revprops      : retrieve all revision properties
              --with-no-revprops       : retrieve no revision properties
              --with-revprop ARG       : retrieve revision property ARG
              --depth ARG              : limit operation by depth ARG ('empty', 'files',
                                         'immediates', or 'infinity')
              --diff                   : produce diff output
              --diff-cmd ARG           : use ARG as diff command
              --internal-diff          : override diff-cmd specified in config file
              -x [--extensions] ARG    : Specify differencing options for external diff or
                                         internal diff or blame. Default: '-u'. Options are
                                         separated by spaces. Internal diff and blame take:
                                           -u, --unified: Show 3 lines of unified context
                                           -b, --ignore-space-change: Ignore changes in
                                             amount of white space
                                           -w, --ignore-all-space: Ignore all white space
                                           --ignore-eol-style: Ignore changes in EOL style
                                           -U ARG, --context ARG: Show ARG lines of context
                                           -p, --show-c-function: Show C function name
              --search ARG             : use ARG as search pattern (glob syntax)
              --search-and ARG         : combine ARG with the previous search pattern
            """

        options = {}
        flags = []
        arguments = []

        if path is not None:
            if type(target) == str:
                arguments.append(target)
            else:
                arguments += target
        if revision is not None:
            options['revision'] = revision
        if change is not None:
            options['change'] = change
        if quiet:
            flags.append('quiet')
        if verbose:
            flags.append('verbose')
        if use_merge_history:
            flags.append('use-merge-history')
        if targets is not None:
            options['targets'] = targets
        if stop_on_copy:
            flags.append('stop-on-copy')
        if incremental:
            flags.append('incremental')
        if xml:
            flags.append('xml') 
        if limit is not None:
            options['limit'] = str(limit)
        if all_props:
            flags.append('with-all-revprops')
        if no_revprops:
            flags.append('with-no-revprops') 
        if revprop is not None:
            options['with-revprop'] = revprop
        if depth is not None:
            options['depth'] = depth
        if diff:
            flags.append('diff')
        if diff_cmd is not None:
            options['diff_cmd'] = diff_cmd
        if internal_diff:
            flags.append('internal-diff')
        if extension is not None:
            options['extensions'] = extension
        if search is not None:
            options['search'] = search
        if search_and is not None:
            options['search-and'] = search_and
        if cwd is None:
            cwd = self.cwd
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('log', *arguments, flags=flags,
            cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            return out, errs

    def info(self, target=None, revision=None, recursive=False,
        depth=None, targets=None, incremental=False, xml=False,
        changelist=None, include_externals=False, show_item=None,
        no_newline=False, cwd=None, *args, **kwargs):
        """Display information about a local or remote item."""
        options = {}
        flags = []
        arguments = []

        if target is not None:
            if type(target) == str:
                arguments.append(target)
            else:
                arguments += target
        if revision is not None:
            options['r'] = revision
        if recursive:
            flags.append('R')
        if depth is not None:
            options['depth'] = depth
        if targets is not None:
            options['targets'] = targets
        if incremental:
            flags.append('incremental')
        if xml is not None:
            flags.append('xml')
        if changelist is not None:
            options['changelist'] = changelist
        if include_externals:
            flags.append('include-externals')
        if show_item is not None:
            options['show-item'] = show_item
        if no_newline:
            flags.append('no-newline')
        if cwd is None:
            cwd = self.cwd
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('info', *arguments, flags=flags,
            cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            return out, errs

    def checkout(self, url, path=None, revision=None, quiet=False, non_recursive=False, depth=None, force=False, ignore_externals=False, cwd=None, *args, **kwargs):
        options = {}
        flags = []
        arguments = []

        if type(url) == str:
            arguments.append(url)
        else:
            arguments += url
        if path is not None:
            arguments.append(path)
        if revision:
          options['revision'] = revision
        if quiet:
          flags.append('quiet')
        if non_recursive:
          flags.append('non-recursive')
        if depth:
          options['depth'] = depth
        if force:
          flags.append('force')
        if ignore_externals:
          flags.append('ignore-externals')
        if cwd is None:
            cwd = self.cwd
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('checkout', *arguments, flags=flags,
            cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            return out, errs