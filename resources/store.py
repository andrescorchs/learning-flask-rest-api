from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema

from db import db
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("stores", __name__, description="Operations on stores")

@blp.route("/store/<string:storeId>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, storeId):
        store = StoreModel.query.get_or_404(storeId)
        return store
    
    def delete(self, storeId):
        store = StoreModel.query.get_or_404(storeId)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted."}

@blp.route("/store")
class Stores(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, requestData):        
        store = StoreModel(**requestData)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting the store.")

        return store