from .inventory_manager import InventoryManager
from .exceptions import *


"""
# InventoryManager 的原理如下，这个库，会利用 sqlalchemy 和 redis 来记录库存。
# 其中，sqlalchemy 会把设置库存操作记录到数据库的一个表中，然后数量同步记录到redis，
# 使用消费库存的时候，会在 redis 中执行 incr 或者 decr 操作，同时在数据库的另一个表中记录流水日志。
# 在 InventoryManager 中，会使用 python 动态创建 class 来实现 sqlalchemy 的 model class 定义和使用。
# 所以 InventoryManager 实例化的参数需要 sqlalchemy 的 db_session, Base，还需要 redis client。
# 考虑到实际使用场景，如果有多个 InventoryManager(), 那么他们的数据库表名字，redis的key，都需要用不同前缀隔开。
# 所以实例化的参数需要提供一个 prefix（要求prefix在业务中务必是unique）


# demo 如下
# ========================================================================
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from inventory_manager import InventoryManager


# 创建必要的参数
# --------------------------------------------------
db_prefix = 'prefix1'


# 这个 get_db_arg 是获取 sqlalchemy 的 db_session, Base，给 InventoryManager 参数用
def get_db_arg():
    # 需要提前确认 database 已存在
    db_config = 'mysql+pymysql://***:****@127.0.0.1:3306/demo1?charset=utf8mb4'

    echo = False
    # echo = True
    max_overflow = 1000
    engine = create_engine(db_config, pool_size=40, max_overflow=max_overflow, pool_recycle=28000, pool_pre_ping=True, convert_unicode=True, echo=echo)

    db_session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )
    Base = declarative_base()
    Base.query = db_session.query_property()
    Base.__table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    return db_session, Base


redis_host = '127.0.0.1'
redis_port = 6379
redis_db = 1
redis_password = ''

red = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    db=redis_db,

    decode_responses=True,
)

# red.flushdb()

db_session, db_Base = get_db_arg()

# 这个是例子，如 item_id='1'的初始库存10个，item_id='2'的初始库存20个，。。。。
map_sku_inventory = {
    '1': 10,
    '2': 20,
    '3': 30,
}


# 以下是使用方法教程。
# ========================================================================
# ========================================================================
# ========================================================================
# ========================================================================

# 实例一个 InventoryManager，参数第一个代表字符串前缀，接着是前文的 sqlalchemy 变量，最后一个是 redis client
mgr = InventoryManager(db_prefix, db_session, db_Base, red)

# ping 一下 database 和 redis 通不通
mgr.ping()

# 这个会在 db 中创建对应的 table
mgr.create_table()

# 检查 db 中创建对应的 table 是否完成
mgr.table_initialized()

# 初始化设置库存最大数量
for item_id, num in map_sku_inventory.items():
    mgr.inventory_init(item_id, num)

# 修改总库存量
mgr.modification_adjust(item_id='1', delta=100)

# 获取库存
r = mgr.get(item_id='1')
print('''r = mgr.get(item_id='1')''', r)

# 扣库存
success = mgr.usage_decr(item_id='1', num=1)
assert success
r = mgr.get(item_id='1')
print('''mgr.usage_decr(item_id='1', num=1)''', r)

# 扣库存
success = mgr.usage_decr(item_id='1', num=3)
assert success
r = mgr.get(item_id='1')
print('''mgr.usage_decr(item_id='1', num=3)''', r)

# 扣库存
success = mgr.usage_decr(item_id='1', num=999999999)
assert not success
r = mgr.get(item_id='1')
print('''failed, mgr.usage_decr(item_id='1', num=999999999)''', r)

# 退回库存
mgr.usage_incr(item_id='1', num=1000)
r = mgr.get(item_id='1')
print('''mgr.usage_incr(item_id='1', num=1000)''', r)

# redis 数据丢失或不一致的情况下，使用这个恢复 redis
r = mgr.refresh(item_id='1')
print('''r = mgr.refresh(item_id='1')''', r)

'''
# todo 
    1. 幂等，幂等id
    2. refresh() 没有加锁
    3. def refresh_all()
    4. 没测 flask_sqlalchemy 环境
    5. 没测 sqlalchemy 2.x.x 兼容
    6. table add column create_time
'''

"""
