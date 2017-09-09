"""module to provide file-based I/O function"""
import os
import numpy as np


def conf_label_size(ax, label_size):
    ax.xaxis.label.set_size(label_size)
    ax.yaxis.label.set_size(label_size)


def conf_tick_size(ax, tick_size):
    for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(tick_size)
    for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(tick_size)


def chi_read(fn, skiprows=4):
    """wrapper for reading .chi files

    Parameters
    ----------
    fn : str
        filename of .chi files
    skiprows : int, optional
        number of rows will be skipped.
        default to 4 for fit2d format

    Return
    ------
    array : ndarray
        n by 2 array. first row is data grid, second row is data values
    """
    try:
        array =np.loadtxt(fn)
    except:
        array = np.loadtxt(fn, skiprows=skiprows)
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
    unit = None # update later
    int_data_fn_list = None # update later
    sorted_fn_list = sorted(os.listdir(filepath))
    img_data_fn_list = [f for f in sorted_fn_list\
                        if os.path.splitext(f)[1] == img_data_ext]
    if not img_data_fn_list:
        print("INFO: can't find 2d image data with extension = {} "
              "in directory = {}".format(img_data_ext, filepath))
        return (None, None, None)

    img_key_list = list(map(lambda x: os.path.splitext(x)[0],
                            img_data_fn_list))
    if int_data_ext == '.gr':
        unit = ('r($\mathrm{\AA}$)',
                'G($\mathrm{\AA}$$^{-2}$)')
        gr_fn_list = []
        for fn in img_key_list:
            gr_fn = ''.join([fn, int_data_ext])
            if os.path.isfile(os.path.join(filepath, gr_fn)):
                gr_fn_list.append(gr_fn)
        # check if valid
        if len(gr_fn_list) == len(img_key_list):
            int_data_fn_list = gr_fn_list
    elif int_data_ext == '.chi':
        # construct valid chi file name assuming xpdAn/xpdAcq logic
        # Note: we only read "Q_" as prefix
        unit = ('Q(nm$^{-1}$)', 'I(Q), a.u.)') # flip if reads in fit2d
        Q_fn_list = []
        fit2d_fn_list = []
        for fn in img_key_list:
            Q_fn = ''.join([int_data_prefix, fn, int_data_ext])
            if os.path.isfile(os.path.join(filepath, Q_fn)):
                Q_fn_list.append(Q_fn)
            fit2d_fn = ''.join([fn, int_data_ext])
            if os.path.isfile(os.path.join(filepath, fit2d_fn)):
                fit2d_fn_list.append(fit2d_fn)
        # check if 1d data list is valid
        if not Q_fn_list and not fit2d_fn_list:
            # no 1d data, only update image
            print("INFO: can't find reduced data with extension = {} in "
                  "directory = {}".format(int_data_ext, filepath))
            print("INFO: only 2d image viewer will be updated")
            int_data_fn_list = None
        elif len(Q_fn_list) == len(img_data_fn_list):
            int_data_fn_list = Q_fn_list
        elif len(fit2d_fn_list) == len(img_data_fn_list):
            # further determine y label
            unit = ('Q($\mathrm{\AA}$$^{-1}$)', 'I(Q), a.u.')
            int_data_fn_list = fit2d_fn_list
        else:
            # number of data are not the same, can't update
            print("INFO: the number of reduced data files found with "
                  "xpdView standard format {} is {}\n"
                  "INFO: the number of reduced data files found with "
                  "xpdView standard format {} is {}\n"
                  "None of them equal to the number of image data"
                  "files = {}"
                  .format('Q_<image_name>'+int_data_ext,
                          len(Q_fn_list),
                          '<image_name>'+int_data_ext,
                          len(fit2d_fn_list),
                          len(img_data_fn_list)
                          )
                  )
            print("INFO: Please make sure you follow standard workflow")
            print("INFO: only 2d image viewer will be updated")

    if int_data_fn_list:
        operation_list = zip(img_data_fn_list, int_data_fn_list)
    else:
        operation_list = img_data_fn_list

    return (img_key_list, operation_list, unit)
