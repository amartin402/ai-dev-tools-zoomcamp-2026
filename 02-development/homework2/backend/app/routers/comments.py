from fastapi import APIRouter

from ..models import Card, Comment, CreateCommentRequest
from ..store import store


router = APIRouter(tags=["Comments"])


@router.post("/cards/{card_id}/comments", response_model=dict[str, Comment | Card], operation_id="addComment")
def add_comment(card_id: str, request: CreateCommentRequest) -> dict[str, Comment | Card]:
    comment, card = store.add_comment(card_id, request)
    return {"comment": comment, "card": card}
