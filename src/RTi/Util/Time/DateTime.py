# DateTime - general Date/Time class

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
# DateTime - general Date/Time class
# ----------------------------------------------------------------------------
# History:
#
# May 96	Steven A. Malers, RTi	Start developing the class based on the
#					HMData HMTimeData structure.
# 24 Jan 97	Matthew J. Rutherford, 	Added TSDATE_STRICT, and TSDATE_FAST
#		RTi.			to help with speed issues brought
#					about by the reset function.
# 11 Mar 97	MJR, RTi		Put in cast to char* for use in print
#					statements. Couldn't figure out how
#					the syntax for defining the operator
#					so I had to inline it.
# 21 May 1997	MJR, RTi		Put in operator= (char*) to handle
#					string to date conversions.
# 16 Jun 1997	MJR, RTi		Added string as private member to
#					be used on (char*) cast.
# 05 Jan 1998	SAM, RTi		Update to be consistent with C++.
#					Remove unused code.
# 04 Mar 1998	SAM, RTi		Change *absMonth* routines to
#					*absoluteMonth*.  Depricate the old.
# 28 Apr 1998 	DLG, RTi		Added
#					FORMAT_MM_SLASH_DD_SLASH_YYYY_HH_mm
#					for toString.
# 29 Apr 1998	SAM, RTi		Add parse().  Add _precision and
#					set/get routines.  Also add to behavior
#					mask so we can construct.  Add zero
#					case checks to the add routines.
#					Really do something with DATE_FAST.
# 08 Jun 1998	CEN, RTi		Add isDate().
# 09 Jun 1998 	CEN, RTi		Added FORMAT_MM_SLASH_YYYY
# 22 Jun 1998	SAM, RTi		Add subtract to get an offset and
#					overload add to take a TSDate.
# 26 Jun 1998	SAM, RTi		When constructing from a TSDate, also
#					set the precision flag.
# 13 Jul 1998	SAM, RTi		Port C++ parse ( String ) code to Java
#					to generically handle date parsing.
# 27 Jul 1998	SAM, RTi		Add DATE_CURRENT behavior flag to
#					bring in line with C++ behavior.  At
#					some convenient point in the future,
#					make DATE_ZERO the default.
# 02 Sep 1998	SAM, RTi		Added FORMAT_MM_SLASH_YYYY to parse and
#					fix bug in DD/YY parse.
# 15 Oct 1998	SAM, RTi		Change the time zone to MST for default
#					conversion of local time.  Hopefully
#					we will go to Java 1.2 soon and that
#					problem will go away.
# 25 Nov 1998	SAM, RTi		Add constructor to take Date and flag
#					so precision can be set.  Add
#					getBehaviorFlag so that the DMI package
#					can use to set precision on query date
#					strings.
# 02 Jan 1998	SAM, RTi		Overload isDate to take any string.
# 06 Jan 1998	SAM, RTi		Use StringUtil.atoi to do some date
#					conversions to avoid problems with
#					spaces.  Change the TSDate constructor
#					that takes a double to call the
#					TimeUtil.getMonthAndDayFromDayOfYear to
#					pass the year to be more robust.
#					Change the init routines to
#					setToZero and setToCurrent and make
#					public to make useful (e.g., in
#					iterations).  Also make it a little
#					clearer how to switch the defaults (want
#					zero to be default in future).
# 12 Apr 1999	SAM, RTi		Add finalize.  Add
#					FORMAT_YYYY_MM_DD_HH_mm_SS_ZZZ to
#					toString().
# 29 Apr 1999	SAM, RTi		Update the time zone code now that
#					Java 1.2 retrieves a local time zone
#					correctly.  TimeUtil will also have
#					similar code but for performance also
#					have here.  Add getLocalTimeZoneAbbr()
#					to support shifts of database data.
# 30 May 2000	SAM, RTi		Update to call reset() in constructors
#					so absolute date, etc., will be set.
# 12 Oct 2000	SAM, RTi		Add setDate() to assign one date to
#					another without allocating a new date.
# 23 Nov 2000	SAM, RTi		Add FORMAT_HHmm and FORMAT_HH_mm to
#					support plots.  Previously updated to
#					change hour 24 to hour 0 of the next day
#					to agree with C++ version.
#					Add FORMAT_MM_SLASH_DD_SLASH_YYYY_HH.
# 20 Dec 2000	SAM, RTi		Add FORMAT_YYYYMMDDHHmm to agree with
#					C++.
# 20 Mar 2001	SAM, RTi		Add a little more smarts to the subtract
#					method to get it to perform better.
#					Fix bug where TSDate(TSDate,int)
#					constructor was not correctly setting
#					the precision.
# 11 Apr 2001	SAM, RTi		Add MM_DD_YYYY_HH format to better
#					support Excel, Access.
# 18 May 2001	SAM, RTi		Add setPrecision ( TS ) to simplify
#					interval handling.
# 31 May 2001	SAM, RTi		Change toDouble() to check precision so
#					that accidental remainder junk is not
#					used.  Change so that the copy
#					constructor that takes a date and a
#					flag checks the precision during the
#					copy and ignores unneeded information.
# 01 Aug 2001	SAM, RTi		Add FORMAT_NONE, FORMAT_AUTOMATIC, and
#					FORMAT_MM to be consistent with C++.
# 28 Aug 2001	SAM, RTi		Implement clone().  A copy constructor
#					is already implemented but clone() is
#					used by TS and might be preferred by
#					some developers.  Delete all the old
#					C++/C style documentation and fold into
#					the javadoc.  Remove debug information
#					where no longer needed.  Enable
#					addInterval() to handle week as multiple
#					of 7 days, in case it ever is needed.
# 06 Sep 2001	SAM, RTi		Fix so isDate() returns false if a null
#					date on parse.
# 2001-11-06	SAM, RTi		Review javadoc.  Verify that veriables
#					are set to null when no longer used.
#					Change all the add and set methods to
#					have a void return type, consistent with
#					C++ code.  Fix getNumIntervals() to use
#					a local copy of a TSDate for iteration -
#					previously the start date was modified
#					in the method.
# 2001-11-20	SAM, RTi		Add FORMAT_YYYY_MM_DD_HH_ZZZ to better
#					handle real-time data.  The parse() and
#					toString() methods will automatically
#					handle hour dates with a time zone,
#					regardless of the precision.
# ===============
# 2001-12-13	SAM, RTi		Copy the TSDate class and modify to
#					make generic.  Assume some of the C++
#					conventions, like making the default
#					initialization be to a zero date.
#					Move the following to TimeUtil:
#						getDateFromIndex()
#						getLocalTimeZoneAbbr()
#						getNumIntervals()
#					Use TimeUtil.getLocalTimeZone().
#					Add a _use_time_zone data member to
#					handle time zone separately from the
#					other parts of the precision.
#					Add FORMAT_YYYY_MM_DD_HH_mm_ZZZ to
#					parse and toString().
# 2001-12-19	SAM, RTi		Update to use new TZ class.  Add method
#					isZero() to indicate whether the
#					DateTime has been initialized to zero
#					but has had no changes since then.
#					Change to only store the time zone
#					abbreviation, especially since time zone
#					shifts in minutes is now the standard.
#					Change getLeapFlag() to isLeapYear().
#					Move subtract() to TimeUtil.diff() since
#					it is more of a utility and does not
#					operate on the instance.
# 2001-12-27	SAM, RTi		Changed fixedRead() calls to new
#					standard - blank fields are not
#					returned.  Hopefully this increases
#					performance some.
# 2002-01-16	SAM, RTi		Fix bug where _behavior_flag is not
#					being disagreggated correctly.
#					Fix some places where result of & was
#					being compared to 1 rather than != 0.
# 2002-07-05	SAM, RTi		Add setDate() to allow a DateTime to be
#					set using a Date.  This increates
#					performance (e.g., when iterating using
#					dates from a database record).
# 2003-01-27	SAM, RTi		Fix bug in behavior of the comareTo()
#					method.
# 2003-11-03	SAM, RTi		When creating a zero DateTime,
#					initialize the time zone to an empty
#					String.  Previously, it was getting set
#					to the local computer time zone, which
#					causes unexpected results.
# 2004-01-19	J. Thomas Sapienza, RTi	Added check in the DateTime(Date)
#					constructor for null dates.
# 2004-03-01	SAM, RTi		Fix bug where parsing an hour of 24 was
#					setting the day to 1, not day + 1.
# 2004-03-04	JTS, RTi		Class is now serializable.
# 2004-03-12	SAM, RTi		Add support for parsing permutations of
#					M/D/YYYY, M/DD/YYYY, MM/D/YYYY,
#					MM/DD/YYYY for daily precision dates.
#					This involved overloading parse() to
#					take an additional flag in the private
#					method.  The original public method is
#					still available.  Additional work may
#					be needed if non-USA standard dates are
#					also parsed.  The preference is still to
#					use ISO standard formats.
# 2004-04-05	SAM, RTi		Fix a bug in setPrecision() where if the
#					flag does not contain precision
#					information, the precision was
#					defaulting to IRREGULAR.
# 2004-04-06	SAM, RTi		Fix a bug in setSecond() where check for
#					_iszero was against 1 - it is now
#					changed to check against 0.
# 2004-04-14	SAM, RTi		* Overload setPrecision() to have a flag
#					  indicating whether the set should be
#					  cumulative or a reset.  This resolves
#					  problems where, for example, a date is
#					  parsed with time zone and later the
#					  precision is set, ignoring the time
#					  zone flag.  The change can now be
#					  cumulative so the previous settings
#					  are not totally reset.
#					* Change setTimeZone() to set the
#					  _use_time_zone flag to true.
#					* Fix setDate() since it was treating
#					  _precision as a bit mask and not a
#					  simple integer.
#					* When constructing from a Date, do NOT
#					  set the time zone unless the behavior
#					  flags asks for the time zone.
#					* When setting to current time, DO use
#					  the time zone (will be ignored in code
#					  if daily or courser precision).
# 2004-04-27	SAM, RTi		* Change parse for FORMAT_MM_SLASH_YYYY
#					  to handle 1-digit month without using
#					  StringTokenizer.
# 2004-10-21	JTS, RTi		Added FORMAT_DD_SLASH_MM_SLASH_YYYY.
# 2004-10-27	JTS, RTi		Class now implements Comparable so that
#					it can easily be sorted using the
#					Collections.sort() method.
# 2005-02-23	SAM, RTi		Overload lessThan(),
#					lessThanOrEqualTo(), greaterThan(), and
#					greaterThanOrEqualTo() to take a
#					precision, to facilitate processing of
#					data with different precision.  So as to
#					not reduce performance, inline the code
#					rather than having one method call the
#					other (these methods are used
#					extensively when iterating).
# 2005-09-01	SAM, RTi		parse() was not throwing exceptions in
#					all cases if a string did not match a
#					criteria.  Add the exception.
# 2005-12-14	SAM, RTi		Overload parse() to recognize DateTime
#					expressions.
# 2006-04-16	SAM, RTi		Throw an exception if a date/time string
#					length is not recognized in parsing.
# 2006-04-20	JTS, RTi		Added subtractInterval().
# 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
# 2012-04-20   HSK, RTi        Added equals(Object) and hashCode overrides.
# ----------------------------------------------------------------------------
# EndHeader

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
        a call to setTimeZone(), then the time zone is intended to be used
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

    def __init__(self, flag=None, date=None, dateTime=None):

        logger = logging.getLogger("StateMod")

        # Hundredths of a second (0-99)
        self.__hsecond = int()

        # Seconds (0-59)
        self.__second = int()

        # Minutes past hour (0-59)
        self.__minute = int()

        # Hours past midnight (0-23).  Important - hour 24 in data should be handled as
        # hour 0 of the next day.
        self.__hour = int()

        # Day of month (1-31)
        self.__day = int()

        # Month (1-12)
        self.__month = int()

        # Year (4 digit).
        self.__year = int()

        # Time zone abbreviation
        self.__tz = str()

        # Indicate whether the year a leap year (true) or not (false).
        self.__isleap = bool()

        # Is the DateTime initialized to zero without further changes?
        self.__iszero = bool()

        # Day of week (0=Sunday). Will be calculated in getWeekDay(0.
        self.__weekday = -1

        # Day of year (0-356).
        self.__yearday = int()

        # Absolute month (year*12 + month)
        self.__abs_month = int()

        # Precision of the DateTime (allows some optimization and automatic
        # decisions when converting). This is the PRECISION_* value only
        # (not a bit mask).  _use_time_zone and _time_only control other precision information.
        self.__precision = int()

        # Flag for special behavior of dates.  Internally this contains all the
        # behavior flags but for the most part it is only used for ZERO/CURRENT and FAST/STRICT checks.
        self.__behavior_flag = int()

        # Indicates whether the time zone should be used when processing the DateTime.
        # SetTimeZone() will set to true if the time zone is not empty, false if empty.
        # Setting the precision can override this if time zone flag is set.
        self.__use_time_zone = False

        # Use only times for the DateTime.
        self.__time_only = False

        if flag is not None:
            self.initialize_DateTime_Flag(flag)
        elif date is not None:
            self.initialize_DateTime_Date(date)
        elif dateTime is not None:
            self.initialize_DateTime_DateTime(dateTime)

    def addMonth(self, add):
        """
        Add month(s) to the DateTime.  Other fields will be adjusted if necessary.
        :param add: Indicates the number of months to add (can be a multiple and can be negative).
        """
        i = int()

        if add == 0:
            return
        if add == 1:
            # Dealing with one month...
            self.__month += add
            # Have added one month so check if went into the next year
            if self.__month > 12:
                # Have gone into the next year...
                self.__month = 1
                self.addYear(1)
        # Else...
        # Loop through the number to add/subtract...
        # Use recursion because multi-month increments are infrequent
        # and the overhead of the multi-month checks is probably a wash.
        elif add > 0:
            for i in range(add):
                self.addMonth(1)
            # No need to reset because it was done in the previous call.
            return
        elif add == -1:
            self.__month -= 1
            # Have subtracted the specified number so check if in the previous year
            if self.__month < 1:
                # Have gone into the previous year...
                self.__month = 12
                self.addYear(-1)
        elif add < 0:
            for i in range(add, -1, -1):
                self.addMonth(-1)
            # No need to reset because it was done in the previous call.
            return
        else:
            # Zero...
            return
        # Reset time
        self.setAbsoluteMonth()
        self.setYearDay()
        self.__iszero = False

    def addYear(self, add):
        """
        Add year(s) to the DateTime.  The month and day are NOT adjusted if an
        inconsistency occurs with leap year information.
        :param add: Indicates the number of years to add (can be a multiple and can be negative).
        """
        self.__year += add
        self.reset()
        self.__iszero = False

    def addDay(self, add):
        """
        Add day(s) to the DateTime.  Other fields will be adjusted if necessary.
        :param add: Indicates the number of days to add (can be multiple and can be negative)
        """
        i = int()

        if add == 1:
            num_days_in_month = TimeUtil.numDaysInMonth(self.__month, self.__year)
            self.__day += 1
            if self.__day > num_days_in_month:
                # Have gone into the next month...
                self.__day -= num_days_in_month
                self.addMonth(1)
            # Reset the private data members.
            self.setYearDay()
        # Else...
        # Figure out if we are trying to add more than one day.
        # If so, recurse (might be a faster way, but this works)...
        elif add > 0:
            for i in range(add):
                self.addDay(1)
        elif add == -1:
            self.__day -= 1
            if self.__day < 1:
                # Have gone into the previous month...
                # Temporarily set day to 1, determine the day and year, and then set the day
                self.__day = 1
                self.addMonth(-1)
                self.__day = TimeUtil.numDaysInMonth(self.__month, self.__year)
            # Reset the private data members.
            self.setYearDay()
        elif add < 0:
            i = add
            while i < 0:
                self.addDay(-1)
                i += 1
        self.__iszero = False

    def getAbsoluteMonth(self):
        """
        Return the absolute month.
        :return: The absolute month (year*12 + month).
        """
        # since some data are public, recompute...
        return (self.__year * 12 + self.__month)

    def getDay(self):
        """
        Return the day
        :return: The day.
        """
        return self.__day

    def getMonth(self):
        """
        Return the month
        :return: The month
        """
        return self.__month

    def getYear(self):
        """
        Return the year
        :return: The year.
        """
        return self.__year

    def getYearDay(self):
        """
        Return the Julian day in the year.
        :return: The day of the year where Jan 1 is 1. If the behavior of the DateTime
        is DATE_FAST, zero is likely to be returned because the day of the year is not
        automatically recomputed.
        """
        # Need to set it...
        self.setYearDay()
        return self.__yearday

    def greaterThan(self, t):
        """
        Determine if the instance is greater than another date.  Time zone is not
        considered in the comparison (no time zone shift is made).  The comparison is
        made at the precision of the instance.
        :param t: DateTime to compare.
        :return: True if the instance is greater than the given date.
        """
        if not self.__time_only:
            if self.__year < t.__year:
                return False
            else:
                if self.__year > t.__year:
                    return True

            if self.__precision == DateTime.PRECISION_YEAR:
                # Equal so return false...
                return False

            # otherwise years are equal so check months
            if self.__month < t.__month:
                return False
            else:
                if self.__month > t.__month:
                    return True

            if self.__precision == DateTime.PRECISION_MONTH:
                # Equal so return false...
                return False

            # months must be equal so check day

            if self.__day < t.__day:
                return False
            else:
                if self.__day > t.__day:
                    return True

            if self.__precision == DateTime.PRECISION_DAY:
                # Equal so return false...
                return False

        # days are equal so check hour

        if self.__hour < t.__hour:
            return False
        else:
            if self.__hour > t.__hour:
                return True

        if self.__precision == DateTime.PRECISION_HOUR:
            # Equal so return false...
            return False

        # means that hours match - so check minute

        if self.__minute < t.__minute:
            return False
        else:
            if self.__minute > t.__minute:
                return True

        if self.__precision == DateTime.PRECISION_MINUTE:
            # Equal so return false..
            return False

        # means that seconds match - so check hundredths of seconds

        if self.__hsecond < t.__hsecond:
            return False
        else:
            if self.__hsecond > t.__hsecond:
                return True

        # means the are equal
        return False


    # def getWeekDay(self):
    #     """
    #     Return the week day by returning getDate(TimeZoneDefaultType.GMT).getDay()
    #     :return: The weekday (sunday is 0)
    #     """
    #     # Always recompute because don't know if DateTime was copied and modified.
    #     # Does not matter what timezone because internal date/time values
    #     # are used in absolute sense.
    #     #self.__weekday = self.getDate(TimeZoneDefault.GMT).getDay()
    #     self.__weekday = self.getDate("GMT").getDay()
    #     return self.__weekday

    def initialize_DateTime_Flag(self, flag):
        """
        Construct using the constructor modifiers (combination of PRECISION_*,
        DATE_CURRENT, DATE_ZERO, DATE_STRICT, DATE_FAST).  If no modifiers are given,
        the date/time is initialized to zeros and precision is PRECISION_MINUTE.
        :param flag: Constructor modifier
        """
        if (flag & DateTime.DATE_CURRENT) != 0:
            self.setToCurrent()
        else:
            # Default
            self.setToZero()

        self.__behavior_flag = flag
        self.setPrecision(flag)
        self.reset()

    def initialize_DateTime_Date(self, d):
        """
        Construct from a Python datetime.  The time zone is not set - use the overloaded method if necessary.
        :param d: Python datetime.
        """
        if d is None:
            self.setToZero()
            self.reset()
            return
        # Use deprecated indicates whether to use the deprecated Date
        # functions. These should be fast (no strings) but are, of course, deprecated.
        use_deprecated = True

        if use_deprecated:
            # Returns the number of years since 1900
            year = d.year
            self.setYear()
            # Month between 1-12
            self.setMonth(d.month)
            # Day between 1 and the number of days in the given month of the given year.
            self.setDay(d.day)
            self.setPrecision(DateTime.PRECISION_DAY)
            # Sometimes Dates are instantiated from data where hours, etc.
            # are not available (e.g., from a database date/time).
            # Therefore catch exceptions at each step...
            try:
                # Returned hours are 0-23
                self.setHour(d.hour)
                self.setPrecision(DateTime.PRECISION_HOUR)
            except Exception as e:
                # Don't do anything. Just leave the DateTime default.
                pass
            try:
                # Return minute is in 0 to 59
                self.setMinute(d.minute)
                self.setPrecision(DateTime.PRECISION_MINUTE)
            except Exception as e:
                # Don't do anything. Just leave the DateTime default
                pass
            try:
                # Returned seconds is 0 to 59
                self.setSecond(d.second)
                self.setPrecision(DateTime.PRECISION_SECOND)
            except Exception as e:
                # Don't do anything. Just leave the DateTime default.
                pass
            self.__tz = ""

        else:
            # Date/Calendar are ugly to work with, let's get information by formatting strings...

            # year month
            # Use the formatTimeString routine instead of the following...
            # String format = "yyy M d H m s S"
            # time_date = TimeUtil.getTimeString(d, format)
            format = "%Y %m %d %H %M %S"
            list = StringUtil.breakStringList(str(d), " ", StringUtil.DELIM_SKIP_BLANKS)

    def initialize_DateTime_DateTime(self, t):
        """
        Copy constructor. If the incoming date is None, the date will be initialized
        to zero information.
        :param t: DateTime to copy
        """
        logger = logging.getLogger("StateMod")
        if t is not None:
            self.__hsecond = t.__hsecond
            self.__second = t.__second
            self.__minute = t.__minute
            self.__hour = t.__hour
            self.__day = t.__day
            self.__month = t.__month
            self.__year = t.__year
            self.__isleap = t.__isleap
            self.__weekday = t.__weekday
            self.__yearday = t.__yearday
            self.__abs_month = t.__abs_month
            self.__behavior_flag = t.__behavior_flag
            self.__precision = t.__precision
            self.__use_time_zone = t.__use_time_zone
            self.__time_only = t.__time_only
            self.__iszero = t.__iszero
            self.__tz = t.__tz
        else:
            # Constructing from a None usually means that there is a code
            # logic problem with exception handling...
            logger.warning("Constructing DateTime from None - will have zero date!")
            self.setToZero()
        self.reset()

    def isLeapYear(self):
        """
        Indicate whether a leap year.
        :return: True if a leap year
        """
        # Reset to make sure...
        self.__isleap = TimeUtil.isLeapYear(self.__year)
        return self.__isleap

    def lessThan(self, t):
        """
        Determine if the DateTime is less than another DateTime.  Time zone is not
        considered in the comparison (no time zone shift is made).  The precision of the
        instance is used for the comparison.
        :param date: DateTime to compare
        :return: True if the instance is less than the given DateTime.
        """
        if not self.__time_only:
            if self.__year < t.__year:
                return True
            else:
                if self.__year > t.__year:
                    return False

            if self.__precision == DateTime.PRECISION_YEAR:
                # Equal so return false...
                return False

            # otherwise years are equal so check months
            if self.__month < t.__month:
                return True
            else:
                if self.__month > t.__month:
                    return False

            if self.__precision == DateTime.PRECISION_MONTH:
                # Equal so return false...
                return False

            # months must be equal so check day

            if self.__day < t.__day:
                return True
            else:
                if self.__day > t.__day:
                    return False

            if self.__precision == DateTime.PRECISION_DAY:
                # Equal so return false...
                return False

        # days are equal so check hour

        if self.__hour < t.__hour:
            return True
        else:
            if self.__hour > t.__hour:
                return False

        if self.__precision == DateTime.PRECISION_HOUR:
            # Equal so return false...
            return False

        # means that hours match - so check minute

        if self.__minute < t.__minute:
            return True
        else:
            if self.__minute > t.__minute:
                return False

        if self.__precision == DateTime.PRECISION_MINUTE:
            # Equal so return false..
            return False

        # means that seconds match - so check hundredths of seconds

        if self.__hsecond < t.__hsecond:
            return True
        else:
            if self.__hsecond > t.__hsecond:
                return False

        # means the are equal
        return False
    def reset(self):
        """
        Reset the derived data (year day, absolute month, and leap year).  This is
        normally called by other DateTime functions but can be called externally if
        data are set manually.
        """
        # Always reset the absolute month since it is cheap...
        self.setAbsoluteMonth()
        if (self.__behavior_flag & DateTime.DATE_FAST) != 0:
            # Want to run fast so don't check...
            return
        self.setYearDay()
        self.__isleap = TimeUtil.isLeapYear(self.__year)

    def setAbsoluteMonth(self):
        """
        Set the absolute month from the month and year. This is called internally.
        """
        self.__abs_month = (self.__year * 12) + self.__month

    def setDay(self, d):
        """
        Set the day
        :param day: Day
        """
        logger = logging.getLogger("StateMod")
        if (self.__behavior_flag & DateTime.DATE_STRICT) != 0:
            if (d > TimeUtil.numDaysInMonth(self.__month, self.__year)) or (d < 1):
                message = "Trying to set invalid day ({}) in DateTime for year {}".format(d, self.__year)
                logger.warning(d)
                return
        self.__day = d
        self.setYearDay()
        # This has the flaw of not changing the flag when the value is set to 1!
        if self.__day != 1:
            self.__iszero = False

    def setHour(self, h):
        """
        Set the hour
        :param h: hour
        """
        logger = logging.getLogger("StateMod")
        if (self.__behavior_flag & DateTime.DATE_STRICT) != 0:
            if (h > 23) or (h < 0):
                message = "Trying to set invalid hour ({}) in DateTime.".format(h)
                logger.warning(message)
                return
        self.__hour = h
        # This has the flaw of not changing the flag when the value is set to 0!
        if self.__hour != 0:
            self.__iszero = False

    def setMinute(self, m):
        """
        Set the minute
        :param m: Minute.
        """
        logger = logging.getLogger("StateMod")
        if (self.__behavior_flag & DateTime.DATE_STRICT) != 0:
            if (m > 59) or (m < 0):
                message = "Trying to set invalid minute ({}) in DateTime.".format(m)
                logger.warning(m)
                return
        self.__minute = m
        # This has the flaw of not changing the flag when the value is set to 0!
        if m != 0:
            self.__iszero = False

    def setMonth(self, m):
        """
        Set the month
        :param m: Month
        """
        logger = logging.getLogger("StateMod")
        if (self.__behavior_flag & DateTime.DATE_STRICT) != 0:
            if (m > 12) or (m < 1):
                message = "Trying to se invalid month ({}) in DateTime.".format(m)
                logger.warning(m)
        self.__month = m
        self.setYearDay()
        self.setAbsoluteMonth()
        # This has the flaw of not changing the flag when the value is set to 0!
        if m != 1:
            self.__iszero = False

    def setPrecision(self, behavior_flag, cumulative=None):
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
            self.__month = 1
            self.__day = 1
            self.__hour = 0
            self.__minute = 0
            self.__second = 0
            self.__hsecond = 0
            self.__precision = precision
        if precision == DateTime.PRECISION_MONTH:
            self.__day = 1
            self.__hour = 0
            self.__minute = 0
            self.__second = 0
            self.__hsecond = 0
            self.__precision = precision
        if precision == DateTime.PRECISION_DAY:
            self.__hour = 0
            self.__minute = 0
            self.__second = 0
            self.__hsecond = 0
            self.__precision = precision
        if precision == DateTime.PRECISION_HOUR:
            self.__minute = 0
            self.__second = 0
            self.__hsecond = 0
            self.__precision = precision
        if precision == DateTime.PRECISION_MINUTE:
            self.__second = 0
            self.__hsecond = 0
            self.__precision = precision
        if precision == DateTime.PRECISION_SECOND:
            self.__hsecond = 0
            self.__precision = precision
        if precision == DateTime.PRECISION_HSECOND:
            self.__precision = precision

        # Else do not set _precision - assume that it was set previously (e.g.m in a copy ocnstructor).

        # Time zone is separate and always get set...
        if (behavior_flag & DateTime.PRECISION_TIME_ZONE) != 0:
            self.__use_time_zone = True
        elif not cumulative:
            self.__use_time_zone = False

        # Time only is separate and always gets set...
        if (behavior_flag & DateTime.TIME_ONLY) != 0:
            self.__time_only = True
        elif not cumulative:
            self.__time_only = False
        return self

    def setSecond(self, s):
        """
        Set the second.
        :param s: Second
        """
        logger = logging.getLogger("StateMod")
        if (self.__behavior_flag & DateTime.DATE_STRICT) != 0:
            if s > 59 or s < 0:
                message = "Trying to set invalid second ({}) in DateTime.".format(s)
                logger.warning(message)
        self.__second = s
        # This the flaw of not changing the flag when the value is set to 0!
        if s != 0:
            self.__iszero = False

    def setTimeZone(self, zone):
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
            self.__tz = ""
            self.__use_time_zone = False
        else:
            self.__use_time_zone = True
            self.__tz = zone
        return self

    def setToCurrent(self):
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
        self.__hsecond = now.__hsecond
        self.__second = now.__second
        self.__minute = now.__minute
        self.__hour = now.__hour
        self.__day = now.__day
        self.__month = now.__month
        self.__year = now.__year
        self.__isleap = now.isLeapYear()
        # self.__weekday = now.getWeekDay()
        self.__yearday = now.getYearDay()
        self.__abs_month = now.getAbsoluteMonth()
        self.__tz = now.__tz
        self.__behavior_flag = DateTime.DATE_STRICT
        self.__precision = DateTime.PRECISION_SECOND
        self.__use_time_zone = False
        self.__time_only = False

        # Set the time zone. Use TimeUtil directly to increase performance...
        if TimeUtil._time_zone_lookup_method == TimeUtil.LOOKUP_TIME_ZONE_ONCE:
            if (not TimeUtil._local_time_zone_retrieved):
                # Need to initialize...
                #self.shiftTimeZone(TimeUtil.getLocalTimeZoneAbbr())
                pass
            else:
                # Use the existing data...
                self.shiftTimeZone(TimeUtil._local_time_zone_string)
        elif TimeUtil._time_zone_lookup_method == TimeUtil.LOOKUP_TIME_ZONE_ALWAYS:
            #self.shiftTimeZone(TimeUtil.getLocalTimeZoneAbbr())
            pass
        self.__iszero = False

    def setToZero(self):
        """
        Set the date/time to all zeros, except day and month are 1.  The time zone is set to "".
        The default precision is PRECISION_SECOND and the time zone is not used.  This
        method is usually only called internally to initialize dates.  If called
        externally, the precision should be set separately.
        """
        self.__hsecond = 0
        self.__second = 0
        self.__minute = 0
        self.__hour = 0
        self.__day = 1
        self.__month = 1
        self.__year = 0
        self.__isleap = False
        self.__weekday = 0
        self.__yearday = 0
        self.__abs_month = 0
        self.__tz = ""
        self.__behavior_flag = DateTime.DATE_STRICT
        self.__precision = DateTime.PRECISION_SECOND
        self.__use_time_zone = False
        self.__time_only = False

        # Indicate that the date/time has been zero to zeroes...

        self.__iszero = True

    def setYear(self, y):
        """
        Set the year
        :param y: Year
        """
        if (self.__behavior_flag & DateTime.DATE_STRICT) != 0:
            # TODO Evaluate whether negative year should be allowed.
            pass
        self.__year = y
        self.setYearDay()
        self.setAbsoluteMonth()
        self.__isleap = TimeUtil.isLeapYear(self.__year)
        if y != 0:
            self.__iszero = False

    def setYearDay(self):
        """
        Set the year day from other data.
        The information is set ONLY if the DATE_FAST bit is not set in the behavior mask
        """
        if (self.__behavior_flag & DateTime.DATE_FAST) != 0:
            # Want to run fast so don't check...
            return
        i = int()
        # Calculate the year day...
        self.__yearday = 0
        # Get the days from the previous months...
        for i in range(self.__month):
            self.__yearday += TimeUtil.numDaysInMonth(i, self.__year)
        # Add the days from the current month...
        self.__yearday += self.__day

    def shiftTimeZone(self, zone):
        """
        Shift the data to the specified time zone, resulting in the hours and possibly minutes being changed.
        :param zone: This method shifts the hour/minutes and
        then sets the time zone for the instance to the requested time zone.
        """
        logger = logging.getLogger("StateMod")
        if len(zone) == 0:
            # Just set the time zone to blank to make times timezone-agnostic
            self.setTimeZone("")
        elif zone.upper() == self.__tz:
            # The requested time zone is the same as original. Do nothing.
            pass
        # TODO @jurentie 04/26/2019 - port the rest of the code for this function from Java.
        elif zone.startswith("+") or zone.startswith("-"):
            pass
        else:
            # All other time zones
            # Want to change the time zone so compute an offset and apply
            self.setTimeZone(zone)
