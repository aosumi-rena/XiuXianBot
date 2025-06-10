# Editing the SQLite Database
*// Documents will be moved into wiki in future?*  
The bot stores data in `data/xiu_xian.db` by default. If the file does not yet
exist it will be created on first run. You can inspect or modify it using the
`sqlite3` CLI that ships with Python.

```bash
# open the database file
python -m sqlite3 data/xiu_xian.db
```

Once inside the prompt you can run SQL statements. For example, to remove a
user with a specific UID:

```sql
DELETE FROM users WHERE user_id = '1234567';
```

Type `.tables` to list tables and `.schema users` to show the structure.
Exit the shell with `.quit`.

Be sure to stop the bot while editing to avoid file locks or corrupted data.
