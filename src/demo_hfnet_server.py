#!/usr/bin/env python3
# coding=utf-8

from hfnet_server.srv import ImageFeatures,ImageFeaturesResponse
from hfnet_server.msg import KeyPoint
import cv2
import time
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import MultiArrayDimension
import threading
import queue

# 该程序将执行 /hfnet_service 服务, 服务数据类型为 hfnet_server::ImageFeatures

# config
net_name = 'hfnet_tf'
server_name = '/hfnet_service'
gui = 'False'
log_interval = 3.0

class Node():
    def __init__(self, net, gui, log_interval):
        self.net = net
        self.gui = gui
        self.log_interval = log_interval
        self.cv_bridge = CvBridge()
        self.result_queue = queue.Queue()

    def response(self):
        while not rospy.is_shutdown():
            if self.result_queue.qsize() > 5:
                rospy.logwarn_throttle(1, 'WOW! Inference is faster than publishing' +
                                       ' (%d unpublished result in the queue)\n' % self.result_queue.qsize() +
                                       'Please add more publisher threads!')
            try:
                res = self.result_queue.get(timeout=.5)
            except queue.Empty:
                continue
            features = res['features']
            header = res['header']

            self.result_queue.task_done()
            response = ImageFeaturesResponse()

            response.header = header
            response.sorted_by_score.data = False

            for kp in features['keypoints']:
                p = KeyPoint()
                p.x = kp[0]
                p.y = kp[1]
                response.keypoints.append(p)
            response.scores = features['scores'].flatten()
            response.descriptors.data = features['local_descriptors'].flatten()
            shape = features['local_descriptors'][0].shape
            response.descriptors.layout.dim.append(MultiArrayDimension())
            response.descriptors.layout.dim[0].label = 'keypoint'
            response.descriptors.layout.dim[0].size = shape[0]
            response.descriptors.layout.dim[0].stride = shape[0] * shape[1]
            response.descriptors.layout.dim.append(MultiArrayDimension())
            response.descriptors.layout.dim[1].label = 'descriptor'
            response.descriptors.layout.dim[1].size = shape[1]
            response.descriptors.layout.dim[1].stride = shape[1]
            response.global_descriptor = features['global_descriptor'][0]
            return response

    def process(self, msg):
        if msg.encoding == '8UC1' or msg.encoding == 'mono8':
            image = self.cv_bridge.imgmsg_to_cv2(msg)
            image_gray = image
        else:
            image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        start = time.time()
        features = self.net.infer(image_gray)
        stop = time.time()
        rospy.logdebug('Infer time : %.2f (%d keypoints)' % (
            (stop - start) * 1000,
            features['keypoints'].shape[0]))

        if (features['keypoints'].shape[0] != 0):
            res = {'features': features, 'header': msg.header, 'image': image}
            self.result_queue.put(res)

    def draw_keypoints(self, image, keypoints, scores):
        upper_score = 0.5
        lower_score = 0.1
        scale = 1 / (upper_score - lower_score)
        for p,s in zip(keypoints, scores):
            s = min(max(s - lower_score, 0) * scale, 1)
            color = (255 * (1 - s), 255 * (1 - s), 255) # BGR
            cv2.circle(image, tuple(p), 3, color, 2)

def hfnet_request(req):

    if net_name == 'hfnet_vino':
        from hfnet_vino import FeatureNet
    elif net_name == 'hfnet_tf':
        from hfnet_tf import FeatureNet
    else:
        exit('Unknown net %s' % net_name)

    net = FeatureNet()
    node = Node(net, gui, log_interval)
    # 接收到的 req 为sensor::Image类型数据，将其转换成numpy类型，并输入到HFNET网络进行特征提取
    node.process(req.image)
    return node.response()

def main():
    # ROS node init
    rospy.init_node('demo_hfnet_server')
    # 创建一个名为 /hfnet_service 的server，注册回调函数 hfnet_request
    s = rospy.Service(server_name, ImageFeatures, hfnet_request)

    # print
    print('\n*************************** CONFIG ************************** \n')
    print('hfnet_mode: ',net_name)
    print('service name: ',server_name)
    print('\n*************************** ****** ************************** \n')

    print('wait for client ................................')

    rospy.spin()

if __name__ == '__main__':
    main()


