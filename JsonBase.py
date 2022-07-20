#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://github.com/MSFPT/JsonBase

import json

class JsonBase():

  def __init__(self,file_db: str) :

    try: self.file = open(file_db,'r+')

    except FileNotFoundError as ferr : 
      
      with open(file_db,'w+')as f:f.close()

      self.file = open(file_db,'r+')

    except PermissionError as perr: quit(perr)

    if(self.file.name.split('.')[-1]!='json'):quit(f"[\aErrno 2] No such file or directory: '{str(self.file.name)}'")
    
    self.file_db = self.file.name
    
    self.file.close()

  def clear(self,backdata:str=''): self.write('')

  def write(self,data) :

    with open(self.file_db, 'w+') as f :
      
      f.write(json.dumps(data))
      
      f.close()
  
  def commit(self,data = None) :
    
    self.data = data if (data!=None) else self.data
    
    self.write(self.data)

  def get(self,fn = None) :
    
    with open(self.file_db, 'r+') as f :
    
      self.data=json.loads(f.read())
    
      try: fn(data=self.data)
    
      except: pass
    
      f.close()
    
    return(self.data)