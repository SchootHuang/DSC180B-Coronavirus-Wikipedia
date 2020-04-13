from keras.utils import get_file
from zipfile import ZipFile, BadZipfile
from lxml import etree
from py7zr import unpack_7zarchive
from bs4 import BeautifulSoup
import dill as pickle
import wikipediaapi
import shutil
import os
import pandas as pd
import requests
import subprocess

# Paths are as follows
# i.e. Page: page_id, page_title
#       -> Revision: 'rev_id', 'parent_id', 'timestamp',
#                     'comment' ,'model', 'format',
#                     'edit', 'sha1'}
#           -> Contributor: 'username', 'user_id', 'user_ip'
xpath_dict = {'page': 'ns:page',
              'page_id': 'ns:id',
              'page_title': 'ns:title',
              'revision': 'ns:revision',
              'rev_id': 'ns:id',
              'parent_id': 'ns:parentid',
              'timestamp': 'ns:timestamp',
              'model': 'ns:model',
              'format': 'ns:format',
              'edit': 'ns:text',
              'comment': 'ns:comment',
              'contributor': 'ns:contributor',
              'username': 'ns:username',
              'user_id': 'ns:id',
              'user_ip': 'ns:ip',
              }

page_level_tags = {'page_id', 'page_title'}
rev_level_tags = {'rev_id', 'parent_id', 'timestamp', 'comment', 'model',
                  'format', 'edit', 'sha1'}
contr_level_tags = {'username', 'user_id', 'user_ip'}

nsmap = {'ns': 'http://www.mediawiki.org/xml/export-0.10/'}


# ---------------------------------------------------------------------
# Helper Functions for Getting Data
# ---------------------------------------------------------------------
def context_to_pkl(context, out_spec_dir, tags, article_set):
    """
    Converts the XML Tree context to some text format
    Either csv or light format
    :param context: XML iterable context for streaming
    :param out_dir: Output directory
    :param tags: Tags used for csv format
    :param article_set: Set of article titles
    """

    # loop through the large XML tree (streaming)
    for event, elem in context:
        curr_title = get_tag_if_exists(elem, 'page_title')
        if curr_title in article_set:
            pkl_tree(root=elem, out_spec_dir=out_spec_dir, tags=tags)

        # release unneeded XML from memory
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    del context


def pkl_tree(root, out_spec_dir, tags):
    """
    Pickles tree to csv file
    :param root: Root node of tree
    :param out_dir: Data directory for output
    :param tags: Tags used for output
    :return:
    """
    curr_title = get_tag_if_exists(root, 'page_title')
    print('Beginning conversion of {}'.format(curr_title))

    df = convert_tree_to_df(root=root, tags=tags)
    print('Converted to {}'.format(curr_title))
    save_pkl(df, '{}{}.pkl'.format(out_spec_dir, curr_title))
    del root, df


def get_tag_if_exists(parent, tag):
    """
    Checks if tag is a child of the parent in the XML tree
    If so, gets the Wikipedia tag format
    :param parent: Parent node in XML tree
    :param tag: Desired child tag
    :return: Text within the XML tag OR None
    """
    res = parent.find(xpath_dict[tag], namespaces=nsmap)
    try:
        return res.text
    except:
        # When tag is not child of parent and res = None
        return res


def convert_tree_to_df(root, tags):
    """
    Converts the XML tree to a dataframe with each tag as a column
    :param root: Root of current XML tree
    :param tags: Desired tags
    :return: Dataframe
    """
    # Initializes tags for different levels within the xml format
    curr_page_level_tags = list(tags.intersection(page_level_tags))
    curr_rev_level_tags = list(tags.intersection(rev_level_tags))
    curr_contr_level_tags = list(tags.intersection(contr_level_tags))
    curr_tags = [curr_page_level_tags, curr_rev_level_tags,
                 curr_contr_level_tags]
    # Column order for output
    cols = [tag for tag_level in curr_tags for tag in tag_level]
    # Temporary matrix before dataframe
    df_lists = []

    for page_el in root.iterfind(xpath_dict['page'], namespaces=nsmap):
        curr_row = {}
        # Gets all Page level tags
        for page_tag in curr_tags[0]:
            curr_row[page_tag] = get_tag_if_exists(page_el, page_tag)
        for rev_el in page_el.iterfind(xpath_dict['revision'],
                                       namespaces=nsmap):
            # Gets all Revision level tags
            for rev_tag in curr_tags[1]:
                curr_row[rev_tag] = get_tag_if_exists(rev_el, rev_tag)
            contr_el = rev_el.find(xpath_dict['contributor'], namespaces=nsmap)
            # Gets all contributor level tags
            for contr_tag in curr_tags[2]:
                curr_row[contr_tag] = get_tag_if_exists(contr_el, contr_tag)
            df_lists.append(list(curr_row.values()))
    df = pd.DataFrame(df_lists, columns=cols)
    del df_lists
    if 'timestamp' in cols:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    return df


