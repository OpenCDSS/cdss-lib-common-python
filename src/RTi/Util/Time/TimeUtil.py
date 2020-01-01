# TimeUtil - date/time utility data and methods

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
    local_time_zone = None
    local_time_zone_string = ""
    local_time_zone_retrieved = False
    time_zone_lookup_method = LOOKUP_TIME_ZONE_ONCE

    def __init__(self):
        pass

    @staticmethod
    def absolute_month(month, year):
        """
        Return the absolute month, which is the year*12 + month.
        :param month: Month number
        :param year: Year
        :return: The absolute month, which is the year*12 + month.
        """
        return (year*12 + month)

    @staticmethod
    def is_leap_year(year):
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
    def num_days_in_month(month, year):
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
            return TimeUtil.num_days_in_month((month%12), (year + month/12))
        else:
            # Usual case...
            ndays = TimeUtil.MONTH_DAYS[month - 1]
            if (month == 2) and TimeUtil.is_leap_year(year):
                ndays += 1
        return ndays

    @staticmethod
    def num_days_in_month_from_datetime(dt):
        """
        Return the number of days in a month, checking for leap year for February.
        :param dt: The DateTime object to examine.
        :return: The number of days in a month, or zero if an error.
        """
        return TimeUtil.num_days_in_month_from_datetime(dt.getMonth(), dt.getYear())

    @staticmethod
    def num_days_in_months(month0, year0, month1, year1):
        """
        Calculate the number of days in several months.
        :param month0: The initial month of interest.
        :param year0: The initial year of interest.
        :param month1: The last month of interest.
        :param year1: The last year of interest.
        :return: The number of days in several months.
        """
        nmonths = TimeUtil.absolute_month(month1, year1) - TimeUtil.absolute_month(month0, year0) + 1

        i = 0
        month = 0
        ndays = 0
        year = int()

        month = month0
        year = year0
        for i in range(nmonths):
            ndays += TimeUtil.num_days_in_month(month, year)
            month += 1
            if month == 13:
                month = 1
                year += 1
        return ndays