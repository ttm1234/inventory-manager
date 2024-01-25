import redis
import sqlalchemy
import warnings

from .models import InventoryUsageRecordABC, InventoryModificationRecordABC
from .exceptions import *
from .inventory_redis_handler import InventoryRedisHandler

log = print


class InventoryManager(object):

    def __init__(self, prefix: str, db_session, db_Base, redis_client: redis.StrictRedis):
        """
        :param prefix: string, for database tablename prefix and redis key prefix, must be unique, such as "sku", "coupon" or "acitivty1" ...
        :param db_session: the "session" from sqlalchemy, or the "db.session" from flask_sqlalchemy
        :param db_Base: it's a class, so uppercase arg name, db_Base is the "Base" from sqlalchemy, or the "db.Model" from flask_sqlalchemy
        :param redis_client: redis.StrictRedis, common python redis client
        """
        self.prefix = prefix

        self._inventory_redis = InventoryRedisHandler(prefix, redis_client)

        self.db_session = db_session
        self.db_Base = db_Base

        self.cls_usage: InventoryUsageRecordABC = ...
        self.cls_modification: InventoryModificationRecordABC = ...

        self._init()

    @staticmethod
    def _gen_db_model_cls(prefix, db_Base, cls_ABC):
        cls_name = prefix + cls_ABC.classname_suffix_

        _tmp_cls = type('_tmp_' + cls_name, (db_Base, cls_ABC,), {
            '__abstract__': True,
            '__table_args__': cls_ABC.__table_args__,
        })

        cls_tablename = prefix + cls_ABC.tablename_suffix_
        r_cls = type(
            cls_name,
            (_tmp_cls,),
            {
                '__tablename__': cls_tablename,
                'author': 'ttm1234',
            }
        )
        return r_cls

    def _init(self):
        self.cls_usage = self._gen_db_model_cls(self.prefix, self.db_Base, InventoryUsageRecordABC)
        self.cls_modification = self._gen_db_model_cls(self.prefix, self.db_Base, InventoryModificationRecordABC)

        # _tmp_cls_usage = type('_tmp_cls_usage' + self.prefix, (self.db_Base, InventoryUsageRecordABC,), {
        #     '__abstract__': True,
        #     '__table_args__': InventoryUsageRecordABC.__table_args__,
        # })
        # cls_usage_name = self.prefix + InventoryUsageRecordABC.classname_suffix_
        # cls_usage_tablename = self.prefix + InventoryUsageRecordABC.tablename_suffix_
        # self.cls_usage = type(
        #     cls_usage_name,
        #     (_tmp_cls_usage,),
        #     {
        #         '__tablename__': cls_usage_tablename,
        #     }
        # )
        # # log('self.cls_usage', self.cls_usage)
        # # log('self.db_Base.metadata.tables', self.db_Base.metadata.tables)
        #
        # # -----------------------
        # _tmp_cls_modification = type('_tmp_cls_modification' + self.prefix, (self.db_Base, InventoryModificationRecordABC,), {
        #     '__abstract__': True,
        #     '__table_args__': InventoryModificationRecordABC.__table_args__,
        # })
        # cls_modification_name = self.prefix + InventoryModificationRecordABC.classname_suffix_
        # cls_modification_tablename = self.prefix + InventoryModificationRecordABC.tablename_suffix_
        # self.cls_modification = type(
        #     cls_modification_name,
        #     (_tmp_cls_modification,),
        #     {
        #         '__tablename__': cls_modification_tablename,
        #     }
        # )
        # # log('self.cls_modification', self.cls_modification)

    # ------------------------------------------------------
    def _db_save(self, *args):
        if len(args) == 0:
            return None
        for i in args:
            self.db_session.add(i)
        self.db_session.commit()

    # ------------------------------------------------------
    def ping(self):
        self.ping_redis()
        self.ping_db()

    def ping_redis(self):
        r = self._inventory_redis.ping()
        # log('ping_redis', r)
        if not r:
            raise InventoryManagerPingError('ping_redis error')

    def ping_db(self):
        ping_query = "SELECT 1"
        result = self.db_session.execute(ping_query)

        result_scalar = result.scalar()
        # # 检查查询结果
        # if result_scalar == 1:
        #     log("ping_db, Database is reachable.")
        # else:
        #     log("ping_db, Unexpected result from the ping query.")

        if result_scalar != 1:
            raise InventoryManagerPingError('ping_db error')

    def create_table(self):
        # Base.metadata.create_all(bind=engine)
        for _Model in [self.cls_usage, self.cls_modification, ]:
            # log('init, self.db_Base.metadata.tables', self.db_Base.metadata.tables)
            self.db_Base.metadata.tables[_Model.__tablename__].create(bind=self.db_session.get_bind())

    def table_initialized(self):
        # todo 其他方法
        inspector = sqlalchemy.inspect(self.db_session.get_bind())
        table_names = inspector.get_table_names()

        # log('check_init_finished, table_names', table_names)

        for _Model in [self.cls_usage, self.cls_modification]:
            # todo
            assert _Model.__tablename__ in table_names

    def inventory_init(self, item_id, num):
        self.cls_usage: InventoryUsageRecordABC
        self.cls_modification: InventoryModificationRecordABC

        if self.cls_modification.exists_by_item_id(item_id):
            raise InventoryManagerExistsError()

        if self._inventory_redis.get(item_id, null_to_zero=False) is not None:
            raise InventoryManagerConsistencyError()

        # -------------------------------
        m_modify = self.cls_modification.create(item_id, num)
        self._db_save(m_modify)
        self._inventory_redis.set(item_id, num)

    def modification_adjust(self, item_id, delta):
        """
        only for manager modify
        :param item_id: item_id
        :param delta: can be either a positive or a negative number.
        """
        self.cls_usage: InventoryUsageRecordABC
        self.cls_modification: InventoryModificationRecordABC

        # -------------------------------
        m_modify = self.cls_modification.create(item_id, delta)

        if not self._inventory_redis.exists(item_id):
            raise InventoryManagerRedisNotFoundError()

        self._db_save(m_modify)

        self._inventory_redis.incr(item_id, delta, allow_negative=True)

    def get(self, item_id):
        return self._inventory_redis.get(item_id)

    def usage_decr(self, item_id, num):
        self.cls_usage: InventoryUsageRecordABC
        self.cls_modification: InventoryModificationRecordABC

        assert num > 0
        delta = num * -1

        _n = self._inventory_redis.get(item_id, null_to_zero=False)
        if _n is None:
            raise InventoryManagerRedisNotFoundError()
        if _n < num:
            return False

        # ------------------------------------------------------
        m_usage = self.cls_usage.create(item_id, delta)

        success = self._inventory_redis.decr(item_id, num)
        if success:
            try:
                self._db_save(m_usage)
            except Exception as e:
                self._inventory_redis.incr(item_id, num)
                raise e

        return success

    def usage_incr(self, item_id, num):
        self.cls_usage: InventoryUsageRecordABC
        self.cls_modification: InventoryModificationRecordABC

        assert num > 0
        delta = num

        _n = self._inventory_redis.get(item_id, null_to_zero=False)
        if _n is None:
            raise InventoryManagerRedisNotFoundError()

        # ------------------------------------------------------
        m_usage = self.cls_usage.create(item_id, delta)

        db_success = False
        try:
            self._db_save(m_usage)
            db_success = True
        except Exception as e:
            raise e

        if db_success:
            self._inventory_redis.incr(item_id, num)

        return True

    def refresh(self, item_id):
        warnings.warn("Not Safe for Concurrency, 并发不安全", UserWarning)
        return self._refresh(item_id)

    def _refresh(self, item_id):
        self.cls_usage: InventoryUsageRecordABC
        self.cls_modification: InventoryModificationRecordABC

        if not self.cls_modification.exists_by_item_id(item_id):
            raise InventoryManagerExistsError()

        a = self.cls_modification.sum_by_item_id(item_id)
        b = self.cls_usage.sum_by_item_id(item_id)

        num = a + b

        self._inventory_redis.set(item_id, num)
        return num