def unpack_zip(raw_dir, temp_dir, fp_zip):
    """
    Unpacks a zip file
    Supports .7z and .zip
    :param raw_dir: Directory for raw data containing zipped file
    :param temp_dir: Directory for temporary data for unzipped file
    :param fp_zip: File path of zipped file
    :return: file path of unzipped file
    """
    # Unzips the current file
    if fp_zip.split('.')[-1] == '7z':
        # Registers format to .7zip
        try:
            shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)
            print('.7z registered for "7zip"')
        except:
            print('.7z is already registered for "7zip"')
        shutil.unpack_archive(raw_dir + fp_zip, temp_dir)
    else:
        try:
            ZipFile(raw_dir + fp_zip).extractall(path=temp_dir)
        except BadZipfile:
            print('File already unpacked')
            shutil.copy(raw_dir + fp_zip, temp_dir + fp_zip)
            fp_unzip = fp_zip
            print('Unzipped file path:', temp_dir + fp_unzip)
            return fp_unzip

    print('Unzipped', raw_dir + fp_zip, 'to', temp_dir)

    fp_unzip = max([temp_dir + file for file in os.listdir(temp_dir)],
                   key = os.path.getctime)

    print('Unzipped file path:', fp_unzip)
    return fp_unzip[len(temp_dir):]


def unzip_to_pkl(data_dir, fp_unzip, tags, article_set, file_type):
    """
    Unzips file to desired output format
    Currently supports only csv or light dump format
    :param data_dir: Directory for all data
    :param fp_unzip: File path of unzipped file
    :param tags: Desired tags for csv format
    :param article_set: Set of article titles
    :param file_type: Either pageview or edit-history
    """
    temp_dir = '{}temp/'.format(data_dir)
    out_spec_dir = '{}out/{}/'.format(data_dir, file_type)

    context = etree.iterparse(temp_dir + fp_unzip,
                              tag='{http://www.mediawiki.org/' +\
                                  'xml/export-0.10/}page',
                              encoding='utf-8', huge_tree=True)
    print('Converting to pickle')
    context_to_pkl(context=context, out_spec_dir=out_spec_dir, tags=tags,
                   article_set=article_set)

    # Delete etree
    del context
    print('Done with ' + temp_dir + fp_unzip)


def scrape_files(base_url, scrape_file_desc, scrape_file_ext, raw_dir,
                 temp_dir, skip_unzip):
    """
    Scrapes files from a base url with a specific file extension and file path
    :param base_url: Base URL where files lie in
    :param scrape_file_desc: Description required to be a part of the file
    :param scrape_file_ext: Extension of file
    :param raw_dir: Directory for raw files to be saved to
    :param temp_dir: Temporary directory for unzipped files
    :param skip_unzip: 2 to skip unzip, else do unzip
    :return: File paths of unzipped files
    """
    print('Scraping files from one main URL, so starting download now')
    print('Starting with URL:', base_url)
    index = requests.get(base_url).text
    soup_index = BeautifulSoup(index, 'html.parser')
    file_dumps = [a for a in soup_index.find_all('a')
                  if a.has_attr('href')
                  and scrape_file_desc in a['href']
                  and scrape_file_ext == a['href'][-3:]]
    fp_unzips = []
    for dump in file_dumps:
        print('Starting with dump:', dump.text)
        fp_zip = get_file(dump.text, base_url + dump.text,
                          cache_dir='.', cache_subdir=raw_dir)
        print('Done with dump:', dump.text)

        if skip_unzip != 2:
            print('Now unpacking/unzipping dump.')
            fp_unzip = unpack_zip(raw_dir=raw_dir, temp_dir=temp_dir,
                                fp_zip=fp_zip)
            fp_unzips.append(fp_unzip)
            print('Done unzipping.')
    return fp_unzips


def get_categorymembers(categorymembers, out_fh, article_set,
                        level=0, max_level=1000):
    """
    Gets all the articles in a Wikipedia category
    :param categorymembers: Wikipedia category members
    :param out_fh: File handler for output
    :param article_set: Set of articles
    :param level: Current level in the category search
    :param max_level: Deepest level to go to
    :return:
    """
    for c in categorymembers.values():
        # print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
        curr_title = c.title.replace(" ", "_")
        if curr_title not in article_set:
            article_set.add(curr_title)
            # Stores article title
            if c.ns == wikipediaapi.Namespace.MAIN:
                out_fh.write("%s\n" % curr_title)
            # Recursively gets the pages under a category
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                get_categorymembers(c.categorymembers, out_fh, article_set,
                                    level=level + 1, max_level=max_level)


