# Prop - use to hold an object's properties

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

# ----------------------------------------------------------------------------
# Prop - use to hold an object's properties
# ----------------------------------------------------------------------------
# Notes:
# (1)	This is useful for program or other component information.
# (2)	PropList manages a list of these properties.
# ----------------------------------------------------------------------------


class Prop(object):

    # This class provides a way to generically store property information and can
    # be used similar to Java properties, environment variables, etc.  The main
    # difference is that it allows the contents of a property to be an Object, which
    # allows flexibility to use the property for anything in Java.
    # <p>
    # A property essentially consists of a string key and an associated object.
    # The functions that deal with property "contents" return the literal object.
    # The functions that deal with property "value" return a string representation of
    # the value.  In many cases, the Object will actually be a String and therefore
    # the contents and value will be the same (there is currently no constructor to
    # take contents only - if it is added, then the value will be set to
    # contents.toString() at construction).
    # <p>
    # A property can also hold a literal string.  This will be the case when a configuration
    # file is read and a literal comment or blank line is to be retained, to allow outputting
    # the properties with very close to the original formatting.  In this case, the
    # isLiteral() call will return true.
    # @see PropList
    # @see PropListManager

    # Indicates that it is unknown how the property was set (this is default).
    SET_UNKNOWN = 0

    # Indicates that the property was set from a file or database.  In this case,
    # when a PropList is saved, the property should typically be saved.
    SET_FROM_PERSISTENT = 1

    # Indicates that the property was set at run-time as a default value.  In this
    # case, when a PropList is saved, the property often may be ignored because it
    # will be set to the same default value the next time.
    SET_AS_RUNTIME_DEFAULT = 2

    # Indicates that the property was set by the user at run-time.  In this case,
    # when a PropList is saved, the property should likely be saved because the user
    # has specified a value different from internal defaults.
    SET_AT_RUNTIME_BY_USER = 3

    # Indicates that the property was automatically set for the user at run-time.  In
    # this case, when a PropList is saved, the property should likely be saved because
    # the user the property is considered important in defining something.  However,
    # for all practical purposes, it is a run-time default and, in and of itself,
    # should not force the user to save.
    SET_AT_RUNTIME_FOR_USER = 4

    # Indicates that the property was set behind the scenes in a way that should be
    # invisible to the user.  Users cannot edit hidden properties, will never see
    # hidden properties, and should never be able to save hidden properties to a persistent source.
    SET_HIDDEN = 5

    def __init__(self, how_set=None, int_key=None, key=None, contents=None, value=None):
        # Indicates whether property is read from a persistent source, set internally as a
        # run-time default, or is set at runtime by the user.
        self.how_set = int()

        # Integer key for faster lookups.
        self.int_key = int()

        # Indicate whether the property is a literal string.
        # By default the property is a normal property.
        self.isLiteral = False

        # String to look up property.
        self.key = ""

        # Contents of property (anything derived from Object).  This may be a string or another
        # object.  If a string, it contains the value before expanding wildcards, etc.
        self.contents = None

        # Value of the object as a string.  In most cases, the object will be a string.  The
        # value is the fully-expanded string (wildcards and other variables are expanded).  If not
        # a string, this may contain the toString() representation.
        self.value = ""

        if how_set is not None:
            if int_key is not None:
                if value is not None:
                    # Construct using a string key, an integer key, and both contents and value.
                    # Prop(key, int_key, contents, value, how_set)
                    self.initialize(how_set, int_key, key, contents, value)
                else:
                    # Construct using a string key, an integer key, string contents, and specify modifier flags.
                    # Prop(key, int_key, contents, how_set)
                    self.initialize(how_set, int_key, key, contents, contents)
            else:
                # Construct using a string key, and both contents and string value.
                # Prop(key, contents, value, how_set)
                self.initialize(how_set, 0, key, contents, value)
        elif how_set is None:
            if int_key is not None:
                if value is not None:
                    # Construct using a string key, an integer key, and both contents and value.
                    # Prop(key, int_key, key, contents, value)
                    self.initialize(Prop.SET_UNKNOWN, int_key, key, contents, value)
                else:
                    # Construct using a string key, an integer key, and string contents.
                    # Prop(key, int_key, contents)
                    self.initialize(Prop.SET_UNKNOWN, int_key, key, contents, contents)
            else:
                if value is not None:
                    # Construct using a string key, and both contents and string value.
                    # Prop(key, contents, value)
                    self.initialize(Prop.SET_UNKNOWN, 0, key, contents, value)
                else:
                    # Construct using a string key and a string.
                    # Prop(key, contents)
                    self.initialize(Prop.SET_UNKNOWN, 0, key, contents, contents)
        else:
            # Construct a property having no key and no object (not very useful!).
            # Prop()
            self.initialize(Prop.SET_UNKNOWN, 0, "", None, None)

    def get_contents(self):
        """
        Return the contents (Object) for the property.
        :return: The contents (Object) for the property (note: the original is returned, not a copy).
        """
        return self.contents

    def get_key(self):
        """
        Return the string key for the property
        :return: The string key for the property.
        """
        return self.key

    def get_value(self, props=None):
        # This will expand contents if necessary...
        # self.refresh( props )
        return self.value

    def initialize(self, how_set, int_key, key, contents, value):
        """
        initialize member data
        :param how_set: Indicates how the property is being set.
        :param int_key: Integer to use to look up the property (integer keys can be used
        in place of strings for lookups).
        :param key: String to use as key to look up property.
        :param contents: The contents of the property (in this case the same as the
        :param value: The value of the property as a string.
        """
        self.how_set = how_set
        self.int_key = int_key
        if key == None:
            self.key = ""
        else:
            self.key = key
        self.contents = contents
        if value == None:
            self.value = ""
        else:
            self.value = value

    # def refresh(self, props):
    #     """
    #     Refresh the contents by resetting the value by expanding the contents.
    #     :param props: PropList to search.
    #     :return: The string value for the property
    #     """
    #     persistent_format = props.getPersistentFormat()
    #     if persistent_format == PropList.FORMAT_MAKEFILE or persistent_format == PropList.FORMAT_NWSRFS or \
    #         persistent_format == PropList.FORMAT_PROPERTIES:
    #         # Try to expand the contents...
    #         if isinstance(self.contents, str):
    #             self.value = PropListManager.resolveContentsValue(props, str(self.contents))

    def set_how_set(self, how_set):
        """
        Set how the property is being set (see SET_*)
        :param how_set: Set how the property is being set.
        """
        self.how_set = how_set

    def set_is_literal(self, is_literal):
        """
        Indicate whether the property is a literal string.
        :param is_literal: True if the property is a literal string, False if a normal
        property.
        """
        self.is_literal = is_literal