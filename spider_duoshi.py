# -*- coding: utf-8 -*-
# @Time : 2020/8/8 1:14
# @Author : Zhongyi Hua
# @FileName: spider_duoshi.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com

import requests
from urllib.request import quote
import re
import pandas as pd
from pyquery import PyQuery as Pq


def get_html(url):
    my_header = {
        'User-Agent': r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"}
    return requests.get(url, headers=my_header).text


def spider_family():
    apg4_url = 'http://duocet.ibiodiversity.net/index.php?title=APG_IV%E7%B3%BB%E7%BB%9F'
    gym_url = 'http://duocet.ibiodiversity.net/index.php?title=%E5%A4%9A%E8%AF%86%E8%A3%B8%E5%AD%90%E6%A4%8D%E7%89%A9%E7%B3%BB%E7%BB%9F'
    ppg1_url = 'http://duocet.ibiodiversity.net/index.php?title=PPG_I%E7%B3%BB%E7%BB%9F'
    bry_url = 'http://duocet.ibiodiversity.net/index.php?title=%E5%A4%9A%E8%AF%86%E8%8B%94%E8%97%93%E7%B3%BB%E7%BB%9F'
    tmp_list = []

    def spider_apg():
        page = Pq(get_html(apg4_url))
        tmp_dict = {}
        for idx, _ in enumerate(page('ol li ol li').items()):
            tmp_dict[idx] = {'ch_family': re.search('(.*)\u3000(.*?)\u0020', _.text()).group(1),
                             'family': re.search('(.*)\u3000(.*?)\u0020', _.text()).group(2)}
        return pd.DataFrame.from_dict(tmp_dict, 'index')

    def spider_gym():
        page = Pq(get_html(gym_url))
        tmp_dict = {}
        for idx, _ in enumerate(page('ol li ol li ol li').items()):
            tmp_dict[idx] = {'ch_family': re.search('(.*)\u3000(.*?)\u0020', _.text()).group(1),
                             'family': re.search('(.*)\u3000(.*?)\u0020', _.text()).group(2)}
        return pd.DataFrame.from_dict(tmp_dict, 'index')

    def spider_ppg():
        page = Pq(get_html(ppg1_url))
        tmp_dict = {}
        for idx, _ in enumerate(page('ol li ol li ol li').items()):
            tmp_dict[idx] = {'ch_family': _('a:eq(0)').text(),
                             'family': _('font').text()}
        tmp_df = pd.DataFrame.from_dict(tmp_dict, 'index')
        tmp_df.drop(tmp_df[tmp_df['ch_family'].str.contains('亚目')].index, inplace=True)
        return tmp_df

    def spider_bry():
        page = Pq(get_html(bry_url))
        tmp_dict = {}
        for idx, _ in enumerate(page('dl dd dl dd dl dd dl dd').items()):
            tmp_dict[idx] = {'ch_family': _('a:eq(0)').text(),
                             'family': _('font').text()}
        tmp_df = pd.DataFrame.from_dict(tmp_dict, 'index')
        tmp_df.drop(tmp_df[tmp_df['ch_family'].str.contains('亚目')].index, inplace=True)
        return tmp_df

    for func in [spider_apg, spider_gym, spider_ppg, spider_bry]:
        tmp_list.append(func())
    result_df = pd.concat(tmp_list)
    result_df.reset_index(inplace=True, drop=True)
    return result_df


def spider_genus(_family):
    _url = 'http://duocet.ibiodiversity.net/index.php?title=' + _family
    _url = quote(_url, safe=";/?:@&=+$,", encoding="utf-8")
    page = Pq(get_html(_url))
    genus_list = []
    for _ in page('ul i').items():
        genus_list.append(_.text())
    return genus_list


def main():
    family_df = spider_family()
    genus_df_list = []
    for idx, row in family_df.iterrows():
        tmp_df = pd.DataFrame(spider_genus(row['ch_family']), columns=['genus'])
        tmp_df['ch_family'] = row['ch_family']
        genus_df_list.append(tmp_df)
    genus_df = pd.concat(genus_df_list)
    genus_df = genus_df.merge(family_df, how='left')
    genus_df.drop(columns=['ch_family'], inplace=True)
    return genus_df


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="This is the script for spidering accepted genus name from \
                                                  duocet(多识百科).")
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path> result path')
    args = parser.parse_args()
    genus_result = main()
    genus_result.to_csv(args.output)
