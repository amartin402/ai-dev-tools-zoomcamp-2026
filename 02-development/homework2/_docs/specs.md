# Kanbits — Mini Kanban Board: Product & Technical Spec

## 1. Overview

Kanbits is a lightweight, real-time, multi-user Kanban board app. Users can create
multiple boards (e.g. one per project), each with fixed columns (To Do / In Progress /
Done), and collaborate live — no login required, just a display name.

---

## 2. Core Entities

### 2.1 Board
| Field | Type | Notes |
|---|---|---|
| `id` | string (UUID) | |
| `name` | string | e.g. "Website Redesign" |
| `createdAt` | timestamp | |
| `columns` | Column[] | Fixed set, created with the board |

### 2.2 Column
| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `name` | enum | `"To Do"`, `"In Progress"`, `"Done"` — fixed, not renameable/reorderable (v1) |
| `order` | number | Fixed: 0, 1, 2 |
| `cardOrder` | string[] | Ordered list of card IDs in this column (drives drag position) |

### 2.3 Card (Task)
| Field | Type | Notes |
|---|---|---|
| `id` | string (UUID) | |
| `boardId` | string | |
| `columnId` | string | |
| `title` | string | Required |
| `description` | string | Optional, markdown-lite or plain text |
| `dueDate` | date \| null | Optional |
| `labels` | Label[] | Zero or more |
| `assignee` | User \| null | One assignee per card (v1) |
| `createdAt` | timestamp | |
| `updatedAt` | timestamp | |
| `comments` | Comment[] | |
| `activityLog` | ActivityEntry[] | Auto-generated |

### 2.4 Label
| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `name` | string | e.g. "Bug", "Urgent" |
| `color` | string (hex) | |

### 2.5 User (lightweight, no auth)
| Field | Type | Notes |
|---|---|---|
| `id` | string | Generated client-side, persisted in localStorage |
| `name` | string | User-entered display name |
| `color` | string (hex) | Auto-assigned, used for avatars/presence cursors |

> No passwords, no accounts. A user picks a name once per browser; it's remembered
> locally and reused across sessions and boards.

### 2.6 Comment
| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `cardId` | string | |
| `author` | User | |
| `text` | string | |
| `createdAt` | timestamp | |

### 2.7 ActivityEntry
| Field | Type | Notes |
|---|---|---|
| `id` | string | |
| `cardId` | string | |
| `actor` | User | Who did it |
| `type` | enum | `created`, `moved`, `edited`, `assigned`, `commented`, `due_date_changed`, `label_changed` |
| `detail` | string | Human-readable, e.g. "moved from To Do to In Progress" |
| `timestamp` | timestamp | |

---

## 3. Main User Flows

### 3.1 Entering the app
1. First visit: prompt for a display name (stored in localStorage, no login).
2. Land on a **Board List** view showing all existing boards (name, card count, last updated).
3. User can **create a new board** (enter a name → auto-creates the 3 fixed columns) or **open an existing board**.

### 3.2 Viewing a board
1. Board opens showing 3 columns: To Do / In Progress / Done.
2. Each column shows its cards as compact cards (title, labels, due date, assignee avatar).
3. Presence indicators show which other users currently have this board open (avatars top-right + optional live cursors).

### 3.3 Creating a card
1. Click "+ Add card" in a column.
2. Enter title (required) → card is created instantly, appears at bottom of column, syncs to all viewers.
3. Click the card to open a detail panel and fill in description, due date, labels, assignee.

### 3.4 Editing a card
1. Click a card to open the detail modal/panel.
2. Edit any field inline; changes save automatically (debounced) and broadcast to other viewers in real time.
3. Every meaningful change appends an entry to the card's activity log.

### 3.5 Moving a card (drag & drop)
1. Drag a card within a column to reorder, or across columns to change status.
2. On drop: update `columnId` + `cardOrder` for affected columns, broadcast to all connected clients, append an activity log entry ("moved from X to Y").
3. Other users see the card animate into its new position live.

### 3.6 Commenting
1. In the card detail panel, add a comment with name + timestamp.
2. New comments appear live for all viewers with the card open.

### 3.7 Filtering / searching (assumed, lightweight v1 addition)
1. Board view has a filter bar: filter by assignee, label, or due date range.
2. Optional text search box filters cards by title/description match.

### 3.8 Managing boards
1. Rename or delete a board from the Board List (delete requires confirmation).
2. Deleting a board cascades to delete its cards/comments/activity.

---

## 4. Real-Time & Multi-User Behavior

- **Transport:** WebSockets (Node/Express + `ws` or `socket.io`).
- **Model:** Each board is a "room." Clients connect and join the room for the board they're viewing.
- **Sync strategy:** Server holds source of truth in a database; on any mutation (card created/edited/moved, comment added), the server persists it, then broadcasts the resulting event to all other clients in that room. Last-write-wins for simultaneous edits to the same field (acceptable for v1 scope).
- **Presence:**
  - On joining a board room, client emits `{ user, boardId }`.
  - Server tracks active users per room and broadcasts the current presence list on join/leave.
  - UI shows avatars of active viewers; optionally shows "X is editing this card" when someone has a card's detail panel open.
- **Reconnection:** On disconnect/reconnect, client re-fetches full board state via REST, then resumes the WebSocket subscription (avoids drift).
- **Conflict handling (v1, kept simple):** No operational-transform/CRDT — mutations are field-level and last-write-wins is acceptable given the small scale.

---

## 5. Suggested Architecture

- **Frontend:** React (Vite), drag-and-drop via `@dnd-kit` or `react-beautiful-dnd`-style library, WebSocket client for real-time sync, REST calls for initial load/board management.
- **Backend:** Node.js + Express for REST endpoints (CRUD on boards/cards/comments) + WebSocket server (`socket.io` recommended for its room support and reconnection handling) for real-time events.
- **Database:** A simple document/relational store is fine at this scale — e.g. SQLite (via Prisma) for simplicity, or Postgres if you want room to grow.
- **Identity:** No auth system; `User` is just `{id, name, color}` generated client-side and passed with every request/socket event.

### Suggested REST endpoints
```
GET    /boards
POST   /boards
GET    /boards/:id
PATCH  /boards/:id
DELETE /boards/:id

POST   /boards/:id/cards
PATCH  /cards/:id
DELETE /cards/:id
POST   /cards/:id/comments
```

### Suggested WebSocket events
```
join_board / leave_board
presence_update

card_created / card_updated / card_moved / card_deleted
comment_added
```

---

## 6. Out of Scope (v1)

- User accounts / authentication / permissions
- Custom or reorderable columns
- Multiple assignees per card
- File attachments
- Notifications/email digests
- Offline support / CRDT-based conflict resolution
- Workspaces/teams (multiple boards is supported, but no org-level grouping)

---

## 7. Open Assumptions to Confirm Later

- Filtering/search bar was added as a reasonable default for usability with real-time collaboration — confirm if wanted for v1.
- Board deletion cascades immediately with no soft-delete/undo — confirm if an "archive" step is preferred instead.
- Last-write-wins conflict resolution is acceptable given the no-auth, small-team scale.
