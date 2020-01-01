# TSUtil - utility functions for TS

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

from abc import ABC
import logging

from RTi.TS.TSIdent import TSIdent
from RTi.TS.DayTS import DayTS
from RTi.TS.MonthTS import MonthTS
from RTi.Util.Time.TimeInterval import TimeInterval


class TSUtil(ABC):
    """
    This class contains static utility functions that operate on time series.
    Some of these routines are candidates for inclusion in the TS class, but are
    included here first because changes in the TS C++ class require extensive
    recompiles which slow development.  Putting the code here is almost as
    efficient.  Most of these classes accept a TS or Vector of TS as an argument.
    @see TS
    @see DateTime
    @see TSLimits
    """

    # Used with getPerioodFromTS, and getPeriodFromLimits and others. Find the maximum period.
    MAX_POR = 0

    # Used with getPeriodFromTS and others. Find the minimum (overlapping) period.
    MIN_POR = 1

    # Use the available period.  For example, when adding time series, does the
    # resulting time series have the maximum (combined period),
    # minimum (overlapping period), or original period (of the first time series).
    AVAILABLE_POR = 2

    # Ignore missing data when adding, subtracting, etc.
    IGNORE_MISSING = 1

    # Set result to missing of any data being analyzed are missing.
    SET_MISSING_IF_ANY_MISSING = 3

    # When used as a property, indicates that a time series transfer or analysis
    # should occur strictly by date/time.  In other words, if using
    # TRANSFER_BYDATETIME, Mar 1 will always line up with Mar 1, regardless of whether
    # leap years are encountered.  However, if TRANSFER_SEQUENTIALLY is used, then
    # data from Feb 29 of a leap year may be transferred to Mar 1 on the non-leapyear time series.
    TRANSFER_BYDATETIME = "ByDateTime"
    TRANSFER_SEQUENTIALLY = "Sequentially"

    @staticmethod
    def new_time_series(tsid, long_id):
        """
        Given a time series identifier as a string, determine the type of time series
        to be allocated and creates a new instance.  Only the interval base and
        multiplier are set (the memory allocation must occur elsewhere).  Time series metadata including the
        identifier are also NOT set.
        :param tsid: time series identifier as a string.
        :param long_id: If true, then the string is a full identifier. Otherwise, the string
        is only the interval (e.g., "10min").
        :return: A pointer to the time series, or null if the time series type cannot be determined.
        """
        logger = logging.getLogger(__name__)
        interval_base = 0
        interval_mult = 0
        interval_string = ""
        if long_id:
            # Create a TSIdent so that the type of time series can be determined...
            tsident = TSIdent(tsid)

            # Get the interval and base...
            interval_string = tsident.get_interval()
            interval_base = tsident.get_interval_base()
            interval_mult = tsident.get_interval_mult()
        else:
            # Parse a TimeInterval so that the type of time series can be determined...
            interval_string = tsid
            tsinterval = TimeInterval.parse_interval(interval_string)

            # Get the interval and base...
            interval_base = tsinterval.getBase()
            interval_mult = tsinterval.getMultiplier()

        # Now interpret the results and declare the time series...
        ts = None
        # if interval_base == TimeInterval.MINUTE:
        #     ts = MinuteTS()
        # elif interval_base == TimeInterval.HOUR:
        #     ts = HourTS()
        if interval_base == TimeInterval.DAY:
            ts = DayTS()
        elif interval_base == TimeInterval.MONTH:
            ts = MonthTS()
        # elif interval_base == TimeInterval.YEAR:
        #     ts = YearTS()
        # elif interval_base == TimeInterval.IRREGULAR:
        #     ts = IrregularTS()
        else:
            message = ("Cannot create a new time series for \"" + tsid + "\" (the interval \"" +
                       interval_string + "\" [" + interval_base + "] is not recognized.")
            logger.warning(message)
            return

        # Set the multiplier
        ts.set_data_interval(interval_base, interval_mult)
        ts.set_data_interval_original(interval_base, interval_mult)
        # Set the genesis information
        ts.add_to_genesis("Created new time series with interval determined from TSID \"" + tsid + "\"")

        # Return whatever was created...
        return ts