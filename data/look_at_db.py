import sqlite3
from typing import List, Optional, Any

def get_data_from_table(table_name: str) -> List[tuple[Any]]:
    with sqlite3.connect('kilovatt_market.db') as conn:
        cursor = conn.cursor()
        data = cursor.execute(
            f'SELECT * from {table_name}'
        ).fetchmany()

        return data

def delete_all_from_table(table_name: str):
    with sqlite3.connect('kilovatt_market.db') as conn:
        cursor = conn.cursor()
        data = cursor.execute(
            f'DELETE from {table_name}')

        return data

if __name__ == "__main__":
    print(get_data_from_table('clients'))
    # print(delete_all_from_table('clients'))
    print(get_data_from_table('clients'))