from sqlalchemy import Column, func
import sqlalchemy as db


class InventoryModificationRecordABC(object):
    classname_suffix_ = 'InventoryModificationRecord'
    tablename_suffix_ = '_inventory_modification_record'

    id = Column(db.Integer, autoincrement=True, primary_key=True)
    item_id = Column(db.String(length=64), comment='item_id')
    delta = Column(db.Integer, comment='num for modify，such as 100 or -50 and so on')

    __table_args__ = (
        {
            'comment': '库存管理增减记录，如仓库非使用情况的进出货物；'
                       'Inventory management with records of increase and decrease, '
                       'such as the entry and exit of goods in a warehouse during non-usage scenarios.',
        },
    )

    @classmethod
    def one_by_item_id(cls, item_id):
        r = cls.query.filter(cls.item_id == item_id).first()
        return r

    @classmethod
    def exists_by_item_id(cls, item_id):
        r = cls.one_by_item_id(item_id)
        return r is not None

    @classmethod
    def create(cls, item_id, delta):
        m = cls()
        m.item_id = item_id
        m.delta = delta

        return m

    # @classmethod
    # def sum_by_item_id(cls, db_session, item_id):
    #     stmt = db_session.query(func.sum(cls.delta)).filter(cls.item_id == item_id)
    #     result = stmt.scalar()
    #     result = int(result) if result is not None else 0
    #     return result

    @classmethod
    def sum_by_item_id(cls, item_id):
        """
        """
        stmt = cls.query.filter(cls.item_id == item_id).with_entities(func.sum(cls.delta))
        result = stmt.scalar()
        result = int(result) if result is not None else 0

        return result
