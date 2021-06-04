from typing import List, Tuple, Union
from uuid import UUID
from ..model import EntityValue
from enum import IntEnum


class GenesisState(IntEnum):
    """State of creation / delition of an entity or property.
    
    - deleted: the item needs to exist, and gets deleted
    - alive: the item needs to exist, and remains existing
    - created: the item needs to be freshly created
    - dead: the item needs to not exist, and is not created (just verified)
    """
    deleted = -1
    alive = 0
    created = 1
    dead = 2


class ChangesetEntity:
    id: UUID
    created: GenesisState
    props: List[Tuple[str, EntityValue, EntityValue, GenesisState]]

    def __init__(self, id: UUID, created: Union[int, GenesisState], props: List[Tuple[str, EntityValue, EntityValue, Union[int, GenesisState]]]):
        self.id = id
        self.created = GenesisState(created)
        self.props = [(k, o, n, GenesisState(g)) for k, o, n, g in props]


class Changeset:
    id: UUID
    parent: UUID
    entities: List[ChangesetEntity]

    def __init__(self, parent: UUID, *entities: List[ChangesetEntity]):
        self.parent = parent
        self.entities = entities
