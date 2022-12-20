from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError

from schemas import TagSchema, TagAndItemSchema
from models import TagModel, StoreModel, ItemModel
from db import db

blp = Blueprint("tags", __name__, description="Operations on tags")

@blp.route("/store/<string:storeId>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, storeId):
        store = StoreModel.query.get_or_404(storeId)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tagData, storeId):
        tag = TagModel(**tagData, storeId=storeId)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        
        return tag

@blp.route("/tag/<string:tagId>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tagId):
        tag = TagModel.query.get_or_404(tagId)
        return tag

    @blp.response(202, description="Deletes a tag if no item is tagged with it.", example={"message": "Tag deleted"})
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.")
    def delete(self, tagId):
        tag = TagModel.query.get_or_404(tagId)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(400, message="Could not delete tag. Make sure tag is not associated with any items, then try again.")


@blp.route("/item/<string:itemId>/tag/<string:tagId>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, itemId, tagId):
        item = ItemModel.query.get_or_404(itemId)
        tag = TagModel.query.get_or_404(tagId)

        if item.store.id != tag.store.id:
            abort(400, message="Make sure item and tag belong to the same store before linking.")

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")
        
        return tag
    
    @blp.response(200, TagAndItemSchema)
    def delete(self, itemId, tagId):
        item = ItemModel.query.get_or_404(itemId)
        tag = TagModel.query.get_or_404(tagId)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")
        
        return {"message": "Item removed from tag", "item": item, "tag": tag}
