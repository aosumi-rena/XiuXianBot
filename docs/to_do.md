# To Do List

### Phase 1: Database Migration to SQLite (Completed)
- [X] Define SQLite schema (users, items, timers, indexes)
- [X] Write migration script: `scripts/mongo_to_sqlite.py`
- [X] Update Python data access to use `sqlite3` with transactions
- [X] Test all features under SQLite
- [X] Enable WAL mode or queue writes for concurrency
- [X] Add localization storage (`preferred_lang` or `language_prefs.json`)
- [X] Update config to use `"sqlite_path"` and update docs

### Phase 2: Develop the C# Core Server
- [x] Initialize ASP.NET Core Web API project in `Server/`
- [x] Configure `Program.cs` (port 11450, DI)
- [x] Create data layer (`Database.cs`) using Microsoft.Data.Sqlite or Dapper
- [x] Define RESTful API endpoints for all bot commands
- [x] Port Python core logic to C# services (e.g., `CultivationService`)
- [x] Define data models (`Player`, `Item`, etc.)
- [x] Implement timing logic (passive, compute on stop)
- [x] Load config/assets from JSON (item stats, textmaps)
- [x] Require `API_SECRET` header for all requests
- [x] Bind server to localhost in Docker; secure admin endpoints
- [ ] Write multi-stage Dockerfile for core server
- [ ] Add `docker-compose.yml` for all services
- [x] Share volumes for config and database
- [x] Use environment variables for tokens/secrets
- [ ] Write unit tests for core logic
- [ ] Test API manually (Postman/curl)
- [ ] Compare outputs with legacy Python core

### Phase 2.5: Migrate Local Admin Dashboard to Node.js Web App
- [ ] Set up a new Node.js web app project for the admin dashboard
- [ ] Choose and scaffold frontend framework (SvelteKit or React/Next.js)
- [ ] Implement UI with Tailwind CSS and component library (e.g. daisyUI)
- [ ] Reimplement all dashboard features:
  - [ ] Config management page (view/edit config.json, trigger reload)
  - [ ] Service control (start/stop core and adapters, status indicators)
  - [ ] Admin tools (rebuild indexes, adjust player data, etc.)
  - [ ] Logs viewer (real-time, filtering, download)
  - [ ] Database/accounts browser (query users, inventories, ban/unban, linking)
- [ ] Integrate frontend with C# core server via REST API (use API_SECRET)
- [ ] Add admin endpoints to core server if needed for process control
- [ ] Ensure database queries go through core admin API or read-only SQLite
- [ ] Dockerize the Node.js app:
  - [ ] Option 1: Multi-stage Dockerfile for single-container deployment
  - [ ] Option 2: Separate container in docker-compose (default port 11451)
- [ ] Ensure dashboard auto-starts and is accessible at http://localhost:11451
- [ ] Apply security: restrict to localhost, use API_SECRET for sensitive actions
- [ ] Enhance UI/UX:
  - [ ] Navigation bar for sections
  - [ ] Real-time features (WebSockets/SSE for logs)
  - [ ] Multilingual/i18n support
  - [ ] Random anime background and tooltips/help text

### Phase 3: Adapter Integration & Communication
- [ ] Update Python adapters to use HTTP API (replace direct imports)
- [ ] Handle API responses and errors in adapters
- [ ] Include `API_SECRET` in adapter requests
- [ ] Update admin dashboard for new service control and config management
- [ ] Update data views to use core admin APIs or read-only SQLite
- [ ] Expose logs via shared volume or core endpoint
- [ ] Update UI text for client-server model

### Phase 4: Testing, Optimization, and Hot-Reload
- [ ] Write integration tests for full stack (`docker-compose up`)
- [ ] Tune performance (thread pool, SQL, pagination)
- [ ] Implement `/api/admin/reload-config` endpoint
- [ ] Add failure recovery (adapters retry, user messages)
- [ ] Document path for DB migration to Postgres and horizontal scaling

### Phase 5: Documentation & Release Updates
- [ ] Update/create `docs/core_update_plan.md`
- [ ] Update/create `docs/architecture.md` (diagram + explanation)
- [ ] Update/create `docs/deployment.md`
- [ ] Update `README.md` for new architecture and roadmap
- [ ] Sync localized READMEs (`README_CHS.md`, `README_CHT.md`, `README_JPN.md`)
- [ ] Update `TODO.md` (remove completed, add new items)
- [ ] Update contributors/acknowledgments

### Phase 6: Future Enhancements
- [ ] Public web portal (account linking, stats)
- [ ] Matrix adapter (matrix-nio)
- [ ] DB migration to Postgres
- [ ] Monitoring endpoints and profiling
- [ ] Deprecate/archive Python core
- [ ] Explore embedded scripting (Lua)
