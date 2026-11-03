# Architecture

React and Tiptap manage the editor. Content is stored as Tiptap JSON so marks, headings, and lists survive reloads. Edits are debounced for 650 ms and sent to `PATCH /documents/{id}`. FastAPI validates input; SQLAlchemy persists records in PostgreSQL. `DATABASE_URL` can select SQLite for local smoke tests.

## Database

`users(id, name)` contains seeded Alice and Bob. `documents(id, owner_id, title, content JSON, updated_at)` holds documents. `shares(document_id, user_id)` grants recipient read access. Owners can edit, share, and delete. The API checks permissions for every document operation.

## API

`GET /users`, `GET /documents`, `POST /documents`, `GET/PATCH/DELETE /documents/{id}`, `POST /documents/{id}/share`, `POST /documents/import`, `GET /health`. Requests identify a demo user with `X-User-Id`. Validation errors use HTTP 422; oversize uploads use 413; forbidden access uses 403.

## Decisions and tradeoffs

The demo header is intentionally simple for the assignment and provides no security against impersonation. Sharing is read-only. Markdown import preserves line content and heading levels, but does not parse full Markdown syntax. Tables are created on startup for a small MVP; production schema changes would need migrations. Autosave uses a client debounce and has no conflict resolution for concurrent edits.
