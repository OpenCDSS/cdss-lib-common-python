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

    def __init__(self, displayName, startyearOffset, startMonth, endYearOffset, endMonth):

        # The name that is used for choices and other technical code (terse).
        self.__displayName = str()

        # The calendar year offset in which the year starts.
        # For example, -1 indicates that the year starts in the previous calendar year.
        self.__startYearOffset = int()

        # The calendar year offset in which the year ends
        # For example, 0 indicates that the year ends in the previous calendar year.
        self.__endYearOffset = int()

        # The calendar month (1-12) when the year starts. For example, 10 indicates that the
        # year starts in October.
        self.__startMonth = int()

        # The calendar month (1-12) when the year ends. For example, 9 indicates that the year
        # ends in September.
        self.__endMonth = int()

        self.initialize_YearType(displayName, startyearOffset, startMonth, endYearOffset, endMonth)

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

    def initialize_YearType(self, displayName, startyearOffset, startMonth, endYearOffset, endMonth):
        """
        Construct an enumeration value.
        :param displayName: name that should be displayed in choices, etc.
        :param startyearOffset: the offset to the calendar year for the start of the year.
        For example, does the output year start in the same year as the calendar year (0),
        previous calendar year (-1), or next calendar year (1)?
        :param startMonth: the first calendar month (1-12) for the year type.
        :param endYearOffset: the offset to the calendar year for the end of the year.
        For example, does the output year end in the same year as the calendar year (0),
        previous calendar year (-1), or next calendar year (1)?
        :param endMonth: the last calendar month (1-12) for the year type
        """
        self.__displayName = displayName
        self.__startYearOffset = startyearOffset
        self.__startMonth = startMonth
        self.__endYearOffset = endYearOffset
        self.__endMonth = endMonth

    def getEndMonth(self):
        """
        Return the last month (1-12) in the year.
        :return: last month in the year.
        """
        return self.__endMonth

    def getEndYearOffset(self):
        """
        Return the end year offset.
        :return: the end year offset.
        """
        return self.__endYearOffset

    def getStartMonth(self):
        """
        Return the first month (1-12) in the year.
        :return: the first month in the year
        """
        return self.__startYearOffset

    def getStartYearOffset(self):
        """
        Return the start year offset.
        For example, -1 indicates that the year starts in the previous calendar year.
        :return: the start year offset
        """
        return self.__startYearOffset