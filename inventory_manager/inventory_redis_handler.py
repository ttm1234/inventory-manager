import redis


class InventoryRedisHandler(object):
    lua_script = """
        local current_inventory = tonumber(redis.call('GET', KEYS[1])) or -1
        
        if current_inventory >= tonumber(ARGV[1]) then
            redis.call('DECRBY', KEYS[1], ARGV[1])
            return true
        else
            return false
        end
    """

    def __init__(self, db_prefix: str, redis_client: redis.StrictRedis):
        self.prefix = db_prefix
        self.red: redis.StrictRedis = redis_client

        self._init()

    def _init(self):
        self.redis_func_lua_script = self.red.register_script(self.lua_script)

    def get_key(self, item_id):
        assert '.' not in item_id
        r = 'InventoryManager.{}.{}'.format(self.prefix, item_id)
        return r

    def ping(self):
        return self.red.ping()

    def set(self, item_id, n):
        assert isinstance(n, int)
        k = self.get_key(item_id)
        self.red.set(k, n)
        return True

    def get(self, item_id, null_to_zero=True):
        k = self.get_key(item_id)
        s = self.red.get(k)

        if s is not None:
            return int(s)
        else:
            if null_to_zero:
                return 0
            else:
                return None

    def exists(self, item_id):
        r = self.get(item_id, null_to_zero=False)
        return r is not None

    def incr(self, item_id, n, allow_negative=False):
        assert isinstance(n, int)
        if not allow_negative:
            assert n > 0

        k = self.get_key(item_id)
        self.red.incr(k, n)
        return True

    def decr(self, item_id, n):
        assert isinstance(n, int) and n > 0
        k = self.get_key(item_id)
        if n == 1:
            r = self.red.decr(k, 1)
            # print('self.red.decr', type(r), r)
            return int(r) >= 0

        else:
            return self.decr_multi(k, n)

    def decr_multi(self, k, n):
        result = self.redis_func_lua_script(keys=[k], args=[n])
        result = bool(result)
        return result
