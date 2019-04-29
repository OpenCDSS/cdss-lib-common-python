# TSUtil - utility functions for TS

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

#------------------------------------------------------------------------------
# TSUtil - utility functions for TS
#------------------------------------------------------------------------------
# Copyright:	See the COPYRIGHT file.
#------------------------------------------------------------------------------
# Notes:	(1)	These are static data functions.  They are outside of
#			TS so that we do not end up with a huge TS class and
#			also to remove some of the circular dependency that
#			would result (TS having MonthTS instances, etc.)
#------------------------------------------------------------------------------
# History:
#
# 14 Dec 1997	Steven A. Malers, RTi	Initial version of code.
# 13 Mar 1998	SAM, RTi		This code has been getting modified to
#					pull in C++ routines.  Continue to do
#					that and change the changeInterval code
#					to accept a PropList rather than a
#					bit mask.
# 25 Mar 1998	SAM, RTi		Add areUnitsCompatible.
# 05 Apr 1998	SAM, RTi		Add formatOutput, areIntervalsSame.
# 03 May 1998	SAM, RTi		Add generic fill that can handle several
#					fill methods at each time step.
# 20 May 1998	CEN, RTi		Add toArray.
# 26 May 1998	SAM, RTi		Add fillMonthly.
# 29 May 1998	CEN, RTi		Add fillRegressLinear.
# 01 Jun 1998	CEN, RTi		Add fillRegressLinear12.
# 14 Jun 1998	SAM, RTi		Change fillMonthly to
#					fillConstantByMonth.
# 17 Jun 1998	SAM, RTi		Change fillMonthlyIfMissing to
#					fillMonthly.
# 17 Jun 1998	CEN, RTi		Add changePeriodOfRecord.
# 21 Jun 1998	SAM, RTi		Add fillCarryForward.
# 26 Jun 1998	SAM, RTi		Realized that the change in Oct 1997
#					where we initialize TSDates to the
#					current time is not compatible with much
#					of this code.  Mixing those time series
#					with zerod time series results in loops
#					sometimes not handling the first and
#					last dates.  Change all the new TSDate
#					calls here to use the DATE_ZERO flag.
# 01 Jul 1998	SAM, RTi		Add enforceLimits.
# 23 Jul 1998	SAM, RTi		Removed changePeriodOfRecord.  CEN had
#					appropriately moved to the MonthTS
#					class (because it is associated with
#					data storage).  Add
#					createPeriodOfRecordTS.
# 20 Aug 1998	SAM, RTi		Complete toArray* methods.  Optimize
#					getDataLimits some.
# 31 Aug 1998	SAM, RTi		Change fillConstant to only fill
#					missing and add setConstant.
# 30 Sep 1998	SAM, RTi		Update fill to accept a property with
#					the monthly averages.
# 06 Nov 1998	SAM, RTi		Change TSRegressionData to TSRegression
#					and modify its use.  Add findTSFile.
# 04 Dec 1998	SAM, RTi		Update with new regression fill code.
# 02 Jan 1999	SAM, RTi		Add mean and sum to TSLimits data.
#					Add wrapper exception handling to many
#					methods (except the low-level
#					changeInterval code - too many!).
#					Fix bug where getDataLimits was getting
#					the wrong overall dates because a
#					TSDate was being reused.  Add
#					AVAILABLE_POR flag.
# 10 Mar 1999	SAM, RTi		Update so if filling using regression
#					and the independent value is zero,
#					use .001 as the observed value.
# 12 Apr 1999	SAM, RTi		Fill in DayTS change interval methods.
#					Add other features to support DayTS.
#					Update genesis calls.  Fix so that
#					if regression data are not available
#					for a month, the month is skipped.
# 10 Jun 1999	SAM, RTi		Add numIntervalsInMonth().
# 26 Jul 1999	SAM, RTi		Add fillInterpolate() and
#					changeInterval() to convert daily to
#					monthly using nearest end value.
# 09 Aug 1999	SAM, RTi		Enable linear and log regression for
#					daily time series.
# 28 Oct 1999	SAM, RTi		Add ability to ignore <= 0 values in
#					fill pattern averaging.
# 04 Dec 1999	SAM, RTi		Fix bug where in fill() the monthly
#					average fill would break out of filling
#					even if a missing data value was in the
#					historic averages.
# 25 Sep 2000	SAM, RTi		Add newTimeSeries, similar to C++.
# 11 Oct 2000	SAM, RTi		Add getTracesFromTS().
# 28 Oct 2000	SAM, RTi		Add normalize().
# 01 Nov 2000	SAM, RTi		Add findTS().
# 13 Nov 2000	SAM, RTi		Add another overload to getMonthTotals()
#					to support efficiency calculations.
# 18 Dec 2000	SAM, RTi		Change findTS() to indexOf().
# 31 Dec 2000	SAM, RTi		Update so the following change the
#					decriptions of the output time series
#					and (*) allow the calling code to
#					specify the description string:
#						createRunningAverageTS()
#						* fillConstantByMonth()
#						* fillRegress()
#						scale()
# 15 Jan 2001	SAM, RTi		Continue above with:
#						fillConstant()
#					Replace deprecated IO with IOUtil.
#					Calls to addToGenesis now do not have
#					routine.  Update add() and subtract()
#					to have missing data flag.
# 24 Jul 2001	SAM, RTi		Add parameter to indexOf() to allow
#					search in either direction.
# 25 Feb 2001	SAM, RTi		Update fillInterpolate() to have a
#					parameter indicating maximum number of
#					timesteps to interpolate and add an
#					interpolation type (but don't enable).
#					Update createRunningAverageTS() to
#					support daily data.  Add
#					fillDayTSFrom2MonthTSAnd1DayTS().
#					Add genesis and description info to
#					fillPattern().
# 15 Mar 2001	SAM, RTi		Add max(), allow indexOf() to search by
#					location.  Add sequence number overload
#					to indexOf().
# 13 Apr 2001	SAM, RTi		Overload getDataUnits() to ignore units.
# 08 May 2001	SAM, RTi		Add divide(), multiply().
# 27 Aug 2001	SAM, RTi		Add blend(), cumulate(), relativeDiff(),
#					replaceValue().
# 2001-11-07	SAM, RTi		Made a number of changes to other TS
#					classes so recompile this.
# 2002-01-25	SAM, RTi		Fix getPeriodFromTS() to allow first
#					TS to be null - search for first
#					non-null TS to initialize.
# 2002-02-26	SAM, RTi		Update regression code so names of the
#					time series variables are more easily
#					associated with filled and independent
#					data.
# 2002-03-24	SAM, RTi		Update to support MOVE1 and MOVE2
#					consistently with regression.
#					Add fillFromTS(), setFromTS().
# 2002-03-31	SAM, RTi		Update fillRegress() to reflect using 3
#					periods for MOVE2.
# 2002-04-15	SAM, RTi		Add shiftTimeByInterval().
# 2002-04-17	SAM, RTi		Add ARMA().
# 2002-04-18	SAM, RTi		Finish implemenenting disaggregate().
# 2002-04-19	SAM, RTi		Update ARMA() to consider ARMA interval.
# 2002-04-29	SAM, RTi		Update ARMA() to handle more ARMA
#					interval possibilities.
# 2002-05-01	SAM, RTi		Update ARMA() to allow ARMA interval
#					greater than the data interval.
# 2002-05-08	SAM, RTi		Update disaggregate() to handle all zero
#					input for the Ormsbee method and also
#					add a SameValue method.
# 2002-05-20	SAM, RTi		Overload toArrayByMonth() to allow more
#					than one month to be specified.  This
#					simplifies seasonal analysis.  Add
#					getTSFormatSpecifiers().  Add
#					adjustExtremes().
# 2002-06-05	SAM, RTi		Add createMonthSummary ().
# 2002-06-16	SAM, RTi		Fix when manipulating IrregularTS data -
#					need to call isDirty() directly because
#					the TSData cannot do so.  Need to
#					correct this by using TSIterator with
#					TS!  Fix bug where cumulate was not
#					setting the initial cumulative value -
#					had to call isDirty(true) for
#					IrregularTS.
# 2002-08-23	SAM, RTi		Add addConstant() method.
# 2003-03-06	SAM, RTi		Add the fillRepeat() method - similar to
#					fillCarryForward().
# 2003-05-20	SAM, RTi		Fix bug in createMonthSummary() where
#					the minimum was not getting computed
#					correctly.  The min and max were also
#					not getting initialized correctly.
# 2003-06-02	SAM, RTi		Upgrade to use generic classes.
#					* Change TSDate to DateTime.
#					* Change TSUnits to DataUnits.
#					* Change TS.INTERVAL* to TimeInterval.
#					* Handle exceptions thrown by parsing
#					  code.
#					* Change TSInterval to TimeInterval.
# 2003-08-21	SAM, RTi		* Change TS.isDirty(boolean) calls to
#					  setDirty(boolean).
# 2003-10-06	SAM, RTi		* Add TRANSFER_BYDATE and
#					  TRANSFER_SEQUENTIALLY to indicate how
#					  time series should be transferred when
#					  iterating.
#					* Update setFromTS() to take a
#					  PropList() to indicate how the
#					  transfer should occur.
# 2003-11-17	SAM, RTi		* Add average() method.
# 2003-11-20	SAM, RTi		* Fix bug in changeToMonthTS(DayTS)
#					  where the search of daily data was not
#					  working correctly.
# 2003-12-22	SAM, RTi		* Fix bug in add() where the debug
#					  messages where printing the result of
#					  the add twice instead of the value to
#					  be added and the initial value.
# 2004-01-26	SAM, RTi		* Add Javadoc to formatOutput() to
#					  describe OutputStart and OutputEnd.
# 2004-02-22	SAM, RTi		* Add fillProrate(), similar to
#					  fillRepeat().
# 2004-08-12	SAM, RTi		* Fix bug in setConstantByMonth() where
#					  the genesis was using a null date.
# 2004-08-22	SAM, RTi		* Change fillPattern() status messages
#					  from level 1 to 2.
# 2004-09-07	SAM, RTi		* Fix bug in createMonthSummary() - it
#					  was not handling minute data.
# 2004-09-13	SAM, RTi		* Change convertUnits() to do nothing if
#					  the requested units are null or blank.
#					  An exception is no longer thrown for
#					  this case.
# 2004-11-08	SAM, RTi		* Add shiftTimeZone().
# 2005-01-25	SAM, RTi		* Add sort() to sort a time series list
#					  by ID.
# 2005-02-16	SAM, RTi		* Overload changeInterval() to adhere
#		LT, RTi			  to the new calling convention utilized
#					  by TSTool, and using a port of the
#					  C++ code.  SAM initialize the code and
#					  LT fill it out.
# 2005-02-23 	LT, RTi			* Redesigned the changeInterval() method
# to					  and all its helper method to better
# 2005-03-04				  handle the current supported
#					  conversions and to allow for future
#					  addition. Fixed a series of bugs found
#					  in the C++ code which was not dealing
#					  with conversion beyond hour. Renamed
#					  all the helper methods to better
#					  represent their functions. Fully docu-
#					  mented and cleanup the code.
# 2005-04-22	SAM, RTi		* Fix the getDataLimits(Vector,...)
#					  method.  Previously it always returned
#					  the full limits, even if dates were
#					  passed in.   The dates are now
#					  considered.
# 2005-04-26	J. Thomas Sapienza, RTi	Corrected a bug in getDataLimits() that
#					was causing it to use the entire period
#					for irregular time series.
# 2005-04-27	SAM, RTi		* Handle missing indicator better in
#					  fillPattern() for months outside
#					  the data period.
# 2005-05-12	SAM, RTi		* Update fillRegress to include the
#					  FillFlag parameter.
#					* Change fillRegress, fillRegressTotal,
#					  fillRegressMonthly to also throw
#					  Exception.
# 2005-05-17	SAM, RTi		* Overload fillConstantByMonth() to take
#					  a PropList and support FillFlag.
# 2005-05-18	SAM, RTi		* Overload fillConstant() to take
#					  a PropList and support FillFlag.
# 2005-05-20	SAM, RTi		* For fillRegression(), make the default
#					  description suffix use the alias if
#					  available.
# 2005-06-02	Luiz Teixeira, RTi	* Fixed bug in changeInterval_fromINST
#					  method by assing the old time series
#					  value to the new one only if the date
#					  coincides with the date of the new
#					  time series data point.
#					  See code commant
#					  "Assign value only if dates are equal"
# 2005-06-15	SAM, RTi		* Add FillFlag property to fillPattern()
#					  and SetFlag to enforceLimits().
#					* Show the number of values filled in
#					  the genesis information for constant,
#					  pattern, and average.
# 2005-07-17	SAM, RTi		* Update fillProrate() to take a
#					  PropList and call the PropList version
#					  from other methods.
#					* Update fillProrate() to support an
#					  analysis period and average for the
#					  factor.
# 2005-07-28	SAM, RTi		* Add findNearestDataValue().
#					* Add interpolateDataValue().
# 2005-09-12	SAM, RTi		* Fix bug where filling with pattern was
#					  not using the first character of the
#					  indicator when the flag was Auto, for
#					  regular time series.
# 2005-09-28	SAM, RTi		* Overload cumulate() to take a
#					  PropList and deprecate the old
#					  method.
# 2005-10-28	SAM, RTi		* Minor change to remove redundant
#					  catch/throw in getPeriodFromTS().
# 2005-12-14	SAM, RTi		* newTimeSeries() was not throwing an
#					  Exception for a bad interval - now it
#					  does.
#					* Change warning messages for add,
#					  consistent with new command standards.
# 2006-01-08	SAM, RTi		* Clarify convertUnits() to only show
#					  add factor if not zero.
# 2006-01-02	SAM, RTi		* Notes for scaling by
#					  DaysInMonthInverse were not getting
#					  handled, leading to a misleading
#					  number being shown in output notes.
# 2006-05-15	SAM, RTi		* DataUnits.getConversion() no longer
#					  throws TSException so some errors were
#					  not getting caught.  Change to catch
#					  Exception in a couple of places.
# 2007-01-30	KAT, RTi		Updated the fill() method to allow
#							the use of the FillFlag when using
#							fillConstant.
# 2007-03-01	SAM, RTi		Fix bug in cumulate() where optional argument
#							was not being handled, resulting in null pointer.
#							Clean up code based on Eclipse feedback.
#------------------------------------------------------------------------------
#EndHeader

