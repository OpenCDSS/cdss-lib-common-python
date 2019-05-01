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
#			time series can derive from this class.
#		(2)	Data for this time series interval is stored as follows:
#
#			day within month  ->
#
#			------------------------
#              	|  |  |.......|  |  |  |     first month in period
#			------------------------
#			|  |  |.......|  |  |
#			------------------------
#			|  |  |.......|  |  |  |
#			------------------------
#			|  |  |.......|  |  |
#			---------------------
#			.
#			.
#			.
#			------------------------
#			|  |  |.......|  |  |  |
#			------------------------
#			|  |  |.......|  |  |        last month in period
#			---------------------
#
#			The base block of storage is the month.  This lends
#			itself to very fast data retrieval but may waste some
#			memory for short time series in which full months are
#			not stored.  This is considered a reasonable tradeoff.
# ----------------------------------------------------------------------------
# History:
#
# 09 Apr 1998	Steven A. Malers, RTi	Copy the HourTS code and modify as
#					necessary.  Start to use this instead
#					of a 24-hour time series to make
#					storage more straightforward.
# 22 Aug 1998	SAM, RTi		In-line up getDataPosition in this
#					class to increase performance. Change
#					so that getDataPosition returns an
#					array.
# 09 Jan 1999	SAM, RTi		Add more exception handling due to
#					changes in other classes.
# 05 Apr 1999	CEN, RTi		Optimize by adding _row, _column,
#					similar to HourTS.
# 21 Apr 1999	SAM, RTi		Add precision lookup for formatOutput.
#					Add genesis to output.
# 09 Aug 1999	SAM, RTi		Add changePeriodOfRecord to support
#					regression.
# 21 Feb 2001	SAM, RTi		Add clone().  Add copy constructor.
#					Remove printSample(), read and write
#					methods.
# 04 May 2001	SAM, RTi		Add OutputPrecision property, which is
#					more consistent with TS notation.
# 29 Aug 2001	SAM, RTi		Fix clone() to work correctly.  Remove
#					old C-style documentation.  Change _pos
#					from static - trying to minimize the
#					amount of static data that is used.
# 2001-11-06	SAM, RTi		Review javadoc.  Verify that variables
#					are set to null when no longer used.
#					Remove constructor that takes a file
#					name.  Change some methods to have void
#					return type to agree with base class.
# 2002-01-31	SAM, RTi		Add support for data flags.  Change so
#					getDataPoint() returns a reference to an
#					internal object that is reused.
# 2002-05-24	SAM, RTi		Add total period statistics for each
#					month.
# 2002-09-05	SAM, RTi		Remove hasDataFlags().  Let the base TS
#					class method suffice.  Change so that
#					hasDataFlags() does not allocate the
#					data flags memory but instead do it in
#					allocateDataSpace().
# 2003-01-08	SAM, RTi		Add hasData().
# 2003-05-02	SAM, RTi		Fix bug in getDataPoint() - was not
#					recalculationg the row/column position
#					for the data flag.
# 2003-06-02	SAM, RTi		Upgrade to use generic classes.
#					* Change TSDate to DateTime.
#					* Change TSUnits to DataUnits.
#					* Change TS.INTERVAL* to TimeInterval.
# 2003-10-21	SAM, RTi		Overload allocateDataSpace(), similar
#					to MonthTS to take an initial value.
# 2003-12-09	SAM, RTi		* Handle data flags in clone().
# 2004-01-26	SAM, RTi		* Add OutputStart and OutputEnd
#					  properties to formatOutput().
#					* In formatOutput(), convert the file
#					  name to a full path.
# 2004-03-04	J. Thomas Sapienza, RTi	* Class now implements Serializable.
#					* Class now implements Transferable.
#					* Class supports being dragged or
#					  copied to clipboard.
# 2005-06-02	SAM, RTi		* Add allocateDataFlagSpace(), similar
#					  to MonthTS.
#					* Remove warning about reallocating data
#					  space.
# 2005-12-07	JTS, RTi		Added copy constructor to create a DayTS
#					from an HourTS.
# 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
# ----------------------------------------------------------------------------
# EndHeader

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

        self._data = [[]]  # This is the data space for daily time series.
        self._dataFlags = []  # Data flags
        self._pos = []  # Used to optimize performance when getting data.
        self._row = int()  # Row position in data.
        self._column = int()  # column position in data

        super().__init__()
        self.initialize_DayTS()

    def allocateDataSpace(self):
        """
        Allocate the data space for the time series.  The start and end dates and the
        data interval multiplier must have been set.  Initialize the space with the missing data value.
        """
        self.allocateDataSpaceFromNum(self._missing)

    def allocateDataSpaceFromNum(self, value):
        """
        Allocate the data space.  The start and end dates and the interval multiplier should have been set.
        :param value: The value to initialize the time series.
        :return: 0 if successful, 1 if failure.
        """
        logger = logging.getLogger("StateMod")
        routine = "DayTS.allocateDataSpace"
        ndays_in_month = int()
        nmonths = 0
        nvals = int()

        if (self._date1 == None) or (self._date2 == None):
            logger.warning("No dates set for memory allocation.")
            return 1
        if self._data_interval_mult != 1:
            # Do not know how to handle N-day interval...
            message = "Only know how to handle 1-day data, not " + str(self._data_interval_mult) + "Day"
            logger.warning(message)
            return 1

        if nmonths == 0:
            logger.warning("TS has 0 months POR, maybe dates haven't been set yet")
            return 1

        self._data = [[float()]]*nmonths
        if self._has_data_flags:
            self._dataFlags = [[str()]]*nmonths

        # May need to catch an exception here in case we run out of memory.

        # Set the counter date to match the starting month. This data is used to
        # to determine the number of days in each month.

        date = DateTime(DateTime.DATE_FAST)
        date.setMonth(self._date1.getMonth())
        date.setYear(self._date1.getYear())

        iday = 0
        for imon in range(nmonths):
            ndays_in_month = TimeUtil.numDaysInMonthFromDateTime(date)
            # Handle 1-day data, otherwise an excpetion was thrown above.
            # Here would change the number of values if N-day was supported.
            nvals = ndays_in_month
            self._data[imon] = [float()]*nvals

            # Now fill with the missing data value for each day in month...

            for iday in range(nvals):
                self._data[imon][iday] = value
                if self._has_data_flags:
                    self._dataFlags[imon][iday] = ""

            date.addMonth(1)

        nactual = DayTS.calculateDataSize(self._date1, self._date2, self._data_interval_mult)
        self.setDataSize(nactual)

        date = None
        routine = None
        return 0

    @staticmethod
    def calculateDataSize(start_date, end_date, interval_mult):
        """
        Determine the number of points between two dates for the given interval multiplier.
        :param start_date: The first date of the period.
        :param end_date: The last date of the period.
        :param interval_mult: The time series data interval multiplier.
        :return: The number of data points for a day time series
        given the data interval multiplier for the specified period.
        """
        logger = logging.getLogger("StateMod")
        routine = "DayTS.calculateDataSize"
        datasize = 0

        if start_date == None:
            logger.warning("Start date is null")
            return 0
        if end_date == None:
            logger.warning("End date is null")
            return 0
        if interval_mult > 1:
            logger.warning("Greater than 1-day TS not supported")
            return 0

        # First set to the number of data in the months...
        datasize = TimeUtil.numDaysInMonths(start_date.getMonth(), start_date.getYear(), end_date.getMonth(), end_date.getYear())
        # Now subtract off the data at the ends that are missing...
        # Start by subtracting the full day at the beginning of the month is not included...
        datasize -= (start_date.getDay() - 1)
        # Now subtract off the data at the end...
        # Start by subtracting the full days off the end of the month...
        ndays_in_month = TimeUtil.numDaysInMonth(end_date.getMonth(), end_date.getYear())
        datasize -= (ndays_in_month - end_date.getDay())
        routine = None
        return datasize


    def initialize_DayTS(self):
        """
        Initialize data members
        """
        self._data = None
        self._data_interval_base = TimeInterval.DAY
        self._data_interval_mult = 1
        self._data_interval_base_original = TimeInterval.DAY
        self._data_interval_mult_original = 1
        self._pos = [int()] * 2
        self._pos[0] = 0
        self._pos[1] = 0
        self._row = 0
        self._column = 0

    def getDataPosition(self, date):
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

        self._row = date.getAbsoluteMonth() - self._date1.getAbsoluteMonth()

        # Calculate the column position of the data. We know that daily data
        # is stored in a 2 deminsional array with the column being the daily data by interval.

        self._column = date.getDay() - 1

        self._pos[0] = self._row
        self._pos[1] = self._column
        return self._pos

    def setDataValue(self, date, value):
        """
        Set the data value for the date.
        :param date: Date of interest
        :param value: Data value corresponding to date.
        """
        if date.lessThan(self._date1) or date.greaterThan(self._date2):
            return
        self.getDataPosition(date)
        # Set the dirty flag so that we know to recompute the limits if desired...
        self._dirty = True
        self._data[self._row][self._column] = value