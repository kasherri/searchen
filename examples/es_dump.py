from elasticsearch import Elasticsearch
import elasticsearch.helpers
import os, csv

## MS MARCO DUMP
INDEX = 'ms_marco'

ES_HOST = 'localhost'
READ_CHUNKSIZE = 10 * 6
REQUEST_TIMEOUT = 1000
MAX_CHUNK_BYTES = 10 ** 9
MAX_RETRIES = 10

MAPPINGS = {
    "mappings": {
        "properties": {
            "passage": {
                "type": "text",
                "analyzer": "english"
            }
        }
    },
    "settings": {
        "index": {
            "number_of_shards": 1
        }
    }
}


def stream_bodies():
    with open(os.path.join('collection.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for id, passage in data:
            body = {
                "_index": INDEX,
                "_id": id,
                "_source": {
                    "passage": passage,
                }
            }
            # print(f'Sent {id}: {passage}.')
            yield body


if __name__ == "__main__":
    es = Elasticsearch(host=ES_HOST)

    if es.indices.exists(INDEX):
        res = es.indices.delete(index=INDEX)
        print(res)
    res = es.indices.create(index=INDEX, body=MAPPINGS)
    print(res)

    print('Sending articles.')
    for ok, response in elasticsearch.helpers.streaming_bulk(es, actions=stream_bodies()):
        if not ok:
            # failure inserting
            print(response)