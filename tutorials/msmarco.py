import argparse


def main():
    def get_args(argv: List[str] = None):
        version = termcolor.colored('NBoost (v%s)' % __version__, 'cyan',
                                    attrs=['underline'])
        parser = argparse.ArgumentParser(
            description='%s: is a scalable, search-api-boosting platform for '
                        'developing and deploying SOTA models to improve the '
                        'relevance of search results..' % version,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--verbose', action='store_true', default=False,
                            help='turn on detailed logging')
        parser.add_argument('--host', type=str, default='127.0.0.1',
                            help='host of the proxy')
        parser.add_argument('--port', type=int, default=8000,
                            help='port of the proxy')
        parser.add_argument('--ext_host', type=str, default='127.0.0.1',
                            help='host of the server')
        parser.add_argument('--ext_port', type=int, default=9200,
                            help='port of the server')
        parser.add_argument('--lr', type=float, default=10e-3,
                            help='learning rate of the model')
        parser.add_argument('--model_ckpt', type=str,
                            default='bert_base_msmarco',
                            help='path to rerank model')
        parser.add_argument('--max_seq_len', type=int, default=64,
                            help='max combined token length')
        parser.add_argument('--batch_size', type=int, default=4,
                            help='batch size for running through rerank model')
        parser.add_argument('--data_dir', type=str, default='./.cache',
                            help='dir for model binary')
        parser.add_argument('--multiplier', type=int, default=5,
                            help='factor to increase results by')
        parser.add_argument('--field', type=str,
                            help='specified meta field to train on')
        parser.add_argument('--laps', type=int, default=100,
                            help='number of laps to perform for benchmarking')
        parser.add_argument('--server',
                            type=lambda x: import_class('server', x),
                            default='AioHttpServer', help='server class')
        parser.add_argument('--codex', type=lambda x: import_class('codex', x),
                            default='ESCodex', help='codex class')
        parser.add_argument('--model', type=lambda x: import_class('model', x),
                            default='BertMarcoModel', help='model class')
        parser.add_argument('--db', type=lambda x: import_class('db', x),
                            default='HashDb', help='db class')
        args = parser.parse_args(argv)
        return args