import os
import subprocess
from typing import Dict, List, Optional, Union, Tuple

from codeminer.clients.commandline import CommandLineClient

class CVSException(Exception):
    pass

class CVSClient(CommandLineClient):
    def __init__(self, cvs_root=None, binary='cvs', cwd=None):
        env = CVSClient.get_env_vars()
        if cvs_root is not None:
            env['CVSROOT'] = cvs_root
        self.cwd = cwd
        super().__init__(binary, env=env)

    @classmethod
    def get_env_vars(self):
        #ftp://ftp.gnu.org/old-gnu/Manuals/cvs/html_node/cvs_144.html
        valid_variables = [
            "CVSIGNORE", "CVSWRAPPERS", "CVSREAD", "CVSROOT", "EDITOR",
            "CVSEDITOR", "PATH", "RCSBIN", "HOME", "HOMEPATH", "CVS_RSH",
            "CVS_SERVER", "CVS_PASSFILE", "CVS_PASSWORD", "CVS_CLIENT_PORT",
            "CVS_RCMD_PORT", "CVS_CLIENT_LOG", "CVS_SERVER_SLEEP",
            "CVS_IGNORE_REMOTE_ROOT", "COMSPEC", "TMPDIR", "TMP", "TEMP",
            "LOGNAME", "USER", "RCSINIT"]
        env = os.environ
        return {key : val for key, val in env.items() if key in valid_variables}

    def add(self, files : Union[List[str], str], message : str = None,
        rcs_kflag : str = None, cwd=None, *args : str, **kwargs : str) -> Tuple[str,str]:
        """Add a new file/directory to the repository

        Parameters
        ----------
        files : str or list of str
            Files to be added
        message : str, optional
            Use this "message" for the creation log
        rcs_kflag : str, optional
            Add the file with the specified kflag.
        cwd : str, optional
            Change working directory to this path before executing
            CVS comman

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command

        Raises
        ------
        CVSException
            If the cvs program returns an error code

        """
        options = {}
        flags = []
        arguments = []

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        if message is not None:
            options['m'] = '"{message}"'.format(message=message)

        if rcs_kflag is not None:
            options['k'] = rcs_kflag

        if cwd is None:
            cwd = self.cwd

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.run_subcommand('add', *arguments, flags=flags,
            cwd=cwd, **options)

        out, errs = result.communicate()
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return out, errs

    def checkout(self, path : str = None,
        reset : bool = False, no_shorten : bool = False, prune : bool = False,
        recursive : bool = False, cat : bool = False, force : bool = False,
        local_directory : bool = False, no_module : bool = False,
        stdout : bool = False, status : bool = False, revision : str = None,
        date : str = None, dir : str = None, kopt : str = None,
        merge : bool = None, cwd=None, *args : str, **kwargs : str) -> Tuple[str,str]:
        """Checkout sources for editing

        Parameters
        ----------
        reset : bool
            Reset any sticky tags/date/kopts.
        no_shorten : bool
            Don't shorten module paths if -d specified.
        prune : bool
            Prune empty directories.
        recursive : bool
            Process directories recursively.
        cat : bool
            "cat" the module database.
        force : bool
            Force a head revision match if tag/date not found.
        local_directory : bool
            Local directory only, not recursive
        no_module : bool
            Do not run module program (if any).
        stdout : bool
            Check out files to standard output (avoids stickiness).
        status : bool
            Like -c, but include module status.
        revision : str
            Check out revision or tag. (implies -P) (is sticky)
        date : str
            Check out revisions as of date. (implies -P) (is sticky)
        dir : str
            Check out into dir instead of module name.
        kopt : str
            Use RCS kopt -k option on checkout. (is sticky)
        merge : str
            Merge in changes made between current revision and rev.
        cwd : str, optional
            Change working directory to this path before executing
            CVS comman

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command

        Raises
        ------
        CVSException
            If the cvs program returns an error code

        """
        options = {}
        flags = []
        arguments = []

        if path is not None:
            arguments.append(path)

        if reset:
            flags.append('A')
        if no_shorten:
            flags.append('N')
        if prune:
            flags.append('P')
        if recursive:
            flags.append('R')
        if cat:
            flags.append('c')
        if force:
            flags.append('f')
        if local_directory:
            flags.append('l')
        if no_module:
            flags.append('n')
        if stdout:
            flags.append('p')
        if status:
            flags.append('s')

        if revision is not None:
            options['r'] = revision
        if date is not None:
            options['D'] = date
        if dir is not None:
            options['d'] = dir
        if kopt is not None:
            options['k'] = kopt
        if merge is not None:
            options['j'] = merge

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
            raise CVSException(result.stderr)
        else:
            return out, errs

    def commit(self, message : str, files : Union[List[str], str] = [],
        recursive : bool = False, local_directory : bool = False,
        force : bool = False, revision : str = None, cwd=None, 
        *args : str, **kwargs : str) -> Tuple[str,str]:
        """Check files into the repository

        Parameters
        ----------
        message : str
            Log message.
        files : str or list of str, optional
            Files to be commited, default is current working directory
        recursive : bool, optional
            Process directories recursively.
        local_directory : bool, optional
            Local directory only (not recursive).
        force: bool, optional
            Force the file to be committed; disables recursion.
        revision : str, optional
            Commit to this branch or trunk revision.

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command
        cwd : str, optional
            Change working directory to this path before executing
            CVS comman

        Raises
        ------
        CVSException
            If the cvs program returns an error code

        """
        options = {}
        flags = []
        arguments = []

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        options['m'] = '"{message}"'.format(message=message)

        if recursive:
            flags.append('R')
        if local_directory:
            flags.append('l') 
        if force:
            flags.append('f')
        if revision is not None:
            options['r'] = revision

        if cwd is None:
            cwd = self.cwd

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.run_subcommand('commit', *arguments, flags=flags,
            cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return out, errs

    def remove(self, files : Union[List[str], str] = [],
        delete : bool = False, local_directory : bool = False,
        recursive : bool = False, cwd=None, *args : str, **kwargs : str):
        """Remove an entry from the repository

        Parameters
        ----------
        files : str or list of str, optional
            Files to be commited, default is current working directory
        delete : bool, optional
            Delete the file before removing it.
        local_directory : bool, optional
            Process this directory only (not recursive).
        recursive : bool, optional
            Process directories recursively.
        cwd : str, optional
            Change working directory to this path before executing
            CVS comman

        Raises
        ------

        """
        options = {}
        flags = []
        arguments = []

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        if delete:
            flags.append('f')
        if local_directory:
            flags.append('l') 
        if recursive:
            flags.append('R')

        if cwd is None:
            cwd = self.cwd

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.run_subcommand('remove', *arguments, flags=flags,
            cwd=cwd, **options)
        out, errs = result.communicate()
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return out, errs

    def log(self, local : bool = False, list_revisions : bool = False,
        header_only : bool = False, name_only : bool = False, descriptive_only: bool = False,
        no_tags : bool = False, tags : bool = False, 
        no_header_if_revision: bool = False, revisions : Union[List[str], str] = None,
        dates : Union[List[str], str] = None, states : Union[List[str], str] = None,
        logins : Union[List[str], str] = None, files : Union[List[str], str] = [],
        xml : bool = False, cwd=None, *args, **kwargs):
        """Print out history information for files

        Parameters
        ----------
        local : bool, optional
            Local directory only, no recursion.
        list_revisions : bool, optional
            List revisions on the default branch.
        header_only : bool, optional
            Only print header.
        name_only : bool, optional
            Only print name of RCS file.
        descriptive_only: bool, optional
            Only print header and descriptive text.
        no_tags : bool, optional
            Do not list tags.
        tags : bool, optional
            List tags (default).
        no_header_if_revision: bool, optional
            Do not print name/header if no revisions selected.  -d, -r,
            -s, & -w have little effect in conjunction with -b, -h, -R, and
            -t without this option.
        revisions : str or list of str, optional
            A comma-separated list of revisions to print:
        dates : str or list of str, optional
            A semicolon-separated list of dates
        states : str or list of str, optional
            Only list revisions with specified states.
        logins : str , optional
            Only list revisions checked in by specified logins.
        files : str or list of str, optional
            Files to log        
        xml : bool, optional
            Return XML representation of the log. This
            is not a native operation and relies on
            cvs2cl perl script
        cwd : str, optional
            Change working directory to this path before executing
            CVS comman

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command

        Raises
        ------
        CVSException
            If the cvs program returns an error code"""

        options = {}
        flags = []
        arguments = []

        if local:
            flags.append('l')
        if list_revisions:
            flags.append('b')
        if header_only:
            flags.append('h')
        if name_only:
            flags.append('R')
        if descriptive_only:
            flags.append('t')
        if no_tags:
            flags.append('N')
        if tags:
            flags.append('n')
        if no_header_if_revision:
            flags.append('S')
        if revisions is not None:
            # The 'r' option is strange because there's no space. Treat
            # as an argument.. this just means it will go last in the options
            # list.
            if type(revisions) == str:
                arguments.append('-r{revisions}'.format(revisions=revisions))
            else:
                arguments.append('-r{revisions}'.format(revisions=','.join(revisions)))
        if dates is not None:
            if type(dates) == str:
                options['d'] = dates
            else:
                options['d'] = ';'.join(dates)
        if states is not None:
            if type(states) == str:
                options['s'] = states
            else:
                options['s'] = ','.join(states)
        if logins is not None:
            # The 'w' option is also strange with no space. Again, treate
            # as an argument
            arguments.append('-w{logins}'.format(logins=logins)) 

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        if cwd is None:
            cwd = self.cwd

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        log_process = self.run_subcommand('log', *arguments, flags=flags,
            cwd=self.cwd, **options)

        if xml:
            cvs2cl = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '..', 'tools', 'cvs2cl.pl')
            xml_process = subprocess.Popen(['perl', cvs2cl, '--stdin', '--stdout', 
            '--xml', '--noxmlns', '--lines-modified', '--tags', '--follow'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=log_process.stdout,
            cwd=cwd, env=self.env)

            # Close stdout handle for log_process since it will be used by cvs2cl
            log_process.stdout.close()
            # Get stderr/stdout from cvs2cl
            out, errs = xml_process.communicate()
            # Close out log_process (communicate() ensured it was done)
            # We only need this to get the return code populated
            log_process.wait()
            # Read and close the stderr which we had left open on log_process
            cvs_error = log_process.stderr.read()
            log_process.stderr.close()
            if log_process.returncode != 0:
                raise CVSException(errs)
            return out, errs
        else:
            out, errs = log_process.communicate()
            if log_process.returncode != 0:
                raise CVSException(errs)

        return out, errs
