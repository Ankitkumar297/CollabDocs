# Submission

Delivered: document CRUD, rich text formatting and persistence, text/Markdown import, demo user switching, read-only sharing, backend permission checks, responsive dashboard and editor, API tests, deployment configuration, and setup documentation.

Test results: `py -3.12 -m pytest -q` passed 3 tests (2 FastAPI deprecation warnings). `npm run lint` passed. `npm run build` passed with a bundle-size warning. A headless Chrome local smoke test passed create, rename, formatting, autosave, refresh/reopen, `.txt` and `.md` imports, invalid upload error, Alice-to-Bob sharing, Bob read-only view and rejected edit/delete, owner deletion, and mobile sidebar/overflow checks. Browser console had no unexpected errors after fixes. PostgreSQL hosting and deployment were not tested.

Known limitations: Demo user switching is not authentication. Sharing is read-only. Markdown import handles headings and plain lines, not complete Markdown syntax. No concurrent edit conflict handling or migrations.

Live URL: pending deployment; see `LIVE_URL.txt`.

Walkthrough: pending manual recording; see `VIDEO_LINK.txt`.
