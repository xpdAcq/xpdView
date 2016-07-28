from tifffile import imread
import numpy as np
import sys
import multiprocessing

class analysis_concurrent:

    def __init__(self, x_start, x_stop, y_start, y_stop, selection):
        self.x_start = x_start
        self.x_stop = x_stop
        self.y_start = y_start
        self.y_stop = y_stop
        self.selection = selection
        self.label = ""
        assert self.selection is not None


    def get_img_array(self, filename):

        """
        :param filename: the name of the file or the path to the file if it is not in the same directory
        :type filename: str
        :return: the image data in an array
        """

        return imread(filename)


    # def get_grid_to_analyze(self, x_start, x_stop, y_start, y_stop, array):
    #
    #     """
    #     This function gets image data for later calculations
    #     :param x_start: the start position of the desired image data's x axis
    #     :param x_stop:  the stop position of the desired image data's x axis
    #     :param y_start: the start position of the desired image data's y axis
    #     :param y_stop: the stop position of the desired image data's y axis
    #     :param array: the array to be passed through
    #     :return: a subset of the original array to be analyzed
    #     """
    #     #pre checks on values
    #     assert x_start >= 0 and x_start < x_stop
    #     assert x_stop < len(array)
    #     assert y_start >= 0 and y_start < y_stop
    #     assert y_stop < len(array[0])
    #
    #     temp_arr=np.ndarray(shape=(x_stop-x_start, y_stop-y_start))
    #
    #     #loop that assigns values to the temporary array
    #     for i in range(x_start,x_stop):
    #         for j in range(y_start,y_stop):
    #             temp_arr[i-x_start][j-y_start] = array[i][j]
    #
    #     return temp_arr


    def get_avg_2d(self, arr):
        """
        This function calculates the average for values in a 2d array
        :param arr: the user selected array
        :return: the average for pixel values
        """
        sum = 0

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                sum += arr[i][j]

        return sum/float(arr.size)


    def get_avg_1d(self, arr):
        """
        this function calculates the average for a 1d array
        :param arr: the user selected array
        :return: the average for the 1d array
        """
        sum = 0
        for i in range(0,len(arr)):
            sum+=i

        return i/len(arr)


    def get_stdev(self, arr):

        """
        This function calculates the standard deviation for a 2d ndarray
        :param arr: the array to be passed through
        :return: the standard deviation of the array
        """
        #getting mean
        array_avg = self.get_avg_2d(arr)

        x = 0

        #list and loop to subtract mean from each val

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                x += (array_avg - arr[i][j])**2

        #returning sqrt of the subtracted and squared mean to get stdev
        return np.sqrt(x/arr.size)

    def get_min(self, arr):

        """
        this function gets the minimum value in the array
        :param arr: the array to be passed through
        :return: the minimum value
        """

        min_val = sys.maxsize

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                if arr[i][j] < min_val:
                    min_val = arr[i][j]

        return min_val

    def get_max(self, arr):
        """
            this function gets the max value in the array
            :param arr: the array to be passed through
            :return: the maximum value
            """

        max_val = -sys.maxsize

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                if arr[i][j] > max_val:
                    max_val = arr[i][j]

        return max_val

    def get_total_intensity(self, arr):
        total_intensity = 0
        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                total_intensity = arr[i][j]

        return total_intensity

    def x_and_y_vals(self, lock, queue, file_list):

        #x = range(0,len(self.file_list))
        y = []
        label = ""
        func = None

        if self.selection == "Standard Deviation":
            func= self.get_stdev
            self.label = "standard deviation"
        elif self.selection == "mean":
            func = self.get_avg_2d
            self.label = "mean"
        elif self.selection == "min":
            func = self.get_min
            self.label = "min"
        elif self.selection == "max":
            func = self.get_max
            self.label = "max"
        elif self.selection == "Total Intensity":
            func = self.get_total_intensity
            self.label = "Total Intensity"

        list_num = file_list.pop(0)
        y.append(list_num)
        for img in file_list:

            lock.acquire()
            print("file from list:" + str(list_num) + " analyzed")
            lock.release()
            #temp_arr = imread(img)

            y.append(func(img))

        queue.put_nowait(y)
        #queue.cancel_join_thread()
from tifffile import imread
import numpy as np
import sys
import multiprocessing

