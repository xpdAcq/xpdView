##############################################################################
#
# xpdView.azimuthal         SULI
#                           (c) 2016 Brookhaven Science Associates,
#                           Brookhaven National Laboratory.
#                           All rights reserved.
#
# File coded by:            Caleb Duff
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

'''
This file will handle the pyFai integration for quick azimuthal integration of the data
'''

import pyFAI
import pyFAI.calibrant


class Azimuthal(object):
    """
    This class handles all of the azimuthal integration of the data so that it can be done automatically as long
    as the data comes in as a list of 2D numpy arrays

    Attributes
    ----------
    """

    def __init__(self):
        """
        This method simply initializes the class

        Parameters
        ----------
        self

        Returns
        -------
        None
        """
        self.x_lists = []
        self.y_lists = []
        self.file_names = []

    def get_right_names(self, file_names, data_list):
        """
        This method sets up all of the file_names to their appropriate titles

        Parameters
        ----------
        file_names : list of strings
            this is the list of file names that you want associated with each image
        data_list : list of 2D numpy arrays
            this list should contain all of the 2D data that the user wants to integrate

        Returns
        -------
        None

        """
        for file in file_names:
            if file[-4:] == '.tif':
                self.file_names.append(file[:-4] + '.chi')
            else:
                self.file_names.append(file)

        self.integration_time(data_list)

    def integration_time(self, data_list):
        """
        This method will integrate the 2D images into their appropriate data forms

        Parameters
        ----------
        file_names
        data_list

        Returns
        -------
        None

        """
        # Insert pyFAI calibration parameters, can be changed if better detector parameters found
        det = pyFAI.detectors.Perkin()
        wl = 0.184320e-10
        ni = pyFAI.calibrant.ALL_CALIBRANTS("Ni")
        ni.set_wavelength(wl)
        poni1 = .1006793 * 2
        poni2 = .1000774 * 2
        ai = pyFAI.AzimuthalIntegrator(dist=0.2418217, poni1=poni1, poni2=poni2, rot1=0, rot2=0, detector=det)
        ai.set_wavelength(wl)

        for data in data_list:
            x, y = ai.integrate1d(data, 1000, unit='q_A^-1')
            self.x_lists.append(x)
            self.y_lists.append(y)

    def refresh_time(self, new_files, new_data):
        """
        This method is for when the refresh method is used in the xpd_view class

        Parameters
        ----------
        new_files : list of strings
            list of strings with all of the new file names
        new_data : list of 2D numpy arrays
            list of 2D numpy arrays to be integrated

        Returns
        -------
        The returns of refresh integrate

        """
        new_file_names = []
        for file in new_files:
            if file[-4:] == '.tif':
                self.file_names.append(file[:-4] + '.chi')
                new_file_names.append(file[:-4] + '.chi')
            else:
                self.file_names.append(file)
                new_file_names.append(file)

        return self.refresh_integrate(new_file_names, new_data)

    def refresh_integrate(self, new_files, new_data):
        """
        This method is meant to be used in conjuction with the refresh time method

        Parameters
        ----------
        new_files : list of strings
            list of new file names to be sent back
        new_data : list of 2D numpy arrays
            list of 2D arrays to be integrated

        Returns
        -------
        new_files : list of strings
            see above
        new_x_lists : list of 1D arrays
            list of the newly integrated x_data
        new_y_lists : list of 1D arrays
            list of the newly integrated y_data

        """
        det = pyFAI.detectors.Perkin()
        wl = 0.184320e-10
        ni = pyFAI.calibrant.ALL_CALIBRANTS("Ni")
        ni.set_wavelength(wl)
        poni1 = .1006793 * 2
        poni2 = .1000774 * 2
        ai = pyFAI.AzimuthalIntegrator(dist=0.2418217, poni1=poni1, poni2=poni2, rot1=0, rot2=0, detector=det)
        ai.set_wavelength(wl)

        new_x_list = []
        new_y_list = []

        for data in new_data:
            x, y = ai.integrate1d(data, 1000, unit='q_A^-1')
            self.x_lists.append(x)
            self.y_lists.append(y)
            new_x_list.append(x)
            new_y_list.append(y)

        return new_files, new_x_list, new_y_list
