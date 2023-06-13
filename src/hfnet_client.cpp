//
// Created by zhu on 23-6-12.
//
#include <ros/ros.h>
#include "/home/zhu/RosProjects/hfnet_server_ws/devel/include/hfnet_server/ImageFeatures.h"
#include <sensor_msgs/Image.h>

using namespace std;
ros::ServiceClient client;
int keypoint_size;
int local_descriptors_size;
int global_descriptors_size = 4096;

void img_callback(const sensor_msgs::Image::ConstPtr& img_msg)
{
    double start_t = ros::Time::now().toSec();
    hfnet_server::ImageFeatures srv;
    srv.request.image = *img_msg;

    if(client.call(srv)){
        keypoint_size = srv.response.descriptors.layout.dim[0].size;
//        local_descriptors_size = srv.response.descriptors.layout.dim[1].size;

        /**
        std::cout << "***************************************************" << endl;
        std::cout << "time_stamp: " << srv.response.header << endl;
        std::cout << "keypoint_size: " << keypoint_size <<" local_descriptors_size: "<< local_descriptors_size << endl;


        std::cout << "********************* keypoint: *******************" << endl;
        for(int i=0;i < keypoint_size;i++)
            std::cout << "(x:" << srv.response.keypoints[i].x << ",y:" <<srv.response.keypoints[i].y<<") ";
        std::cout << endl;
        std::cout << "********************* local_descriptors: **********" << endl;

        for(int i=0;i<keypoint_size;i++){
            for(int j=0;j<local_descriptors_size;j++)
            {
                std::cout << srv.response.descriptors.data[i*local_descriptors_size+j]<<' ';
            }
            std::cout <<endl;
        }
        std::cout << endl;
        std::cout << "********************* global_descriptors: *********" << endl;
        for(int i=0; i < global_descriptors_size; i++)
            std::cout << srv.response.global_descriptor[i] << ' ';
        std::cout << endl;
        std::cout << "*****************************************************************" << endl;
        **/
    }
    std::cout << "hfnet detect cost: "<< ros::Time::now().toSec() - start_t << endl;
}

int main(int argc, char** argv)
{
    ros::init(argc,argv,"hfnet_client");
    ros::NodeHandle node;

    // 初始化请求数据, 接收 /cam0/image 话题
    std::cout << "wait for ros data .................. "<<endl;
    ros::Subscriber img_sub = node.subscribe("/cam0/image_raw",10,img_callback);

    client = node.serviceClient<hfnet_server::ImageFeatures>("hfnet_service");

    ros::spin();
    return 0;
}