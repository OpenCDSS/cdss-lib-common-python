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

import logging

from RTi.TS.TSIdent import TSIdent
from RTi.TS.DayTS import DayTS
from RTi.TS.MonthTS import MonthTS
from RTi.TS.TSLimits import TSLimits
from RTi.Util.Time.DateTime import DateTime
from RTi.Util.Time.TimeInterval import TimeInterval


class TSUtil(object):
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
    def get_period_from_ts(tslist, por_flag):
        """
        Determine the limits for a list of time series.
        <pre>
        Example of POR calculation:
            ------------------------    TS1
              -------------------       TS2
                        --------------  TS3

            --------------------------  MAX_POR
                        ---------       MIN_POR
        </pre>
        @return The TSLimits for the list of time series (recomputed).  If the limits
        do not overlap, return the maximum.
        @param tslist A list of time series of interest.
        @param por_flag Use a *_POR flag.
        @exception RTi.TS.TSException If the period cannot be determined from the time series.
        """

        logger = logging.getLogger(__name__)
        debug = False

        end = None
        start = None

        if tslist is None:
            message = "Unable to get period for time series - time series list is null"
            logger.warning(message)
            raise ValueError(message)

        list_size = len(tslist)
        if debug:
            logger.debug("Getting " + str(por_flag) + "-flag limits for " + str(list_size) + " time series")

        if list_size == 0:
            message = "Unable to get period for time series - time series list is zero size"
            logger.warning(message)
            raise ValueError(message)
        if (por_flag != TSUtil.MIN_POR) and (por_flag != TSUtil.MAX_POR):
            message = "Unknown option for TSUtil.getPeriodForTS" + str(por_flag)
            logger.warning(message)
            raise ValueError(message)

        # Initialize the start and end dates to the first TS dates...

        nullcount = 0
        for its in range(list_size):
            ts_ptr = tslist[its]
            if ts_ptr is not None:
                if ts_ptr.get_date1() is not None:
                    start = ts_ptr.get_date1()
                if ts_ptr.get_date2() is not None:
                    end = ts_ptr.get_date2()
                if (start is not None) and (end is not None):
                    # Done looking for starting date/times
                    break
            else:
                nullcount += 1

        if debug:
            logger.debug("Starting comparison dates " + str(start) + " " + str(end))

        if (start is None) or (end is None):
            message = "Unable to get period (all null dates) from " + str(list_size) +\
                      " time series (" + str(nullcount) + " null time series)."
            logger.warning(message)
            raise ValueError(message)

        # Now loop through the remaining time series...

        for i in range(1, list_size):
            ts_ptr = tslist[i]
            if ts_ptr is None:
                # Ignore the time series...
                continue
            ts_ptr_start = ts_ptr.get_date1()
            ts_ptr_end = ts_ptr.get_date2()
            if (ts_ptr_start is None) or (ts_ptr_end is None):
                continue
            if debug:
                logger.debug("Comparison dates " + str(ts_ptr_start) + " " + str(ts_ptr_end))
            if por_flag == TSUtil.MAX_POR:
                if ts_ptr_start.less_than(start):
                    start = DateTime(date_time=ts_ptr_start)
                if ts_ptr_end.greater_than(end):
                    end = DateTime(date_time=ts_ptr_end)
            elif por_flag == TSUtil.MIN_POR:
                if ts_ptr_start.greater_than(start):
                    start = DateTime(date_time=ts_ptr_start)
                if ts_ptr_end.less_than(end):
                    end = DateTime(date_time=ts_ptr_end)

        # If the time series do not overlap, then the limits may be reversed.  In this case, throw an exception...
        if start.greater_than(end):
            message = "Periods do not overlap.  Can't determine minimum period."
            logger.warning(message)
            raise ValueError(message)

        if debug:
            if por_flag == TSUtil.MAX_POR:
                if debug:
                    logger.debug("Maximum POR limits are " + str(start) + " to " + str(end))
            elif por_flag == TSUtil.MIN_POR:
                if debug:
                    logger.debug("Minimum POR limits are " + str(start) + " to " + str(end))

        # Now return the dates as a new instance so we don't mess up what was in the time series...

        limits = TSLimits()
        limits.set_date1(DateTime(date_time=start))
        limits.set_date2(DateTime(date_time=end))
        limits.set_limits_found(True)
        return limits

    @staticmethod
    def get_valid_period(ts, suggested_start, suggested_end):
        """
        This method takes two dates which are generally the start and end dates for an iteration.  If they are
        specified, they are used (even if they are outside the range of the time series).  If a date is not specified,
        then the appropriate date from the time series is used.  This routine may require logic at some point to
        handle special cases.  For example, the incoming arguments may specify a start date but no end date.
        If the start date from the time series is later than the specified end date, then what?
        @return The limits given a suggested start and end date.  The date limits can
        extend beyond the end of the time series dates.  If the suggestions are null,
        the appropriate start/end dates from the time series are used.  New date instances
        are created to protect against changing the original dates.
        @param ts Time series of interest.
        @param suggested_start Suggested start date.
        @param suggested_end Suggested end date.
        """
        dates = TSLimits()
        if (suggested_start is None) and (ts is not None):
            dates.set_date1(DateTime(date_time=ts.get_date1()))
        else:
            dates.set_date1(DateTime(date_time=suggested_start))
        if (suggested_end is None) and (ts is not None):
            dates.set_date2(DateTime(date_time=ts.get_date2()))
        else:
            dates.set_date2(DateTime(date_time=suggested_end))
        return dates

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

    @staticmethod
    def to_array(ts, start_date=None, end_date=None, month_index=None, month_indices=None, include_missing=None):
        """
        Return an array containing the data values of the time series for the specified
        period.  If the start date or end date are outside the period of
        record for the time series, use the missing data value from the time series
        for those values.  If the start date or end date are null, the start and end
        dates of the time series are used.  This is a utility routine mainly used by other versions of this routine.
        @return The array of data for the time series.  If an error, return null.
        @param ts Time series to convert data to array format.
        @param start_date Date corresponding to the first date of the returned array.
        @param end_date Date corresponding to the last date of the returned array.
        @param month_index Month of interest (1=Jan, 12=Dec).  If zero, process all months.
        @param includeMissing indicate whether missing values should be included in the result.
        """
        if month_index == None:
            # Called with no month index
            month_indices = None
            if month_index != 0:
                month_indices = [month_index]
            # Recursively call
            return TSUtil.to_array(ts, start_date=start_date, end_date=end_date, month_indices=month_indices,
                                   include_missing=include_missing)
