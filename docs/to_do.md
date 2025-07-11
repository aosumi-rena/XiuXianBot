# Core Update TODO Schedule

**Plan generated by AI**  

The timeline begins on **9 June 2025**. Each day lists concrete steps needed to reach a working SQLite database and Java server.

## 9 June
- Set up Python's `sqlite3` dependency.
- Update `config.json` with the `db.sqlite_path` value.
- Implement connection factory in `core/database/connection.py`.
- Create `data/language_prefs.json` and helpers in `core/utils/lang_file.py` to store user language. The JSON keeps separate objects per platform (`discord`, `telegram`). Adapters read this file and offer a `/lang` command.

## 10 June
- Define table schemas for `users`, `items`, and `timings`.
- Add automatic table creation logic on startup.
- Write basic CRUD helpers for user and item operations.

## 11 June
- Replace MongoDB queries across modules with SQLite equivalents.
- Start updating `core/server.py` to use the new helpers.

## 12 June
- Create `scripts/mongo_to_sqlite.py` for migrating existing data.
- Test data migration on a sample database.

## 13 June
- Modify admin utilities and `web_local/app.py` for SQLite.
- Remove MongoDB packages from `requirements.txt`.

## 14 June
- Run Python unit tests and fix any failures.
- Clean up configuration files and documentation.

## 15 June
- Scaffold Java 21 project inside `Server/`.
- Add initial files `Main.java` and database helper classes.

## 16 June
- Implement endpoints `/health`, `/api/user/lookup`, and `/api/register`.

## 17 June
- Add cultivation endpoints `/api/cultivate/start` and `/api/cultivate/stop`.

## 18 June
- Implement `/api/stat/{user_id}` and replicate remaining Python routes.

## 19 June
- Port game logic modules or set up a bridge to the existing Python code.
- Verify adapters can communicate with the Java server.

## 20 June
- Prepare Docker configuration to run the Java service alongside adapters.
- Execute integration tests covering common flows.

## 21 June
- Finalize documentation and remove the old Python server from production.

## 22 June
- Begin developing new game features on the upgraded platform.