class analysis_concurrent:

    def __init__(self, x_start, x_stop, y_start, y_stop, selection):
        self.x_start = x_start
        self.x_stop = x_stop
        self.y_start = y_start
        self.y_stop = y_stop
        self.selection = selection
        self.label = ""
        assert self.selection is not None


    def get_img_array(self, filename):

        """
        :param filename: the name of the file or the path to the file if it is not in the same directory
        :type filename: str
        :return: the image data in an array
        """

        return imread(filename)


    # def get_grid_to_analyze(self, x_start, x_stop, y_start, y_stop, array):
    #
    #     """
    #     This function gets image data for later calculations
    #     :param x_start: the start position of the desired image data's x axis
    #     :param x_stop:  the stop position of the desired image data's x axis
    #     :param y_start: the start position of the desired image data's y axis
    #     :param y_stop: the stop position of the desired image data's y axis
    #     :param array: the array to be passed through
    #     :return: a subset of the original array to be analyzed
    #     """
    #     #pre checks on values
    #     assert x_start >= 0 and x_start < x_stop
    #     assert x_stop < len(array)
    #     assert y_start >= 0 and y_start < y_stop
    #     assert y_stop < len(array[0])
    #
    #     temp_arr=np.ndarray(shape=(x_stop-x_start, y_stop-y_start))
    #
    #     #loop that assigns values to the temporary array
    #     for i in range(x_start,x_stop):
    #         for j in range(y_start,y_stop):
    #             temp_arr[i-x_start][j-y_start] = array[i][j]
    #
    #     return temp_arr


    def get_avg_2d(self, arr):
        """
        This function calculates the average for values in a 2d array
        :param arr: the user selected array
        :return: the average for pixel values
        """
        sum = 0

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                sum += arr[i][j]

        return sum/float(arr.size)


    def get_avg_1d(self, arr):
        """
        this function calculates the average for a 1d array
        :param arr: the user selected array
        :return: the average for the 1d array
        """
        sum = 0
        for i in range(0,len(arr)):
            sum+=i

        return i/len(arr)


    def get_stdev(self, arr):

        """
        This function calculates the standard deviation for a 2d ndarray
        :param arr: the array to be passed through
        :return: the standard deviation of the array
        """
        #getting mean
        array_avg = self.get_avg_2d(arr)

        x = 0

        #list and loop to subtract mean from each val

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                x += (array_avg - arr[i][j])**2

        #returning sqrt of the subtracted and squared mean to get stdev
        return np.sqrt(x/arr.size)

    def get_min(self, arr):

        """
        this function gets the minimum value in the array
        :param arr: the array to be passed through
        :return: the minimum value
        """

        min_val = sys.maxsize

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                if arr[i][j] < min_val:
                    min_val = arr[i][j]

        return min_val

    def get_max(self, arr):
        """
            this function gets the max value in the array
            :param arr: the array to be passed through
            :return: the maximum value
            """

        max_val = -sys.maxsize

        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                if arr[i][j] > max_val:
                    max_val = arr[i][j]

        return max_val

    def get_total_intensity(self, arr):
        total_intensity = 0
        for i in range(self.y_start, self.y_stop):
            for j in range(self.x_start, self.x_stop):
                total_intensity = arr[i][j]

        return total_intensity

    def x_and_y_vals(self, file_list):

        #x = range(0,len(self.file_list))
        y = []
        label = ""
        func = None


        if self.selection == "Standard Deviation":
            func= self.get_stdev
            self.label = "Standard Deviation"
        elif self.selection == "mean":
            func = self.get_avg_2d
            self.label = "mean"
        elif self.selection == "min":
            func = self.get_min
            self.label = "min"
        elif self.selection == "max":
            func = self.get_max
            self.label = "max"
        elif  self.selection == "Total Intensity":
            func = self.get_total_intensity
            self.label = "Total Intensity"

        list_num = file_list.pop(0)
        # lock.acquire()
        print("process " + str(list_num) + " active")
        # lock.release()
        y.append(list_num)
        for img in file_list:

            # lock.acquire()
            # print("file from list:" + str(list_num) + " analyzed")
            # lock.release()
            #temp_arr = imread(img)

            y.append(func(img))

        #queue.put(y)
        # lock.acquire()
        print("process " + str(list_num) + " complete")
        return y
        # lock.release()