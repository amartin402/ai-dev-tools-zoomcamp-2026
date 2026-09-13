import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api } from './services/api';
import './styles.css';

const Icon = ({ name, size = 18, stroke = 1.8 }) => {
  const paths = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    more: <><circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="19" cy="12" r="1" fill="currentColor"/></>,
    chevron: <path d="m8 10 4 4 4-4"/>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    calendar: <><rect x="3" y="4.5" width="18" height="17" rx="2"/><path d="M16 2v5M8 2v5M3 10h18"/></>,
    tag: <path d="m20.5 13.5-7 7a2 2 0 0 1-2.8 0l-8.2-8.2V4h8.3l9.7 9.5a2 2 0 0 1 0 2.8ZM7.5 8.5h.01"/>,
    user: <><circle cx="12" cy="8" r="3.5"/><path d="M5 21a7 7 0 0 1 14 0"/></>,
    bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>,
    back: <path d="m15 18-6-6 6-6"/>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    message: <><path d="M20 11.5a7.5 7.5 0 0 1-8 7.5 8.5 8.5 0 0 1-4-.9L4 20l1.8-3.7A7.2 7.2 0 0 1 4 11.5a7.5 7.5 0 0 1 8-7.5 7.5 7.5 0 0 1 8 7.5Z"/></>,
    check: <path d="m5 12 4.5 4.5L19 7"/>,
    filter: <path d="M4 6h16M7 12h10M10 18h4"/>,
    trash: <><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></>,
    edit: <><path d="m4 16.5-.8 4.3 4.3-.8L19 8.5 15.5 5 4 16.5Z"/><path d="m13.5 7 3.5 3.5"/></>,
    activity: <><path d="M4 12h3l2-7 4 14 2-7h5"/></>,
    spark: <><path d="m12 3 1.3 5.7L19 10l-5.7 1.3L12 17l-1.3-5.7L5 10l5.7-1.3L12 3ZM19 17l.5 2.5L22 20l-2.5.5L19 23l-.5-2.5L16 20l2.5-.5L19 17Z"/></>,
  };
  return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
};

