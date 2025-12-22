from DatabaseManagement import localChzzkDbConnection
from pathlib import Path


if __name__ == "__main__":
    with localChzzkDbConnection() as chzzk_db:
        chzzk_db.execute_sql_script(Path("sql scripts\\table_init.sql"))