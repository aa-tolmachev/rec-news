import json
from io import BytesIO
import logging
from typing import Iterable, Mapping, Optional

from bs4 import BeautifulSoup
import requests
from PIL import Image
# import torch

# from lib_image.classifier import IMAGE_TRANSFORMS, Classifier

YANDEX_IMAGES_URL = r'https://yandex.ru/images/search'
# IMAGE_CLASSIFIER = Classifier()
# IMAGE_CLASSIFIER.load_state_dict(
#     torch.load(
#         './models/image_clf.pt',
#         map_location=torch.device('cpu')
#     )
# )

def get_images_by_description(text: str) -> Iterable[str]:
    response = requests.get(
        YANDEX_IMAGES_URL, verify=False,
        params={'text': text}
    )
    
    def _get_preview_from_image(image: Mapping) -> Optional[str]:
        try:
            # Get picture with highest resolution
            images = sorted(
                json.loads(image['data-bem'])['serp-item']['preview'],
                key=lambda image: image['w'] + image['h'], reverse=True
            )
            return images[0]['url']
        except:
            logging.exception('Error while image parsing', extra=image)


    soup = BeautifulSoup(response.text, 'lxml')
    images_iter = map(
        _get_preview_from_image,
        soup.find_all('div', class_='serp-item')
    )

    return filter(None, images_iter)


def is_suitable_image(image: Image.Image) -> bool:
    try:
        image_tensor = IMAGE_TRANSFORMS(image).reshape(1,3,256,256)
        logits = IMAGE_CLASSIFIER(image_tensor)
        return torch.argmax(logits, dim=1)[0].item() == 0
    except:
        return False
    

def download_image(image_url: str) -> Optional[Image.Image]:
    if not image_url:
        return None
    try:
        return Image.open(
            BytesIO(requests.get(image_url, verify=False).content)
        ).convert('RGB')
    except:
        logging.exception('Cannot download image by url "%s"', image_url)    


def prepare_image(picture_url: str, summary: str) -> Optional[str]:
    original_picture = download_image(picture_url)
    if original_picture:
        return picture_url
    # if picture_url and is_suitable_image(original_picture):
    #     return picture_url
    print(f'search image by text "{summary}"')
    for image_url in get_images_by_description(summary):
        return image_url
        image = download_image(image_url)
        prediction = is_suitable_image(image)
        print(
            f'For picture url "{image_url}" prediction is {prediction}'
            )
        if prediction:
            return image_url
    return None
