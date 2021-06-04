from ..csets.model import Changeset, ChangesetEntity
from json.encoder import JSONEncoder
import os
from typing import Dict, Optional
from uuid import UUID, uuid4
from csdb.model import Entity, EntityValue
from csdb.csets import utils
from ._base import Storage
import json


class FileEntity(Entity):
    def __init__(self, id: UUID, storage: 'FileStorage', exists: bool):
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

    def __delitem__(self, key: str) -> EntityValue:
        del self._data[key]

    def save(self):
        self._storage._save_entity_data(self.id, self._data)

    def delete(self):
        self._storage._delete_entity(self.id)
    
    def to_dict(self):
        return dict(self._data)


def die(*args):
    raise TypeError(*args)


class FileStorage(Storage):
    def __init__(self, path: str):
        self._path = path

    def get_entity(self, id: UUID) -> Optional[Entity]:
        return FileEntity(id, self, True) if self._exists_entity(id) else None

    def create_entity(self, id: UUID = None) -> Entity:
        return FileEntity(id or uuid4(), self, False)

    def _save_entity_data(self, id: UUID, data):
        with open(self._make_file_path(id), 'w') as f:
            json.dump(utils.convert_strings(data), f, separators=(',', ':'))

    def _get_entity_data(self, id: UUID) -> Dict[str, EntityValue]:
        with open(self._make_file_path(id)) as f:
            return utils.return_strings(json.load(f))

    def _exists_entity(self, id: UUID) -> bool:
        return os.path.exists(self._make_file_path(id))

    def _delete_entity(self, id: UUID):
        os.remove(self._make_file_path(id, False))

    def _make_file_path(self, id: UUID, create_dirs=True, prefix='items') -> str:
        filename = id.hex
        dname = os.path.join(self._path, prefix, filename[:2])
        if create_dirs:
            os.makedirs(dname, exist_ok=True)
        return os.path.join(dname, filename[2:])

    def commit_changeset(self, changeset: Changeset) -> UUID:

        data = utils.cset_to_dict(changeset)

        cid = uuid4()
        changeset.id = cid

        with open(self._make_file_path(cid, prefix='cs'), 'w') as f:
            json.dump(data, f)

        with open(self._csroot_path(), 'w') as f:
            f.write(cid.hex)

        return cid

    def get_last_changeset(self) -> Optional[UUID]:
        try:
            with open(self._csroot_path()) as f:
                return UUID(hex=f.read())
        except FileNotFoundError:
            return None

    def get_changeset(self, cid: UUID) -> Changeset:
        with open(self._make_file_path(cid, prefix='cs')) as f:
            data = json.load(f)

        cs = utils.dict_to_cset(data)
        cs.id = cid
        return cs

    def _csroot_path(self):
        return os.path.join(self._path, 'csroot')
