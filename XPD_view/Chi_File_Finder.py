"""
This class will handle reading in .chi files from the directory so that XPD view can show
the 1-D integration patterns extracted from the .chi files
"""

import numpy as np
import os


class ChiFileFinder(object):
    """
    This class handles the finding of .chi files for the user

    Attributes
    ----------
    _directory_name : strings
        the directory in which the program should search for chi files
    dir_fil : list of strings
        contains the list of all the files in general that are read in
    file_list : list of strings
        contains the list of chi files found in the directory
    x_lists : list of 1D numpy arrays
        contains the lists of x-axis data that are found in the chi files
    y_lists : list of 1D numpy arrays
        same as above, just for the y-axis
    """

    def __init__(self):
        """
        This method initializes the class
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        self._directory_name = None
        self.dir_fil = []
        self.file_list = []
        self.x_lists = []
        self.y_lists = []

    def get_file_list(self):
        """
        This method gets all of the chi files from the directory and organizes them according to the time they were
        made

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        if self._directory_name is None:
            raise NotADirectoryError
        if self._directory_name[-1] != '/' or '\\':
            self._directory_name += '/'
        self.dir_fil = os.listdir(self._directory_name)
        self.dir_fil.sort(key=lambda x: os.path.getmtime(self._directory_name + x))
        self.file_list = [file for file in self.dir_fil if file.endswith('.chi')]
        self.get_data_lists()

    def get_data_lists(self):
        """
        This method reads in the data from the files and then splits it up into the x and y data

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        temp = []

        for file in self.file_list:
            temp = np.loadtxt(self._directory_name+file, skiprows=4)
            x, y = np.hsplit(temp, 2)
            self.x_lists.append(x)
            self.y_lists.append(y)

    def get_new_files(self):
        """
        This method checks for new files and being the read in process for them

        Parameters
        ----------
        self

        Returns
        -------
        The returns of the get_new_data method

        """
        self.dir_fil = os.listdir(self._directory_name)
        self.dir_fil.sort(key=lambda x: os.path.getmtime(self._directory_name + x))
        new_file_list = [file for file in self.dir_fil if file.endswith('.chi')]
        need_read_files = []
        for i in new_file_list:
            add = True
            for j in self.file_list:
                if i == j:
                    add = False
                    break
            if add:
                self.file_list.append(i)
                need_read_files.append(i)
        return self.get_new_data(need_read_files)

    def get_new_data(self, temp_file_list):
        """
        This method gets the new data from the files that get_new_files determined had not been read in yet

        Parameters
        ----------
        temp_file_list : list of strings
            a list of strings that correspond to all of the new files that need to be read in

        Returns
        -------
        temp_file_list : list of strings
            see above
        temp_data_x : list of 1D numpy arrays
            a temporary list of all the new x axis data
        temp_data_y : list of 1D numpy arrays
            a temporary list of all the new y axis data

        """
        temp_data_x = []
        temp_data_y = []
        if temp_file_list is not None:
            for i in temp_file_list:
                temp = np.loadtxt(self._directory_name+i, skiprows=4)
                x, y = np.hsplit(temp, 2)
                self.x_lists.append(x)
                self.y_lists.append(y)
                temp_data_x.append(x)
                temp_data_y.append(y)
        return temp_file_list, temp_data_x, temp_data_y
