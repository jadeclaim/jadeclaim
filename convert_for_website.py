import json

path1 = "./final_data.json"
data = json.load(open(path1, "r"))

# print(data)

sources = [[r["name"] for r in d] for d in data.values()]
sources_add = [[r["address"] for r in d] for d in data.values()]
s = []
for source in sources:
    s += source
sources = list(set(s))

s = []
for source in sources_add:
    s += source
sources_add = list(set(s))

table = dict(zip(sources, range(len(sources))))
table_add = dict(zip(sources_add, range(len(sources_add))))
for key, item in data.items():
    for r in item:
        r["name"] = table[r["name"]]
        r["address"] = table_add[r["address"]]

json.dump(
    {"names": table, "addresses": table_add, "data": data},
    open("./website_export.json", "w"),
)
