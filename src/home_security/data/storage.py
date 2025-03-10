from typing import List, Tuple
from PIL import Image
from datetime import datetime
import uuid
import logging
logger = logging.getLogger()

from home_security.data.postgresql.models import Household, Camera, ImageSet, IntrusionImage
from home_security.data.minio.minio_client import Minio


class StorageDriver:
    def __init__(self, minio: Minio, session):
        self.minio = minio
        self.session = session
    
    def add_image_set(self, images: List[Image.Image], camera_id, datetime_str):
        datetime_obj = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
        match camera_id[0]:
            case 'D':
                household_name='denning'
            case 'A':
                household_name = 'rectory'
            case _:
                raise Exception(f'Household code not found for camera id {camera_id}')
        logger.info(f'Adding new images for camera {camera_id}')

        household_id = self.session.query(Household).filter(Household.name == household_name).all()[0].id
        if not self.session.get(Camera, camera_id):
            logger.info(f'New camera feed detected at {household_name}, adding {camera_id} to DB!')
            new_camera = Camera(id=camera_id, household_id=household_id)
            self.session.add(new_camera)
            self.session.commit()
        else:
            logger.info(f'Got new images for camera {camera_id} at household {household_name}')
        
        imgset = ImageSet(received_date=datetime_obj, camera_id=camera_id, inferenced=False)
        self.session.add(imgset)
        self.session.commit()

        # Add each image to IntrusionImage table and minio bucket
        for image in images:
            image_uuid = uuid.uuid4()
            image_value = IntrusionImage(imageset_id=imgset.id, id=image_uuid)
            self.session.add(image_value)
            self.session.commit()
            self.minio.add_image(image=image, image_uuid=str(image_uuid), bucket_name='intrusionimages')
            logger.info(f'added image {image_value.id}, of set {image_value.imageset_id}')
    
    def get_uninferenced_image_sets(self) -> List[int]:
        uninferenced_set_ids = self.session.query(ImageSet).with_entities(ImageSet.id).filter(ImageSet.inferenced == False).all()
        return [id[0] for id in uninferenced_set_ids]
    
    #def get_image_set(self, image_set_id: int) -> Tuple[List[Image.Image], ]