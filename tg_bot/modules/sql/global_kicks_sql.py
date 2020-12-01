import threading

from sqlalchemy import Column, UnicodeText, Integer, String, Boolean

from tg_bot.modules.sql import BASE, SESSION

class GloballyKickedUsers(BASE):
    __tablename__ = "gkicks"
    user_id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    times = Column(Integer)
    
    def __init__(self, user_id, name, times):
        self.user_id = user_id
        self.name = name
        self.times = times
        
    def to_dict(self):
        return {"user_id": self.user_id,
                "name": self.name,
                "times": self.times}

GloballyKickedUsers.__table__.create(checkfirst=True)

def gkick_user(user_id, name, increment):
        user = SESSION.query(GloballyKickedUsers).get(user_id)
        if not user:
                user = GloballyKickedUsers(user_id, name, 0)
        user.name = name
        user.times += increment

        SESSION.merge(user)
        SESSION.commit()
        __load_gkick_userid_list()

def gkick_setvalue(user_id, name, value):
        user = SESSION.query(GloballyKickedUsers).get(user_id)
        if user:
            user.times = value
        if not user:
            user = GloballyKickedUsers(user_id, name, value)
        SESSION.merge(user)
        SESSION.commit()
        __load_gkick_userid_list()
      
def gkick_reset(user_id):
        user = SESSION.query(GloballyKickedUsers).get(user_id)
        if user:
            user.times = 0
            SESSION.delete(user)
        SESSION.commit()
        __load_gkick_userid_list()

def get_times(user_id):
        user = SESSION.query(GloballyKickedUsers).get(user_id)
        if not user:
                return 0
        return user.times

def __load_gkick_userid_list():
    global GKICK_LIST
    try:
        GKICK_LIST = {x.user_id for x in SESSION.query(GloballyKickedUsers).all()}
    finally:
        SESSION.close()
