#!/usr/bin/env python

import sys
import json

sys.path.insert(0, 'src') # add library code to path
from src.etl import get_data, extract_data, get_wiki_category_articles, remove_dir
from src.media_etl import get_media_data, process_media_data
from src.m_stat import get_m_stat_data, grab_m_stat_over_time

DATA_PARAMS = 'config/data-params.json'
MEDIA_DATA_PARAMS  = 'config/media-data-params.json'
MEDIA_PROCESS_PARAMS  = 'config/media-process-params.json'

def load_params(fp):
    with open(fp) as fh:
        param = json.load(fh)

    return param


def main(targets):

    # make the clean target
    if 'clean' in targets:
        remove_dir('data/raw')
        remove_dir('data/temp')
        remove_dir('data/out')
        remove_dir('data/out_m_stat')

    # make the data target
    if 'data' in targets:
        cfg = load_params(DATA_PARAMS)
        get_data(**cfg)

    # make the media data target
    if 'media-data' in targets:
        cfg = load_params(MEDIA_DATA_PARAMS)
        get_media_data(**cfg)

    # cleans and prepares the media data for analysis
    if 'process-media' in targets:
        cfg = load_params(PROCESS_MEDIA_PARAMS)
        process_media_data(**cfg)

    return


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
