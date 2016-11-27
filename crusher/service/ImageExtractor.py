import config
import requests
from bs4 import BeautifulSoup
from PIL import Image
from StringIO import StringIO

import uuid
import urlparse

from boto.s3.key import Key
from boto.s3.connection import S3Connection


class ImageExtractor(object):

    def __init__(self):
        self.conn = S3Connection(config.S3_API_KEY, config.S3_SECRET_KEY)
        self.bucket = self.conn.get_bucket(config.S3_BUCKET)

    def extract(self, article, datasource):
        url = article["rss_link"]

        html = requests.get(url).content
        soup = BeautifulSoup(html)

        for img in soup.find_all('img'):

            imgurl = urlparse.urljoin(url, img.get('src'))
            dbimage = datasource.check_if_image_exists(imgurl)

            if dbimage:
                datasource.increment_image_count(imgurl)
                continue

            else:
                # image has not appeared before, let's save it and check the size
                datasource.insert_image(imgurl)
                try:
                    thumbsize = 400, 400
                    try:
                        im = Image.open(StringIO(requests.get(imgurl).content))
                    except IOError:
                        break

                    # check the size
                    if im.size[0] > 150 and im.size[1] > 150:

                        # scale image
                        im.thumbnail(thumbsize, Image.ANTIALIAS)

                        if im.mode != 'RGB':
                            im = im.convert('RGB')

                        output = StringIO()

                        im.save(output, 'JPEG')
                        image_data = output.getvalue()
                        output.close()

                        # create key for s3
                        key = uuid.uuid4()
                        k = Key(self.bucket)
                        k.key = str(key)+".jpg"

                        k.set_contents_from_string(image_data)
                        self.bucket.set_acl('public-read', k.key)

                        return str(key) + ".jpg"

                except (requests.exceptions.ConnectionError,
                        RuntimeError,
                        TypeError,
                        NameError,
                        requests.exceptions.MissingSchema):

                    # Ignore image errors for now, in this case no image is shown
                    pass
