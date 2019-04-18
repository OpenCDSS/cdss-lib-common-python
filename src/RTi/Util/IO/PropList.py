# PropList - use to hold a list of properties

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

#  ----------------------------------------------------------------------------
#  PropList - use to hold a list of properties
#  ----------------------------------------------------------------------------
#  Copyright:  See the COPYRIGHT file.
#  ----------------------------------------------------------------------------
#  History:
#
#  Sep 1997?	Steven A. Malers,	Initial version.
# 		Riverside Technology,
# 		inc.
#  02 Feb 1998	SAM, RTi		Get all of the Prop* classes working
# 					together.
#  24 Feb 1998	SAM, RTi		Add the javadoc comments.
#  02 May 1998	SAM, RTi		Add the getValid function.
#  13 Apr 1999	SAM, RTi		Add finalize.
#  17 May 1999	SAM, RTi		Add setUsingObject to avoid overload
# 					conflict.
#  06 Nov 2000	CEN, RTi		Added read/writePersistent
#   					implementation similar to C++ implem.
# 					Included adding clear
#  14 Jan 2001	SAM, RTi		Overload set to take a Prop.
#  13 Feb 2001	SAM, RTi		Change readPersistent() and associated
# 					methods return void as per C++.  Fix
# 					bug where readPersistent() was not
# 					handling whitespace correctly.  Add
# 					javadoc to readPersistent().  Add
# 					getValue(key,inst), getProp(key,inst),
# 					findProp(key,inst) to store multiple
# 					instances of properties with the same
# 					key.
#  27 Apr 2001	SAM, RTi		Change all debug levels to 100.
#  10 May 2001	SAM, RTi		Testing to get working with embedded
# 					variables like ${...}.  This involves
# 					passing the persistent format to the
# 					Prop.getValue() method so that it can
# 					decide whether to expand the contents.
# 					Move routine names into messages
# 					themselves to limit overhead.  Set
# 					unused variables to null to optimize
# 					memory management.  Change initial
# 					list size from 100 to 20.
#  14 May 2001	SAM, RTi		Change so that when parsing properties
# 					the = is the only delimiter so that
# 					quotes around arguments with spaces
# 					are not needed.
#  2001-11-08	SAM, RTi		Synchronize with UNIX.  Changes from
# 					2001-05-14... Add a boolean flag
# 					_literal_quotes to keep the quotes in
# 					the PropList.  This is useful where
# 					commands are saved in PropLists.
# 					Change so when reading a persistent
# 					file, the file can be a regular file or
# 					a URL.
#  2002-01-20	SAM, RTi		Fix one case where equals() was being
# 					used instead of equalsIgnoreCase() when
# 					finding property names.
#  2002-02-03	SAM, RTi		Add setHowSet() and getHowSet() to track
# 					how a property is set.  Remove the
# 					*_CONFIG static parameters because
# 					similar values are found in Prop.  The
# 					values were never used.  Change set
# 					methods to be void instead of having a
# 					return type.  The return value is never
# 					used.  Fix bug where setValue() was
# 					replacing the Prop in the PropList with
# 					the given object (rather than the value
# 					in the Prop) - not sure if this code
# 					was ever getting called!  Change
# 					readPersistent() and writePersistent()
# 					to throw an IOException if there is an
# 					error.  Add getPropsMatchingRegExp(),
# 					which is used by TSProduct to help write
# 					properties.
#  2002-07-01	SAM, RTi		Add elementAt() to get a property at
# 					a position.
#  2002-12-24	SAM, RTi		Support /* */ comments in Java PropList.
#  2003-03-27	SAM, RTi		Fix bugs in setContents() and setValue()
# 					methods where when a match was found
# 					the code did not return, resulting in
# 					a new duplicate property also being
# 					appended.
#  2003-10-27	J. Thomas Sapienza, RTi	Added a very basic copy constructor.
# 					In the future should implement
# 					clone() and a copy constructor that
# 					can handle Props that have data objects.
#  2003-11-11	JTS, RTi		* Added getPropCount().
# 					* Added the methods with the replace
# 					  parameter.
# 					* Added unSetAll().
#  2004-02-03	SAM, RTi		* Add parse().
#  2004-07-15	JTS, RTi		Added sortList().
#  2004-11-29	JTS, RTi		Added getList().
#  2005-04-29	SAM, RTi		* Overload the parse method to take a
# 					  "how set" value.
#  2005-06-09	JTS, RTi		Warnings in readPersistent() are now
# 					printed at level 2.
#  2005-12-06	JTS, RTi		Added validatePropNames().
#  2007-03-02	SAM, RTi		Update setUsingObject() to allow null.
#  ----------------------------------------------------------------------------
#  EndHeader

