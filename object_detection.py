#!/usr/bin/env python3

"""Object detection
Make Vector dectect objects.
"""
import io
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Imports the Anki Vector SDK
import anki_vector
import anki_vector.camera


robot = anki_vector.Robot(anki_vector.util.parse_command_args().serial)
screen_dimensions = anki_vector.screen.SCREEN_WIDTH, anki_vector.screen.SCREEN_HEIGHT
current_directory = os.path.dirname(os.path.realpath(__file__))
image_file = os.path.join(current_directory, 'resources', "latest.jpg")

def detect_labels(path):
    print('Detect labels, image = {}'.format(path))
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

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


def localize_objects(path):
    print('Localize objects, image = {}'.format(path))
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(image=image).localized_object_annotations

    res_list = []
    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        res_list.append(object_.name)
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))

    return ', and '.join(res_list)


def connect_robot():
    print('Connect to Vector...')
    robot.connect()


def disconnect_robot():
    robot.disconnect()
    print('Vector disconnected')


def setRobotPosition():
    # If necessary, move Vector's Head and Lift to make it easy to see his face
    robot.behavior.set_lift_height(0.0)


def close_camera():
    print('Close camera')
    robot.vision.enable_display_camera_feed_on_face(False)
    robot.camera.close_camera_feed()


def save_image(file_name):
    print('Save image')
    image = robot.camera.latest_image.raw_image.save(file_name, 'JPEG')
    # image = robot.camera.capture_single_image()
    # robot.camera.capture_single_image()
    # image = robot.camera.latest_image
    # image.raw_image.save(file_name, 'JPEG')

def show_image(file_name):
    print('Show image = {}'.format(file_name))

    # Load an image
    image = Image.open(file_name)

    # Convert the image to the format used by the Screen
    print("Display image on Vector's face...")
    screen_data = anki_vector.screen.convert_image_to_screen_data(image.resize(screen_dimensions))
    robot.screen.set_screen_with_image_data(screen_data, 5.0, True)


def robot_say(text):
    print('Say {}'.format(text))
    robot.behavior.say_text(text)


def analyze():
    setRobotPosition()
    robot_say('Going to take a photo now')
    save_image(image_file)
    show_image(image_file)

    robot_say('Starting to analyze the objects in the photo')
    text = detect_labels(image_file)
    show_image(image_file)
    robot_say('Might be {}'.format(text))

    '''
    robot_say('Start to localize the object')
    text = localize_objects(image_file)
    show_image(image_file)
    robot_say('I found {}'.format(text))
    '''

    close_camera()
    robot_say('Over, goodbye!')


def main():
    connect_robot()
    try:
        analyze()
    except Exception as e:
        print('Analyze Exception: {}', e)

    disconnect_robot()


if __name__ == "__main__":
    main()
