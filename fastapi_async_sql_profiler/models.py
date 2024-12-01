
from typing import Optional
from sqlalchemy import (
    JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text)
# import sqlalchemy
# import sqlalchemy.event
from sqlalchemy.orm import relationship
import sqlparse
from fastapi_async_sql_profiler.database import (
    Base, engine)  # init_db
from sqlalchemy.ext.asyncio import AsyncEngine
# from collections import OrderedDict


class Items(Base):
    # __tablename__ = 'middleware_items'
    __tablename__ = 'fasp_items'

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, default='')


class RequestInfo(Base):
    __tablename__ = 'fasp_requests'

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(200))
    query_params = Column(Text, default='')
    raw_body = Column(Text, default='')
    body = Column(Text, default='')
    method = Column(String(10))
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    time_taken = Column(Float, nullable=True)
    total_queries = Column(Integer)
    time_spent_queries = Column(Float, nullable=True)
    headers = Column(JSON)
    response_info = relationship(
        "ResponseInfo", back_populates="request_info",
        uselist=False)


class ResponseInfo(Base):
    __tablename__ = 'fasp_response'
    id = Column(Integer, primary_key=True, index=True)
    status_code = Column(Integer, nullable=True)
    raw_body = Column(Text, default='')
    body = Column(Text, default='')
    headers = Column(JSON)

    # Add a foreign key that references RequestInfo
    request_info_id = Column(
        Integer, ForeignKey('fasp_requests.id'),
        nullable=False, unique=True)
    request_info = relationship(
        RequestInfo, back_populates="response_info",
        uselist=False)
    # encoded_headers = Column(Text, default='')


class QueryInfo(Base):
    __tablename__ = 'fasp_query'
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=True)
    time_taken = Column(Float, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    traceback = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)

    request_id = Column(Integer, ForeignKey(
        'fasp_requests.id'), nullable=False, index=True)

    @property
    def formatted_traceback_list(self) -> list[str]:
        res = self.traceback.split('\n')[::2]
        return res

    @property
    def traceback_ln_only(self):
        return '\n'.join(self.traceback.split('\n')[::2])

    @property
    def formatted_query(self):
        sql_result = sqlparse.format(
            self.query,
            reindent=True,
            # keyword_case='upper',
            # use_space_around_operators=True,
            # indent_width=8,
            # indent_width=1,
            # reindent_aligned=True,
            # use_space_around_operators=True,
            # wrap_after=80,
            # compact=True,
            # use_space_around_operators=True,
            # reindent_aligned=True,
            # indent_tabs=True,
            output_format='sql'
            )
        return sql_result

    @property
    def first_keywords(self):
        parsed_query = sqlparse.parse(self.query)
        keywords = []
        for statement in parsed_query[0].tokens:
            if not statement.is_keyword:
                break
            keywords.append(statement.value)
        return ' '.join(keywords)

    @property
    def num_joins(self):
        parsed_query = sqlparse.parse(self.query)
        count = 0
        for statement in parsed_query:
            count += sum(map(lambda t: t.match(sqlparse.tokens.Keyword, r'\.*join\.*', regex=True), statement.flatten()))
        return count

    @property
    def tables_involved(self):
        """
        A really another rudimentary way to work out tables involved in a
        query.
        TODO: Can probably parse the SQL using sqlparse etc and pull out table
        info that way?
        """
        components = [x.strip() for x in self.query.split()]
        tables = []

        for idx, component in enumerate(components):
            # identified as tables...
            if component.lower() == 'from' or component.lower() == 'join' or component.lower() == 'as':
                try:
                    _next = components[idx + 1]
                    if not _next.startswith('('):  # Subquery
                        stripped = _next.strip().strip(',')

                        if stripped:
                            tables.append(stripped)
                except IndexError:  # Reach the end
                    pass
        return tables

    @property
    def get_tables_from_query(self):
        # Парсим SQL-запрос
        query = self.query
        parsed = sqlparse.parse(query)
        tables = set()  # Используем множество для уникальности
        tables = []  # Используем множество для уникальности

        for statement in parsed:
            # Ищем токены типа Identifier, которые представляют таблицы
            from_seen = False
            for token in statement.tokens:
                if token.ttype is sqlparse.tokens.Keyword and (
                    token.value.upper() == 'FROM'
                ):
                    from_seen = True
                    id_next_token_from, next_token_from = statement.token_next(
                        statement.token_index(token))
                    tables.append(next_token_from.get_real_name())
                    # tables.add(next_token_from.get_real_name())
                # if from_seen and token.ttype is sqlparse.tokens.Name:
                # # if from_seen and token.ttype is sqlparse.tokens.Keyword:
                #     # tables.add(token.get_real_name())  # add table name
                #     tables.append(token._get_repr_name())  # add table name
                #     tables.append(token._get_repr_value())  # add table name
                # if token.ttype is sqlparse.tokens.Keyword and (
                #     token.value.upper() in [
                #         'JOIN', 'INNER JOIN', 'LEFT JOIN',
                #         'RIGHT JOIN', 'FULL JOIN',
                #         'LEFT OUTER JOIN',]
                # ):
                if token.ttype is sqlparse.tokens.Keyword and (
                    'JOIN' in token.value.upper()
                ):
                    # Если видим JOIN, добавляем следующую таблицу
                    id_next_token, next_token = statement.token_next(
                        statement.token_index(token))

                    # tables.append(next_token.value)  # add table name
                    # tables.add(next_token.normalized)
                    # tables.add(next_token._get_repr_value())
                    # a = next_token.get_real_name()
                    tables.append(next_token.get_real_name())

                    # if next_token and next_token.ttype is sqlparse.tokens.Name:
                    #     tables.add(next_token.get_real_name())

        return list(tables)


async def init_db(*, engine_async: AsyncEngine | None = None):
    if engine_async:
        async with engine_async.begin() as conn:
            await conn.run_sync(Items.__table__.create, checkfirst=True)
            await conn.run_sync(RequestInfo.__table__.create, checkfirst=True)
            await conn.run_sync(QueryInfo.__table__.create, checkfirst=True)
            await conn.run_sync(ResponseInfo.__table__.create, checkfirst=True)
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Items.__table__.create, checkfirst=True)
            await conn.run_sync(RequestInfo.__table__.create, checkfirst=True)
            await conn.run_sync(QueryInfo.__table__.create, checkfirst=True)
            await conn.run_sync(ResponseInfo.__table__.create, checkfirst=True)

# task = asyncio.create_task(init_db())
