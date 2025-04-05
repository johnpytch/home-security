import logging
from PIL import Image
from io import BytesIO
import minio


class Minio:
    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        """Create minio client object

        Args:
            endpoint (str): The Minio container url
            access_key (str): The minio access key (username)
            secret_key (str): The minio secret key (password)
        """

        self.logger = logging.getLogger(name="Minio-client")
        self.minio_client = minio.Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

        self.logger.info(f"Successfully connected to Minio client")

    def add_image(self, image: Image, bucket_name: str, image_uuid: str) -> None:
        """Adds an image to a Minio bucket

        Args:
            image (PIL.Image): The image to upload.
            bucket_name (str): The name of the bucket, it not exists, one will be created.
            image_uuid (str): The unique identifier for the image. Should be a stringified uuid.uuid4()

        Raises:
            Exception: Cannot add image to minio bucket.
        """

        self._create_bucket_if_not_exists(bucket_name)
        # Convert PIL Image to bytes and generate UUID
        image_bytes = self._image_to_bytes(image=image)

        try:
            # Store it in minio
            self.minio_client.put_object(
                bucket_name=bucket_name,
                object_name=image_uuid,
                data=image_bytes,
                length=image_bytes.getbuffer().nbytes,
                content_type="image/jpeg",
            )

        except Exception as e:
            raise Exception(
                f"Could not add image {image_uuid} to {bucket_name}, likely due to a connectivity problem:\n{e}"
            )

    def remove_image(self, image_uuid: str, bucket_name: str) -> None:
        """Removes an image from a Minio bucket. If the bucket does not exist, nothing happens.

        Args:
            image_uuid (str): The unique identifier for the image. Should be a stringified uuid.uuid4().
            bucket_name (str): The name of the bucket, if not exists, one will be created.

        Raises:
            Exception: Could not remove the object from the bucket.
        """

        if self._bucket_exists(bucket_name):
            try:
                # Delete image from the bucket
                self.minio_client.remove_object(
                    bucket_name=bucket_name, object_name=image_uuid
                )

            except Exception as e:
                raise Exception(
                    f"Could not remove {image_uuid} from {bucket_name}\n{e}"
                )
        else:
            self.logger.info(
                f"Could not remove {image_uuid} from {bucket_name} as the bucket does not exist"
            )

    def get_image(self, image_uuid: str, bucket_name: str) -> Image:
        """Gets an image from a Minio bucket.

        Args:
            image_uuid: (str): The unique identifier for the image. Should be a stringified uuid.uuid4().
            bucket_name (str): The name of the bucket, if not exists, one will be created.

        Raises:
            minio.S3Error: The bucket_name specified does not exist.

        Returns:
            image (PIL.Image): The image object from the Minio bucket.
        """

        if self._bucket_exists(bucket_name):
            image_bytes = self.minio_client.get_object(
                bucket_name=bucket_name, object_name=image_uuid
            ).data
            image = self._bytes_to_image(image_bytes)
            return image

        else:
            raise minio.S3Error("The bucket_name specified does not exist")

    def _image_to_bytes(self, image: Image) -> BytesIO:
        """Converter for PIL.Image to BytesIO object"""

        image_bytes = BytesIO()
        image.save(image_bytes, format="jpeg")
        image_bytes.seek(0)
        return image_bytes

    def _bytes_to_image(self, image_bytes: BytesIO) -> Image:
        """Converter for BytesIO object to PIL.Image"""

        image = Image.open(BytesIO(image_bytes))
        return image

    def _bucket_exists(self, bucket_name: str) -> bool:
        """Checks if a bucket exists

        Args:
            bucket_name (str): The Minio bucket name.

        Returns:
            bool: True if bucket exists, else False.
        """

        if not self.minio_client.bucket_exists(bucket_name):
            return False
        else:
            return True

    def _create_bucket_if_not_exists(self, bucket_name: str) -> None:
        """Checks if a bucket exists - if it does not, a new one will be created

        Args:
            bucket_name (str): The Minio bucket name.
        """

        if self._bucket_exists(bucket_name):
            pass
        else:
            self.minio_client.make_bucket(bucket_name)
            self.logger.info(
                f"Created bucket {bucket_name} as it did not already exist!"
            )
