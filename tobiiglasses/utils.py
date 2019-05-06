import json
import logging
import gzip
import os


def load_json_from_file(source_dir, filename):
    logging.info('Loading JSON from %s in %s' % (filename, source_dir))
    with open(os.path.join(source_dir, filename)) as f:
        try:
            res = json.load(f)
        except:
            res = None
    return res

def import_json_items_from_gzipfile(source_dir, filename, decode_JSON=None):
    logging.info('Importing JSON items from %s in %s' % (filename, source_dir))
    with gzip.open(os.path.join(source_dir, filename)) as f:
        for item in f:
            json.loads(item.decode('utf-8'), object_hook=decode_JSON)

def import_df_from_pickle(source_dir, filename):
    logging.info('Importing dataframe from %s in %s' % (filename, source_dir))
    return pd.read_pickle(os.path.join(source_dir, filename))
