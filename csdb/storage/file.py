from ..csets.model import Changeset, ChangesetEntity
from json.encoder import JSONEncoder
import os
from typing import Dict, Optional
from uuid import UUID, uuid4
from csdb.model import Entity, EntityValue
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


def die(*args):
    raise TypeError(*args)


def return_strings(x):
    if isinstance(x, str):
        if x[0] == '$':
            return x[1:]
        elif x[0] == '#':
            return UUID(hex=x[1:])
        else:
            raise ValueError('unknown string prefix "' + x[0] + '"')
    elif isinstance(x, list):
        return [return_strings(y) for y in x]
    elif isinstance(x, dict):
        return {k: return_strings(v) for k, v in x.items()}
    else:
        return x


def convert_strings(x):
    if isinstance(x, str):
        return '$' + x
    elif isinstance(x, UUID):
        return '#' + x
    elif isinstance(x, list):
        return [convert_strings(y) for y in x]
    elif isinstance(x, dict):
        return {k: convert_strings(v) for k, v in x.items()}
    else:
        return x


class FileStorage(Storage):
    def __init__(self, path: str):
        self._path = path

    def get_entity(self, id: UUID) -> Optional[Entity]:
        return FileEntity(id, self, True) if self._exists_entity(id) else None

    def create_entity(self, id: UUID = None) -> Entity:
        return FileEntity(id or uuid4(), self, False)

    def _save_entity_data(self, id: UUID, data):
        with open(self._make_file_path(id), 'w') as f:
            json.dump(convert_strings(data), f, separators=(',', ':'))

    def _get_entity_data(self, id: UUID) -> Dict[str, EntityValue]:
        with open(self._make_file_path(id)) as f:
            return return_strings(json.load(f))

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
        data = {
            'parent': changeset.parent.hex if changeset.parent else None,
            'entities': [{
                'id': e.id.hex,
                'created': int(e.created),
                'props': [[a, convert_strings(b), convert_strings(c), int(d)] for a, b, c, d in e.props]
            } for e in changeset.entities]
        }

        cid = uuid4()
        changeset.id = cid

        print(data)

        with open(self._make_file_path(cid, prefix='cs'), 'w') as f:
            json.dump(data, f)

        with open(self._csroot_path(), 'w') as f:
            f.write(cid.hex)

    def get_last_changeset(self) -> Optional[UUID]:
        try:
            with open(self._csroot_path()) as f:
                return UUID(hex=f.read())
        except FileNotFoundError:
            return None

    def get_changeset(self, cid: UUID) -> Changeset:
        with open(self._make_file_path(cid, prefix='cs')) as f:
            data = json.load(f)

        ents = [ChangesetEntity(
            id=UUID(hex=e['id']),
            created=e['created'],
            props=[(a, return_strings(b), return_strings(c), d)
                   for a, b, c, d in e['props']]
        ) for e in data['entities']]

        cs = Changeset(*ents)
        cs.parent = UUID(hex=data['parent'])
        cs.id = cid

    def _csroot_path(self):
        return os.path.join(self._path, 'csroot')
