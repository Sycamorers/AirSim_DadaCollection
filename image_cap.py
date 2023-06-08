import os
import pprint
import math
import time
import tempfile
import airsim

pp = pprint.PrettyPrinter(indent=4)

client = airsim.VehicleClient()
client.confirmConnection()



output_dir = "/home/summer-atr/image_capture_data"
# output_dir = "image_capture_data"


print ("Saving images to %s" % output_dir)
try:
    os.makedirs(output_dir)
except OSError:
    if not os.path.isdir(output_dir):
        raise

# airsim.wait_key('Press any key to get images')
 
# Setup parameters for figure-8 motion
radius = 50  # radius of the figure-8 motion
pi = math.pi  # pi constant
total_time = 60  # Total time to complete the figure-8 motion in seconds
images = 100  # Number of images to capture (also the number of steps)
steps = images
delay = total_time / steps  # Time delay between steps

# Get initial camera position
initial_pose = client.simGetVehiclePose()
initial_position = initial_pose.position

# Get initial camera orientation (quaternion -> euler angles)
initial_orientation = airsim.to_eularian_angles(initial_pose.orientation)


for s in range(steps):

    # # Get camera position
    # camera_pose = client.simGetVehiclePose()
    # camera_position = camera_pose.position

    # Calculate position along figure-8 trajectory
    t = 2 * pi * (s / steps)  # normalized time variable
    x = initial_position.x_val + radius * math.sin(t)
    y = initial_position.y_val + radius * math.sin(t) * math.cos(t)

    # client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, 0 ), airsim.to_quaternion(0, 0, 0)), True)
    client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, 0 ), 
                                         airsim.to_quaternion(initial_orientation[0], 
                                                               initial_orientation[1], 
                                                               initial_orientation[2])), 
                                                               True)

    responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene)])


    for i, response in enumerate(responses):
        filename = os.path.join(output_dir, str(s) + "_" + str(i))
        if response.pixels_as_float:
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_float), pprint.pformat(response.camera_position)))
            airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
        else:
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_uint8), pprint.pformat(response.camera_position)))
            airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)

    time.sleep(delay)

# currently reset() doesn't work in CV mode. Below is the workaround
client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0)), True)

