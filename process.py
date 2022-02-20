
import json

with open("main_stuffed.json") as f:
  st  = json.load(f)

nst = {}

for k in st:
  nst[k.replace("raw_","")] = st[k]

with open("config.json", "w") as f:
  json.dump(nst, f)


