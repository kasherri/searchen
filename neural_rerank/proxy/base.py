from ..base import *
from ..server import BaseServer, ServerHandler
from ..clients import BaseClient
from ..models import BaseModel
import aiohttp
from aiohttp import web
import itertools


class BaseProxy(BaseServer):
    handler = ServerHandler(BaseServer.handler)

    def __init__(self,
                 client: BaseClient = BaseClient,
                 model: BaseModel = BaseModel,
                 ext_host: str = '127.0.0.1',
                 ext_port: int = 54001,
                 **kwargs):
        super().__init__(status_method=client.search_method, status_path=client.status_path, **kwargs)
        self.client = client
        self.model = model
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.queries = {}
        self.counter = itertools.count()
        self.handler.add_route(self.client.search_method, self.client.search_path)(self.search)
        self.handler.add_route(self.client.train_method, self.client.train_path)(self.train)

    @property
    def state(self):
        return {
            self.__name__: self.handler.bind_states(self),
            self.model.__name__: self.model.handler.bind_states(self.model),
            self.client.__name__: self.client.handler.bind_states(self.client)
        }

    @handler.add_state
    def backlog(self):
        return len(self.queries)

    async def pipe(self, reader, writer):
        try:
            while not reader.at_eof():
                writer.write(await reader.read(self._read_bytes))
        finally:
            writer.close()

    async def handle_not_found(self, request):
        self.handler.redirect(request.url)
        # try:
        #     remote_reader, remote_writer = await asyncio.open_connection(
        #         '127.0.0.1', 9200)
        #     pipe1 = self.pipe(local_reader, remote_writer)
        #     pipe2 = self.pipe(remote_reader, local_writer)
        #     await asyncio.gather(pipe1, pipe2)
        # finally:
        #     local_writer.close()

    async def train(self, request: web.BaseRequest) -> web.Response:
        qid, cid = await self.client.parse_qid_cid(request)
        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1

        self.logger.info('TRAIN: %s' % query)
        self.logger.debug('candidates: %s\nlabels:%s' % (pformat(candidates), pformat(labels)))

        await self.model.train(query, candidates, labels)
        return self.handler.no_content()

    async def search(self, request: web.BaseRequest) -> web.Response:
        topk, method, ext_url, data = await self.client.magnify_request(request)
        self.logger.info('PROXY: <Request %s %s >' % (method, ext_url))
        self.logger.debug(pfmt_obj(data))

        async with aiohttp.request(method, ext_url, data=data) as client_response:
            self.logger.info('RECV: ' + repr(client_response).split('\n')[0])
            query, candidates = await self.client.parse_query_candidates(request, client_response)

            self.logger.info('RANK: %s' % query)
            self.logger.debug('candidates: %s' % pformat(candidates))
            ranks = await self.model.rank(query, candidates)
            qid = next(self.counter)
            self.queries[qid] = query, candidates
            response = await self.client.format_response(client_response, topk, ranks, qid)

            return response
