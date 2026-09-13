# Kanbits

Kanbits is a lightweight, real-time collaborative Kanban board. Users can create boards, manage cards across fixed workflow columns, and collaborate with other viewers without accounts.

Product behavior and technical requirements are documented in [`_docs/specs.md`](_docs/specs.md).

The backend uses SQLite by default and reads the database connection string from
`DATABASE_URL`. For example, `DATABASE_URL=sqlite:///./kanbits.db` or a
PostgreSQL SQLAlchemy URL can be used when deploying the backend.
