import os
import json

with open("../data/countries.json") as f:
    countries = json.load(f)["countries"]

image_folder = os.path.join(os.curdir, "../data/images")
files = [f for f in os.listdir(image_folder)]

country_list = []
counter_list = {}
last_code = ""
counter = 0
for f in files:
    code = f[:f.find("_")]
    if code in counter_list:
        counter_list[code] += 1
    else:
        counter_list[code] = 1
    if code == last_code:
        continue
    found = False
    for c in countries:
        if c["alpha_3_code"] == code:
            country_list.append(f"{c['name']},{c['alpha_2_code']},{c['alpha_3_code']}")
            found = True
    if not found:
        country_list.append(code)
    last_code = code

with open("../data/country_list.txt", "w") as cl:
    for c in country_list:
        cl.write(c)
        cl.write(" : " + str(counter_list[c.split(",")[-1]]))
        cl.write("\n")

with open("../data/country_list.txt") as cl:
    lines = cl.readlines()

lines = sorted(lines, key=lambda x : x.split(",")[0].lower())
with open("../data/country_list.txt", "w") as cl:
    cl.writelines(lines)