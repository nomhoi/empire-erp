import pytest_postgresql.factories.client
import pytest_postgresql.factories.noprocess
from pytest_postgresql.compat import connection

postgresql_my_proc = pytest_postgresql.factories.noprocess.postgresql_noproc(
    dbname="empire-erp-2", load=["./step1.sql"]
)
postgres = pytest_postgresql.factories.client.postgresql(
    "postgresql_my_proc", dbname="empire-erp-2"
)

def test_1(postgres: connection) -> None:
    # with postgres.cursor() as cur:
    #     cur.execute("SELECT * FROM general_journal ORDER BY id;")
    #     res = cur.fetchall()
    #     # assert len(res) == 3
    pass