/*********************************************************************
*
* Software License Agreement (BSD License)
*
*  Copyright (c) 2014, P.A.N.D.O.R.A. Team.
*  All rights reserved.
*
*  Redistribution and use in source and binary forms, with or without
*  modification, are permitted provided that the following conditions
*  are met:
*
*   * Redistributions of source code must retain the above copyright
*     notice, this list of conditions and the following disclaimer.
*   * Redistributions in binary form must reproduce the above
*     copyright notice, this list of conditions and the following
*     disclaimer in the documentation and/or other materials provided
*     with the distribution.
*   * Neither the name of the P.A.N.D.O.R.A. Team nor the names of its
*     contributors may be used to endorse or promote products derived
*     from this software without specific prior written permission.
*
*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
*  POSSIBILITY OF SUCH DAMAGE.
*
* Author:  Evangelos Apostolidis
* Author:  Chris Zalidis
*********************************************************************/
#ifndef PANDORA_SENSOR_ORIENTATION_CONTROLLER_SENSOR_ORIENTATION_CONTROLLER_H
#define PANDORA_SENSOR_ORIENTATION_CONTROLLER_SENSOR_ORIENTATION_CONTROLLER_H

#include <string>
#include <vector>

#include <boost/math/constants/constants.hpp>

#include <ros/ros.h>
#include <tf/transform_listener.h>
#include <actionlib/server/simple_action_server.h>

#include <std_msgs/Float64.h>

#include <pandora_sensor_orientation_controller/MoveSensorAction.h>
#include <pandora_sensor_msgs/ImuRPY.h>

namespace pandora_control
{
  enum
  {
    START = 0,
    UP_LEFT_ONE = 1,
    UP_LEFT_TWO = 2,
    DOWN_LEFT = 3,
    DOWN_CENTER = 4,
    DOWN_RIGHT = 5,
    UP_RIGHT_TWO = 6,
    UP_RIGHT_ONE = 7,
    UP_CENTER = 8,
    UNKNOWN = 9
  };

  class SensorOrientationActionServer
  {
   private:
      ros::NodeHandle nodeHandle_;
      std::string actionName_;
      actionlib::SimpleActionServer<
        pandora_sensor_orientation_controller::MoveSensorAction> actionServer_;

      ros::Publisher sensorPitchPublisher_;
      ros::Publisher sensorYawPublisher_;

      ros::Subscriber imuSubscriber_;

      ros::Timer scanYawTimer_;
      ros::Timer softScanTimer_;
      ros::Timer scanPitchTimer_;
      ros::Timer pointSensorTimer_;

      int position_;
      int command_;
      double pitchStep_;
      double yawStep_;
      double minPitch_;
      double minYaw_;
      double maxPitch_;
      double maxYaw_;
      double scanRate_;
      double softScanRate_;
      double pitchRate_;
      double commandTimeout_;
      double pointThreshold_;
      double movementThreshold_;
      double laxMovementThreshold_;
      std::string pitchJointParent_;
      std::string pitchJointChild_;
      std::string yawJointParent_;
      std::string yawJointChild_;
      std::string imuTopic_;
      std::string pitchCommandTopic_;
      std::string yawCommandTopic_;
      std::string sensorFrame_;
      std::string pointOfInterest_;

      std::vector<double> pitchBuffer_;
      double stabilizedPitch_;
      int bufferSize_;
      int bufferCounter_;

      bool firstOfSoftScan_;
      double direction_;
      double pitchScan_;
      double offsetPitch_;
      double yawScan_;
      double offsetYaw_;

      double lastPitchTarget_;
      double lastYawTarget_;

      std_msgs::Float64 pitchTargetPosition_;
      std_msgs::Float64 yawTargetPosition_;

      tf::TransformListener tfListener_;

      void imuCallback(const pandora_sensor_msgs::ImuRPYConstPtr& msg);
      void callback(const pandora_sensor_orientation_controller::MoveSensorGoalConstPtr& goal);
      void preemptCallback();

      bool getcontrollerParams();
      void testSensor();
      void centerSensor();
      void scan(const ros::TimerEvent& event);
      void softScan(const ros::TimerEvent& event);
      void stabilizePitch(const ros::TimerEvent& event);
      void pointSensor(const ros::TimerEvent& event);

      void publishScanPitchCommand();
      void publishScanYawCommand();

      int checkGoalCompletion();
      void setGoalState(int state);
      void checkAngleLimits();
      void stopPreviousTimers();

   public:
      SensorOrientationActionServer(
        std::string name,
        ros::NodeHandle nodeHandle_);

      ~SensorOrientationActionServer(void);
  };
}  // namespace pandora_control

#endif  // PANDORA_SENSOR_ORIENTATION_CONTROLLER_SENSOR_ORIENTATION_CONTROLLER_H
