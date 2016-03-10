"""Functions to store index in a mysql database"""

import sqlite3
from util import readconfig

config = readconfig()
DB_DATABASE = config.get('default', 'DB_DATABASE')

def index_createdb():

    conn = sqlite3.connect(DB_DATABASE)

def index_connect():
    """Connect to the database"""

    conn = sqlite3.connect(DB_DATABASE)

    return conn

def index_create_tables(conn):
    """Create the required tables for the index"""

    sql = """
CREATE TABLE IF NOT EXISTS documents (
   id INT unique primary key,
   offset BIGINT,
   length INT,
   document VARCHAR(100)
)"""

    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute(sql)
    conn.commit()


def index_insert(cursor, id, offset, length, document):
    """Add an entry, does not commit"""

    # update if the id is already present, otherwise insert

    cursor.execute("SELECT id FROM documents WHERE id=?", (id,))

    if cursor.fetchone():
        sql = """UPDATE documents
        SET  offset=?, length=?, document=?
        WHERE id=?"""

        cursor.execute(sql, (offset, length, document, id))
    else:
        sql = """INSERT INTO documents (id, offset, length, document)
                 VALUES (?, ?, ?, ?)"""

        cursor.execute(sql, (id, offset, length, document))



def index_get(conn, id):
    """Get data for a document id, return a tuple
    of (offset, length, document)"""

    sql = """SELECT offset, length, document FROM documents WHERE id=?"""

    cursor = conn.cursor()
    cursor.execute(sql, (id,))

    result = cursor.fetchone()
    return result


def index_documents(conn):
    """Return an iterator over documents returning an
    iterator over the id of each document"""

    sql = """SELECT id FROM documents"""

    cursor = conn.cursor()
    cursor.execute(sql)

    for row in cursor:
        yield row[0]


if __name__=='__main__':

    print "Creating database and tables..."
    index_createdb()
    conn = index_connect()
    index_create_tables(conn)
    print "...Done"
