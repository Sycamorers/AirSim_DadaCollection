import setup_path
import airsim
import cv2
import numpy as np
import os
import time

import subprocess

# # Open AirSim environment
# binary_path = "/home/summer-atr/LandscapeMountains/LinuxNoEditor/LandscapeMountains/Binaries/Linux/LandscapeMountains"
# if os.path.exists(binary_path):
#     subprocess.Popen([binary_path])
# else:
#     print("Error: AirSim binary not found at the specified path.")


# connect to the AirSim simulator
client = airsim.CarClient()
client.confirmConnection()
client.enableApiControl(True)
print("API Control enabled: %s" % client.isApiControlEnabled())
car_controls = airsim.CarControls()

tmp_dir = os.path.join(os.getcwd(), "dataset_collection")
print ("Saving images to %s" % tmp_dir)
try:
    os.makedirs(tmp_dir)
except OSError:
    if not os.path.isdir(tmp_dir):
        raise

start_time = time.time()

idx = 0

while True:
    current_time = time.time()

    # if 10 seconds have passed, break the loop
    if current_time - start_time > 5:
        break

    # Move in circle
    car_controls.throttle = 0.5
    car_controls.steering = 1  # constantly steering to the right
    client.setCarControls(car_controls)
    
    # get camera images from the car
    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])

    for response_idx, response in enumerate(responses):
        filename = os.path.join(tmp_dir, f"{idx}_{response.image_type}_{response_idx}")

        if response.compress: #png format
            print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)
        else: #uncompressed array
            print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
            img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 3 channel image array H X W X 3
            print("Image shape: ", img_rgb.shape)
            # airsim.write_png(os.path.normpath(filename + '.png'), img_rgb) 
            cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # write to png
            # img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
            # img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 3 channel image array H X W X 3
            # img_resized = cv2.resize(img_rgb, (2560, 1440)) # resize the image to the desired dimensions
            # cv2.imwrite(os.path.normpath(filename + '.png'), img_resized) # write to png

    idx += 1

    # sleep for 1 second to take next picture
    time.sleep(1)

#restore to original state
client.reset()

client.enableApiControl(False)
