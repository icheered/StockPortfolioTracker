from rethinkdb import RethinkDB
from rethinkdb.errors import RqlRuntimeError, RqlDriverError, ReqlRuntimeError

r =  RethinkDB()

DB_ADDRESS = "0.0.0.0"
DB_PORT = 28015
DB_NAME = "TESTING"
try: 
    connection = r.connect(host=DB_ADDRESS, port=DB_PORT)
    r.db_create(DB_NAME).run(connection)
except ReqlRuntimeError:
   print("Database already exists")

conn = r.connect(
    host=DB_ADDRESS, 
    port=DB_PORT, 
    db=DB_NAME,
)

tables = r.db(DB_NAME).table_list().run(conn)

TABLENAME = "test"
if TABLENAME not in tables:
    r.db(DB_NAME).table_create(TABLENAME).run(conn)


datapoint = {
    "exch": {}
}
# ret_cursor = r.table(TABLENAME).insert(datapoint).run(conn)
# print(ret_cursor)

# print("Before")
# ret_cursor = r.table(TABLENAME).run(conn)
# print(ret_cursor)

ret_cursor = r.\
    table(TABLENAME).\
    filter(r.row["Date"] == "26-04-2021").\
    update({"EXCHRATES": 
        {
            "usd": 2,
            "eur": 1
        }
    }).\
    run(conn)
print(ret_cursor)

print("After")
ret_cursor = r.table(TABLENAME).run(conn)
print(ret_cursor)



# ret_cursor = r.\
#     table(TABLENAME).\
#     delete().\
#     run(conn)
# print(ret_cursor)