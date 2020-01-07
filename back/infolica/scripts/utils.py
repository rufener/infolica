from datetime import time, date, datetime

class Utils():

    """ Serialize one query item"""
    @classmethod
    def serialize_one(cls, _query):
        d = _query.__dict__
        item = {}
        for n in d.keys():
            if n != '_sa_instance_state':
                if isinstance(d[n], (datetime, date)):
                    item[n] = d[n].isoformat()
                else:
                    item[n] = d[n]

        return item

    """ Serialize many query items"""
    @classmethod
    def serialize_many(cls, _query):
        master = []
        item = {}
        x = 0
        for u in _query:
            d = u.__dict__
            item = {}
            for n in d.keys():
                if n != '_sa_instance_state':
                    if isinstance(d[n], (datetime, date)):
                        item[n] = d[n].isoformat()
                    else:
                        item[n] = d[n]
            master.append(item)
        return master
