import json
import os

with open("data/countries.json") as f:
    countries = json.load(f)["countries"]

def rename_normal():
    shapefile_folder = os.path.join(os.curdir, "data/images")
    files = [f for f in os.listdir(shapefile_folder)]
    country_names = [country["name"].lower() for country in countries]
    for f in files:
        underscore = f.find("_")
        if f[:underscore].lower() in country_names:
            for c in countries:
                if c["name"].lower() == f[:underscore].lower():
                    a = 1
                    #os.rename("data/images/" + f, "data/images/" + c["alpha_3_code"] + f[underscore:])

def rename_single(old_name, new_name):
    shapefile_folder = os.path.join(os.curdir, "data/images")
    files = [f for f in os.listdir(shapefile_folder) if f[:f.find("_")] == old_name]

    for f in files:
        underscore = f.find("_")
        #os.rename("data/images/" + f, "data/images/" + new_name + f[underscore:])

shapefile_folder = os.path.join(os.curdir, "data/images")
#rename_single("ivory-coast", "CIV")
files = [f for f in os.listdir(shapefile_folder) if len(f[:f.find("_")]) > 3]
print(files)