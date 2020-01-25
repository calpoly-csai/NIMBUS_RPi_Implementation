import json
from Benchmark_Class import Benchmark

with open("init_bm_test.json", "r") as json_in:
    json_dat = json.load(json_in)
print(json_dat)

bm = Benchmark()

bm.load_json("init_bm_test.json")
bm.benchmark_init("Wake Word Prediction", "Laptop")

print(bm.parse_data())

bm.graph_data()
