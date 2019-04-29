# TSIdent - class to store and manipulate a time series identifier, or TSID string

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

import logging

from RTi.Util.String.StringUtil import StringUtil
from RTi.Util.Time.TimeInterval import TimeInterval

class TSIdent(object):
    """
    The TSIdent class stores and manipulates a time series identifier, or
    TSID string. The TSID string consists of the following parts:
    <p>
    <pre>
    [LocationType:]Location[-SubLoc].Source.Type[-Subtype].Interval.Scenario[SeqID]~InputType~InputName
    </pre>
    <pre>
    [LocationType:]Location[-SubLoc].Source.Type[-Subtype].Interval.Scenario[SeqID]~DataStoreName
    </pre>
    <p>
    TSID's as TSIdent objects or strings can be used to pass unique time series
    identifiers and are used throughout the time series package.  Some TS object
    data, including data type, are stored only in the TSIdent, to avoid redundant data.
    """

    # Mask indicating that no sub-location should be allowed (treat as part of the main location),
    # used by setLocation()
    NO_SUB_LOCATION = 0x1

    # Mask indicating that no sub-source should be allowed (treat as part of the main source),
    # used by setSource()
    NO_SUB_SOURCE = 0x2

    # Mask indicating that no sub-type should be allowed (treat as part of the main type),
    # used by setType()
    NO_SUB_TYPE = 0x4

    # Mask indicating that no validation of data should occur. This is useful for storing
    # identifier parts during manipulation (e.g., use wildcards, or specify parts of identifiers).
    NO_VALIDATION = 0x8

    # Separator string for TSIdent string parts.
    SEPARATOR = "."

    # Separator string between the TSIdent location type and start of the location ID.
    LOC_TYPE_SEPARATOR = ":"

    # Separator string for TSIdent location parts.
    LOCATION_SEPARATOR = "-"

    # Separator string for TSIdent source parts.
    SOURCE_SEPARATOR = "-"

    # Separator string for TSIdent data type parts.
    TYPE_SEPARATOR = "-"

    # Start of sequence identifier (old sequence number).
    SEQUENCE_NUMBER_LEFT = "["

    # End of sequence identifier (odl sequence number).
    SEQUENCE_NUMBER_RIGHT = "]"

    # Separator string for input type and datastore at end of TSID.
    INPUT_SEPARATOR = "~"

    # The quote can be used to surround TSID parts that have periods, so as to protect the part.
    PERIOD_QUOTE = "'"

    # The DataFlavor for transferring this specific class.
    # tsIdentFlavor = DataFlavor(TSIdent.class, "TSIdent")

    def __init__(self, full_location=None, full_source=None, full_type=None, interval_string=None,
                 scenario=None, input_type=None, input_name=None, mask=None, identifier=None,
                 TSIdent=None):

        # Data members...

        # The whole identifier, including the input type.
        self.__identifier = str()

        # A comment that can be used to describe the TSID, for example on-line TSTool software comment.
        self.__comment = ""

        # A short alias for the time series identifer.
        self.__alias = str()

        # The location (combining the main location and the sub-location).
        self.__full_location = str()

        # Location type (optional).
        self.__locationType = ""

        # The main location.
        self.__main_location = str()

        # The sub-location (2nd+ parts of the location, using the LOCATION_SEPARTOR).
        self.__sub_location = str()

        # The time series data source (combining the main source and the sub-source).
        self.__full_source = str()

        # The main source.
        self.__main_source = str()

        # The sub-source
        self.__sub_source = str()

        # The time series data type (combining the main and sub types).
        self.__full_type = str()

        # The main data type.
        self.__main_type = str()

        # The sub data type.
        self.__sub_type = str()

        # The time series interval as a string
        self.__interval_string = str()

        # The base data interval.
        self.__interval_base = int()

        # The data interval multiplier.
        self.__interval_mult = int()

        # The time series scenario.
        self.__scenario = str()

        # Identifier used for ensemble trace (e.g., if a list of time series is
        # grouped as a set of traces in an ensemble, the trace ID can be the year that the trace starts).
        self.__sequenceID = str()

        # Type of input (e.g., "DateValue", "RiversideDB")
        self.__input_type = str()

        # Name of input (e.g., a file, data store, or database connection name).
        self.__input_name = str()

        # Mask that controls behavior (e.g., how sub-fields are handled).
        self.__behavior_mask = int()

        # Identifier will get set from its parts from its parts
        self.init()

        if mask is not None:
            if identifier is not None:
                # TSIdent(identifier, mask)
                self.setBehaviorMask(mask)
                self.setIdentifier(identifier)
            elif scenario is not None:
                # TSIdent(full_location, full_source, full_type, interval_string, scenario, mask)

                self.setBehaviorMask(mask)
                self.setIdentifier(full_location, full_source, full_type, interval_string, scenario, "", "")
            else:
                # TSIdent(mask)
                self.setBehaviorMask(mask)
        elif identifier is not None:
            # TSIdent(identifier)
            self.setIdentifier(identifier)
        elif scenario is not None:
            if input_type is not None:
                # TSIdent(full_location_full_source, full_type, interval_string, scenario, input_type, input_name)
                self.setIdentifier(full_location, full_source, full_type, interval_string, scenario, input_type,
                                   input_name)
            else:
                # TSIdent(full_location, full_source, full_type, interval_string, scenario)
                self.setIdentifier(full_location, full_source, full_type, interval_string, scenario, "", "")

        elif TSIdent is not None:
            self.initializeTSIdent_TSIdent(TSIdent)

    def initializeTSIdent_TSIdent(self, tsident):
        """
        Copy Constructor
        :param tsident: TSIdent to copy.
        """
        self.setAlias(tsident.getAlias())
        self.setBehaviorMask(tsident.getBehaviorMask())
        self.setLocationType(tsident.getLocationType())
        self.setIdentifier(full_location=tsident.getLocation(), full_source=tsident.getSource(),
                           type=tsident.getType(), interval_string=tsident.getInterval(), scenario=tsident.getScenario()
                           , sequenceID=tsident.getSequenceID(), input_type=tsident.getInputType(),
                           input_name=tsident.getInputName())
        self.__interval_base = tsident.getIntervalBase()
        self.__interval_mult = tsident.getIntervalMult()

    def getAlias(self):
        """
        Return the time series alias
        :return: The alias for the time series
        """
        return self.__alias

    def getBehaviorMask(self):
        """
        Return the behavior mask
        :return: The behavior mask
        """
        return self.__behavior_mask

    def getIdentifierFromParts(self, locationType, full_location, full_source, full_type, interval_string,
                              scenario, sequenceID, input_type, input_name):
        """
        Return the full identifier given the parts.  This method may be called
        internally.  Null fields are treated as empty strings.
        :param locationType: location type
        :param full_location: Full location string
        :param full_source: Full source string.
        :param full_type: Full data type.
        :param interval_string: Data interval string.
        :param scenario: Scenario string.
        :param sequenceID: sequence identifier for the time series (in an ensemble)
        :param input_type: Input type. If blank, the input type will not be added.
        :param input_name: Input name. If blank, the input name will not be added.
        :return: The full identifier string given the parts.
        """
        full_identifier = ""

        if (locationType is not None) and (len(locationType) > 0):
            full_identifier += locationType + TSIdent.LOC_TYPE_SEPARATOR
        if full_location is not None:
            full_identifier += full_location
        full_identifier += (TSIdent.SEPARATOR)
        if full_source is not None:
            full_identifier += full_source
        full_identifier += TSIdent.SEPARATOR
        if full_type is not None:
            full_identifier += full_type
        full_identifier += TSIdent.SEPARATOR
        if interval_string is not None:
            full_identifier += interval_string
        if (scenario is not None) and (len(scenario) != 0):
            full_identifier += TSIdent.SEPARATOR
            full_identifier += scenario
        if (sequenceID is not None) and (len(sequenceID) != 0):
            full_identifier += (TSIdent.SEQUENCE_NUMBER_LEFT + sequenceID + TSIdent.SEQUENCE_NUMBER_RIGHT)
        if (input_type is not None) and (len(input_type) != 0):
            full_identifier += "~" + input_type
        if (input_name is not None) and (len(input_name) != 0):
            full_identifier += "~" + input_name
        return full_identifier

    def getInputName(self):
        """
        Return the input name.
        :return: the input name
        """
        return self.__input_name

    def getInputType(self):
        """
        Return the input name.
        :return: The input name.
        """
        return self.__input_type

    def getInterval(self):
        """
        Return the full interval string.
        :return: the full interval string.
        """
        return self.__interval_string

    def getIntervalBase(self):
        """
        Return the data interval base as an int
        :return: The data interval base (see TimeInterval.*).
        """
        return self.__interval_base

    def getIntervalMult(self):
        """
        Return the data interval multiplier.
        :return: The data interval multiplier.
        """
        return self.__interval_mult

    def getLocation(self):
        """
        Return the full location.
        :return: The full location string.
        """
        return self.__full_location

    def getLocationType(self):
        """
        Return the location type.
        :return: The location type string.
        """
        return self.__locationType

    def getScenario(self):
        """
        Return the scenario string.
        :return: The scenario string.
        """
        return self.__scenario

    def getSequenceID(self):
        """
        Return the sequence identifier for the time series.
        :return: The sequence identifier for the time series. This is meant to be used
        when an array of time series traces is maintained, for example in an ensemble.
        """
        if self.__sequenceID is None:
            return ""
        else:
            return self.__sequenceID

    def getSource(self):
        """
        Return the full source string.
        :return: The full source string.
        """
        return self.__full_source

    def getType(self):
        """
        Return the data type.
        :return: the full data type string.
        """
        return self.__full_type

    def init(self):
        """
        Initialize data members
        """
        self.__behavior_mask = 0  # Default is to process sub-location and sub-source

        # Initialize to None strings so that there are not problems with recursive logic.
        self.__identifier = None
        self.__full_location = None
        self.__main_location = None
        self.__sub_location = None
        self.__full_source = None
        self.__main_source = None
        self.__sub_source = None
        self.__full_type = None
        self.__main_type = None
        self.__sub_type = None
        self.__interval_string = None
        self.__scenario = None
        self.__sequenceID = None
        self.__input_type = None
        self.__input_name = None

        self.setAlias("")

        # Initialize the overall identifier to an empty string...

        self.setFullIdentifier("")

        # Initialize the location components...
        self.setMainLocation("")

        self.setSubLocation("")

        # Initialize the source...

        self.setMainSource("")
        self.setSubSource("")

        #  Initialize the data type...

        self.setType("")
        self.setMainType("")
        self.setSubType("")

        self.__interval_base = TimeInterval.UNKNOWN
        self.__interval_mult = 0

        try:
            self.setInterval_intervalString("")
        except Exception as e:
            # Can ignore here
            pass

        # Initialize the scenario...

        self.setScenario("")

        # Initialize the input...
        self.setInputType("")
        self.setInputName("")

    @staticmethod
    def parseIdentifier(identifier, behavior_flag):
        """
        Parse a TSIdent instance given a String representation of the identifier.
        :param identifier: Full identifier as string.
        :param behavior_flag: Behavior mask to use when creating instance.
        :return: A TSIdent instance given a full identifier string.
        """
        logger = logging.getLogger("StateMod")
        routine = "TSIdent.parseIdentifier"
        dl = 100

        # Declare a TSIdent which we will fill and return..
        tsident = TSIdent(mask=behavior_flag)

        # First parse the datastore and input type information...

        identifier0 = identifier
        list = StringUtil.breakStringList(identifier, "~", 0)
        print(list)
        i = int()
        nlist1 = int()
        if list is not None:
            nlist1 = len(list)
            # Reset to first part for checks below...
            identifier = list[0]
            if nlist1 == 2:
                tsident.setInputType(list[1])
            elif nlist1 >= 3:
                tsident.setInputType(list[1])
                # File name may have a ~ so find the second instance
                # of ~ and use the remaining string...
                pos = identifier0.find("~")
                if (pos >= 0) and (len(identifier) > (pos + 1)):
                    # Have something at the end...
                    sub = identifier0[:pos + 1]
                    pos = sub.find("~")
                    if (pos >= 0) and (len(sub) > (pos + 1)):
                        # The rest is the file...
                        tsident.setInputName(sub[:pos + 1])

        # Now parse the 5-part identifier...
        full_location = ""
        full_source = ""
        interval_string = ""
        scenario = ""
        full_type = ""

        # Figure out whether we are suing the new or old conventions. First
        # check to see if the number of fields is small. Then check to see if
        # the data type and interval are combined.

        posQuote = identifier.find("'")
        if posQuote >= 0:
            # Have at least one quote so assume TSID something like:
            # LocaId.Source. 'DataType-some.parts.with.pariods'.Interval
            list = TSIdent.parseIdentifier_SplitWithQuotes(identifier)
        else:
            # No quote in TSID so do simple parse
            list = StringUtil.breakStringList(identifier, ".", 0)
        nlist1 = len(list)

        # Parse out location and split the rest of the ID...
        # This field is allowed to be surrounded by quotes since some
        # locations cannot be identifier by a simple string. Allow
        # either ' or " to be used and bracket it.
        locationTypeSepPos = -1
        if (identifier[0] != '\'') and (identifier[0] != '\"'):
            # There is not a quoted location string so there is the possibility of having a location type
            # This logic looks at teh full string. If the separator is after a period, then the colon is
            # being detected other than at the start in the location.
            locationTypeSepPos = identifier.find(TSIdent.LOC_TYPE_SEPARATOR)
            if locationTypeSepPos > identifier.find(TSIdent.SEPARATOR):
                locationTypeSepPos = -1

        locationType = ""
        if locationTypeSepPos >= 0:
            # Have a location type so split out and set, then treat the rest of the identifier
            # as the location identifier for further processing.
            locationType = identifier[0:locationTypeSepPos]
            identifier = identifier[:locationTypeSepPos + 1]
        if (identifier[0] == '\'') or (identifier[0] =='\"'):
            full_location = StringUtil.readToDelim(identifier[:1], identifier[0])
            # Get the 2nd+ fields...
            posQuote2 = identifier.find("'")
            if posQuote2 > 0:
                # Have at least one quote so assume TSID something like:
                # LocId.Source.'DataType-some.parts.with.periods'.Interval
                list = TSIdent.parseIdentifier_SplitWithQuotes(identifier[:len(full_location) + 1])
            else:
                list = StringUtil.breakStringList(identifier[len(full_location) + 1], ".", 0)
            nlist1 = len(list)
        else:
            posQuote2 = identifier.find("'")
            if posQuote2 >= 0:
                # Have at least one quote so assume TSID something like:
                # LocaId.Source.'DataType-some.parts.with.periods'.Interval
                list = TSIdent.parseIdentifier_SplitWithQuotes(identifier)
            else:
                list = StringUtil.breakStringList(identifier, ".", 0)
            nlist1 = len(list)
            if nlist1 >= 1:
                full_location = list[0]
        # Data source...
        if nlist1 >= 2:
            full_source = list[1]
        # Data type...
        if nlist1 >= 3:
            full_type = list[2]
        # Data interval...
        sequenceID = None
        if nlist1 >= 4:
            interval_string = list[3]
            # If no scenario is used, the interval string may have the sequence ID on the end, so search
            # for the p and split the sequence ID out of the interval string...
            index = interval_string.find(TSIdent.SEQUENCE_NUMBER_LEFT)
            # Get the sequence ID...
            if index >= 0:
                if interval_string.endswith(TSIdent.SEQUENCE_NUMBER_RIGHT):
                    # Should be properly-formed sequenceID, but need to remove the brackets...
                    sequenceID = interval_string[index+1:len(interval_string)-1].strip()
                if index == 0:
                    # There is no interval, just the sequence ID (should not happen)...
                    interval_string = ""
                else:
                    interval_string = interval_string[0:index]
        # Scenario... It is possible that the scenario has delimiters in it.
        # Therefore, we need to concatenate all the remaining fields to compose
        # fields to compose the complete scenario...
        if nlist1 >= 5:
            buffer = ""
            buffer += list[4]
            for i in range(nlist1):
                buffer += "."
                buffer += list[i]
            scenario = buffer
        # The scenario may now have the sequence ID on the end, search for the [ and split out of the
        # scenario...
        index = scenario.find(TSIdent.SEQUENCE_NUMBER_LEFT)
        # Get the sequence ID...
        if index >= 0:
            if scenario.endswith(TSIdent.SEQUENCE_NUMBER_RIGHT):
                # Should be a properly-formed sequence ID...
                sequenceID = scenario[index+1:len(scenario)-1].strip()
            if index == 0:
                # There is no scenario, just the sequence ID...
                scenario = ""
            else:
                scenario = scenario[0:index]

        # Now set the identifier component parts...

        tsident.setLocationType(locationType)
        tsident.setLocation2(full_location)
        tsident.setSource(full_source)
        tsident.setType(full_type)
        tsident.setInterval_intervalString(interval_string)
        tsident.setScenario(scenario)
        tsident.setSequenceID(sequenceID)

        # Return the TSIdent object for use elsewhere...
        return tsident

    def parseIdentifier_SplitWithQuotes(self, identifier):
        """
        Parse a TSID that has quoted part with periods in one or more parts.
        :param identifier: TSID main part (no ~)
        :return: list of parts for TSID
        """
        logger = logging.getLogger("StateMod")
        # Process by getting one token at a time.
        # - tokens are between periods
        # - if first character of part is single quote, get to the next single quote
        parts = []
        inPart = True
        inQuote = False
        c = ''
        b = ""
        ilen = len(identifier)
        # Use debug messages for now but code seems to be OK
        # - remove debug messages later.
        for i in range(ilen):
            c = identifier[i]
            if c == '.':
                if inQuote:
                    b += c
                else:
                    # Not in quote
                    if inPart:
                        # Between periods. Already in part so end it without adding period.
                        parts.append(b)
                        # Will be in part at top of loop because current period will be skipped
                        # - but if last period treat the following part as empty string
                        if i == (ilen - 1):
                            # Add an empty string
                            parts.append("")
                        else:
                            # Keep processing
                            # Set to not be in part
                            inPart = False
                            i -= 1  # Re-process period to trigger in a part in next iteration.
                    else:
                        # Was not in a part so start it
                        inPart = True
                        # Don't add period to part.
            elif c == '\'':
                # Found a quote, which will surround a point, as in: .'some.part'.
                if inQuote:
                    # At the end of the quoted part
                    # Always include the quote in the part
                    b += c
                    parts.append(b)
                    # Next period immediately following will cause next part to be added, even if
                    # period at end of string
                    inQuote = False
                    inPart = False
                else:
                    # Need to start a part
                    b += c
                    inQuote = True
            else:
                # Character to add to part
                b += c
                if i == (ilen - 1):
                    # Last part
                    parts.append(b)
        return parts

    def setAlias(self, alias):
        """
        Se the time series alias.
        :param alias: Alias for the time series
        """
        if alias is not None:
            self.__alias = alias

    def setBehaviorMask(self, behavior_mask):
        """
        Set the behavior mask. The behavior mask controls how identifier sub-parts are joined into the
        full identifier. Currently this routine does a full reset (not bit-wise).
        :param behavior_mask:
        """
        self.__behavior_mask = behavior_mask

    def setIdentifier(self, identifier=None, full_location=None, full_source=None, full_type=None, type=None,
                      interval_string=None, scenario=None, sequenceID=None, input_type=None, input_name=None):
        """
        Set the identifier
        :param identifier: Full identifier string.
        :param full_location: Full location string.
        :param full_source: Full source string.
        :param full_type: Full data type.
        :param type: Data type.
        :param interval_string: Data interval string.
        :param scenario: Scenario string.
        :param sequenceID: sequence identifier (for time series in ensemble).
        :param input_type: Input type.
        :param input_name: Input name
        """
        logger = logging.getLogger("StateMod")
        routine = "TSIdent.setIdentifier"
        dl = 100

        if identifier is None:
            # Assume that all the individual set routines have handled the
            # __behavior_mask accordingly and therefore we can just concatenate
            # strings here...

            full_identifier = ""
            full_identifier = self.getIdentifierFromParts(self.__locationType, self.__full_location,
                                                          self.__full_source, self.__full_type, self.__interval_string,
                                                          self.__scenario, self.__sequenceID, self.__input_type,
                                                          self.__input_name)
            self.setFullIdentifier(full_identifier)
        elif identifier is not None:
            # Parse the identifier using the public static function to create a temporary identifier object...

            tsident = self.parseIdentifier(identifier, self.__behavior_mask)

            # Now copy the temporary coopy into this instance.

            self.setLocationType(tsident.getLocationType())
            self.setLocation2(tsident.getLocation())
            self.setSource(tsident.getSource())
            self.setType(tsident.getType())
            self.setInterval_intervalString(tsident.getInterval())
            self.setScenario(tsident.getScenario())
            self.setSequenceID(tsident.getSequenceID())
            self.setInputType(tsident.getInputType())
            self.setInputName(tsident.getInputName())
        elif full_type is not None:
            self.setLocation2(full_location)
            self.setSource(full_source)
            self.setType(full_type)
            self.setInterval_intervalString(interval_string)
            self.setScenario(scenario)
        elif sequenceID is not None:
            self.setLocation2(full_location)
            self.setSource(full_source)
            self.setType(type)
            self.setInterval_intervalString(interval_string)
            self.setScenario(scenario)
            self.setSequenceID(sequenceID)
            self.setInputType(input_type)
            self.setInputName(input_name)
        else:
            self.setLocation2(full_location)
            self.setSource(full_source)
            self.setType(type)
            self.setInterval_intervalString(interval_string)
            self.setScenario(scenario)
            self.setInputType(input_type)
            self.setInputName(input_name)

    def setFullIdentifier(self, full_identifier):
        """
        Set the full identifier (this does not result in a parse). It is normally only
        called from within this class.
        :param full_identifier: Full identifier string.
        """
        if full_identifier is None:
            return
        self.__identifier = full_identifier
        # DO NOT call setIdentifer() from here!

    def setFullLocation(self, full_location):
        """
        Set the full location (this does not result in a parse). It is normally only
        called from within this class.
        :param full_location: Full location string.
        """
        if full_location is None:
            return
        self.__full_location = full_location
        # DO NOT call setIdentifier() from here!

    def setFullSource(self, full_source):
        """
        Set the full source (this does not result in a parse). It is normally only
        called from within this class.
        :param full_source: Full source string.
        """
        if full_source is None:
            return
        self.__full_source = full_source
        # DO NOT call setIdentifier() from here!

    def setFullType(self, full_type):
        """
        Set the full data type (this does not result in a parse). It is normally only
        called from within this class
        :param full_type: Full data type string.
        """
        if full_type is None:
            return
        self.__full_type = full_type
        # DO NOT call setIdentifier() from here!

    def setInputName(self, input_name):
        """
        Set the input name.
        :param input_name: the input name.
        """
        if input_name is not None:
            self.__input_name = input_name

    def setInputType(self, input_type):
        """
        Set the input type
        :param input_type: the input type
        """
        if input_type is not None:
            self.__input_type = input_type

    def setInterval_intervalString(self, interval_string):
        """
        Set the interval given the interval string
        :param interval_string: Data interval string
        """
        routine = "TSIdent.setInterval(String)"
        dl = 100
        tsinterval = None
        if interval_string is None:
            return
        if (interval_string != "*") and (len(interval_string) > 0):
            # First split the string into its base and multiplier...
            if (self.__behavior_mask & TSIdent.NO_VALIDATION) == 0:
                try:
                    tsinterval = TimeInterval.parseInterval(interval_string)
                except:
                    # Not validating so let this pass...
                    pass
            else:
                tsinterval = TimeInterval.parseInterval(interval_string)

            # Now set the base and multiplier...
            if tsinterval is not None:
                self.__interval_base = tsinterval.getBase()
                self.__interval_mult = tsinterval.getMultipler()
        # Else, don't do anything (leave as zero initialized values).

        # Now set the interval string. Use the given interval base string
        # because we need to preserve existing file names, etc.
        self.setIntervalString(interval_string)
        self.setIdentifier()

    def setInterval_intervalBase_intervalMult(self, interval_base, interval_mult):
        """
        Set the interval given the interval integer values.
        :param interval_base: Base interval (see TimeInterval.*)
        :param interval_mult: Base interval multiplier.
        """
        logger = logging.getLogger("StateMod")
        if interval_mult <= 0:
            logger.warning("Interval multiplier ({}) must be greater than zero".format(interval_mult))
        if ((interval_base != TimeInterval.SECOND) and
                (interval_base != TimeInterval.MINUTE) and
                (interval_base != TimeInterval.HOUR) and
                (interval_base != TimeInterval.DAY) and
                (interval_base != TimeInterval.WEEK) and
                (interval_base != TimeInterval.MONTH) and
                (interval_base != TimeInterval.YEAR) and
                (interval_base != TimeInterval.IRREGULAR)):
                logger.warning("Base interval ({}) is not recognized".format(interval_base))
                return
        self.__interval_base = interval_base
        self.__interval_mult = interval_mult

        # Now need to set the string representation of the interval...
        interval_string = ""
        if (interval_base != TimeInterval.IRREGULAR) and (interval_mult != 1):
            interval_string += interval_mult
        if interval_base == TimeInterval.SECOND:
            interval_string += "sec"
        elif interval_base == TimeInterval.MINUTE:
            interval_string += "min"
        elif interval_base == TimeInterval.HOUR:
            interval_string += "hour"
        elif interval_base == TimeInterval.DAY:
            interval_string += "day"
        elif interval_base == TimeInterval.WEEK:
            interval_string += "week"
        elif interval_base == TimeInterval.MONTH:
            interval_string += "month"
        elif interval_base == TimeInterval.YEAR:
            interval_string += "year"
        elif interval_base == TimeInterval.IRREGULAR:
            interval_string += "irreg"

        self.setInterval_intervalString(interval_string)
        self.setIdentifier()

    def setIntervalString(self, interval_string):
        """
        Set the interval string. This is normally only called from this class
        :param interval_string: Interval string.
        """
        if interval_string is not None:
            self.__interval_string = interval_string

    def setLocation1(self):
        """
        Set the full location from its parts. This method is generally called from
        setMainLocation() and setSubLocation() methods to reset __full_location.
        """
        logger = logging.getLogger("StateMod")
        routine = "TSIdent.setLocation"
        dl = 100

        if (self.__behavior_mask & TSIdent.NO_SUB_LOCATION) != 0:
            # Just use the main location as the full location...
            if self.__main_location is not None:
                # There should always be a main location after the object is initialized...
                self.setFullLocation(self.__main_location)
        else:
            # Concatenate the main and sub-locations to get the full location
            full_location = ""
            # We may want to check for __main_location[] also...
            if self.__main_location is not None:
                # This should always be the case after the object is initialized...
                full_location += self.__main_location
                if self.__sub_location is not None:
                    # We only want to add the sublocation if it is not
                    # an empty string (it will be an empty string after the
                    # object is initialized).
                    if len(self.__sub_location) > 0:
                        # Have a sub_location so append it to the main location...
                        full_location += TSIdent.LOCATION_SEPARATOR
                        full_location += self.__sub_location
                self.setFullLocation(full_location)
        # Now reset the full identifier...
        self.setIdentifier()

    def setLocation2(self, full_location):
        """
        Set the full location from its full string.
        :param full_location: The full location string.
        """
        logger = logging.getLogger("StateMod")
        routine = "TSIdent.setLocation(full_location)"
        dl = 100

        if full_location is None:
            return
        if (self.__behavior_mask & TSIdent.NO_SUB_LOCATION) != 0:
            # The entire string passed in is used for the main location...
            self.setMainLocation(full_location)
        else:
            # Need to split the location into main and sub-location...
            list = []
            sub_location = ""
            nlist = int()
            if nlist >= 1:
                # Set the main location...
                self.setMainLocation(list[0])
            if nlist >= 2:
                # Now set the sub-location. This allows for multiple delimited
                # parts (everything after the first delimiter is treated as the sublocation).
                iend = nlist - 1
                for i in range(iend + 1):
                    if i != 1:
                        sub_location += TSIdent.LOCATION_SEPARATOR
                    sub_location += list[i]
                self.setSubLocation(sub_location)
            else:
                # Since only setting the main location need to set the sub-location to an empty string...
                self.setSubLocation( "" )

    def setLocationType(self, locationType):
        """
        Set the location type.
        :param locationType: location type.
        """
        if locationType is None:
            return
        self.__locationType = locationType
        self.setIdentifier()

    def setMainLocation(self, main_location):
        """
        Set the main location string (and reset the full location).
        :param main_location: The location string.
        """
        if main_location is None:
            return
        self.__main_location = main_location
        self.setLocation1()

    def setMainSource(self, main_source):
        """
        Set the main source string (and reset the full source).
        :param main_source: The main source string.
        """
        if main_source is None:
            return
        self.__main_source = main_source
        self.setSource()

    def setMainType(self, main_type):
        """
        Set the main data type string (and reset the full type).
        :param main_type: The main data type string.
        """
        if main_type is None:
            return
        self.__main_type = main_type
        self.setType()

    def setScenario(self, scenario):
        """
        Set the scenario string
        :param scenario: The scenario string.
        """
        if scenario is None:
            return
        self.__scenario = scenario
        self.setIdentifier()

    def setSequenceID(self, sequenceID):
        """
        Set the sequence identifier, for example when the time series is part of an ensemble
        :param sequenceID: sequence identifier for the time series
        """
        self.__sequenceID = sequenceID
        self.setIdentifier()

    def setSource(self, source=None):
        """
        Set the full source from a full string.
        :param source: the full source string
        """
        if source is None:
            if (self.__behavior_mask & TSIdent.NO_SUB_SOURCE) != 0:
                # Just use the main source as the full source...
                if self.__main_source is not None:
                    # There should always be a main source after the object is initialized...
                    self.setFullSource(self.__main_source)
            else:
                # Concatenate the main and sub-sources to get the full source.
                full_source = ""
                if self.__main_source is not None:
                    # We only want to add the subsource if it is not an empty
                    # string (it will be an empty string after the object is initialized).
                    full_source += self.__main_source
                    if self.__sub_source is not None:
                        # We have sub_source so append it to the main source...
                        # We have a sub_source so append it to the main source...
                        if len(self.__sub_source) > 0:
                            full_source += TSIdent.SOURCE_SEPARATOR
                            full_source += self.__sub_source
                    self.setFullSource(full_source)
            # Now reset the full identifier...
            self.setIdentifier()
            return
        else:
            if source == "":
                self.setMainSource("")
                self.setSubSource("")
            elif (self.__behavior_mask & TSIdent.NO_SUB_SOURCE) != 0:
                # The entire string passed in is used for the main source...
                self.setMainSource(source)
            else:
                # Need to split the source into main and sub-source...
                list = []
                nlist = int()
                sub_source = ""
                list = StringUtil.breakStringList(source, TSIdent.SOURCE_SEPARATOR, 0)
                nlist = len(list)
                if nlist >= 1:
                    # Set the main source...
                    self.setMainSource(list[0])
                if nlist >= 2:
                    # Now set the sub-source...
                    iend = nlist - 1
                    for i in range(iend + 1):
                        sub_source += list[i]
                        if i != iend:
                            sub_source += TSIdent.SOURCE_SEPARATOR
                    self.setSubSource(sub_source)
                else:
                    # Since we are only setting the main location we need
                    # to set the sub-location to an empty string...
                    self.setSubSource("")

    def setSubSource(self, sub_source):
        """
        Set the sub-source string (and reset the full source).
        :param sub_source: The sub-source string.
        """
        if sub_source is None:
            return
        self.__sub_source = sub_source
        self.setSource()

    def setSubLocation(self, sub_location):
        """
        Set the sub-location string (and reset the full location).
        :param sub_location: The sub-location string
        """
        if sub_location is not None:
            return
        self.__sub_location = sub_location
        self.setLocation1()

    def setSubType(self, sub_type):
        """
        Set the sub-type string (and reset the full data type).
        :param sub_type: The sub-type string.
        """
        if sub_type is None:
            return
        self.__sub_type = sub_type
        self.setType()

    def setType(self, type=None):
        """
        Set the full data type from is parts. This method is generally called from setMainType()
        and setSubType() methods to reset __full_type.
        :param type: the full data type string (optional)
        """
        logger = logging.getLogger("StateMod")
        routine = "TSIdent.setType()"
        if type is None:
            if (self.__behavior_mask & TSIdent.NO_SUB_TYPE) != 0:
                # Just use the main type as the full type...
                if self.__main_type is not None:
                    # There should always be a main type after the object is initialized...
                    self.setFullType(self.__main_type)
            else:
                # Concatenate the main and sub-types to get the full type.
                full_type = ""
                if self.__main_type is not None:
                    # This should always be the case after the object is initialized...
                    full_type += self.__main_type
                    if self.__sub_type is not None:
                        # We only want to add the subtype if it is
                        # not an empty string (it will be an empty string
                        # after the object is initialized).
                        if len(self.__sub_type) > 0:
                            # We have a sub type so append it to the main type...
                            full_type += TSIdent.TYPE_SEPARATOR
                            full_type += self.__sub_type
                    self.setFullType(full_type)
            # Now reset the full identifier...
            self.setIdentifier()
        else:
            if (self.__behavior_mask & TSIdent.NO_SUB_TYPE) != 0:
                # The entire string passed in is used for the main data type...
                self.setMainType(type)
            else:
                # Need to split the data type into main and sub-locaiton...
                list = []
                sub_type = ""
                nlist = int()
                list = StringUtil.breakStringList(type, TSIdent.TYPE_SEPARATOR, 0)
                nlist = len(list)
                if nlist >= 1:
                    # Set the mian type...
                    self.setMainType(list[0])
                if nlist >= 2:
                    # Now set the sub-type...
                    iend = nlist - 1
                    for i in range(iend + 1):
                        sub_type += list[i]
                        if i != iend:
                            sub_type += TSIdent.TYPE_SEPARATOR
                    self.setSubType(sub_type)
                else:
                    # Since we are only setting the main type we
                    # need to set the sub-type to an empty string...
                    self.setSubType("")