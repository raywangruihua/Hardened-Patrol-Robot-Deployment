# Hardening Patrol Robot Deployment

This is intended as a reference for projects involving the Yahboom ROSMASTER X3 and for using the SROS2 package with SoftHSM2.

## Table of Contents

- [Summary](#summary)
- [Demonstration](#demonstration)
  - [Setup](#setup)
  - [Voice Control](#voice-control)
  - [Astra Camera](#astra-camera)
  - [Operation](#operation)
    - [Yahboom Navigation](#yahboom-navigation)
    - [SROS2 Enabled Patrol with Privacy Mode](#sros2-enabled-patrol-with-privacy-mode)
  - [SoftHSM2](#softhsm2)

## Summary

I implemented basic privacy blurring features, configured SROS2 and stored cryptographic signatures on SoftHSM2 on a ROSMASTER X3 for this project. For more information on the ROSMASTER, refer to their [github repo](https://github.com/YahboomTechnology/ROSMASTERX3), which comes with lots of tutorials.

## Demonstration

### Setup

If you would like to reproduce the results from this project, copy the `secure_patrol` package in this repository to your ROS2 workspace source folder and build.

Your final workspace directory structure should look like:

```text
ros2_ws/
├── build/
├── install/
├── log/
└── src/
    └── secure_patrol/
        ├── launch/
        ├── models/
        │   └── yolov8n-face-lindevs.onnx
        ├── resource/
        ├── secure_patrol/
        ├── package.xml
        ├── setup.cfg
        └── setup.py
```

The `models/` directory is not tracked in this repository. Download `yolov8n-face-lindevs.onnx` separately and place it as shown.

> [!NOTE]
> Change the filepath in line 118 in [uvc_camera_driver.cpp](ros2_astra_camera/astra_camera/src/uvc_camera_driver.cpp) if you would like to use your own model.

### Voice Control

Privacy mode is toggled via the voice interaction module on the ROSMASTER X3. Begin any instruction by saying **"Hi, Yahboom"**. The standard commands **"car turns left"** and **"car turns right"** toggle **blur** and **selective blur** respectively. It is possible to reconfigure voice commands for the module but the process was too annoying for me to continue.

### Astra Camera

When blurring is **on**, the Astra RGB-D camera publishes blurred frames. This affects both the screen display and RTAB-Map localisation. This change is implemented on the driver level in the implementation files [uvc_camera_driver.cpp](ros2_astra_camera/astra_camera/src/uvc_camera_driver.cpp) and [ob_camera_node.cpp](ros2_astra_camera/astra_camera/src/ob_camera_node.cpp) as well as [uvc_camera_driver.h](ros2_astra_camera/astra_camera/include/astra_camera/uvc_camera_driver.h) and [ob_camera_node.h](ros2_astra_camera/astra_camera/include/astra_camera/ob_camera_node.h). If starting a new project, the same driver files on the ROSMASTER X3 must be replaced and the `astra_camera` package must be rebuilt, which can be found deep inside in `library_ws` with the folder name `ros2_astra_camera`.

> [!TIP]
> If there are any issues with ros2 not launching the new compiled binaries, use this command: `colcon build --packages-select astra_camera --cmake-clean-first`. This removes old binaries that might still be linked used after buiding.

### Operation

#### Yahboom Navigation

For simple rtabmap based nav2 navigation, launch the following files:

```bash
# Terminal 1: Starts the camera
ros2 launch astra_camera astro_pro_plus.launch.xml

# Terminal 2: This should be launched on an external PC, which is connected to the ROSMASTER X3 hotspot. You will also have to download the yahboomcar_nav pacakge from the ROSMASTER and build it on the PC (with ROS2 installed).
ros2 launch yahboomcar_nav display_rtabmap_nav_launch.py

# Terminal 3: Start rtabmap based navigation
ros2 launch yahboomcar_nav navigation_rtabmap_launch.py
```

To give the ROSMASTER movement commands (using the external PC):

1. Click **[2D Pose Estimate]** to set the initial pose of the ROSMASTER
2. For single point navigation, click **[2D Goal Pose]** to set navigation points, and the ROSMASTER will immediately start navigation
3. For multipoint navigation, click **[Panels]**, then select **[Navigation 2]**. Click **[Waypoint Mode]**, then **[Nav2 Goal]** to set waypoints, and click **[Start Navigation]** to make the ROSMASTER navigate to all waypoints in order

#### SROS2 Enabled Patrol with Privacy Mode

To run the full project demonstration, you must first create a map of your test environment by launching the following files:

```bash
# Terminal 1: Launch camera
ros2 launch astra_camera astro_pro_plus.launch.xml

# Terminal 2: Launch rtabmap map builder
ros2 launch yahboomcar_nav map_rtabmap_launch.py

# Terminal 3: This should be launched on an external PC, which is connected to the ROSMASTER X3 hotspot. You will also have to download the yahboomcar_nav package from the ROSMASTER and build it on the PC (with ROS2 installed).
ros2 launch yahboomcar_nav display_rtabmap_launch.py

# Terminal 4: Also launched on external PC, download required yahboom_ctrl package and build. There are other options for joystick controls as well.
ros2 run yahboomcar_ctrl yahboom_keyboard
```

After setting everything up, use the keyboard controls on your external PC to explore the test environment as thoroughly as possible. You can visually see the cloud map being built on rviz2, if everything is configured correctly.

> [!TIP]
> A good test environment is one that is varied. Localisation performance decreases when the environment is uniform, as camera frames captured throughout the room have small differences between them.

> [!TIP]
> Move slowly when operating the ROSMASTER X3. Return to the starting position at the end so that rtabmap can perform loop closure. By default, the map is saved to `~/.ros/rtabmap.db`, and will be overwritten with new launches.

> [!NOTE]
> If there is a large amount of drift between starting and end positions, loop closure must be corrected using `rtabmap-databaseViewer /path/to/map.db`, which should be done on an external PC for ease. Follow the steps below after the map view GUI appears:
>
> 1. Click **[Detect more loop closures]** under the Edit tab
> 2. Click **[Regenerate local grid maps...]** under Edit tab
> 3. Click **[Graph view]** under View tab
> 4. If the start and end nodes still are not linked, then open the **[Constraints view]** under View tab
> 5. Click on the start and end nodes, ensure that the correct indexes are reflected in the main window section.
> 6. Click **[Add]** and click accept on all dialogue boxes to add the new node links.
> 7. Click **[Refine]**.
> 8. Repeat step 2.
> 9. The nodes will now be linked and optimised, save the map.

Then create and configure sros2, which is thankfully automated. Setup is as follows:

```bash
# Terminal 1: Create keystore
mkdir ~/sros2 && cd ~/sros2
ros2 security create_keystore keystore

# Terminal 2: Bringup required hardware and software nodes
ros2 launch secure_patrol patrol_bringup_launch.py

# Terminal 3: Actual patrol algorithm, the patrol path can be edited via the waypoints list in patrol.py
cd ~/ros2_ws/src/secure_patrol/secure_patrol
python patrol.py

# Terminal 1: Capture live policies
ros2 security generate_policy policy.xml
# automically generate all enclaves, keys, permissions and signatures using captured policies
ros2 security generate_artifacts -k keystore -p policy.xml
```

Add the following environmental variables:

```bash
export ROS_SECURITY_KEYSTORE=~/sros2/keystore
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce
```

Finally, run the following files:

```bash
# Optionally run on external machine to view the ROSMASTER X3's internal map as it updates
ros2 launch yahboomcar_nav display_rtabmap_nav_launch.py

# Terminal 1
ros2 launch secure_patrol patrol_bringup_launch.py

# Terminal 2
python ~/ros2_ws/src/secure_patrol/secure_patrol/patrol.py
```

### SoftHSM2

Unfortunately, the ROSMASTER X3 comes prepackaged with ROS2 Humble, which does not support PKCS#11 URIs that link to hardware security modules. However, I did include the script that transfers all enclave private keys to SoftHSM2 that I used.  It is theoretically possible for HSMs to work with more recent distros such as Jazzy. However, I did not want to accidentally brick the ROSMASTER X3 by updating, so I left it as it is.

> ![NOTE]
> Install SoftHSM2 and PKCS#11 with `sudo apt install softhsm2` and `sudo apt install opensc` before using the script.
