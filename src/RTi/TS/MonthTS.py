# MonthTS - base class from which all monthly time series are derived

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
# MonthTS - base class from which all monthly time series are derived
# ----------------------------------------------------------------------------
# Notes:	(1)	This base class is provided so that specific monthly
#			time series can derived from this class.
#		(2)	Data for this time series interval is stored as follows:
#
#			month in year  ->
#
#			------------------------
#              	|XX|  |.......|  |  |  |     first year in period
#			------------------------
#			|  |  |.......|  |  |  |
#			------------------------
#			|  |  |.......|  |  |  |
#			------------------------
#			|  |  |.......|  |  |  |
#			------------------------
#			.
#			.
#			.
#			------------------------
#			|  |  |.......|  |  |  |
#			------------------------
#			|  |  |.......|  |XX|XX|     last year in period
#			------------------------
#
#			The base block of storage is the year.  This lends
#			itself to very fast data retrieval but may waste some
#			memory for short time series in which full months are
#			not stored.  This is considered a reasonable tradeoff.
# ----------------------------------------------------------------------------
# History:
#
# 11 Mar 1997	Steven A. Malers, RTi	Copy HourTS and modify as appropriate.
# 06 Jun 1997	SAM, RTi		Add third positional argument to
#					getDataPosition to agree with the base
#					class.  It is not used here.
# 16 Jun 1997  MJR, RTi                Added overload of calcMaxMinValues.
# 09 Jan 1998	SAM, RTi		Update to agree with C++.
# 05 May 1998	SAM, RTi		Update formatOutput to have
#					UseCommentsForHeader.
# 06 Jul 1998	SAM, RTi		Eliminate the getDataPosition and
#					getDataPointer code and global data to
#					set the position data.  This class only
#					uses that internally.
# 12 Aug 1998	SAM, RTi		Update formatOutput.
# 20 Aug 1998	SAM, RTi		Add a new version of getDataPosition
#					that can be used by derived classes.
# 18 Nov 1998	SAM, RTi		Add copyData().
# 13 Apr 1999	SAM, RTi		Add finalize().
# 21 Feb 2001	SAM, RTi		Add clone().  Start setting unused
#					variables to null to improve memory use.
#					Update addGenesis().  Remove
#					printSample().  Remove
#					readPersistent*() and
#					writePersistent*().
# 04 May 2001	SAM, RTi		Recognize OutputPrecision property,
#					which is more consistent with TS
#					notation.
# 28 Aug 2001	SAM, RTi		Fix the clone() method and the copy
#					constructor.  Was not being rigorous
#					before.  Clean up Javadoc.
# 2001-11-06	SAM, RTi		Review javadoc.  Verify that variables
#					are set to null when no longer used.
#					Set return type for some methods to void
#					to agree with base class.  Remove
#					constructor that takes a file.
# 2003-01-08	SAM, RTi		Add hasData().
# 2003-02-05	SAM, RTi		Add support for data flags to be
#					consistent with DayTS.
# 2003-06-02	SAM, RTi		Upgrade to use generic classes.
#					* Change TSDate to DateTime.
#					* Change TSUnits to DataUnits.
#					* Change TS.INTERVAL* to TimeInterval.
# 2004-01-26	SAM, RTi		* Add OutputStart and OutputEnd
#					  properties to formatOutput().
#					* In formatOutput(), convert the file
#					  name to a full path.
# 2004-03-04	J. Thomas Sapienza, RTi	* Class now implements Serializable.
#					* Class now implements Transferable.
#					* Class supports being dragged or
#					  copied to clipboard.
# 2005-05-12	SAM, RTi		* Add allocateDataFlagSpace().
# 2005-05-16	SAM, RTi		* Update allocateDataFlagSpace() to
#					  resize in addition to simply
#					  allocating the array.
# 2005-06-02	SAM, RTi		* Cleanup in allocateDataFlagSpace() and
#					  allocateDataSpace() - a DateTime was
#					  being iterated unnecessarily, causing
#					  a performance hit.
#					* Add _tsdata to improve performance
#					  getting data points.
#					* Fix getDataPoint() to return a TSData
#					  with missing data if outside the
#					  period of record.
# 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
# ----------------------------------------------------------------------------
# EndHeader

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

        self._data = []  # This is the data space for the monthly values. The deminsions are [year][month]
        self._dataFlags = []  # Data flags for eah monthly value. The deminsions are [year][month]
        self._min_amon = int()  # Minimum absolute month stored.
        self._max_amon = int()  # Maximum absolute month stored.
        self._pos = []  # Use to return data without creating memory all the time.

        super().__init__()
        self.initialize_MonthTS()

    def initialize_MonthTS(self):
        """
        Initialize instance
        """
        self._data = [[]]
        self._data_interval_base = TimeInterval.MONTH
        self._data_interval_mult = 1
        self._data_interval_base_original = TimeInterval.MONTH
        self._data_interval_mult_original = 1
        self._pos = [int()] * 2
        self._pos[0] = 0
        self._pos[1] = 0
        self._min_amon = 0
        self._max_amon = 0

    def setDataValue(self, date, value):
        """
        Set the data value for the specified date.
        :param date: Date of interest
        :param value: Value corresponding to date.
        """
        # Do not define routine here to increase performance.

        # Check the date coming in...

        if date is not None:
            return

        amon = date.getAbsoluteMonth()

        if (amon < self._min_amon) or (amon > self._max_amon):
            # Print within debug to optimize performance...
            return

        # THIS CODE NEEDS TO BE EQUIVELENT IN setDataValue...

        row = date.getYear() - self._date1.getYear()
        column = date.getMonth() - 1  # Zero offset!

        # ... END OF EQUIVELENT CODE.

        # Set the dirty flag so that we know to recompute the limits if desired...
        self._dirty = True
        self._data[row][column] = value