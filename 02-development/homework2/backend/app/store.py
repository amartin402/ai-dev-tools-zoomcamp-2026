from datetime import datetime, timezone

from .database import BoardRecord, SessionLocal
from .models import (
    ActivityEntry,
    Board,
    BoardSummary,
    Card,
    Column,
    Comment,
    CreateBoardRequest,
    CreateCardRequest,
    CreateCommentRequest,
    UpdateBoardRequest,
    UpdateCardRequest,
    User,
    new_id,
)


class NotFoundError(Exception):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found")
        self.resource = resource


class DatabaseStore:
    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _default_actor() -> User:
        return User(id="user-system", name="Kanbits", color="#7c7a71")

    @staticmethod
    def _columns() -> list[Column]:
        return [
            Column(id="todo", name="To Do", order=0),
            Column(id="progress", name="In Progress", order=1),
            Column(id="done", name="Done", order=2),
        ]

    @staticmethod
    def _to_record(board: Board) -> BoardRecord:
        return BoardRecord(id=board.id, data=board.model_dump(mode="json"))

    @staticmethod
    def _from_record(record: BoardRecord) -> Board:
        return Board.model_validate(record.data)

    def reset(self) -> None:
        with SessionLocal.begin() as session:
            session.query(BoardRecord).delete()

    def _get_board(self, board_id: str) -> Board:
        with SessionLocal() as session:
            record = session.get(BoardRecord, board_id)
            if record is None:
                raise NotFoundError("Board")
            return self._from_record(record)

    def _save_board(self, board: Board) -> Board:
        with SessionLocal.begin() as session:
            session.merge(self._to_record(board))
        return board

    def _get_card(self, card_id: str) -> tuple[Board, Card]:
        with SessionLocal() as session:
            records = session.query(BoardRecord).all()
            for record in records:
                board = self._from_record(record)
                for card in board.cards:
                    if card.id == card_id:
                        return board, card
        raise NotFoundError("Card")

    def list_boards(self) -> list[BoardSummary]:
        with SessionLocal() as session:
            records = session.query(BoardRecord).all()
            boards = [self._from_record(record) for record in records]
        return [
            BoardSummary(
                **board.model_dump(exclude={"cards"}),
                cardCount=len(board.cards),
            )
            for board in boards
        ]

    def get_board(self, board_id: str) -> Board:
        return self._get_board(board_id)

    def create_board(self, request: CreateBoardRequest) -> Board:
        now = self._now()
        board = Board(
            id=new_id("board"),
            name=request.name,
            createdAt=now,
            updatedAt=now,
            columns=self._columns(),
            cards=[],
        )
        return self._save_board(board)

    def rename_board(self, board_id: str, request: UpdateBoardRequest) -> Board:
        board = self._get_board(board_id)
        board.name = request.name
        board.updatedAt = self._now()
        return self._save_board(board)

    def delete_board(self, board_id: str) -> bool:
        with SessionLocal.begin() as session:
            record = session.get(BoardRecord, board_id)
            if record is None:
                raise NotFoundError("Board")
            session.delete(record)
        return True

    def create_card(self, board_id: str, request: CreateCardRequest) -> Card:
        board = self._get_board(board_id)
        column = next((item for item in board.columns if item.id == request.columnId), None)
        if column is None:
            raise ValueError("Column not found")
        now = self._now()
        actor = self._default_actor()
        card = Card(
            id=new_id("card"),
            title=request.title,
            description="",
            columnId=column.id,
            dueDate=None,
            labels=[],
            assignee=None,
            createdAt=now,
            updatedAt=now,
            comments=[],
            activityLog=[self._event("created", "created this task", actor, now)],
        )
        board.cards.append(card)
        column.cardOrder.append(card.id)
        board.updatedAt = now
        self._save_board(board)
        return card

    def update_card(self, card_id: str, request: UpdateCardRequest) -> Card:
        board, card = self._get_card(card_id)
        changes = {
            field: getattr(request, field)
            for field in request.model_fields_set
            if field not in {"columnId", "position", "actor"}
        }
        actor = request.actor or self._default_actor()
        activity_type = "edited"
        activity_detail = "updated this task"

        if request.columnId is not None or request.position is not None:
            target_column_id = request.columnId or card.columnId
            target_column = next((item for item in board.columns if item.id == target_column_id), None)
            if target_column is None:
                raise ValueError("Column not found")
            source_column = next(item for item in board.columns if item.id == card.columnId)
            target_position = request.position if request.position is not None else len(target_column.cardOrder)
            for column in board.columns:
                if card.id in column.cardOrder:
                    column.cardOrder.remove(card.id)
            target_column.cardOrder.insert(min(target_position, len(target_column.cardOrder)), card.id)
            card.columnId = target_column.id
            activity_type = "moved"
            activity_detail = (
                "reordered this task"
                if source_column.id == target_column.id
                else f"moved from {source_column.name} to {target_column.name}"
            )

        if len(changes) == 1 and "assignee" in changes:
            activity_type = "assigned"
            activity_detail = f"assigned to {request.assignee.name}" if request.assignee else "removed the assignee"
        elif len(changes) == 1 and "dueDate" in changes:
            activity_type = "due_date_changed"
            activity_detail = "changed the due date"
        elif len(changes) == 1 and "labels" in changes:
            activity_type = "label_changed"
            activity_detail = "updated the labels"

        for field, value in changes.items():
            setattr(card, field, value)
        now = self._now()
        card.updatedAt = now
        card.activityLog.insert(0, self._event(activity_type, activity_detail, actor, now))
        board.updatedAt = now
        self._save_board(board)
        return card

    def add_comment(self, card_id: str, request: CreateCommentRequest) -> tuple[Comment, Card]:
        board, card = self._get_card(card_id)
        now = self._now()
        comment = Comment(id=new_id("comment"), author=request.author, text=request.text, createdAt=now)
        card.comments.append(comment)
        card.updatedAt = now
        card.activityLog.insert(0, self._event("commented", "left a comment", request.author, now))
        board.updatedAt = now
        self._save_board(board)
        return comment, card

    @staticmethod
    def _event(event_type, detail, actor, timestamp) -> ActivityEntry:
        return ActivityEntry(id=new_id("event"), type=event_type, detail=detail, actor=actor, timestamp=timestamp)


store = DatabaseStore()
