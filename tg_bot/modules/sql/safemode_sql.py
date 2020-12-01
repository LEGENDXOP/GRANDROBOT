import threading
from sqlalchemy import Column, String, Boolean
from tg_bot.modules.sql import SESSION, BASE

class Safemode(BASE):
    __tablename__="Safemode"
    chat_id = Column(String(14), primary_key=True)
    safemode_status = Column(Boolean, default=False)

    def __init__(self, chat_id, safemode_status=False):
        self.chat_id = str(chat_id) # ensure string
        self.safemode_status = safemode_status

Safemode.__table__.create(checkfirst=True)
SAFEMODE_INSERTION_LOCK = threading.RLock()

def set_safemode(chat_id, safemode_status=True):
    with SAFEMODE_INSERTION_LOCK:
        curr = SESSION.query(Safemode).get((str(chat_id)))
        if curr:
            SESSION.delete(curr)
        switch_status = Safemode(str(chat_id), safemode_status)

        SESSION.add(switch_status)
        SESSION.commit()

def is_safemoded(chat_id):
    try:
        return SESSION.query(Safemode).get((str(chat_id)))
    finally:
        SESSION.close()
