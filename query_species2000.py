# -*- coding: utf-8 -*-
# @Time : 2020/8/8 3:14
# @Author : Zhongyi Hua
# @FileName: query_species2000.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com

import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="HUA",
    password="Your password",
    database="species2019",
    charset="utf8")

cursor = conn.cursor(pymysql.cursors.DictCursor)


def query_species(query_name):
    name_list = query_name.split(' ')
    if len(name_list) == 2:
        genus, species = name_list
        sql = f'SELECT acceptedNameUsageID, scientificName FROM taxon WHERE genus="{genus}" AND specificEpithet="{species}"'
        try:
            cursor.execute(sql)
            cursor.fetchall()
        except:
            conn.rollback()
