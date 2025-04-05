from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError

from home_security.data.postgresql.models import Base, Household, Camera
from home_security.settings import settings


engine = create_engine(
    url=URL.create(
        drivername="postgresql",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    )
)

# Create a session
Session = sessionmaker(bind=engine)


def get_session():
    return Session()


def create_tables():
    Base.metadata.create_all(engine)


def seed_db():
    session = get_session()
    # Check if required households exist already
    households = [Household(name="denning"), Household(name="rectory")]
    cameras = [
        Camera(id="D01", household_id=1, caption="front drive"),
        Camera(id="D02", household_id=1, caption="front door"),
        Camera(id="D03", household_id=1, caption="side gate"),
        Camera(id="D04", household_id=1, caption="back garden"),
        Camera(id="A03", household_id=2, caption="garage back door"),
        Camera(id="A05", household_id=2, caption="back garden"),
    ]
    session.add_all(households)
    session.add_all(cameras)
    try:
        session.commit()
    except IntegrityError:
        # Idempotence :)
        session.rollback()
