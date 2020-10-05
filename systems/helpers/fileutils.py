# -*- coding: utf-8 -*-
import hashlib
import imghdr
import logging
import os
import sys

import requests
from werkzeug.utils import secure_filename

from systems.config import NeoConfig
from systems.exception.base import NeoException
from systems.helpers import datetimeutils

log = logging.getLogger(__name__)

img_allowed_ext = [
    'jpg', 'jpeg',
    'png', 'gif'
]


def upload_to_thumbor(blob, filename=None):
    """_upload image

    :param filename: file name
    :type blob: werkzeug.datastructures.FileStorage
    :return: absolute path to file

    """
    if not filename:
        plain = "{}-{}".format(datetimeutils.get_current_epoch(), blob.filename).encode('utf-8')
        randhash = hashlib.md5(plain).hexdigest()
        filename = secure_filename("{}_{}".format(randhash, blob.filename))
    else:
        filename = secure_filename(blob.filename).lower()

    thumbor_url = "{}/image".format(NeoConfig.THUMBOR_URL)

    headers = {
        'Content-Type': blob.mimetype,
        'Content-Length': str(sys.getsizeof(blob.stream)),
        'Slug': filename
    }

    r = requests.post(thumbor_url, data=blob.stream, headers=headers)
    rel_path = r.headers.get('Location')
    return rel_path


def upload_images(blob, directory, filename=None):
    """_upload image

    :param filename: file name
    :param directory: base directory
    :type blob: werkzeug.datastructures.FileStorage
    :return: absolute path to file

    """
    if not filename:
        plain = "{}-{}".format(datetimeutils.get_current_epoch(), blob.filename).encode('utf-8')
        randhash = hashlib.md5(plain).hexdigest()
        filename = secure_filename("{}_{}".format(randhash, blob.filename))
    else:
        filename = secure_filename(blob.filename).lower()

    if not os.path.exists(directory):
        try:
            os.mkdir(directory)
        except OSError as e:
            if e.errno == 17:
                log.debug("directory already exist")
            else:
                raise NeoException from e
        except Exception as e:
            log.exception(e)
            raise NeoException from e

    filepath = os.path.join(directory, filename)
    blob.save(filepath)

    imgtype = imghdr.what(filepath)
    if imgtype not in img_allowed_ext:
        os.remove(filepath)
        raise NeoException("file type is not supported")

    return filepath
