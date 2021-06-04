from typing import Union
from uuid import UUID, uuid4

EntityValue = Union[int, float, bool, str, UUID, None]


class Entity:
    id: UUID

    def __getitem__(self, key: str) -> EntityValue:
        raise NotImplementedError()

    def __setitem__(self, key: str, val: EntityValue):
        raise NotImplementedError()
    
    def __contains__(self, key: str) -> bool:
        raise NotImplementedError()
    
    def __delitem__(self, key: str):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()
    
    def delete(self):
        raise NotImplementedError()
