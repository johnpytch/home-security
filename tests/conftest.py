from pytest import fixture
import PIL.Image
import helpers


@fixture
def test_image() -> PIL.Image:
    return helpers.test_image()
