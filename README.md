# HFNET_server_ws

### TODO:
1. the description of project


# Setup

### System requirement

- Ubuntu + ROS
- Python 3.6 or higher
- TensorFlow 1.12 or higher (`pip3.6 install tensorflow`)
- OpenVINO 2020 R1 or higher ([download](https://software.intel.com/en-us/openvino-toolkit/choose-download))
- OpenCV for Python3 (`pip3 install opencv-python`; not needed if OpenVINO is installed and activated)
- numpy (`pip3 install numpy`)
- No GPU requirement

### Download and build

0. Preliminary
```
sudo apt install python3-dev python3-catkin-tools python3-catkin-pkg-modules python3-rospkg-modules python3-empy python3-yaml
```

1. Set up catkin workspace and download this repo
```
mkdir -p hfnet_server_ws/src && cd src
git clone https://github.com/YongshuaiZ/hfnet_server.git
```
2. Download one of the saved [HF-Net](https://github.com/ethz-asl/hfnet) models from the [Releases](https://github.com/cedrusx/deep_features/releases), and move it to **hfnet_sever/model/**

3. build
```
cd ..
catkin_make
source devel/setup.bash
```
# Run

### hfnet_server


```
rosrun hfnet_server demo_hfnet_server.py
rosrun hfnet_server hfnet_client
rosbag play ~/datasets/Euroc/MH_01_easy.bag 
```