def get_pageview_articles(raw_dir, out_spec_dir, fp_zip, domain_set,
                          article_set):
    """
    Extracts all the desired articles from a pageviews zip file
    :param fp_zip: File path for zipped file
    :param domain_set: Set of domains to extract
    :param article_set: Set of articles to look at
    :return:
    """
    fp_unzip = fp_zip.replace('.gz', '.csv')
    fh_unzip = open(out_spec_dir + fp_unzip, 'w+')
    fh_unzip.write('Domain_Code,Title,Count_Pageviews\n')
    # Iterate through compressed file one line at a time
    for line in subprocess.Popen(['gunzip'],
                                 stdin=open(raw_dir + fp_zip),
                                 stdout=subprocess.PIPE).stdout:
        curr_arr = line.decode('UTF-8').split()
        curr_domain = curr_arr[0]
        curr_title = curr_arr[1]
        curr_views = curr_arr[2]
        if curr_domain in domain_set and curr_title in article_set:
            fh_unzip.write('{},{},{}\n'.format(curr_domain, curr_title,
                                               curr_views))


def remove_dir(dir_to_remove):
    """
    Removes directory
    :param dir_to_remove: Directory to remove
    """
    shutil.rmtree(dir_to_remove, ignore_errors=True)


def get_basic_data_dirs(data_dir='data/',
                        child_dirs=('', 'out/', 'temp/', 'raw/')):
    """
    Adds desired sub-directories to parent data directory
    :param data_dir: Directory for data
    :param child_dirs: Sub-directories for where data actually exists within
    """
    for child_dir in child_dirs:
        if not os.path.exists(data_dir + child_dir):
            os.makedirs(data_dir + child_dir)


def save_pkl(fp, obj):
    """Saves an object to pickle file."""
    with open(fp, "wb") as fh:
        pickle.dump(obj, fh)


# ---------------------------------------------------------------------
# Driver Function for EXTRACTING AND UNZIPPING COMPRESSED DATA/URLS
# ---------------------------------------------------------------------

def get_data(
        data_dir='data/',
        fps=(
            'https://dumps.wikimedia.org/enwiki/20200101/' +
            'enwiki-20200101-pages-meta-history1.xml-p10p1036.7z',
            'https://dumps.wikimedia.org/enwiki/20200101/' +
            'enwiki-20200101-pages-meta-history1.xml-p1037p2031.7z'
        ),
        fp_type=0, unzip_type=0, scrape_file_ext='.7z',
        scrape_file_desc='pages-meta-history'
):
    """
    Gets the data from either a url or some file destination and unzips
    the file. If file is passed in, function will copy the file over to the
    raw data directory within the directory containing data
    :param data_dir: Directory for data
    :param fps: Filepaths/URLs for downloading and unzipping
    :param fp_type: 0 for URL, 1 for actual file, 2 for scraping URL
    :param unzip_type: Whether to unzip and what the unzipped file is
                       (i.e. light dump format)
                       0 for XML format -> redirect to temp directory
                       1 for light dump format -> directly to output directory
                       2 for keeping zipped file -> ignore and keep zip in raw
    :param scrape_file_ext: Extension of files to scrap
    :param scrape_file_desc: Description required to be a part of the file
    :return: None
    """

    child_dirs = ['', 'out/', 'temp/', 'raw/']
    get_basic_data_dirs(data_dir, child_dirs)
    raw_dir = data_dir + 'raw/'
    temp_dir = data_dir + 'temp/'
    out_dir = data_dir + 'out/'

    print('Directories are made/were made')

    fp_unzips = []
    for curr_fp in fps:
        if fp_type == 0:
            print('Using urls for files, so going to download them now')
            print('Starting fp:', curr_fp)
            print('Downloading zip from url')
            zip_fp = curr_fp.split('/')[-1]
            curr_fp = get_file(zip_fp, curr_fp, cache_dir='.',
                               cache_subdir=raw_dir)
            print('Done downloading zip.')
        elif fp_type == 1:
            print('File already downloaded : - )')
            # Copies file to raw directory if not there yet
            if curr_fp not in os.listdir(raw_dir):
                if curr_fp in os.listdir(data_dir):
                    shutil.copyfile(data_dir + curr_fp,
                                    raw_dir + curr_fp.split('/')[-1])
                else:
                    shutil.copyfile(curr_fp,
                                    raw_dir + curr_fp.split('/')[-1])
                    curr_fp = curr_fp.split('/')[-1]
        elif fp_type == 2:
            fp_unzips.extend(
                scrape_files(curr_fp, scrape_file_desc, scrape_file_ext,
                             raw_dir, temp_dir, unzip_type))
            continue
        print('Now unpacking/unzipping zip.')
        # Directs unzip file to desired sub-directory
        if unzip_type == 0:
            fp_unzip = unpack_zip(raw_dir=raw_dir, temp_dir=temp_dir,
                                  fp_zip=curr_fp)
        elif unzip_type == 1:
            fp_unzip = unpack_zip(raw_dir=raw_dir, temp_dir=out_dir,
                                  fp_zip=curr_fp)
        else:
            print('Skipping unzip.')
            continue
        fp_unzips.append(fp_unzip)
        print('Done unzipping.')
    print('Done. The unzipped files are:', fp_unzips)
    return


