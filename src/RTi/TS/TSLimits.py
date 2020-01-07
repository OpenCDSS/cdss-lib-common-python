# TSLimits - simple class for managing time series data limits

# NoticeStart
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
#     but WITHOUT ANY WARRANTY     without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with CDSS Common Java Library.  If not, see <https://www.gnu.org/licenses/>.
# NoticeEnd
import logging
import math

# from RTi.TS.TSUtil import TSUtil
from RTi.TS.DayTS import DayTS
from RTi.TS.MonthTS import MonthTS
from RTi.TS.TSToArrayReturnType import TSToArrayReturnType
from RTi.Util.Math.MathUtil import MathUtil
from RTi.Util.String.StringUtil import StringUtil
from RTi.Util.Time.DateTime import DateTime
from RTi.Util.Time.TimeInterval import TimeInterval


class TSLimits(object):
    """
    The TSLimits class stores information about the data and date limits of a time
    series, including maximum, minimum, and mean, and important date/times.
    An instance is used by the TS base class and TSUtil routines use TSLimits to
    pass information.  In general, code outside of the TS package will only use the
    get*() methods (because TS or TSUtil methods will set the data).
    This TSLimits base class can be used for any time series.  More detailed limits
    like MonthTSLimits can be extended to contain more information.  The
    toString() method should be written to provide output suitable for use in a report.
    """

    # Flags used to indicate how limits are to be computed.
    # The following indicates that a time series' full limits should be refreshed.
    # This is generally used only by code internal to the TS library.
    REFRESH_TS = 0x1

    # Do not compute the total limits (using this TSLimits class).  This is used by
    # classes such as MonthTSLimits to increase performance.
    NO_COMPUTE_TOTALS = 0x2

    # Do not compute the detailed limits (e.g., using MonthTSLimits).  This is used by
    # classes such as MonthTSLimits to increase performance.
    NO_COMPUTE_DETAIL = 0x4

    # Ignore values <= 0 when computing averages (treat as missing data).
    # This make sense for time series
    # such as reservoirs and flows.  It may be necessary at some point to allow any
	# value to be ignored but <= 0 is considered a common and special case.
    IGNORE_LESS_THAN_OR_EQUAL_ZERO = 0x8

    def __init__(self, limits=None):
        """
        Default constructor.  Initialize the dates to null and the limits to zeros.
        :instance instance: Copy constructor.  A deep copy is made, except that the time series is not copied.
        """

        # Data members...

        self.ts = None  # Time series being studied.
        self.date1 = None
        self.date2 = None
        self.flags = None  # Flags to control behavior.
        self.max_value = None
        self.max_value_date = None
        self.mean = None
        self.median = None
        self.min_value = None
        self.min_value_date = None
        self.missing_data_count = None
        self.non_missing_data_count = None
        self.non_missing_data_date1 = None
        self.non_missing_data_date2 = None
        self.skew = None
        self.stdDev = None
        self.sum = None
        self.data_units=""  # Data units (just copy from TS at the time of creation).

        self.found = False

        if limits is None:
            self.initialize()
        else:
            # Copy constructor
            self.initialize()
            if limits.date1 is not None:
                self.date1 = DateTime(date_time=limits.date1)
            if limits.date2 is not None:
                date2 = DateTime(date_time=limits.date2)
            self.max_value = limits.max_value
            if limits.max_value_date is not None:
                self.max_value_date = DateTime(date_time=limits.max_value_date)
            self.min_value = limits.min_value
            if limits.min_value_date is not None:
                min_value_date = DateTime(date_time=limits.min_value_date)
            if limits.non_missing_data_date1 is not None:
                non_missing_data_date1 = DateTime(date_time=limits.non_missing_data_date1)
            if limits.non_missing_data_date2 is not None:
                non_missing_data_date2 = DateTime(date_time=limits.non_missing_data_date2)
            self.non_missing_data_count = limits.non_missing_data_count
            self.missing_data_count = limits.missing_data_count
            self.mean = limits.mean
            self.median = limits.median
            self.sum = limits.sum
            self.found = limits.found
            self.flags = limits.flags
            self.skew = limits.skew
            self.std_dev = limits.std_dev
            self.ts = limits.ts

    def are_limits_found(self):
        """
        Indicates whether the time series data and dates have been fully processed.
        Sometimes only some of the data members are used.  This routine is most often used by low-level code.
        @return A boolean indicating whether the limits have been found.
        """
        return self.found

    def calculate_data_limits(self, ts, start0, end0, refresh_flag):
        """
        Calculate the total data limits for a time series between two dates.
        This code was taken from the TSUtil.getDataLimits method.
        @param ts Time series of interest.
        @param start0 Starting date for the check.
        @param end0 Ending date for the check.
        @param refresh_flag Indicates whether the time series should be refreshed first
        (in general this is used only within the TS package and the version of this
        routine without the flag should be called).
        """
        max = 1.0
        mean = 0.0
        min = 0.0
        sum = 0.0
        value = 0.0
        base = 0
        missing_count = 0
        mult = 0
        non_missing_count = 0
        found = False
        max_date = None
        min_date = None
        non_missing_data_date1 = None
        non_missing_data_date2 = None
        t = None

        logger = logging.getLogger(__name__)
        debug = False

        try:
            # Main try...
            if ts is None:
                message = "NULL time series"
                logger.warning(message)
                # throw new TSException ( message )
                raise ValueError(message)

            # Initialize the sum and the mean...

            missing = ts.get_missing()
            sum = missing
            mean = missing

            # Get valid date limits because the ones passed in may have been null...

            valid_dates = self.get_valid_period(ts, start0, end0)
            start = valid_dates.get_date1()
            end = valid_dates.get_date2()
            valid_dates = None

            # Make sure that the time series has current limits...

            base = ts.get_data_interval_base()
            mult = ts.get_data_interval_mult()
            if refresh_flag:
                # Force a refresh of the time series.
                ts.refresh()

            # Get the variables that are used often in this function.

            ts_date1 = ts.get_date1()
            ts_date2 = ts.get_date2()

            # Figure out if we are treating data <= 0 as missing...

            ignore_lezero = False
            if (self.flags & TSLimits.IGNORE_LESS_THAN_OR_EQUAL_ZERO) != 0:
                ignore_lezero = True

            # Loop through the dates and get max and min data values
            # TODO SAM 2010-06-15 Need to consolidate code to use iterator

            if base == TimeInterval.IRREGULAR:
                # Loop through the dates and get max and min data values
                # Need to cast as an irregular TS...

                # IrregularTS its = (IrregularTS)ts
                its = ts

                data_array = its.get_data
                if data_array is None:
                    message = "Null data for " + str(ts)
                    logger.warning(message)
                    # throw new TSException ( message )
                    raise ValueError(message)
                size = len(data_array)
                ptr = None
                for i in range(size):
                    ptr = data_array[i]
                    date = ptr.get_date()

                    if date.less_than(ts_date1):
                        # Still looking for data...
                        continue
                    elif date.greater_than(ts_date2):
                        # No need to continue processing...
                        break

                    value = ptr.get_data_value()

                    if ts.is_data_missing(value) or (ignore_lezero and (value <= 0.0)):
                        # The value is missing
                        missing_count += 1
                        continue

                    # Else, data value is not missing...

                    if ts.is_data_missing(sum):
                        # Reset the sum...
                        sum = value
                    else:
                        # Add to the sum...
                        sum += value
                    non_missing_count += 1

                    if found:
                        # Already found the first non-missing point so
                        # all we need to do is check the limits.  These
                        # should only result in new DateTime a few times...
                        if value > max:
                            max = value
                            max_date = DateTime(date_time=date)
                        if value < min:
                            min = value
                            min_date = DateTime(date_time=date)
                    else:
                        # Set the limits to the first value found...
                        # date = new DateTime ( t )
                        max = value
                        max_date = DateTime(date_time=date)
                        min = value
                        min_date = max_date
                        non_missing_data_date1 = max_date
                        non_missing_data_date2 = max_date
                        found = True
                        continue

                # Now search backwards to find the first non-missing date...

                if found:
                    for i in range((size - 1), 0, -1):
                        ptr = data_array[i]
                        date = ptr.get_date()
                        value = ptr.get_data_value()
                        if date.greater_than(end):
                            # Have not found data...
                            continue
                        elif date.less_than(start):
                            # Passed start...
                            break
                        if (not ignore_lezero and not ts.is_data_missing(value)) or \
                                (ignore_lezero and ((value > 0.0) and not ts.is_data_missing(value))):
                            # Found the one date we are after...
                            non_missing_data_date2 = DateTime(date_time=date)
                            break
            else:
                # A regular TS... easier to iterate...
                # First loop through and find the data limits and the minimum non-missing date...
                t = DateTime(date_time=start, flag=DateTime.DATE_FAST)
                # Python for loops are not as clean as original Java code
                # for ( ; t.lessThanOrEqualTo(end); t.addInterval( base, mult )) {
                first_iteration = True
                while t.less_than_or_equal_to(end):
                    if first_iteration:
                        first_iteration = False
                    else:
                        t.add_interval(base, mult)

                    value = ts.get_data_value(t)

                    if ts.is_data_missing(value) or (ignore_lezero and (value <= 0.0)):
                        # The value is missing
                        missing_count += 1
                        continue

                    # Else, data value is not missing...

                    if ts.is_data_missing(sum):
                        # Reset the sum...
                        sum = value
                    else:
                        # Add to the sum...
                        sum += value
                    non_missing_count += 1

                    if found:
                        # Already found the first non-missing point so
                        # all we need to do is check the limits.  These
                        # should only result in new DateTime a few times...
                        if value > max:
                            max = value
                            max_date = DateTime(date_time=t)
                        if value < min:
                            min = value
                        min_date = DateTime(date_time=t)
                    else:
                        # First non-missing point so set the initial values...
                        date = DateTime(date_time=t)
                        max = value
                        max_date = date
                        min = value
                        min_date = date
                        non_missing_data_date1 = date
                        non_missing_data_date2 = date
                        found = True
                # Now loop backwards and find the last non-missing value...
                t = DateTime(date_time=end, flag=DateTime.DATE_FAST)
                if found:
                    # for(; t.greaterThanOrEqualTo(start); t.addInterval( base, -mult )) {
                    first_iteration = True
                    while t.greater_than_or_equal_to(start):
                        if first_iteration:
                            first_iteration = False
                        else:
                            t.add_interval(base, -mult)
                        value = ts.get_data_value(t)
                        if (not ignore_lezero and not ts.is_data_missing(value)) or \
                                (ignore_lezero and ((value > 0.0) and not ts.is_data_missing(value))):
                            # The value is not missing...
                            non_missing_data_date2 = DateTime(date_time=t)
                            break

            # TODO SAM 2010-06-15 This is a performance hit, but not too bad
            # TODO SAM 2010-06-15 Consider treating other statistics similarly but need to define unit tests
            # TODO SAM 2010-06-15 This code would need to be changed if doing Lag-1 correlation because order matters
            # For newly added statistics, use helper method to get data, ignoring missing...
            data_array = self.to_array(ts, start, end, 0, False)
            # Check for <= 0 values if necessary
            n_data_array = len(data_array)
            if ignore_lezero:
                for i in range(n_data_array):
                    if data_array[i] <= 0.0:
                        # Just exchange with the last value and reduce the size
                        temp = data_array[i]
                        data_array[i] = data_array[n_data_array - 1]
                        data_array[n_data_array - 1] = temp
                        n_data_array -= 1

            if n_data_array > 0:
                self.set_median(MathUtil.median(n_data_array, data_array))

            if n_data_array > 1:
                try:
                    self.set_std_dev(MathUtil.standard_deviation(n_data_array, data_array))
                except Exception as e:
                    # Likely due to small sample size
                    pass
            if n_data_array > 2:
                try:
                    self.set_skew(MathUtil.skew(n_data_array, data_array))
                except Exception as e:
                    # Likely due to small sample size
                    pass

            if not found:
                message = "\"" + ts.getIdentifierString() + "\": problems finding limits, whole POR missing!"
                logger.warning(message)
                # throw new TSException ( message )
                raise ValueError(message)

            if debug:
                logger.debug("Overall date limits are: " + str(start) + " to " + str(end))
                logger.debug("Found limits to be: " + str(min) + " on " + str(min_date) + " to " + str(max) +
                             " on " + str(max_date))
                logger.debug("Found non-missing data dates to be: " + str(non_missing_data_date1) + " -> " +
                             str(non_missing_data_date2))

            # Set the basic information...

            self.set_date1(start)
            self.set_date2(end)
            self.set_max_value(max, max_date)
            self.set_min_value(min, min_date)
            self.set_non_missing_data_date1(non_missing_data_date1)
            self.set_non_missing_data_date2(non_missing_data_date2)
            self.set_missing_data_count(missing_count)
            self.set_non_missing_data_count(non_missing_count)
            # //int data_size = calculate_data_size(ts, start, end)
            # //limits.set_non_missing_data_count(data_size - missing_count)
            if not ts.is_data_missing(sum) and (non_missing_count > 0):
                mean = sum/float(non_missing_count)
            else:
                mean = missing
            self.set_sum(sum)
            self.set_mean(mean)
        except Exception as e:
            message = "Error computing limits."
            logger.warning(message)
            # Put in debug because output sometimes is overwhelming when data are not available.
            if debug:
                logger.warning(e)
            # throw new TSException ( message )
            raise Exception(message)

    def calculate_data_size(self, start_date, end_date, interval_base, interval_mult):
        """
        Determine the data size for a time series for a period.  If an IrregularTS
        data size is needed, call the non-static IrregularTS.calculateDataSize() method.
        @return The number of data points for a time series of the given data
        interval for the specified period.  This is a utility function to call the
        time series base class calculateDataSize methods.  An instance of the time
        series is not required (note that this will not work for IrregularTS, where the
        spacing of data is unknown unless a time series is supplied).
        @param start_date The first date of the period.
        @param end_date The last date of the period.
        @param interval_base The time series data interval base.
        @param interval_mult The time series data interval multiplier.
        """
        logger = logging.getLogger(__name__)
        if start_date is None:
            logger.warning("Start date is null")
            return 0
        if end_date is None:
            logger.warning("End date is null")
            return 0
        if interval_base == TimeInterval.YEAR:
            # return YearTS.calculateDataSize ( start_date, end_date, interval_mult;
            pass
        elif interval_base == TimeInterval.MONTH:
            return MonthTS.calculate_data_size(start_date, end_date, interval_mult)
        elif interval_base == TimeInterval.DAY:
            return DayTS.calculate_data_size(start_date, end_date, interval_mult)
        # elif ( interval_base == TimeInterval.HOUR ):
        #     return HourTS.calculateDataSize(start_date, end_date, interval_mult)
        # elif interval_base == TimeInterval.MINUTE:
        #     return MinuteTS.calculateDataSize(start_date, end_date, interval_mult)
        # elif interval_base == TimeInterval.IRREGULAR:
        #     # This will just count the data values in the period...
        #     return IrregularTS.calculateDataSize(start_date, end_date, interval_mult)
        else:
            # Interval is not supported.  Big problem!
            logger.warning("Time series interval " + interval_base + " is not supported")
            return 0

    def check_dates(self):
        """
        Check to see if ALL the dates have been set (are non-null) and if so set the
        _found flag to true.  If a TSLimits is being used for something other than fill
        limits analysis, then external code may need to call setLimitsFound() to manually set the found flag.
        """
        if (self.date1 is not None) and (self.date2 is not None) and \
            (self.max_value_date is not None) and (self.min_value_date is not None) and \
                (self.non_missing_data_date1 is not None) and (self.non_missing_data_date2 is not None):
            # The dates have been fully processed (set)...
            self.found = True

    def get_data_units(self):
        """
        Return the data units for the data limits.
        """
        return self.data_units

    def get_date1(self):
        """
        Return the first date for the time series according to the memory allocation.
        @return The first date for the time series according to the memory allocation.
        A copy of the date is returned.
        """
        if self.date1 is None:
            return self.date1
        else:
            return DateTime(date_time=self.date1)

    def get_date2(self):
        """
        Return the last date for the time series according to the memory allocation.
        @return The last date for the time series according to the memory allocation.
        A copy of the date is returned.
        """
        if self.date2 is None:
            return self.date2
        else:
            return DateTime(date_time=self.date2)

    def get_max_value(self):
        """
        Return the maximum data value for the time series.
        @return The maximum data value for the time series.
        """
        return self.max_value

    def get_max_value_date(self):
        """
        Return the date corresponding to the maximum data value for the time series.
        @return The date corresponding to the maximum data value for the time series.
        A copy of the date is returned.
        """
        if self.max_value_date is None:
            return self.max_value_date
        else:
            return DateTime(date_time=self.max_value_date)

    def get_mean(self):
        """
        Return the mean data value for the time series.
        @return The mean data value for the time series.
        """
        return self.mean

    def get_median(self):
        """
        Return the median data value for the time series.
        @return The median data value for the time series, or NaN if not computed.
        """
        return self.median

    def get_min_value(self):
        """
        Return the minimum data value for the time series.
        @return The minimum data value for the time series.
        """
        return self.min_value

    def get_min_value_date(self):
        """
        Return the date corresponding to the minimum data value for the time series.
        @return The date corresponding to the minimum data value for the time series.
        A copy of the date is returned.
        """
        if self.min_value_date is None:
            return self.min_value_date
        else:
            return DateTime(date_time=self.min_value_date)

    def get_missing_data_count(self):
        """
        Return the count for the number of missing data in the time series.
        @return The count for the number of missing data in the time series.
        """
        return self.missing_data_count

    def get_non_missing_data_count(self):
        """
        Return the count for the number of non-missing data in the time series.
        @return The count for the number of non-missing data in the time series.
        """
        return self.non_missing_data_count

    def get_non_missing_data_date1(self):
        """
        Return the date corresponding to the first non-missing data in the time series.
        @return The date corresponding to the first non-missing data in the time series.
        A copy of the date is returned.
        """
        if self.non_missing_data_date1 is None:
            return self.non_missing_data_date1
        else:
            return DateTime(date_time=self.non_missing_data_date1)

    def get_non_missing_data_date2(self):
        """
        Return the date corresponding to the last non-missing data in the time series.
        @return The date corresponding to the last non-missing data in the time series.
        A copy of the date is returned.
        """
        if self.non_missing_data_date2 is None:
            return self.non_missing_data_date2
        else:
            return DateTime(date_time=self.non_missing_data_date2)

    def get_sum(self):
        """
        Return the sum of non-missing data values for the time series.
        @return The sum of non-missing data values for the time series.
        """
        return self.sum

    def get_time_series(self):
        """
        Return the time series that is associated with these limits.
        @return the time series that is associated with these limits.
        """
        return self.ts

    def has_non_missing_data(self):
        """
        Determine whether non-missing data are available.
        @return true if time series has non-missing data, false if not.
        """
        if self.non_missing_data_count > 0:
            return True
        else:
            return False

    def get_skew(self):
        """
        Return the skew for the time series.
        @return The skew for the time series, or NaN if not computed.
        """
        return self.skew

    def get_std_dev(self):
        """
        Return the standard deviation for the time series.
        @return The standard deviation for the time series, or NaN if not computed.
        """
        return self.std_dev

    # TODO smalers 2020-01-04 copied from TSUtil to prevent circular import reference
    def get_valid_period(self, ts, suggested_start, suggested_end):
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
            dates.set_date1(date_time=DateTime(ts.get_date1()))
        else:
            dates.set_date1(date_time=DateTime(suggested_start))
        if (suggested_end is None) and (ts is not None):
            dates.set_date2(date_time=DateTime(ts.get_date2()))
        else:
            dates.set_date2(date_time=DateTime(suggested_end))
        return dates

    def initialize(self):
        """
        Initialize the data.
        Need to rework code to use an instance of TS so we can initialize to missing
        data values used by the time series!
        :param self:
        :return:
        """
        self.ts = None
        self.data_units = ""
        self.date1 = None
        self.date2 = None
        self.flags = 0
        self.max_value = 0.0
        self.max_value_date = None
        self.mean = math.nan  # Assume
        self.median = math.nan  # Assume.
        self.min_value = 0.0
        self.min_value_date = None
        self.missing_data_count = 0
        self.non_missing_data_count = 0
        self.non_missing_data_date1 = None
        self.non_missing_data_date2 = None
        self.skew = math.nan
        self.stdDev = math.nan
        self.sum = math.nan  # Assume
        self.found = False

    def intervals_match(self, ts1=None, ts2=None, tslist=None, interval_base=None, interval_mult=None):
        """
        Determine whether two time series have matching data intervals.  The intervals must exactly match and not
        just be equivalent (i.e., 1Day != 24Hour).
        @return true if the time series have the same data interval, false if not.
        @param ts1 first time series to check
        @param ts2 second time series to check
        """
        if (ts1 is not None) and (ts2 is not None):
            tslist = []
            tslist.append(ts1)
            tslist.append(ts2)
            return self.intervals_match(tslist=tslist)
        elif tslist is not None:
            if len(tslist) == 0:
                return True
            if interval_base is None and interval_mult is None:
                # Find first non - null time series to compare...
                for ts in tslist:
                    if ts is not None:
                        return self.intervals_match(tslist=tslist, interval_base=ts.get_data_interval_base(),
                                                    interval_mult=ts.get_data_interval_mult())
                # Could not find non-null time series to check
                return False
            else:
                # Main logic
                for ts in tslist:
                    if ts is None:
                        # Message.printWarning ( 3, "TSUtil.intervalsMatch", "TS [" + i + "] is null" );
                        return False
                    if (ts.get_data_interval_base() != interval_base) or (ts.get_data_interval_mult() != interval_mult):
                        return False
                # All the intervals match...
                return True

    def set_date1(self, date1):
        """
        Set the first date for the time series.  This is used for memory allocation.
        @param date1 The first date for the time series.
        @see TS#allocateDataSpace
        """
        if date1 is not None:
            self.date1 = DateTime(date_time=date1)
        self.check_dates()

    def set_date2(self, date2):
        """
        Set the last date for the time series.  This is used for memory allocation.
        @param date2 The last date for the time series.
        @see TS#allocateDataSpace
        """
        if date2 is not None:
            self.date2 = DateTime(date_time=date2)
        self.check_dates()

    def set_limits_found(self, flag):
        """
        Set whether the limits have been found.  This is mainly used by routines in
        the package when only partial limits are needed (as opposed to checkDates(),
        which checks all the dates in a TSLimits).  Call this method after any methods
        that set the date to offset the check done by checkDates().
        @param flag Indicates whether the limits have been found (true or false).
        """
        self.found = flag

    def set_max_value(self, max_value, max_value_date=None):
        """
        Set the maximum data value for the time series.
        @param max_value The maximum data value.
        @param max_value_date The date corresponding to the maximum data value.
        """
        self.max_value = max_value
        if max_value_date is not None:
            self.set_max_value_date(max_value_date)

    def set_max_value_date(self, max_value_date):
        """
        Set the date corresponding to the maximum data value for the time series.
        @param max_value_date The date corresponding to the maximum data value.
        """
        if max_value_date is not None:
            self.max_value_date = DateTime(date_time=max_value_date)
        self.check_dates()

    def set_mean(self, mean):
        """
        Set the mean data value for the time series.
        @param mean The mean data value.
        """
        self.mean = mean

    def set_median(self, median):
        """
        Set the median data value for the time series.
        @param median The median data value.
        """
        self.median = median

    def set_min_value(self, min_value, min_value_date=None):
        """
        Set the minimum data value for the time series.
        @param min_value The minimum data value.
        @param min_value_date The date corresponding to the minimum data value.
        """
        self.min_value = min_value
        if min_value_date is not None:
            self.set_min_value_date(min_value_date)

    def set_min_value_date(self, min_value_date):
        """
        Set the date corresponding to the minimum data value for the time series.
        @param min_value_date The date corresponding to the minimum data value.
        """
        if min_value_date is not None:
            self.min_value_date = DateTime(date_time=min_value_date)
        self.check_dates()

    def set_missing_data_count(self, missing_data_count):
        """
        Set the counter for missing data.
        @param missing_data_count The number of missing data in the time series.
        """
        self.missing_data_count = missing_data_count

    def set_non_missing_data_count(self, non_missing_data_count):
        """
        Set the counter for non-missing data.
        @param non_missing_data_count The number of non-missing data in the time series.
        """
        self.non_missing_data_count = non_missing_data_count

    def set_non_missing_data_date1(self, date):
        """
        Set the date for the first non-missing data value.
        @param date The date for the first non-missing data value.
        """
        if date is not None:
            self.non_missing_data_date1 = DateTime(date_time=date)
            self.check_dates()

    def set_non_missing_data_date2(self, date):
        """
        Set the date for the last non-missing data value.
        @param date The date for the last non-missing data value.
        """
        if date is not None:
            self.non_missing_data_date2 = DateTime(date_time=date)
        self.check_dates()

    def set_skew(self, skew):
        """
        Set the skew for the time series.
        @param skew The skew data value.
        """
        self.skew = skew

    def set_std_dev(self, std_dev):
        """
        Set the standard deviation for the time series.
        @param std_dev The standard deviation.
        """
        self.std_dev = std_dev

    def set_sum(self, sum):
        """
        Set the sum of data values for the time series.
        @param sum The sum of data value.
        """
        self.sum = sum

    def set_time_series(self, ts):
        """
        Set the time series.  No analysis occurs after the set.  This method is most
        often used by the derived classes.
        @param ts The time series.
        """
        self.ts = ts

    # TODO smalers 2020-01-04 copied from TSUtil to prevent circular import
    def to_array(self, ts, start_date=None, end_date=None, month_index=None, include_months=None, include_missing=True,
                 match_other_nonmissing=None, paired_ts=None, return_type=None):
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
        @param include_months
        @param include_missing indicate whether missing values should be included in the result.
        @param match_other_nonmissing
        @param paired_ts
        @param return_type
        """
        if month_index == None:
            # Called with no month index
            month_indices = None
            if month_index != 0:
                month_indices = [month_index]
            # Recursively call
            return self.to_array(ts, start_date=start_date, end_date=end_date, include_months=include_months,
                                 include_missing=include_missing)

        # If here do the processing based on input arguments

        if paired_ts is not None:
            if not TimeInterval.is_regular_interval(ts.get_data_interval_base()):
                # throw new IrregularTimeSeriesNotSupportedException(
                raise ValueError(
                    "Irregular interval time series cannot have data array extracted using paired time series.")
            if not self.intervals_match(ts, paired_ts):
                # throw new UnequalTimeIntervalException(
                raise ValueError(
                    "Time series from which to extract data has a different interval than paired time series.")
        # Get valid dates because the ones passed in may have been null...

        valid_dates = self.get_valid_period(ts, start_date, end_date)
        start = valid_dates.get_date1()
        end = valid_dates.get_date2()

        interval_base = ts.get_data_interval_base()
        interval_mult = ts.get_data_interval_mult()
        size = 0
        # if ts.get_data_interval_base() == TimeInterval.IRREGULAR:
            # size = self.calculate_data_size(ts, start, end)
        # else:
        size = self.calculate_data_size(start, end, interval_base, interval_mult)
        if return_type is None:
            return_type = TSToArrayReturnType.DATA_VALUE
        if return_type == TSToArrayReturnType.DATE_TIME:
            # Only 1Year, 1Month, 1Day intervals are supported
            if (interval_mult != 1) or ((interval_base != TimeInterval.YEAR) and
                (interval_base != TimeInterval.YEAR) and (interval_base != TimeInterval.YEAR)):
                # throw new InvalidTimeIntervalException(
                raise ValueError(
                    "Interval must be Year, Month, or Day (no multiplier) to return date/time as array.")

        include_months_mask = []
        if (include_months is None) or (len(include_months) == 0):
            for i in range(12):
                include_months_mask[i] = True
        else:
            for i in range(12):
                include_months_mask[i] = False
            for i in range(len(include_months)):
                include_months_mask[include_months[i] - 1] = True

        if size == 0:
            return []

        data_array = []  # Initial size including missing
        count = 0  # Number of values in array.
        month = 0  # Month

        if interval_base == TimeInterval.IRREGULAR:
            # Get the data and loop through the vector...
            irrts = ts
            alltsdata = irrts.get_data()
            if alltsdata is None:
                # No data for the time series...
                return None
            nalltsdata = len(alltsdata)
            tsdata = None
            date = None
            for i in range(nalltsdata):
                tsdata = alltsdata[i]
                date = tsdata.get_date()
                if date.greater_than(end):
                    # Past the end of where we want to go so quit...
                    break
                if date.greater_than_or_equal_to(start):
                    month = date.get_month()
                    if include_months_mask[month - 1]:
                        value = tsdata.get_data_value()
                        if include_missing or not ts.is_data_missing(value):
                            if return_type == TSToArrayReturnType.DATA_VALUE:
                                data_array[count] = value
                                count += 1
                            elif return_type == TSToArrayReturnType.DATE_TIME:
                                if interval_base == TimeInterval.YEAR:
                                    data_array[count] = date.get_year()
                                    count += 1
                                elif interval_base == TimeInterval.MONTH:
                                    data_array[count] = date.get_absolute_month()
                                    count += 1
                                elif interval_base == TimeInterval.DAY:
                                    data_array[count] = date.get_absolute_day()
                                    count += 1
        else:
            # Regular, increment the data by interval...
            date = DateTime(date_time=start)
            count = 0
            do_transfer = False
            is_missing = False
            # for ; date.lessThanOrEqualTo( end); date.addInterval(interval_base, interval_mult):
            first_iteration = True
            while date.less_than_or_equal_to(end):
                if first_iteration:
                    first_iteration = False
                else:
                    date.add_interval(interval_base, interval_mult)
                # First figure out if the data should be skipped because not in a requested month
                month = date.get_month()
                if not include_months_mask[month - 1]:
                    continue
                # Now transfer the value while checking the paired time series
                do_transfer = False  # Do not transfer unless criteria are met below
                value = ts.get_data_value(date)
                is_missing = ts.is_data_missing(value)
                if paired_ts is not None:
                    # Value in "ts" time series MUST be non-missing
                    if not is_missing:
                        value2 = paired_ts.get_data_value(date)
                        is_missing2 = paired_ts.is_data_missing(value2)
                        if match_other_nonmissing:
                            # Want non-missing in both "ts" and "pairedTS"
                            if not is_missing2:
                                do_transfer = True
                        else:
                            # Want non-missing in "ts" and missing in "pairedTS"
                            if is_missing2:
                                do_transfer = True
                else:
                    if include_missing or not is_missing:
                        # Value is not missing.
                        do_transfer = True

                # OK to transfer the value...
                if do_transfer:
                    if return_type == TSToArrayReturnType.DATA_VALUE:
                        data_array[count] = value
                        count += 1
                    elif return_type == TSToArrayReturnType.DATE_TIME:
                        if interval_base == TimeInterval.YEAR:
                            data_array[count] = date.get_year()
                            count += 1
                        elif interval_base == TimeInterval.MONTH:
                            data_array[count] = date.get_absolute_month()
                            count += 1
                        elif interval_base == TimeInterval.DAY:
                            # TODO smalers 2020-01-04 need to enable
                            # data_array[count] = date.get_absolute_day()
                            count += 1

        if count != size:
            # The original array is too big and needs to be cut down to the exact size due to limited
            # months or missing data being excluded)...
            new_data_array = [count]
            for j in range(count):
                new_data_array[j] = data_array[j]
            return new_data_array

        # Return the full array...
        return data_array

    def to_string(self):
        """
        Return a string representation.
        @return A verbose string representation of the limits.
        """
        units = ""
        if len(self.data_units) > 0:
            units = self.data_units
        missing_percent = 0.0
        non_missing_percent = 0.0
        if (self.missing_data_count + self.non_missing_data_count) > 0:
            missing_percent = 100.0*float(self.missing_data_count) / \
                float(self.missing_data_count + self.non_missing_data_count)
            non_missing_percent = 100.0*float(self.non_missing_data_count) / \
                float(self.missing_data_count + self.non_missing_data_count)
        return \
            "Min:  " + StringUtil.format_string(self.min_value, "%20.4f") + units + " on " + \
            str(self.min_value_date) + "\n" + \
            "Max:  " + StringUtil.format_string(self.max_value, "%20.4f") + units + " on " + \
            str(self.max_value_date) + "\n" + \
            "Sum:  " + StringUtil.format_string(self.sum, "%20.4f") + units + "\n" + \
            "Mean: " + StringUtil.format_string(self.mean, "%20.4f") + units + "\n" + \
            "Median: " + StringUtil.format_string(self.median, "%20.4f") + units + "\n" + \
            "StdDev: " + StringUtil.format_string(self.stdDev, "%20.4f") + units + "\n" + \
            "Skew: " + StringUtil.format_string(self.skew, "%20.4f") + units + "\n" + \
            "Number Missing:     " + str(self.missing_data_count) + " (" + \
            StringUtil.format_string(missing_percent, "%.2f")+"%)\n" + \
            "Number Not Missing: " + str(self.non_missing_data_count) + " (" + \
            StringUtil.format_string(non_missing_percent, "%.2f") + "%)\n" + \
            "Total period: " + str(self.date1) + " to " + str(self.date2) + "\n" + \
            "Non-missing data period: " + str(self.non_missing_data_date1) + " to " + \
            str(self.non_missing_data_date2)
