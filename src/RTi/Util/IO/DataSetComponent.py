# DataSetComponent - class to maintain information about a single component from a data set

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

# -----------------------------------------------------------------------------
#  DataSetComponent - an object to maintain information about a single
# 			component from a data set
# -----------------------------------------------------------------------------
#  History:
#
#  2003-07-12	Steven A. Malers, RTi	Created class. Copy
# 					StateCU_DataSetComponent and make more
# 					general.
#  2003-07-15	J. Thomas Sapienza, RTi	Added hasData()
#  2003-10-13	SAM, RTi		* Initialize __is_dirty and __is_group
# 					  to false.
# 					* Add a copy constructor.
#  2005-04-26	J. Thomas Sapienza, RTi	Added all data members to finalize().
#  2006-04-10	SAM, RTi		* Added isOutput() to indicate whether
# 					  the component is being created as
# 					  output.  This is used to evaluate
# 					  whether data checks need to be done.
# 					* Add getDataCheckResults() and
# 					  setDataCheckResults() to handle
# 					  verbose output for data checks.
#  2007-05-08	SAM, RTi		Cleanup code based on Eclipse feedback.
# -----------------------------------------------------------------------------

import logging

class DataSetComponent(object):
    """
    This DataSetComponent class stores information for a single data component in a data set.
    Typically, each component corresponds to a file, a table in a database or a
    section within a single monolithic data file.  A list of components is maintained in the DataSet class.
    Components may be initialized during automated data processing or may be read and then edited in a UI.
    """

    # Indicate how the list for a component group is created.
    LIST_SOURCE_PRIMARY_COMPONENT = "PrimaryComponent"
    LIST_SOURCE_NETWORK_COMPONENT = "Network"
    LIST_SOURCE_LISTFILE = "ListFile"

    def __init__(self, dataset, type, comp = None, deep_copy = None):

        # Type of component - integer used to increase performance so string lookups don't need to be done.
        self.__type = -1

        # Name of component
        self.__name = ""

        # Name of file that will hold the data when saved to disk
        self.__data_file_name = ""

        # Name of the command file used to create the component, if _created_from is DATA_FROM_COMMANDS
        self.__commandFileName = ""

        # Name of the list corresponding to the data component (e.g., used by StateDMI).
        self.__list_file_name = ""

        # Indicates how the list for a component group is created (see LIST_SOURCE_*)
        self.__list_source = ""

        # Data for component type (often a list of objects). If the component is a group, the data
        # will be a list of the components in the group.
        self.__data = None

        # Indicates whether the component is dirty
        self.__is_dirty = False

        # Indicates whether there was an error when reading the data from an input file.
        # If true, care should be taken with further processing because code may further corrupt the data and
        # file if re-written
        self.__errorReadingInputFile = False

        # Is the data component actually a group of components.  In this case the _data is a
        # list of StateCU_DataSetComponent.  This is determined from the group type, not
        # whether the component actually has subcomponents
        self.__is_group = False

        # Is the data component being saved as output?  This is used, for example, to help know when
        # to perform data checks.
        self.__is_output = False

        # Indicates if the component should be visible because of the data set type (control settings).
        # Extra components may be included in a data set to ease transition from one data set type to another.
        self.__is_visible = True

        # If the component belongs to a group, this reference points to the group component.
        self.__parent = None

        # The DataSet that this DataSetComponent belongs to.  It is assumed that a
        # DataSetComponent always belongs to a DataSet, even if only a partial data set (e.g., one group).
        self.__dataset = None

        # A list of String used to store data check results, suitable for printing to an output
        # file header, etc.  See the __is_output flag to help indicate when check results should be created.
        self.__data_check_results = None

        if type is not None:
            self.DataSetComponent_init1(dataset, type)

        # if not (comp == None and deep_copy == None):
        #     self.DataSetComponent_init2(comp, dataset, deep_copy)

    def DataSetComponent_init1(self, dataset, type):
        """
        Construct the data set component and set values to empty strings and null.
        :param dataset: the DataSet instance that this component belongs to (note that
        the DataSet.addComponent() method must still be called to add the component).
        :param type: Component type.
        """
        self.__dataset = dataset
        if (type < 0) or (type >= len(self.__dataset._component_types)):
            # Throw error
            pass
        self.__type = type
        # size = 0
        # if self.__dataset._component_groups != None:
        #     size = self.__dataset._component_groups.length
        # Set whether the component is a group, based on the data set information.
        self.__is_group = False
        for component_group in self.__dataset._component_groups:
            if component_group == self.__type:
                self.__is_group = True
                break
        # Set the component name, based on the data set information.
        self.__name = self.__dataset.lookupComponentName(self.__type)

    def addComponent(self, component):
        """
        Add a component to this component.  This method should only be called to add
        sub-components to a group component.
        :param component: Sub-component to add to the component.
        :return:
        """
        routine = "DataSetComponent.addComponent"
        if not self.__is_group:
            # Message.printWarning (2, routine, "Trying to add component to non-group component.")
            return
        if self.__data == None:
            # Allocate memory for the components
            self.__data = []
        self.__data.append(component)
        component.__parent = self
        # if Message.isDebugOn:
        #   Message.printDebug( 1, routine, "Added " + component.getComponentName() + " to " getComponentName())

    def getComponentName(self):
        """
        Return the name of the component
        :return: the name of the component.
        """
        return self.__name

    def getComponentType(self):
        """
        Get the component type
        :return: the Component type
        """
        return self.__type

    def getData(self):
        """
        get the data
        :return: data
        """
        return self.__data

    def getDataFileName(self):
        """
        :return: the data file name
        """
        return self.__data_file_name

    def isGroup(self):
        """
        :return: is group
        """
        return self.__is_group

    def setData(self, data):
        """
        Set the data object containing the component's data. Often this is a Vector of objects.
        :param data: Data object containing the component's data.
        """
        self.__data = data

    def setDataFileName(self, filename):
        """
        Set the data file name
        :param filename: the filename to set as this classes filename
        """
        self.__data_file_name = filename

    def setDirty(self, is_dirty):
        """
        Set whether the component is dirty (has been edited).
        :param is_dirty: True if the component is dirty (has been edited).
        """
        self.__is_dirty = is_dirty

    def setErrorReadingInputFile(self, errorReadingInputFile):
        """
        Set whether there was an error reading an input file.  This is useful in cases where the file
        may be hand-edited or created outside of software, or perhaps the specification has changed and the
        Java code has not caught up.  If the error flag is set to true, then software like a UI has a clue to
        NOT try to edit or save because data corruption might occur.
        :param errorReadingInputFile: if True, then an error occurred reading the component data from the
        input file
        """
        self.__errorReadingInputFile = errorReadingInputFile

    def setListSource(self, list_source):
        """
        Set the source of the list for the component (see LIST_SOURCE_*).
        :param list_source: The source of the list for the component
        """
        self.__list_source = list_source

    def setVisible(self, is_visible):
        self.__is_visible = is_visible