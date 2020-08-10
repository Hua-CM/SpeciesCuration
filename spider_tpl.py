# -*- coding: utf-8 -*-
# @Time : 2020/8/8 3:14
# @Author : Zhongyi Hua
# @FileName: spider_tpl.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com

import requests
import re
import pandas as pd
from time import sleep
from pyquery import PyQuery as Pq


def get_html(url):
    my_header = {
        'User-Agent': r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"}
    return requests.get(url, headers=my_header).text


def spider_accepted_name(latin_name):
    species_url = 'http://www.theplantlist.org/tpl1.1/search?q=' + '+'.join(latin_name.split(' '))

    def query(query_url):
        sleep(0.2)
        page_text = Pq(get_html(query_url))
        if 'This name is the accepted name of a species in the genus' in page_text('p:eq(0)').text():
            return latin_name
        elif 'This name is a synonym of' in page_text('p:eq(0)').text():
            sci_name = re.search('This name is a synonym of (.*)', page_text('p:eq(0)').text()).group(1)
            return sci_name
        elif 'The results are below' in page_text('p:eq(0)').text():
            lv2_url = 'http://www.theplantlist.org' + page_text('table>tbody>tr:eq(0)>td:eq(0)>a').attr('href')
            sci_name = page_text('table>tbody>tr:eq(0)>td:eq(0)').text()
            if latin_name in sci_name:
                return query(lv2_url)
            else:
                return 'check tbl manually'
        else:
            return 'check NCBI'
    a = query(species_url)
    return a


def main(input_path, output_path):
    tb1 = pd.read_table(input_path, names=['raw_name'])
    tb1['fix_name'] = tb1['raw_name'].apply(spider_accepted_name)
    tb1.to_csv(output_path, sep='\t', index=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="This is the script for fix scientific name based on The plant list")
    parser.add_argument('-i', '--input', required=True,
                        help='<file_path> imput path')
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path> result path')
    args = parser.parse_args()
    main(args.input, args.output)