# ---------------------------------------------------------------------
# Driver Function for EXTRACTING DESIRED ARTICLES
# ---------------------------------------------------------------------

def extract_data(
        data_dir='data/',
        fps=(
            'enwiki-20200401-pages-meta-history1.xml-p1p908.7z',
        ),
        article_list_fps=(
                '2019–20_coronavirus_pandemic_articles.csv',
        ),
        file_type='edit-history', domain_list=('en', 'en.m'),
        delete_unzipped=0, delete_zipped=0,
        tags=('page_title', 'timestamp', 'username', 'user_ip', 'edit'),
):
    """
    Processes the XML file into more readable formats
    Output formats possible are light dump format or csv format
    :param data_dir: Directory for data
    :param fps: List of file paths for zipped files
    :param article_list_fps: List of file paths for article lists
    :param file_type: 'edit-history' or 'pageviews'
    :param domain_list: List of Wikipedia domains
    :param delete_unzipped: 1 to delete unzipped file, 0 to keep
    :param delete_zipped: 1 to delete zipped file, 0 to keep
    :param tags: Tags to keep for output
    """

    if not isinstance(tags, set):
        try:
            tags = set(tags)
        except TypeError:
            print("Tags needs to be a iterable, like the default:" +
                  "{'page_title', 'timestamp', 'username', 'user_ip'}." +
                  "Try again")

    raw_dir = data_dir + 'raw/'
    temp_dir = data_dir + 'temp/'
    out_dir = data_dir + 'out/'
    out_spec_dir = '{}{}/'.format(out_dir, file_type)
    if not os.path.exists(out_spec_dir):
        os.makedirs(out_spec_dir)

    article_set = set()
    for article_list_fp in article_list_fps:
        curr_article_df = pd.read_csv(out_dir + article_list_fp, sep='\\')
        article_set = article_set.union(curr_article_df['Title'])

    domain_set = set(domain_list)
    for fp_zip in fps:
        print('Starting with {}'.format(fp_zip))
        if file_type == 'edit-history':
            fp_unzip = unpack_zip(raw_dir=raw_dir, temp_dir=temp_dir,
                                  fp_zip=fp_zip)
            unzip_to_pkl(data_dir=data_dir, fp_unzip=fp_unzip, tags=tags,
                         article_set=article_set, file_type=file_type)
            if delete_unzipped:
                os.remove(fp_unzip)
        elif file_type == 'pageview':
            get_pageview_articles(raw_dir=raw_dir,
                                  out_spec_dir=out_spec_dir,
                                  fp_zip=fp_zip,
                                  domain_set=domain_set,
                                  article_set=article_set)
        else:
            print("Unknown file type. We only taking 'edit-history' or" +
                  "'pageview'. Try again xd.")

        if delete_zipped:
            os.remove(fp_zip)


# ---------------------------------------------------------------------
# Driver Function for GRABBING WIKIPEDIA ARTICLES FOR CATEGORY
# ---------------------------------------------------------------------

def get_wiki_category_articles(
        data_dir='data/',
        category='2019–20_coronavirus_pandemic',
        language='en', max_level=1000
):
    """
    Extracts a desired files from Wikipedia url
    :param data_dir: Directory for data
    :param category: Category to grab articles from
    :param language: Language in question
    :param max_level: Deepest level to go in search of category's articles
    """

    out_dir = '{}out/'.format(data_dir)
    out_fp = out_dir + category + '_articles.csv'
    wiki_wiki = wikipediaapi.Wikipedia(
        language=language,
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    cat_page = wiki_wiki.page('Category:' + category)
    out_fh = open(out_fp, 'w+')
    out_fh.write('Title\n')
    article_set = set()
    get_categorymembers(categorymembers=cat_page.categorymembers,
                        out_fh=out_fh, article_set=article_set,
                        level=0, max_level=max_level)
