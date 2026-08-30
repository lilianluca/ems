"""Administrative commands run manually against any environment.

The system has no public registration, so administrator accounts are created
here — both the first one and any added later:

    uv run python -m src.cli create-admin --email admin@example.com \
        --first-name Lilian --last-name Luca

The password is always typed at the prompt rather than passed as an argument,
so it stays out of shell history and out of the process list.
"""

import argparse
import asyncio
import getpass
import logging
import sys

from src.auth.security import hash_password
from src.core.database import SessionLocal, engine
from src.core.logger import setup_logging
from src.users.enums import UserRole
from src.users.repository import UserRepository
from src.users.schemas import MAX_PASSWORD_BYTES, MIN_PASSWORD_LENGTH

setup_logging()
logger = logging.getLogger(__name__)


def read_password() -> str | None:
    """Prompt for the password twice, returning None when the two differ."""
    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Repeat password: "):
        logger.error("Passwords do not match.")
        return None
    return password


async def create_admin(email: str, first_name: str, last_name: str, promote: bool) -> int:
    """Create an administrator, or promote an existing account to one."""
    async with SessionLocal() as session:
        user_repo = UserRepository(session)

        existing = await user_repo.get_by_email(email)
        if existing is not None:
            if not promote:
                logger.error(
                    f"User {email} already exists. Pass --promote to grant the admin role."
                )
                return 1
            existing.role = UserRole.ADMIN
            existing.is_active = True
            await session.commit()
            logger.info(f"✅ Promoted {email} to administrator.")
            return 0

        password = read_password()
        if password is None:
            return 1
        if len(password) < MIN_PASSWORD_LENGTH:
            logger.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            return 1
        if len(password.encode()) > MAX_PASSWORD_BYTES:
            logger.error(f"Password must be at most {MAX_PASSWORD_BYTES} bytes.")
            return 1

        user = await user_repo.create(
            email=email,
            hashed_password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
        )
        await session.commit()
        logger.info(f"✅ Created administrator {email} (id={user.id}).")
        return 0


async def dispatch(args: argparse.Namespace) -> int:
    """Run the selected command and release the database engine afterwards."""
    try:
        return await create_admin(
            email=args.email,
            first_name=args.first_name,
            last_name=args.last_name,
            promote=args.promote,
        )
    finally:
        await engine.dispose()


def main() -> int:
    """Parse arguments and run the requested command."""
    parser = argparse.ArgumentParser(prog="python -m src.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser(
        "create-admin",
        help="Create an administrator account, prompting for the password.",
    )
    create.add_argument("--email", required=True)
    create.add_argument("--first-name", required=True)
    create.add_argument("--last-name", required=True)
    create.add_argument(
        "--promote",
        action="store_true",
        help="Grant the admin role to an existing account instead of failing.",
    )

    return asyncio.run(dispatch(parser.parse_args()))


if __name__ == "__main__":
    sys.exit(main())
