# TimeInterval - time interval class

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
# TimeInterval - time interval class
# ----------------------------------------------------------------------------
# History:
#
# 22 Sep 1997	Steven A. Malers, RTi	First version.
# 13 Apr 1999	SAM, RTi		Add finalize.
# 01 May 2001	SAM, RTi		Add toString(), compatible with C++.
# 					Add equals().
# 2001-11-06	SAM, RTi		Review javadoc.  Verify that variables
# 				are set to null when no longer used.
# 					Change set methods to have void return
# 					type.
# 2001-12-13	SAM, RTi		Copy TSInterval to TimeInterval and
# 					make changes to make the class more
# 					generic.  parseInterval() now throws an
# 					exception if unable to parse.
# 2001-04-19	SAM, RTi		Add constructor to take integer base and
# 					multiplier.
# 2002-05-30	SAM, RTi		Add getMultiplierString() to better
# 					support exact lookups of interval parts
# 					(e.g., for database queries that require
# 				parts).
# 2003-05-30	SAM, RTi		Add multipliersForIntervalBase()
# 					to return reasonable multipliers for a
# 					base string.  Add support for seconds
# 					in parseInterval().
# 2003-10-27	SAM, RTi		Add UNKNOWN for time interval.
# 2005-02-16	SAM, RTi		Add getTimeIntervalChoices() to
# 					facilitate use in interfaces.
# 2005-03-03	SAM, RTi		Add lessThan(), lessThanOrEquivalent(),
# 					greaterThan(),greaterThanOrEquivalent(),
# 					equivalent().  REVISIT - only put in the
# 					comments but did not implement.
# 2005-08-26	SAM, RTi		Overload getTimeIntervalChoices() to
# 					include Irregular.
# 2005-09-27	SAM, RTi		Add isRegularInterval().
# 2006-04-24	SAM, RTi		Change parseInterval() to throw an
# 					InvalidTimeIntervalException if the
# 					interval is not recognized.
# 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
#  ----------------------------------------------------------------------------
# EndHeader

import logging


class TimeInterval(object):
    # The TimeInterval class provide methods to convert intervals from
    # integer to string representations.  Common usage is to call the parseInterval()
    # method to parse a string and then use the integer values to increase
    # performance.  The TimeInterval data members can be used when creating DateTime instances.
    # A lookup of string interval names from the integer values may not return
    # exactly the string that is allowed in a parse (due to case being ignored, etc.).

    # Time interval base values.  These intervals are guaranteed to have values less
    # than 256 (this should allow for addition of other intervals if necessary).  The
    # interval values may change in the future.  The values assigned to intervals
    # increase with the magnitude of the interval (e.g., YEAR > MONTH).  Only irregular has no place in
    # the order.  Flags above >= 256 are reserved for DateTime constructor flags.
    # These values are set as the DateTime.PRECISION* values to maintain consistency.
    UNKNOWN = -1
    IRREGULAR = 0
    HSECOND = 5
    SECOND = 10
    MINUTE = 20
    HOUR = 30
    DAY = 40
    WEEK = 50
    MONTH = 60
    YEAR = 70

    def __init__(self):
        # THe string associated with the base interval (e.g., "Month").
        self.__intervalBaseString = ""
        # The string associated with the interval multiplier (may be "" if
        # not specified in string used with the constructor).
        self.__intervalMultString = ""
        # The base data interval.
        self.__intervalBase = 0
        # The data interval multiplier.
        self.__intervalMult = 0

        self.init()

    def init(self):
        """
        Initialize the data.
        """
        self.__intervalBase = 0
        self.__intervalBaseString = ""
        self.__intervalMult = 0
        self.__intervalMultString = ""

    def getBase(self):
        """
        Return the interval base (see TimeInterval.INTERVAL*).
        :return: The interval base (see TimeInterval.INTERVAL*).
        """
        return self.__intervalBase

    def getMultiplier(self):
        """
        Return the interval multiplier.
        :return: The interval multiplier.
        """
        return self.__intervalMult

    @staticmethod
    def parseInterval(intervalString):
        """
        Parse an interval string like "6Day" into its parts and return as a
        TimeInterval.  If the multiplier is not specified, the value returned from
        getMultiplierString() will be "", even if the getMultiplier() is 1.
        :param intervalString: Time series interval as a string, containing
        interval string and an optional multiplier.
        :return: The time interval that is parsed from the string.
        """
        logger = logging.getLogger("StateMod")
        routine = "TimeInterval.parseInterval"
        digitCount = 0  # Count of digits at start of the interval string
        dl = 50
        i = 0
        length = len(intervalString)

        interval = TimeInterval()

        # Need to strip of any leading digits.

        while i < length:
            if intervalString[i].isdigit():
                digitCount += 1
                i += 1
            else:
                # We have reached the end of the digit part of the string
                break

        if digitCount == 0:
            #
            # This string had no leading digits, interpret as one.
            #
            interval.setMultiplier(1)
        elif digitCount == length:
            #
            # The whole string is a digit, default to hourly (legacy behavior)
            #
            interval.setBase(TimeInterval.HOUR)
            interval.setMultiplier(int(intervalString))
            return interval
        else:
            intervalMultString = intervalString[digitCount:]
            interval.setMultiplier(int(intervalMultString))
            interval.setMultiplierString(intervalMultString)

        # Now parse out the Base interval
        intervalBaseString = intervalString[digitCount:].strip()
        intervalBaseStringUpper = intervalBaseString.upper()
        if (intervalBaseStringUpper.startswith("DAY")) or (intervalBaseStringUpper.startswith("DAI")):
            interval.setBaseString(intervalBaseString)
            interval.setBase(TimeInterval.DAY)
        elif (intervalBaseStringUpper.startswith("MON")):
            interval.setBaseString(intervalBaseString)
            interval.setBase(TimeInterval.MONTH)
        else:
            if len(intervalString) == 0:
                logger.warning("No interval specified.")
            else:
                logger.warning("Unrecognized interval \"{}\"".format(intervalString[digitCount:]))
            return
        return interval

    def setBase(self, base):
        """
        Set the interval base.
        :param base: Time series interval.
        :return: Zero if successful, non-zero if not.
        """
        self.__intervalBase = base

    def setBaseString(self, base_string):
        """
        Set the interval base string. This is normally only called by other methods within this class.
        :param base_string: Time series interval base as string.
        """
        if base_string is not None:
            self.__intervalBaseString = base_string

    def setMultiplier(self, mult):
        """
        Set the interval multiplier
        :param mult: Time series interval
        """
        self.__intervalMult = mult

    def setMultiplierString(self, multiplier_string):
        """
        Set the interval multiplier string.  This is normally only called by other methods within this class.
        :param multiplier_string: Time series interval base as string.
        """
        if multiplier_string is not None:
            self.__intervalMultString = multiplier_string