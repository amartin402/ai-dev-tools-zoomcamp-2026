const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8091';

const currentUser = {
  id: 'user-you',
  name: localStorage.getItem('kanbits-user-name') || 'Alex Morgan',
  color: '#d95d39',
};

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const error = await response.json();
      message = error.message || message;
    } catch {
      // Keep the status-based message when the server does not return JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

const json = (method, body) => ({ method, body: JSON.stringify(body) });

export const api = {
  getCurrentUser: () => currentUser,

  saveUserName: async (name) => {
    currentUser.name = name.trim() || 'Alex Morgan';
    localStorage.setItem('kanbits-user-name', currentUser.name);
    return { ...currentUser };
  },

  listBoards: () => request('/boards'),

  getBoard: (boardId) => request(`/boards/${boardId}`),

  createBoard: (name) => request('/boards', json('POST', { name })),

  renameBoard: (boardId, name) => request(`/boards/${boardId}`, json('PATCH', { name })),

  deleteBoard: (boardId) => request(`/boards/${boardId}`, { method: 'DELETE' }),

  createCard: (boardId, columnId, title) => request(
    `/boards/${boardId}/cards`,
    json('POST', { columnId, title }),
  ),

  updateCard: (boardId, cardId, changes) => request(
    `/cards/${cardId}`,
    json('PATCH', { ...changes, actor: currentUser }),
  ),

  moveCard: (boardId, cardId, targetColumnId, targetIndex) => request(
    `/cards/${cardId}`,
    json('PATCH', { columnId: targetColumnId, position: targetIndex, actor: currentUser }),
  ),

  addComment: (boardId, cardId, text) => request(
    `/cards/${cardId}/comments`,
    json('POST', { text, author: currentUser }),
  ),
};
