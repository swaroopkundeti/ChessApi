import uuid

from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint


def generate_uuid():
    an_id = uuid.uuid4()
    print("id created is: " + str(an_id))
    return an_id


def db_drop_everything(database):
    # From http://www.mbeckler.org/blog/?p=218
    # and http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything

    conn = database.engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(database.engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    conn.execute('DROP VIEW IF EXISTS most_recent_inspection;')

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()
    conn.close()
