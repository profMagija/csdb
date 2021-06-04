from csdb.csets.model import Changeset
import os
from typing import Dict, Optional
from uuid import UUID, uuid4
from csdb.model import Entity, EntityValue
from ._base import Storage


class MemEntity(Entity):
    def __init__(self, id: UUID, storage: 'MemStorage', exists: bool):
        self.id = id
        self._storage = storage
        self._exists = exists
        self._data = {} if not exists else storage._get_entity_data(id)

    def __setitem__(self, key: str, val: EntityValue):
        self._data[key] = val

    def __getitem__(self, key: str) -> EntityValue:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __delitem__(self, key: str):
        del self._data[key]

    def save(self):
        self._storage._save_entity_data(self.id, self._data)


class MemStorage(Storage):
    def __init__(self):
        self._storage = {}
        self._changesets = {}
        self._last_changeset = None

    def get_entity(self, id: UUID) -> Entity:
        return MemEntity(id, self, True) if id in self._storage else None

    def create_entity(self, id: UUID = None) -> Entity:
        return MemEntity(id or uuid4(), self, False)

    def _save_entity_data(self, id: UUID, data):
        self._storage[id] = data

    def _get_entity_data(self, id: UUID) -> Dict[str, EntityValue]:
        return self._storage[id]

    def print(self):
        for eid, ent in self._storage.items():
            print('Entity', eid.hex)
            for k, v in ent.items():
                print('  ', k, ':', repr(v))

    def get_last_changeset(self) -> Optional[UUID]:
        return self._last_changeset

    def commit_changeset(self, changeset):
        cid = uuid4()
        self._changesets[cid] = changeset
        self._last_changeset = cid

    def get_changeset(self, cid: UUID) -> Changeset:
        return self._changesets[cid]
