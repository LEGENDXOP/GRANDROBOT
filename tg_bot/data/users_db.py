from .import X as mongo
data = mongo["USERS"]
def new_user(id):
  k = data.find_one({"_id": "LEGENDX22"})
  if k:
    data.update({"_id": "LEGENDX22"}, {"$push": {"user": id}})
  else:
    id_list = [id]
    data.insert_one({"_id": "LEGENDX22", "user": id_list})
def rem_user(id):
  data.update_one({"_id": "LEGENDX22"}, {"$pull": {"user": id}})
def all_users():
  pros = data.find_one({"_id": "LEGENDX22"})
  return list(pros["user"])
def already_user(id):
  k = data.find_one({"_id": "LEGENDX22"})
  if id in list(k["user"]):
    return True
  else:
    return False
