# DateTime - general Date/Time class

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
import logging

from RTi.Util.String.StringUtil import StringUtil
from RTi.Util.Time.TimeInterval import TimeInterval
from RTi.Util.Time.TimeUtil import TimeUtil


class DateTime(object):
    """
    The DateTime class provides date/time storage and manipulation for general use.
    Unlike the Java Date and Calendar classes, this class allows date/time
    data fields to be easily set and manipulated, for example to allow fast iteration without
    having to recreate DateTime instances.
    Specific features of the DateTime class are:
    <ul>
    <li>	An optional bitmask flag can be used at construction to indicate the
        precision (which matches the TimeInterval values), initialization
        (to zero or current date/time), and performance (fast or strict).
        TimeInterval.YEAR is equal to DateTime.PRECISION_YEAR, etc.</li>
    <li>	The precision values are mutually exclusive; therefore, they can be
        compared as binary mask values or with ==.</li>
    <li>	By default the time zone is not used in DateTime manipulation or output.
        However, if the PRECISION_TIME_ZONE flag is set during creation or with
        a call to set_time_zone(), then the time zone is intended to be used
        throughout (comparison, output, etc.).  See the getDate*() methods for
        variations that consider time zone.</li>
    <li>	DateTime objects can be used in TimeUtil methods in a generic way.</li>
    <li>	Call isZero() to see whether the DateTime has zero values.  A zero
        DateTime means that the date is not the current time and values have
        not been reset from the defaults.</li>
    <li>	Precisions allow "abbreviating" a DateTime to consider only certain
        data fields.  By default, the larger interval data (e.g., year) are
        included and only smaller data (e.g., seconds) can be cut out of the
        precision.  If the TIME_ONLY bitmask is used at creation, then the
        date fields can be ignored.</li>
    </ul>
    """

    # /**
    # Flags for constructing DateTime instances, which modify their behavior.
    # These flags have values that do not conflict with the TimeInterval base interval
    # values and the flags can be combined in a DateTime constructor.
    # The following flag indicates that a DateTime be treated strictly, meaning that
    # the following dependent data are reset each time a date field changes:
    # <p>
    # day of year<br>
    # whether a leap year<br>

    # This results in slower processing of dates and is the default behavior.  For
    # iterators, it is usually best to use the DATE_FAST behavior.
    DATE_STRICT = 0x1000

    # Indicates that dates need not be treated strictly.  This is useful for faster
    # processing of dates in loop iterators.
    DATE_FAST = 0x2000

    # Create a DateTime with zero data and blank time zone, which is the default.
    DATE_ZERO = 0x4000

    # Create a DateTime with the current date and time.
    DATE_CURRENT = 0x8000

    # Create a DateTime and only use the time fields. This works in conjunction with the precision flag.
    TIME_ONLY = 0x10000

    # The following are meant to be used in the constructor and will result in the
    # the precision for the date/time being limited only to the given date/time field.
    # These flags may at some
    # point replace the flags used for the equals method.  If not specified, all of
    # the date/time fields for the DateTime are carried (PRECISION_HSECOND).  Note
    # that these values are consistent with the TimeInterval base interval values.

    # Create a DateTime with precision only to the year.
    PRECISION_YEAR = TimeInterval.YEAR

    # Create a DateTime with a precision only to the month.
    PRECISION_MONTH = TimeInterval.MONTH

    # Create a DateTime with a precision only to the day.
    PRECISION_DAY = TimeInterval.DAY

    # Create a DateTime with a precision only to the hour.
    PRECISION_HOUR = TimeInterval.HOUR

    # Create a DateTime with a precision only to the minute.
    PRECISION_MINUTE = TimeInterval.MINUTE

    # Create a DateTime with a precision only to the second.
    PRECISION_SECOND = TimeInterval.SECOND

    # Create a DateTime with a precision to the hundredth-second
    PRECISION_HSECOND = TimeInterval.HSECOND

    # Create a DateTime with a precision that includes the time zone (and may include another precision flag).
    PRECISION_TIME_ZONE = 0x20000

    # Alphabetize the formats, but the numbers may not be in order because they
    # are added over time (do not renumber because some dependent classes may not get recompiled).

    # The following are used to format date/time output.
    # <pre>
    # 	Y = year
    # 	M = month
    # 	D = day
    # 	H = hour
    # 	m = minute
    # 	s = second
    # 	h = 100th second
    # 	Z = time zone
    # </pre>

    # The following returns an empty string for formatting but can be used to
    # indicate no formatting in other code.
    FORMAT_NONE = 1

    # The following returns the default format and can be used to
    # indicate automatic formatting in other code.
    FORMAT_AUTOMATIC = 2

    # The following formats a date as follows:  "DD/MM/YYYY".  This date format
    # cannot be parsed properly by parse(); FORMAT_MM_SLASH_DD_SLASH_YYYY will be returned instead.
    FORMAT_DD_SLASH_MM_SLASH_YYYY = 27

    # The following formats a data as follows: "HH:mm"
    FORMAT_HH_mm = 3

    # The following formats a data as follows (military time): "HHmm"
    FORMAT_HHmm = 4

    # The following formats a date as follows:  "MM".  Parsing of this date format
    # without specifying the format is NOT supported because it is ambiguous.
    FORMAT_MM = 5

    # The following formats a data as follows: "MM-DD".
    FORMAT_MM_DD = 6

    # The following formats a data as follows: "MM/DD".
    FORMAT_MM_SLASH_DD = 7

    # The following formats a date as follows: "MM/DD/YY".
    FORMAT_MM_SLASH_DD_SLASH_YY = 8

    # The following formats a date as follows: "MM/DD/YYYY".
    FORMAT_MM_SLASH_DD_SLASH_YYYY = 9

    # The following formats a data as follows: "MM/DD/YYYY HH"
    FORMAT_MM_SLASH_DD_SLASH_YYYY_HH = 10

    # The following formats a data as follows: "MM-DD-YYYY HH"
    FORMAT_MM_DD_YYYY_HH = 11

    # The following formats a data as follows: "MM/DD/YYYY HH:mm". For the parse() method,
    # months, days, and hours that are not padded with zeroes will also be parsed properly.
    FORMAT_MM_SLASH_DD_SLASH_YYYY_HH_mm = 12

    # The following formats a data as follows: "MM/YYYY"
    FORMAT_MM_SLASH_YYYY = 13

    # The following formats a data as follows: "YYYY".
    FORMAT_YYYY = 14

    # The following formats a data as follows: "YYYY-MM"
    FORMAT_YYYY_MM = 15

    # The following formats a data as follows: "YYYY-MM-DD"
    FORMAT_YYYY_MM_DD = 16

    # The following is equivelent to FORMAT_YYYY_MM_DD
    FORMAT_Y2K_SHORT = FORMAT_YYYY_MM_DD

    # The following formats a data as follows: "YYYY-MM-DD HH"
    FORMAT_YYYY_MM_DD_HH = 17

    # The following formats a data as follows: "YYYY-MM-DD HH ZZZ"
    FORMAT_YYYY_MM_DD_HH_ZZZ = 18

    # The following formats a data as follows: "YYYY-MM-DD HH:mm"
    FORMAT_YYYY_MM_DD_HH_mm = 19

    # The following is equivelent to FORMAT_YYYY_MM_DD_HH_mm
    FORMAT_Y2K_LONG = FORMAT_YYYY_MM_DD_HH_mm

    # The following formats a data as follows: "YYYY-MM-DD HHmm"
    FORMAT_YYYY_MM_DD_HHmm = 20

    # The following formats a data as follows: "YYYYMMDDHHmm"
    FORMAT_YYYYMMDDHHmm = 21

    # The following formats a data as follows: "YYYY-MM-DD HH:mm ZZZ".
    #     # This format is currently only supported for toString() (not parse).
    FORMAT_YYYY_MM_DD_HH_mm_ZZZ = 22

    # The following formats a data as follows: "YYYY-MM-DD HH:mm:SS"
    FORMAT_YYYY_MM_DD_HH_mm_SS = 23

    # The following formats a data as follows: "YYYY-MM-DD HH:mm:SS:hh"
    FORMAT_YYYY_MM_DD_HH_mm_SS_hh = 24

    # The following formats a data as follows: "YYYY-MM-DD HH:mm:SS:hh ZZZ"
    # This is nearly ISO 8601 but it does not include the T before time and the time
    # zone has a space.
    FORMAT_YYYY_MM_DD_HH_mm_SS_hh_ZZZ = 25

    # The following formats a data as follows: "YYY-MM-DD HH:mm:SS ZZZ"
    FORMAT_YYYY_MM_DD_HH_mm_SS_ZZZ = 26

    # The following formats a data as follows: "MM/DD/YYYY HH:mm:SS"
    FORMAT_MM_SLASH_DD_SLASH_YYYY_HH_mm_SS = 28

    # The following formats a data as follows: "YYYYMMDD"
    FORMAT_YYYYMMDD = 29

    # The following formats a date/time according to ISO 8601, for example for longest form:
    # 2017-06-30T23:03:33.123+06:00
    FORMAT_ISO_8601 = 30

    # The following formats a data as follows, for debugging: year=YYYY, month=MM, etc...
    FORMAT_VERBOSE = 200

    def __init__(self, flag=None, date=None, date_time=None):

        logger = logging.getLogger("StateMod")

        # Hundredths of a second (0-99)
        self.hsecond = int()

        # Seconds (0-59)
        self.second = int()

        # Minutes past hour (0-59)
        self.minute = int()

        # Hours past midnight (0-23).  Important - hour 24 in data should be handled as
        # hour 0 of the next day.
        self.hour = int()

        # Day of month (1-31)
        self.day = int()

        # Month (1-12)
        self.month = int()

        # Year (4 digit).
        self.year = int()

        # Time zone abbreviation
        self.tz = str()

        # Indicate whether the year a leap year (true) or not (false).
        self.isleap = bool()

        # Is the DateTime initialized to zero without further changes?
        self.iszero = bool()

        # Day of week (0=Sunday). Will be calculated in getWeekDay(0.
        self.weekday = -1

        # Day of year (0-356).
        self.yearday = int()

        # Absolute month (year*12 + month)
        self.abs_month = int()

        # Precision of the DateTime (allows some optimization and automatic
        # decisions when converting). This is the PRECISION_* value only
        # (not a bit mask).  _use_time_zone and _time_only control other precision information.
        self.precision = int()

        # Flag for special behavior of dates.  Internally this contains all the
        # behavior flags but for the most part it is only used for ZERO/CURRENT and FAST/STRICT checks.
        self.behavior_flag = int()

        # Indicates whether the time zone should be used when processing the DateTime.
        # SetTimeZone() will set to true if the time zone is not empty, false if empty.
        # Setting the precision can override this if time zone flag is set.
        self.use_time_zone = False

        # Use only times for the DateTime.
        self.time_only = False

        if flag is not None:
            self.initialize_DateTime_Flag(flag)
        elif date is not None:
            self.initialize_DateTime_Date(date)
        elif date_time is not None:
            self.initialize_DateTime_DateTime(date_time)

    def __str__(self):
        """
        Return string representation of instance.
        """
        return self.to_string()

    def add_day(self, add):
        """
        Add day(s) to the DateTime.  Other fields will be adjusted if necessary.
        :param add: Indicates the number of days to add (can be multiple and can be negative)
        """
        i = int()

        if add == 1:
            num_days_in_month = TimeUtil.num_days_in_month(self.month, self.year)
            self.day += 1
            if self.day > num_days_in_month:
                # Have gone into the next month...
                self.day -= num_days_in_month
                self.add_month(1)
            # Reset the private data members.
            self.set_year_day()
        # Else...
        # Figure out if we are trying to add more than one day.
        # If so, recurse (might be a faster way, but this works)...
        elif add > 0:
            for i in range(add):
                self.add_day(1)
        elif add == -1:
            self.day -= 1
            if self.day < 1:
                # Have gone into the previous month...
                # Temporarily set day to 1, determine the day and year, and then set the day
                self.day = 1
                self.add_month(-1)
                self.day = TimeUtil.num_days_in_month(self.month, self.year)
            # Reset the private data members.
            self.set_year_day()
        elif add < 0:
            i = add
            while i < 0:
                self.add_day(-1)
                i += 1
        self.iszero = False

    def add_interval(self, interval, add):
        """
        Add a time series interval to the DateTime (see TimeInterval).  This is useful when iterating a date.
        An irregular interval is ignored (the date is not changed).
        @param interval Time series base interval.
        @param add Multiplier for base interval.
        """
        # Based on the interval, call lower-level routines...

        if interval == TimeInterval.SECOND:
            self.add_second(add)
        elif interval == TimeInterval.MINUTE:
            self.add_minute(add)
        elif interval == TimeInterval.HOUR:
            self.addHour(add)
        elif interval == TimeInterval.DAY:
            self.add_day(add)
        elif interval == TimeInterval.WEEK:
            self.add_day(7*add)
        elif interval == TimeInterval.MONTH:
            self.add_month(add)
        elif interval == TimeInterval.YEAR:
            self.add_year(add)
        elif interval == TimeInterval.IRREGULAR:
            return
        else:
            # Unsupported interval...
            #// TODO SAM 2007-12-20 Evaluate throwing InvalidTimeIntervalException
            message = "Interval " + str(interval) + " is unsupported"
            logger = logging.getLogger(__name__)
            logger.warning(message)
            return
        self.iszero = False

    def add_month(self, add):
        """
        Add month(s) to the DateTime.  Other fields will be adjusted if necessary.
        :param add: Indicates the number of months to add (can be a multiple and can be negative).
        """
        i = int()

        if add == 0:
            return
        if add == 1:
            # Dealing with one month...
            self.month += add
            # Have added one month so check if went into the next year
            if self.month > 12:
                # Have gone into the next year...
                self.month = 1
                self.add_year(1)
        # Else...
        # Loop through the number to add/subtract...
        # Use recursion because multi-month increments are infrequent
        # and the overhead of the multi-month checks is probably a wash.
        elif add > 0:
            for i in range(add):
                self.add_month(1)
            # No need to reset because it was done in the previous call.
            return
        elif add == -1:
            self.month -= 1
            # Have subtracted the specified number so check if in the previous year
            if self.month < 1:
                # Have gone into the previous year...
                self.month = 12
                self.add_year(-1)
        elif add < 0:
            for i in range(add, -1, -1):
                self.add_month(-1)
            # No need to reset because it was done in the previous call.
            return
        else:
            # Zero...
            return
        # Reset time
        self.set_absolute_month()
        self.set_year_day()
        self.iszero = False

    def add_year(self, add):
        """
        Add year(s) to the DateTime.  The month and day are NOT adjusted if an
        inconsistency occurs with leap year information.
        :param add: Indicates the number of years to add (can be a multiple and can be negative).
        """
        self.year += add
        self.reset()
        self.iszero = False

    def get_absolute_month(self):
        """
        Return the absolute month.
        :return: The absolute month (year*12 + month).
        """
        # since some data are public, recompute...
        return self.year * 12 + self.month

    def get_day(self):
        """
        Return the day
        :return: The day.
        """
        return self.day

    def get_month(self):
        """
        Return the month
        :return: The month
        """
        return self.month

    def get_year(self):
        """
        Return the year
        :return: The year.
        """
        return self.year

    def get_year_day(self):
        """
        Return the Julian day in the year.
        :return: The day of the year where Jan 1 is 1. If the behavior of the DateTime
        is DATE_FAST, zero is likely to be returned because the day of the year is not
        automatically recomputed.
        """
        # Need to set it...
        self.set_year_day()
        return self.yearday

    def greater_than(self, t):
        """
        Determine if the instance is greater than another date.  Time zone is not
        considered in the comparison (no time zone shift is made).  The comparison is
        made at the precision of the instance.
        :param t: DateTime to compare.
        :return: True if the instance is greater than the given date.
        """
        if not self.time_only:
            if self.year < t.year:
                return False
            else:
                if self.year > t.year:
                    return True

            if self.precision == DateTime.PRECISION_YEAR:
                # Equal so return false...
                return False

            # otherwise years are equal so check months
            if self.month < t.month:
                return False
            else:
                if self.month > t.month:
                    return True

            if self.precision == DateTime.PRECISION_MONTH:
                # Equal so return false...
                return False

            # months must be equal so check day

            if self.day < t.day:
                return False
            else:
                if self.day > t.day:
                    return True

            if self.precision == DateTime.PRECISION_DAY:
                # Equal so return false...
                return False

        # days are equal so check hour

        if self.hour < t.hour:
            return False
        else:
            if self.hour > t.hour:
                return True

        if self.precision == DateTime.PRECISION_HOUR:
            # Equal so return false...
            return False

        # means that hours match - so check minute

        if self.minute < t.minute:
            return False
        else:
            if self.minute > t.minute:
                return True

        if self.precision == DateTime.PRECISION_MINUTE:
            # Equal so return false..
            return False

        # means that seconds match - so check hundredths of seconds

        if self.hsecond < t.hsecond:
            return False
        else:
            if self.hsecond > t.hsecond:
                return True

        # means the are equal
        return False

    def greater_than_or_equal_to(self, d, precision):
        """
        Determine if the DateTime is >= another DateTime.  Time zone is not
        considered in the comparison (no time zone shift is made).
        @return true if the instance is >= the given DateTime.
        @param d DateTime to compare.
        @param precision The precision used when comparing the DateTime instances.
        """
        if not self.less_than(d, precision):
            return True
        else:
            return False

    # def getWeekDay(self):
    #     """
    #     Return the week day by returning getDate(TimeZoneDefaultType.GMT).get_day()
    #     :return: The weekday (sunday is 0)
    #     """
    #     # Always recompute because don't know if DateTime was copied and modified.
    #     # Does not matter what timezone because internal date/time values
    #     # are used in absolute sense.
    #     #self.weekday = self.getDate(TimeZoneDefault.GMT).get_day()
    #     self.weekday = self.getDate("GMT").get_day()
    #     return self.weekday

    def initialize_DateTime_Flag(self, flag):
        """
        Construct using the constructor modifiers (combination of PRECISION_*,
        DATE_CURRENT, DATE_ZERO, DATE_STRICT, DATE_FAST).  If no modifiers are given,
        the date/time is initialized to zeros and precision is PRECISION_MINUTE.
        :param flag: Constructor modifier
        """
        if (flag & DateTime.DATE_CURRENT) != 0:
            self.set_to_current()
        else:
            # Default
            self.set_to_zero()

        self.behavior_flag = flag
        self.set_precision(flag)
        self.reset()

    def initialize_DateTime_Date(self, d):
        """
        Construct from a Python datetime.  The time zone is not set - use the overloaded method if necessary.
        :param d: Python datetime.
        """
        if d is None:
            self.set_to_zero()
            self.reset()
            return
        # Use deprecated indicates whether to use the deprecated Date
        # functions. These should be fast (no strings) but are, of course, deprecated.
        use_deprecated = True

        if use_deprecated:
            # Returns the number of years since 1900
            year = d.year
            self.set_year()
            # Month between 1-12
            self.set_month(d.month)
            # Day between 1 and the number of days in the given month of the given year.
            self.set_day(d.day)
            self.set_precision(DateTime.PRECISION_DAY)
            # Sometimes Dates are instantiated from data where hours, etc.
            # are not available (e.g., from a database date/time).
            # Therefore catch exceptions at each step...
            try:
                # Returned hours are 0-23
                self.set_hour(d.hour)
                self.set_precision(DateTime.PRECISION_HOUR)
            except Exception as e:
                # Don't do anything. Just leave the DateTime default.
                pass
            try:
                # Return minute is in 0 to 59
                self.set_minute(d.minute)
                self.set_precision(DateTime.PRECISION_MINUTE)
            except Exception as e:
                # Don't do anything. Just leave the DateTime default
                pass
            try:
                # Returned seconds is 0 to 59
                self.set_second(d.second)
                self.set_precision(DateTime.PRECISION_SECOND)
            except Exception as e:
                # Don't do anything. Just leave the DateTime default.
                pass
            self.tz = ""

        else:
            # Date/Calendar are ugly to work with, so get information by formatting strings...

            # year month
            # Use the formatTimeString routine instead of the following...
            # String format = "yyy M d H m s S"
            # time_date = TimeUtil.getTimeString(d, format)
            format = "%Y %m %d %H %M %S"
            list = StringUtil.break_string_list(str(d), " ", StringUtil.DELIM_SKIP_BLANKS)

    def initialize_DateTime_DateTime(self, t):
        """
        Copy constructor. If the incoming date is None, the date will be initialized
        to zero information.
        :param t: DateTime to copy
        """
        logger = logging.getLogger("StateMod")
        if t is not None:
            self.hsecond = t.hsecond
            self.second = t.second
            self.minute = t.minute
            self.hour = t.hour
            self.day = t.day
            self.month = t.month
            self.year = t.year
            self.isleap = t.isleap
            self.weekday = t.weekday
            self.yearday = t.yearday
            self.abs_month = t.abs_month
            self.behavior_flag = t.behavior_flag
            self.precision = t.precision
            self.use_time_zone = t.use_time_zone
            self.time_only = t.time_only
            self.iszero = t.iszero
            self.tz = t.tz
        else:
            # Constructing from a None usually means that there is a code
            # logic problem with exception handling...
            logger.warning("Constructing DateTime from None - will have zero date!")
            self.set_to_zero()
        self.reset()

    def is_leap_year(self):
        """
        Indicate whether a leap year.
        :return: True if a leap year
        """
        # Reset to make sure...
        self.isleap = TimeUtil.is_leap_year(self.year)
        return self.isleap

    def less_than(self, t):
        """
        Determine if the DateTime is less than another DateTime.  Time zone is not
        considered in the comparison (no time zone shift is made).  The precision of the
        instance is used for the comparison.
        :param t: DateTime to compare
        :return: True if the instance is less than the given DateTime.
        """
        if not self.time_only:
            if self.year < t.year:
                return True
            else:
                if self.year > t.year:
                    return False

            if self.precision == DateTime.PRECISION_YEAR:
                # Equal so return false...
                return False

            # otherwise years are equal so check months
            if self.month < t.month:
                return True
            else:
                if self.month > t.month:
                    return False

            if self.precision == DateTime.PRECISION_MONTH:
                # Equal so return false...
                return False

            # months must be equal so check day

            if self.day < t.day:
                return True
            else:
                if self.day > t.day:
                    return False

            if self.precision == DateTime.PRECISION_DAY:
                # Equal so return false...
                return False

        # days are equal so check hour

        if self.hour < t.hour:
            return True
        else:
            if self.hour > t.hour:
                return False

        if self.precision == DateTime.PRECISION_HOUR:
            # Equal so return false...
            return False

        # means that hours match - so check minute

        if self.minute < t.minute:
            return True
        else:
            if self.minute > t.minute:
                return False

        if self.precision == DateTime.PRECISION_MINUTE:
            # Equal so return false..
            return False

        # means that seconds match - so check hundredths of seconds

        if self.hsecond < t.hsecond:
            return True
        else:
            if self.hsecond > t.hsecond:
                return False

        # means the are equal
        return False

    def less_than_or_equal_to(self, d):
        """
        Determine if the DateTime is <= another.  Time zone is not
        considered in the comparison (no time zone shift is made).
        @return true if the DateTime instance is less than or equal to given DateTime.
        @param d DateTime to compare.
        """
        return not self.greater_than(d)

    def reset(self):
        """
        Reset the derived data (year day, absolute month, and leap year).  This is
        normally called by other DateTime functions but can be called externally if
        data are set manually.
        """
        # Always reset the absolute month since it is cheap...
        self.set_absolute_month()
        if (self.behavior_flag & DateTime.DATE_FAST) != 0:
            # Want to run fast so don't check...
            return
        self.set_year_day()
        self.isleap = TimeUtil.is_leap_year(self.year)

    def set_absolute_month(self):
        """
        Set the absolute month from the month and year. This is called internally.
        """
        self.abs_month = (self.year * 12) + self.month

    def set_day(self, d):
        """
        Set the day
        :param d: Day
        """
        logger = logging.getLogger("StateMod")
        if (self.behavior_flag & DateTime.DATE_STRICT) != 0:
            if (d > TimeUtil.num_days_in_month(self.month, self.year)) or (d < 1):
                message = "Trying to set invalid day ({}) in DateTime for year {}".format(d, self.year)
                logger.warning(d)
                return
        self.day = d
        self.set_year_day()
        # This has the flaw of not changing the flag when the value is set to 1!
        if self.day != 1:
            self.iszero = False

    def set_hour(self, h):
        """
        Set the hour
        :param h: hour
        """
        logger = logging.getLogger("StateMod")
        if (self.behavior_flag & DateTime.DATE_STRICT) != 0:
            if (h > 23) or (h < 0):
                message = "Trying to set invalid hour ({}) in DateTime.".format(h)
                logger.warning(message)
                return
        self.hour = h
        # This has the flaw of not changing the flag when the value is set to 0!
        if self.hour != 0:
            self.iszero = False

    def set_minute(self, m):
        """
        Set the minute
        :param m: Minute.
        """
        logger = logging.getLogger("StateMod")
        if (self.behavior_flag & DateTime.DATE_STRICT) != 0:
            if (m > 59) or (m < 0):
                message = "Trying to set invalid minute ({}) in DateTime.".format(m)
                logger.warning(m)
                return
        self.minute = m
        # This has the flaw of not changing the flag when the value is set to 0!
        if m != 0:
            self.iszero = False

    def set_month(self, m):
        """
        Set the month
        :param m: Month
        """
        logger = logging.getLogger("StateMod")
        if (self.behavior_flag & DateTime.DATE_STRICT) != 0:
            if (m > 12) or (m < 1):
                message = "Trying to se invalid month ({}) in DateTime.".format(m)
                logger.warning(m)
        self.month = m
        self.set_year_day()
        self.set_absolute_month()
        # This has the flaw of not changing the flag when the value is set to 0!
        if m != 1:
            self.iszero = False

    def set_precision(self, behavior_flag, cumulative=None):
        """
        Set the precision using a bit mask.  The precision can be used to optimize code
        (avoid performing unnecessary checks) and set more intelligent dates.  This
        call automatically truncates unused date fields (sets them to initial values
        as appropriate).  Subsequent calls to getPrecision(), timeOnly(), and
        useTimeZone() will return the separate field values (don't need to handle as a bit mask upon retrieval).
        :param behavior_flag: Full behavior mask containing precision bit (see
        PRECISION_*).  The precision is set when the first valid precision bit
        is found (starting with PRECISION_YEAR).
        :param cumulative: If true, the bit-mask values will be set cumulatively.  If
        false, the values will be reset to defaults and only new values will be set.
        :return: DateTime instance, which allows chained calls.
        """
        # The behavior flag contains the precision (small bits) and higher
        # bit masks. The lower precision values are not unique bit masks.
        # Therefore, get the actual precision value by cutting off the higher
        # values > 100 (the maximum precision value is 70).
        # >precision = behavior_flag - ((behavior_flag/100)*100)
        # Need to remove the effects of the higher order masks...
        if cumulative is None:
            cumulative = True
        behavior_flag_no_precision = behavior_flag
        precision = behavior_flag
        if (behavior_flag & DateTime.DATE_STRICT) != 0:
            behavior_flag_no_precision |= DateTime.DATE_STRICT
            precision ^= DateTime.DATE_STRICT
        if (behavior_flag & DateTime.DATE_FAST) != 0:
            behavior_flag_no_precision |= DateTime.DATE_FAST
            precision ^= DateTime.DATE_FAST
        if (behavior_flag & DateTime.DATE_ZERO) != 0:
            behavior_flag_no_precision |= DateTime.DATE_ZERO
            precision ^= DateTime.DATE_ZERO
        if (behavior_flag & DateTime.DATE_CURRENT) != 0:
            behavior_flag_no_precision |= DateTime.DATE_CURRENT
            precision ^= DateTime.DATE_CURRENT
        if (behavior_flag & DateTime.TIME_ONLY) != 0:
            behavior_flag_no_precision |= DateTime.TIME_ONLY
            precision ^= DateTime.TIME_ONLY
        if (behavior_flag & DateTime.PRECISION_TIME_ZONE) != 0:
            behavior_flag_no_precision |= DateTime.PRECISION_TIME_ZONE
            precision ^= DateTime.PRECISION_TIME_ZONE
        # Now the precision should be what is left...
        if precision == DateTime.PRECISION_YEAR:
            self.month = 1
            self.day = 1
            self.hour = 0
            self.minute = 0
            self.second = 0
            self.hsecond = 0
            self.precision = precision
        if precision == DateTime.PRECISION_MONTH:
            self.day = 1
            self.hour = 0
            self.minute = 0
            self.second = 0
            self.hsecond = 0
            self.precision = precision
        if precision == DateTime.PRECISION_DAY:
            self.hour = 0
            self.minute = 0
            self.second = 0
            self.hsecond = 0
            self.precision = precision
        if precision == DateTime.PRECISION_HOUR:
            self.minute = 0
            self.second = 0
            self.hsecond = 0
            self.precision = precision
        if precision == DateTime.PRECISION_MINUTE:
            self.second = 0
            self.hsecond = 0
            self.precision = precision
        if precision == DateTime.PRECISION_SECOND:
            self.hsecond = 0
            self.precision = precision
        if precision == DateTime.PRECISION_HSECOND:
            self.precision = precision

        # Else do not set _precision - assume that it was set previously (e.g.m in a copy ocnstructor).

        # Time zone is separate and always get set...
        if (behavior_flag & DateTime.PRECISION_TIME_ZONE) != 0:
            self.use_time_zone = True
        elif not cumulative:
            self.use_time_zone = False

        # Time only is separate and always gets set...
        if (behavior_flag & DateTime.TIME_ONLY) != 0:
            self.time_only = True
        elif not cumulative:
            self.time_only = False
        return self

    def set_second(self, s):
        """
        Set the second.
        :param s: Second
        """
        logger = logging.getLogger("StateMod")
        if (self.behavior_flag & DateTime.DATE_STRICT) != 0:
            if s > 59 or s < 0:
                message = "Trying to set invalid second ({}) in DateTime.".format(s)
                logger.warning(message)
        self.second = s
        # This the flaw of not changing the flag when the value is set to 0!
        if s != 0:
            self.iszero = False

    def set_time_zone(self, zone):
        """
        Set the string time zone.  No check is made to verify that it is a valid time zone abbreviation.
        The time zone should normally only be set for DateTime that have a time component.
        For most analytical purposes the time zone should be GMT or a standard zone like MST.
        Time zones that use daylight savings or otherwise change over history or during the year are
        problematic to maintaining continuity.
        The getDate*() methods will consider the time zone if requested.
        :param zone: Time zone abbreviation. If non-null and non-blank, the
        DateTime precision is automatically set so that PRECISION_TIME_ZONE is on.
        If null or blank, PRECISION_TIME_ZONE is off.
        :return: the same DateTime instance, which allows chained calls
        """
        if (zone is None) or (len(zone) == 0):
            self.tz = ""
            self.use_time_zone = False
        else:
            self.use_time_zone = True
            self.tz = zone
        return self

    def set_to_current(self):
        """
        Set to the current date/time.
        The default precision is PRECISION_SECOND and the time zone is set.
        This method is usually only called internally to initialize dates.
        If called externally, the precision should be set separately.
        """
        # First get the current time (construct a new date because this code
        # is not executed that much). If we call this a lot, inline the
        # code rather than constructing...

        date = datetime.datetime.now()
        now = DateTime(d=date)

        # Now set...
        self.hsecond = now.hsecond
        self.second = now.second
        self.minute = now.minute
        self.hour = now.hour
        self.day = now.day
        self.month = now.month
        self.year = now.year
        self.isleap = now.is_leap_year()
        # self.weekday = now.getWeekDay()
        self.yearday = now.get_year_day()
        self.abs_month = now.get_absolute_month()
        self.tz = now.tz
        self.behavior_flag = DateTime.DATE_STRICT
        self.precision = DateTime.PRECISION_SECOND
        self.use_time_zone = False
        self.time_only = False

        # Set the time zone. Use TimeUtil directly to increase performance...
        if TimeUtil.time_zone_lookup_method == TimeUtil.LOOKUP_TIME_ZONE_ONCE:
            if (not TimeUtil.local_time_zone_retrieved):
                # Need to initialize...
                #self.shift_time_zone(TimeUtil.getLocalTimeZoneAbbr())
                pass
            else:
                # Use the existing data...
                self.shift_time_zone(TimeUtil.local_time_zone_string)
        elif TimeUtil.time_zone_lookup_method == TimeUtil.LOOKUP_TIME_ZONE_ALWAYS:
            #self.shift_time_zone(TimeUtil.getLocalTimeZoneAbbr())
            pass
        self.iszero = False

    def set_to_zero(self):
        """
        Set the date/time to all zeros, except day and month are 1.  The time zone is set to "".
        The default precision is PRECISION_SECOND and the time zone is not used.  This
        method is usually only called internally to initialize dates.  If called
        externally, the precision should be set separately.
        """
        self.hsecond = 0
        self.second = 0
        self.minute = 0
        self.hour = 0
        self.day = 1
        self.month = 1
        self.year = 0
        self.isleap = False
        self.weekday = 0
        self.yearday = 0
        self.abs_month = 0
        self.tz = ""
        self.behavior_flag = DateTime.DATE_STRICT
        self.precision = DateTime.PRECISION_SECOND
        self.use_time_zone = False
        self.time_only = False

        # Indicate that the date/time has been zero to zeroes...

        self.iszero = True

    def set_year(self, y):
        """
        Set the year
        :param y: Year
        """
        if (self.behavior_flag & DateTime.DATE_STRICT) != 0:
            # TODO Evaluate whether negative year should be allowed.
            pass
        self.year = y
        self.set_year_day()
        self.set_absolute_month()
        self.isleap = TimeUtil.is_leap_year(self.year)
        if y != 0:
            self.iszero = False

    def set_year_day(self):
        """
        Set the year day from other data.
        The information is set ONLY if the DATE_FAST bit is not set in the behavior mask
        """
        if (self.behavior_flag & DateTime.DATE_FAST) != 0:
            # Want to run fast so don't check...
            return
        i = int()
        # Calculate the year day...
        self.yearday = 0
        # Get the days from the previous months...
        for i in range(self.month):
            self.yearday += TimeUtil.num_days_in_month(i, self.year)
        # Add the days from the current month...
        self.yearday += self.day

    def shift_time_zone(self, zone):
        """
        Shift the data to the specified time zone, resulting in the hours and possibly minutes being changed.
        :param zone: This method shifts the hour/minutes and
        then sets the time zone for the instance to the requested time zone.
        """
        logger = logging.getLogger("StateMod")
        if len(zone) == 0:
            # Just set the time zone to blank to make times timezone-agnostic
            self.set_time_zone("")
        elif zone.upper() == self.tz:
            # The requested time zone is the same as original. Do nothing.
            pass
        # TODO @jurentie 04/26/2019 - port the rest of the code for this function from Java.
        elif zone.startswith("+") or zone.startswith("-"):
            pass
        else:
            # All other time zones
            # Want to change the time zone so compute an offset and apply
            self.set_time_zone(zone)

    def to_string(self, date_format=None):
        """
        TODO smalers 2020-01-04 need to implment.
        :return: formatted string version of DateTime
        """
        if date_format is None:
            # Recursively call after determining format to use
            # Arrange these in probable order of use...
            if self.precision == DateTime.PRECISION_MONTH:
                return self.to_string(DateTime.FORMAT_YYYY_MM)
            elif self.precision == DateTime.PRECISION_DAY:
                return self.to_string(DateTime.FORMAT_YYYY_MM_DD)
        elif date_format == DateTime.FORMAT_YYYY_MM:
            return \
                StringUtil.format_string(self.year, "%04d") + "-" + \
                StringUtil.format_string(self.month, "%02d")
        elif date_format == DateTime.FORMAT_YYYY_MM_DD:
            return \
                StringUtil.format_string(self.year, "%04d") + "-" + \
                StringUtil.format_string(self.month, "%02d") + "-" + \
                StringUtil.format_string(self.day, "%02d")
        elif date_format == DateTime.FORMAT_YYYY_MM_DD_HH_mm:
            # Default output is ISO-8601
            return \
                StringUtil.format_string(self.year, "%04d") + "-" + \
                StringUtil.format_string(self.month, "%02d") + "-" + \
                StringUtil.format_string(self.day, "%02d") + " " + \
                StringUtil.format_string(self.hour, "%02d") + ":" + \
                StringUtil.format_string(self.minute, "%02d")
        else:
            # Assume that hours and minutes but NOT time zone are desired...
            if self.use_time_zone and (len(self.tz) > 0):
                prefix = self.tz[0]
                if (prefix == "-") or (prefix == "+") or self.tz == "Z":
                    return self.to_string(DateTime.FORMAT_ISO_8601)
                else:
                    return self.to_string(DateTime.FORMAT_YYYY_MM_DD_HH_mm_ZZZ)
            else:
                return self.to_string(DateTime.FORMAT_YYYY_MM_DD_HH_mm)
