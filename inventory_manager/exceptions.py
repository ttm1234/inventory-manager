class InventoryManagerError(Exception):
    pass


class InventoryManagerExistsError(InventoryManagerError):
    pass


class InventoryManagerRedisNotFoundError(InventoryManagerError):
    pass


class InventoryManagerConsistencyError(InventoryManagerError):
    pass


class InventoryManagerPingError(InventoryManagerError):
    pass
