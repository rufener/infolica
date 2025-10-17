import pytest
from alembic.config import Config
from alembic import command

from pyramid.paster import get_appsettings, setup_logging
from configparser import ConfigParser
from sqlalchemy import create_engine, orm, text
from sqlalchemy.engine.url import make_url

@pytest.fixture(scope='session')
def settings():
    ini_path = 'development.ini'
    setup_logging(ini_path)
    app_settings = get_appsettings(ini_path)
    parser = ConfigParser()
    parser.read(ini_path)
    # override with [testing] section
    for key, value in parser.items('testing'):
        app_settings[key] = value
    return app_settings

@pytest.fixture(scope='session')
def test_db_url(settings):
    yield make_url(settings['sqlalchemy.url'])

@pytest.fixture(scope='session')
def test_db_name(test_db_url):
    yield test_db_url.database

@pytest.fixture(scope='session')
def test_db_engine(settings, test_db_name, test_db_url):
    admin_url = test_db_url.__copy__().set(database='postgres')
    admin_engine = create_engine(admin_url, isolation_level='AUTOCOMMIT')

    # Terminate sessions and drop test database if it exists
    with admin_engine.connect() as conn:
        term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE ' \
            f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();'
        conn.execute(text(term_stmt))
        conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        conn.execute(text(f"CREATE DATABASE {test_db_name}"))
    admin_engine.dispose()

    engine = create_engine(test_db_url, isolation_level='AUTOCOMMIT')
    with engine.connect() as conn:
        conn.execute(text(f"CREATE EXTENSION POSTGIS"))
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS infolica"))
    engine.dispose()

    alembic_cfg = Config('development.ini', ini_section='alembic')
    alembic_cfg.set_main_option('sqlalchemy.url', settings['sqlalchemy.url'])
    command.upgrade(alembic_cfg, 'head')

    engine = create_engine(test_db_url, isolation_level='AUTOCOMMIT')
    yield engine
    engine.dispose()

    if settings.get('preserve_test_db', 'false').lower() != 'true':
        # Cleanup: drop the test database
        admin_engine = create_engine(admin_url, isolation_level='AUTOCOMMIT')
        with admin_engine.connect() as conn:
            term_stmt = 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE ' \
                f'pg_stat_activity.datname = \'{test_db_name}\' AND pid <> pg_backend_pid();'
            conn.execute(text(term_stmt))
            conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        admin_engine.dispose()

@pytest.fixture(scope='session')
def session_factory(test_db_engine):
    return orm.sessionmaker(bind=test_db_engine)
