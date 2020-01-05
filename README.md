<img src="https://user-images.githubusercontent.com/799578/52912304-8c5aae80-32ea-11e9-8a04-b92ca50a7cb7.jpg" width="480"/>

# Table of contents
- [Table of contents](#table-of-contents)
- [Description](#description)
- [Object detection](#object-detection)
    - [Run the code yourself](#run-the-code-yourself)
    - [How it works](#how-it-works)

# Description
[Anki Vector](https://www.anki.com/en-us/vector) - The Home Robot With Interactive AI Technology.

This project borrows from [# Anki Vector AI++](https://github.com/open-ai-robot/awesome-anki-vector).  I plan on expanding upon this and
setting up a maze game where Vector will traverse a maze and gather info along his journey.  This information will be sent up to the cloud
and upon completion of the maze, statistics about Vector's journey will be presented.  The focus will be on learning cloud technologies
such as image recognition, nosql databases, and serverless compute.

As of right now, this project will likely focus on Google cloud, but will likely expand to AWS and Azure soon. 


# Object detection
This program is to enable Vector to detect objects with its camera, and tell us what it found. 

We take a photo from Vector's camera, then post to [Google Vision Service](https://cloud.google.com/vision/docs/labels), then Google Vision Service returns the object detection result, 
finally, we turn all the label text into a sentence and send to Vector so that Vector can say it out loud.

### Run the code yourself
1. Install [Vector Python SDK](https://developer.anki.com/vector/docs/install-macos.html). You can test the SDK by running any of the example from [anki/vector-python-sdk/examples/tutorials/](https://github.com/anki/vector-python-sdk/tree/master/examples/tutorials) 
1. Set up your Google Vision account. Then follow the [Quickstart](https://cloud.google.com/vision/docs/quickstart-client-libraries) to test the API.
1. Clone this project to local. It requires Python 3.6+.
1. Change directory to this project in commandline.
1. Create python virtual envirionment `python3 -m venv .`
1. Install all dependencies for this project `pip3 install -r requirements.txt`
1. Don forget to set Google Vision environment variable GOOGLE_APPLICATION_CREDENTIALS to the file path of the JSON file that contains your service account key.  e.g. `export GOOGLE_APPLICATION_CREDENTIALS="/Workspace/Vector-vision-62d48ad8da6e.json"`
1. Make sure your computer and Vector in the same WiFi network. Then run `./object_detection.py`.
1. Done

### How it works
1. Connect to Vector with `enable_camera_feed=True`, because we need the [anki_vector.camera](https://developer.anki.com/vector/docs/generated/anki_vector.camera.html) API.
```python
robot = anki_vector.Robot(anki_vector.util.parse_command_args().serial, enable_camera_feed=True)
```

2. We'll need to show what Vector see on its screen.

```python
def show_camera():
    print('Show camera')
    robot.camera.init_camera_feed()
    robot.vision.enable_display_camera_feed_on_face(True)
```

and close the camera after the detection.

```python    
def close_camera():
    print('Close camera')
    robot.vision.enable_display_camera_feed_on_face(False)
    robot.camera.close_camera_feed()
```
3. We'll save take a photo from Vector's camera and save it later to send to Google Vision.

```python
def save_image(file_name):
    print('Save image')
    robot.camera.latest_image.save(file_name, 'JPEG')
```
4. We post the image to Google Vision and parse the result as a text for Vector.

```python
def detect_labels(path):
    print('Detect labels, image = {}'.format(path))
    # Instantiates a client
    # [START vision_python_migration_client]
    client = vision.ImageAnnotatorClient()
    # [END vision_python_migration_client]

    # Loads the image into memory
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    res_list = []
    for label in labels:
        if label.score > 0.5:
            res_list.append(label.description)

    print('Labels: {}'.format(labels))
    return ', or '.join(res_list)
```
5. Then we send the text to Vector and make it say the result.

```python
def robot_say(text):
    print('Say {}'.format(text))
    robot.say_text(text)
```
6. Finally, we put all the steps together.

```python
def analyze():
    stand_by()
    show_camera()
    robot_say('My lord, I found something interesting. Give me 5 seconds.')
    time.sleep(5)

    robot_say('Prepare to take a photo')
    robot_say('3')
    time.sleep(1)
    robot_say('2')
    time.sleep(1)
    robot_say('1')
    robot_say('Cheers')

    save_image(image_file)
    show_image(image_file)
    time.sleep(1)

    robot_say('Start to analyze the object')
    text = detect_labels(image_file)
    show_image(image_file)
    robot_say('Might be {}'.format(text))

    close_camera()
    robot_say('Over, goodbye!')

```
7. We want Vector randomly active the detection action, so we wait for a random time (about 30 seconds to 5 minutes) for the next detection.

```python
def main():
    while True:
        connect_robot()
        try:
            analyze()
        except Exception as e:
            print('Analyze Exception: {}', e)

        disconnect_robot()
        time.sleep(random.randint(30, 60 * 5))
```

8. When Vector success to active the detection action, you should see logs:

```shell
2019-02-17 21:55:42,113 anki_vector.robot.Robot WARNING  No serial number provided. Automatically selecting 009050ae
Connect to Vector...
2019-02-17 21:55:42,116 anki_vector.connection.Connection INFO     Connecting to 192.168.1.230:443 for Vector-M2K2 using /Users/gaolu.li/.anki_vector/Vector-M2K2-009050ae.cert
2019-02-17 21:55:42,706 anki_vector.connection.Connection INFO     control_granted_response {
}


Save image
Show image = /Workspace/labs/Anki-Vector-AI/resources/latest.jpg
Display image on Vector's face...
Say Start to analyze the object
Detect labels, image = /Workspace/labs/Anki-Vector-AI/resources/latest.jpg
Labels: [mid: "/m/08dz3q"
description: "Auto part"
score: 0.6821197867393494
topicality: 0.6821197867393494
]
Show image = /Workspace/labs/Anki-Vector-AI/resources/latest.jpg
Display image on Vector's face...
Say Might be Auto part
Close camera
Say Over, goodbye!
2019-02-17 21:56:12,460 anki_vector.connection.Connection INFO     control_lost_event {
}

2019-02-17 21:56:12,460 anki_vector.robot.Robot WARNING  say_text cancelled because behavior control was lost
2019-02-17 21:56:12,461 anki_vector.util.VisionComponent INFO     Delaying disable_all_vision_modes until behavior control is granted
2019-02-17 21:56:12,707 anki_vector.connection.Connection INFO     control_granted_response {
}

Vector disconnected

```

You can find the latest photo that Vector uses to detention in `resources/latest.jpg`.
