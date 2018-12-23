# -*- coding: utf-8 -*-
# Common package
import pymongo
import config


def mongo_conn():
    conn = pymongo.MongoClient(**config.MONGO)
    db = conn[config.MONGO_DB]
    return db
