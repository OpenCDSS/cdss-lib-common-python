# NoticeStart
#
# CDSS Common Java Library
# CDSS Common Java Library is a part of Colorado's Decision Support Systems (CDSS)
# Copyright (C) 1994-2019 Colorado Department of Natural Resources
#
# CDSS Common Java Library is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     CDSS Common Java Library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with CDSS Common Java Library.  If not, see <https://www.gnu.org/licenses/>.
#
# NoticeEnd

import logging
import os
import sys
import traceback


class IOUtil:
    # Flags use to indicate the vendor
    SUN = 1
    MICROSOFT = 2
    UNKNOWN = 3

    # String to use to indicate a file header revision line.
    _HEADER_REVISION_STRING = "HeaderRevision"
    # String used to indicate comments in files (unless otherwise indicated)
    _UNIVERSAL_COMMENT_STRING = "#"
    # Command-line arguments, guaranteed to be non-null but may be empty
    _argv = []
    # Program command file
    _command_file = ""
    # Program command list
    _command_list = None
    # Host (computer) running the program.
    _host = ""
    # Program name, as it should appear in the title bars, Help, About, etc.
    _progname = ""
    # Program version, typically "XX.XX.XX" or "XX.XX.XX beta".
    _progver = ""
    # Program user.
    _user = ""
    # Indicates weather a test run (not used much anymore) - can be used for experimental
    # features that are buried in the code base.
    _testing = False
    # Program working directory, which is virtual and used to create absolute paths to files.
    # This is needed because the application cannot change the current working directory due to
    # security checks.
    _working_dir = ""
    # Indicates whether global data are initialized.
    _initialized = False
    # Indicate whether the program is running as an applet.
    _is_applet = False
    # Indicates whether the program is running in batch (non-interactive) or interactive GUI/shell.
    _is_batch = False
    # A property list manager that can be used globally in the application.
    _prop_list_manager = None
    _runningApplet = False
    # Home directory for the application, typically the installation location
    # (e.g., C:\Program Files\Company\AppName).
    _homeDir = None

    def __init(self):
        pass

    @staticmethod
    def setProgramArguments(args):
        """
        Set the program arguments. This is generally only called from low-level code
        (normally just need to call setProgramData(). A copy is saved.
        :param args: Program arguments.
        """
        # Get globals
        IOUtil._argv

        #if not _initialized:
        #   self.initialize()
        for arg in args:
            IOUtil._argv.append(arg)

    @staticmethod
    def getPathUsingWorkingDir(path):
        """
        Return a path considering the working directory set by
        setProgramWorkingDir().  The following rules are used:
        <ul>
        <li>	If the path is null or empty, return the path.</li>
        <li>	If the path is an absolute path (starts with / or \ or has : as the
            second character; or starts with http:, ftp:, file:), it is returned as is.</li>
        <li>	If the path is a relative path and the working directory is ".", the path is returned.</li>
        <li>	If the path is a relative path and the working directory is not ".",
            the path is appended to the current working directory (separated with
            / or \ as appropriate) and returned.</li>
        </ul>
        :param path: Path to use.
        :return: a path considering the working directory
        """
        routine = "IOUtil.getPathUsingWorkingDir"
        logger = logging.getLogger("StateMod")
        if path is None or len(path) == 0:
            return path
        # Check for URL...
        bool = path.startswith("http:")
        if (path.startswith("http:")) or (path.startswith("ftp:")) or (path.startswith("file:")):
            return path
        if sys.platform.startswith("linux2"):
            if path[0] == '/':
                return path
            if _working_dir == "" or _working_dir == ".":
                return path
            else:
                fullPath = path
                try:
                    fullPath = os.path.realpath(_working_dir + "/" + path)
                except Exception as e:
                    logger.warning(e)
                    traceback.print_exc()
                return fullPath
        else:
            if path.startswith("\\\\"):
                # UNC Path
                return path
            if path[0] == "\\" or len(path) >= 2 or path[1] == ":":
                return path
            if _working_dir == "" or _working_dir == ".":
                return path
            else:
                fullPath = path
                try:
                    fullPath = os.path.realpath(_working_dir + "\\" + path)
                except Exception as e:
                    logger.warning(e)
                    traceback.print_exc()
                return fullPath

    @staticmethod
    def setProgramData(progname, progver, args):
        """
        Set the program main data, which can be used later for GUI labels, etc. This
        is generally called from the main() or init() function of an application (or
        from application base classes.)
        :param progname: The program name.
        :param progver: The program version.
        :param args: The program command-line arguments (ignored if an Applet).
        """
        #if not self._initialized:
        #    self.initialize()
        IOUtil.setProgramName(progname)
        IOUtil.setProgramVersion(progver)
        IOUtil.setProgramArguments(args)

    @staticmethod
    def setProgramName(progname):
        """
        Set the program name.
        :param progname: The program name.
        """
        # Get globals
        global _progname

        #if not self._initialized:
        #    self.initialize()
        if progname:
            _progname = progname

    @staticmethod
    def setProgramVersion(progver):
        """
        Set the program version.
        :param progver: The program version.
        """
        # Get globals
        global _progver

        #if not self._initialized:
        #   self.initialize()
        if progver:
            _progver = progver

    @staticmethod
    def setProgramWorkingDir(working_dir):
        # Get globals
        global _working_dir

        # if not self._initialized
        # self.initialize()
        if working_dir:
            working_dir = working_dir.strip()
            if working_dir.endswith(os.path.sep):
                working_dir = working_dir.substring(0, (working_dir.length() - 1))

        # For windows machines:
        if os.sep == "\\":
            # on dos
            if working_dir.startswith("\\\\"):
                # UNC drive -- leave as
                pass
            elif working_dir[1] != ':':
                # working_dir does not start with a drive letter. Get the drive letter
                # of the current working_dir and use it instead. Since dir is initialized
                # to the java working_dir when IOUTil is first used, _working_dir will
                # always have a drive letter for windows machines.
                drive = _working_dir[0]
                working_dir = drive + ":" + working_dir

        _working_dir = working_dir