# StopWatch - this class provides a way to track execution time similar to a physical stopwatch

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

from datetime import datetime
import time

class StopWatch(object):
    # This class provides a way to track execution time similar to a physical stopwatch.  To
    # use the class, declare an instance and then call "start" and "stop" as necessary
    # to add to the time.  Use "clear" to reset the timer to zero.  The time amounts
    # are tracked internally in milliseconds.  Note that the StopWatch features do
    # introduce overhead into program execution because it requests the system time
    # and should only be used when debugging or in
    # cases where the performance issues are not large.  For example, put start/stop
    # calls outside of loops, or, if in loops, consider only using if wrapped in
    # Message.isDebugOn() checks.

    def __init__(self, total = None):

        # Total elapsed running time in milliseconds
        self._total_milliseconds = float()

        # Start date for a StopWatch session.
        self._start_date = None

        # Indicates if the start time has been set
        self._start_set = bool()

        # Stop date for a StopWatch session.
        self._stop_date = None

        if total is not None:
            self.initialize(total)
        else:
            self.initialize(0)

    def add(self, sw):
        """
        Add the time from another stopwatch to the elapsed time for this stopwatch
        :param sw: the StopWatch from which to get additional time.
        """
        self._total_milliseconds += sw.getMilliseconds()

    def clear(self):
        """
        Reset the StopWatch to zero.
        """
        self._total_milliseconds = 0

    def clearAndStart(self):
        """
        Reset the StopWatch to zero and call start()
        """
        self._total_milliseconds = 0
        self.start()

    def finalize(self):
        """
        Finalize before garbage collection.
        :return:
        """
        self._start_date = None
        self._stop_date = None

    def getMilliseconds(self):
        """
        Return the accumulated milliseconds.
        :return: The number of milliseconds accumulated in the StopWatch
        """
        return self._total_milliseconds

    def getSeconds(self):
        """
        Return the accumulated seconds.
        :return: The number of seconds accumulated in the StopWatch (as a double so that
        milliseconds are also reflected).
        """
        return self._total_milliseconds/1000.0

    def initialize(self, total):
        """
        Initialize Stopwatch.
        :param total:  initial StopWatch value in milliseconds
        """
        self._total_milliseconds = total
        self._start_date = None
        self._start_set = False
        self._stop_date = None

    def start(self):
        """
        Start accumulation time in the StopWatch.
        """
        self._start_set = True
        self._start_date = time.time()

    def stop(self):
        """
        Stop accumulating time in the StopWatch.  This does not clear the StopWatch and
        subsequent calls to "start" can be made to continue adding to the StopWatch.
        """
        self._stop_date = time.time()
        # Compute the difference anc add to the elapsed time.
        if self._start_set:
            add = int(round(self._stop_date * 1000)) - int(round(self._start_date * 1000))
            self._total_milliseconds += add
        self._start_set = False

    def __str__(self):
        """
        Print the StopWatch value as seconds
        """
        return str("StopWatch(seconds)=" + str(self.getSeconds()))