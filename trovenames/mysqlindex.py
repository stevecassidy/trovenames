"""Functions to store index in a mysql database"""

import MySQLdb
from util import readconfig

config = readconfig()
DB_USER = config.get('default', 'DB_USER')
DB_PASS = config.get('default', 'DB_PASS')
DB_DATABASE = config.get('default', 'DB_DATABASE')

# mysqladmin -u root -p  create trovenames

def index_createdb():

    conn = MySQLdb.connect(user=DB_USER, passwd=DB_PASS)
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS ' + DB_DATABASE)


def index_connect():
    """Connect to the database"""

    conn = MySQLdb.connect(user=DB_USER, passwd=DB_PASS, db=DB_DATABASE)

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

    cursor.execute("SELECT id FROM documents WHERE id=%s", (id,))

    if cursor.fetchone():
        sql = """UPDATE documents
        SET  offset=%s, length=%s, document=%s
        WHERE id=%s"""
        
        cursor.execute(sql, (offset, length, document, id))
    else:
        sql = """INSERT INTO documents (id, offset, length, document)
                 VALUES (%s, %s, %s, %s)"""

        cursor.execute(sql, (id, offset, length, document))



def index_get(conn, id):
    """Get data for a document id, return a tuple
    of (offset, length, document)"""

    sql = """SELECT offset, length, document FROM documents WHERE id=%s"""

    cursor = conn.cursor()
    cursor.execute(sql, (id,))

    result = cursor.fetchone()
    return result


if __name__=='__main__':

    print "Creating database and tables..."
    index_createdb()
    conn = index_connect()
    index_create_tables(conn)
    print "...Done"
