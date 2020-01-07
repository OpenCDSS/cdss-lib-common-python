# TimeInterval - time interval class

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


class TimeInterval(object):
    # The TimeInterval class provide methods to convert intervals from
    # integer to string representations.  Common usage is to call the parse_interval()
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
        self.interval_base_string = ""
        # The string associated with the interval multiplier (may be "" if
        # not specified in string used with the constructor).
        self.interval_mult_string = ""
        # The base data interval.
        self.interval_base = 0
        # The data interval multiplier.
        self.interval_mult = 0

        self.init()

    def init(self):
        """
        Initialize the data.
        """
        self.interval_base = 0
        self.interval_base_string = ""
        self.interval_mult = 0
        self.interval_mult_string = ""

    def get_base(self):
        """
        Return the interval base (see TimeInterval.INTERVAL*).
        :return: The interval base (see TimeInterval.INTERVAL*).
        """
        return self.interval_base

    def get_multiplier(self):
        """
        Return the interval multiplier.
        :return: The interval multiplier.
        """
        return self.interval_mult

    @staticmethod
    def is_regular_interval(interval_base):
        """
Determine whether an interval is regular.
@param intervalBase the time interval base to check
@return true if the interval is regular, false if not (unknown or irregular).
        """
        if (interval_base >= TimeInterval.HSECOND) and (interval_base <= TimeInterval.YEAR):
            return True
        else:
            # Irregular and unknown are what are left.
            return False

    @staticmethod
    def parse_interval(interval_string):
        """
        Parse an interval string like "6Day" into its parts and return as a
        TimeInterval.  If the multiplier is not specified, the value returned from
        get_multiplier() will be "", even if the get_multiplier() is 1.
        :param interval_string: Time series interval as a string, containing
        interval string and an optional multiplier.
        :return: The time interval that is parsed from the string.
        """
        logger = logging.getLogger(__name__)
        digit_count = 0  # Count of digits at start of the interval string
        dl = 50
        i = 0
        length = len(interval_string)

        interval = TimeInterval()

        # Need to strip of any leading digits.

        while i < length:
            if interval_string[i].isdigit():
                digit_count += 1
                i += 1
            else:
                # We have reached the end of the digit part of the string
                break

        if digit_count == 0:
            #
            # This string had no leading digits, interpret as one.
            #
            interval.set_multiplier(1)
        elif digit_count == length:
            #
            # The whole string is a digit, default to hourly (legacy behavior)
            #
            interval.set_base(TimeInterval.HOUR)
            interval.set_multiplier(int(interval_string))
            return interval
        else:
            interval_mult_string = interval_string[digit_count:]
            interval.set_multiplier(int(interval_mult_string))
            interval.set_multiplier_string(interval_mult_string)

        # Now parse out the Base interval
        interval_base_string = interval_string[digit_count:].strip()
        interval_base_string_upper = interval_base_string.upper()
        if (interval_base_string_upper.startswith("DAY")) or (interval_base_string_upper.startswith("DAI")):
            interval.set_base_string(interval_base_string)
            interval.set_base(TimeInterval.DAY)
        elif (interval_base_string_upper.startswith("MON")):
            interval.set_base_string(interval_base_string)
            interval.set_base(TimeInterval.MONTH)
        else:
            if len(interval_string) == 0:
                logger.warning("No interval specified.")
            else:
                logger.warning("Unrecognized interval \"{}\"".format(interval_string[digit_count:]))
            return
        return interval

    def set_base(self, base):
        """
        Set the interval base.
        :param base: Time series interval.
        :return: Zero if successful, non-zero if not.
        """
        self.interval_base = base

    def set_base_string(self, base_string):
        """
        Set the interval base string. This is normally only called by other methods within this class.
        :param base_string: Time series interval base as string.
        """
        if base_string is not None:
            self.interval_base_string = base_string

    def set_multiplier(self, mult):
        """
        Set the interval multiplier
        :param mult: Time series interval
        """
        self.interval_mult = mult

    def set_multiplier_string(self, multiplier_string):
        """
        Set the interval multiplier string.  This is normally only called by other methods within this class.
        :param multiplier_string: Time series interval base as string.
        """
        if multiplier_string is not None:
            self.interval_mult_string = multiplier_string