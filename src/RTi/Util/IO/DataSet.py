# DataSet - class to manage a list of DataSetComponent

# NoticeStart

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

from RTi.Util.IO.DataSetComponent import DataSetComponent
import logging


class DataSet(object):
    """
    This DataSet class manages a list of DataSetComponent, typically for use with
    a model where each component corresponds to a file or section of data within
    a file.  This class should be extended to provide specific functionality for a data set.
    """

    def __init__(self, component_types=None, component_names=None, component_groups=None,
                 component_group_assignments=None, component_group_primaries=None, type=None,
                 dataset_dir=None, basename=None):

        # Base name for data set, used to provide default file names when creating new files
        self.basename = ""

        # List of data components in the data set. Each component is a type that is described
        # in the lookup arrays for the data set, and has data for the component. Components are
        # hierarchical and therfore the top level components will contain groups.

        self.components = None

        # Array of component names, used in lookups
        self.component_names = None

        # Array of component types (as integers), corresponding to the component names
        self.component_types = None

        # Array of component types (as integers) that are group components.
        self.component_groups = None

        # Array of component types (as integers) that indicates the group components for each component.
        self.component_group_assignments = None

        # Array of component types (as integers) that indicates the primary components for each group.
        # These components are used to get the list of object identifiers for displays and processing.
        self.component_group_primaries = None

        # Directory for data set.
        self.dataset_dir = ""

        # Name of the data set file (XML file).
        self.dataset_filename = ""

        self.type = -1

        # print("component_types: " + str(component_types))
        # print("component_names: " + str(component_names))
        # print("component_groups: " + str(component_groups))
        # print("component_group_assignments: " + str(component_group_assignments))
        # print("component_group_primaries: " + str(component_group_primaries))
        # print("type: " + str(type))
        # print("dataset_dir: " + str(dataset_dir))
        # print("basename: " + str(basename))

        # Call the appropriate constructor given the parameters passed to __init__
        if not (component_types is None and component_names is None and component_groups is None
                and component_group_assignments is None and component_group_primaries is None):
            self.DataSet_init2(component_types, component_names, component_groups, component_group_assignments,
                               component_group_primaries)
        elif not (type is None and dataset_dir is None and basename is None):
            self.DataSet_init3(type, dataset_dir, basename)
        else:
            self.DataSet_initDefault()

    def DataSet_initDefault(self):
        """
        Construct a blank data set. It is expected that other information will be set during
        further processing. Component groups are not initialized until a data set type is set.
        """
        self.components = []

    def DataSet_init2(self, component_types, component_names, component_groups, component_group_assignments,
                      component_group_primaries):
        """
        Construct a blank data set.  It is expected that other information will be set
        during further processing.
        :param component_types: Array of sequential integers (0...N) that are used to
        identify components.  Integers are used to optimize processing in classes that
        use the data set.  Components can be groups or individual components.
        :param component_names: Array of String component names, suitable for use in
        displays and messages.
        :param component_groups: A subset of the component_types array, in the same order
        as component_types, indicating the components that are group components
        :param component_group_assignments: An array of integers containing values for
        each value in component_types.  The values should be the component group for
        each individual component.
        :param component_group_primaries: An array of integers, having the same length
        as component_groups, indicating the components within the group that are the
        primary components.  One primary component should be identified for each group
        and the primary component will be used to supply a list of objects/identifiers
        to create the list of objects identifiers in the group.
        """
        self.components = []
        self.component_types = component_types
        self.component_names = component_names
        self.component_groups = component_groups
        self.component_group_assignments = component_group_assignments
        self.component_group_primaries = component_group_primaries

    def DataSet_init3(self, type, dataset_dir, basename):
        """
        Construct a blank data set.  Specific output files, by default, will use the
        output directory and base file name in output file names.  The derived class
        method should initialize the specific data components.
        :param type: Data set type.
        :param dataset_dir: Data set directory.
        :param basename: Basename for files (no directory).
        """
        self.components = []
        self.type = type
        self.dataset_dir = dataset_dir
        self.basename = basename

    def add_component(self, comp):
        """
        Add a component to the data set.
        :param comp: Component to add.
        """
        self.components.append(comp)

    def get_component_for_component_type(self, type):
        """
        Return the component for the requested data component type.
        :param type: Component type
        :return: the component for the requested data component type or null if
        the component is not in the data set.
        """
        # logger = logging.getLogger("StateMod")
        # logging.info("looking up component " + type)
        for component in self.components:
            # logging.info("Checking " + comp.get_component_type())
            if component.get_component_type() == type:
                return component
            # If the component is a group and did not match the type, check
            # the sub-types in the component...
            if component.is_group():
                v = component.get_data()
                if v is not None:
                    for component in v:
                        if component.get_component_type() == type:
                            return component
        return None

    def get_dataset_directory(self):
        """
        :return: the directory for the data set
        """
        return self.dataset_dir

    def lookup_component_name(self, component_type):
        """
        Return the component name given its number
        :param component_type:
        :return: the component name given its number or null if the component type is not
        found.
        """
        # The component types are not necessarily numbers that match array indices so that
        # match the type values
        for i, component_type_search in enumerate(self.component_types):
            if component_type == component_type_search:
                return self.component_names[i]

    def set_dataset_directory(self, dir):
        """
        Set the directory for the data set.
        :param dir: Directory for the data set.
        """
        self.dataset_dir = dir

    def set_dataset_filename(self, filename):
        """
        SEt the file name (no directory) for the data set (XML file).
        :param filename: Directory for the data set.
        """
        self.dataset_filename = filename

    def set_dataset_type(self, type, initialize_components):
        """
        Set the data set type.
        :param type: Data set type.
        :param initialize_components: If true, the components are cleared and the
        component groups for the type are initialized by calling the
        initializeDataSet() method, which should be defined in the extended class.
        """
        self.type = type
        if initialize_components:
            self.components.clear()

    def set_dirty(self, component_type, is_dirty):
        comp = self.get_component_for_component_type(component_type)
        if comp is not None:
            comp.set_dirty(is_dirty)
