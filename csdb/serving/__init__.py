from csdb.csets import algo, utils
from uuid import UUID
from csdb.csets.model import ChangesetEntity
from flask import Flask, request, Response
from ..storage import Storage


def serve(path, **kwargs):
    if path is not None:
        from ..storage.file import FileStorage
        DB = FileStorage(path)
    else:
        from ..storage.mem import MemStorage
        DB = MemStorage()

    app = Flask(__name__)

    @app.route('/cset', methods=["POST"])
    def post_cset():
        data = request.json
        cset = utils.dict_to_cset(data)
        print(data)
        if not algo.apply_changeset(DB, cset):
            return Response('transaction aborted', status=400)
        cid = DB.commit_changeset(cset)
        return cid.hex
    
    @app.route('/entity/<eid>', methods=["GET"])
    def get_entity(eid: str):
        ent = DB.get_entity(UUID(hex=eid))
        if ent is None:
            return Response('not found', status=404)
        return ent.to_dict()

    app.run(**kwargs)
