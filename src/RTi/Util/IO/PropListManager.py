# PropListManager - manage a list of property lists

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


class PropListManager(object):
    # This class manages a list of PropList objects.  It is generally only used for
    # applications where several property lists need to be evaluated to determine the
    # value of properties.  For example, an application may support a user
    # configuration file, a system configuration file, and run-time user settings.
    # Each source of properties can be stored in a separate PropList and can be
    # managed by PropListManager.  This class has several functions that can handle
    # recursive checks of PropLists and can expand configuration contents.

    def __init__(self):
        self.proplists = []
        self.initialize()

    def get_prop_lists(self):
        """
        Return the list of PropLists managed by this PropListManager.
        """
        return self._proplists

    def initialize(self):
        self.proplists = []
        return 0