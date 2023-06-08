import os
import pprint
import math
import time
import tempfile
import airsim

pp = pprint.PrettyPrinter(indent=4)

client = airsim.VehicleClient()
client.confirmConnection()

airsim.wait_key('Press any key to set camera-0 gimbal to 15-degree pitch')
camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(math.radians(15), 0, 0)) #radians
client.simSetCameraPose("0", camera_pose)    


airsim.wait_key('Press any key to get camera parameters')
for camera_name in range(5):
    camera_info = client.simGetCameraInfo(str(camera_name))
    print("CameraInfo %d:" % camera_name)   
    pp.pprint(camera_info)

output_dir = "/home/summer-atr/image_capture_data"
# output_dir = "image_capture_data"


print ("Saving images to %s" % output_dir)
try:
    os.makedirs(output_dir)
except OSError:
    if not os.path.isdir(output_dir):
        raise

airsim.wait_key('Press any key to get images')
 
# Setup parameters for figure-8 motion
radius = 50  # radius of the figure-8 motion
images = 20  # number of images to capture
steps = images  # steps to complete the figure-8 motion
pi = math.pi  # pi constant

for x in range(steps):
    # Calculate position along figure-8 trajectory
    t = 2 * pi * (x / steps)  # normalized time variable
    z = radius * math.sin(t)
    y = radius * math.sin(t) * math.cos(t)
    client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0, y, z), airsim.to_quaternion(0, 0, 0)), True)

    # Capture images
    # responses = client.simGetImages([
    #     airsim.ImageRequest("0", airsim.ImageType.DepthVis),
    #     airsim.ImageRequest("1", airsim.ImageType.DepthPerspective, True),
    #     airsim.ImageRequest("2", airsim.ImageType.Segmentation),
    #     airsim.ImageRequest("3", airsim.ImageType.Scene),
    #     airsim.ImageRequest("4", airsim.ImageType.DisparityNormalized),
    #     airsim.ImageRequest("4", airsim.ImageType.SurfaceNormals)])

    responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene)])


    for i, response in enumerate(responses):
        filename = os.path.join(output_dir, str(x) + "_" + str(i))
        if response.pixels_as_float:
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_float), pprint.pformat(response.camera_position)))
            airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
        else:
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_uint8), pprint.pformat(response.camera_position)))
            airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)

    time.sleep(3)

# currently reset() doesn't work in CV mode. Below is the workaround
client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0)), True)
