# YearType - Year Types, which indicate the span of months that define a year.

# Year types, which indicate the span of months that define a year.  For example "Water Year" is often
# used in the USA to indicate annual water volumes, based on seasons.  This enumeration should be used to
# indicate common full-year definitions.  Year types that include only a season or part of the year could
# specify this enumeration for full years and would otherwise need to define the year in some other way.
# By convention, non-calendar year types that do not contain "Year" in the name start in the previous
# calendar year and end in the current calendar year.  As new year types are added they should conform to the
# standard of starting with "Year" if the start matches the calendar year, and ending with "Year" if the end
# matches the calendar year.


class YearType():

    def __init__(self, display_name, start_year_offset, start_month, end_year_offset, end_month):

        # The name that is used for choices and other technical code (terse).
        self.display_name = str()

        # The calendar year offset in which the year starts.
        # For example, -1 indicates that the year starts in the previous calendar year.
        self.start_year_offset = int()

        # The calendar year offset in which the year ends
        # For example, 0 indicates that the year ends in the previous calendar year.
        self.end_year_offset = int()

        # The calendar month (1-12) when the year starts. For example, 10 indicates that the
        # year starts in October.
        self.start_month = int()

        # The calendar month (1-12) when the year ends. For example, 9 indicates that the year
        # ends in September.
        self.end_month = int()

        self.initialize_yeartype(display_name, start_year_offset, start_month, end_year_offset, end_month)

    @staticmethod
    def YearType_CALENDAR():
        yearType = YearType("Calendar", 0, 1, 0, 12)
        return yearType

    @staticmethod
    def YearType_NOV_TO_OCT():
        yearType = YearType("NovToOct", -1, 11, 0, 10)
        return yearType

    @staticmethod
    def YearType_WATER():
        yearType = YearType("Water", -1, 11, 0, 10)
        return yearType

    @staticmethod
    def YearType_YEAR_MAY_TO_APR():
        yearType = YearType("YearMayToApr", 0, 5, 1, 4)
        return yearType

    def initialize_yeartype(self, display_name, start_year_offset, start_month, end_year_offset, end_month):
        """
        Construct an enumeration value.
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