import psycopg2
from key_generator import load_public_key
from crypto_utils import encrypt_data


def get_db_connection():
    return psycopg2.connect(
        dbname="dbpostgrado2",
        user="postgres",
        password="1122ffgg",
        host="localhost"
    )


def setup_encryption_for_table(table_name):
    conn = get_db_connection()
    cur = conn.cursor()

    # Get all columns for the table
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s;
    """, (table_name,))
    columns_info = cur.fetchall()
    columns = [row[0] for row in columns_info]
    column_types = {row[0]: row[1] for row in columns_info}

    if not columns:
        cur.close()
        conn.close()
        return

    # Create audit table
    audit_table = f"aud_{table_name}"
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {audit_table} (
            {', '.join([f"{col} BYTEA" for col in columns])}
        );
    """
    cur.execute(create_table_query)

    # Copy and encrypt existing data
    public_key = load_public_key()
    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()
    for row in rows:
        encrypted_row = []
        for col_value in row:
            encrypted_value = encrypt_data(
                col_value, public_key) if col_value is not None else None
            encrypted_row.append(encrypted_value)
        cur.execute(f"""
            INSERT INTO {audit_table} ({', '.join(columns)})
            VALUES ({', '.join(['%s' for _ in columns])})
            ON CONFLICT DO NOTHING;
        """, encrypted_row)

    # Create trigger to copy data to audit table
    trigger_name = f"encrypt_{table_name}_trigger"
    audit_insert = f"""
        INSERT INTO {audit_table} ({', '.join(columns)})
        VALUES ({', '.join([f"NEW.{col}" for col in columns])});
    """
    cur.execute(f"""
        CREATE OR REPLACE FUNCTION audit_{table_name}_trigger()
        RETURNS TRIGGER AS $$
        BEGIN
            {audit_insert}
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    cur.execute(f"""
        DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
        CREATE TRIGGER {trigger_name}
        AFTER INSERT OR UPDATE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION audit_{table_name}_trigger();
    """)

    conn.commit()
    cur.close()
    conn.close()
