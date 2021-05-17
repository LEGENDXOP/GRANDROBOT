# MADE BY LEGENDX22
# COPY WITH CREDITS
from .import db
X = db["settings"]
def add_name(name):
  LEGENDX = {
    "_id": "LEGENDX22"
    }
  pro = X.find_one(LEGENDX)
  if pro:
    LEGEND = {"_id": "LEGENDX22"}, {"$set": {"username": name}}
    X.update_one(LEGEND)
  else:
    LEGENDXOP = {
      "_id": "LEGENDX22",
      "username": name
      }
    X.insert_one(LEGENDXOP)
def give_name():
  x = X.find_one({"_id": "LEGENDX22"})
  if x:
    return x["username"]
  else:
    return "LEGENDX22"
