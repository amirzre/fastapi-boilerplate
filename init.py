from alembic import command
from alembic.config import Config


def run_migration():
    """Run Alembic migrations to upgrade the database to head."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migration()
