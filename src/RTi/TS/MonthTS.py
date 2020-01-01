# MonthTS - base class from which all monthly time series are derived

# NoticeStart

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

# ----------------------------------------------------------------------------
# MonthTS - base class from which all monthly time series are derived
# ----------------------------------------------------------------------------
# Notes:	(1)	This base class is provided so that specific monthly
#           time series can derived from this class.
#           (2)	Data for this time series interval is stored as follows:
#
#           month in year  ->
#
#           ------------------------
#          	|XX|  |.......|  |  |  |     first year in period
#           ------------------------
#           |  |  |.......|  |  |  |
#           ------------------------
#           |  |  |.......|  |  |  |
#           ------------------------
#           |  |  |.......|  |  |  |
#           ------------------------
#           .
#           .
#           .
#           ------------------------
#           |  |  |.......|  |  |  |
#           ------------------------
#           |  |  |.......|  |XX|XX|     last year in period
#           ------------------------
#
#           The base block of storage is the year.  This lends
#           itself to very fast data retrieval but may waste some
#           memory for short time series in which full months are
#           not stored.  This is considered a reasonable tradeoff.
# ----------------------------------------------------------------------------

import logging

from RTi.TS.TS import TS
from RTi.Util.Time.TimeInterval import TimeInterval


class MonthTS(TS):
    """
    The MonthTS class is the base class for monthly time series.  Derive from this
    class for specific monthly time series formats (override allocateDataSpace() to control memory management).
    """

    # The DataFlavor for transferring this specific class.
    # dayTSFlavor = DataFlavor(RTi.TS.DayTS.class, "RTi.TS.DayTS")

    def __init__(self):
        # Data members...

        self.data = []  # This is the data space for the monthly values. The deminsions are [year][month]
        self.data_flags = []  # Data flags for eah monthly value. The deminsions are [year][month]
        self.min_amon = int()  # Minimum absolute month stored.
        self.max_amon = int()  # Maximum absolute month stored.
        self.pos = []  # Use to return data without creating memory all the time.

        super().__init__()
        self.initialize_monthts()

    def initialize_monthts(self):
        """
        Initialize instance
        """
        self.data = [[]]
        self.data_interval_base = TimeInterval.MONTH
        self.data_interval_mult = 1
        self.data_interval_base_original = TimeInterval.MONTH
        self.data_interval_mult_original = 1
        self.pos = [int()] * 2
        self.pos[0] = 0
        self.pos[1] = 0
        self.min_amon = 0
        self.max_amon = 0

    def allocate_data_space(self, value=None):
        """
        Allocate the data space for the time series.  The start and end dates and the
        data interval multiplier must have been set.  Fill with the specified data value.
        :param value: Value to initialize data space, if None default to time series missing
        :return: 1 if the allocation fails, 0 if success.
        """
        logger = logging.getLogger(__name__)

        if not value:
            value = self.missing

        if not self.date1 or not self.date2:
            logger.warning("Dates have not been set. Cannot allocate data space.")
            return 1
        if self.data_interval_mult != 1:
            # Do not know how to handle N-month interval...
            logger.warning("Only know how to handle 1 month data, not " + str(self.data_interval_mult) + "-month")
            return 1

        nyears = self.date2.get_year() - self.date1.get_year()

        if nyears == 0:
            logger.warning("TS has 0 years POR, maybe dates haven't been set yet")
            return 1

        self.data = [[float()]]*nyears
        if self.has_data_flags:
            self.data_flags = [[str()]]*nyears

        # Allocate memory...

        nvals = 12
        for i_year in range(nyears):
            self.data[i_year] = [float()]*nvals
            if self.has_data_flags:
                self.data_flags[i_year] = [str()]*nvals

            # Now fill with the missing data value...

            for i_month in range(nvals):
                self.data[i_year][i_month] = value
                if self.has_data_flags:
                    self.data_flags[i_year][i_month] = ""

        # Set the data size...
        datasize = MonthTS.calculate_data_size(self.date1, self.date2, self.data_interval_mult)
        self.set_data_size(datasize)

        # Set the limits used for set/get routines...
        self.min_amon = self.date1.get_absolute_month()
        self.max_amon = self.date2.get_absolute_month()

        return 0

    @staticmethod
    def calculate_data_size(start_date, end_date, interval_mult):
        """
        Calculate and return the number of data points that have been allocated.
        :param start_date: Teh first date of the period.
        :param end_date: The last date of the period.
        :param interval_mult: The time series data interval multiplier.
        :return: The number of data points for a month time series
        given the data interval multiplier for the specified period, including missing data.
        """
        logger = logging.getLogger(__name__)

        if start_date is None:
            logger.warning("Start date is null")
            return 0
        if end_date is None:
            logger.warning("End date is null")
            return 0
        if interval_mult != 1:
            logger.warning("Do no know how to handle N-month time series")
            return 0

        datasize = end_date.get_absolute_month() - start_date.get_absolute_month() + 1
        return datasize

    def set_data_value(self, date, value):
        """
        Set the data value for the specified date.
        :param date: Date of interest
        :param value: Value corresponding to date.
        """
        # Do not define routine here to increase performance.

        # Check the date coming in...

        if date is not None:
            return

        amon = date.get_absolute_month()

        if (amon < self.min_amon) or (amon > self.max_amon):
            # Print within debug to optimize performance...
            return

        # THIS CODE NEEDS TO BE EQUIVELENT IN set_data_value...

        row = date.get_year() - self.date1.get_year()
        column = date.get_month() - 1  # Zero offset!

        # ... END OF EQUIVELENT CODE.

        # Set the dirty flag so that we know to recompute the limits if desired...
        self.dirty = True
        self.data[row][column] = value
