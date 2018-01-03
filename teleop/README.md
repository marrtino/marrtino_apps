# Teleop #

## Install ##

Download the following packages in your catkin workspace and compile them with catkin_make:

```
https://github.com/Imperoli/gradient_based_navigation
```

For joystick control, you also need the ROS node joy.

```
sudo apt install ros-kinetic-joy
```

For obstacle avoidance, you also need xtion and depth2laser (see xtion app).


## Run ##

* Joystick control

```
roslaunch robot_teleop.launch
```


* Keyboard control

```
roslaunch robot_teleop.launch use_joystick:=false
```

* Keyboard/Joystick control with obstacle avoidance


```
roslaunch robot_teleop_nav.launch  (joystick control)
roslaunch robot_teleop_nav.launch use_joystick:=false (keyboard control)
```

* Visualizing the sensor data

```
rosrun rviz rviz -d robot_nav.rviz
```
