"""module to provide file-based I/O function"""
import os
import numpy as np

def chi_read(fn):
    """wrapper for reading .chi files

    Parameters
    ----------
    fn : str
        filename of .chi files

    Return
    ------
    array : ndarray
        n by 2 array. first row is data grid, second row is data values
    """
    try:
        array =np.loadtxt(fn)
    except OSError:
        # fit2d format
        array = np.loadtxt(fn, skiprows=4)
    return array


def load_files(filepath, img_data_ext, int_data_ext,
               int_data_prefix=None):
    """
    function to include loading logic for filebased operation

    Parameters
    ----------
    filepath : str
        path to the directory
    img_data_ext : str
        extention of image data will be loaded in.
        expects '.npy' or '.tif'
    int_data_ext : str
        extention of 1d reduced data will be loaded in.
        expects '.gr' or '.chi'
    int_data_prefix : str, optional
        additional prefix of 1d reduced data

    Returns
    -------
    (img_key_list, operation_list, unit)
    """
    unit = None # will be updated later
    sorted_fn_list = sorted(os.listdir(filepath))
    img_data_fn_list = [f for f in sorted_fn_list\
                        if os.path.splitext(f)[1] == img_data_ext]
    if not img_data_fn_list:
        print("INFO: can't find 2d image data with extension = {} "
              "in directory = {}".format(img_data_ext, filepath))
        return (None, None)

    img_key_list = list(map(lambda x: os.path.splitext(x)[0],
                            img_data_fn_list))
    # construct valid chi file name assuming xpdAn/xpdAcq logic
    # Note: we only read "Q_" as prefix
    int_data_fn_list_Q = []
    int_data_fn_list_fit2d = []
    for fn in img_key_list:
        Q_fn = ''.join([int_data_prefix, fn, int_data_ext])
        if os.path.isfile(os.path.join(filepath, Q_fn)):
            int_data_fn_list_Q.append(Q_fn)
        fit2d_fn = ''.join([fn, int_data_ext])
        if os.path.isfile(os.path.join(filepath, fit2d_fn)):
            int_data_fn_list_fit2d.append(fit2d_fn)
    if not int_data_fn_list_Q and not int_data_fn_list_fit2d:
        # no 1d data, only update image
        print("INFO: can't find reduced data with extension = {} in "
              "directory = {}".format(int_data_ext, filepath))
        print("INFO: only 2d image viewer will be updated")
        operation_list = img_data_fn_list
    else:
        # find lists of reduced data -> check if they are valid
        if len(int_data_fn_list_Q) == len(img_data_fn_list):
            # xpdAn logic first
            operation_list = zip(img_data_fn_list,
                                 int_data_fn_list_Q)
            # further determine y label
            unit = ('Q(nm$^{-1}$)', 'I(Q), a.u.)')
        elif len(int_data_fn_list_fit2d) == len(img_data_fn_list):
            # fit2d logic later
            operation_list = zip(img_data_fn_list,
                                 int_data_fn_list_fit2d)
            # further determine y label
            unit = ('Q($\mathrm{\AA}$$^{-1}$)', 'I(Q), a.u.')
        else:
            # number of data are not the same, can't update
            print("INFO: the number of reduced data files found with "
                  "xpdView standard format {} is {}\n"
                  "INFO: the number of reduced data files found with "
                  "xpdView standard format {} is {}\n"
                  "None of them equal to the number of image data"
                  "files = {}"
                  .format('Q_<image_name>'+int_data_ext,
                          len(int_data_fn_list_Q),
                          '<image_name>'+int_data_ext,
                          len(int_data_fn_list_fit2d),
                          len(img_data_fn_list)
                          )
                  )
            print("INFO: Please make sure you follow standard workflow")
            print("INFO: only 2d image viewer will be updated")
            operation_list = img_data_fn_list
    if int_data_ext == '.gr':
            unit = ('r($\mathrm{\AA}$)',
                    'G($\mathrm{\AA}$$^{-2}$)')

    return (img_key_list, operation_list, unit)
