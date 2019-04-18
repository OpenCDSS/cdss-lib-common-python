# Prop - use to hold an object's properties

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

 # ----------------------------------------------------------------------------
 # Prop - use to hold an object's properties
 # ----------------------------------------------------------------------------
 # Notes:	(1)	This is useful for program or other component
	# 		information.
	# 	(2)	PropList manages a list of these properties.
 # ----------------------------------------------------------------------------
 # History:
 #
 # Sep 1997?	Steven A. Malers,	Initial version.  Start dabbling to
	# 	Riverside Technology,	formalize update of legacy setDef/
	# 	inc.			getDef code.
 # 02 Feb 1998	SAM, RTi		Get all the Prop* classes working
	# 				together and start to use in
	# 				production.
 # 24 Feb 1998	SAM, RTi		Add the javadoc comments.
 # 13 Apr 1999	SAM, RTi		Add finalize.
 # 10 May 2001	SAM, RTi		Add ability to expand the property
	# 				contents as per makefile and RTi
	# 				property file.  Do so by overloading
	# 				getValue() to take a persistent format
	# 				flag to indicate that expansion should
	# 				be checked.  Also add refresh().
 # 2002-02-03	SAM, RTi		Change long _flags integer _how_set and
	# 				clean up the SET_* values - use with
	# 				PropList's _how_set flag to streamline
	# 				tracking user input.  Change methods to
	# 				be of void type rather than return an
	# 				int (since the return type is of no
	# 				importance).
 # 2004-02-19	J. Thomas Sapienza, RTi	Implements the Comparable interface so
	# 				that a PropList can be sorted.
 # 2004-05-10	SAM, RTi		Add a "how set" option of
	# 				SET_AT_RUNTIME_FOR_USER.
 # 2005-10-20	JTS, RTi		Added a "how set" option of
	# 				SET_HIDDEN for Properties that are
	# 				always behind-the-scenes, which should
	# 				never be saved, viewed, or known by
	# 				users.
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

    def __init__(self, howSet=None, intKey=None, key=None, contents=None, value=None):
        # Indicates whether property is read from a persistent source, set internally as a
        # run-time default, or is set at runtime by the user.
        self.__howSet = int()

        # Integer key for faster lookups.
        self.__intKey = int()

        # Indicate whether the property is a literal string.
        # By default the property is a normal property.
        self.__isLiteral = False

        # String to look up property.
        self.__key = ""

        # Contents of property (anything derived from Object).  This may be a string or another
        # object.  If a string, it contains the value before expanding wildcards, etc.
        self.__contents = None

        # Value of the object as a string.  In most cases, the object will be a string.  The
        # value is the fully-expanded string (wildcards and other variables are expanded).  If not
        # a string, this may contain the toString() representation.
        self.__value = ""

        if howSet is not None:
            if intKey is not None:
                if value is not None:
                    # Construct using a string key, an integer key, and both contents and value.
                    # Prop(key, intKey, contents, value, howSet)
                    self.initialize(howSet, intKey, key, contents, value)
                else:
                    # Construct using a string key, an integer key, string contents, and specify modifier flags.
                    # Prop(key, intKey, contents, howSet)
                    self.initialize(howSet, intKey, key, contents, contents)
            else:
                # Construct using a string key, and both contents and string value.
                # Prop(key, contents, value, howSet)
                self.initialize(howSet, 0, key, contents, value)
        elif howSet is None:
            if intKey is not None:
                if value is not None:
                    # Construct using a string key, an integer key, and both contents and value.
                    # Prop(key, intKey, key, contents, value)
                    self.initialize(Prop.SET_UNKNOWN, intKey, key, contents, value)
                else:
                    # Construct using a string key, an integer key, and string contents.
                    # Prop(key, intKey, contents)
                    self.initialize(Prop.SET_UNKNOWN, intKey, key, contents, contents)
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

    def getContents(self):
        """
        Return the contents (Object) for the property.
        :return: The contents (Object) for the property (note: the original is returned, not a copy).
        """
        return self.__contents

    def getKey(self):
        """
        Return the string key for the property
        :return: The string key for the property.
        """
        return self.__key

    def getValue(self, props=None):
        # This will expand contents if necessary...
        # self.refresh( props )
        return self.__value

    def initialize(self, howSet, intKey, key, contents, value):
        """
        initialize member data
        :param howSet: Indicates how the property is being set.
        :param intKey: Integer to use to look up the property (integer keys can be used
        in place of strings for lookups).
        :param key: String to use as key to look up property.
        :param contents: The contents of the property (in this case the same as the
        :param value: The value of the property as a string.
        """
        self.__howSet = howSet
        self.__intKey = intKey
        if key == None:
            self.__key = ""
        else:
            self.__key = key
        self.__contents = contents
        if value == None:
            self.__value = ""
        else:
            self.__value = value

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
    #         if isinstance(self.__contents, str):
    #             self.__value = PropListManager.resolveContentsValue(props, str(self.__contents))

    def setHowSet(self, how_set):
        """
        Set how the property is being set (see SET_*)
        :param how_set: Set how the property is being set.
        """
        self.__howSet = how_set

    def setIsLiteral(self, isLiteral):
        """
        Indicate whether the property is a literal string.
        :param isLiteral: True if the property is a literal string, False if a normal
        property.
        """
        self.__isLiteral = isLiteral