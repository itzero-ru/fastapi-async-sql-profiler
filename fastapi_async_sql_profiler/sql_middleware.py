import datetime
# import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import traceback
import time
import sqlalchemy.event

from fastapi_async_sql_profiler.crud import add_db, get_obj_by_id
from fastapi_async_sql_profiler.models import Items, QueryInfo, RequestInfo


class SessionHandler(object):

    def __init__(self, engine=sqlalchemy.engine.Engine):

        self.started = False
        self.engine = engine
        # self.engine = engine_sync

        self.query_objs = []

    def _before_exec(self, conn, clause, multiparams, params):  # noqa: ARG002
        conn._sqltap_query_start_time = time.time()

    def _after_exec(self, conn, clause,
                    multiparams, params, results):  # noqa: ARG002

        end_time = time.time()
        start_time = getattr(conn, '_sqltap_query_start_time', end_time)

        try:
            # text = clause.bindparams(**params).compile(
            #     dialect=conn.engine.dialect)
            text = clause.compile(
                dialect=conn.engine.dialect,
                compile_kwargs={"literal_binds": True}  # add params value
            )
        except AttributeError:
            text = clause
        stack = traceback.extract_stack()
        stack_string = ''.join(traceback.format_list(stack))
        d = {
            "start_time": start_time,
            "end_time": end_time,
            "text": text,
            "stack": stack_string,
        }
        self.query_objs.append(d)

    def start(self):
        """Start profiling.

        :raises AssertionError: If calling this function when the session
            is already started.
        """
        if self.started is True:
            msg = "Profiling session is already started!"
            raise AssertionError(msg)
        self.started = True
        sqlalchemy.event.listen(self.engine, "before_execute",
                                self._before_exec)
        # sqlalchemy.event.listen(
        #     self.engine, "after_cursor_execute", self._after_exec)
        sqlalchemy.event.listen(self.engine, "after_execute", self._after_exec)

    def stop(self):
        """Stop profiling.

        :raises AssertionError: If calling this function when the session
            is already stopped.
        """
        if self.started is False:
            msg = "Profiling session is already stopped"
            raise AssertionError(msg)

        self.started = False
        sqlalchemy.event.remove(self.engine, "before_execute",
                                self._before_exec)
        # sqlalchemy.event.remove(
        #     self.engine, "after_cursor_execute", self._after_exec)
        sqlalchemy.event.remove(self.engine, "after_execute", self._after_exec)


class SQLProfilerMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, engine) -> None:

        self.app = app
        self.engine = engine
        self.dispatch_func = self.dispatch
        self.queries = []

    async def add_request(self, request, raw_body, body):

        method = request.method
        path = request.url.path
        query_params = str(request.query_params)
        headers_json = dict(request.headers)
        request_info = RequestInfo(path=path, query_params=query_params,
                                   raw_body=raw_body,
                                   body=body, method=method,
                                   start_time=datetime.datetime.utcnow(),
                                   headers=headers_json)
        item = Items(body='ZZZZZ')
        await add_db(item)
        await add_db(request_info)
        # session.add(request_info)
        # session.commit()
        # session.refresh(request_info)
        return request_info

    async def store(self, session_handler, request_id):

        for query_obj in session_handler.query_objs:
            time_taken = query_obj['end_time'] - query_obj['start_time']
            mstimetaken = round(time_taken*1000, 3)
            query_data = QueryInfo(query=str(
                query_obj['text']),
                request_id=request_id, time_taken=mstimetaken,
                traceback=query_obj['stack'])
            await add_db(query_data)
            # session.add(query_data)
            # session.commit()
            # session.close()
        end_time = datetime.datetime.utcnow()
        # request_obj = session.get(RequestInfo, request_id)
        request_obj = await get_obj_by_id(RequestInfo, request_id)
        time_taken = end_time - request_obj.start_time
        time_taken_second = time_taken.total_seconds()
        time_taken_ms = round(time_taken_second*1000, 3)
        request_obj.end_time = end_time
        request_obj.time_taken = time_taken_ms
        request_obj.total_queries = len(session_handler.query_objs)
        await add_db(request_obj)
        # session.add(request_obj)
        # session.commit()
        # session.refresh(request_obj)
        # session.close()

    async def set_body(self, request: Request, body: bytes):
        async def receive():
            return {"type": "http.request", "body": body}
        """
        File "/Users/set/projects/audio-books/backend/.venv/lib/python3.11/
        site-packages/starlette/middleware/base.py",
        line 58, in wrapped_receive

        if msg["type"] != "http.disconnect":

        raise RuntimeError(f"Unexpected message received: {msg['type']}")
        RuntimeError: Unexpected message received: http.request"""
        # request._receive = receive

    async def dispatch(self, request: Request,
                       call_next: RequestResponseEndpoint):

        # print("Before Request")
        await self.set_body(request, await request.body())
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" in content_type:
            raw_body = await request.form()
            body = str(dict(raw_body))
            raw_body = str(raw_body)
        elif "application/json" in content_type:
            raw_body = await request.body()
            body = raw_body.decode()
        else:
            raw_body = ''
            body = ''
        request_path = request.url.path
        if request_path == '/all_request' or request_path.startswith((
            '/request_detail', '/request_query', '/favicon', '/clear_db'
        )):
            response = await call_next(request)
        else:
            request_data = await self.add_request(request, raw_body, body)
            request_id = request_data.id
            # Not support async engine to SQLAlchemy
            session_handler = SessionHandler(self.engine.sync_engine)
            session_handler.start()
            response = await call_next(request)
            session_handler.stop()
            # print("After Request")
            await self.store(session_handler, request_id)
        return response

# class SQLProfilerMiddleware2(BaseHTTPMiddleware):
#     def __init__(self, app: FastAPI):
#         super().__init__(app)
#         self.queries = []

#     def add_request(self, request, raw_body, body):

#         method = request.method
#         path = request.url.path
#         query_params = str(request.query_params)
#         headers_json = dict(request.headers)
#         request_info = {}
#         return request_info

#     async def dispatch(self, request: Request, call_next):

#         # Генерация уникального идентификатора для запроса
#         request_id = str(uuid.uuid4())
#         # Сохранение идентификатора в состоянии запроса
#         request.state.request_id = request_id
#         raw_body = await request.body()
#         body = raw_body.decode()
#         request_data = self.add_request(request, raw_body, body)
#         self.queries = queries
#         start_time = time.time()

#         response = await call_next(request)

#         duration = time.time() - start_time
#         response.headers["X-Process-Time"] = str(duration)

#         if self.queries:
#             response.headers["X-Query-Count"] = str(len(self.queries))
#             response.headers["X-Query-Time"] = str(
#                 sum(q["duration"] for q in self.queries))

#         return response

#     def log_query(self, statement, parameters, duration):
#         # self.queries
#         queries.append({
#             "statement": str(statement),
#             "parameters": parameters,
#             "duration": duration
#         })

#         print(self.queries)
