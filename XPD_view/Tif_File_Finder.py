"""
This class is what gets the .tif files from the directory when entered and returns the numpy arrays used
in XPD_view. This class is designed to ensure that files are ordered according to time signature, and that
all dark tifs and raw tifs are ignored as they are being read in.
"""

from tifffile import imread
import os


class TifFileFinder(object):

    def __init__(self):
        self._directory_name = None
        self.dir_fil = []
        self.file_list = []
        self.pic_list = []

    def get_file_list(self):
        if self._directory_name is None:
            raise NotADirectoryError
        if self._directory_name[-1] != '/' or '\\':
            self._directory_name += '/'
        self.dir_fil = os.listdir(self._directory_name)
        self.dir_fil.sort(key=lambda x: os.path.getmtime(self._directory_name + x))
        self.file_list = [file for file in self.dir_fil if file.endswith('.tif') and not (file.endswith('.dark.tif') or
                                                                                          file.endswith('.raw.tif'))]
        print(len(self.file_list))
        self.get_image_arrays()

    def get_image_arrays(self):
        self.pic_list = []
        for i in self.file_list:
            self.pic_list.append(imread(self._directory_name + i))

    def get_new_files(self):
        self.dir_fil = os.listdir(self._directory_name)
        no1 = '.dark.tif'
        no2 = '.raw.tif'
        self.dir_fil.sort(key=lambda x: os.path.getmtime(self._directory_name + x))
        new_file_list = [el for el in self.dir_fil
                         if el.endswith('.tif') and not (el.endswith(no1) or el.endswith(no2))]
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
        new_pics = []
        if temp_file_list is not None:
            for i in temp_file_list:
                self.pic_list.append(imread(self._directory_name + i))
                new_pics.append(imread(self._directory_name + i))
        return temp_file_list, new_pics
