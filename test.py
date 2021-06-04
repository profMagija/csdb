
from csdb.storage.file import FileStorage
from uuid import UUID, uuid4
from csdb.storage.mem import MemStorage
from csdb.csets import Changeset, ChangesetEntity, apply_changeset

fdb = FileStorage('./db')

id1 = uuid4()
id2 = uuid4()
id3 = uuid4()


def try_changeset(*cs):
    res = apply_changeset(fdb, Changeset(fdb.get_last_changeset(), *cs))
    print('success', res)
    # fdb.print()


try_changeset(
    ChangesetEntity(id1, 1, [
        ('prop1', None, 'test', 1),
        ('prop2', None, 'test2', 1),
    ]),
    ChangesetEntity(id2, 1, [
        ('prop3', None, 213, 1),
        ('prop4', None, True, 1)
    ])
)


try_changeset(
    ChangesetEntity(id1, 0, [
        ('prop1', 'test', 'tralala', 0),
    ]),
    ChangesetEntity(id2, 0, [
        ('prop3', 213, None, -1),
        ('prop5', None, 'oho', 1)
    ])
)


try_changeset(
    ChangesetEntity(id3, 0, [
        ('properino', 213, None, 1),
    ])
)
