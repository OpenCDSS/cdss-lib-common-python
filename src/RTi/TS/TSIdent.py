# TSIdent - class to store and manipulate a time series identifier, or TSID string

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
    # used by set_source()
    NO_SUB_SOURCE = 0x2

    # Mask indicating that no sub-type should be allowed (treat as part of the main type),
    # used by set_type()
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

    # Debug for class
    debug = False

    def __init__(self, full_location=None, full_source=None, full_type=None, interval_string=None,
                 scenario=None, input_type=None, input_name=None, mask=None, identifier=None,
                 tsident=None):
        """
        Constructor for TSIdent, which handles various overloaded versions (as per Java code).
        It should be called one of the following variations:
        1) TSIdent() - default all values, generally when parts will be set incrementally.
        2) TSIdent(mask) - similar to (1) but set the behavior mask
        3) TSIdent(identifier) - set with a TSID string
        4) TSIdent(identifier, mask) - set with a TSID string and mask
        5) TSIdent(full_location, full_source, full_type, interval_string, scenario) - set using parts
        6) TSIdent(full_location, full_source, full_type, interval_string, scenario, mask) - set using parts and mask
        7) TSIdent(full_location, full_source, full_type, interval_string, scenario, input_type, input_name) - all parts
        8) TSIdent(tsident) - copy constructor
        :param full_location:
        :param full_source:
        :param full_type:
        :param interval_string:
        :param scenario:
        :param input_type:
        :param input_name:
        :param mask:
        :param identifier:
        :param tsident:
        """

        # Define and set data members to initial values.

        # The whole identifier, including the input type.
        self.identifier = None

        # A comment that can be used to describe the TSID, for example on-line TSTool software comment.
        self.comment = ""

        # A short alias for the time series identifier.
        self.alias = None

        # The location (combining the main location and the sub-location).
        self.full_location = None

        # Location type (optional).
        self.location_type = ""

        # The main location.
        self.main_location = None

        # The sub-location (2nd+ parts of the location, using the LOCATION_SEPARTOR).
        self.sub_location = None

        # The time series data source (combining the main source and the sub-source).
        self.full_source = None

        # The main source.
        self.main_source = None

        # The sub-source
        self.sub_source = None

        # The time series data type (combining the main and sub types).
        self.full_type = None

        # The main data type.
        self.main_type = None

        # The sub data type.
        self.sub_type = None

        # The time series interval as a string
        self.interval_string = None

        # The base data interval.
        self.interval_base = 0

        # The data interval multiplier.
        self.interval_mult = 0

        # The time series scenario.
        self.scenario = None

        # Identifier used for ensemble trace (e.g., if a list of time series is
        # grouped as a set of traces in an ensemble, the trace ID can be the year that the trace starts).
        self.sequence_id = None

        # Type of input (e.g., "DateValue", "RiversideDB")
        self.input_type = None

        # Name of input (e.g., a file, data store, or database connection name).
        self.input_name = None

        # Mask that controls behavior (e.g., how sub-fields are handled).
        self.behavior_mask = 0

        if (full_location is None) and (full_source is None) and (full_type is None) and \
            (interval_string is None) and (scenario is None) and (input_type is None) and \
                (input_name is None) and (mask is None) and (identifier is None) and (tsident is None):
            # Variation 1 - nothing set, default constructor
            self.init()
        elif (full_location is None) and (full_source is None) and (full_type is None) and \
            (interval_string is None) and (scenario is None) and (input_type is None) and \
                (input_name is None) and (mask is not None) and (identifier is None) and (tsident is None):
            # Variation 2 - only mask set
            self.init()
            self.set_behavior_mask(mask)
        elif identifier is not None:
            # Variation 3
            # TSIdent(identifier)
            self.init()
            self.set_identifier(identifier=identifier)
        elif (full_location is None) and (full_source is None) and (full_type is None) and \
            (interval_string is None) and (scenario is None) and (input_type is None) and \
                (input_name is None) and (mask is not None) and (identifier is not None) and (tsident is None):
            # Variation 4 - identifier string and mask set
            self.init()
            self.set_behavior_mask(mask)
            self.set_identifier(identifier=identifier)
        elif (full_location is not None) and (full_source is not None) and (full_type is not None) and \
            (interval_string is not None) and (scenario is not None) and (input_type is None) and \
                (input_name is None) and (mask is None) and (identifier is None) and (tsident is None):
            # Variation 5
            self.init()
            self.set_identifier(full_location=full_location, full_source=full_source, full_type=full_type,
                                interval_string=interval_string, scenario=scenario, input_type="",
                                input_name="")
        elif (full_location is not None) and (full_source is not None) and (full_type is not None) and \
            (interval_string is not None) and (scenario is not None) and (input_type is None) and \
                (input_name is None) and (mask is not None) and (identifier is None) and (tsident is None):
            # Variation 6
            self.init()
            self.set_behavior_mask(mask)
            self.set_identifier(full_location=full_location, full_source=full_source, full_type=full_type,
                                interval_string=interval_string, scenario=scenario, input_type="",
                                input_name="")
        elif (full_location is not None) and (full_source is not None) and (full_type is not None) and \
            (interval_string is not None) and (scenario is not None) and (input_type is not None) and \
                (input_name is not None):
            # Variation 7
            self.init()
            self.set_identifier(full_location=full_location, full_source=full_source, full_type=full_type,
                                interval_string=interval_string, scenario=scenario, input_type=input_type,
                                input_name=input_name)
        elif tsident is not None:
            # Variation 8
            # TSIdent(TSIdent)
            self.init()
            self.init_tsident(tsident)
        else:
            raise ValueError("TSIdent constructor is not supported.")

    # TODO smalers 2020-01-05 need to implement __eq__

    def __str__(self):
        """
        Return a string representation of the time series identifier, calls to_string().
        :return: string representation of time series identifier
        """
        return self.to_string()

    def init_tsident(self, tsident):
        """
        Copy Constructor
        :param tsident: TSIdent to copy.
        """
        self.init()
        self.set_alias(tsident.get_alias())
        self.set_behavior_mask(tsident.get_behavior_mask())
        # Do not use the following!  It triggers infinite recursion!
        # set_identifier(identifier=tsident.identifier)
        self.set_location_type(tsident.get_location_type())
        self.set_identifier(full_location=tsident.get_location(), full_source=tsident.get_source(),
                            full_type=tsident.get_type(), interval_string=tsident.get_interval(),
                            scenario=tsident.get_scenario(), sequence_id=tsident.get_sequence_id(),
                            input_type=tsident.get_input_type(), input_name=tsident.get_input_name())
        self.interval_base = tsident.get_interval_base()
        self.interval_mult = tsident.get_interval_mult()

    def get_alias(self):
        """
        Return the time series alias
        :return: The alias for the time series
        """
        return self.alias

    def get_behavior_mask(self):
        """
        Return the behavior mask
        :return: The behavior mask
        """
        return self.behavior_mask

    def get_identifier_from_parts(self, location_type=None, full_location=None,
                                  full_source=None, full_type=None, interval_string=None,
                                  scenario=None, sequence_id=None, input_type=None,
                                  input_name=None):
        """
        Return the full identifier given the parts.  This method may be called
        internally.  Null fields are treated as empty strings.
        :param location_type: location type
        :param full_location: Full location string
        :param full_source: Full source string.
        :param full_type: Full data type.
        :param interval_string: Data interval string.
        :param scenario: Scenario string.
        :param sequence_id: sequence identifier for the time series (in an ensemble)
        :param input_type: Input type. If blank, the input type will not be added.
        :param input_name: Input name. If blank, the input name will not be added.
        :return: The full identifier string given the parts.
        """
        # Call the overloaded variations first, which will cascade to the generic case below
        if (location_type is None) and (full_location is not None) and (full_source is not None) and \
                (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
                (sequence_id is None) and (input_type is None) and (input_name is None):
            return self.get_identifier_from_parts(full_location=full_location, full_source=full_source,
                                                  full_type=full_type, interval_string=interval_string,
                                                  scenario=scenario, sequence_id=None, input_type="", input_name="")
        elif (location_type is None) and (full_location is not None) and (full_source is not None) and \
                (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
                (sequence_id is not None) and (input_type is None) and (input_name is None):
            return self.get_identifier_from_parts(full_location=full_location, full_source=full_source,
                                                  full_type=full_type, interval_string=interval_string,
                                                  scenario=scenario, sequence_id=sequence_id, input_type="",
                                                  input_name="")
        elif (location_type is None) and (full_location is not None) and (full_source is not None) and \
             (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
             (sequence_id is None) and (input_type is not None) and (input_name is not None):
            # TODO smalers 2020-01-05 Java code seems suspicious - is not setting input type and name?
            return self.get_identifier_from_parts(full_location=full_location, full_source=full_source,
                                                  full_type=full_type, interval_string=interval_string,
                                                  scenario=scenario, sequence_id=None, input_type=input_type,
                                                  input_name=input_name)
        elif (location_type is None) and (full_location is not None) and (full_source is not None) and \
             (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
             (sequence_id is not None) and (input_type is not None) and (input_name is not None):
            return self.get_identifier_from_parts(location_type="", full_location=full_location,
                                                  full_source=full_source,
                                                  full_type=full_type, interval_string=interval_string,
                                                  scenario=scenario, sequence_id=None, input_type=input_type,
                                                  input_name=input_name)
        else:
            # Logic to handle the most verbose variation
            full_identifier = ""

            if (location_type is not None) and (len(location_type) > 0):
                full_identifier += location_type + TSIdent.LOC_TYPE_SEPARATOR
            if full_location is not None:
                full_identifier += full_location
            full_identifier += TSIdent.SEPARATOR
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
            if (sequence_id is not None) and (len(sequence_id) != 0):
                full_identifier += (TSIdent.SEQUENCE_NUMBER_LEFT + sequence_id + TSIdent.SEQUENCE_NUMBER_RIGHT)
            if (input_type is not None) and (len(input_type) != 0):
                full_identifier += "~" + input_type
            if (input_name is not None) and (len(input_name) != 0):
                full_identifier += "~" + input_name
            return full_identifier

    def get_input_name(self):
        """
        Return the input name.
        :return: the input name
        """
        return self.input_name

    def get_input_type(self):
        """
        Return the input name.
        :return: The input name.
        """
        return self.input_type

    def get_interval(self):
        """
        Return the full interval string.
        :return: the full interval string.
        """
        return self.interval_string

    def get_interval_base(self):
        """
        Return the data interval base as an int
        :return: The data interval base (see TimeInterval.*).
        """
        return self.interval_base

    def get_interval_mult(self):
        """
        Return the data interval multiplier.
        :return: The data interval multiplier.
        """
        return self.interval_mult

    def get_location(self):
        """
        Return the full location.
        :return: The full location string.
        """
        return self.full_location

    def get_location_type(self):
        """
        Return the location type.
        :return: The location type string.
        """
        return self.location_type

    def get_main_location(self):
        """
        Return the main location.
        :return: The main location.
        """
        return self.main_location

    def get_main_source(self):
        """
        Return the main source.
        :return: The main source.
        """
        return self.main_source

    def get_main_type(self):
        """
        Return the main type.
        :return: The main type.
        """
        return self.main_type

    def get_scenario(self):
        """
        Return the scenario string.
        :return: The scenario string.
        """
        return self.scenario

    def get_sequence_id(self):
        """
        Return the sequence identifier for the time series.
        :return: The sequence identifier for the time series. This is meant to be used
        when an array of time series traces is maintained, for example in an ensemble.
        """
        if self.sequence_id is None:
            return ""
        else:
            return self.sequence_id

    def get_source(self):
        """
        Return the full source string.
        :return: The full source string.
        """
        return self.full_source

    def get_sub_location(self):
        """
        Return the sub location string.
        :return: The sub location string.
        """
        return self.sub_location

    def get_sub_source(self):
        """
        Return the sub source string.
        :return: The sub source string.
        """
        return self.sub_source

    def get_sub_type(self):
        """
        Return the sub type string.
        :return: The sub type string.
        """
        return self.sub_type

    def get_type(self):
        """
        Return the data type.
        :return: the full data type string.
        """
        return self.full_type

    def init(self):
        """
        Initialize data members
        """
        self.behavior_mask = 0  # Default is to process sub-location and sub-source

        # Initialize to None strings so that there are not problems with recursive logic.
        self.identifier = None
        self.full_location = None
        self.main_location = None
        self.sub_location = None
        self.full_source = None
        self.main_source = None
        self.sub_source = None
        self.full_type = None
        self.main_type = None
        self.sub_type = None
        self.interval_string = None
        self.scenario = None
        self.sequence_id = None
        self.input_type = None
        self.input_name = None

        self.set_alias("")

        # Initialize the overall identifier to an empty string...

        self.set_full_identifier("")

        # Initialize the location components...

        self.set_main_location("")
        self.set_sub_location("")

        # Initialize the source...

        self.set_main_source("")
        self.set_sub_source("")

        #  Initialize the data type...

        self.set_type("")
        self.set_main_type("")
        self.set_sub_type("")

        self.interval_base = TimeInterval.UNKNOWN
        self.interval_mult = 0

        try:
            self.set_interval(interval_string="")
        except Exception as e:
            # Can ignore here
            pass

        # Initialize the scenario...

        self.set_scenario("")

        # Initialize the input...
        self.set_input_type("")
        self.set_input_name("")

    # TODO smalers 2020-01-05 need to implement matches

    @staticmethod
    def parse_identifier(identifier, behavior_mask=None):
        """
        Parse a TSIdent instance given a String representation of the identifier.
        :param identifier: Full identifier as string.
        :param behavior_mask: Behavior mask to use when creating instance.
        :return: A TSIdent instance given a full identifier string.
        """
        # Handle overloaded versions
        if behavior_mask is None:
            behavior_mask = 0  # default

        # Main logic
        logger = logging.getLogger(__name__)
        dl = 100

        # Declare a TSIdent which we will fill and return..
        tsident = TSIdent(mask=behavior_mask)

        # First parse the datastore and input type information...

        identifier0 = identifier
        part_list = StringUtil.break_string_list(identifier, "~", 0)
        print(part_list)
        if part_list is not None:
            nlist1 = len(part_list)
            # Reset to first part for checks below...
            identifier = part_list[0]
            if nlist1 == 2:
                tsident.set_input_type(part_list[1])
            elif nlist1 >= 3:
                tsident.set_input_type(part_list[1])
                # File name may have a ~ so find the second instance
                # of ~ and use the remaining string...
                pos = identifier0.find("~")
                if (pos >= 0) and (len(identifier) > (pos + 1)):
                    # Have something at the end...
                    sub = identifier0[pos + 1:]
                    pos = sub.find("~")
                    if (pos >= 0) and (len(sub) > (pos + 1)):
                        # The rest is the file...
                        tsident.set_input_name(sub[pos + 1:])

        # Now parse the 5-part identifier...
        full_location = ""
        full_source = ""
        interval_string = ""
        scenario = ""
        full_type = ""

        # Figure out whether we are suing the new or old conventions. First
        # check to see if the number of fields is small. Then check to see if
        # the data type and interval are combined.

        pos_quote = identifier.find("'")
        if pos_quote >= 0:
            # Have at least one quote so assume TSID something like:
            # LocaId.Source. 'DataType-some.parts.with.pariods'.Interval
            part_list = TSIdent.parse_identifier_split_with_quotes(identifier)
        else:
            # No quote in TSID so do simple parse
            part_list = StringUtil.break_string_list(identifier, ".", 0)
        nlist1 = len(part_list)

        # Parse out location and split the rest of the ID...
        # This field is allowed to be surrounded by quotes since some
        # locations cannot be identifier by a simple string. Allow
        # either ' or " to be used and bracket it.
        location_type_sep_pos = -1
        if (identifier[0] != "'") and (identifier[0] != '"'):
            # There is not a quoted location string so there is the possibility of having a location type
            # This logic looks at teh full string. If the separator is after a period, then the colon is
            # being detected other than at the start in the location.
            location_type_sep_pos = identifier.find(TSIdent.LOC_TYPE_SEPARATOR)
            if location_type_sep_pos > identifier.find(TSIdent.SEPARATOR):
                location_type_sep_pos = -1

        location_type = ""
        if location_type_sep_pos >= 0:
            # Have a location type so split out and set, then treat the rest of the identifier
            # as the location identifier for further processing.
            location_type = identifier[0:location_type_sep_pos]
            identifier = identifier[location_type_sep_pos + 1:]
        if (identifier[0] == "'") or (identifier[0] == '"'):
            full_location = StringUtil.read_to_delim(identifier[1:], identifier[0])
            # Get the 2nd+ fields...
            pos_quote2 = identifier.find("'")
            if pos_quote2 > 0:
                # Have at least one quote so assume TSID something like:
                # LocId.Source.'DataType-some.parts.with.periods'.Interval
                part_list = TSIdent.parse_identifier_split_with_quotes(identifier[len(full_location) + 1:])
            else:
                part_list = StringUtil.break_string_list(identifier[len(full_location) + 1], ".", 0)
            nlist1 = len(part_list)
        else:
            pos_quote2 = identifier.find("'")
            if pos_quote2 >= 0:
                # Have at least one quote so assume TSID something like:
                # LocaId.Source.'DataType-some.parts.with.periods'.Interval
                part_list = TSIdent.parse_identifier_split_with_quotes(identifier)
            else:
                part_list = StringUtil.break_string_list(identifier, ".", 0)
            nlist1 = len(part_list)
            if nlist1 >= 1:
                full_location = part_list[0]
        # Data source...
        if nlist1 >= 2:
            full_source = part_list[1]
        # Data type...
        if nlist1 >= 3:
            full_type = part_list[2]
        # Data interval...
        sequence_id = None
        if nlist1 >= 4:
            interval_string = part_list[3]
            # If no scenario is used, the interval string may have the sequence ID on the end, so search
            # for the p and split the sequence ID out of the interval string...
            index = interval_string.find(TSIdent.SEQUENCE_NUMBER_LEFT)
            # Get the sequence ID...
            if index >= 0:
                if interval_string.endswith(TSIdent.SEQUENCE_NUMBER_RIGHT):
                    # Should be properly-formed sequence_id, but need to remove the brackets...
                    sequence_id = interval_string[index + 1:len(interval_string) - 1].strip()
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
            buffer += part_list[4]
            for i in range(5, nlist1):
                buffer += "."
                buffer += part_list[i]
            scenario = buffer
        # The scenario may now have the sequence ID on the end, search for the [ and split out of the
        # scenario...
        index = scenario.find(TSIdent.SEQUENCE_NUMBER_LEFT)
        # Get the sequence ID...
        if index >= 0:
            if scenario.endswith(TSIdent.SEQUENCE_NUMBER_RIGHT):
                # Should be a properly-formed sequence ID...
                sequence_id = scenario[index + 1:len(scenario) - 1].strip()
            if index == 0:
                # There is no scenario, just the sequence ID...
                scenario = ""
            else:
                scenario = scenario[0:index]

        # Now set the identifier component parts...

        tsident.set_location_type(location_type)
        tsident.set_location(full_location=full_location)
        tsident.set_source(full_source)
        tsident.set_type(full_type)
        tsident.set_interval_string(interval_string)
        tsident.set_scenario(scenario)
        tsident.set_sequence_id(sequence_id)

        # Return the TSIdent object for use elsewhere...
        return tsident

    @staticmethod
    def parse_identifier_split_with_quotes(identifier):
        """
        Parse a TSID that has quoted part with periods in one or more parts.
        :param identifier: TSID main part (no ~)
        :return: list of parts for TSID
        """
        logger = logging.getLogger(__name__)
        # Process by getting one token at a time.
        # - tokens are between periods
        # - if first character of part is single quote, get to the next single quote
        parts = []
        in_part = True
        in_quote = False
        c = ''
        b = ""
        ilen = len(identifier)
        # Use debug messages for now but code seems to be OK
        # - remove debug messages later.
        for i in range(ilen):
            c = identifier[i]
            if c == '.':
                if in_quote:
                    b += c
                else:
                    # Not in quote
                    if in_part:
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
                            in_part = False
                            i -= 1  # Re-process period to trigger in a part in next iteration.
                    else:
                        # Was not in a part so start it
                        in_part = True
                        # Don't add period to part.
            elif c == '\'':
                # Found a quote, which will surround a point, as in: .'some.part'.
                if in_quote:
                    # At the end of the quoted part
                    # Always include the quote in the part
                    b += c
                    parts.append(b)
                    # Next period immediately following will cause next part to be added, even if
                    # period at end of string
                    in_quote = False
                    in_part = False
                else:
                    # Need to start a part
                    b += c
                    in_quote = True
            else:
                # Character to add to part
                b += c
                if i == (ilen - 1):
                    # Last part
                    parts.append(b)
        return parts

    def set_alias(self, alias):
        """
        Se the time series alias.
        :param alias: Alias for the time series
        """
        if alias is not None:
            self.alias = alias

    def set_behavior_mask(self, behavior_mask):
        """
        Set the behavior mask. The behavior mask controls how identifier sub-parts are joined into the
        full identifier. Currently this routine does a full reset (not bit-wise).
        :param behavior_mask:
        """
        self.behavior_mask = behavior_mask

    def set_comment(self, comment):
        """
        Se the comment for the identifier.
        :param comment: comment for the identifier
        """
        if comment is not None:
            self.comment = comment

    def set_full_identifier(self, full_identifier):
        """
        Set the full identifier (this does not result in a parse). It is normally only
        called from within this class.
        :param full_identifier: Full identifier string.
        """
        if full_identifier is None:
            return
        self.identifier = full_identifier
        # DO NOT call set_identifier() from here!

    def set_full_location(self, full_location):
        """
        Set the full location (this does not result in a parse). It is normally only
        called from within this class.
        :param full_location: Full location string.
        """
        if full_location is None:
            return
        self.full_location = full_location
        # DO NOT call set_identifier() from here!

    def set_full_source(self, full_source):
        """
        Set the full source (this does not result in a parse). It is normally only
        called from within this class.
        :param full_source: Full source string.
        """
        if full_source is None:
            return
        self.full_source = full_source
        # DO NOT call set_identifier() from here!

    def set_full_type(self, full_type):
        """
        Set the full data type (this does not result in a parse). It is normally only
        called from within this class
        :param full_type: Full data type string.
        """
        if full_type is None:
            return
        self.full_type = full_type
        # DO NOT call set_identifier() from here!

    def set_identifier(self, identifier=None, full_location=None, full_source=None, full_type=None,
                       interval_string=None, scenario=None, sequence_id=None, input_type=None, input_name=None,
                       tsident=None):
        """
        Set the identifier
        :param identifier: Full identifier string.
        :param full_location: Full location string.
        :param full_source: Full source string.
        :param full_type: Full data type.
        :param interval_string: Data interval string.
        :param scenario: Scenario string.
        :param sequence_id: sequence identifier (for time series in ensemble).
        :param input_type: Input type.
        :param input_name: Input name
        :param tsident: TSIdent instance to copy
        """
        logger = logging.getLogger(__name__)

        if (identifier is None) and (full_location is None) and (full_source is None) and (full_type is None) and \
            (interval_string is None) and (scenario is None) and (sequence_id is None) and \
                (input_type is None) and (input_name is None):
            # Case where all parameters are None and the identifier can be formed by the parts in the instance:
            # set_identifier()

            # Assume that all the individual set routines have handled the
            # behavior_mask accordingly and therefore we can just concatenate
            # strings here...

            if self.debug:
                logger.debug("Setting full identifier from parts: \"" + str(self.full_location) +
                    "." + str(self.full_source) + "." + str(self.full_type) +"." + str(self.interval_string) +
                    "." + str(self.scenario) + "~" + str(self.input_type) + "~" + str(self.input_name))

            if self.debug:
                logger.debug("Calling get_identifier_from_parts..." )
            full_identifier = self.get_identifier_from_parts(location_type=self.location_type,
                                                             full_location=self.full_location,
                                                             full_source=self.full_source,
                                                             full_type=self.full_type,
                                                             interval_string=self.interval_string,
                                                             scenario=self.scenario,
                                                             sequence_id=self.sequence_id,
                                                             input_type=self.input_type,
                                                             input_name=self.input_name)
            if self.debug:
                logger.debug("...successfully called get_identifier_from_parts...")
            self.set_full_identifier(full_identifier)
            if self.debug:
                logging.debug("ID: \"" + str(self.identifier) + "\"")

        elif (identifier is not None) and (full_location is None) and (full_source is None) and \
             (full_type is None) and (interval_string is None) and (scenario is None) and (sequence_id is None) and \
                (input_type is None) and (input_name is None):
            # Case where only identifier string is not None:
            # set_identifier(identifier)
            if identifier is None:
                return

            if self.debug:
                logger.debug("Trying to set identifier to \"" + identifier + "\"")

            if len(identifier) == 0:
                # Cannot parse the identifier because doing so would result in an infinite loop.
                # If this routine is being called with an empty string, it is a mistake.
                # The initialization code will call set_full_identifier() directly.
                if self.debug:
                    logger.debug("Identifier string is empty, not processing!")
                return

            # Parse the identifier using the public static function to create a temporary identifier object...

            if self.debug:
                logger.debug("Done declaring temp TSIdent.")
                logger.debug("Parsing identifier...")

            tsident = TSIdent.parse_identifier(identifier, behavior_mask=self.behavior_mask)
            if self.debug:
                logger.debug("...back from parsing identifier")

            # Now copy the temporary copy into this instance...

            if self.debug:
                logger.debug("Setting the individual parts...")
                self.set_location_type(tsident.get_location_type())
                self.set_location(full_location=tsident.get_location())
                self.set_source(source=tsident.get_source())
                self.set_type(tsident.get_type())
                self.set_interval(tsident.get_interval())
                self.set_scenario(tsident.get_scenario())
                self.set_sequence_id(tsident.get_sequence_id())
                self.set_input_type(tsident.get_input_type())
                self.set_input_name(tsident.get_input_name())
        elif (identifier is None) and (full_location is not None) and (full_source is not None) and \
                (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
                (sequence_id is None) and (input_type is None) and (input_name is None):
            # set_identifier(full_location, full_source, full_type, interval_string, scenario)
            self.set_location(full_location=full_location)
            self.set_source(source=full_source)
            self.set_type(full_type)
            self.set_interval(interval_string)
            self.set_scenario(scenario)
        elif (identifier is None) and (full_location is not None) and (full_source is not None) and \
                (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
                (sequence_id is None) and (input_type is not None) and (input_name is not None):
            # set_identifier(full_location, full_source, type, interval_string, scenario, input_type, input_name)
            self.set_location(full_location=full_location)
            self.set_source(source=full_source)
            self.set_type(full_type)
            self.set_interval(interval_string)
            self.set_scenario(scenario)
            self.set_input_type(input_type)
            self.set_input_name(input_name)
        elif (identifier is None) and (full_location is not None) and (full_source is not None) and \
                 (full_type is not None) and (interval_string is not None) and (scenario is not None) and \
                 (sequence_id is not None) and (input_type is not None) and (input_name is not None):
            # set_identifier(full_location, full_source, type, interval_string, scenario, sequence_id,
            # input_type, input_name)
            # All not None
            self.set_location(full_location=full_location)
            self.set_source(source=full_source)
            self.set_type(full_type)
            self.set_interval(interval_string)
            self.set_scenario(scenario)
            self.set_sequence_id(sequence_id)
            self.set_input_type(input_type)
            self.set_input_name(input_name)
        else:
            raise ValueError("Unsupported parameters for set_identifier(): " +
                             "identifier=" + str(identifier) +
                             " full_location=" + str(full_location) +
                             " full_source=" + str(full_source) +
                             " full_type=" + str(full_type) +
                             " interval_string=" + str(interval_string) +
                             " scenario=" + str(scenario) +
                             " sequence_id=" + str(sequence_id) +
                             " input_type=" + str(input_type) +
                             " input_name=" + str(input_name) +
                             " tsident=" + str(tsident))

    def set_input_name(self, input_name):
        """
        Set the input name.
        :param input_name: the input name.
        """
        if input_name is not None:
            self.input_name = input_name

    def set_input_type(self, input_type):
        """
        Set the input type
        :param input_type: the input type
        """
        if input_type is not None:
            self.input_type = input_type

    def set_interval(self, interval_string=None, interval_base=None, interval_mult=None):
        """
        Set the interval given the interval string or base and multipler.
        :param interval_string: Data interval string
        :param interval_base: Base interval (see TimeInterval.*)
        :param interval_mult: Base interval multiplier.
        """
        if interval_string is not None:
            if interval_string is None:
                return
            if (interval_string != "*") and (len(interval_string) > 0):
                # First split the string into its base and multiplier...
                tsinterval = None
                if (self.behavior_mask & TSIdent.NO_VALIDATION) == 0:
                    try:
                        tsinterval = TimeInterval.parse_interval(interval_string)
                    except:
                        # Not validating so let this pass...
                        pass
                else:
                    tsinterval = TimeInterval.parse_interval(interval_string)

                # Now set the base and multiplier...
                if tsinterval is not None:
                    self.interval_base = tsinterval.get_base()
                    self.interval_mult = tsinterval.get_multiplier()
            # Else, don't do anything (leave as zero initialized values).

            # Now set the interval string. Use the given interval base string
            # because we need to preserve existing file names, etc.
            self.set_interval_string(interval_string)
            self.set_identifier()

        elif (interval_base is not None) and (interval_mult is not None):
            # Set the interval using the interval base and multiplier
            logger = logging.getLogger(__name__)
            if interval_mult <= 0:
                logger.warning("Interval multiplier ({}) must be greater than zero".format(interval_mult))
            if (interval_base != TimeInterval.SECOND) and \
                    (interval_base != TimeInterval.MINUTE) and \
                    (interval_base != TimeInterval.HOUR) and \
                    (interval_base != TimeInterval.DAY) and \
                    (interval_base != TimeInterval.WEEK) and \
                    (interval_base != TimeInterval.MONTH) and \
                    (interval_base != TimeInterval.YEAR) and \
                    (interval_base != TimeInterval.IRREGULAR):
                logger.warning("Base interval ({}) is not recognized".format(interval_base))
                return
            self.interval_base = interval_base
            self.interval_mult = interval_mult

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

            self.set_interval_string(interval_string)
            self.set_identifier()
        else:
            raise ValueError("Invalid parameters to set_interval")

    def set_interval_string(self, interval_string):
        """
        Set the interval string. This is normally only called from this class
        :param interval_string: Interval string.
        """
        if interval_string is not None:
            self.interval_string = interval_string

    def set_location(self, main_location=None, sub_location=None, full_location=None):
        """
        Set the full location from its parts. This method is generally called from
        set_main_location() and set_sub_location() methods to reset full_location.
        :param full_location: The full location string.
        :param main_location: The main location string.
        :param sub_location: The sub location string.
        """
        logger = logging.getLogger(__name__)

        if self.debug:
            logger.debug("Resetting full location from parts...")
        if (main_location is None) and (sub_location is None) and (full_location is None):
            # set_location()
            if self.debug:
                logger.debug("Resetting location from saved parts")
            if (self.behavior_mask & TSIdent.NO_SUB_LOCATION) != 0:
                # Just use the main location as the full location...
                if self.main_location is not None:
                    # There should always be a main location after the object is initialized...
                    self.set_full_location(self.main_location)
            else:
                # Concatenate the main and sub-locations to get the full location
                full_location = ""
                # We may want to check for main_location[] also...
                if self.main_location is not None:
                    # This should always be the case after the object is initialized...
                    full_location += self.main_location
                    if self.sub_location is not None:
                        # We only want to add the sublocation if it is not
                        # an empty string (it will be an empty string after the
                        # object is initialized).
                        if len(self.sub_location) > 0:
                            # Have a sub_location so append it to the main location...
                            full_location += TSIdent.LOCATION_SEPARATOR
                            full_location += self.sub_location
                    self.set_full_location(full_location)
            # Now reset the full identifier...
            self.set_identifier()
        elif (main_location is not None) and (sub_location is not None):
            # Set the location from main and sub parts
            if self.debug:
                logger.debug("Resetting location from main and sub")
            self.set_main_location(main_location)
            self.set_sub_location(sub_location)
            # The full location will be set when the parts are set.
        elif (main_location is not None) and (sub_location is None):
            # Set the location from main and sub parts
            if self.debug:
                logger.debug("Resetting location from main")
            self.set_main_location(main_location)
            # The full location will be set when the parts are set.
        elif full_location is not None:
            # Set the full location from its full string.
            if self.debug:
                logger.debug("Resetting location from full location")

            # if full_location is None:
            #    return
            if (self.behavior_mask & TSIdent.NO_SUB_LOCATION) != 0:
                # The entire string passed in is used for the main location...
                self.set_main_location(full_location)
            else:
                # Need to split the location into main and sub-location...
                sub_location = ""
                part_list = StringUtil.break_string_list(full_location, TSIdent.LOCATION_SEPARATOR, 0)
                nlist = len(part_list)
                if nlist >= 1:
                    # Set the main location...
                    self.set_main_location(part_list[0])
                if nlist >= 2:
                    # Now set the sub-location. This allows for multiple delimited
                    # parts (everything after the first delimiter is treated as the sublocation).
                    iend = nlist - 1
                    for i in range(iend + 1):
                        if i != 1:
                            sub_location += TSIdent.LOCATION_SEPARATOR
                        sub_location += part_list[i]
                    self.set_sub_location(sub_location)
                else:
                    # Since only setting the main location need to set the sub-location to an empty string...
                    self.set_sub_location("")
        else:
            raise ValueError("Invalid parameters for set_location()")

    def set_location_type(self, location_type):
        """
        Set the location type.
        :param location_type: location type.
        """
        if location_type is None:
            return
        self.location_type = location_type
        self.set_identifier()

    def set_main_location(self, main_location):
        """
        Set the main location string (and reset the full location).
        :param main_location: The location string.
        """
        if main_location is None:
            return
        self.main_location = main_location
        self.set_location()

    def set_main_source(self, main_source):
        """
        Set the main source string (and reset the full source).
        :param main_source: The main source string.
        """
        if main_source is None:
            return
        self.main_source = main_source
        self.set_source()

    def set_main_type(self, main_type):
        """
        Set the main data type string (and reset the full type).
        :param main_type: The main data type string.
        """
        if main_type is None:
            return
        self.main_type = main_type
        self.set_type()

    def set_scenario(self, scenario):
        """
        Set the scenario string
        :param scenario: The scenario string.
        """
        if scenario is None:
            return
        self.scenario = scenario
        self.set_identifier()

    def set_sequence_id(self, sequence_id):
        """
        Set the sequence identifier, for example when the time series is part of an ensemble
        :param sequence_id: sequence identifier for the time series
        """
        self.sequence_id = sequence_id
        self.set_identifier()

    def set_source(self, source=None, main_source=None, sub_source=None):
        """
        Set the full source from internal parts, from a full string, or from main and sub parts.
        :param source: the full source string
        :param main_source: the main source string
        :param sub_source: the sub source string
        """
        if (source is None) and (main_source is None) and (sub_source is None):
            # set_source()
            if (self.behavior_mask & TSIdent.NO_SUB_SOURCE) != 0:
                # Just use the main source as the full source...
                if self.main_source is not None:
                    # There should always be a main source after the object is initialized...
                    self.set_full_source(self.main_source)
            else:
                # Concatenate the main and sub-sources to get the full source.
                full_source = ""
                if self.main_source is not None:
                    # We only want to add the subsource if it is not an empty
                    # string (it will be an empty string after the object is initialized).
                    full_source += self.main_source
                    if self.sub_source is not None:
                        # We have sub_source so append it to the main source...
                        # We have a sub_source so append it to the main source...
                        if len(self.sub_source) > 0:
                            full_source += TSIdent.SOURCE_SEPARATOR
                            full_source += self.sub_source
                    self.set_full_source(full_source)
            # Now reset the full identifier...
            self.set_identifier()
            return
        elif (source is not None) and (main_source is None) and (sub_source is None):
            # set_source(source)
            if source == "":
                self.set_main_source("")
                self.set_sub_source("")
            elif (self.behavior_mask & TSIdent.NO_SUB_SOURCE) != 0:
                # The entire string passed in is used for the main source...
                self.set_main_source(source)
            else:
                # Need to split the source into main and sub-source...
                sub_source = ""
                part_list = StringUtil.break_string_list(source, TSIdent.SOURCE_SEPARATOR, 0)
                nlist = len(part_list)
                if nlist >= 1:
                    # Set the main source...
                    self.set_main_source(part_list[0])
                if nlist >= 2:
                    # Now set the sub-source...
                    iend = nlist - 1
                    for i in range(iend + 1):
                        sub_source += part_list[i]
                        if i != iend:
                            sub_source += TSIdent.SOURCE_SEPARATOR
                    self.set_sub_source(sub_source)
                else:
                    # Since we are only setting the main location we need
                    # to set the sub-location to an empty string...
                    self.set_sub_source("")
        elif (source is None) and (main_source is not None) and (sub_source is not None):
            # set_source(main_source, sub_source)
            self.set_main_source(main_source)
            self.set_sub_source(sub_source)
            # The full source will be set when the parts are set.
        else:
            raise ValueError("Invalid parameters for set_source()")

    def set_sub_source(self, sub_source):
        """
        Set the sub-source string (and reset the full source).
        :param sub_source: The sub-source string.
        """
        if sub_source is None:
            return
        self.sub_source = sub_source
        self.set_source()

    def set_sub_location(self, sub_location):
        """
        Set the sub-location string (and reset the full location).
        :param sub_location: The sub-location string
        """
        if sub_location is not None:
            return
        self.sub_location = sub_location
        self.set_location()

    def set_sub_type(self, sub_type):
        """
        Set the sub-type string (and reset the full data type).
        :param sub_type: The sub-type string.
        """
        if sub_type is None:
            return
        self.sub_type = sub_type
        self.set_type()

    def set_type(self, type=None):
        """
        Set the full data type from is parts. This method is generally called from set_main_type()
        and set_sub_type() methods to reset full_type.
        :param type: the full data type string (optional)
        """
        logger = logging.getLogger(__name__)
        if type is None:
            # set_type()
            if (self.behavior_mask & TSIdent.NO_SUB_TYPE) != 0:
                # Just use the main type as the full type...
                if self.main_type is not None:
                    # There should always be a main type after the object is initialized...
                    self.set_full_type(self.main_type)
            else:
                # Concatenate the main and sub-types to get the full type.
                full_type = ""
                if self.main_type is not None:
                    # This should always be the case after the object is initialized...
                    full_type += self.main_type
                    if self.sub_type is not None:
                        # We only want to add the subtype if it is
                        # not an empty string (it will be an empty string
                        # after the object is initialized).
                        if len(self.sub_type) > 0:
                            # We have a sub type so append it to the main type...
                            full_type += TSIdent.TYPE_SEPARATOR
                            full_type += self.sub_type
                    self.set_full_type(full_type)
            # Now reset the full identifier...
            self.set_identifier()
        else:
            # set_type(type)
            if (self.behavior_mask & TSIdent.NO_SUB_TYPE) != 0:
                # The entire string passed in is used for the main data type...
                self.set_main_type(type)
            else:
                # Need to split the data type into main and sub-locaiton...
                sub_type = ""
                part_list = StringUtil.break_string_list(type, TSIdent.TYPE_SEPARATOR, 0)
                nlist = len(part_list)
                if nlist >= 1:
                    # Set the mian type...
                    self.set_main_type(part_list[0])
                if nlist >= 2:
                    # Now set the sub-type...
                    iend = nlist - 1
                    for i in range(iend + 1):
                        sub_type += part_list[i]
                        if i != iend:
                            sub_type += TSIdent.TYPE_SEPARATOR
                    self.set_sub_type(sub_type)
                else:
                    # Since we are only setting the main type we
                    # need to set the sub-type to an empty string...
                    self.set_sub_type("")

    def to_string(self, include_input=False):
        """
        Return a string representation of the TSIdent.
        @return A string representation of the TSIdent.
        @param include_input If true, the input type and name are included in the
        identifier.  If false, the 5-part TSID is returned.
        """
        location_type = ""
        scenario = ""
        sequence_id = ""
        input_type = ""
        input_name = ""
        if (self.location_type is not None) and (len(self.location_type) > 0):
            location_type = self.location_type + TSIdent.LOC_TYPE_SEPARATOR
        if (self.scenario is not None) and (len(self.scenario) > 0):
            # Add the scenario if it is not blank...
            scenario = "." + self.scenario
        if (self.sequence_id is not None) and (len(self.sequence_id) > 0):
            # Add the sequence ID if it is not blank...
            sequence_id = TSIdent.SEQUENCE_NUMBER_LEFT + self.sequence_id + TSIdent.SEQUENCE_NUMBER_RIGHT
        if include_input:
            if (self.input_type is not None) and (len(self.input_type) > 0):
                input_type = "~" + self.input_type
            if (self.input_name is not None) and (len(self.input_name) > 0):
                input_name = "~" + self.input_name
        return location_type + self.full_location + "." + self.full_source + "." + self.full_type + \
            "." + self.interval_string + scenario + sequence_id + input_type + input_name
