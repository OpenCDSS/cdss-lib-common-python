# TS - base class from which all time series are derived

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
# TS - base class from which all time series are derived
# see C++ version for difference notes.
# ----------------------------------------------------------------------------
# This is the abstract base class for all time series.
# The derived class hierarchy is then:
#
#              -----------------------TS-----------------------------
#              |           |        |          |                    |
#              V           V        V          V                    V
#           MinuteTS     HourTS   DayTS     MonthTS             IrregularTS
#              |           |                   |
#
#         ~~~~~~~~~~~~~~~~~~~Below have static read/write methods~~~~~~~~~~
#              |           |                   |
#              V           V                   V
#       HECDSSMinuteTS NWSCardTS          DateValueTS		etc.
#
# In general, the majority of the data members will be used for all derived
# time series.  However, some will not be appropriate.  The decision has been
# made to keep them here to make it less work to manage the first layer of
# derived classes.  For example, the irregular time series does not need to
# store _interval_mult.  Most of the other data still apply.
#
# Because this is a base class, anything derived from the class can only be as
# specific as the base class.  Therefore, routines to do conversions between
# time series types will have to be done outside of this class library.  Using
# the TS base class allows polymorphism when used by complicated objects.
#
# It is assumed that the first layer will define the best way to store the
# data.  In other words, different data intervals will have different storage
# methods.  The goal is not to conceptualize time series so much that they all
# consist of an array of date and data values.  For constant interval time
# series, the best performance will be to store the values in an ordered array
# that is indexed by month, etc.  If this assumption is wrong, then maybe the
# middle layer gets folded into the base class.
#
# It may be desirable to build some streaming control into this class.  For
# example, read multiple time series from the same file (for certain time
# series types) or may want to read one block of data from multiple files
# (e.g., when running a memory-sensitive application that only needs to have
# in memory one month of data for every time series in the system and reuses
# that space).  For now assume that we will always read the entire time series
# in but be aware that more control may be added later.
#
# New code does not have 3 layers.  Instead, I/O classes should have static
# methods like readTimeSeries, writeTimeSeries that operate on time series
# instances.  See DateValueTS for an example.  Older code may not follow this
# approach.
# ----------------------------------------------------------------------------
# History:
#
# Apr, May 96	Steven A. Malers, RTi	Start developing the library based on
#					the C version of the TS library.
# 10 Sep 96	SAM, RTi		Formalize the class enough so that we
#					can begin to use with the Operation
#					class to work on the DSS.
# 05 Feb 97	SAM, RTi		Add allocateDataSpace and setDataValue
#					virtual functions.  Add _dirty
#					so that we know when data has been
#					set (to indicate that we need to redo
#					calcMaxMin).  Add getDataPosition and
#					freeDataSpace.
# 26 May 97	SAM, RTi		Add writePersistentHeader.  To increase
#					performance in derived classes, make
#					more data members protected.  Also add
#					_data_date1 and _data_date2 to hold the
#					dates where we actually have data.
# 06 Jun 1997	SAM, RTi		Add a third position argument to
#					getDataPosition to work with the
#					MinuteTS data.  Other intervals will not
#					use the 2nd or 3rd positions.
#					Add TSIntervalFromString.
# 16 Jun 1997	MJR, RTi		Overloaded calcMaxMinValues to
#					find and return max and min between
#					two dates that are passed in.
# 03 Nov 1997  Daniel Weiler, RTi	Added GetPeriodFromTS function
# 26 Nov 1997	SAM, DKW, RTi		Add getValidPeriod.
# 14 Dec 1997	SAM, RTi		Add copyHeader.
# 06 Jan 1998	SAM, RTi		Update to use getDataLimits,
#					setDataLimits, refresh(), and change
#					data limits to _data_limits.  Put all
#					but the original dates and overal date
#					limits in _data_limits.
#					Add _sequence_number.
# 22 Feb 1998	SAM, RTi		Add _data_size to hold the total number
#					of elements allocated for data.
# 31 Mar 1998	SAM, DLG, RTi		Add _legend for use with output plots,
#					reports, etc.
# 28 Apr 1998	SAM, RTi		Add _status to allow general use by
#					other programs (e.g., to indicate that
#					the TS should not be used in a later
#					computation).
# 01 May 1998	SAM, RTi		Add _extended_legend for use with output
#					reports, etc.  Change so that
#					setComments resets the comments.
# 07 May 1998	SAM, RTi		Add formatHeader.
# 13 Jul 1998	SAM, RTi		Update copyHeader documentation.
# 23 Jul 1998	SAM, RTi		Add changePeriodOfRecord as "virtual"
#					function.  This needs to be implemented
#					at the storage level (next level of
#					extension).
# 06 Aug 1998	SAM, RTi		Remove getDataPosition, getDataPointer
#					from this class.  Those routines are
#					often not needed and should be private
#					to the derived classes.
# 20 Aug 1998	SAM, RTi		OK, realized that getDataPosition is
#					valuable for derived classes, but change
#					to return an array of integers with the
#					positions.  Make class abstract to
#					pass compile with 1.2.
# 18 Nov 1998	SAM, RTi		Add copyData method.
# 11 Jan 1998	SAM, RTi		Add routine name to virtual functions
#					so we can track down problems.
# 13 Apr 1999	SAM, RTi		Add finalize.  Add genesis format flag.
#					Change so addToGenesis does not
#					include routine name.
# 28 Jan 2000	SAM, RTi		Add setMissingRange() to allow handling
#					of -999 and -998 missing data values
#					in NWS work.
# 11 Oct 2000	SAM, RTi		Add iterator(), getDataPoint().
# 16 Oct 2000	SAM, RTi		Add _enabled, _selected, and _plot*
#					data to work with visualization.
# 13 Nov 2000	SAM, RTi		copyHeader() was not copying the
#					interval base.
# 20 Dec 2000	SAM, RTi		Add _data_limits_original, which is
#					currently just a convenience for code
#					(like tstool) so the original data
#					limits can be saved for use with
#					filling.  This may actually be a good
#					way to compare before and after data
#					statistics.  This data item is not a
#					copy of the limits (whereas the current
#					data limits object is a copy - the old
#					convention may be problematic).
# 28 Jan 2001	SAM, RTi		Update javadoc to not rely on @return.
#					Add checks for null strings when adding
#					to comments/genesis.  Add
#					allocateDataSpace() that takes period,
#					consistent with C++.  Make sure methods
#					are alphabetized.  Change so setDate*
#					methods set the precision of the date
#					to be appropriate for the time series
#					interval.
# 21 Feb 2001	SAM, RTi		Implement clone().  Add getInputName()
#					and setInputName().
# 31 May 2001	SAM, RTi		Use TSDate.setPrecision(TS) to ensure
#					start and end dates are the correct
#					precision in set*Date() methods.
# 28 Aug 2001	SAM, RTi		Fix the clone() method to be a deep
#					copy.
# 2001-11-05	SAM, RTi		Full review of javadoc.  Verify that
#					variables are set to null when no longer
#					used.  Change methods to have return
#					type of void where appropriate.
#					Change calculateDataSize() to be a
#					static method.  Remove the deprecated
#					readPersistent(), writePersistent()
#					methods.
# 2002-01-21	SAM, RTi		Remove the plot data.  This is now
#					handled in the TSGraph* code.  By
#					removing here, we decouple the plot
#					properties from the TS, eliminating
#					problems.
# 2002-01-30	SAM, RTi		Add _has_data_flags, _data_flag_length,
#					hasDataFlags(), and setDataValue(with
#					data flag and duration) to support data
#					flags and duration.  Flags should be
#					returned by using the getDataPoint()
#					method in derived classes.  Remove the
#					input stream flags and data - this has
#					never been used.  Fix copyHeader() to
#					do a deep copy on the TSIdent.
# 2002-02-17	SAM, RTi		Change the sequence number initial value
#					to -1.
# 2002-04-17	SAM, RTi		Update setGenesis() to have append flag.
# 2002-04-23	SAM, RTi		Deprecated getSelected() and
#					setSelected() in favor of isSelected().
#					Add %z to formatLegend() to use the
#					sequence number.
# 2002-06-03	SAM, RTi		Add support for NaN as missing data
#					value.
# 2002-06-16	SAM, RTi		Add isDirty() to help IrregularTS.
# 2002-08-12	J. Thomas Sapienza, RTi	Added calcDataDate for use with JTable
#					models.
# 2002-09-04	SAM, RTi		Remove calcDataDate() - same effect
#					can occur by a call to a TSDate.
#					Add getDataFlagLength() to allow
#					DateValueTS to output the flags.
#					Update javadoc to explain that
#					allocateDataSpace() and
#					changePeriodOfRecord() should handle the
#					data flag - previously hasDataFlag.
# 2002-11-25	SAM, RTi		Change getDate*() methods to return null
#					if the requested data are null.
# 2003-01-08	SAM, RTi		Add a hasData() method to indicate
#					whether the time series has data.
# 2003-06-02	SAM, RTi		Upgrade to use generic classes.
#					* Change TSDate to DateTime.
#					* Change TSUnits to DataUnits.
#					* Remove INTERVAL_* - TS package classes
#					  should use TimeInterval.* instead.
#					* Remove _date_type data member and
#					  associated DATES_* - they have never
#					  been used.
#					* Remove FORMAT_ since other classes
#					  handle formatting themselves.
#					* Remove the _data_type because it is
#					  stored in the TSIdent.
# 2003-07-24	SAM, RTi		* Fully remove commented out code for
#					  getDataDate() - it is not used by
#					  TSIterator any more and no other code
#					  uses.
#					* TSIterator constructor now throws an
#					  exception so declare throws here.
# 2003-08-21	SAM, RTi		* Change isSelected(boolean) back to
#					  setSelected() - ARG!
#					* Add isEditable() and setEditable().
#					* Remove deprecated constructor to take
#					  a String (filename) - extended classes
#					  should handle I/O.
#					* Remove deprecated addToGenesis() that
#					  took a routine name.
#					* Remove deprecated INFINITY - not used.
# 2004-01-28	SAM, RTi		* Change wording in text format header
#					  to more clearly identify original and
#					  current data period.
# 2004-03-04	J. Thomas Sapienza, RTi	* Class now implements serializable.
#					* Class now implements transferable.
# 2004-04-14	SAM, RTi		* Fix so that when setting the dates
#					  the original time zone precision
#					  information is not clobbered.
# 2004-11-23	SAM, RTi		* Move the sequence number to TSIdent
#					  since it is now part of the TSID.
#					* In formatLegend(), use instance data
#					  members instead of calling get()
#					  methods - performance increases.
# 2005-05-12	SAM, RTi		* Add allocateDataFlagSpace() to support
#					  enabling data flags after the initial
#					  allocation.
# 2006-10-03	SAM, RTi		* Add %p to formatLegend() for period.
# 2006-11-22	SAM, RTi		Fix but in addToComments() where the
#					wrong Vector was being used.
# 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
# ----------------------------------------------------------------------------
# EndHeader

