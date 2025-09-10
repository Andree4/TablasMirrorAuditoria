from flask import Flask, request, render_template
from db_utils import get_db_connection, setup_encryption_for_table
from key_generator import load_private_key
from crypto_utils import decrypt_data
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get all tables (excluding audit tables)
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name NOT LIKE 'aud_%';
    """)
    tables = [row[0] for row in cur.fetchall()]

    # Get audit tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE 'aud_%';
    """)
    audit_tables = [row[0] for row in cur.fetchall()]

    # Handle encryption request
    encrypt_table = request.form.get('encrypt_table')
    if encrypt_table:
        setup_encryption_for_table(encrypt_table)
        audit_tables.append(f"aud_{encrypt_table}")

    # Handle table viewing
    selected_table = request.form.get('view_table', '')
    private_key_pem = request.form.get('private_key', '')
    table_data = []
    columns = []

    if selected_table:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s;
        """, (selected_table,))
        columns_info = cur.fetchall()
        columns = [row[0] for row in columns_info]
        column_types = {row[0]: row[1] for row in columns_info}

        cur.execute(f"SELECT * FROM {selected_table};")
        rows = cur.fetchall()

        private_key = load_private_key(
            private_key_pem) if private_key_pem else None

        for row in rows:
            decrypted_row = []
            for i, col in enumerate(row):
                if selected_table.startswith('aud_') and column_types[columns[i]] == 'bytea' and private_key:
                    decrypted_row.append(decrypt_data(col, private_key))
                else:
                    decrypted_row.append(col)
            table_data.append(decrypted_row)

    cur.close()
    conn.close()

    return render_template('index.html', tables=tables, audit_tables=audit_tables,
                           selected_table=selected_table, columns=columns, table_data=table_data)


if __name__ == '__main__':
    from key_generator import generate_rsa_keys

    if not os.path.exists('keys/private_key.pem') or not os.path.exists('keys/public_key.pem'):
        generate_rsa_keys()

    app.run(debug=True)
