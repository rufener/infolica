import pytest

from unittest.mock import patch

from sqlalchemy import create_engine, orm, text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import OperationalError

@pytest.fixture(scope='session')
def config_path():
    return 'testing.ini'

@pytest.fixture(scope='session')
def base_engine(test_db_url):
    base_db_url = URL.create(
        test_db_url.get_backend_name(),
        test_db_url.username,
        test_db_url.password,
        test_db_url.host,
        test_db_url.port,
        database="postgres"
    )
    engine = create_engine(base_db_url)
    yield engine


@pytest.fixture(scope='session')
def stats_db_url(test_db_url):
    base_db_url = URL.create(
        test_db_url.get_backend_name(),
        test_db_url.username,
        test_db_url.password,
        test_db_url.host,
        test_db_url.port,
        database="infolica_stats_test"
    )
    yield base_db_url


@pytest.fixture(scope='session')
def test_db_name(test_db_url):
    yield test_db_url.database


@pytest.fixture(scope='session')
def test_db_url(config_path):
    # TODO read test.ini
    # content = pyaml_env.parse_config(config_path)
    yield make_url('postgresql://user:pwd@localhost:5432/infolica_test')


@pytest.fixture(scope='session')
def test_db_engine(base_engine, test_db_name, config_path):
    """
    create a new test DB called test_db_name and its engine
    """
    with base_engine.begin() as base_connection:
        # terminate existing connections to be able to DROP the DB
        term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE ' \
            f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();'
        base_connection.execute(text(term_stmt))
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"DROP DATABASE if EXISTS {test_db_name}"))
        base_connection.execute(text('COMMIT'))
        base_connection.execute(text(f"CREATE DATABASE {test_db_name}"))

    test_db_url = URL.create(
        base_engine.url.get_backend_name(),
        base_engine.url.username,
        base_engine.url.password,
        base_engine.url.host,
        base_engine.url.port,
        database=test_db_name
    )
    engine = create_engine(test_db_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION POSTGIS"))

    return engine

    # currently there is a problem with teardown of the DB and sessions:
    # DROP DATABASE may be called while a connection is still alive, this may lead to error messages
    # therefore, the DB will temporarily be dropped at the beginning of the test instead of a final
    # cleanup (see above)
    # # do cleanup: disconnect users and DROP DB
    # base_connection.execute('SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE '
    #                         f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();')
    # base_connection.execute('COMMIT')
    # base_connection.execute(f"DROP DATABASE if EXISTS {test_db_name}")


@pytest.fixture(scope='session')
def dbsession(test_db_engine):
    session = orm.sessionmaker(bind=test_db_engine)()
    with patch(
        'pyramid_oereb.core.adapter.DatabaseAdapter.get_session', return_value=session
    ), patch.object(
        session, "close"
    ):
        yield session


@pytest.fixture
def transact(dbsession):
    transact = dbsession.begin_nested()
    yield transact
    transact.rollback()
    dbsession.expire_all()