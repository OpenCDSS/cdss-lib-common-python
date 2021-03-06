# NoticeStart
#
# CDSS Common Python Library
# CDSS Common Python Library is a part of Colorado's Decision Support Systems (CDSS)
# Copyright (C) 1994-2019 Colorado Department of Natural Resources
#
# CDSS Common Python Library is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     CDSS Common Python Library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with CDSS Common Python Library.  If not, see <https://www.gnu.org/licenses/>.
#
# NoticeEnd
import datetime
import getpass
import logging
import os
import platform
import sys
import traceback

from RTi.Util.IO.PropList import PropList


class IOUtil:
    # Flags use to indicate the vendor
    SUN = 1
    MICROSOFT = 2
    UNKNOWN = 3

    # String to use to indicate a file header revision line.
    HEADER_REVISION_STRING = "HeaderRevision"
    # String used to indicate comments in files (unless otherwise indicated)
    UNIVERSAL_COMMENT_STRING = "#"
    # Command-line arguments, guaranteed to be non-null but may be empty
    argv = []
    # Program command file
    command_file = ""
    # Program command list
    command_list = None
    # Host (computer) running the program.
    host = ""
    # Program name, as it should appear in the title bars, Help, About, etc.
    progname = ""
    # Program version, typically "XX.XX.XX" or "XX.XX.XX beta".
    progver = ""
    # Program user.
    user = ""
    # Indicates weather a test run (not used much anymore) - can be used for experimental
    # features that are buried in the code base.
    testing = False
    # Program working directory, which is virtual and used to create absolute paths to files.
    # This is needed because the application cannot change the current working directory due to
    # security checks.
    working_dir = ""
    # Indicates whether global data are initialized.
    initialized = False
    # Indicate whether the program is running as an applet.
    is_applet = False
    # Indicates whether the program is running in batch (non-interactive) or interactive GUI/shell.
    is_batch = False
    # A property list manager that can be used globally in the application.
    prop_list_manager = None
    # Home directory for the application, typically the installation location
    # (e.g., C:\Program Files\Company\AppName).
    home_dir = None

    def __init(self):
        pass

    @staticmethod
    def format_creator_header(comment_line_prefix, maxwidth, is_xml):
        """
        Format a header for a file, useful to understand the file creation.  The header looks like the following:
        <p>
        <pre>
        # File generated by
        # program:   demandts 2.7 (25 Jun 1995)
        # user:      sam
        # date:      Mon Jun 26 14:49:18 MDT 1995
        # host:      white
        # directory: /crdss/dmiutils/demandts/data
        # command:   ../src/demandts -d1 -w1,10 -demands -istatemod
        #            /crdss/statemod/data/white/white.ddh -icu
        #            /crdss/statemod/data/white/white.ddc -sstatemod
        #            /crdss/statemod/data/white/white.dds -eff12
        </pre>
        <p>
        @param comment_line_prefix The string to use for the start of comment lines (e.g., "#").  Use blank if the
        prefix character will be added by calling code.
        @param maxwidth The maximum length of a line of output (if whitespace is
        embedded in the header information, lines will be broken appropriately to fit
        within the specified length.
        @param is_xml Indicates whether the comments are being formatted for an XML file.
        XML files must be handled specifically because some characters that may be printed
        to the header may not be handled by the XML parser.  The opening and closing
        XML tags must be added before and after calling this method.
        @return the list of formatted header strings, guaranteed to be non-null
        """
        left_border = 12

        if not IOUtil.initialized:
            # Need to initialize the class static data
            IOUtil.initialize()

        now = datetime.datetime.now().isoformat()

        # Make sure that a valid comment string is used...

        if comment_line_prefix is None:
            comment_line_prefix = ""
        comment_line_prefix2 = ""
        if not comment_line_prefix == "":
            # Add a space to the end of the prefix so that comments are not smashed right up against
            # the line prefix - this helps with readability
            comment_line_prefix2 = comment_line_prefix + " "
        comment_len = len(comment_line_prefix2)

        # Format the comment string for the command line printout...

        comment_space0 = comment_line_prefix2
        for i in range(0, (left_border - 1)):
            comment_space0 = comment_space0 + " "
        comment_space = comment_space0

        comments = []
        comments.append(comment_line_prefix2 + "File generated by...")
        comments.append(comment_line_prefix2 + "program:      " + IOUtil.progname + " " + IOUtil.progver)
        comments.append(comment_line_prefix2 + "user:         " + IOUtil.user)
        comments.append(comment_line_prefix2 + "date:         " + now)
        comments.append(comment_line_prefix2 + "host:         " + IOUtil.host)
        comments.append(comment_line_prefix2 + "directory:    " + IOUtil.working_dir)
        comments.append(comment_line_prefix2 + "command line: " + IOUtil.progname)
        column0 = comment_len + left_border + len(IOUtil.progname) + 1
        column = column0  # Column position, starting at 1
        b = comment_line_prefix2
        if IOUtil.argv is not None:
            for i in range(0, (len(IOUtil.argv) - 1)):
                argv_len = len(IOUtil.argv[i])
                # Need 1 to account for blank between arguments...
                if (column + 1 + argv_len) > maxwidth:
                    # Put the argument on a new line...
                    comments.append(b)
                    b = ""
                    b = b + comment_line_prefix2
                    b = b + comment_space + IOUtil.argv[i]
                    column = column0 + argv_len
                else:
                    # Put the argument on the same line...
                    b = b + " " + IOUtil.argv[i]
                    column += (argv_len + 1)
        comments.append(b)
        # TODO smalers 2020-01-02 add support for command file - not needed for StateMod prototype
        #if IOUtil.command_list is not None:
        #    # Print the command list contents...
        #    if is_xml:
        #        comments.append(comment_line_prefix2)
        #    else:
        #        comments.append(comment_line_prefix2 +
        #                        "-----------------------------------------------------------------------")
        #    if fileReadable(IOUtil.command_file):
        #        comments.append(comment_line_prefix2 + "Last command file: \"" + IOUtil.command_file + "\"")
        #    comments.append(comment_line_prefix2)
        #    comments.append(comment_line_prefix2 + "Commands used to generate output:")
        #    comments.append(comment_line_prefix2)
        #    int size = IOUtil.command_list.size()
        #    for command_list_line in IOUtil.command_list:
        #        comments.append(comment_line_prefix2 + command_list_line)
        # TODO smalers 2020-01-02 add support for command file - not needed for StateMod prototype
        #elif fileReadable(IOUtil.command_file):
        #    # Print the command file contents...
        #    if is_xml:
        #        comments.append(comment_line_prefix2)
        #    else:
        #        comments.append(comment_line_prefix2 +
        #                        "-----------------------------------------------------------------------" )
        #    comments.append ( comment_line_prefix2 + "Command file \"" + IOUtil.command_file + "\":" )
        #    comments.append ( comment_line_prefix2 )
        #    error = False
        #    BufferedReader cfp = null
        #    FileReader file = null
        #    try:
        #        file = new FileReader ( IOUtil.command_file )
        #        cfp = new BufferedReader ( file )
        #    except Exception as e:
        #        error = True
        #    if  not error:
        #        while(True):
        #            try:
        #                string = cfp.readLine ()
        #                if string is None:
        #                    break
        #            except Exception:
        #                # End of file.
        #                break
        #            comments.append(comment_line_prefix2 + " " + string)
        return comments

    # TODO smalers 2020-01-02 need to enable but not used in StateMod prototype since files overwritten
    @staticmethod
    def get_file_header (old_file, comment_indicators, ignored_comment_indicators, flags):
        return None

    @staticmethod
    def get_path_using_working_dir(path):
        """
        Return a path considering the working directory set by
        set_program_working_dir().  The following rules are used:
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
        logger = logging.getLogger(__name__)
        if path is None or len(path) == 0:
            return path
        # Check for URL...
        # bool = path.startswith("http:")
        if (path.startswith("http:")) or (path.startswith("ftp:")) or (path.startswith("file:")):
            return path
        if sys.platform.startswith("linux2"):
            if path[0] == '/':
                return path
            if IOUtil.working_dir == "" or IOUtil.working_dir == ".":
                return path
            else:
                full_path = path
                try:
                    full_path = os.path.realpath(IOUtil.working_dir + "/" + path)
                except Exception as e:
                    logger.warning(e)
                    traceback.print_exc()
                return full_path
        else:
            if path.startswith("\\\\"):
                # UNC Path
                return path
            if path[0] == "\\" or len(path) >= 2 or path[1] == ":":
                return path
            if IOUtil.working_dir == "" or IOUtil.working_dir == ".":
                return path
            else:
                full_path = path
                try:
                    full_path = os.path.realpath(IOUtil.working_dir + "\\" + path)
                except Exception as e:
                    logger.warning(e)
                    traceback.print_exc()
                return full_path

    @staticmethod
    def initialize():
        """
        Initialize the global data.
        :return:  None
        """

        logger = logging.getLogger(__name__)
        logger.debug("Initializing IOUtil...")
        try:
            # A stand-alone application...
            IOUtil.command_file = ""
            IOUtil.command_list = None
            IOUtil.host = platform.node()
            IOUtil.progname = os.path.basename(sys.argv[0])
            # Need to be set by a specific application
            IOUtil.progver = "version unknown"
            IOUtil.user = getpass.getuser()
            # IOUtil.working_dir = System.getProperty ("user.dir")
            # IOUtil.home_dir = System.getProperty ("user.dir")
            IOUtil.args = sys.argv
        except Exception as e:
            # Don't do anything.  Just print a warning...
            logger.warning("Caught an exception initializing IOUtil.  Continuing.", exc_info=True)

        # Initialize the property list manager to contain an unnamed list...

        # _prop_list_manager = new PropListManager ();
        # _prop_list_manager.addList ( new PropList("", PropList.FORMAT_PROPERTIES), true );

        # Set the flag to know that the class has been initialized...

        # Make sure that global value is set, otherwise will recurse infinitely
        IOUtil.initialized = True

    @staticmethod
    def print_creator_header(ofp, comment_line_prefix, maxwidth, flag, props):
        """
        Print a header to a file.  The header looks like the following:
        <p>
        <pre>
        # File generated by
        # program:   demandts 2.7 (25 Jun 1995)
        # user:      sam
        # date:      Mon Jun 26 14:49:18 MDT 1995
        # host:      white
        # directory: /crdss/dmiutils/demandts/data
        # command:   ../src/demandts -d1 -w1,10 -demands -istatemod
        #            /crdss/statemod/data/white/white.ddh -icu
        #            /crdss/statemod/data/white/white.ddc -sstatemod
        #            /crdss/statemod/data/white/white.dds -eff12
        </pre>
        <p>
        @param ofp PrintWriter that is being written to.
        @param comment_line_prefix The string to use for the start of comment lines (e.g., "#").
        @param maxwidth The maximum length of a line of output (if whitespace is
        embedded in the header information, lines will be broken appropriately to fit
        within the specified length.
        @param flag Currently unused.
        @param props Properties used to format the header.  Currently the only
        property that is recognized is "IsXML", which can be "true" or "false".  XML
        files must be handled specifically because some characters that may be printed
        to the header may not be handled by the XML parser.  The opening and closing
        XML tags must be added before and after calling this method.
        @return 0 if successful, 1 if not.
        """
        is_xml = False
        nl = "\n"  # Use for all platforms
        # Figure out properties...
        if props is not None:
            prop_value = props.get_value("IsXML")
            if (prop_value is not None) and (prop_value.upppercase() == "TRUE"):
                is_xml = True
                # If XML, do not print multiple dashes together in the comments below.

        if ofp is None:
            logger = logging.getLogger(__name__)
            logger.warning("Output file pointer is NULL")
            return 1

        if not IOUtil.initialized:
            IOUtil.initialize()

        # Get the formatted header comments...

        comments = IOUtil.format_creator_header(comment_line_prefix, maxwidth, is_xml)

        for c in comments:
            ofp.write(c + nl)
        # ofp.flush ();
        return 0

    @staticmethod
    def process_file_headers(old_file, new_file, new_comments, comment_indicators, ignored_comment_indicators, flags):
        """
        This method should be used to process the header of a file that is going through
        revisions over time.  It can be used short of full revision control on the file.
        The old file header will be copied to the new file using special comments
        (assume # is comment):
        <p>

        <pre>
        #HeaderRevision 1
        </pre>
        <p>

        Where the number indicates the revision for the header.  The initial header will be number 0.
        @return PrintWriter for the file (it will be opened and processed so that the
        new file header consists of the old header with new comments at the top).  The
        file can then be written to.  Return null if the new file cannot be opened.
        @param old_file An existing file whose header is to be updated.
        @param new_file The name of the new file that is to contain the updated header
        (and will be pointed to by the returned PrintWriter (it can be the same as
        "old_file").  If the name of the file ends in XML then the file is assumed to
        be an XML file and the header is wrapped in <!-- --> (this may change to actual XML tags in the future).
        @param new_comments list of strings to be added as comments in the new revision (often null).
        @param comment_indicators list of strings that indicate comment lines that should be retained in the
        next revision.
        @param ignored_comment_indicators list of strings that indicate comment lines that
        can be ignored in the next revision (e.g., lines that describe the file format that only need to appear once).
        @param flags Currently unused.
        """
        # FileHeader oldheader
        oldheader = None
        # PrintWriter	ofp = null
        dl = 50
        header_last = -1
        wl = 20
        is_xml = False
        logger = logging.getLogger(__name__)
        nl = "\n"  # Use on all platforms

        # Get the old file header...

        if old_file is None:
            logger.debug("Old file is None - no old header")
            oldheader = None
        elif len(old_file) == 0:
            logger.warning("Empty old file - no old header")
            oldheader = None
        else:
            # Try to get the header...
            oldheader = IOUtil.get_file_header(old_file, comment_indicators, ignored_comment_indicators, 0)
            if oldheader is not None:
                header_last = oldheader.get_header_last()

        # Open the new output file...

        ofp = None
        try:
            if new_file is None:
                logger.warning("Trying to open null output file")
                return None
            ofp = open(new_file, "w")
            if str(new_file).upper().endswith(".XML"):
                is_xml = True
        except Exception as e:
            logger.warning("Unable to open new output file \"" + str(new_file) + "\"", exc_info=True)
            return None

        # Print the new file header.  If a comment string is not specified, use the default...

        if (comment_indicators is None) or (len(comment_indicators) == 0):
            comment = IOUtil.UNIVERSAL_COMMENT_STRING
        else:
            comment = comment_indicators[0]

        header_revision = header_last + 1
        if is_xml:
            ofp.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>" + nl)
            ofp.write("<!--" + nl)

        ofp.write(comment + IOUtil.HEADER_REVISION_STRING + " " + str(header_revision) + nl)
        ofp.write(comment + nl)

        # Now print the standard header...

        props = PropList("header")
        if is_xml:
            props.set("IsXML=true")
        IOUtil.print_creator_header(ofp, comment, 80, 0, props)

        # Now print essential comments for this revision.  These strings do not have the comment prefix...

        if new_comments is not None:
            if len(new_comments) > 0:
                if is_xml:
                    ofp.write(comment + nl)
                else:
                    ofp.write(comment + "----" + nl)
                for new_comment in new_comments:
                    ofp.write(comment + " " + new_comment + nl)

        if is_xml:
            ofp.write(comment + nl)
        else:
            ofp.write(comment + "------------------------------------------------" + nl)

        # Now print the old header.  It already has the comment character.

        if oldheader is not None:
            if len(oldheader) > 0:
                for oldheader_line in oldheader:
                    ofp.write(oldheader_line + nl)

        if is_xml:
            ofp.write("-->" + nl)
        return ofp

    @staticmethod
    def set_program_arguments(argv):
        """
        Set the program arguments. This is generally only called from low-level code
        (normally just need to call set_program_data(). A copy is saved in a new list.
        :param argv: Program arguments.
        """

        if not IOUtil.initialized:
            IOUtil.initialize()
        # Get globals
        IOUtil.argv = []
        for arg in argv:
            IOUtil.argv.append(arg)

    @staticmethod
    def set_program_data(progname, progver, args):
        """
        Set the program main data, which can be used later for GUI labels, etc. This
        is generally called from the main() or init() function of an application (or
        from application base classes.)
        :param progname: The program name.
        :param progver: The program version.
        :param args: The program command-line arguments (ignored if an Applet).
        """
        if not IOUtil.initialized:
            IOUtil.initialize()
        IOUtil.set_program_name(progname)
        IOUtil.set_program_version(progver)
        IOUtil.set_program_arguments(args)

    @staticmethod
    def set_program_name(progname):
        """
        Set the program name.
        :param progname: The program name.
        """
        if not IOUtil.initialized:
            IOUtil.initialize()
        if progname:
            IOUtil.progname = progname

    @staticmethod
    def set_program_version(progver):
        """
        Set the program version.
        :param progver: The program version.
        """
        if not IOUtil.initialized:
            IOUtil.initialize()
        if progver:
            IOUtil.progver = progver

    @staticmethod
    def set_program_working_dir(working_dir):
        if not IOUtil.initialized:
            IOUtil.initialize()
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
                drive = working_dir[0]
                working_dir = drive + ":" + working_dir

        # Set in the global data
        IOUtil.working_dir = working_dir
