from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("items", __name__, description="Operations on items")

@blp.route("/item/<string:itemId>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, itemId):
        item = ItemModel.query.get_or_404(itemId)
        return item

    @blp.arguments(ItemUpdateSchema)  
    @blp.response(200, ItemSchema)  
    def put(self, data, itemId):
        item = ItemModel.query.get_or_404(itemId)
        item.price = data["price"]
        item.name = data["name"]

        db.session.add(item)
        db.session.commit()

        return item

    @jwt_required()
    def delete(self, itemId):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        item = ItemModel.query.get_or_404(itemId)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}


@blp.route("/item")
class Items(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, itemData):
        item = ItemModel(**itemData)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting the item.")

        return item
