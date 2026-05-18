import os
import logging
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .exceptions import DatabaseConnectionError
from typing import Any

logger = logging.getLogger(__name__)


def connect(
    host: str | None = None,
    port: str | None = None,
    user: str | None = None,
    password: str | None = None,
    db_name: str | None = None,
    timeout_ms: int = 2000,
) -> tuple[MongoClient, Database]:
    """
    Crea un client MongoDB e restituisce (client, database).

    Il database viene creato automaticamente al primo inserimento
    se non esiste ancora (comportamento standard di MongoDB).

    Solleva:
        DatabaseConnectionError – server irraggiungibile
    """
    host = host or os.environ.get("DB_HOST", "localhost")
    port = port or os.environ.get("DB_PORT", "27017")
    user = user or os.environ.get("DB_USER", "")
    password = password or os.environ.get("DB_PASSWORD", "")
    db_name = db_name or os.environ.get("DB_NAME", "mvp_db")

    uri = f"mongodb://{user}:{password}@{host}:{port}/"
    client: MongoClient[dict[str, Any]] = MongoClient(
        uri,
        serverSelectionTimeoutMS=timeout_ms,
        connectTimeoutMS=timeout_ms,
    )

    try:
        client.admin.command("ping")
        logger.info(f"Connesso a MongoDB su {host}:{port}")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseConnectionError(
            f"Impossibile connettersi a MongoDB su {host}:{port} — {e}"
        ) from e

    return client, client[db_name]
