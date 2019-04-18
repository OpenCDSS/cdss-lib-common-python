# PropListManager - manage a list of property lists

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
 # PropListManager - manage a list of property lists
 # ----------------------------------------------------------------------------
 # Copyright: see the COPYRIGHT file
 # ----------------------------------------------------------------------------
 # History:
 #
 # Sep 1997	Steven A. Malers	Original version.
	# 	Riverside Technology,
	# 	inc.
 # 02 Feb 1998	SAM, RTi		Update so all Prop* classes work
	# 				together.
 # 24 Feb 1998	SAM, RTi		Add javadoc comments.  Clean up some
	# 				code where values were being handled
	# 				as Object rather than String.
 # 27 Apr 2001	SAM, RTi		Change all debug levels to 100.
 # 10 May 2001	SAM, RTi		Add finalize().  Optimize code for
	# 				unused variables, loops.
 # 2001-11-08	SAM, RTi		Synchronize with UNIX code... Add
	# 				handling of literal quotes.
 # 2002-10-11	SAM, RTi		Change ProcessManager to
	# 				ProcessManager1.
 # 2002-10-16	SAM, RTi		Revert to ProcessManager - seems to work
	# 				OK with cleaned up ProcessManager!
 # 2003-09-26	SAM, RTi		Fix problem where parsePropString() was
	# 				not handling "X=" - now it sets the
	# 				property to a blank string.
 # 2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
 # ----------------------------------------------------------------------------

class PropListManager(object):
    # This class manages a list of PropList objects.  It is generally only used for
    # applications where several property lists need to be evaluated to determine the
    # value of properties.  For example, an application may support a user
    # configuration file, a system configuration file, and run-time user settings.
    # Each source of properties can be stored in a separate PropList and can be
    # managed by PropListManager.  This class has several functions that can handle
    # recursive checks of PropLists and can expand configuration contents.

    def __init__(self):
        self._proplists = []
        self.initialize()

    def getPropLists(self):
        """
        Return the list of PropLists managed by this PropListManager.
        """
        return self._proplists

    def initialize(self):
        self._proplists = []
        return 0