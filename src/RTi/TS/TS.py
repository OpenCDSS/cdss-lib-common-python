# TS - base class from which all time series are derived

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

# ----------------------------------------------------------------------------
# TS - base class from which all time series are derived
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

    def __init__(self, ts=None):
        # General string to use for status of the time series (use as appropriate by
        # high-level code).  This value is volatile - do not assume its value will remain
        # for long periods.  This value is not used much now that the GRTS package has been updated.
        self.status = None

        # Beginning date/time for data, at a precision appropriate for the data.
        # Missing data may be included in the period.
        self.date1 = None

        # Original starting date/time for data, at a precision appropriate for the data.
        # For example, this may be used to indicate the period in a database, which is
        # different than the period that was actually queried and saved in memory.
        self.date1_original = None

        # Ending date/time for data, at a precision appropriate for the data.
        # Missing data may be included in the period.
        self.date2 = None

        # Original ending date/time for data, at a precision appropriate for the data.
        # For example, this may be used to indicate the period in a database, which is
        # different than the period that was actually queried and saved in memory.
        self.date2_original = None

        # The data interval base. See TimeInterval.HOUR, etc.
        self.data_interval_base = None

        # The base interval multiplier (what to multiply _interval_base by to get the
        # real interval).  For example 15-minute data would have
        # _interval_base = TimeInterval.MINUTE and _interval_mult = 15.
        self.data_interval_mult = None

        # The data interval in the original data source (for example, the source may be
        # in days but the current time series is in months).
        self.data_interval_base_original = None

        # The data interval multiplier in the original data source.
        self.data_interval_mult_original = None

        # Number of data values inclusive of _date1 and _date2.  Set in the
        # allocate_data_space() method.  This is useful for general information.
        self.data_size = None

        # Data units. A list of units and conversions is typically maintained in the DataUnits* classes.
        self.data_units = None

        # Units in the original data source (e.g., the current data may be in CFS and the
        # original data were in CMS).
        self.data_units_original = None

        # Indicates whether data flags are being used with data.  If enabled, the derived
        # classes that store data should override the allocate_data_space(boolean, int)
        # method to create a data array to track the data flags.  It is recommended to
        # save space that the flags be handled using String.intern().
        self.has_data_flags = False

        # Indicate whether data flags should use String.intern()
        # - used in Java to reuse string instances
        # self.internDataFlagStrings = True

        # Version of the data format (mainly for use with flies).
        self.version = None

        # Input source information.  Filename if read from file or perhaps a database
        # name and table (e.g., HydroBase.daily_flow).  This is the actual location read,
        # which should not be confused with the TSIdent storage name (which may not be fully expanded).
        self.input_name = None

        # Time series identifier, which provides a unique and absolute handle on the time series.
        # An alias is provided within the TSIdent class.
        self.tsid = TSIdent()

        # Indicates whether the time series data have been modified by calling
        # setDataValue().  Call refresh() to update the limits.  This is not used with header data.
        self.dirty = None

        # Indicates whether the time series is editable.  This primarily applies to the
        # data (not the header information).  UI components can check to verify whether
        # users should be able to edit the time series.  It is not intended to be checked
        # by low-level code (manipulation is always granted).
        self.editable = False

        # A short description (e.g, "XYZ gage at ABC river").
        self.description = None

        # Comments that describe the data.  This can be anything from an original data
        # source.  Sometimes the comments are created on the fly to generate a standard
        # header (e.g., describe drainage area).
        self.comments = []

        # List of metadata about data flags.  This provides a description about flags
        # encountered in the time series.
        self.dataFlagMetadataList = []

        # History of time series.  This is not the same as the comments but instead
        # chronicles how the time series is manipulated in memory.  For example the first
        # genesis note may be about how the time series was read.  The second may
        # indicate how it was filled.  Many TSUtil methods add to the genesis.
        self.genesis = []

        # TODO SAM 2010-09-21 Evaluate whether generic "Attributable" interface should be implemented instead.
        # Properties for the time series beyond the built-in properties.  For example, location
        # information like county and state can be set as a property.
        self.property_HashMap = None

        # The missing data value. Default for some legacy formats is -999.0 but increasingly Double.NaN is used.
        self.missing = None

        # Lower bound on the missing data value (for quick comparisons and when missing data ranges are used).
        self.missingl = None

        # Upper bound on the missing data value (for quick comparisons and when missing data ranges are used).
        self.missingu = None

        # Limits of the data. This also contains the date limits other than the original dates.
        # self.data_limits = TSLimits()

        # Limits of the original data. Currently only used by apps like TSTool.
        # self.data_limits_original = TSLimits()

        # Legend to show when plotting or tabulating a time series. This is generally a short legend.
        self.legend = None

        # Legend to show when plotting or tabulating a time series.  This is usually a
        # long legend.  This may be phased out now that the GRTS package has been phased in for visualization.
        self.extended_legend = None

        # Indicates whether time series is enabled (used to "comment" out of plots, etc).
        # This may be phased out.
        self.enabled = None

        # Indicates whether time series is selected (e.g., as result of a query).
        # Often time series might need to be programmatically selected (e.g., with TSTool
        # selectTimeSeries() command) to simplify output by other commands.
        self.selected = None

        self.initialize()

    def add_to_genesis(self, genesis):
        """
        Add a string to the genesis string list.  The genesis is a list of comments
        indicating how the time series was read and manipulated.  Genesis information
        should be added by methods that, for example, fill data and change the period.
        :param genesis: Comment string to add to genesis information.
        """
        if genesis is not None:
            self.genesis.append(genesis)

    def allocate_data_space(self):
        """
        Allocate the data space for the time series.  This requires that the data
        interval base and multiplier are set correctly and that _date1 and _date2 have
        been set.  If data flags are used, hasDataFlags() should also be called before
        calling this method.  This method is meant to be overridden in derived classes
        (e.g., MinuteTS, MonthTS) that are optimized for data storage for different intervals.
        :return: 0 if successful allocating memory, non-zero if failure.
        """
        logger = logging.getLogger(__name__)
        logger.warning("TS.allocate_data_space() is virtual, define in derived classes.")
        return 1

    def get_date1(self):
        """
        Return the first date in the period of record (returns a copy).
        :return: The first date in the period of record, or None if the date is None
        """
        if self.date1 is None:
            return None
        return DateTime(date_time=self.date1)

    def get_date1_original(self):
        """
        Return the first date in the original period of record (returns a copy).
        :return: The first date of the original data source (generally equal to or
        earlier than the time series that is actually read), or None if the data is None.
        """
        if self.date1_original is None:
            return None
        return DateTime(date_time=self.date1_original)

    def get_date2(self):
        """
        Return the last date in the period of record (returns a copy).
        :return: The last date in the period of record, or None if the date is None.
        """
        if self.date2 is None:
            return None
        return DateTime(date_time=self.date2)

    def get_date2_original(self):
        """
        Return the last date in the original period of record (returns a copy).
        :return: The last date of the original data source (generally equal to or
        later than the time series that is actually read), or null if the date is null.
        """
        if self.date2_original is None:
            return None
        return DateTime(date_time=self.date2_original)

    def get_identifier(self):
        """
        Return the time series identifier as TSIdent
        :return: the time series identifier as TSIdent
        """
        return self.tsid

    def get_location(self):
        """
        Return the location part of the time series identifier. Does not include location type.
        :return: The location part of the time series identifier (from TSIdent).
        """
        return self.tsid.get_location()

    def initialize(self):
        """
        Initialize data members.
        """
        self.version = ""

        self.input_name = ""

        # Need to initialize an empty TSIdent...

        # self.tsid = TSIdent()
        self.legend = ""
        self.extended_legend = ""
        self.data_size = 0
        # DateTime need to be initialized somehow...
        # self.set_data_type( "" )
        self.data_interval_base = 0
        self.data_interval_mult = 1
        self.data_interval_base_original = 1
        self.data_interval_mult_original = 0
        self.set_description("")
        self.comments = []
        self.genesis = []
        self.set_data_units("")
        self.set_data_units_original("")
        self.set_missing(-999.0)
        # self.data_limits = TSLimits()
        self.dirty = True
        self.enabled = True
        self.selected = False
        self.editable = False

    def set_data_interval(self, base, mult):
        """
        Set the data interval.
        :param base: Base interval (see TimeInterval.*)
        :param mult: Base interval multiplier.
        """
        self.data_interval_base = base
        self.data_interval_mult = mult

    def set_data_interval_original(self, base, mult):
        """
        Set the data interval for the original data.
        :param base: Base interval (see TimeInterval.*)
        :param mult: Base interval multiplier.
        """
        self.data_interval_base_original = base
        self.data_interval_mult_original = mult

    def set_data_size(self, data_size):
        """
        Set the number of data points including the full period. This should be called by refresh()
        :param data_size: Number of data points in the time series.
        """
        self.data_size = data_size

    def set_data_type(self, data_type):
        """
        Set the data type
        :param data_type: Data type abbreviation
        """
        if (data_type is not None) and (self.tsid is not None):
            self.tsid.set_type(type=data_type)

    def set_data_units(self, data_units):
        """
        Set the data units.
        :return: Data units abbreviation
        """
        if data_units is not None:
            self.data_units = data_units

    def set_data_units_original(self, units):
        """
        Set the data units for the original data.
        :param units: Data units abbreviation
        """
        if units is not None:
            self.data_units_original = units

    def set_date1(self, t):
        """
        Set the first date in the period.  A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: First date in period
        """
        if t is not None:
            self.date1 = DateTime(date_time=t)
            if self.data_interval_base != TimeInterval.IRREGULAR:
                # For irregular, rely on the DateTime precision
                self.date1.set_precision(self.data_interval_base)

    def set_date1_original(self, t):
        """
        Set the first date in the period in the original data.  A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: First date in period in the original data.
        """
        if t is not None:
            self.date1_original = DateTime(date_time=t)
            if self.data_interval_base != TimeInterval.IRREGULAR:
                # For irregular, rely on the DateTime precision
                self.date1_original.set_precision(self.data_interval_base)

    def set_date2(self, t):
        """
        Set the last date in the period.  A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: Last date in period
        """
        if t is not None:
            self.date2 = DateTime(date_time=t)
            if self.data_interval_base != TimeInterval.IRREGULAR:
                self.date2.set_precision(self.data_interval_base)

    def set_date2_original(self, t):
        """
        Set the last date in the period in the original data. A copy is made.
        The date precision is set to the precision appropriate for the time series.
        :param t: Last date in period in the original data.
        """
        if t is not None:
            self.date2_original = DateTime(date_time=t)
            if self.data_interval_base != TimeInterval.IRREGULAR:
                # For irregular, rely on the DateTime precision.
                self.date2_original.set_precision(self.data_interval_base)

    def set_description(self, description):
        """
        Set the description
        :param description: Time series description (this is not the comments).
        """
        if description is not None:
            self.description = description

    def set_identifier(self, tsid):
        """
        Note that this only sets the identifier but does not set the
        separate data fields (like data type).
        :param tsid: Time series identifier.
        """
        if tsid is not None:
            self.tsid = TSIdent(TSIdent=tsid)

    def set_input_name(self, input_name):
        """
        Set the input name (file or database table)
        :param input_name: the input name
        """
        if input_name is not None:
            self.input_name = input_name

    def set_missing(self, missing):
        """
        Set the missing data value for the time series.  The upper and lower bounds
        of missing data are set to this value +.001 and -.001, to allow for precision truncation.
        The value is constrained to Double.MAX and Double.Min.
        :param missing: Missing data value for time series.
        """
        self.missing = missing
        if not math.isnan(missing):
            # Set the bounding limits also just to make sure that values like -999 are not treated as missing.
            self.missingl = math.nan
            self.missingu = math.nan
            return
        if missing == sys.float_info.max:
            self.missingl = missing - .001
            self.missingu = missing
        else:
            # Set a range on the missing value check that is slightly on each side of the value
            self.missingl = missing - .001
            self.missingu = missing + .001

    def set_property(self, property_name, property_value):
        """
        Set a time series property's contents (case-specific).
        :param property_name: name of property being set.
        :param property_value: property object corresponding to the property name.
        """
        if self.property_HashMap is None:
            self.property_HashMap = {}
        self.property_HashMap[property_name] = property_value
