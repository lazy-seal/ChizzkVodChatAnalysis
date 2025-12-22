from DatabaseManagement import localChzzkDbConnection


if __name__ == "__main__":
    with localChzzkDbConnection() as chzzk_db:
        chzzk_db.execute_sql_statement("DROP TABLE IF EXISTS chats, videos, users CASCADE;")