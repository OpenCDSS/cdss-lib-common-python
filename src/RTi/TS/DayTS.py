# DayTS - base class from which all daily time series are derived

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
# DayTS - base class from which all daily time series are derived
# ----------------------------------------------------------------------------
# Notes:	(1)	This base class is provided so that specific daily
#           time series can derive from this class.
#           (2)	Data for this time series interval is stored as follows:
#
#           day within month  ->
#
#           ------------------------
#           |  |  |.......|  |  |  |     first month in period
#           ------------------------
#           |  |  |.......|  |  |
#           ------------------------
#           |  |  |.......|  |  |  |
#           ------------------------
#           |  |  |.......|  |  |
#           ---------------------
#           .
#           .
#           .
#           ------------------------
#           |  |  |.......|  |  |  |
#           ------------------------
#           |  |  |.......|  |  |        last month in period
#           ---------------------
#
#           The base block of storage is the month.  This lends
#           itself to very fast data retrieval but may waste some
#           memory for short time series in which full months are
#           not stored.  This is considered a reasonable tradeoff.
# ----------------------------------------------------------------------------

import logging

from RTi.TS.TS import TS
from RTi.Util.Time.DateTime import DateTime
from RTi.Util.Time.TimeInterval import TimeInterval
from RTi.Util.Time.TimeUtil import TimeUtil


class DayTS(TS):
    """
    The DayTS class is the base class for daily time series.  The class can be
    extended for variations on daily data.  Override the allocateDataSpace() and set/get methods to do so.
    """

    # The DataFlavor for transferring this specific class.
    # dayTSFlavor = DataFlavor(RTi.TS.DayTS.class, "RTi.TS.DayTS")

    def __init__(self):
        # Data members...

        self.data = [[]]  # This is the data space for daily time series.
        self.data_flags = []  # Data flags
        self.pos = []  # Used to optimize performance when getting data.
        self.row = int()  # Row position in data.
        self.column = int()  # column position in data

        super().__init__()
        self.initialize_dayts()

    def allocate_data_space(self, value=None):
        """
        Allocate the data space.  The start and end dates and the interval multiplier should have been set.
        :param value: The value to initialize the time series, if None use the time series missing value.
        :return: 0 if successful, 1 if failure.
        """
        logger = logging.getLogger(__name__)
        nmonths = 0

        if not value:
            value = self.missing

        if not self.date1 or not self.date2:
            logger.warning("No dates set for memory allocation.")
            return 1
        if self.data_interval_mult != 1:
            # Do not know how to handle N-day interval...
            message = "Only know how to handle 1-day data, not " + str(self.data_interval_mult) + "Day"
            logger.warning(message)
            return 1

        if nmonths == 0:
            logger.warning("TS has 0 months POR, maybe dates haven't been set yet")
            return 1

        self.data = [[float()]]*nmonths
        if self.has_data_flags:
            self.data_flags = [[str()]]*nmonths

        # May need to catch an exception here in case we run out of memory.

        # Set the counter date to match the starting month. This data is used to
        # to determine the number of days in each month.

        date = DateTime(DateTime.DATE_FAST)
        date.set_month(self.date1.get_month())
        date.set_year(self.date1.get_year())

        for imon in range(nmonths):
            ndays_in_month = TimeUtil.num_days_in_month_from_datetime(date)
            # Handle 1-day data, otherwise an excpetion was thrown above.
            # Here would change the number of values if N-day was supported.
            nvals = ndays_in_month
            self.data[imon] = [float()]*nvals

            # Now fill with the missing data value for each day in month...

            for iday in range(nvals):
                self.data[imon][iday] = value
                if self.has_data_flags:
                    self.data_flags[imon][iday] = ""

            date.add_month(1)

        nactual = DayTS.calculate_data_size(self.date1, self.date2, self.data_interval_mult)
        self.set_data_size(nactual)

        return 0

    @staticmethod
    def calculate_data_size(start_date, end_date, interval_mult):
        """
        Determine the number of points between two dates for the given interval multiplier.
        :param start_date: The first date of the period.
        :param end_date: The last date of the period.
        :param interval_mult: The time series data interval multiplier.
        :return: The number of data points for a day time series
        given the data interval multiplier for the specified period.
        """
        logger = logging.getLogger(__name__)

        if not start_date:
            logger.warning("Start date is null")
            return 0
        if not end_date:
            logger.warning("End date is null")
            return 0
        if interval_mult > 1:
            logger.warning("Greater than 1-day TS not supported")
            return 0

        # First set to the number of data in the months...
        datasize = TimeUtil.num_days_in_months(start_date.get_month(), start_date.get_year(), end_date.get_month(),
                                               end_date.get_year())
        # Now subtract off the data at the ends that are missing...
        # Start by subtracting the full day at the beginning of the month is not included...
        datasize -= (start_date.get_day() - 1)
        # Now subtract off the data at the end...
        # Start by subtracting the full days off the end of the month...
        ndays_in_month = TimeUtil.num_days_in_month(end_date.get_month(), end_date.get_year())
        datasize -= (ndays_in_month - end_date.get_day())
        return datasize

    def initialize_dayts(self):
        """
        Initialize data members
        """
        self.data = None
        self.data_interval_base = TimeInterval.DAY
        self.data_interval_mult = 1
        self.data_interval_base_original = TimeInterval.DAY
        self.data_interval_mult_original = 1
        self.pos = [int()] * 2
        self.pos[0] = 0
        self.pos[1] = 0
        self.row = 0
        self.column = 0

    def get_data_position(self, date):
        """
        :param date: Date of interest
        :return: The data position corresponding to the date.
        """
        # Do not define the routine or debug level here so we can optimize.

        # Note that unlike HourTS, do not need to check the time zone!

        # Check the date coming in...
        if date is None:
            return None

        # Calculate the row position of the data...

        self.row = date.get_absolute_month() - self.date1.get_absolute_month()

        # Calculate the column position of the data. We know that daily data
        # is stored in a 2 deminsional array with the column being the daily data by interval.

        self.column = date.get_day() - 1

        self.pos[0] = self.row
        self.pos[1] = self.column
        return self.pos

    def set_data_value(self, date, value):
        """
        Set the data value for the date.
        :param date: Date of interest
        :param value: Data value corresponding to date.
        """
        if date.less_than(self.date1) or date.greater_than(self.date2):
            return
        self.get_data_position(date)
        # Set the dirty flag so that we know to recompute the limits if desired...
        self.dirty = True
        self.data[self.row][self.column] = value
