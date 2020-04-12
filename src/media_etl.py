import pandas as pd
import zipfile

def get_media_data(**cfg):
    for url in cfg['URLs']:
        print(url)
        infile = os.path.join(cfg['outpath'],url.split('/')[-1])
        os.system(cfg['wget_fmt']%(url,infile))
        print(infile)

    with zipfile.ZipFile(infile, 'r') as zip_ref:
        zip_ref.extractall(infile)
        
def process_media_data(**cfg):
    pass