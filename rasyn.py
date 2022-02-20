

import json
import os

import asyn as ayn


with open("/content/web_mscra/main_config.json", "r") as f:
  st = json.load(f)

base_link = st["base_link"]
min_ = st["min_"]

s = base_link.replace(".html","")
home_link = s[:s.rfind('.')+s[s.rfind('.'):].find("/")]

print(st)
print(home_link)

ayn.main_func([base_link.format(i) for i in range(st["min_"],st["max_"])], "/content/tri", home_link)
