import os
import subprocess
from typing import Dict, List, Optional, Union, Tuple

from codeminer_tools.clients.commandline import CommandLineClient


class SVNException(Exception):
    pass


class SVNClient(CommandLineClient):

    def __init__(self, binary='svn', cwd=None, username=None, password=None):
        self.cwd = cwd
        self.name = 'SVN'
        self.username = username
        self.password = password
        env = os.environ.copy()
        super().__init__(binary, env=env)

    def cat(
            self,
            target,
            revision=None,
            ignore_keywords=False,
            cwd=None,
            *args,
            **kwargs):
        """Output the content of specified files or URLs."""
        options = {}
        flags = []
        arguments = []

        if isinstance(target, str):
            arguments.append(target)
        else:
            arguments += target
        if revision is not None:
            options['r'] = revision
        if ignore_keywords:
            flags.append('ignore-keywords')
        if cwd is None:
            cwd = self.cwd
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
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

    def log(
            self,
            path=None,
            revision=None,
            change=None,
            quiet=False,
            verbose=False,
            use_merge_history=False,
            targets=None,
            stop_on_copy=False,
            incremental=False,
            xml=False,
            limit=None,
            all_props=False,
            no_revprops=False,
            revprop=None,
            depth=None,
            diff=False,
            diff_cmd=None,
            internal_diff=False,
            extension=None,
            search=None,
            search_and=None,
            cwd=None,
            streaming=False,
            *args,
            **kwargs):
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
            if isinstance(target, str):
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
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('log', *arguments, flags=flags,
                                     cwd=cwd, **options)

        if streaming:
            return result.stdout, result.stderr
        else:
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
            if isinstance(target, str):
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
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
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

    def checkout(
            self,
            url,
            path=None,
            revision=None,
            quiet=False,
            non_recursive=False,
            depth=None,
            force=False,
            ignore_externals=False,
            cwd=None,
            *args,
            **kwargs):
        options = {}
        flags = []
        arguments = []

        if isinstance(url, str):
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
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
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

    def proplist(
            self,
            path=None,
            verbose=True,
            recursive=False,
            depth=None,
            revision=None,
            quiet=True,
            revprop=False,
            xml=True,
            changelist=None,
            showinherited=False,
            cwd=None,
            *args,
            **kwargs):
        options = {}
        flags = []
        arguments = []

        if path is not None:
            if isinstance(path, str):
                arguments.append(path)
            else:
                arguments += path
        if revision is not None:
            options['revision'] = revision
        if recursive:
            flags.append('recursive')
        if verbose:
            flags.append('verbose')
        if quiet:
            flags.append('quiet')
        if depth is not None:
            options['depth'] = depth
        if revprop:
            flags.append('revprop')
        if xml:
            flags.append('xml')
        if changelist is not None:
            options['changelist'] = changelist
        if showinherited:
            flags.append('show-inherited-props')
        if cwd is None:
            cwd = self.cwd
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('proplist', *arguments, flags=flags,
                                     cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            print(out, errs)
            return out, errs

    def list(self,
        path=None,
        revision=None,
        verbose=False,
        recursive=True,
        depth=None,
        incremental=False,
        xml=True,
        include_externals=False,
        cwd=None):

        options = {}
        flags = []
        arguments = []

        if path is not None:
            if isinstance(path, str):
                arguments.append(path)
            else:
                arguments += path
        if revision is not None:
            options['revision'] = revision
        if recursive:
            flags.append('recursive')
        if verbose:
            flags.append('verbose')
        if depth is not None:
            options['depth'] = depth
        if incremental:
            flags.append('incremental')
        if xml:
            flags.append('xml')
        if include_externals:
            flags.append('include-externals')
        if cwd is None:
            cwd = self.cwd
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('list', *arguments, flags=flags,
                                     cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            print(out, errs)
            return out, errs

    def commit(self,
            message = "",
            path = None,
            quiet = False,
            depth = None,
            targets = None,
            no_unlock = False,
            force_log = False,
            encoding = None,
            with_revprop = None,
            changelist = None,
            keep_changelists = False,
            include_externals = False,
            cwd = None,
            *args, **kwargs):

        """
        commit (ci): Send changes from your working copy to the repository.
        usage: commit [PATH...]

          A log message must be provided, but it can be empty.  If it is not
          given by a --message or --file option, an editor will be started.
          If any targets are (or contain) locked items, those will be
          unlocked after a successful commit.

          If --include-externals is given, also commit file and directory
          externals reached by recursion. Do not commit externals with a
          fixed revision.

        Valid options:
          -q [--quiet]             : print nothing, or only summary information
          -N [--non-recursive]     : obsolete; try --depth=files or --depth=immediates
          --depth ARG              : limit operation by depth ARG ('empty', 'files',
                                     'immediates', or 'infinity')
          --targets ARG            : pass contents of file ARG as additional args
          --no-unlock              : don't unlock the targets
          -m [--message] ARG       : specify log message ARG
          -F [--file] ARG          : read log message from file ARG
          --force-log              : force validity of log message source
          --editor-cmd ARG         : use ARG as external editor
          --encoding ARG           : treat value as being in charset encoding ARG
          --with-revprop ARG       : set revision property ARG in new revision
                                     using the name[=value] format
          --changelist [--cl] ARG  : operate only on members of changelist ARG
          --keep-changelists       : don't delete changelists after commit
          --include-externals      : also operate on externals defined by
                                     svn:externals properties

        Global options:
          --username ARG           : specify a username ARG
          --password ARG           : specify a password ARG (caution: on many operating
                                     systems, other users will be able to see this)
          --no-auth-cache          : do not cache authentication tokens
          --non-interactive        : do no interactive prompting (default is to prompt
                                     only if standard input is a terminal device)
          --force-interactive      : do interactive prompting even if standard input
                                     is not a terminal device
          --trust-server-cert      : deprecated; same as
                                     --trust-server-cert-failures=unknown-ca
          --trust-server-cert-failures ARG : with --non-interactive, accept SSL server
                                     certificates with failures; ARG is comma-separated
                                     list of 'unknown-ca' (Unknown Authority),
                                     'cn-mismatch' (Hostname mismatch), 'expired'
                                     (Expired certificate), 'not-yet-valid' (Not yet
                                     valid certificate) and 'other' (all other not
                                     separately classified certificate errors).
          --config-dir ARG         : read user configuration files from directory ARG
          --config-option ARG      : set user configuration option in the format:
                                         FILE:SECTION:OPTION=[VALUE]
                                     For example:
                                         servers:global:http-library=serf"""

        options = {}
        flags = []
        arguments = []

        options['message'] = message
        if path is None:
            path = self.cwd
        if quiet is not None:
            flags.append('quiet')
        if depth is not None:
            options['depth'] = depth
        if targets is not None:
            options['Targets'] = targets
        if no_unlock:
            flags.append('no-unlock')
        if force_log:
            flags.append('force-log')
        if encoding is not None:
            options['encoding'] = encoding
        if with_revprop is not None:
            options['with-revprop'] = with_revprop
        if changelist is not None:
            options['changelist'] = changelist
        if keep_changelists:
            flags.append('keep-changelists')
        if include_externals:
            flags.append('include_externals')

        if cwd is None:
            cwd = self.cwd
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('commit', *arguments, flags=flags,
                                     cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            print(out, errs)
            return out, errs

    def add(self,
            path,
            cwd = None,
            *args, **kwargs):

        """
        add: Put files and directories under version control, scheduling
        them for addition to repository.  They will be added in next commit.
        usage: add PATH...

        Valid options:
          --targets ARG            : pass contents of file ARG as additional args
          -N [--non-recursive]     : obsolete; try --depth=files or --depth=immediates
          --depth ARG              : limit operation by depth ARG ('empty', 'files',
                                     'immediates', or 'infinity')
          -q [--quiet]             : print nothing, or only summary information
          --force                  : force operation to run
          --no-ignore              : disregard default and svn:ignore and
                                     svn:global-ignores property ignores
          --auto-props             : enable automatic properties
          --no-auto-props          : disable automatic properties
          --parents                : add intermediate parents

        Global options:
          --username ARG           : specify a username ARG
          --password ARG           : specify a password ARG (caution: on many operating
                                     systems, other users will be able to see this)
          --no-auth-cache          : do not cache authentication tokens
          --non-interactive        : do no interactive prompting (default is to prompt
                                     only if standard input is a terminal device)
          --force-interactive      : do interactive prompting even if standard input
                                     is not a terminal device
          --trust-server-cert      : deprecated; same as
                                     --trust-server-cert-failures=unknown-ca
          --trust-server-cert-failures ARG : with --non-interactive, accept SSL server
                                     certificates with failures; ARG is comma-separated
                                     list of 'unknown-ca' (Unknown Authority),
                                     'cn-mismatch' (Hostname mismatch), 'expired'
                                     (Expired certificate), 'not-yet-valid' (Not yet
                                     valid certificate) and 'other' (all other not
                                     separately classified certificate errors).
          --config-dir ARG         : read user configuration files from directory ARG
          --config-option ARG      : set user configuration option in the format:
                                         FILE:SECTION:OPTION=[VALUE]
                                     For example:
                                         servers:global:http-library=serf"""
        options = {}
        flags = []
        arguments = []

        arguments.append(path)
        if cwd is None:
            cwd = self.cwd
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('add', *arguments, flags=flags,
                                     cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            print(out, errs)
            return out, errs

    def update(self, cwd=None, *args, **kwargs):
        options = {}
        flags = []
        arguments = []

        if cwd is None:
            cwd = self.cwd
        if self.username is not None:
            options['username'] = self.username
        if self.password is not None:
            options['password'] = self.password
        for arg in args:
            flags.append(arg)
        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]
        result = self.run_subcommand('update', *arguments, flags=flags,
                                     cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise SVNException(errs)
        else:
            print(out, errs)
            return out, errs