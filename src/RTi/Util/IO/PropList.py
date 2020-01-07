# PropList - use to hold a list of properties

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
    evaluates to to_string(); however, applications will often use the contents
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
    props.set_persistent_name ( "somefile" );
    // The following uses a "how set" value of Prop.SET_FROM_PERSISTENT.
    props.read_persistent ( "somefile" );
    // Next, the application may check the file properties and assign some internal
    // defaults to have a full set of properties...
    props.set_how_set ( Prop.SET_AS_RUNTIME_DEFAULT );
    // When a user interface is displayed...
    props.set_how_set ( Prop.SET_AT_RUNTIME_BY_USER );
    // ...User interaction...
    props.set_how_set ( Prop.SET_UNKNOWN );
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

    def __init__(self, list_name=None, persistent_name=None, persistent_format=None):
        # Name of this PropList.
        self.list_name = ""

        # List of Prop.
        # - use "prop_list" rather than "list" because the latter is part of Python
        self.prop_list = []

        # File to save in.
        self.persistent_name = ""

        # Format of file to read
        self.persistent_format = None

        # Last line read from the property file.
        self.last_line_number_read = None

        # Indicates if quotes should be treated literally when setting Prop values.
        self.literal_quotes = True

        # The "how set" value to use when properties are being set
        self.how_set = Prop.SET_UNKNOWN

        if list_name is not None:
            if persistent_format is not None:
                if persistent_name is not None:
                    # Construct using a list name, a configuration file name,
                    # and a configuration file format type.  The file is not actually read (call read_persistent()
                    # to do so).
                    # PropList(list_name, persistent_name, persistent_format)
                    self.initialize(list_name, persistent_name, persistent_format)
                else:
                    # Construct using a list name, a configuration file name,
                    # and a configuration file format type.  The file is not actually read (call read_persistent()
                    # to do so).
                    # PropList(list_name, persistent_format)
                    self.initialize(list_name, "", persistent_format)
            else:
                # Construct given the name of the list (the list name should be unique if
                # multiple lists are being used in a PropListManager.  The persistent format defaults to
                # FORMAT_UNKNOWN.
                # PropList(list_name)
                self.initialize(list_name, "", PropList.FORMAT_UNKNOWN)

    def append(self, key, contents=None, value=None, is_literal=False):
        """
        Append a property to the list using a string key.
        :param key: String key for the property
        :param contents: Contents for the property (any object type)
        :param value: String value for property, str(contents) if None
        :param is_literal: whether the property is a literal string (contents=value)
        """
        int_key = None
        if value is None:
            value = str(contents)
        prop = Prop(self.how_set, int_key, key, contents, value)
        prop.set_is_literal(is_literal)
        self.prop_list.append(prop)

    def clear(self):
        """
        Remove all items from the PropList
        """
        self.prop_list.clear()

    def element_at(self, pos):
        """
        Return the Prop instance at the requested position.  Use size() to determine the size of the PropList.
        :param pos: the position of the property to return (0+).
        :return: the Prop at the specified position.
        """
        return self.prop_list[pos]

    def find_prop(self, key):
        """
        Find a property in the list.
        :param key: The string key used to look up the property.
        """
        for i, prop_i in enumerate(self.prop_list):
            prop_key = prop_i.get_key()
            if key.upper() == prop_key.upper():
                # Have a match. Return the position...
                return i
        return -1

    def get_contents(self, key):
        """
        The data object for the property corresponding to the string key, or None if not found.
        :param key: The string key used to look up the property
        """
        pos = self.find_prop(key)
        if pos >= 0:
            # Have a match. Get the value...
            return self.prop_list[pos].get_contents(self)
        return None

    def get_list(self):
        """
        Returns the list of Props.
        :return: the list of props.
        """
        return self.prop_list

    def get_persistent_name(self):
        """
        Return the format of the property list file.
        :return: The format of the property list file.
        """
        return self.persistent_format

    def get_value(self, key):
        """
        The string value of the property corresponding to the string key, or None if not found.
        :param key: The string key used to look up the property
        """
        pos = self.find_prop(key)
        if pos >= 0:
            # We have a match. Get the value...
            return self.prop_list[pos].get_value(self)
        return None

    def initialize(self, list_name, persistent_name, persistent_format):
        """
        Initialize the object.
        :param list_name: Name for the PropList.
        :param persistent_name: Persistent name for the PropList (used only when reading from a file).
        :param persistent_format: Format for properties file.
        """
        if list_name is None:
            self.list_name = ""
        else:
            self.list_name = list_name
        if persistent_name is None:
            self.persistent_name = ""
        else:
            self.persistent_name = persistent_name
        self.persistent_format = persistent_format
        self.prop_list = []
        self.last_line_number_read = 0

    def read_persistent(self, append=None, include_literals=None):
        """
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
        :param include_literals: if true, comments and other non-property lines will be included as literals
        in the property list using key "Literal1", "Literal2", etc.  This is useful if reading a property file,
        updating its values, and then writing out again, trying to retain the original comments.
        """
        logger = logging.getLogger(__name__)

        if append is None:
            # Default is to reset append when read
            append = True
        if include_literals is None:
            # Default is store properties with content object and string object
            include_literals = False

        prefix = ""
        continuation = False
        line_save = None
        in_comment = False
        literal_count = 0

        if not append:
            self.clear()

        how_set_prev = self.how_set
        self.how_set = Prop.SET_FROM_PERSISTENT
        try:
            self.last_line_number_read = 0
            with open(self.persistent_name) as f:
                for line in f:
                    line = line.strip()
                    self.last_line_number_read += 1
                    if continuation:
                        # Take this line and add it to the previous. Add a space to separate tokens.
                        # Should not normally be a comment.
                        line = str(line_save) + " " + line
                    # Handle line continuation with \ at end...
                    if line.endswith("\\"):
                        continuation = True
                        # Add a space at the end because when continuing lines the next line
                        # likely has separation tokens.
                        line_save = line[0:len(line)-1]
                        continue
                    continuation = False
                    line_save = None
                    if len(line) > 0:
                        if line[0] == '#':
                            # Comment line
                            if include_literals:
                                literal_count += 1
                                self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
                            continue
                        elif line.startswith("<#") or line.startswith("</#"):
                            # Freemarker template syntax
                            continue
                    if line.find('#') != -1:
                        idx = line.index('#')
                        line = line[0:idx]
                    if in_comment and line.startswith("*/"):
                        in_comment = False
                        # For now the end of comment must be at the start of the line so
                        # ignore the rest of the line...
                        if include_literals:
                            literal_count += 1
                            self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
                        continue
                    if (not in_comment) and line.startswith("/*"):
                        in_comment = True
                        # For now the end of comment must be at the start of the line so ignore the rest of the
                        # line...
                        if include_literals:
                            literal_count += 1
                            self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
                        continue
                    if in_comment:
                        # Did not detect an end to the comment above so skip the line...
                        if include_literals:
                            literal_count += 1
                            self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
                        continue
                    if len(line) == 0:
                        if include_literals:
                            literal_count += 1
                            self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
                        continue
                    if line[0] == '[':
                        # Block indicator - contents of [] will be prepended to property names
                        if line.index("${") >= 0:
                            # Likely a freemarker template syntax so skip
                            continue
                        if line.index(']') == -1:
                            logger.warning("Missing ] on line " + str(self.last_line_number_read) + " of " +
                                           self.persistent_name)
                            continue
                        prefix = line[1: line.index(']')] + "."
                        if include_literals:
                            literal_count += 1
                            self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
                        continue
                    try:
                        pos = line.index('=')
                    except ValueError:
                        pos = -1
                    if pos < 0:
                        logger.warning("Missing equal sign on line " + str(self.last_line_number_read) + " of " +
                                       self.persistent_name + " (" + line + ")")
                        if include_literals:
                            literal_count += 1
                            self.append(key="Literal" + str(literal_count), contents=line, is_literal=True)
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
                            self.append(key=name, contents=value, is_literal=False)
                    else:
                        logger.warning("Missing or too many equal signs on line " + str(self.last_line_number_read) +
                                       " of " + self.persistent_name + " (" + line + ")")
        except Exception as e:
            message = ("Exception caught while reading line " + str(self.last_line_number_read) + " of " +
                       self.persistent_name + ".")
            logger.warning(message, exc_info=True)
        # Clean up...
        self.how_set = how_set_prev

    def set(self, prop=None, key=None, value=None, replace=True):
        """
        Set the property given a Prop or "Property=Value" string.
        If the property key exists, reset the property to the new information.
        :param prop: The contents of the property.
        :param key: Property name.
        :param value: Property value.
        :param replace: Whether to replace matched property.
        """
        replace = True
        # Find if this is already a property in this list...
        if prop is not None:
            # Prop instance is provided
            i = self.find_prop(prop.get_key())
            if (i < 0) or not replace:
                # Not currently in the list so add it...
                self.append(key=prop.get_key(), contents=prop.get_contents(), value=prop.get_value(self))
            else:
                # Already in the list so change it...
                prop.set_how_set(self.how_set)
                self.prop_list[i] = prop
        elif key is not None:
            # String in format "key" = "value" is provided
            i = self.find_prop(key)
            if (i < 0) or not replace:
                # Not currently in the list so add it...
                self.append(key=key, contents=value, value=value)
            else:
                # Already in the list so change it...
                prop = self.prop_list[i]
                prop.set_key(key)
                prop.set_contents(value)
                prop.set_value(value)
                prop.set_how_set(self.how_set)

    def set_persistent_name(self, persistent_name):
        if persistent_name is not None:
            self.persistent_name = persistent_name

    def __str__(self):
        return self.to_string(",")

    def to_string(self, delim):
        s = ""
        for i, prop in enumerate(self.prop_list):
            if i > 0:
                s += delim
            if prop is None:
                s += "None"
            else:
                s += (prop.get_key() + "=\"" + prop.get_value() + "\"")
        return s