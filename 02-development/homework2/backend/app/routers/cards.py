from fastapi import APIRouter

from ..models import Card, CreateCardRequest, UpdateCardRequest
from ..store import store


router = APIRouter(tags=["Cards"])


@router.post("/boards/{board_id}/cards", response_model=Card, operation_id="createCard")
def create_card(board_id: str, request: CreateCardRequest) -> Card:
    return store.create_card(board_id, request)


@router.patch("/cards/{card_id}", response_model=Card, operation_id="updateCard")
def update_card(card_id: str, request: UpdateCardRequest) -> Card:
    return store.update_card(card_id, request)
