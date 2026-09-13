from fastapi import APIRouter

from ..models import Board, BoardSummary, CreateBoardRequest, UpdateBoardRequest
from ..store import store


router = APIRouter(prefix="/boards", tags=["Boards"])


@router.get("", response_model=list[BoardSummary], operation_id="listBoards")
def list_boards() -> list[BoardSummary]:
    return store.list_boards()


@router.post("", response_model=Board, operation_id="createBoard")
def create_board(request: CreateBoardRequest) -> Board:
    return store.create_board(request)


@router.get("/{board_id}", response_model=Board, operation_id="getBoard")
def get_board(board_id: str) -> Board:
    return store.get_board(board_id)


@router.patch("/{board_id}", response_model=Board, operation_id="renameBoard")
def rename_board(board_id: str, request: UpdateBoardRequest) -> Board:
    return store.rename_board(board_id, request)


@router.delete("/{board_id}", response_model=bool, operation_id="deleteBoard")
def delete_board(board_id: str) -> bool:
    return store.delete_board(board_id)
