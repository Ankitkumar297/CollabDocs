# Submission

Delivered: document CRUD, rich text formatting and persistence, text/Markdown import, demo user switching, read-only sharing, backend permission checks, responsive dashboard and editor, API tests, deployment configuration, and setup documentation.

Test results: `py -3.12 -m pytest -q` passed 3 tests (2 FastAPI deprecation warnings). `npm run lint` passed. `npm run build` passed with a bundle-size warning. A headless Chrome local smoke test passed create, rename, formatting, autosave, refresh/reopen, `.txt` and `.md` imports, invalid upload error, Alice-to-Bob sharing, Bob read-only view and rejected edit/delete, owner deletion, and mobile sidebar/overflow checks. On November 3, 2026, production `/health` and `/users` returned 200, CORS preflight from the Vercel origin returned 200, and production API tests passed create, save/reopen of Tiptap JSON, Alice-to-Bob sharing, recipient listing, and rejection of Bob edits/deletes. A headless Chrome production test passed create, autosave, refresh/reopen, sharing, Bob read-only view, and cleanup with no console errors. Neon SQL access and persistence across a Render restart were not independently tested.

Known limitations: Demo user switching is not authentication. Sharing is read-only. Markdown import handles headings and plain lines, not complete Markdown syntax. No concurrent edit conflict handling or migrations.

- Live frontend: https://collabdocs-ankit.vercel.app
- Live backend: https://collabdocs-api-00bk.onrender.com
- GitHub: https://github.com/Ankitkumar297/CollabDocs

Walkthrough: pending manual recording; see `VIDEO_LINK.txt`.
