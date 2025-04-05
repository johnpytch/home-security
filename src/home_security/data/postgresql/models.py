from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Uuid,
    SmallInteger,
    DECIMAL,
    Text,
    Boolean,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Household(Base):
    __tablename__ = "household"

    id = Column(Integer(), primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    cameras = relationship("Camera", backref="household")

    def __repr__(self):
        return f"<Household(id={self.id}, name={self.name})>"


class Camera(Base):
    __tablename__ = "camera"
    id = Column(Text(), primary_key=True)
    household_id = Column(Integer(), ForeignKey("household.id"))
    caption = Column(String(20), nullable=True)
    image_sets = relationship("ImageSet", backref="camera")


class ImageSet(Base):
    __tablename__ = "imageset"
    id = Column(Integer(), primary_key=True)
    received_date = Column(DateTime(timezone=True), nullable=False)
    camera_id = Column(String(5), ForeignKey("camera.id"))
    inferenced = Column(Boolean, nullable=False, default=False)
    intrusion_images = relationship("IntrusionImage", backref="imageset")

    @property
    def pretty_date(self) -> str:
        day = self.received_date.day
        if 11 <= day <= 13:
            ordinal = "th"
        else:
            last_digit = day % 10
            if last_digit == 1:
                ordinal = "st"
            elif last_digit == 2:
                ordinal = "nd"
            elif last_digit == 3:
                ordinal = "rd"
            else:
                ordinal = "th"
        return self.received_date.strftime(format=f"At %H:%M on %A %d{ordinal} %B, %Y")


class IntrusionImage(Base):
    __tablename__ = "image"
    id = Column(Uuid(as_uuid=True), primary_key=True)
    imageset_id = Column(Integer(), ForeignKey("imageset.id"))
    detections = relationship("Detection", backref="image")


class Detection(Base):
    __tablename__ = "detection"
    id = Column(Integer(), primary_key=True)
    image_id = Column(Uuid(as_uuid=True), ForeignKey("image.id"))
    label = Column(
        String(10), nullable=False
    )  # My labels won't be more than 10 characters - eg: 'person'
    confidence = Column(SmallInteger(), nullable=False)  # Can only be from 1 to 100
    x_min = Column(DECIMAL(precision=5, scale=2))  # EG: 135.23 ??
    y_min = Column(DECIMAL(precision=5, scale=2))  # EG: 135.26 ??
    x_max = Column(DECIMAL(precision=5, scale=2))  # EG: 135.36 ??
    y_max = Column(DECIMAL(precision=5, scale=2))  # EG: 135.26 ??
