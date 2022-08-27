from typing import Union, Optional
import math
from io import BytesIO
import re
import base64
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
import requests
import boto3


def get_resource_stream(uri: str) -> str:
    url = urlparse(uri)
    host_segments = url.hostname.split('.')

    if len(host_segments) != 5:
        print(f'Get remote resource: {uri}')
        return requests.get(uri, stream=True).raw

    if host_segments[1] != 's3' or host_segments[3] != 'amazonaws' or host_segments[4] != 'com':
        print(f'Get remote resource: {uri}')
        return requests.get(uri, stream=True).raw

    bucket, _, region, _, _ = host_segments

    s3_client = boto3.client('s3', region_name=region)

    print(f'Get s3 resource: {uri}')
    return s3_client.get_object(Bucket=bucket, Key=url.path[1:])['Body']


def cover(fp: Union[str, bytes, Path], width: Optional[Union[int, str]], height: Optional[Union[int, str]]) -> Image:
    image = Image.open(fp, 'r')

    image_width, image_height = image.size

    if width is None:
        width = image_width
    if height is None:
        height = image_height
    
    if isinstance(width, str) and width.isnumeric():
        width = int(width)
    if isinstance(height, str) and height.isnumeric():
        height = int(height)

    if isinstance(width, str) and isinstance(height, str):
        width = image_width
        height = image_height
    elif isinstance(width, str):
        height_ratio = height / image_height
        width = round(image_width * height_ratio)
    else:
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


def thumbnail(fp: Union[str, bytes, Path], width: Optional[Union[int, str]], height: Optional[Union[int, str]]) -> Image:
    return cover(fp, width, height).convert('RGB')


def lambda_handler(event, context):
    query = event['queryStringParameters']
    image_stream = get_resource_stream(query['src'])

    if 'size' in query and re.match(r'(\d+|auto)x(\d+|auto)', query['size']):
        width, height = query['size'].split('x')
    else:
        width = None
        height = None

    image = thumbnail(image_stream, width, height)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")

    return {
        "statusCode": "200",
        "headers": {
            "Content-Type": "image/jpeg"
        },
        "body": base64.b64encode(buffered.getvalue()),
        "isBase64Encoded": True
    }


if __name__ == '__main__':
    lambda_handler({
        'queryStringParameters': {
            'src': 'https://onulbanchan-static.s3.ap-northeast-2.amazonaws.com/products/cover/5Brt29QNYEBGfb0qGmJuT8n7WINHr2HMM77zzq7T.jpg'
        }
    }, None)