from abc import ABC, abstractmethod
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
    def newTimeSeries(id, long_id):
        """
        Given a time series identifier as a string, determine the type of time series
        to be allocated and creates a new instance.  Only the interval base and
        multiplier are set (the memory allocation must occur elsewhere).  Time series metadata including the
        identifier are also NOT set.
        :param id: time series identifier as a string.
        :param long_id: If true, then the string is a full identifier. Otherwise, the string
        is only the interval (e.g., "10min").
        :return: A pointer to the time series, or null if the time series type cannot be determined.
        """
        logger = logging.getLogger("StateMod")
        intervalBase = 0
        intervalMult = 0
        intervalString = ""
        if long_id:
            # Create a TSIdent so that the type of time series can be determined...
            tsident = TSIdent(id)

            # Get the interval and base...
            intervalString = tsident.getInterval()
            intervalBase = tsident.getIntervalBase()
            intervalMult = tsident.getIntervalMult()
        else:
            # Parse a TimeInterval so that the type of time series can be determined...
            intervalString = id
            tsinterval = TimeInterval.parseInterval(intervalString)

            # Get the interval and base...
            intervalBase = tsinterval.getBase()
            intervalMult = tsinterval.getMultiplier()

        # Now interpret the results and declare the time series...
        ts = None
        # if intervalBase == TimeInterval.MINUTE:
        #     ts = MinuteTS()
        # elif intervalBase == TimeInterval.HOUR:
        #     ts = HourTS()
        if intervalBase == TimeInterval.DAY:
            ts = DayTS()
        elif intervalBase == TimeInterval.MONTH:
            ts = MonthTS()
        # elif intervalBase == TimeInterval.YEAR:
        #     ts = YearTS()
        # elif intervalBase == TimeInterval.IRREGULAR:
        #     ts = IrregularTS()
        else:
            message = ("Cannot create a new time series for \"" + id + "\" (the interval \"" +
                       intervalString + "\" [" + intervalBase + "] is not recognized.")
            logger.warning(message)
            return

        # Set the multiplier
        ts.setDataInterval(intervalBase, intervalMult)
        ts.setDataIntervalOriginal(intervalBase, intervalMult)
        # Set the genesis information
        ts.addToGenesis("Created new time series with interval determined from TSID \"" + id + "\"")

        # Return whatever was created...
        return ts