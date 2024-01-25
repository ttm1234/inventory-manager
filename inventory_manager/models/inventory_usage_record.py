from sqlalchemy import Column, func
import sqlalchemy as db


class InventoryUsageRecordABC(object):
    classname_suffix_ = 'InventoryUsageRecord'
    tablename_suffix_ = '_inventory_usage_record'

    id = Column(db.Integer, autoincrement=True, primary_key=True)
    item_id = Column(db.String(length=64), comment='item_id')
    delta = Column(db.Integer, comment='num for use，such as -1 for purchasing an item and +1 for canceling an order.')

    __table_args__ = (
        {
            'comment': '库存管理使用记录，如购买一个就是-1，取消订单一个就是1; '
                       'Inventory management with usage records, '
                       'such as -1 for purchasing an item and +1 for canceling an order.',
        },
    )

    @classmethod
    def create(cls, item_id, delta):
        m = cls()
        m.item_id = item_id
        m.delta = delta

        return m

    @classmethod
    def sum_by_item_id(cls, item_id):
        """
        """
        stmt = cls.query.filter(cls.item_id == item_id).with_entities(func.sum(cls.delta))
        result = stmt.scalar()
        result = int(result) if result is not None else 0

        return result
