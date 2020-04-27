import pandas as pd
import plotly.graph_objects as go


class Article:
    def __init__(self, title, parent=None):
        self.title = title
        self.parent = parent
        self.children = {}

    def add_child(self, node):
        self.children[node.title] = node

    def get_title(self):
        return self.title

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children


def assign_node(row, root, node_map):
    """

    :param row:
    :param root:
    :param node_map:
    :return:
    """
    if not row['Level']:
        node = Article(row['Title'])
        root.add_child(node)
    else:
        prev_node = node_map[row['Previous_Article']]
        node = Article(row['Title'], prev_node)
        prev_node.add_child(node)
    node_map[row['Title']] = node
    return


def build_graph(covid_df):
    root = Article(title='root')
    node_map = {}
    covid_df.apply(assign_node, axis=1, args=(root, node_map))
    rev_index_map = covid_df['Title'].to_dict()
    index_map = {v: k for k, v in rev_index_map.items()}

    return root, node_map, index_map, rev_index_map


def sum_pageviews(root, pageviews_map, prev_list):
    if root.get_title() not in pageviews_map:
        pageviews_map[root.get_title()] = 0
    if not root.get_children():
        for node in prev_list:
            if node.get_title() not in pageviews_map:
                pageviews_map[node.get_title()] = 0
            pageviews_map[node.get_title()] += pageviews_map[root.get_title()]
    for _, child in root.get_children().items():
        sum_pageviews(child, pageviews_map, prev_list + [root])


def sankey(root, node_map, index_map, rev_index_map, pageview_df, datetime):
    """
    Adapted from https://medium.com/kenlok/e221c1b4d6b0

    :param root:
    :param node_map:
    :param index_map:
    :param pageview_df:
    :param color_palette:
    :return:
    """
    pageviews_map = pageview_df['Count_Pageviews'].to_dict()
    prev_list = []
    for _, child in root.get_children().items():
        sum_pageviews(child, pageviews_map, prev_list)

    label_list = [rev_index_map[i] for i in range(len(rev_index_map))]
    source_list = [index_map[node_map[title].get_parent().get_title()]
                   if node_map[title].get_parent()
                   else index_map[node_map[title].get_title()]
                   for title in label_list]
    target_list = [index_map[list(node_map[title].get_children()
                                  .values())[0].get_title()]
                   if node_map[title].get_children()
                   else index_map[node_map[title].get_title()]
                   for title in label_list]
    value_list = [pageviews_map[title] for title in label_list]

    date, time = datetime.split('-')
    year, month, day = date[:4], date[4:6], date[6:]
    hour = time[:2]


    # creating the sankey diagram
    data = dict(
        type='sankey',
        node=dict(
          pad=15,
          thickness=20,
          line=dict(
            width=0.5
          ),
          label=label_list,
        ),
        link = dict(
          source=source_list,
          target=target_list,
          value=value_list
        )
      )

    layout =  dict(
        title='Pageview-{}-{}-{}@{}'.format(year, month, day, hour),
        font=dict(
          size=10
        )
    )

    fig = dict(data=[data], layout=layout)
    return fig


def create_sankey_figure(data_dir, pageview_fp, covid_fp, save_fp=None):
    covid_df = pd.read_csv(data_dir + 'out/' + covid_fp)
    pageview_df = pd.read_csv(data_dir + 'out/pageview/' + pageview_fp,
                              index_col='Title')
    root, node_map, index_map, rev_index_map = build_graph(covid_df)
    datetime = pageview_fp.split('pageviews-')[-1][:-4]
    fig = sankey(root, node_map, index_map, rev_index_map, pageview_df,
                 datetime)
    fig = go.Figure(**fig)
    if save_fp:
        fig.write_image(data_dir + 'out/pageview/' + save_fp)
    return fig
