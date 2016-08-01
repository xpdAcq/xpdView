import numpy as np
import sys


"""This module has simple analysis functions
"""
def get_avg_2d(arr, x_start, x_stop, y_start, y_stop):
    """
    This function calculates the average for values in a 2d array
    :param arr: the user selected array
    :return: the average for pixel values
    """
    sum = 0

    for i in range(y_start, y_stop):
        for j in range(x_start, x_stop):
            sum += arr[i][j]
    return sum/float(arr.size)


def get_avg_1d(arr, x_start, x_stop, y_start, y_stop):
        
    """
    this function calculates the average for a 1d array
    :param arr: the user selected array
    :return: the average for the 1d array
    """
    sum = 0
    for i in range(0,len(arr)):
         sum+=i

    return i/len(arr)


def get_stdev(arr, x_start, x_stop, y_start, y_stop):

    """
    This function calculates the standard deviation for a 2d ndarray
    :param arr: the array to be passed through
    :return: the standard deviation of the array
    """
    #getting mean
    array_avg = get_avg_2d(arr, x_start, x_stop, y_start, y_stop)

    x = 0
    # list and loop to subtract mean from each val

    for i in range(y_start, y_stop):
        for j in range(x_start, x_stop):
            x += (array_avg - arr[i][j])**2

    #returning sqrt of the subtracted and squared mean to get stdev
    return np.sqrt(x/arr.size)

def get_min(arr, x_start, x_stop, y_start, y_stop):

    """
    this function gets the minimum value in the array
    :param arr: the array to be passed through
    :return: the minimum value
    """

    min_val = sys.maxsize

    for i in range(y_start, y_stop):
        for j in range(x_start, x_stop):
            if arr[i][j] < min_val:
                min_val = arr[i][j]

    return min_val


def get_max(arr, x_start, x_stop, y_start, y_stop):
    """
        this function gets the max value in the array
        :param arr: the array to be passed through
        :return: the maximum value
        """

    max_val = -sys.maxsize

    for i in range(y_start, y_stop):
        for j in range(x_start, x_stop):
            if arr[i][j] > max_val:
                max_val = arr[i][j]

    return max_val


def get_total_intensity(arr, x_start, x_stop, y_start, y_stop):
    total_intensity = 0
    for i in range(y_start, y_stop):
        for j in range(x_start, x_stop):
            total_intensity = arr[i][j]

    return total_intensity
