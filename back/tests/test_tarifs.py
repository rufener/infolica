import pytest

def test_missing_configuration_file(test_db_engine):
    print("Testing with settings from testing.ini")
    print("Using test database URL:", test_db_engine.url)
