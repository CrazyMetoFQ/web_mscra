



import asyncio
import aiohttp
import os

import time
import json
from shutil import rmtree

from bs4 import BeautifulSoup

import img2pdf



def daLeter(path):
  """
  makes path without error, deletes prev
  
  nice for formality of path check
  """

  if not os.path.isdir(path):
    os.mkdir(path)
  else:
    rmtree(path)
    os.mkdir(path)


def update_json(path, data):
  """
  updates a json file with info  
  """

  with open(path, "w+") as fm:
    if fm.read():
      p = json.load(fm)
    else:
      p = dict()

    with open(path, "w") as fc:
      p.update(data)
      json.dump(p, fc)



async def get_urls(urls, log_path= "urls.json"):
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

    update_json(log_path,
                {"time":total_time, "lenght": len(urls)})
    
    return urls_result



def find_imgs(cnt , base_link, log_path,ky = "src",img_args=[None,None,None]):
  """
  cnt -> html
  base_link -> is da base_link
  log_path -> path to log file with extension

  ky -> str, what is the key for src for imgs
  img args: strt, stp, stp -> int 

  finds all imgs in html
  returns list of links to imgs
  """
  start = time.time()  

  soup = BeautifulSoup(cnt, 'lxml')
  img_list = list(soup.findAll('img'))

  # updates da log
  update_json(log_path,
              {"img_list": str(img_list),
               "ky":ky,
               "img_args": img_args}
               ) 


  def im_clean(im_, ky_):
    """
    just a function to clean the urls
    """

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
      update_json(log_path, errors_log)
            

      try:
      
        si = im_clean(im, "data-src")
        imli.append(si)

      except:
        update_json(log_path, {sno:[im, ky, str(type(im)), im[ky]]})
        

  end = time.time()
  total_time = end - start

  update_json(log_path,
              {"time":total_time, "lenght": len(imli)})

  return imli



def converr(imgs, path, save_as = "pdf"):
  """
  imgs -> list of binary imgs
  path - > str of path to files
  save_as --> image or pdf 
  """
  start = time.time()  

  if save_as == "pdf":
    file_format = ".pdf"
  elif save_as == "img":
    file_format = ".jpg"
  else:
    raise Exception("Incorrect file type")

  # pdf
  if save_as == "pdf":
    with open(f"{path}{file_format}",'wb') as f:
      try:
        f.write(img2pdf.convert(imgs))
      
      except:
        raise Exception("eror") # got tp log this not raise later 

    end = time.time()
    total_time = end - start
    print("It took {} seconds to write a {} page pdf".format(total_time,len(imgs)))
  
  # Images
  elif save_as == "img":

    os.mkdir(path)

    for sno,img in enumerate(imgs):
      
      with open(f"{path}/img{sno}{file_format}",'wb') as f:
        try:
          f.write(img)
        
        except Exception() as e:
          print(e)

    end = time.time()
    total_time = end - start
    print("It took {} seconds to write {} images".format(total_time,len(imgs)))




def main_func(urls, path, base_link, save_as = "pdf", ky = 'src', img_args =[None,None,None]):
  """
  urls -> list of urls
  path -> path to pdfs
  """


  start = time.time()

  log_path = "/content/logs"
  daLeter(log_path) # creates dir for all the logs
  daLeter(f"{log_path}/find_imgs") # creates log dir for the image finder
  daLeter(f"{log_path}/converter") # creates log dir for the converter
  daLeter(f"{log_path}/pages") # creates log dir for the chapters
  daLeter(f"{log_path}/creation") # creates log dir for the current going
  
  pg_d = asyncio.run(get_urls(urls, f"{log_path}/intial get.json")) # pages to find the imgs
  all_imgs = [find_imgs(cnt, base_link, f"{log_path}/find_imgs/page_{sno}.json",ky, img_args) for sno,cnt in enumerate(pg_d["content"])] # all image links in nested list

  # want to make this async
  def supa_main(sno_, imgs_):
    """
    the main worker
    """
    update_json(f"{log_path}/creation/getting.json", {"current":sno_})
    img_d = asyncio.run(get_urls(imgs_, f"{log_path}/pages/page {sno_}.json")) # dict of images, contains binary

    update_json(f"{log_path}/creation/making.json", {"current":sno_})
    converr(img_d["content"],f"{path}/ch_{sno_}", save_as)
  
  for sno,imgs in enumerate(all_imgs, start = 1):
    supa_main(sno,imgs)
    
      



  end = time.time()
  total_time = end - start


  update_json(f"{log_path}/main.json",
            {"time":total_time, "lenght": len(urls)})

  return "ho"