import logging
import math
import sys

from RTi.TS.TSIdent import TSIdent
from RTi.Util.Time.DateTime import DateTime
from RTi.Util.Time.TimeInterval import TimeInterval


class TS(object):
    """
    This class is the base class for all time series classes.
    """

    # Data flavor for transferring this object.
    # tsFlavor = DataFlavor(RTi.TS.TS.class, "RTi.TS.TS")

    def __init__(self, ts=None):
        # General string to use for status of the time series (use as appropriate by
        # high-level code).  This value is volatile - do not assume its value will remain
        # for long periods.  This value is not used much now that the GRTS package has been updated.
        self._status = str()

        # Beginning date/time for data, at a precision appropriate for the data.
        # Missing data may be included in the period.
        self._date1 = DateTime()

        # Original starting date/time for data, at a precision appropriate for the data.
        # For example, this may be used to indicate the period in a database, which is
        # different than the period that was actually queried and saved in memory.
        self._date1_original = DateTime()

        # Original ending date/time for data, at a precision appropriate for the data.
        # For example, this may be used to indicate the period in a database, which is
        # different than the period that was actually queried and saved in memory.
        self._date2_original = DateTime()

        # The data interval base. See TimeInterval.HOUR, etc.
        self._data_interval_base = int()

        # The base interval multiplier (what to multiply _interval_base by to get the
        # real interval).  For example 15-minute data would have
        # _interval_base = TimeInterval.MINUTE and _interval_mult = 15.
        self._data_interval_mult = int()

        # The data interval in the original data source (for example, the source may be
        # in days but the current time series is in months).
        self._data_interval_base_original = int()

        # The data interval multiplier in the original data source.
        self._data_interval_mult_original = int()

        # Number of data values inclusive of _date1 and _date2.  Set in the
        # allocateDataSpace() method.  This is useful for general information.
        self._data_size = int()

        # Data units. A list of units and conversions is typically maintained in the DataUnits* classes.
        self._data_units = str()

        # Units in the original data source (e.g., the current data may be in CFS and the
        # original data were in CMS).
        self._data_units_original = str()

        # Indicates whether data flags are being used with data.  If enabled, the derived
        # classes that store data should override the allocateDataSpace(boolean, int)
        # method to create a data array to track the data flags.  It is recommended to
        # save space that the flags be handled using String.intern().
        self._has_data_flags = False

        # Indicate whether data flags should use String.intern()
        self._internDataFlagStrings = True

        # Version of the data format (mainly for use with flies).
        self._version = str()

        # Input source information.  Filename if read from file or perhaps a database
        # name and table (e.g., HydroBase.daily_flow).  This is the actual location read,
        # which should not be confused with the TSIdent storage name (which may not be fully expanded).
        self._input_name = str()

        # Time series identifier, which provides a unique and absolute handle on the time series.
        # An alias is provided within the TSIdent class.
        self._id = TSIdent()

        # Indicates whether the time series data have been modified by calling
        # setDataValue().  Call refresh() to update the limits.  This is not used with header data.
        self._dirty = bool()

        # Indicates whether the time series is editable.  This primarily applies to the
        # data (not the header information).  UI components can check to verify whether
        # users should be able to edit the time series.  It is not intended to be checked
        # by low-level code (manipulation is always granted).
        self._editable = False

        # A short description (e.g, "XYZ gage at ABC river").
        self._description = str()

        # Comments that describe the data.  This can be anything from an original data
        # source.  Sometimes the comments are created on the fly to generate a standard
        # header (e.g., describe drainage area).
        self._comments = []

        # List of metadata about data flags.  This provides a description about flags
        # encountered in the time series.
        self._dataFlagMetadataList = []

        # History of time series.  This is not the same as the comments but instead
        # chronicles how the time series is manipulated in memory.  For example the first
        # genesis note may be about how the time series was read.  The second may
        # indicate how it was filled.  Many TSUtil methods add to the genesis.
        self._genesis = []

        # TODO SAM 2010-09-21 Evaluate whether generic "Attributable" interface should be implemented instead.
        # Properties for the time series beyond the built-in properties.  For example, location
        # information like county and state can be set as a property.
        self.__property_HashMap = None

        # The missing data value. Default for some legacy formats is -999.0 but increasingly Double.NaN is used.
        self._missing = float()

        # Lower bound on the missing data value (for quick comparisons and when missing data ranges are used).
        self._missingl = float()

        # Upper bound on the missing data value (for quick comparisons and when missing data ranges are used).
        self._missingu = float()

        # Limits of the data. This also contains the date limits other than the original dates.
        #self._data_limits = TSLimits()

        # Limits of the original data. Currently only used by apps like TSTool.
        #self._data_limits_original = TSLimits()

        # Legend to show when plotting or tabulating a time series. This is generally a short legend.
        self._legend = str()

        # Legend to show when plotting or tabulating a time series.  This is usually a
        # long legend.  This may be phased out now that the GRTS package has been phased in for visualization.
        self._extended_legend = str()

        # Indicates whether time series is enabled (used to "comment" out of plots, etc).
        # This may be phased out.
        self._enabled = bool()

        # Indicates whether time series is selected (e.g., as result of a query).
        # Often time series might need to be programmatically selected (e.g., with TSTool
        # selectTimeSeries() command) to simplify output by other commands.
        self._selected = bool()

        self.initialize_TS()

    def addToGenesis(self, genesis):
        """
        Add a string to the genesis string list.  The genesis is a list of comments
        indicating how the time series was read and manipulated.  Genesis information
        should be added by methods that, for example, fill data and change the period.
        :param genesis: Comment string to add to genesis information.
        """
        if genesis is not None:
            self._genesis.append(genesis)

    def allocateDataSpace(self):
        """
        Allocate the data space for the time series.  This requires that the data
        interval base and multiplier are set correctly and that _date1 and _date2 have
        been set.  If data flags are used, hasDataFlags() should also be called before
        calling this method.  This method is meant to be overridden in derived classes
        (e.g., MinuteTS, MonthTS) that are optimized for data storage for different intervals.
        :return: 0 if successful allocating memory, non-zero if failure.
        """
        logger = logging.getLogger("StateMod")
        logger.warning("TS.allocateDataSpace() is virtual, define in derived classes.")
        return 1

    def getDate1(self):
        """
        Return the first date in the period of record (returns a copy).
        :return: The first date in the period of record, or None if the date is None
        """
        if self._date1 is None:
            return None
        return DateTime(dateTime=self._date1)

    def getDate1Original(self):
        """
        Return the first date in the original period of record (returns a copy).
        :return: The first date of the original data source (generally equal to or
        earlier than the time series that is actually read), or None if the data is None.
        """
        if self._date1_original is None:
            return None
        return DateTime(dateTime=self._date1_original)

    def getDate2(self):
        """
        Return the last date in the period of record (returns a copy).
        :return: The last date in the period of record, or None if the date is None.
        """
        if self._date2 is None:
            return None
        return DateTime(dateTime=self._date2)

    def getDate2Original(self):
        """
        Return the last date in the original period of record (returns a copy).
        :return: The last date of the original data source (generally equal to or
        later than the time series that is actually read), or null if the date is null.
        """
        if self._date2_original is None:
            return None
        return DateTime(dateTime=self._date2_original)

    def getIdentifier(self):
        """
        Return the time series identifier as TSIdent
        :return: the time series identifier as TSIdent
        """
        return self._id

    def getLocation(self):
        """
        Return the location part of the time series identifier. Does not include location type.
        :return: The location part of the time series identifier (from TSIdent).
        """
        return self._id.getLocation()

    def initialize_TS(self):
        """
        Initialize data members.
        """
        self._version = ""

        self._input_name = ""

        # Need to initialize an empty TSIdent...

        #self._id = TSIdent()
        self._legend = ""
        self._extended_legend = ""
        self._data_size = 0
        # DateTime need to be initialized somehow...
        # self.setDataType( "" )
        self._data_interval_base = 0
        self._data_interval_mult = 1
        self._data_interval_base_original = 1
        self._data_interval_mult_original = 0
        self.setDescription("")
        self._comments = []
        self._genesis = []
        self.setDataUnits("")
        self.setDataUnitsOriginal("")
        self.setMissing(-999.0)
        #self._data_limits = TSLimits()
        self._dirty = True
        self._enabled = True
        self._selected = False
        self._editable = False

    def setDataInterval(self, base, mult):
        """
        Set the data interval.
        :param base: Base interval (see TimeInterval.*)
        :param mult: Base interval multiplier.
        """
        self._data_interval_base = base
        self._data_interval_mult = mult

    def setDataIntervalOriginal(self, base, mult):
        """
        Set the data interval for the original data.
        :param base: Base interval (see TimeInterval.*)
        :param mult: Base interval multiplier.
        """
        self._data_interval_base_original = base
        self._data_interval_mult_original = mult

    def setDataSize(self, data_size):
        """
        Set the number of data points including the full period. This should be called by refresh()
        :param data_size: Number of data points in the time series.
        """
        self._data_size = data_size

    def setDataType(self, data_type):
        """
        Set the data type
        :param data_type: Data type abbreviation
        """
        if (data_type is not None) and (self._id is not None):
            self._id.setType(type=data_type)

    def setDataUnits(self, data_units):
        """
        Set the data units.
        :return: Data units abbreviation
        """
        if data_units is not None:
            self._data_units = data_units

    def setDataUnitsOriginal(self, units):
        """
        Set the data units for the original data.
        :param units: Data units abbreviation
        """
        if units is not None:
            self._data_units_original = units

    def setDate1(self, t):
        """
        Set the first date in the period.  A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: First date in period
        """
        if t is not None:
            self._date1 = DateTime(dateTime=t)
            if self._data_interval_base != TimeInterval.IRREGULAR:
                # For irregular, rely on the DateTime precision
                self._date1.setPrecision(self._data_interval_base)

    def setDate1Original(self, t):
        """
        Set the first date in the period in the original data.  A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: First date in period in the original data.
        """
        if t is not None:
            self._date1_original = DateTime(dateTime=t)
            if self._data_interval_base != TimeInterval.IRREGULAR:
                # For irregular, rely on the DateTime precision
                self._date1_original.setPrecision(self._data_interval_base)

    def setDate2(self, t):
        """
        Set the last date in the period.  A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: Last date in period
        """
        if t is not None:
            self._date2 = DateTime(dateTime=t)
            if self._data_interval_base != TimeInterval.IRREGULAR:
                self._date2.setPrecision(self._data_interval_base)

    def setDate2Original(self, t):
        """
        Set the last date in the period in the original data. A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: Last date in period in the original data.
        """
        if t is not None:
            self._date2_original = DateTime(dateTime=t)
            if self._data_interval_base != TimeInterval.IRREGULAR:
                # For irregular, rely on the DateTime precision.
                self._date2_original.setPrecision(self._data_interval_base)

    def setDescription(self, description):
        """
        Set the description
        :param description: Time series description (this is not the comments).
        """
        if description is not None:
            self._description = description

    def setIdentifier(self, id):
        """
        Note that this only sets the identifier but does not set the
        separate data fields (like data type).
        :param id: Time series identifier.
        """
        if id is not None:
            self._id = TSIdent(TSIdent=id)

    def setInputName(self, input_name):
        """
        Set the input name (file or database table)
        :param input_name: the input name
        """
        if input_name is not None:
            self._input_name = input_name

    def setMissing(self, missing):
        """
        Set the missing data value for the time series.  The upper and lower bounds
        of missing data are set to this value +.001 and -.001, to allow for precision truncation.
        The value is constrained to Double.MAX and Double.Min.
        :param missing: Missing data value for time series.
        """
        self._missing = missing
        if not math.isnan(missing):
            # Set the bounding limits also just to make sure that values like -999 are not treated as missing.
            self._missingl = math.nan
            self._missingu = math.nan
            return
        if missing == sys.float_info.max:
            self._missing1 = missing - .001
            self._missingu = missing
        else:
            # Set a range on the missing value check that is slightly on each side of the value
            self._missingl = missing - .001
            self._missingu = missing + .001

    def setProperty(self, propertyName, property):
        """
        Set a time series property's contents (case-specific).
        :param propertyName: name of property being set.
        :param property: property object corresponding to the property name.
        """
        if self.__property_HashMap is None:
            self.__property_HashMap = {}
        self.__property_HashMap[propertyName] = property