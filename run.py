#!/usr/bin/env python

import sys
import json

sys.path.insert(0, 'src') # add library code to path
from src.etl import get_data, process_data, extract_articles, remove_dir
from src.media_etl import get_media_data, process_media_data
from src.m_stat import get_m_stat_data, grab_m_stat_over_time

DATA_PARAMS = 'config/data-params.json'
MEDIA_DATA_PARAMS  = 'config/media-data-params.json'
MEDIA_PROCESS_PARAMS  = 'config/media-process-params.json'

PROCESS_PARAMS = 'config/process-params.json'
M_STAT_PARAMS = 'config/m-stat-params.json'
EXTRACT_PARAMS = 'config/extract-params.json'
OVER_TIME_DATA_PARAMS = 'config/over-time/data-params.json'
OVER_TIME_PROCESS_PARAMS = 'config/over-time/process-params.json'
OVER_TIME_M_STAT_PARAMS = 'config/over-time/m-stat-params.json'
TEST_DATA_PARAMS = 'config/test/data-params.json'
TEST_PROCESS_PARAMS = 'config/test/process-params.json'
TEST_M_STAT_PARAMS = 'config/test/m-stat-params.json'
LIGHT_DUMP_DATA_PARAMS = 'config/light-dump/data-params.json'
LIGHT_DUMP_EXTRACT_PARAMS = 'config/light-dump/extract-params.json'
LIGHT_DUMP_M_STAT_PARAMS = 'config/light-dump/m-stat-params.json'
LIGHT_DUMP_TIME_PARAMS = 'config/light-dump/over-time-m-stat-params.json'
DEEP_SEARCH_DATA_PARAMS = 'config/deep-search/data-params.json'
DEEP_SEARCH_PROCESS_PARAMS = 'config/deep-search/process-params.json'
DEEP_SEARCH_M_STAT_PARAMS = 'config/deep-search/m-stat-params.json'


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
        
    # make the test data target
    if 'test-data' in targets:
        cfg = load_params(TEST_DATA_PARAMS)
        get_data(**cfg)

    # cleans and prepares the data for analysis
    if 'process' in targets:
        cfg = load_params(PROCESS_PARAMS)
        process_data(**cfg)

    # cleans and prepares the test data for analysis
    if 'test-process' in targets:
        cfg = load_params(TEST_PROCESS_PARAMS)
        process_data(**cfg)

    # runs m-statistic on processed data
    if 'm-stat' in targets:
        cfg = load_params(M_STAT_PARAMS)
        get_m_stat_data(**cfg)

    # runs m-statistic on processed test data
    if 'test-m-stat' in targets:
        cfg = load_params(TEST_M_STAT_PARAMS)
        get_m_stat_data(**cfg)

    # m-statistic for entire light dump
    if 'light-dump' in targets:
        data_cfg = load_params(LIGHT_DUMP_DATA_PARAMS)
        extract_cfg = load_params(LIGHT_DUMP_EXTRACT_PARAMS)
        m_stat_cfg = load_params(LIGHT_DUMP_M_STAT_PARAMS)
        evolution_cfg = load_params(LIGHT_DUMP_TIME_PARAMS)

        get_data(**data_cfg)
        extract_article(**extract_cfg)
        get_m_stat_data(**m_stat_cfg)
        grab_m_stat_over_time(**evolution_cfg)

    # Searches through all thee files from Wikimedia starting with
    # enwiki-20200201-pages-meta-history1.xml
    if 'deep-search' in targets:
        for i in range(6):
            data_cfg =\
                load_params(DEEP_SEARCH_DATA_PARAMS
                            .replace('params', 'params-' + str(i + 1)))
            process_cfg =\
                load_params(DEEP_SEARCH_PROCESS_PARAMS
                            .replace('params', 'params-' + str(i + 1)))
            m_stat_cfg =\
                load_params(DEEP_SEARCH_M_STAT_PARAMS
                            .replace('params', 'params-' + str(i + 1)))

            get_data(**data_cfg)
            remove_dir('data/raw')
            process_data(**process_cfg)
            remove_dir('data/temp')
            get_m_stat_data(**m_stat_cfg)
            remove_dir('data/out')

    # Complete project for generating M-Statistic Evolution
    if 'm-stat-time' in targets:
        data_cfg = load_params(OVER_TIME_DATA_PARAMS)
        process_cfg = load_params(OVER_TIME_PROCESS_PARAMS)
        extract_cfg = load_params(EXTRACT_PARAMS)
        evolution_cfg = load_params(OVER_TIME_M_STAT_PARAMS)

        get_data(**data_cfg)
        process_data(**process_cfg)
        extract_article(**extract_cfg)
        grab_m_stat_over_time(**evolution_cfg)

    # Complete project for test set
    if 'test-project' in targets:
        data_cfg = load_params(TEST_DATA_PARAMS)
        process_cfg = load_params(TEST_PROCESS_PARAMS)
        m_stat_cfg = load_params(TEST_M_STAT_PARAMS)

        get_data(**data_cfg)
        process_data(**process_cfg)
        get_m_stat_data(**m_stat_cfg)

    return


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
