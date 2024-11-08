from fastapi_async_sql_profiler.repository import AbstractRepository


class RequestInfoService:
    def __init__(self, request_info_repository: AbstractRepository):
        self.request_info_repository = request_info_repository

    def get_request_info_by_id(self, id):
        return self.request_info_repository.get_by_id(id)

    def get_request_info_all(self):
        return self.request_info_repository.get_all()

    def create(self, request_info_data):
        # business logic
        return self.request_info_repository.create(request_info_data)


# async def get_request_info_list(filter: dict = {}):
#     """Get all RequestInfo"""

#     async with async_session_maker() as session:
#         # stmt = select(model).where(model.id == kwargs['id'])

#         model = RequestInfo

#         exclude_fields = ['body']

#         all_fields = set(column.key for column in model.__table__.columns)
#         if exclude_fields:
#             fields_to_load = all_fields - set(exclude_fields)
#             fields_to_load = [getattr(model, f) for f in fields_to_load]
#             stmt = select(model).options(load_only(*fields_to_load))
#         else:
#             stmt = select(model)
#         # stmt = select(model)
#         stmt = stmt.options(
#             joinedload(RequestInfo.response_info).load_only(
#                 ResponseInfo.id,
#                 ResponseInfo.status_code,
#                 ResponseInfo.headers,
#             ))
#         print(stmt)
#         # stmt = stmt.options(joinedload(*joinedload_names))
#         # stmt = stmt.options(joinedload(RequestInfo.response_info))
#         stmt = stmt.filter_by(**filter)
#         stmt = stmt.order_by(desc(model.id))
#         res = await session.execute(stmt)

#         return res.scalars().all()
