from typing import Union, Optional
import json
import math
from pathlib import Path
from PIL import Image
import requests

def cover(fp: Union[str, bytes, Path], width: Optional[Union[int, str]], height: Optional[Union[int, str]]) -> Image:
    image = Image.open(fp, 'r')

    if isinstance(width, str) and width.isnumeric():
        width = int(width)

    if isinstance(height, str) and height.isnumeric():
        height = int(height)

    image_width, image_height = image.size

    if width is None or isinstance(width, str):
        height_ratio = height / image_height
        width = round(image_width * height_ratio)

    if height is None or isinstance(height, str):
        width_ratio = width / image_width
        height = round(image_height * width_ratio)

    if image_width > image_height:
        ratio = image_width / image_height
        resized_image = image.resize((round(ratio * height), height))
    else:
        ratio = image_height / image_width
        resized_image = image.resize((width, round(ratio * width)))

    image.close()

    image_width, image_height = resized_image.size

    left = math.floor(image_width / 2 - width / 2)
    right = math.floor(image_width / 2 + width / 2)
    top = math.floor(image_height / 2 - height / 2)
    bottom = math.floor(image_height / 2 + height / 2)

    cropped_image = resized_image.crop((left, top, right, bottom))
    resized_image.close()

    return cropped_image

def lambda_handler(event, context):
    image_stream = requests.get(event['src'], stream=True).raw
    width, height = event['size'].split('x')
    cover_image = cover(image_stream, width, height)
    cover_image.convert('RGB')

    return cover_image

if __name__ == '__main__':
    cover_image = lambda_handler({
        'src': 'https://onulbanchan-static.s3.ap-northeast-2.amazonaws.com/products/cover/5Brt29QNYEBGfb0qGmJuT8n7WINHr2HMM77zzq7T.jpg',
        'size': '120x300'
    }, None)
    cover_image.save('../onulbanchan-api/public/test.jpg')

