import requests
import PIL
import io
import json
from PIL import Image

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
    #synchronous
    response = requests.post(url, data=json.dumps(args))
    #response = async.get(url, data=json.dumps(args))
    return response

def request_photos(args):
    #request camera 0
    args["camera"] = 0
    response_0 = request_photo(args)
    #request camera 1
    args["camera"] = 1
    response_1 = request_photo(args)
    return (response_0, response_1)


def get_photo(photo_id):
    #synchronous to avoid overriting the program from taking more pictures before downlading the current
    response = requests.get(url+"?id="+photo_id)
    print('Getting photo id: ', photo_id)
    return response

def get_photos(take_responses):
    responses = []
    for i in range(len(take_responses)):#iterate over each camera capture
        content_response = json.loads(take_responses[i].content)
        photo_id = content_response["id"]
        responses.append(get_photo(photo_id))
    return responses
    

def take_and_get_photos(args):
    responses = request_photos(args)
    print("Take photo responses: ", responses)
    images = []
    for i in range(len(responses)):#iterate over each camera capture
        content_response = json.loads(responses[i].content)
        photo_id = content_response["id"]
        response= get_photo(photo_id)
        print("Get photo response: ", response)
        stream = io.BytesIO(response.content)
        img = Image.open(stream)
        images.append(img)
    return images

def get_image(get_response):
    print("get image input: ", get_response)
    stream = io.BytesIO(get_response.content)
    return Image.open(stream)

if __name__ == "__main__":
    #parameters
    iterations = 10
    path_to_data_dir = "./calibration_imgs/"
    camera_dir = path_to_data_dir + "camera_{}/"
    #constants
    image_name = "jibo_capture_{}.png"
    jibo_ip = "192.168.41.90"
    media_port = 8486
    photos_extension = "/media/photo"
    url = "http://" + jibo_ip + ":" + str(media_port) + photos_extension
    print("Url: ", url)
    #program
    i = 0#iteration counter
    while i < iterations:
        #make a capture for each camera
        capture_responses = request_photos(args)
        print("capture responses: ", capture_responses)
        get_responses = get_photos(capture_responses)
        print("get responses: ", get_responses)
        if get_responses[0].status_code != 200 or get_responses[1].status_code != 200:
            #failed to fetch capture. Try again
            continue
        else:
            #downloads were successful
            for camera in range(2):
                print("current get_response: ", camera, get_responses[camera])
                img = get_image(get_responses[camera])
                print("saving to: ", image_name.format(str(i)))
                img.save(camera_dir.format(camera)+ image_name.format(str(i)))
            i += 1
