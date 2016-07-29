"""
This class will handle reading in .chi files from the directory so that XPD view can show
the 1-D integration patterns extracted from the .chi files
"""

import numpy as np
import os


class ChiFileFinder(object):

    def __init__(self):
        self._directory_name = None
        self.dir_fil = []
        self.file_list = []
        self.x_lists = []
        self.y_lists = []

    def get_file_list(self):
        if self._directory_name is None:
            raise NotADirectoryError
        if self._directory_name[-1] != '/' or '\\':
            self._directory_name += '/'
        self.dir_fil = os.listdir(self._directory_name)
        self.dir_fil.sort(key=lambda x: os.path.getmtime(self._directory_name + x))
        self.file_list = [file for file in self.dir_fil if file.endswith('.chi')]
        self.get_data_lists()

    def get_data_lists(self):
        temp = []

        for file in self.file_list:
            temp = np.loadtxt(self._directory_name+file, skiprows=4)
            x, y = np.hsplit(temp, 2)
            self.x_lists.append(x)
            self.y_lists.append(y)

    def get_new_files(self):
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
        return self.get_new_images(need_read_files)

    def get_new_images(self, temp_file_list):
        if temp_file_list is not None:
            for i in temp_file_list:
                temp = np.loadtxt(self._directory_name+i, skiprows=4)
                x, y = np.hsplit(temp, 2)
                self.x_lists.append(x)
                self.y_lists.append(y)
