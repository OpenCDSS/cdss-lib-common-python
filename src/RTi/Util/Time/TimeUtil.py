# TimeUtil - date/time utility data and methods

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
# TimeUtil - date/time utility data and methods
# ----------------------------------------------------------------------------
# History:
#
# 05 Jan 1998	Steven A. Malers,	Start getting documentation in order.
#		Riverside Technology,	Move TSDate.computeDayOfWeek to
#		inc.			TimeUtil.getCurrentDayOfWeek.
# 04 Mar 1998	SAM, RTi		Add overload for numDaysInMonths.
# 14 Mar 1998	SAM, RTi		Add javadoc.
# 08 May 1998  DLG, RTi		Added setLocalTimeZone functions.
# 15 May 1998  DLG, RTi		Fixed bug in isValidMinute, isValidHour
#					to restrict the range to 0-59 and 0-23
#					respectively.
# 21 Jun 1998	SAM, RTi		Add getDayAndMonthFromYearDay.
# 23 Jun 1998	SAM, RTi		Remove dependence on TS by adding time
#					zone information here.  Just copy the
#					TSTimeZone.getDefinedCode function to
#					here.
# 30 Jun 1998	SAM, RTi		Add getAbsoluteDay.
# 12 Jan 1999	SAM, RTi		Deprecate the old version of
#					getMonthAndDayFromDayOfYear and
#					replace with a more robust version.
# 28 Mar 2001	SAM, RTi		Change getAbsoluteDay() to
#					absoluteDay().  Add absoluteMinute().
#					Get rid of * imports.
# 08 Jul 2001	SAM, RTi		Add irrigation*FromCalendar() and
#					water*FromCalendar() methods.  Although
#					these are not generic to all code, they
#					are common enough in what RTi does to
#					put here.
# 22 Aug 2001	SAM, RTi		Add waitForFile().
# 2001-12-13	SAM, RTi		Add formatDateTime().  Transfer the
#					following from DateTime:
#						getDateTimeFromIndex()
#						getLocalTimeZone()
#						getNumIntervals()
#						isDateTime()
#					Use TZ and TZData instead of
#					TimeZoneData.
#					Verify that variables are set to null
#					when no longer used.  Change
#					getSystemTimeString() to use
#					formatDateTime().
#					Remove deprecated getTimeString(),
#					getAbsoluteMonth(), getDefinedCode().
#					Change setLocalTimeZone() to set the
#					same data used by
#					getLocalTimeZoneAbbr().
#					Add subtract() from DateTime.
#					Change %Z when dealing with dates to
#					use the TimeZone.getID() rather than
#					look up from a GMT offset (too
#					complicated).
# 2002-02-02	SAM, RTi		Change getDateFromIndex() to
#					addIntervals().
# 2002-05-21	SAM, RTi		Update formatDateTime() to pass through
#					unrecognized %X format specifiers so
#					that the string can be formatted in a
#					secondary formatter.
#					Add getDateTimeFormatSpecifiers().
# 2003-02-20	SAM, RTi		Fix numDaysInMonth(), which was not
#					checking for month 0 properly.
# 2003-06-03	SAM, RTi		Change diff() methods to be static.
# 2003-09-19	SAM, RTi		* formatDateTime() was not handling day
#					  of week abbreviations - was returning
#					  full day.
#					* Update formatDateTime() to use
#					  GregorianCalendar.
# 2003-10-10	SAM, RTi		* Add numDaysInMonth(DateTime).
# 2003-12-08	SAM, RTi		* Add dayOfYear(DateTime).
# 2005-02-24	SAM, RTi		Add highestPrecision() and
#					lowestPrecision().
# 2005-09-27	SAM, RTi		* Add max() and min() to simplify
#					  handling of DateTime comparisons.
#					* Change warning levels from 2 to 3 to
#					  facilitate use of the log file viewer.
# 2005-11-16	SAM, RTi		* Add
#					  convertCalendarMonthToCustomMonth().
# 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
# ----------------------------------------------------------------------------
# EndHeader

