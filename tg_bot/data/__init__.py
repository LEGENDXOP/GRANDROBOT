# made by LEGENDX22 🔥
"""
COPY WITH CREDITS
MAKE SURE YOU HAVE THE LATEST VERSION OF Grand OFFICIAL
"""
from tg_bot import MONGO
import os
try:
  import pymongo, dnspython
except:
  os.system("pip install dnspython && pip install pymongo")
from pymongo import MongoClient as mg

X = mg(MONGO)

db = X["GRAND_OFFICIAL"]
