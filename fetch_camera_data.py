import requests
import PIL
import io
import json
from PIL import Image

jibo_ip = "192.168.41.90"
media_port = 8486
photos_extension = "/media/photo"

url = "http://" + jibo_ip + ":" + str(media_port) + photos_extension
print("Url: ", url)
args= {
        "camera": 0,#defaults camera 0
        "type" : 2, 
        "filters": [
            {
                "kind":"undistort",
                "config":{}
            },
            {
                "kind":"flip",
                "config": {
                    "method" :1
                }
            }
        ]
}

def request_photo(args):
    """
    args: a dictionary (json-like) object containing the arguments to pass on to the photo capture request
    """
    response = requests.post(url, data=json.dumps(args))
    return response


def get_photo(photo_id):
    response = requests.get(url+"?id="+photo_id)
    return response

def take_and_get_photo(args):
    response = request_photo(args)
    print("Take photo response: ", response)
    content_response = json.loads(response.content)
    photo_id = content_response["id"]
    response= get_photo(photo_id)
    print("Get photo response: ", response)
    stream = io.BytesIO(response.content)
    img = Image.open(stream)
    return img

if __name__ == "__main__":
    iterations = 10
    path_to_data_dir = "./data/"
    camera_dir = path_to_data_dir + "camera_{}/"
    image_name = "camera_{}_jibo_capture_{}.png"
    while iterations > 0:
        #make a capture for each camera
        for camera in range(2):
            args["camera"] = camera
            img = take_and_get_photo(args)
            img.save(camera_dir.format(camera)+ image_name.format(camera, iterations))
        iterations -= 1
