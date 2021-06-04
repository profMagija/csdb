from uuid import UUID
from .model import Changeset, ChangesetEntity


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


def dict_to_cset(data: dict) -> Changeset:
    ents = [ChangesetEntity(
            id=UUID(hex=e['id']),
            created=e['created'],
            props=[(a, return_strings(b), return_strings(c), d)
                   for a, b, c, d in e['props']]
            ) for e in data['entities']]

    parent = UUID(hex=data['parent']) if 'parent' in data else None
    cs = Changeset(parent, *ents)
    return cs


def cset_to_dict(changeset) -> dict:
    return {
        'parent': changeset.parent.hex if changeset.parent else None,
        'entities': [{
            'id': e.id.hex,
            'created': int(e.created),
            'props': [[a, convert_strings(b), convert_strings(c), int(d)] for a, b, c, d in e.props]
        } for e in changeset.entities]
    }
