import matplotlib.pyplot as plt
from analysis_concurrent import analysis_concurrent
import time
import multiprocessing


class reducedRepPlot:

    def __init__(self, data_dict, key_list, x_start, x_stop, y_start, y_stop, selection):
        """
        constructor for reducedRepPlot object
        :param file_path: path to file directory
        :type file_path: str
        :param x_start: start val for x analysis
        :param x_stop: stop val for x analysis
        :param y_start:
        :param y_stop:
        """

        # self.tif_list = get_files(file_path)
        assert x_start >= 0 and x_start < x_stop
        assert x_stop <= 2048 #TODO change so resolution is flexible
        assert y_start >= 0 and y_start < y_stop
        assert y_stop <= 2048 #TODO change so resolution is flexible

        self.data_dict = data_dict
        self.key_list = key_list
        self.x_start = x_start
        self.x_stop = x_stop
        self.y_start = y_start
        self.y_stop = y_stop
        self.selection = selection

    def selectionSort(self, alist):
        for fillslot in range(len(alist) - 1, 0, -1):
            positionOfMax = 0
            for location in range(1, fillslot + 1):
                if alist[location][0] > alist[positionOfMax][0]:
                    positionOfMax = location

            temp = alist[fillslot]
            alist[fillslot] = alist[positionOfMax]
            alist[positionOfMax] = temp
        for arr in alist:
            arr.pop(0)
        return alist

    # def check_lists(self, list, nested_list, cpu_num):
    #     flattened_list = [val for sublist in nested_list for val in sublist]
    #     for i in range(0,cpu_num):
    #         flattened_list.remove(i)
    #
    #     print(flattened_list == list)

    def plot(self):
        """
        This function will plot analysis data as a function of the number of images. uses multiprocessing to speed
        things up
        :return: void
        """
        a = analysis_concurrent(self.y_start, self.y_stop, self.x_start, self.x_stop, self.selection)
        trunc_list = []
        cpu_count = multiprocessing.cpu_count()


        def callback(list):
            y.append(list)

        for i in range(0, cpu_count):
            temp_list = []
            if i == cpu_count-1:
                temp_key_list = self.key_list[(i * len(self.key_list) // cpu_count) : (((1 + i) * len(self.key_list) // cpu_count) +
                                                                                     (len(self.data_dict) % cpu_count))]
                for key in temp_key_list:
                    temp_list.append(self.data_dict[key])
                temp_list.insert(0, i)

            else:
                temp_key_list = self.key_list[(i * len(self.key_list) // cpu_count) : ((1 + i) * len(self.key_list) // cpu_count)]
                for key in temp_key_list:
                    temp_list.append(self.data_dict[key])
                temp_list.insert(0, i)
            trunc_list.append(temp_list)

       # print(self.check_lists(self.tif_list, trunc_list, cpu_count))

        process_list = []
        x = range(0, len(self.data_dict))
        y = []
        q = multiprocessing.Queue()
        p = multiprocessing.Pool(cpu_count)
        #a = multiprocessing.Array()
        #l = multiprocessing.Lock()
        #p = multiprocessing.Process(a.x_and_y_vals, args=(l,))


        # for i in range(0, cpu_count):
        #     process_list.append(multiprocessing.Process(target=a.x_and_y_vals, args=(l, q, trunc_list[i])))
        #
        start_time = time.clock()
        for list in trunc_list:
            p.apply_async(a.x_and_y_vals, args=(list,), callback=callback)
        # map = p.map_async(a.x_and_y_vals, trunc_list)
        # y = map.get()
        p.close()
        p.join()
        print(y)
        # for process in process_list:
        #     process.start()


        # for i in range(0, cpu_count):
        #     y.append(q.get())
        # for process in process_list:
        #     y.append(q.get())
        #     process.join()

        end_time = time.clock() - start_time
        print("time to analyze: " + str(end_time))

        # for i in range(0,cpu_count):
        #     y.append(q.get())

        y = self.selectionSort(y)
        print(y)
        flattened_y = [val for sublist in y for val in sublist]

        assert (len(flattened_y) == len(self.key_list))
        plt.scatter(x, flattened_y)

        plt.xlabel("file num")
        plt.ylabel(self.selection)

      #  plt.xscale()

        plt.show()
