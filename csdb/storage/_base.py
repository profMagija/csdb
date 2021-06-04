from typing import Optional
from uuid import UUID
from ..model import Entity
from ..csets.model import Changeset


class Storage:
    def get_entity(self, id: UUID) -> Optional[Entity]:
        raise NotImplementedError()

    def create_entity(self, id: UUID) -> Entity:
        raise NotImplementedError()

    def get_changeset(self, cid: UUID) -> Changeset:
        raise NotImplementedError()
    
    def get_last_changeset(self) -> Optional[UUID]:
        raise NotImplementedError()

    def commit_changeset(self, changeset: Changeset):
        raise NotImplementedError()
