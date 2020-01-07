# DataSetComponent - class to maintain information about a single component from a data set

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

# import logging


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

    def __init__(self, dataset, comp_type, comp=None, deep_copy=None):

        # Type of component - integer used to increase performance so string lookups don't need to be done.
        # -if an Enum is used, then comp_type.value is used where needed for comparisons and lookups
        self.comp_type = -1

        # Name of component
        self.name = ""

        # Name of file that will hold the data hen saved to disk
        self.data_file_name = ""

        # Name of the command file used to create the component, if _created_from is DATA_FROM_COMMANDS
        self.commandFileName = ""

        # Name of the list corresponding to the data component (e.g., used by StateDMI).
        self.list_file_name = ""

        # Indicates how the list for a component group is created (see LIST_SOURCE_*)
        self.list_source = ""

        # Data for component type (often a list of objects). If the component is a group, the data
        # will be a list of the components in the group.
        self.data = None

        # Indicates whether the component is dirty
        self.is_dirty = False

        # Indicates whether there was an error when reading the data from an input file.
        # If true, care should be taken with further processing because code may further corrupt the data and
        # file if re-written
        self.error_reading_input_file = False

        # Is the data component actually a group of components.  In this case the _data is a
        # list of StateCU_DataSetComponent.  This is determined from the group type, not
        # whether the component actually has subcomponents
        self.is_group = False

        # Is the data component being saved as output?  This is used, for example, to help know when
        # to perform data checks.
        self.is_output = False

        # Indicates if the component should be visible because of the data set type (control settings).
        # Extra components may be included in a data set to ease transition from one data set type to another.
        self.is_visible = True

        # If the component belongs to a group, this reference points to the group component.
        self.parent = None

        # The DataSet that this DataSetComponent belongs to.  It is assumed that a
        # DataSetComponent always belongs to a DataSet, even if only a partial data set (e.g., one group).
        self.dataset = None

        # A list of String used to store data check results, suitable for printing to an output
        # file header, etc.  See the __is_output flag to help indicate when check results should be created.
        self.data_check_results = None

        if comp_type is not None:
            self.DataSetComponent_init1(dataset, comp_type)

        # if not (comp == None and deep_copy == None):
        #     self.DataSetComponent_init2(comp, dataset, deep_copy)

    def DataSetComponent_init1(self, dataset, comp_type):
        """
        Construct the data set component and set values to empty strings and null.
        :param dataset: the DataSet instance that this component belongs to (note that
        the DataSet.addComponent() method must still be called to add the component).
        :param comp_type: Component type.
        """
        self.dataset = dataset
        if isinstance(comp_type, int):
            comp_type_value = comp_type
        else:
            # Assume Enum
            comp_type_value = comp_type.value
        if (comp_type_value < 0) or (comp_type_value >= len(self.dataset.component_types)):
            # Throw error
            raise ValueError("Unrecognized component type value " + comp_type_value)
        # Allow assignment
        self.comp_type = comp_type
        # size = 0
        # if self.dataset.component_groups != None:
        #     size = self.dataset.component_groups.length
        # Set whether the component is a group, based on the data set information.
        self.is_group = False
        for component_group in self.dataset.component_groups:
            if component_group == self.comp_type:
                self.is_group = True
                break
        # Set the component name, based on the data set information.
        self.name = self.dataset.lookup_component_name(self.comp_type)

    def add_component(self, component):
        """
        Add a component to this component.  This method should only be called to add
        sub-components to a group component.
        :param component: Sub-component to add to the component.
        :return:
        """
        if not self.is_group:
            # Message.printWarning (2, routine, "Trying to add component to non-group component.")
            return
        if self.data is None:
            # Allocate memory for the components
            self.data = []
        self.data.append(component)
        component.parent = self
        # if Message.isDebugOn:
        #   Message.printDebug( 1, routine, "Added " + component.getComponentName() + " to " getComponentName())

    def get_component_name(self):
        """
        Return the name of the component
        :return: the name of the component.
        """
        return self.name

    def get_component_type(self):
        """
        Get the component type
        :return: the Component type
        """
        return self.comp_type

    def get_data(self):
        """
        get the data
        :return: data
        """
        return self.data

    def get_data_file_name(self):
        """
        :return: the data file name
        """
        return self.data_file_name

    def get_is_group(self):
        """
        :return: is group
        """
        return self.is_group

    def set_data(self, data):
        """
        Set the data object containing the component's data. Often this is a Vector of objects.
        :param data: Data object containing the component's data.
        """
        self.data = data

    def set_data_file_name(self, filename):
        """
        Set the data file name
        :param filename: the filename to set as this classes filename
        """
        self.data_file_name = filename

    def set_dirty(self, is_dirty):
        """
        Set whether the component is dirty (has been edited).
        :param is_dirty: True if the component is dirty (has been edited).
        """
        self.is_dirty = is_dirty

    def set_error_reading_input_file(self, error_reading_input_file):
        """
        Set whether there was an error reading an input file.  This is useful in cases where the file
        may be hand-edited or created outside of software, or perhaps the specification has changed and the
        Java code has not caught up.  If the error flag is set to true, then software like a UI has a clue to
        NOT try to edit or save because data corruption might occur.
        :param error_reading_input_file: if True, then an error occurred reading the component data from the
        input file
        """
        self.error_reading_input_file = error_reading_input_file

    def set_list_source(self, list_source):
        """
        Set the source of the list for the component (see LIST_SOURCE_*).
        :param list_source: The source of the list for the component
        """
        self.list_source = list_source

    def set_visible(self, is_visible):
        self.is_visible = is_visible
