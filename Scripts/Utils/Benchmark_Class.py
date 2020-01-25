import time
import json
import matplotlib.pyplot as plt
import os
import numpy as np
'''
json => {
            {
                "process" : "ww pred",
                "device" : "RPi 4 4 GB",
                "time" : ["0.432", "0.425"],
                "timestamp" : Mar 19, 2019 | 14:32
            },

            ....
        }


'''

class Benchmark:
    def __init__(self):
        self.json_data = {}        
        self.json_filename = ""
        self.benchmark_lut = {}

    def store_json(self, filename):
        print(self.json_data)
        with open(filename, "w") as out_json:
            json.dump(self.json_data, out_json)

    def load_json(self, dir_path):
        print("loading")
        for in_file in os.listdir(os.path.join(os.getcwd(), "bm_data")):
            with open(in_file, "r") as in_json:
                self.json_data.update(json.load(in_json))

    def parse_data(self):
        parsed_data = {}

        for data in self.json_data:
            if parsed_data.get(self.json_data[data]["process"]) == None:

                parsed_data[self.json_data[data]["process"]] = {}
                parsed_data[self.json_data[data]["process"]][self.json_data[data]["device"]] = {"time":self.json_data[data]["time"], "avg":self.get_avgs(self.json_data[data]["time"])}

            else:
                if self.json_data[data]["device"] in parsed_data[self.json_data[data]["process"]]:

                    parsed_data[self.json_data[data]["process"]][self.json_data[data]["device"]]["time"] += self.json_data[data]["time"]
                    parsed_data[self.json_data[data]["process"]][self.json_data[data]["device"]]["avg"] = self.get_avgs(parsed_data[self.json_data[data]["process"]][self.json_data[data]["device"]]["time"])

                else:
                    
                    parsed_data[self.json_data[data]["process"]][self.json_data[data]["device"]] = {"time":self.json_data[data]["time"], "avg":self.get_avgs(self.json_data[data]["time"])}

        return parsed_data
 
    def benchmark_init(self, process, device):
        self.entity = Benchmark_Entity(process, device)
        self.benchmark_lut[process] = self.entity

    def benchmark_record_start(self, process):
        entity = self.benchmark_lut.get(process)
        entity.time_start = time.time()

    def benchmark_record_stop(self, process):
        entity = self.benchmark_lut.get(process)
        entity.time.append(time.time() - entity.time_start)
        self.data_dump(process)

    def data_dump(self, process):
        entity = self.benchmark_lut.get(process)
        json_template = {"process":process, "device":entity.device, "time":entity.time, "timestamp":entity.timestamp}
        self.json_data[entity.timestamp] = json_template

    def get_avgs(self, input_data):
        avg = 0
        for data in input_data:
            avg += data
        return avg / len(input_data)


    def graph_data(self):

        graph_data = self.parse_data()
        plt.rcdefaults()
        fig, ax = plt.subplots()
        fig_count = 1

        for process in graph_data:
            plt.figure(fig_count)
            devices = graph_data[process].keys()
            y_pos = np.arange(len(devices))
            avg_list, avg_list_label = self.pull_avgs(graph_data[process])
            ax.barh(y_pos, avg_list, align='center')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(devices)
            ax.invert_yaxis()
            ax.set_xlabel('Time (s)')
            ax.set_title(process)
            fig_count += 1

        plt.show()
    def pull_avgs(self, process):
        avg_list = []
        avg_list_label = []
        for device in process:
            avg_list_label.append([device])
            avg_list.append(process[device]['avg'])
        print(avg_list)
        return avg_list, avg_list_label

class Benchmark_Entity:
    def __init__(self, process, device):
        self.process = process
        self.device = device
        self.time = []
        self.timestamp = time.strftime("%m%d%Y%H%M%S")
        self.time_start = 0