import logging

from abc import ABC, abstractmethod


class TimeUtil(ABC):
    """
    The TimeUtil class provides time utility methods for date/time data, independent
    of use in time series or other classes.  There is no "Time" or "Date" class
    other than what is supplied by Java or RTi's DateTime class (TSDate is being
    phased out).  Conventions used for all methods are:
    <p>
    Years are 4-digit.<br>
    Months are 1-12.<br>
    Days are 1-31.<br>
    Hours are 0-23.<br>
    Minutes are 0-59.<br>
    Seconds are 0-59.<br>
    HSeconds are 0-99.<br>
    """

    # Datum for absolute day = days inclusive of Dec 31, 1799.
    # This has been computed by looping through years 1-1799 adding numDaysInYear.
    # This constant can be used when computing absolute days (e.g., to calculate the
    # number of days in a period).
    ABSOLUTE_DAY_DATUM = 657071

    # The following indicates how time zones are handled when getLocalTimeZone() is
    # called (which is used when DateTime instances are created).  The default is
    # LOOKUP_TIME_ZONE_ONCE, which results in the best performance when the time
    # zone is not expected to change within a run.  However, if a time zone change
    # will cause a problem, LOOKUP_TIME_ZONE_ALWAYS should be used (however, this
    # results in slower performance).
    LOOKUP_TIME_ZONE_ONCE = 1

    # The following indicates that for DateTime construction the local time zone is
    # looked up each time a DateTime is created.  This should be considered when
    # running a real-time application that runs continuously between time zone changes.
    LOOKUP_TIME_ZONE_ALWAYS = 2

    # Abbreviations for months
    MONTH_ABBREVIATIONS = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    # Full names for months
    MONTH_NAMES = [
        "January", "February", "March",
        "April", "May", "June",
        "July", "August", "September",
        "October", "November",
        "December"
    ]

    # Abbreviation for days
    DAY_ABBREVIATIONS = [
        "Sun", "Mon", "Tue",
        "Wed", "Thu", "Fri",
        "Sat"
    ]

    # Full names for days
    DAY_NAMES = [
        "Sunday", "Monday",
        "Tuesday", "Wednesday",
        "Thursday", "Friday",
        "Saturday"
    ]

    # Days in months (non-leap year).
    MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # For a month, the number of days in the year passed on the first day of the
    # month (non-leap year).
    MONTH_YEARDAYS = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

    # Static data shared in package (so DateTime can get to easily)...
    _local_time_zone = None
    _local_time_zone_string = ""
    _local_time_zone_retrieved = False
    _time_zone_lookup_method = LOOKUP_TIME_ZONE_ONCE

    def __init__(self):
        pass

    @staticmethod
    def isLeapYear(year):
        """
        Determine whether a year is a leap year.
        Leap years occur on years evenly divisible by four.
        However, years evenly divisible by 100 are not leap
        years unless they are also evenly divisible by 400.
        :param year: 4-digit year to check
        :return: True if the specified year is a leap year and false if not.
        """
        if ((((year%4) == 0) and ((year%100)) != 0)) or (((year%100) == 0) and ((year%400)) == 0):
            return True
        else:
            return False

    @staticmethod
    def numDaysInMonth(month, year):
        """
        Return the number of days in a month, checking for leap year for February.
        :param month: The month of interest (1-12).
        :param year: The year of interest.
        :return: The number of days in a month, or zero if an error.
        """
        ndays = int()

        if month < 1:
            # Assume that something is messed up...
            ndays = 0
        elif month > 12:
            return TimeUtil.numDaysInMonth((month%12), (year + month/12))
        else:
            # Usual case...
            ndays = TimeUtil.MONTH_DAYS[month - 1]
            if (month == 2) and TimeUtil.isLeapYear(year):
                ndays += 1
        return ndays