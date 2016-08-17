##############################################################################
#
# XPD_view.Tif_File_Finder     SULI and HSRP
#                              (c) 2016 Brookhaven Science Associates,
#                              Brookhaven National Laboratory.
#                              All rights reserved.
#
# File coded by:               Caleb Duff
#                              Joseph Kaming-Thanassi
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
This class is what gets the .tif files from the directory when entered and returns the numpy arrays used
in XPD_view. This class is designed to ensure that files are ordered according to time signature, and that
all dark tifs and raw tifs are ignored as they are being read in.
"""

from tifffile import imread
import os


class TifFileFinder(object):
    """
    This class finds tif and tiff files for the user and reads them in to be used later in the GUI

    Attributes
    ----------
    _directory_name : str
        The name of directory that contains tif files that user wants to see
    dir_fil : list of strings
        list of all files in directory
    file_list : list of strings
        list of all tif files in directory
    pic_list : list of 2D numpy arrays
        list of all data read in from the tif files
    """

    def __init__(self):
        """
        This initializes the TifFileFinder class

        Returns
        -------
        None
        """
        self._directory_name = None
        self.dir_fil = []
        self.file_list = []
        self.pic_list = []

    def get_file_list(self):
        """
        This class gets the initial list of tif files

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
        self.file_list = [file for file in self.dir_fil if file.endswith('.tif') and not (file.endswith('.dark.tif') or
                                                                                          file.endswith('.raw.tif'))]
        self.get_image_arrays()

    def get_image_arrays(self):
        """
        This method reads in the tif files into 2D numpy arrays and appends them to the class's pic_list

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        for i in self.file_list:
            self.pic_list.append(imread(self._directory_name + i))

    def get_new_files(self):
        """
        This method finds new tif files in the directory for the user

        Parameters
        ----------
        self

        Returns
        -------
        all returns from the get_new_images method

        """
        self.dir_fil = os.listdir(self._directory_name)
        self.dir_fil.sort(key=lambda x: os.path.getmtime(self._directory_name + x))
        new_file_list = [file for file in self.dir_fil if file.endswith('.tif') and not (file.endswith('.dark.tif') or
                                                                                         file.endswith('.raw.tif'))]
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
        return self.get_new_images(need_read_files)

    def get_new_images(self, temp_file_list):
        """
        This method reads in the newly found files if there are any and returns them

        Parameters
        ----------
        self
        temp_file_list : list of strings
            temporary list containing all of the new names

        Returns
        -------
        temp_file_list: list of strings
            see above
        new_pic: list of 2D numpy arrays
            temporary list of all new read in data

        """
        new_pics = []
        if temp_file_list is not None:
            for i in temp_file_list:
                self.pic_list.append(imread(self._directory_name + i))
                new_pics.append(imread(self._directory_name + i))
        return temp_file_list, new_pics