const formatRelative = (date) => {
  const diff = Math.max(0, Date.now() - new Date(date).getTime());
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return 'just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
};
const formatDate = (date) => date ? new Date(`${date}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '';
const initials = (name) => name.split(' ').map((word) => word[0]).join('').slice(0, 2).toUpperCase();

function Avatar({ person, small = false }) {
  return <span className={`avatar ${small ? 'avatar-small' : ''}`} style={{ background: person?.color || '#ddd5ca' }} title={person?.name}>{initials(person?.name || '?')}</span>;
}

function App() {
  const [user, setUser] = useState(api.getCurrentUser());
  const [needsName, setNeedsName] = useState(!localStorage.getItem('kanbits-user-name'));
  const [boards, setBoards] = useState([]);
  const [activeBoardId, setActiveBoardId] = useState('board-spring');
  const [board, setBoard] = useState(null);
  const [view, setView] = useState('boards');
  const [selectedCardId, setSelectedCardId] = useState(null);
  const [search, setSearch] = useState('');
  const [assigneeFilter, setAssigneeFilter] = useState('all');
  const [labelFilter, setLabelFilter] = useState('all');
  const [dueFilter, setDueFilter] = useState('all');
  const [draggedCard, setDraggedCard] = useState(null);
  const [modal, setModal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refreshBoards = async () => setBoards(await api.listBoards());
  const refreshBoard = async (id = activeBoardId) => setBoard(await api.getBoard(id));
  useEffect(() => {
    const loadWorkspace = async () => {
      try {
        const items = await api.listBoards();
        setBoards(items);
        if (items[0]) {
          setActiveBoardId(items[0].id);
          setBoard(await api.getBoard(items[0].id));
        }
      } catch (requestError) {
        setError(requestError.message || 'Could not connect to the Kanbits backend.');
      } finally {
        setLoading(false);
      }
    };
    loadWorkspace();
  }, []);
  useEffect(() => { if (view === 'board' && activeBoardId) refreshBoard(activeBoardId); }, [activeBoardId]);

  const selectedCard = board?.cards.find((card) => card.id === selectedCardId);
  const filteredCards = useMemo(() => board?.cards.filter((card) => {
    const needle = search.toLowerCase();
    const matchesSearch = !needle || `${card.title} ${card.description}`.toLowerCase().includes(needle);
    const matchesAssignee = assigneeFilter === 'all' || card.assignee?.id === assigneeFilter;
    const matchesLabel = labelFilter === 'all' || card.labels.some((label) => label.id === labelFilter);
    const matchesDue = dueFilter === 'all' || (dueFilter === 'due' && card.dueDate) || (dueFilter === 'no-date' && !card.dueDate);
    return matchesSearch && matchesAssignee && matchesLabel && matchesDue;
  }) || [], [board, search, assigneeFilter, labelFilter, dueFilter]);

  const openBoard = (id) => { setActiveBoardId(id); setView('board'); setSelectedCardId(null); };
  const goHome = () => { setView('boards'); setSelectedCardId(null); refreshBoards(); };
  const updateCard = async (changes, activity) => { await api.updateCard(board.id, selectedCardId, changes, activity); await refreshBoard(); await refreshBoards(); };
  const createBoard = async (name) => { const created = await api.createBoard(name); await refreshBoards(); openBoard(created.id); setModal(null); };
  const createCard = async (columnId, title) => { const created = await api.createCard(board.id, columnId, title); await refreshBoard(); await refreshBoards(); setSelectedCardId(created.id); };
  const moveCard = async (cardId, targetColumnId, index) => { await api.moveCard(board.id, cardId, targetColumnId, index); await refreshBoard(); await refreshBoards(); setDraggedCard(null); };
  const deleteBoard = async () => { if (window.confirm(`Delete “${board.name}”? This cannot be undone.`)) { await api.deleteBoard(board.id); const next = (await api.listBoards())[0]; await refreshBoards(); if (next) openBoard(next.id); else setView('boards'); setModal(null); } };

  if (loading) return <div className="loading-screen"><div className="brand-mark">k</div><span>Setting up your space...</span></div>;
  if (error) return <div className="loading-screen"><div className="brand-mark">k</div><strong>Kanbits is offline</strong><span>{error}</span><small>Start the backend at http://localhost:8091 and refresh.</small></div>;

  return <div className="app-shell">
    <aside className="sidebar">
      <button className="brand" onClick={goHome}><span className="brand-mark">k</span><span>kanbits</span></button>
      <div className="sidebar-section-label">Workspace</div>
      <nav className="main-nav">
        <button className={view === 'boards' ? 'nav-item active' : 'nav-item'} onClick={goHome}><Icon name="grid" />All boards<span className="nav-count">{boards.length}</span></button>
        <button className="nav-item" onClick={() => setModal({ type: 'new-board' })}><Icon name="plus" />New board</button>
      </nav>
      <div className="sidebar-section-label board-label">Your boards</div>
      <div className="sidebar-boards">{boards.map((item) => <button key={item.id} className={`sidebar-board ${item.id === activeBoardId && view === 'board' ? 'current' : ''}`} onClick={() => openBoard(item.id)}><span className="board-dot" />{item.name}<span className="board-card-count">{item.cardCount}</span></button>)}</div>
      <div className="sidebar-bottom"><div className="presence-note"><span className="online-dot" />Mock mode <span>·</span> local only</div><button className="profile-button" onClick={() => setNeedsName(true)}><Avatar person={user} small /><span><strong>{user.name}</strong><small>Personal workspace</small></span><Icon name="more" size={16} /></button></div>
    </aside>
    <main className="main-content">
      {view === 'boards' ? <BoardList boards={boards} onOpen={openBoard} onNew={() => setModal({ type: 'new-board' })} onRename={(item) => setModal({ type: 'rename-board', board: item })} onDelete={async (item) => { if (window.confirm(`Delete “${item.name}”?`)) { await api.deleteBoard(item.id); refreshBoards(); } }} /> : <BoardView board={board} user={user} cards={filteredCards} search={search} setSearch={setSearch} assigneeFilter={assigneeFilter} setAssigneeFilter={setAssigneeFilter} labelFilter={labelFilter} setLabelFilter={setLabelFilter} dueFilter={dueFilter} setDueFilter={setDueFilter} selectedCardId={selectedCardId} setSelectedCardId={setSelectedCardId} onNewCard={createCard} onMove={moveCard} draggedCard={draggedCard} setDraggedCard={setDraggedCard} onBack={goHome} onRename={() => setModal({ type: 'rename-board', board })} onDelete={deleteBoard} />}
    </main>
    {selectedCard && <CardDrawer card={selectedCard} board={board} user={user} onClose={() => setSelectedCardId(null)} onUpdate={updateCard} onComment={async (text) => { await api.addComment(board.id, selectedCard.id, text); await refreshBoard(); }} />}
    {(needsName || modal) && <Modal type={needsName ? 'name' : modal.type} data={modal} onClose={() => { setNeedsName(false); setModal(null); }} onName={async (name) => { const next = await api.saveUserName(name); setUser({ ...next }); setNeedsName(false); }} onCreate={createBoard} onRename={async (name) => { await api.renameBoard(modal.board.id, name); await refreshBoards(); if (modal.board.id === activeBoardId) refreshBoard(); setModal(null); }} />}
  </div>;
}

function BoardList({ boards, onOpen, onNew, onRename, onDelete }) {
  return <div className="page-wrap board-list-page"><header className="topbar"><div><p className="eyebrow">Your workspace</p><h1>All boards <span className="heading-count">{boards.length}</span></h1></div><div className="top-actions"><button className="icon-button"><Icon name="bell" /></button><button className="button button-primary" onClick={onNew}><Icon name="plus" size={16} />New board</button></div></header><section className="welcome-strip"><div className="welcome-spark"><Icon name="spark" size={21} /></div><div><strong>Make space for good work.</strong><p>A few focused boards are better than a hundred tabs.</p></div><span className="welcome-decoration">✳</span></section><div className="section-heading"><div><h2>Recent boards</h2><p>Pick up where you left off.</p></div><button className="text-button" onClick={onNew}>Create a board <Icon name="arrow" size={15} /></button></div><div className="board-grid">{boards.map((board) => <BoardTile key={board.id} board={board} onOpen={onOpen} onRename={onRename} onDelete={onDelete} />)}<button className="new-board-tile" onClick={onNew}><span className="new-board-icon"><Icon name="plus" /></span><strong>Start a new board</strong><span>Keep a project moving</span></button></div></div>;
}

function BoardTile({ board, onOpen, onRename, onDelete }) {
  const palette = board.name.length % 3;
  return <article className={`board-tile palette-${palette}`} onClick={() => onOpen(board.id)}><div className="tile-top"><span className="tile-symbol">{palette === 0 ? '✳' : palette === 1 ? '◒' : '⌁'}</span><button className="more-button" onClick={(event) => event.stopPropagation()}><Icon name="more" size={17} /></button></div><h3>{board.name}</h3><p className="tile-description">{board.cardCount ? `${board.cardCount} pieces of work in motion` : 'An empty canvas, ready to go'}</p><div className="tile-footer"><span className="tile-meta"><Icon name="grid" size={14} />{board.cardCount} {board.cardCount === 1 ? 'card' : 'cards'}</span><span className="tile-meta">{formatRelative(board.updatedAt)}</span></div><div className="tile-hover-actions"><button onClick={(event) => { event.stopPropagation(); onRename(board); }}><Icon name="edit" size={13} />Rename</button><button onClick={(event) => { event.stopPropagation(); onDelete(board); }}><Icon name="trash" size={13} />Delete</button></div></article>;
}

function BoardView({ board, cards, user, search, setSearch, assigneeFilter, setAssigneeFilter, labelFilter, setLabelFilter, dueFilter, setDueFilter, selectedCardId, setSelectedCardId, onNewCard, onMove, draggedCard, setDraggedCard, onBack, onRename, onDelete }) {
  const [addingTo, setAddingTo] = useState(null);
  const people = [user, { id: 'user-maya', name: 'Maya Chen', color: '#7b61ff' }, { id: 'user-sam', name: 'Sam Rivera', color: '#268f83' }, { id: 'user-jules', name: 'Jules Park', color: '#d59b2b' }];
  const labels = [{ id: 'label-design', name: 'Design', color: '#8267d8' }, { id: 'label-urgent', name: 'Urgent', color: '#d95d39' }, { id: 'label-product', name: 'Product', color: '#2d917d' }, { id: 'label-research', name: 'Research', color: '#d59b2b' }];
  return <div className="page-wrap board-page"><header className="board-topbar"><div className="board-heading"><button className="back-button" onClick={onBack}><Icon name="back" size={19} /></button><div><div className="breadcrumb">Boards <span>/</span> <em>Active board</em></div><div className="board-title-row"><h1>{board.name}</h1><button className="tiny-action" onClick={onRename}><Icon name="edit" size={13} /></button></div></div></div><div className="board-actions"><div className="presence-stack"><Avatar person={people[1]} small /><Avatar person={people[2]} small /><Avatar person={user} small /><span className="presence-plus">+3</span></div><span className="live-status"><i />Live</span><button className="icon-button"><Icon name="bell" /></button><button className="more-button" onClick={onDelete}><Icon name="more" /></button></div></header><div className="board-tools"><div className="search-box"><Icon name="search" size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search cards..." /><kbd>⌘ K</kbd></div><div className="filter-pills"><div className="filter-select"><Icon name="user" size={15} /><select value={assigneeFilter} onChange={(event) => setAssigneeFilter(event.target.value)}><option value="all">Everyone</option>{people.map((person) => <option key={person.id} value={person.id}>{person.name}</option>)}</select></div><div className="filter-select"><Icon name="tag" size={15} /><select value={labelFilter} onChange={(event) => setLabelFilter(event.target.value)}><option value="all">All labels</option>{labels.map((label) => <option key={label.id} value={label.id}>{label.name}</option>)}</select></div><div className="filter-select"><Icon name="calendar" size={15} /><select value={dueFilter} onChange={(event) => setDueFilter(event.target.value)}><option value="all">Any date</option><option value="due">Has a due date</option><option value="no-date">No due date</option></select></div></div><button className="filter-button"><Icon name="filter" size={16} />Filters</button></div><div className="board-caption"><div><p>{board.cards.length} cards <span>·</span> Updated {formatRelative(board.updatedAt)}</p></div><button className="view-toggle active"><Icon name="grid" size={15} />Board view</button></div><div className="kanban-grid">{board.columns.map((column) => { const columnCards = column.cardOrder.map((id) => cards.find((card) => card.id === id)).filter(Boolean); return <Column key={column.id} column={column} cards={columnCards} adding={addingTo === column.id} setAdding={setAddingTo} onNewCard={onNewCard} onSelect={setSelectedCardId} onMove={onMove} draggedCard={draggedCard} setDraggedCard={setDraggedCard} />; })}</div></div>;
}

function Column({ column, cards, adding, setAdding, onNewCard, onSelect, onMove, draggedCard, setDraggedCard }) {
  const [newTitle, setNewTitle] = useState('');
  const submit = async (event) => { event.preventDefault(); if (newTitle.trim()) { await onNewCard(column.id, newTitle); setNewTitle(''); setAdding(null); } };
  return <section className={`kanban-column column-${column.order}`} onDragOver={(event) => event.preventDefault()} onDrop={() => draggedCard && onMove(draggedCard, column.id, cards.length)}><div className="column-header"><div className="column-title"><span className="column-dot" />{column.name}<span className="column-count">{cards.length}</span></div><button className="more-button"><Icon name="more" size={17} /></button></div><div className="cards-list">{cards.map((card, index) => <Card key={card.id} card={card} onSelect={onSelect} onDragStart={() => setDraggedCard(card.id)} onDrop={() => draggedCard && onMove(draggedCard, column.id, index)} isDragging={draggedCard === card.id} />)}{adding ? <form className="quick-add" onSubmit={submit}><input autoFocus value={newTitle} onChange={(event) => setNewTitle(event.target.value)} placeholder="What needs doing?" onKeyDown={(event) => event.key === 'Escape' && setAdding(null)} /><div><button type="button" onClick={() => setAdding(null)}>Cancel</button><button className="quick-submit">Add card</button></div></form> : <button className="add-card" onClick={() => setAdding(column.id)}><Icon name="plus" size={16} />Add card</button>}</div></section>;
}

function Card({ card, onSelect, onDragStart, onDrop, isDragging }) {
  return <article className={`task-card ${isDragging ? 'dragging' : ''}`} draggable onDragStart={onDragStart} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.stopPropagation(); onDrop(); }} onClick={() => onSelect(card.id)}><div className="task-card-head"><span className="task-title">{card.title}</span><button className="card-more" onClick={(event) => event.stopPropagation()}><Icon name="more" size={15} /></button></div>{card.description && <p className="task-description">{card.description}</p>}<div className="task-labels">{card.labels.map((label) => <span key={label.id} className="label-pill" style={{ '--label-color': label.color }}>{label.name}</span>)}</div><div className="task-footer">{card.dueDate ? <span className={`due-date ${new Date(`${card.dueDate}T12:00:00`) < new Date() ? 'overdue' : ''}`}><Icon name="calendar" size={13} />{formatDate(card.dueDate)}</span> : <span />}{card.assignee ? <Avatar person={card.assignee} small /> : <span className="unassigned-avatar"><Icon name="user" size={12} /></span>}</div></article>;
}

function CardDrawer({ card, board, user, onClose, onUpdate, onComment }) {
  const [comment, setComment] = useState('');
  const [editingTitle, setEditingTitle] = useState(false);
  const [title, setTitle] = useState(card.title);
  const [description, setDescription] = useState(card.description);
  const saveTitle = async () => { setEditingTitle(false); if (title.trim() && title !== card.title) await onUpdate({ title: title.trim() }, { type: 'edited', detail: 'updated the title' }); };
  const saveDescription = async () => { if (description !== card.description) await onUpdate({ description }, { type: 'edited', detail: 'updated the description' }); };
  const updateAssignee = async (event) => { const selected = event.target.value; const assignee = selected === 'none' ? null : [user, { id: 'user-maya', name: 'Maya Chen', color: '#7b61ff' }, { id: 'user-sam', name: 'Sam Rivera', color: '#268f83' }, { id: 'user-jules', name: 'Jules Park', color: '#d59b2b' }].find((person) => person.id === selected); await onUpdate({ assignee }, { type: 'assigned', detail: assignee ? `assigned to ${assignee.name}` : 'removed the assignee' }); };
  const updateDate = async (event) => await onUpdate({ dueDate: event.target.value || null }, { type: 'due_date_changed', detail: event.target.value ? `set the due date to ${formatDate(event.target.value)}` : 'removed the due date' });
  const toggleLabel = async (label) => { const next = card.labels.some((item) => item.id === label.id) ? card.labels.filter((item) => item.id !== label.id) : [...card.labels, label]; await onUpdate({ labels: next }, { type: 'label_changed', detail: card.labels.some((item) => item.id === label.id) ? `removed the ${label.name} label` : `added the ${label.name} label` }); };
  const submitComment = async (event) => { event.preventDefault(); if (comment.trim()) { await onComment(comment); setComment(''); } };
  const people = [user, { id: 'user-maya', name: 'Maya Chen', color: '#7b61ff' }, { id: 'user-sam', name: 'Sam Rivera', color: '#268f83' }, { id: 'user-jules', name: 'Jules Park', color: '#d59b2b' }];
  const allLabels = [{ id: 'label-design', name: 'Design', color: '#8267d8' }, { id: 'label-urgent', name: 'Urgent', color: '#d95d39' }, { id: 'label-product', name: 'Product', color: '#2d917d' }, { id: 'label-research', name: 'Research', color: '#d59b2b' }];
  return <aside className="drawer"><div className="drawer-top"><span className="drawer-kicker">{board.columns.find((column) => column.id === card.columnId)?.name}</span><div><button className="icon-button"><Icon name="more" /></button><button className="icon-button" onClick={onClose}><Icon name="close" /></button></div></div><div className="drawer-content"><div className="drawer-title-row">{editingTitle ? <input className="drawer-title-input" value={title} autoFocus onChange={(event) => setTitle(event.target.value)} onBlur={saveTitle} onKeyDown={(event) => event.key === 'Enter' && saveTitle()} /> : <h2 onClick={() => setEditingTitle(true)}>{card.title}</h2>}<button className="edit-title" onClick={() => setEditingTitle(true)}><Icon name="edit" size={15} /></button></div><div className="drawer-fields"><label className="field-label"><span>Assignee</span><div className="field-control person-control"><Avatar person={card.assignee} small /><select value={card.assignee?.id || 'none'} onChange={updateAssignee}><option value="none">Unassigned</option>{people.map((person) => <option key={person.id} value={person.id}>{person.name}</option>)}</select><Icon name="chevron" size={14} /></div></label><label className="field-label"><span>Due date</span><div className="field-control"><Icon name="calendar" size={15} /><input type="date" value={card.dueDate || ''} onChange={updateDate} /></div></label><div className="field-label"><span>Labels</span><div className="label-picker">{allLabels.map((label) => <button key={label.id} className={`selectable-label ${card.labels.some((item) => item.id === label.id) ? 'selected' : ''}`} style={{ '--label-color': label.color }} onClick={() => toggleLabel(label)}><i />{label.name}{card.labels.some((item) => item.id === label.id) && <Icon name="check" size={12} />}</button>)}</div></div></div><div className="drawer-divider" /><section className="drawer-section"><div className="section-label"><Icon name="edit" size={15} />Description</div><textarea className="description-input" value={description} onChange={(event) => setDescription(event.target.value)} onBlur={saveDescription} placeholder="Add a little context..." /></section><section className="drawer-section activity-section"><div className="section-label"><Icon name="activity" size={15} />Activity <span>{card.activityLog.length}</span></div><div className="activity-list">{card.activityLog.slice(0, 5).map((event) => <div className="activity-item" key={event.id}><Avatar person={event.actor} small /><p><strong>{event.actor.name}</strong> {event.detail}<small>{formatRelative(event.timestamp)}</small></p></div>)}</div></section><section className="drawer-section comments-section"><div className="section-label"><Icon name="message" size={15} />Comments <span>{card.comments.length}</span></div>{card.comments.map((item) => <div className="comment" key={item.id}><Avatar person={item.author} small /><div><p>{item.text}</p><small>{item.author.name} · {formatRelative(item.createdAt)}</small></div></div>)}<form className="comment-form" onSubmit={submitComment}><Avatar person={user} small /><input value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Write a comment..." /></form></section></div></aside>;
}

function Modal({ type, data, onClose, onName, onCreate, onRename }) {
  const [value, setValue] = useState(type === 'name' ? '' : data?.board?.name || '');
  const submit = async (event) => { event.preventDefault(); if (!value.trim()) return; if (type === 'name') await onName(value); else if (type === 'new-board') await onCreate(value); else await onRename(value); };
  const isName = type === 'name';
  return <div className="modal-backdrop"><div className={`modal ${isName ? 'welcome-modal' : ''}`}><button className="modal-close" onClick={onClose}><Icon name="close" size={17} /></button>{isName ? <><div className="modal-mark"><Icon name="spark" size={24} /></div><p className="eyebrow">Welcome to kanbits</p><h2>What should we call you?</h2><p className="modal-copy">Your name appears next to your work and helps your team know who's around.</p></> : <><p className="eyebrow">{type === 'new-board' ? 'New board' : 'Board settings'}</p><h2>{type === 'new-board' ? 'Give this project a name' : 'Rename board'}</h2></>}<form onSubmit={submit}><input autoFocus value={value} onChange={(event) => setValue(event.target.value)} placeholder={isName ? 'Your display name' : 'e.g. Product launch'} /><button className="button button-primary" type="submit">{isName ? 'Enter workspace' : type === 'new-board' ? 'Create board' : 'Save changes'}<Icon name="arrow" size={15} /></button></form>{isName && <small className="modal-footnote">No account needed. Your name stays in this browser.</small>}</div></div>;
}

createRoot(document.getElementById('root')).render(<App />);
