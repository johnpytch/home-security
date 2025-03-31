from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from sqlalchemy.engine import URL
from home_security.data.postgresql.models import Base, Household


# Load env json
# TODO: Start using .env files like a normal person xD
with open("../env.json", "r") as file:
    env_json = json.load(file)
DATABASE = env_json["POSTGRESQL"]
# Create an engine
user = DATABASE["USER"]
password = DATABASE["PASSWORD"]
host = DATABASE["HOST"]
port = int(DATABASE["PORT"])
db = DATABASE["DB"]

engine = create_engine(
    url=URL.create(
        drivername="postgresql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=db,
    )
)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a base class for declarative models
def get_session():
    return Session()


def create_tables():
    Base.metadata.create_all(engine)


def seed_db():
    session = get_session()
    households = [Household(name="denning"), Household(name="rectory")]
    session.add_all(households)
    session.commit()