import logging

from RTi.Util.IO.Prop import Prop


class PropList(object):
    """
    This class manages a list of Prop instances, effectively creating a properties
    list that can be used to store properties for an object, etc.  This class
    contains a list of Prop instances and methods to interface with the data (set
    properties, look up properties, etc.).  Property lists are typically used to
    store and pass variable length, variable content data, as opposed to fixed
    parameters.  Often, only a PropList needs to be used (and Prop, PropListManager)
    can be avoided.  Note that the standard Java Hashtable can also be used for
    properties but does not have some of the features of PropList.
    <p>

    Often, a PropList will contain only simple string properties.  However, it is
    possible to store any Object in a PropList, keyed by a name.  Internally, each
    property has a String key, a String value, an Object contents, and an integer
    flag indicating how the property was set (from file, by user, etc).  For simple
    strings, the value and contents are the same.  For other Objects, the contents
    evaluates to toString(); however, applications will often use the contents
    directly by casting after retrieving from the PropList.
    <p>

    An additional feature of PropList is the use of variables in strings.  If a
    PropList is created using a persistent format of FORMAT_NWSRFS or
    FORMAT_MAKEFILE, variables are encoded using $(varname).  If FORMAT_PROPERTIES,
    the notation is ${varname}.  For example, two properties may be defined as:
    <p>
    <pre>
    prop1 = "Hello World"
    title = "My name is ${prop1}
    </pre>

    The default persistent format does not support this behavior, but using the
    formats described above automatically supports this behavior.  Additionally,
    the IOUtil property methods (setProp(), getProp*()) are used to check for
    properties.  Therefore, you can use IOUtil to define properties one place in an
    application and use the properties in a different part of the application.
    <p>

    Each of the special formats will also make an external call to a program to fill
    in information if the following syntax is used:
    <p>
    <pre>
    prop1 = "Current time: `date`"
    </pre>

    The back-quotes cause a system call using ProcessManager and the output is
    placed in the resulting variable.
    <p>
    If the properties are edited at run-time (e.g., by a graphical user interface),
    it is common to use the "how set" flag to control how the properties file is
    written.  For example:
    <pre>
    PropList props = new PropList ( "" );
    props.setPersistentName ( "somefile" );
    // The following uses a "how set" value of Prop.SET_FROM_PERSISTENT.
    props.readPersistent ( "somefile" );
    // Next, the application may check the file properties and assign some internal
    // defaults to have a full set of properties...
    props.setHowSet ( Prop.SET_AS_RUNTIME_DEFAULT );
    // When a user interface is displayed...
    props.setHowSet ( Prop.SET_AT_RUNTIME_BY_USER );
    // ...User interaction...
    props.setHowSet ( Prop.SET_UNKNOWN );
    // Then there is usually custom code to write a specific PropList to a file.
    // Only properties that were originally read or have been modified by the user
    // may be written (internal defaults often make the property list verbose, but
    // may be still desirable).
    </pre>
    @see Prop
    @see PropListManager
    @see ProcessManager
    """

    # Indicates that the configuration file format is unknown.
    FORMAT_UNKNOWN = 0

    # Indicates that the configuration file format is that used by Makefiles.
    FORMAT_MAKEFILE = 1

    # Indicates that the configuration file format is that used by NWSRFS
    # configuration files (apps_defaults).  A : is used instead of the = for assignment.
    FORMAT_NWSRFS = 2

    # Indicates that configuration information is being stored in a custom database.
    FORMAT_CUSTOM_DB = 3

    # Indicates that configuration information is being stored in standard RTi properties file.
    FORMAT_PROPERTIES = 4

    def __init__(self, listName=None, persistentName=None, persistentFormat=None):
        # Name of this PropList.
        self.__listName = ""

        # List of Prop.
        self.__list = []

        # File to save in.
        self.__persistentName = ""

        # Format of file to read
        self.__persistentFormat = int()

        # Last line read from the property file.
        self.__lastLineNumberRead = int()

        # Indicates if quotes should be treated literally when setting Prop values.
        self.__literalQuotes = True

        # The "how set" value to use when properties are being set
        self.__howSet = Prop.SET_UNKNOWN

        if listName is not None:
            if persistentFormat is not None:
                if persistentName is not None:
                    # Construct using a list name, a configuration file name,
                    # and a configuration file format type.  The file is not actually read (call readPersistent()
                    # to do so).
                    # PropList(listName, persistentName, persistentFormat)
                    self.initialize(listName, persistentName, persistentFormat)
                else:
                    # Construct using a list name, a configuration file name,
                    # and a configuration file format type.  The file is not actually read (call readPersistent()
                    # to do so).
                    # PropList(listName, persistentFormat)
                    self.initialize(listName, "", persistentFormat)
            else:
                # Construct given the name of the list (the list name should be unique if
                # multiple lists are being used in a PropListManager.  The persistent format defaults to
                # FORMAT_UNKNOWN.
                # PropList(listName)
                self.initialize(listName, "", PropList.FORMAT_UNKNOWN)

    def append(self, key, contents, isLiteral):
        """
        Append a property to the list using a string key.
        :param key: String key for the property
        :param contents: Contents for the property
        :param isLiteral:
        """
        prop = Prop(self.__howSet, None, key, contents, str(contents))
        prop.setIsLiteral(isLiteral)
        self.__list.append(prop)

    def clear(self):
        """
        Remove all items from the PropList
        """
        self.__list.clear()

    def elementAt(self, pos):
        """
        Return the Prop instance at the requested position.  Use size() to determine the size of the PropList.
        :param pos: the position of the property to return (0+).
        :return: the Prop at the specified position.
        """
        return self.__list[pos]

    def findProp(self, key):
        """
        Find a property in the list.
        :param key: The string key used to look up the property.
        """
        for i, prop_i in enumerate(self.__list):
            propKey = prop_i.getKey()
            if key.upper() == propKey.upper():
                # Have a match. Return the position...
                return i
        return -1

    def getList(self):
        """
        Returns the list of Props.
        :return: the list of props.
        """
        return self.__list

    def getPersistentFormat(self):
        """
        Return the format of the property list file.
        :return: The format of the property list file.
        """
        return self.__persistentFormat

    def getValue(self, key):
        """
        The string value of the property corresponding to the string key, or null if not found.
        :param key: The string key used to look up the property
        """
        pos = self.findProp(key)
        if pos >= 0:
            # We have a match. Get the value...
            return self.__list[pos].getValue(self)
        return None

    def initialize(self, listName, persistentName, persistentFormat):
        """
        Initialize the object.
        :param listName: Name for the PropList.
        :param persistentName: Persistent name for the PropList (used only when reading from a file).
        :param persistentFormat: Format for properties file.
        """
        if listName is None:
            self.__listName = ""
        else:
            self.__listName = listName
        if persistentName is None:
            self.__persistentName = ""
        else:
            self.__persistentName = persistentName
        self.__persistentFormat = persistentFormat
        self.__list = []
        self.__lastLineNumberRead = 0

    def readPersistent(self, append=None, includeLiterals=None):
        """
        /**
        Read a property list from a persistent source.  The "how_set" flag for each
        property is set to Prop.SET_FROM_PERSISTENT.  The file can have the format:
        <pre>
        # COMMENT
        # Simple setting:
        variable = value

        \/\*
        Multi-line
        comment - start and end of comments must be in first characters of line.
        \*\/

        # Use section headings:
        [MyProps]
        prop1 = value

        # For the above retrieve with MyProps.prop1

        # Lines can have continuation if \ is at the end:
        variable = xxxx \
        yyy

        # Properties with whitespace can be enclosed in " " for clarity (or not):
        variable = "string with spaces"

        # Variables ${var} will be expanded at query time to compare to
        # IOUtil.getPropValue() and also other defined properties:
        variable = ${var}

        # Text defined inside 'hard quotes' will not be expanded and will be literal:
        variable = 'hello ${world}'
        variable = 'hello `date`'

        # Text defined inside "soft quotes" will be expanded:
        variable = "hello ${world}"
        variable = "hello `date`"

        # Duplicate variables will be read in.  However, to lookup, use getPropValue()
        </pre>
        :param append: Append to current property list (true) or clear out current list (false).
        :param includeLiterals: if true, comments and other non-property lines will be included as literals
        in the property list using key "Literal1", "Literal2", etc.  This is useful if reading a property file,
        updating its values, and then writing out again, trying to retain the original comments.
        """
        logger = logging.getLogger("StateMod")

        if append is None:
            append = True
        else:
            append = True
            includeLiterals = False

        routine = "PropList.readPersistent"

        prefix = ""
        continuation = False
        lineSave = None
        inComment = False
        literalCount = 0

        if not append:
            self.clear()

        howSetPrev = self.__howSet
        self.__howSet = Prop.SET_FROM_PERSISTENT
        try:
            self.__lastLineNumberRead = 0
            length = 0
            with open(self.__persistentName) as f:
                while True:
                    line = f.readline()
                    line.strip()
                    self.__lastLineNumberRead += 1
                    if continuation:
                        # Take this line and add it to the previous. Add a space to separate tokens.
                        # Should not normally be a comment.
                        line = str(lineSave) + " " + line
                    # Handle line continuation with \ at end...
                    if line.endswith("\\"):
                        continuation = True
                        # Add a space at the end because when continuing lines the next line
                        # likely has separation tokens.
                        lineSave = line[0:len(line)-1]
                        continue
                    continuation = False
                    lineSave = None
                    if len(line) > 0:
                        if line[0] == '#':
                            # Comment line
                            if includeLiterals:
                                literalCount += 1
                                self.append("Literal" + str(literalCount), line, True)
                            continue
                        elif (line.startswith("<#") or line.startswith("</#")):
                            # Freemarker template syntax
                            continue
                    if line.find('#') != -1:
                        idx = line.index('#')
                        line = line[0:idx]
                    if inComment and line.startswith("*/"):
                        inComment = False
                        # For now the end of comment must be at the start of the line so
                        # ignore the rest of the line...
                        if includeLiterals:
                            literalCount += 1
                            self.append("Literal" + str(literalCount), line, True)
                        continue
                    if ((not inComment) and line.startswith("/*")):
                        inComment = True
                        # For now the end of comment must be at the start of the line so ignore the rest of the
                        # line...
                        if includeLiterals:
                            literalCount += 1
                            self.append("Literal" + str(literalCount), line, True)
                        continue
                    if inComment:
                        # Did not detect an end to the comment above so skip the line...
                        if includeLiterals:
                            literalCount += 1
                            self.append("Literal" + str(literalCount), line, True)
                        continue
                    if len(line) == 0:
                        if includeLiterals:
                            literalCount += 1
                            self.append("Literal" + str(literalCount), line, True)
                    if line[0] == '[':
                        # Block indicator - contents of [] will be prepended to property names
                        if line.index("${") >= 0:
                            # Likely a freemarker template syntax so skip
                            continue
                        if line.index(']') == -1:
                            logger.warning("Missing ] on line " + str(self.__lastLineNumberRead) + " of " +
                                           self.__persistentName)
                            continue
                        prefix = line[1: line.index(']')] + "."
                        if includeLiterals:
                            literalCount += 1
                            self.append("Literal" + str(literalCount), line, True)
                        continue
                    pos = line.index('=')
                    if pos < 0:
                        logger.warning("Missing equal sign on line " + str(self.__lastLineNumberRead) + " of " +
                                       self.__persistentName + " (" + line + ")")
                        if includeLiterals:
                            literalCount += 1
                            self.append("Literal" + str(literalCount), line, True)
                        continue
                    v = []
                    v.append(line[0:pos])
                    v.append(line[pos+1:])

                    if len(v) == 2:
                        name = prefix + v[0].strip()
                        value = v[1].strip()
                        length = len(value)
                        if length > 1 and (value[0] == '"' or value[0] == '\'') and (value[0] == value[length-1]):
                            # Get rid of bounding quotes because they are not needed...
                            value = value[1: length - 1]
                        # Now set in the PropList
                        if len(name) > 0:
                            self.append(name, value, False)
                    else:
                        logger.warning("Missing or too many equal signs on line " + str(self.__lastLineNumberRead) +
                                       " of " + self.__persistentName + " (" + line + ")")
        except Exception as e:
            message = ("Exception caught while reading line " + str(self.__lastLineNumberRead) + " of " +
                       self.__persistentName + ".")
            logger.warning(message)
        # Clean up...
        self.__howSet = howSetPrev

    def set(self, prop):
        """
        Set the property given a Prop.  If the property key exists, reset the property to the new information.
        :param prop: The contents of the property.
        """
        replace = True
        # Find if this is already a property in this list...
        if prop is None:
            return
        index = self.findProp(prop.getKey())
        if (index < 0) or not replace:
            # Not currently in the list so add it...
            self.append(prop.getKey(), prop.getContents(), prop.getValue(self))
        else:
            # Already in the list so change it...
            prop.setHowSet(self.__howSet)
            self.__list[index] = prop

    def setPersistentName(self, persistent_name):
        if persistent_name is not None:
            self.__persistentName = persistent_name

    def __str__(self):
        return self.toString(",")

    def toString(self, delim):
        str = ""
        for i, prop in enumerate(self.__list):
            if i > 0:
                str += delim
            if prop is None:
                str += "None"
            else:
                str += (prop.getKey() + "=\"" + prop.getValue() + "\"")
        return str