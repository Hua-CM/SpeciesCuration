# -*- coding: utf-8 -*-
# @Time : 2022/1/3 11:24
# @Author : Zhongyi Hua
# @FileName: query_common_name.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com

import xml.etree.ElementTree as ET
import asyncio
import argparse
import pandas as pd
from itertools import chain
from aiohttp import ClientSession, TCPConnector

URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


async def query_batch(_query_list, api_key, _step=10):

    async def _esearch_(_common, _session):
        url = URL + 'esearch.fcgi?db=taxonomy&term=' + _common + '&api_key=' + api_key
        async with _session.get(url) as response:
            _esearch_result = ET.fromstring(await response.text(encoding='UTF-8'))
            _id_list = [__.text for _ in _esearch_result if _.tag == 'IdList' for __ in _]
            return _id_list

    async def _esummary_(_id_list, _session):
        url = URL + 'esummary.fcgi?db=taxonomy&id=' + ','.join(_id_list) + '&api_key=' + api_key
        async with _session.get(url) as response:
            _esummary_result = ET.fromstring(await response.text(encoding='UTF-8'))
            _tmp_list = []
            for _item in _esummary_result:
                _tmp_dict = {_.attrib.get('Name'): _.text for _ in _item}
                _tmp_list.append({'common': _tmp_dict.get('CommonName'), 'scientific': _tmp_dict.get('ScientificName')})
            return _tmp_list

    async def wrapper(_query, _func, _session, recur=0):
        recur += 1
        # set retry times
        if recur > 3:
            print(_query, 'is wrong')
            return []
        try:
            return await _func(_query, _session)
        except:
            return await wrapper(_query, _func, session, recur)

    async with ClientSession(connector=TCPConnector(limit=10)) as session:
        esearch_results = []
        esummary_results = []
        print('esearch start')
        batch_list = [_query_list[i:i + _step] for i in range(0, len(_query_list), _step)]
        for per_batch in batch_list:
            tmp = await asyncio.gather(*[asyncio.create_task(wrapper(per_query, _esearch_, session)) for per_query in per_batch])
            esearch_results += chain(*tmp)
            await asyncio.sleep(1)
        esearch_results = [_ for _ in esearch_results if not _ == []]
        print('esearch done')
        if not esearch_results:
            return

        print('esummary start')
        _step = int(len(esearch_results) / 10)
        batch_list = [esearch_results[i:i + _step] for i in range(0, len(esearch_results), _step)]
        tmp = await asyncio.gather(*[asyncio.create_task(wrapper(per_query, _esummary_, session)) for per_query in batch_list])
        esummary_results += chain(*tmp)
        await asyncio.sleep(1) # control requests limit
        print('esummary done')
        return pd.DataFrame(esummary_results)


def parse_args():
    parser = argparse.ArgumentParser(description="Spider Chloroplast information from NCBI")
    parser.add_argument('-i', '--input', required=True,
                        help='<file_path>  File')
    parser.add_argument('-k', '--key', required=True,
                        help='<character>  API key')
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path>  Accession Number')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.input) as f:
        query_list = f.read().splitlines()
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(query_batch(query_list, args.key))
    results.to_csv(args.output, sep='\t', index=False)


if __name__ == '__main__':
    main()
