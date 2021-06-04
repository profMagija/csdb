from .model import Changeset, GenesisState


def apply_changeset(storage, changeset: Changeset):
    # validate
    for ecs in changeset.entities:
        ent = storage.get_entity(ecs.id)

        if ecs.created in (GenesisState.created, GenesisState.dead):
            print(' ** checking that entity does not exist')
            if ent is not None:
                print(' !! entity already exists')
                return False
        else:
            print(' ** checking that entity exists')
            if ent is None:
                print(' !! entity does not exist')
                return False

            for name, old_value, _, propgen in ecs.props:
                print(' ** checking property', name)
                if propgen in (GenesisState.created, GenesisState.dead):
                    print('   ** checking that property exists')
                    if name in ent:
                        print('   !! the property already exists')
                        return False
                else:
                    print('   ** checking that property value matches')
                    if ent[name] != old_value:
                        print('   !! the property does not match')
                        return False

    # apply
    for ecs in changeset.entities:
        if ecs.created == GenesisState.dead:
            # just checking for non-existance
            continue

        if ecs.created == GenesisState.created:
            ent = storage.create_entity(ecs.id)
        else:
            ent = storage.get_entity(ecs.id)

        if ecs.created == GenesisState.deleted:
            ent.delete()
        else:
            for name, _, new_value, propgen in ecs.props:
                if propgen == GenesisState.dead:
                    continue
                if propgen == GenesisState.deleted:
                    del ent[name]
                else:
                    ent[name] = new_value
            ent.save()

    storage.commit_changeset(changeset)

    return True
