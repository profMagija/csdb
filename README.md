# CSDB - changeset database

This is a very simple implementation of a changeset-based database, which allows safe concurrent transactions spanning multiple objects, and multiple transactions editting the same object, while keeping variable atomicity guarantees.

## What ?

Think `git` applied to MongoDB.

## Why ?

The goal of this database is to allow the following use case: having multiple users modify multiple files atomicaly, and not having the transactions fail if multiple users try to edit the same entity. This is important for entities which contain a lot of properties, and only a subset of them is even accessed by a single user.

Some databases (e.g. MongoDB) do not guarantee consistency. Some (like CouchDB) do, but only on the document level (using revisions).

This one works similar to CouchDB, but allows each transaction to specify exactly which fields it is accessing - so multiple transactions can still operate on the same data (if they observe the **multiple readers xor single writer** rule). If the transaction fails, the application can either retry it automaticaly (by recalculating everything, if there was no human interaction), or present the issue to the end user.

## How ?

The database is entity-based, similar to MongoDB. Every entity is a list of key-value pairs, where keys are strings, and values can be any JSON-like value. However it uses a stronger, atomic storage model.

I'll demonstrate with an example. Let's say our database contains the following entities:

```
Entity A:
    key1 = "value1"
    key2 = 3.14

Entity B:
    name = "George"
    age  = 24
```

Now lets say we want to increate the `Entity A`'s `key2` value by 1. We will commit the following changeset to the database:

```
Changeset 1:
    Entity A:
        key2 = 3.14 -> 4.14
```

Note that the changeset contains both the **old and new** value. This immediately means we have atomicity. The database checks at commit time that the old value is still the same, and rejects **the whole** transaction if the check fails. This means that if we execute two "increment" operations, either:
- both will succeed, giving `5.14` (one after the other)
- one of them will fail, giving `4.14` (tried to modify at the same time, the first one succeeded)

In both cases we have a correct result, and in the second the transaction can be retried.

Other benefit is that if we had a concurrent changeset only concerning `Entity B`, or only concerning `Entity A`'s other properties, both could succeed, irrelevant of the order they are comitted in. This is important for transactions that are very long (e.g. include user interaction, editing a page then saving).

Another property of the changesets is that they can keep the value unchanged:

```
Changeset 2:
    Entity B:
        name = "George" -> "George"
        age  = 24 -> 25
```

In this case, the transaction will also fail if the name was modified in the meantime - but will not modify it itself.

We can also have changesets which create entities, delete entities, add new properties, remove properties, and check that properties do not exist (important if we had a `if 'prop' not in entity` check during a transacion). There can also be other variations for more "permissive" changesets (e.g. a requirement that the property exists, irrelevant of its actual value, or that it satisfies a given expression).

By listing all variables accessed during the transaction (even only read), we can give a guarantee of atomicity.

**NOTE:** such implementation is still not 100% atomic - there is still a possibility of a property being modified, then reverted, while a second is read non-concurrently. In this case, a non-atomic state can be read, while the transaction will succeed at the end. To fix this, a versioning system should be employed for each property, that is only incremented on modification. This is not implemented as of right now.

## Further discussion

### Indexing and collections

This would just be a separate layer that goes on top of the rest. The indexes can be updated whenever a changeset is comitted, and can use the data from the changeset to know what indexes need to be rebuilt.

Collections would also be an aditional layer, where each entity can specify in which collection it is. This can also be atomicaly tracked through changesets.

### Parallelization and concurrent snapshot application

Because two changesets can potentially be in conflict only if they mention the same entity (more specificaly the same property of the same entity), we can use some hashing and filtering / sharding to verify and apply multiple changesets at the same time. However performance is not the main concern of this implementation.

### Changeset persistance and rollbacking

The changesets are currently persisted. This has a side benefit of any changesets being reversible, and we can jump to arbitrary points in time. This history is also delta-encoded, so it requires less storage space than storing every version of every entity (e.g. like `git` does).

Only additional requirement is that changesets that delete an entity are extended with the full data of the entity at time of deletion, so that it can be reinstantiated to rollback the changeset.

We can also remove a single changeset, and then reapply all the remaining on top of it, potentialy fixing any merge conflicts.

### Read replicas

In a common case we will have a large read volume, and a small write volume. In this case we can have read replicas, which replicate the data read-only. A single writer node does all the changeset processing, and regularly sends the changes to the replicas (which don't need to validate anything for consistency).

Note that this still keeps the atomicity - if we try to create a changeset with the stale data, the changeset will fail on the write master, as it always has the latest version of the database.

## To Do

- [X] implement base changeset handling
- [ ] implement collections
- [ ] implement property indexing
- [ ] implement querying / lookup by property
- [ ] add a better storage solution (currently using JSON files)
- [ ] move to a non-Python runtime, and add parallelization