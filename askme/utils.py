from PIL import Image
from io import BytesIO

from django.core.files.base import ContentFile

def cropper(original_image, name):
    img_io = BytesIO()
    im = Image.open(original_image)
    width, height = im.size
    new_width = new_height = min(width, height)
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2
    im = im.crop((left, top, right, bottom)).resize((200, 200), Image.ANTIALIAS)
    im.save(img_io, format='JPEG', quality=100)
    img_content = ContentFile(img_io.getvalue(), name)
    return img_content