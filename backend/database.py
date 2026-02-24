"""Neo4j database connection and session management."""
from contextlib import contextmanager
from typing import Generator

from neo4j import GraphDatabase, Driver
from backend.config import get_settings


class Neo4jDriver:
    """Neo4j driver singleton with connection lifecycle."""

    _driver: Driver | None = None

    @classmethod
    def get_driver(cls) -> Driver:
        settings = get_settings()
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return cls._driver

    @classmethod
    def close(cls) -> None:
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None


@contextmanager
def get_neo4j_session() -> Generator:
    """Neo4j 세션 컨텍스트 매니저."""
    driver = Neo4jDriver.get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def verify_connection() -> bool:
    """Neo4j 연결 확인."""
    try:
        with get_neo4j_session() as session:
            session.run("RETURN 1")
        return True
    except Exception:
        return False
