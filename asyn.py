



import asyncio
import aiohttp
import os

import time
import json

from bs4 import BeautifulSoup



def update_json(path, data):
  with open(path, "w+") as fm:
    p = json.load(fm)

    with open(path, "w") as fc:
      p.update(data)
      json.dump(p, fc)



async def get_urls(urls, log_name= "urls"):
  """
  urls -> list of links
  returns response, ok, content of urls.
  requests are sent asynchrously.
  """

  start = time.time()  

  async with aiohttp.ClientSession() as session:
    	   
    tasks = []
    for url in urls:
      tasks.append(asyncio.create_task(session.get(url, ssl=False)))

    responses = await asyncio.gather(*tasks)
      
    urls_result = {"res":responses,
                    "ok":[r.ok for r in responses],
                    "content":[await r.content.read() for r in responses]}

    end = time.time()
    total_time = end - start

    update_json(f"{log_name}_log.json",
                {"time":total_time, "lenght": len(urls)})

    # print("It took {} seconds to make {} calls".format(round(total_time, round_to),len(urls)))
    
    return urls_result



def find_imgs(cnt , base_link, ky = "src",img_args=[None,None,None]):
  """
  cnt -> html
  base_link -> is da base_link

  ky -> str, what is the key for src for imgs
  img args: strt, stp, stp -> int 

  finds all imgs in html
  returns list of links to imgs
  """
  start = time.time()  

  soup = BeautifulSoup(cnt, 'lxml')
  img_list = list(soup.findAll('img'))

  update_json("img_find_log.txt",
              {"img_list": img_list,
               "ky":ky,
               "img_args": img_args}
               )


  def im_clean(im_, ky_):
      try:
        si = im_[ky_]
        si.replace("\n","")
        si.replace("\t","")

        if "." not in si[:-7] and "/" == si[0]:
          si = base_link + si
        else:pass

        if "http" not in si:
          si = "http:" + si
        else:pass

        if "w3.org" not in si:
          pass
        else:
          raise Exception("error")

        return si

      except:
        raise Exception("error")


  imli = []
  errors_log = {"src invalid":{}}
  for sno,im in enumerate(img_list[img_args[0]:img_args[1]:img_args[2]]):
    try:

      si = im_clean(im, ky)
      imli.append(si)
        
    except:
      
      errors_log["src invalid"][sno] = ky
      update_json("img_find_log.json", errors_log)
            

      try:
      
        si = im_clean(im, "data-src")
        imli.append(si)

      except:
        update_json("img_find_log.json", {sno:[im, ky, type(im), im[ky]]})
        

  end = time.time()
  total_time = end - start

  update_json(f"img_find_log.json",
              {"time":total_time, "lenght": len(imli)})

  return imli



def main_func(urls, path, base_link, save_as = "pdf", ky = 'src', img_args =[None,None,None]):
  """
  urls -> list of urls
  path -> path to pdfs
  """


  start = time.time()  

  pg_d = asyncio.run(get_urls(urls, "1")) # pages to find the imgs
  all_imgs = [find_imgs(cnt, base_link,ky, img_args) for cnt in pg_d["content"]] # all image links in nested list


  for sno,imgs in enumerate(all_imgs, start = 1):
    

    print(f"getting ch {sno}")
    img_d = asyncio.run(get_urls(imgs, round_to,debug_ = debug__)) # dict of images, contains binary


    # print(f"making ch {sno}")
    # converr(img_d["content"],f"{path}/ch_{sno}", save_info[0], save_info[1],round_to)
    # print("------------------\n")


  end = time.time()
  total_time = end - start
  print("It took {} seconds to make {} chapters.".format(round(total_time, round_to),len(urls)))

  return "ho"


inp = input("url")
main_func([inp.format(i) for i in range(1,3)], "/content/tri", input("base link"))















