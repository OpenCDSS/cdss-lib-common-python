# YearType - Year Types, which indicate the span of months that define a year.
import logging


class YearType(object):
    """
    Year types, which indicate the span of months that define a year.  For example "Water Year" is often
    used in the USA to indicate annual water volumes, based on seasons.  This enumeration should be used to
    indicate common full-year definitions.  Year types that include only a season or part of the year could
    specify this enumeration for full years and would otherwise need to define the year in some other way.
    By convention, non-calendar year types that do not contain "Year" in the name start in the previous
    calendar year and end in the current calendar year.  As new year types are added they should conform to the
    standard of starting with "Year" if the start matches the calendar year, and ending with "Year" if the end
    matches the calendar year.

    Ideally this could be an enumeration, but Python enumerations are simple and don't have data for each value.
    """

    # Year is January to December
    CALENDAR = 1
    # Year is November of previous year to October of current year
    NOV_TO_OCT = 2
    # Year is October of previous year to November of current year
    WATER = 3
    # Year is May to April of current year
    YEAR_MAY_TO_APR = 4

    def __init__(self, year_type, display_name=None, start_year_offset=None, start_month=None,
                 end_year_offset=None, end_month=None):
        """
        Create an instance of YearType.
        Typically this is done using the integer year_type, which has predefined values.
        Internally, the year_type call results in calling the constructor with specific values depending on the type.
        :param year_type:
        :param display_name:
        :param start_year_offset:
        :param start_month:
        :param end_year_offset:
        :param end_month:
        """

        # The year type number (essentially an enumeration) from above.
        self.year_type = None

        # The name that is used for choices and other technical code (terse).
        self.display_name = None

        # The calendar year offset in which the year starts.
        # For example, -1 indicates that the year starts in the previous calendar year.
        self.start_year_offset = None

        # The calendar year offset in which the year ends
        # For example, 0 indicates that the year ends in the previous calendar year.
        self.end_year_offset = None

        # The calendar month (1-12) when the year starts. For example, 10 indicates that the
        # year starts in October.
        self.start_month = None

        # The calendar month (1-12) when the year ends. For example, 9 indicates that the year
        # ends in September.
        self.end_month = None

        # Now initialize the values based on the method parameters

        if start_month is not None:
            # Values are being specified so initialize with those values
            self.initialize_yeartype(year_type, display_name, start_year_offset, start_month, end_year_offset,
                                     end_month)
        elif year_type is not None:
            # start_month is not specified so create an instance from the type
            if year_type == YearType.CALENDAR:
                self.initialize_CALENDAR()
            elif year_type == YearType.NOV_TO_OCT:
                self.initialize_NOV_TO_OCT()
            elif year_type == YearType.WATER:
                self.initialize_WATER()
            elif year_type == YearType.YEAR_MAY_TO_APR:
                self.initialize_YEAR_MAY_TO_APR()
            else:
                raise ValueError("Unknown year type " + str(year_type))
        else:
            raise ValueError("No valid data provided to create YearType")

    def __eq__(self, an_instance):
        """
        Evaluate whether an instance is equal to this instance using year_type.
        :param an_instance:  an instance to compare
        :return: True if equivalent, False if not.
        """
        logger = logging.getLogger(__name__)
        if isinstance(an_instance, YearType):
            # Comparing to another instance
            an_instance_year_type = an_instance.year_type
        elif isinstance(an_instance, int):
            # Comparing to an integer
            an_instance_year_type = an_instance
        else:
            raise ValueError("Can't compare YearType to " + type(an_instance))

        if self.year_type == an_instance_year_type:
            return True
            # TODO smalers 2020-01-04 evaluate whether alternate equivalent types are allowed,
            # for example everything is the same except year_type and display_name
            # if (self.start_month == an_instance.start_month) and (self.end_month == an_instance.end_month) and \
            #        (self.start_year_offset == an_instance.start_year_offset):
            #    return True
        else:
            return False

    def __ne__(self, an_instance):
        # Use the equality methoc and negate the result
        if self == an_instance:
            return False
        else:
            return True

    def __str__(self):
        """
        Return a string representation of object, just return the name.
        :return:
        """
        return self.display_name

    def initialize_CALENDAR(self):
        self.year_type = YearType.CALENDAR
        self.display_name = "Calendar"
        self.start_year_offset = 0
        self.start_month = 1
        self.end_year_offset = 0
        self.end_month = 12

    def initialize_NOV_TO_OCT(self):
        self.year_type = YearType.NOV_TO_OCT
        self.display_name = "NovToOct"
        self.start_year_offset = -1
        self.start_month = 11
        self.end_year_offset = 0
        self.end_month = 10

    def initialize_WATER(self):
        self.year_type = YearType.WATER
        self.display_name = "Water"
        self.start_year_offset = -1
        self.start_month = 10
        self.end_year_offset = 0
        self.end_month = 9

    def initialize_YEAR_MAY_TO_APR(self):
        self.year_type = YearType.YEAR_MAY_TO_APR
        self.display_name = "YearMayToApr"
        self.start_year_offset = 0
        self.start_month = 5
        self.end_year_offset = 1
        self.end_month = 4

    def initialize_yeartype(self, year_type, display_name, start_year_offset, start_month, end_year_offset,
                            end_month):
        """
        Construct an enumeration value.
        :param year_type: Year type as integer
        :param display_name: name that should be displayed in choices, etc.
        :param start_year_offset: the offset to the calendar year for the start of the year.
        For example, does the output year start in the same year as the calendar year (0),
        previous calendar year (-1), or next calendar year (1)?
        :param start_month: the first calendar month (1-12) for the year type.
        :param end_year_offset: the offset to the calendar year for the end of the year.
        For example, does the output year end in the same year as the calendar year (0),
        previous calendar year (-1), or next calendar year (1)?
        :param end_month: the last calendar month (1-12) for the year type
        """
        self.year_type = year_type
        self.display_name = display_name
        self.start_year_offset = start_year_offset
        self.start_month = start_month
        self.end_year_offset = end_year_offset
        self.end_month = end_month

    def get_end_month(self):
        """
        Return the last month (1-12) in the year.
        :return: last month in the year.
        """
        return self.end_month

    def get_end_year_offset(self):
        """
        Return the end year offset.
        :return: the end year offset.
        """
        return self.end_year_offset

    def get_start_month(self):
        """
        Return the first month (1-12) in the year.
        :return: the first month in the year
        """
        return self.start_year_offset

    def get_start_year_offset(self):
        """
        Return the start year offset.
        For example, -1 indicates that the year starts in the previous calendar year.
        :return: the start year offset
        """
        return self.start_year_offset

    @staticmethod
    def value_of_ignore_case(value_string):
        """
        Return an instance of YearType given a string, or None if not matched.
        :param value_string: String value for year type, for example "WATER".
        :return: YearType instance for string value
        """
        value_string_upper = value_string.upper()
        if value_string_upper == "CAL" or value_string_upper == "CALENDAR":
            return YearType(YearType.CALENDAR)
        elif value_string_upper == "NOV" or value_string_upper == "NOV_TO_OCT":
            return YearType(YearType.NOV_TO_OCT)
        elif value_string_upper == "WAT" or value_string_upper == "WATER":
            return YearType(YearType.WATER)
        elif value_string_upper == "YEAR_MAY_TO_APR":
            return YearType(YearType.YEAR_MAY_TO_APR)
        else:
            return None
