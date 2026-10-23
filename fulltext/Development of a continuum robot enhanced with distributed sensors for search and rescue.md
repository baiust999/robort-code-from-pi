Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ https://doi.org/10.1186/s40648-022-00223-x 

**Open Access** 

## **RESEARCH ARTICLE** 



# Development of a continuum robot enhanced with distributed sensors for search and rescue 

Yu Yamauchi<sup>1*</sup> , Yuichi Ambe<sup>2</sup> , Hikaru Nagano<sup>3</sup> , Masashi Konyo<sup>1</sup> , Yoshiaki Bando<sup>4</sup> , Eisuke Ito<sup>1</sup> , Solvi Arnold<sup>5</sup> , Kimitoshi Yamazaki<sup>5</sup> , Katsutoshi Itoyama<sup>6</sup> , Takayuki Okatani<sup>1</sup> , Hiroshi G. Okuno<sup>7</sup> and Satoshi Tadokoro<sup>1</sup> 

### **Abstract** 

Continuum robots can enter narrow spaces and are useful for search and rescue missions in disaster sites. The exploration efficiency at disaster sites improves if the robots can simultaneously acquire several pieces of information. However, a continuum robot that can simultaneously acquire information to such an extent has not yet been designed. This is because attaching multiple sensors to the robot without compromising its body flexibility is challenging. In this study, we installed multiple small sensors in a distributed manner to develop a continuum-robot system with multiple information-gathering functions. In addition, a field experiment with the robot demonstrated that the gathered multiple information has a potential to improve the searching efficiency. Concretely, we developed an active scope camera with sensory functions, which was equipped with a total of 80 distributed sensors, such as inertial measurement units, microphones, speakers, and vibration sensors. Herein, we consider space-saving, noise reduction, and the ease of maintenance for designing the robot. The developed robot can communicate with all the attached sensors even if it is bent with a minimum bending radius of 250 mm. We also developed an operation interface that integrates searchsupport technologies using the information gathered via sensors. We demonstrated the survivor search procedure in a simulated rubble environment of the Fukushima Robot Test Field. We confirmed that the information provided through the operation interface is useful for searching and finding survivors. The limitations of the designed system are also discussed. The development of such a continuum robot system, with a great potential for several applications, extends the application of continuum robots to disaster management and will benefit the community at large. **Keywords:** Sensor systems, Sensor arrays, Sensor fusion, System integration, Search and Rescue robots, Soft robotics, Continuum robots 

### **Background** 

Continuum robots can search narrow spaces and are useful for searching disaster sites, such as inside collapsed buildings [1–15]. For example, we previously developed a flexible long robot, Active Scope Camera (ASC), that is propelled by vibrating its body, which is covered with inclined cilia. This robot has been used to investigate 

*Correspondence:  yamauchi.yu@rm.is.tohoku.ac.jp 

> 1 Graduate School of Information Sciences, Tohoku University, Sendai-shi, Miyagi 980-8579, Japan Full list of author information is available at the end of the article 

collapsed houses after the Kumamoto earthquake and the accident at the Fukushima Daiichi Nuclear Power Plant [1, 2]. Several other continuum robots have been developed. Tsukagoshi et al. developed a cable robot that uses a smooth creeping actuator with tip-growth motion, which can move through narrow paths and tubes [3, 4]. Hawkes et al. developed a cable robot with an inflatable actuator, which can deform passively in response to the environment and move through narrow spaces [5, 6]. Walker et al. developed a cable robot that can change its shape using wires mounted on its body and is based on the structure of thin-stemmed plants. This robot 

> © The Author(s) 2022. **Open Access** This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http:// creat iveco mmons. org/ licen ses/ by/4. 0/. 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 2 of 13 

was successful in numerous experiments in a full-scale mockup of the International Space Station at NASA’s Johnson Space Center [10, 11]. Olympus developed an industrial endoscope that can bend its tip using a wire mounted on its body, and it has been deployed by firefighters in Japan to investigate the inside of collapsed houses during disasters [12]. 

The exploration efficiency at disaster sites improves if continuum robots can acquire various information simultaneously from inside the disaster site. In particular, the combination of multiple sensory information could provide a synergistic effect. For example, if the position of the tip of the robot and the direction of a survivor’s voice can be obtained simultaneously, the area to search for the survivor can be narrowed down with a high accuracy. Similarly, if a 3D map of the rubble and the position of the tip can be acquired simultaneously, the robot operator can detect the explored and unexplored areas and find a safe entry route for rescue workers. Moreover, if the shape of the robot, environment, and contact status of the robot can be simultaneously acquired, the operator can determine whether the robot is stuck in the rubble. In addition, a 3D environmental map can be generated that contains the robot shape and clues pertaining to any potential survivor, such as acoustic information and pictures of the survivors; this would improve the efficiency of communicating information. However, conventional flexible cable robots [1–15] are mainly aimed at improving mobility and, therefore, have not been studied from the perspective of acquiring such multiple information simultaneously. 

We propose an approach to distribute various types of sensors across a flexible cable-shaped robot to enable collection of the aforementioned information. The distribution of small sensors does not compromise the flexibility of the robot. These sensors enable shape estimation, sound source estimation, and contact position estimation. For example, the shape estimation can be performed via multiple distributed inertial measurement units (IMUs) on the body. In addition, the estimation of sound source can be achieved by installing multiple microphones along the length of the body. The contact position of the robot can be estimated from the distributed vibration sensors on the robot body. 

The purpose of this study was to develop a continuum robot system with multiple information-gathering functions by installing multiple distributed sensors. Specifically, we first developed a continuum robot composed of an air-jet floating ASC with a total of 80 distributed IMUs, microphones, speakers, and contact sensors. Owing to the long and thin robot body, the challenges in the development included incorporating a space-saving design, noise reduction, and the ease of maintenance. We 

designed and developed the robot considering these challenges and confirmed that the installed sensors can communicate with each other without any errors. In addition, a high-speed camera was mounted on the robot tip. This camera enables the structure-from-motion technology to locate the robot’s position and generate a 3D map of the debris [2]. It further enables the automatic recognition of clues of survivors by classifying the debris images [16]. Subsequently, we developed an operation interface by incorporating different searching support technologies using the sensor information. Finally, we demonstrated the survivor search procedure in a simulated rubble environment in Fukushima Robot Test Field. We verified that the distributed sensors function properly even in the simulated environment and that presenting the integrated information is useful for search and rescue missions. 

The contributions of this paper are as follows : (1) We developed a flexible continuum robot system, along with its operation interface, using multiple distributed sensors that can acquire multiple sources of information for the search of a disaster site. (2) An experiment in a simulated rubble environment demonstrates the potential of our system for efficient information-gathering in disaster sites. The air-jet floating ASC has been reported in [17], and the searching support technologies using mounted sensors have been reported in [2]. In this paper, we report the details of the design and implementation of distributed sensors from the perspective of system integration. 

### **Related study** 

In the field of rigid snake-like robots, the installation of distributed sensors is a common approach for information-gathering. In general, the robots consist of multiple links connected by servomotors as joints, and each joint angle is measured by a sensor; thus, the entire shape of the robot can be estimated. For example, Choset et al. developed a rigid cortical robot with sensors to investigate the interior of a building that collapsed during the 2017 earthquake in central Mexico [18]. In addition, Takemori et al. developed a sensing, rigid, snake-like robot capable of climbing and descending ladders [19]. In addition, many studies expanded the search range by distributing other types of sensors. For example, Tanaka et al. developed a wheeled rigid cable robot with distributed proximity sensors; the robot can climb and descend stairs using information from these sensors [20]. In addition, Kamegawa et al. developed a rigid cable robot with distributed pressure sensors; the robot can climb and descend pipes by adjusting its shape using the distributed sensors [21]. 

We used this approach for the continuum robot based on an air-jet floating ASC. However, in contrast to the rigid snake-like robot, a lightweight design was required 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 3 of 13 

to enable floating and an overall small design to maintain the body’s flexibility. In this study, by distributing small sensors on the continuum robot, pose estimation was achieved in a lightweight manner that is compatible with air injection. This enabled our robot to convey more information to the operator without losing its search effectiveness in confined spaces, which is one of the principal advantages of continuum robots. 

### **Development of sensor integration system Design policies** 

The design policy of the sensor-integration system, shown in Fig. 1, is described below. The policy is based on three main design principles: sensor configuration for long length, maintainability, and the ease of system integration. 

First, to mount multiple sensors on the robot, sensors that can be daisy-chained need to be developed. This will reduce the number of cables inside the robot and allow for the mounting of many sensors in a limited space. In addition, because the sensor is long, the GND should be thickened to avoid noise. 

Second, the robot must be modularized to facilitate its maintenance and expandability of its functions. To facilitate a change in the robot’s length and the number and types of sensors, the robot is composed of modules connected together, each of which is approximately 1.6 m in length. In addition, we designed easily replaceable structure of the sensor because a large number of sensors increases the risk of failure and the number of times the maintenance is required. 

Third, we developed software modules. Because the robot is equipped with many sensors, it is necessary to develop various elemental technologies using these 



<!-- Start of picture text -->
(3) ROS<br>(2) Easy to replace<br>(2) Module<br>(1) Sensor<br>Active Scope Camera Camera<br><!-- End of picture text -->

**Fig. 1** Schematic of the three design principles of sensor-integration system. (1) Sensors are daisy-chained to accommodate multiple sensors. (2) To facilitate maintenance, the sensors are easily interchangeable, and to facilitate the expandability of its functions, the robot is composed of modules, each approximately 1.6 m in length. (3) To enable modular development of the system, we use ROS to modularize the program 

sensors in the future. Therefore, we promote the modularization of programs using the robot operating system (ROS) to facilitate the development of elemental technologies by multiple researchers. This makes it possible to easily integrate all elemental technologies and to select and use only the necessary ones. 

#### **Development of integrated active scope camera** **_Overview_** 

In this section, we describe the developed ASC with integrated sensory functions, as shown in Fig. 2. The basic specifications of the developed robot are listed in Table 1. It is a long and lightweight robot with a changeable length (1.6–9 m), an outer diameter of 50 mm, and a bodyweight of 5.7 kg (for 7 m length). We discuss the case when the length is 7 m in this paper as an example. We determine the outer diameter based on the previous tube-shaped ASC robots [22, 23]. This is because the previous robot had achieved some promising results. it had been used and succeeded in the accident investigation of the Fukushima Daiichi Nuclear Power Plant. Its basic structure is the same as the tube-shaped ASC robot proposed in a previous study [22, 23]. The robot body is 



<!-- Start of picture text -->
300 mm<br>Speaker,<br>vibration motor<br>300 mm<br>Microphone, IMU,<br>Vibration sensor Biaxial active nozzle<br><!-- End of picture text -->

**Fig. 2** ASC with various sensors, IMUs, microphones, speakers, and vibration sensors distributed on the robot’s body, and a high-speed camera mounted at the tip. An air-jet nozzle is also mounted at the tip, and a cilia-vibration-driving mechanism is mounted across the body 

**Table 1** Specifications of the robot 

|**Items**|**Value**|
|---|---|
|Length|7 m|
|Mass|5.7 kg|
|Diameter|50 mm|
|Floating height of head|400 mm|
|Communication|UART (1 Mbps)|



Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 4 of 13 

made of a polypropylene corrugated tube (38 mm outer diameter, 32 mm inner diameter). Eccentric vibration motors (12 mm diameter, 6600 rpm, and 14.3 G rating) are mounted on the robot at 300 or 400 mm intervals. Inclined cilia (less than 10 mm in length) are attached to the body of the robot in a spiral pattern to generate a propulsive force. In addition, an air-injection nozzle proposed in a previous study [17] is mounted at the tip of the robot, and compressed air is supplied by a compressor at the root through an air tube (12 mm outer diameter, 8 mm inner diameter) inside the robot. This nozzle can generate a reaction force via air injection and change the direction of air injection around two axes. By controlling the direction of the air-jet, the robot can float the tip and move it from left to right. The tip can be floated approximately 400 mm using the air-jets, and the body can be propelled by the cilia-vibration-driving mechanism. 

A total of 80 sensors are installed by distributing IMUs, microphones, speakers, and vibration sensors throughout the body and mounting a camera at the body tip. The number of sensors was set to the maximum possible number without compromising the flexibility of the platform. The details of the mounted sensors are described in the subsequent subsections. In addition, a high-luminance LED is mounted at the robot’s tip because it is expected to search in a dark environment. 

The ASC with sensory function consists of a combination of 1.0, 1.2, or 1.6 m modules. The developed robot consists of five modules, one each of 1.0 m and 1.2 m, and three of 1.6 m. The modular structure will be described in subsequent subsections. 

The robot is controlled by multiple PCs using the ROS network. 

#### **_Mounted sensors_** 

The ASC with sensory function is equipped with an IMU, microphone, speaker, vibration sensor, and camera. The IMU sensor (MPU-9250, _TDK Corporation_ ) was used to estimate the shape of the robot, and the larger the number of segments, the more accurate the shape can be estimated. The physical quantities that can be measured in this system are 6-axes quantities: 3-axes acceleration and 3-axes angular velocity. The microphones (SPM0423HE4H-WB, _Knowles Electronics_ ) were used to determine the direction of the survivor’s voice, and the greater the number of microphones, the more accurately the direction of the survivor’s voice can be estimated. The speakers (GC0251K, _CUI Devices_ ) were used to talk to the survivors. The vibration sensor was used to detect the contact between the robot and the environment. The larger the number of sensors, the more detailed the contact position can be estimated. Because the shape of the robot did not change significantly when it is exploring 



<!-- Start of picture text -->
RASP-ZX Vibration Sensor Microphone IMU<br>Speaker Module<br>Speaker<br>Vibration Module<br><!-- End of picture text -->

**Fig. 3** Photo of RASP-ZX, IMU, microphone, speaker, vibration sensor 

|Power|
|---|
|MIC<br>MIC<br>MIC<br>MIC<br>DCDC<br>GND<br>RASP-ZX|
|**Fig. 4**Wiring diagram of the distributed sensors. The sensors are<br>interconnected by the cables originating from RASP-ZX. A DC–DC<br>converter is installed at each of the four sensors to prevent voltage<br>drop. In addition, a thick GND cable is passed separately to reduce<br>the electrical noise|



narrow spaces, the distance between adjacent sensors was set to 300 mm or 400 mm. The precise details are described in the module structure section. The camera (STC-MCS241U3V, _OMRON Sentech_ ) was used to generate a map of the rubble using simultaneous localization and mapping (SLAM), and the camera with the highest frame rate was installed under the size and weight constraints. The camera was a high-speed camera with a maximum frame rate of approximately 160 fps. 

The distributed sensors were daisy-chained. Because the number of cables that can be passed through the robot is limited by size constraints, we adopted this connection method to reduce the number of cables. RASPZX is a small sampling device consisting of multiple IMU sensors, microphones, speakers, and vibration sensors. RASP-ZX and the sensors are shown in Fig. 3, and their specifications are listed in Table 2. RASP-ZX and the sensors are connected serially by five cables, as shown in Fig. 4. Because the cables are long, a DC–DC converter is used for each module to prevent voltage drops. In addition, a thick ground cable is run separately to prevent communication noise. 

The camera uses optical signals for transmission. Specifically, the USB3.0 signal from the camera is converted to an optical signal and transmitted through an optical cable inside the robot. This is because the size of the repeater cable of USB3.0 signal is too large to be used for this robot. In addition, optical signals are resistant to electrical noise, which solves the problem of electrical noise caused by the long length of the cable. 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 5 of 13 

**Table 2** Specifications of sensors 

|**Items**|**Value**|
|---|---|
|Channel|32|
|Number of IMUs|20|
|Number of Microphones|20|
|Number of speakers|19|
|Number of vibration sensor|20|
|Number of camera|1|
|Acceleration range|±8 G|
|Gyroscope range|±500 deg/s|
|Update cycle of IMUs|2 kHz|
|Update cycle of Microphones|16 kHz|
|Update cycle of vibration sensors|4 kHz|
|Update cycle of camera|160 fps|





<!-- Start of picture text -->
(a) Connector (b)<br>Microphone Connector<br>Power supply<br>signal line Air tube<br>Connector Connector<br>IMU<br>Optical cable<br>Vibration<br>Connector sensor<br><!-- End of picture text -->

**Fig. 5** CAD diagram and photo of the connecting module. **a** Configuration of the sensor fixing part and the power supply connector of the module connection part. **b** Configuration of the connectors of the optical cable and air tube in the module connection section. 180-degree rotation of ( **a** ) 

#### **_Module structure_** 

To facilitate the expansion of functions, the robot is constructed by combining several modules. As shown in Fig. 5, all the cables, such as optical cables, air tubes, power supply, and sensor cables, are connected to each other at connecting modules at both ends of each module. This connecting module consists of two semi-circular cylinders and has a zigzag structure at both edges of the cylinder. Because the corrugated tube has a bellow structure, this zigzag structure interlocks the tube when two semi-circular cylinders sandwich the tube. To prevent rotation, four holes are drilled into the corrugated tube and four claws are installed on the zigzag structure. As a result, the robot module can be easily attached and detached. 

We developed three modules with different functions, as shown in Fig. 6: the first is a 1.6 m general-purpose (body) module with each sensor mounted at a distance of 400 mm, the second is a 1.2 m sensing-specific (chest) module with each sensor mounted at a distance of 300 mm, and the third is a 1.0 m tip (head) module with a 



<!-- Start of picture text -->
Body module<br>Lni kModelu Senso rModelu<br>IMU IMU VIB IMU IMU<br>Mod<br>VIB VIB VIB VIB<br>MIC MIC MIC M IC<br>SPK SPK SPK SPK<br>400 mm 400 mm<br>Chest module<br>Lni kModelu Senso rModelu<br>IMU IMU VIB IMU IMU<br>Mod<br>VIB VIB VIB VIB<br>MIC MIC MIC M IC<br>SPK SPK SPK SPK<br>300 mm 300 mm<br>Head module<br>Lni kModelu Senso rModelu Biaxial active nozzle<br>IMU IMU VIB IMU IMU<br>Mod<br>VIB VIB VIB VIB CAM<br>MIC MIC MIC MIC<br>SPK SPK SPK<br>300 mm 300 mm<br><!-- End of picture text -->

**Fig. 6** Overview of the three types of modules with the different functions that were developed. From the top, they are the: body module, chest module, the head module. The body module is 1.6 m long, and each sensor is mounted at 400 mm intervals. The chest module is 1.2 m long, and the sensors are mounted at 300 mm intervals. The head module is 1.2 m long, with sensors mounted at 300 mm intervals, a 2-DOF active nozzle, and a high-speed camera at the tip 



<!-- Start of picture text -->
(a) (b)<br>Microphone Vibration motor<br>Vibration<br>sensor Speaker<br>IMU<br><!-- End of picture text -->

**Fig. 7** CAD drawing and photo of the fixed part of the sensor. **a** Structure of the fixed part of IMU sensor, microphone, and vibration sensor. **b** Structure of the fixed part of the speaker and vibration motor 

2-DOF active nozzle and a high-speed camera mounted at the tip. The robot can be customized according to different purposes by replacing or deleting modules. 

To facilitate the maintenance of the sensor, the sensor part was designed to be detachable. The structure of the IMU sensors, microphone, speaker, and vibration sensor is shown in Fig. 7. By disconnecting the cable connected to the sensor and removing the sensor-fixing part, only the sensor part can be easily replaced with a spare part. 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 6 of 13 

The same structure is used for the speaker-mounted part to ensure it can be easily replaced. It is connected to the corrugated tube same as the connecting module. 

#### **_System configuration_** 

The system configuration of the ASC with sensory function is shown in Fig. 8. The functions of the control box are (1) vibration-motor control, (2) air-pressure control for the air-injection nozzle, (3) processing of the IMU sensor, microphone, and speaker by RASP-ZX, and (4) processing of the change from USB 3.0 to optical signals using an active optical cable ( _Oki Electric Cable Co., Ltd._ ). Three personal computers (PCs) were installed to control the vibration motor and the air-jet nozzle and pressure, to acquire the data of the distributed sensors, and to acquire the camera image. Each PC was connected to a wired network, and the data were shared via the ROS. The joypad could be used to control the strength of the vibration motor and the pressure and direction of the air-jet. Finally, in addition to the system presented in Fig. 8, some PCs that process different searching-support technologies using the sensor information could be connected through the ROS. 

#### **_Communication test with distributed sensors_** 

We conduct communication tests to evaluate whether the system can communicate with distributed sensors without an error. 



<!-- Start of picture text -->
ROS<br>Node<br>Node Node<br>Node Node<br>Computers<br>Control PC Control PC Control PC<br>Joypad<br>(Mobiliy) (Sensor) (Camera)<br>Control Box<br>Active<br>Control RASP-ZX RASP-ZX<br>Circuit (IMU/VIB) (MIC/SPK) Optical<br>Cable<br>Electro<br>Air<br>Pneumatic<br>Compressor<br>Regulator<br>Biaxial Vibration IMU VIB MIC SPK<br>Active Camera<br>Motor<br>Nozzle<br>IMU VIB MIC SPK<br>Active Scope Camera<br><!-- End of picture text -->

**Fig. 8** System overview of the active scope camera with sensory functions 

In each experiment trial, the system simultaneously acquires data from the 20 IMU sensors, 20 microphones, and 20 vibration sensors for 15 minutes. Then, we evaluate whether there is a communication error or not. We repeat this trial for six patterns by changing robot shapes (3 patterns) and ON-OFF of vibration motors (2 patterns). The presence or absence of vibration was changed to evaluate the vibration’s noise effects from the vibrating motors. 

The details of the three shapes of the robot are shown in Fig. 9, and explained below. 

- (a) Shape stretched as straight as possible and placed on the ground, 

- (b) Shape wound with a minimum bend radius of approximately 250 mm, 

- (c) Shape created by hanging the robot from 4 m above the ground and wrapping the remaining 3 m with a radius of approximately 250 mm. 

We chose the three shapes because these shapes contain characteristic elements which often observed in ASC. 

As a result, we did not detect any communication error for all sensors in all six experiment trials. We confirm that the vibrating motors also do not affect the communication. 

### **Introduction of searching support technologies and development of integrated operation interface** 

We introduce some information-processing technologies [16, 24–27] to support search activities using the sensors mounted on the ASC. Subsequently, we develop an operation interface that displays the integrated searching-support technologies on a single operation screen to assist the operator. Because all the technologies are described in previous studies, only an overview of the integrated information-processing functions is provided below; subsequently, the developed user interface is described. 

#### **Speech enhancement of victims using microphones** 

This technology extracts human voices from the noise of debris and robots. It can be used to help find clues pertaining to survivors and present information on the sources of these voices using multiple microphones [24]. 

#### **Pose estimation using IMU sensor, microphone, and speaker** 

This technique, based on [25], uses distributed IMU sensors, microphones, and speakers to estimate the shape of a flexible continuum robot [26]. This enables us to identify the search path of the tip and the position of the survivor in the rubble. Specifically, the robot shape is estimated from the IMU sensors on the robot, wherein 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 7 of 13 



<!-- Start of picture text -->
@ om P<br>Hil | ih<br>' ¢ i<br>g fe? | {<br><!-- End of picture text -->

**Fig. 9** Photos of the three different shapes of the robot. **a** Shape stretched as straight as possible and placed on the ground. **b** Shape wound with a minimum bend radius of approximately 250 mm. **c** Shape created by hanging the robot from 4 m above the ground and wrapping the remaining 3 m with a radius of about 250 mm 

the drift errors of IMU sensors are compensated for using the distance information that is estimated from the time difference between the generated sound from the speaker and the sound received at each microphone. The estimated position error of the tip was less than 200 mm for a 3 m insertion length. 

monocular high-speed camera and provides information on the movement trajectory of the tip in the rubble and the 3D shape of the environment [2]. This technology achieves online estimation by thinning out the data and retracing using these thinned-out data if the extraction and tracking of feature points fail. 

#### **Estimation of movement trajectory and environmental mapping using high‑speed cameras** 

This technology enables simultaneous estimation of the camera’s movement trajectory and generation of a 3D environment map, known as Visual SLAM, using a 

#### **Automatic recognition and classification system for rubble** 

#### **images** 

This technology enables the automatic recognition and presentation of target objects from camera images and prevents the operator from missing clues related to 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 8 of 13 

the location of survivors. It is possible to construct an image recognizer quickly from a small amount of prior information about the target object [16]. Based on the assumption that training data of the environment to be searched is difficult to obtain, we developed an image recognition system that acquires the ability to distinguish supported categories as quickly as possible based on few instructions from the operator. 

#### **Estimation and presentation of tactile information** 

This technology enables the estimation of the presence and direction of the distributed contact using a vibration sensor. It enables the operator to understand the contact situation of the body, which cannot be identified by a camera and, thus, enables the operator to understand and avoid getting stuck [27]. 

#### **Developed operation interface** 

This section explains what the user interface tells the operator and how the operator should use the interface. The operation interface, which was developed to display the searching-support technology on a single operation screen and support the operation, is shown in Fig. 11. 

The image of the tip camera is shown in the upper left corner of the figure. Up to four images of clues determined using the image recognition are shown in the lower center of the Figure and can be enlarged by selecting them. In the upper right corner, the shape of the robot estimated using the shape estimation is shown. The viewpoints can be switched freely. The lower right image shows the 3D map estimated using Visual SLAM and the trajectory of the robot tip. As with the robot shape above, the viewpoint can be freely switched. The “Voice” light in the upper left corner indicates that the robot can alert the operator when it detects a human voice using voice-enhancement technology. 

The details of the above contents will be explained in the results of the subsequent experiments, but the two contents not integrated in this development are explained below. By combining speech enhancement and shape estimation, it is possible to display a sphere corresponding to the volume of speech at the position of the microphones on the estimated shape. This enables visual prediction of the location of the survivor (Fig. 10). Next, by combining shape estimation and contact estimation, it is possible to display the contact points with the environment on the estimated shape. This enables the operator to visually understand the state of contact with the environment and avoid getting stuck. 



<!-- Start of picture text -->
Shape of the ASC {rac<br>|<br>Front part<br><!-- End of picture text -->

**Fig. 10** Pose estimation of ASC in rubble superposed with the voice magnitude (size of circle) 



<!-- Start of picture text -->
Shape of robot<br>Posture estimation<br>Point cloud of environment<br>An image processing<br>automatically finds work clothes<br>Head trajectory<br>Visual SLAM<br><!-- End of picture text -->

**Fig. 11** Diagram of the user interface used by the operator during operation. In the upper left corner, the camera image or the camera image when an object is found can be seen. In this figure, the camera image when the work clothes are found using the elemental technology is shown. The automatically recognized camera image is shown in the bottom center of the figure and can be viewed when needed. The upper right corner shows the estimated robot shape, and the lower right corner shows the estimated 3D map and the movement trajectory of the robot tip 

### **Evaluation experiment in simulated rubble environment** 

To demonstrate the feasibility of the developed robot to efficiently search for victims, we conducted a victimsearch experiment in a simulated rubble environment. The operator controlled the robot to follow a predetermined path. In this experiment, we focused on whether the integrated information-processing technology can provide useful information for searching victims. 

#### **Experimental methods** 

#### **_Used system_** 

The appearance of the system used in the experiment is shown in Fig. 12. In addition to the developed ASC with sensory functions, a robotic thruster was used to handle the robot root [28]. The robotic thruster can 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 9 of 13 



<!-- Start of picture text -->
oe ee Control BOX ee wr<br>A<br>B<br>ASC Thruster<br>Survivor<br>ee ants - 4 a<br>Control PC<br>Fig. 13<br>Robot Test Field. This field simulates a situation wherein a factory<br>Active Scope Camera office has exploded and rubble is scattered<br><!-- End of picture text -->



<!-- Start of picture text -->
A<br>wr TAD Ih<br>A<br>B<br>Survivor B<br>- 4 a<br><!-- End of picture text -->

**Fig. 13** Photograph of the debris environment at the Fukushima Robot Test Field. This field simulates a situation wherein a factory office has exploded and rubble is scattered 

**Fig. 12** Photograph of the system used in the search experiment. The system consisted of the developed robot, control box for operating the robot, robotic thruster for insertion, and control PC. In addition, four other PCs were used: one for sensor acquisition and three for the elemental technology for information collection described below 

2 m deep and consists of concrete fragments and metal grids. The inside of the building is 3.7 m wide and 2 m deep, and overturned lockers and desks are scattered. The length of the developed robot was set to 7 m to accommodate this environment. 

In the experiment, a simulated survivor (mannequin) was placed under a shelf placed diagonally in the building, and the robot was supposed to maneuver over the debris scattered in front of the building and then enter the building to find the survivor. A speaker was placed near the mannequin to simulate the voice of the survivor. This speaker continuously played the voice of the victim during the experiment. The work clothes that belonged to the survivors were placed between the building and rubble as clues pertaining to their location. We assumed that the automatic recognition technology knew in advance that the clothes were worn by the survivors. 

insert and twist the robot root without damaging the cilia by using flexible rollers and can measure the insertion length used as a reference value for shape estimation. A total of five PCs were used for the experiment: one for the drive system, one for sensor acquisition, and three for the elemental technology to collect the aforementioned information. 

The following five inputs were used by the operator: 

- Cilia vibration drive mechanism: strength of vibration (corresponding to the speed of the robot body’s progress), 

- Air-jet nozzle: Injection volume, injection direction (corresponding to the robot tip’s floating height and direction of travel, respectively), 

#### **_Procedure_** 

The task of the operator was to search for the simulated victims. The experiment was conducted with five people: one person to operate the robot, one person to assist the ASC to enter the insertion machine (assistant operator), and the other three people to operate the informationgathering technologies. The operator and the assistant knew the environmental information in advance. The operator operated the robot visually within the visible range, whereas within the non-visible range, the operator controlled the robot by observing the developed operation interface. 

- Robotic thruster: insertion speed, torsion speed (corresponding to the insertion speed and posture of the robot root, respectively). 

#### **_Environment_** 

The experiments were conducted at the Fukushima Robot Test Field, which is one of the major research and development center of the field robots for land, sea, and air with respect to logistics, infrastructure inspection, and large-scale disasters. The simulated debris environment in which the experiment was conducted is shown in Fig. 13. This environment simulates a situation wherein a factory office has exploded and debris is scattered. The debris scattered in front of the building is 2 m wide and 

In this experiment, we tested four search-support technologies: (1) pose estimation, (2) the estimation of movement trajectory and environmental mapping, (3) automatic recognition, and (4) voice-activity detection. For the pose estimation, we only used IMUs because there is no need to compensate the drift errors 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 10 of 13 

of IMUs owing to the short duration of experiment. For automatic recognition, we trained the network in advance using the images of the clothes of the survivors. The voice-activity detection can detect the human voice using mic sensor data. Note that all the sensors were not used in this experiment, but we used the sensor information of IMUs, a mic, and camera in this experiment. 

#### **Results** 

We explain the result of experiment as time series. From approximately 0 s to 45 s, the robot started from the edge of the debris field and reached the entrance of the building. With passage of time, the robot ran over the debris in front of the building, as shown in Fig. 14. The operator adjusted the direction of the airjet to steer the floating head and pushed the robot from the thruster to climb over the debris (approximately 100 mm high), in addition to vibrating the motors. The image of user interface at 0 s is shown in Fig. 15. Because the robot did not move at all, the estimated robot shape has a small length, and there is no estimated trajectory. 

From approximately 46 s to 139 s, the robot head entered inside the building and started searching for survivors. The robot head kept floating and moved to the interior of the building. The operator also controlled the air-jet directions and insertion speed of thruster. In the image of the user interface at 60 s (Fig. 15), the automatic recognition system found the previously learned work clothes and showed them to the operator. In addition, the voice-activity detection element detected the survivor’s voice (which was played by the speaker) and indicated it in the operator interface. The trajectory information showed that the robot head had moved almost straight toward the building. Furthermore, the estimated shape showed that there is a curved shape near the root, which informed the operator that the robot body slacked because of the difference in the head moving speed and insertion speed of the thruster. 

From approximately 140 s to 170 s, the robot head reached further into the building and steered its course to the right, to find the survivors. In the image of the user interface, at 140 s (Fig. 15), the robot was the closest to the found work clothes, and the position of the found clothes was automatically marked as a gray sphere on the 3D map generated by Visual SLAM. In addition, in the image of the user interface, at 170 s, (Fig. 15), the robot head turned right as indicated by the estimated shape and trajectory. The operator found the mannequin, i.e., a survivor, lying behind a pipe chair as the camera image in the user interface. 



<!-- Start of picture text -->
E i Hy<br>a a haxe ib e<br>. di<br>op ie are<br>0 s<br>mm Se 6A g<br>i a yey<br>d I;<br>Beea= ee<br>15 s<br>iD ik °<br>SL Sa a ae<br>Sect Oe fae tas gS PY<br>Leee<br>30 s Cea<br>Work clothes<br>lt<br>BP a A<br>Rn deg eee<br>45 s ee<br><!-- End of picture text -->

**Fig. 14** Snapshot of the robot starting from the edge of the rubble and reaching the entrance of the building 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 11 of 13 

#### **Lesson learned** 



<!-- Start of picture text -->
Ee 0 s Root<br>Root<br>LA. Discovered work clothes<br>60 s<br>Detect voice<br>Root<br>~ 140 s Sper:<br>Root<br>Victim<br>170 s er eeoo<br><!-- End of picture text -->

**Fig. 15** Snapshot of the user interface. The robot was able to find the survivor by automatically recognizing the survivor’s characteristic work clothes and by estimating the robot’s shape and the movement trajectory of the tip position 

In terms of controlling the robot, the estimated shape information was useful to find the causes of getting stuck. One of the difficulties in moving the robot forward is that when the body is slack, even if the body is pushed from behind, the deflection only increases, and the tip cannot move forward. In this case, it is necessary to pull the body backward, so as to eliminate the deflection, but this situation cannot be clearly understood only from the tip camera. The shape estimation provided by the system enabled the operator to identify the slack and avoid it. 

In terms of search and rescue mission, the sensory information has the potential to improve the efficiency of a search mission. For example, in this experiment, the victim’s clothes were automatically found and mapped in the 3D map. This could be useful in preventing the victims from being overlooked. In addition, the mapping of the clues on the 3D map could help the rescue workers or the owners to rescue victims. As another example, the voice-activity detection method could automatically detect the human voice in a noisy environment in this experiment. This could serve as a great advantage for finding victims as soon as possible. Although the demonstration was based on a predetermined story, we are sure of these promising possibilities. 

Although the results of the present study are promising, some issues need to be addressed in the future . A limitation of the system was that it consumed a considerable amount of time to set up the robot. Because of the large number of information-collection functions, it was necessary to connect multiple PCs (more than three) for effective operation. In addition, some sensor errors occurred, particularly, when launching the robot. Moreover, the experiment was conducted in a signal-known environment; therefore, we could not demonstrate the system efficiency in an unknown environment. 

### **Conclusion** 

In this paper, we proposed a continuum robot that can acquire information from multiple sources, which is necessary for disaster-site exploration, via the decentralized installation of many sensors. An ASC was developed with a sensory function equipped with IMU, microphone, speaker, and contact detection sensors. We also developed an operation interface that displays searching support technologies using distributed sensors on a single operation screen. A search test was conducted for survivors in the simulated rubble environment of the Fukushima Robot Test Field, and the operation interface was able to detect the survivor’s voices, find their belongings, depict the relationship between the insertion position and the location of the belongings, and inform the operator about the search 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 12 of 13 

area and the rubble environment. These results demonstrate the potential of the proposed system for search and rescue missions. 

In the future, we will improve on the issues raised by the simulated rubble experiment. As for the system, we will improve the reliability of the sensors by using another cable connection pattern. For example, one main communication line with many branches for distributed sensors ensures the robustness against the sensor troubles. Experiments will be conducted in varied environments to increase our knowledge of the robot’s performance. Specifically, the resolution and number of sensors need to be optimized because the required number varies depending on the environment. Furthermore, we need to evaluate whether the operator can control the robot using the developed interface in unknown environments. 

##### **Acknowledgements** 

The authors would like to acknowledge the support of the Human-Robot Informatics Laboratory, Graduate School of Information Sciences, Tohoku University, Japan, for their contributions. 

##### **Authors’ contributions** 

YY developed the robot, carried out the experiments, and drafted most part of the manuscript. YA developed the robot and revised the manuscript. HN developed the operation interface and drafted the manuscript. MK conceived of the study, coordinated the study, and critically revised the manuscript. YB developed the software of the speech enhancement and the pose estimation. EI developed the software of the environment mapping using High speed camera. SA developed the software of the automatic recognition and classification system for rubble image. YY, YA, HN, YB, EI, and SA have carried out the demonstration. KY, KI, TO, HO, and ST have conceived of the study and coordinated the study. All authors have read and approved the final manuscript. 

##### **Funding** 

This research was supported by the JSPS Grant-in-Aid for Scientific Research (KAKENHI), Grant Numbers JP19H00748 and JP20J12891. 

##### **Availability of data and materials** 

Not applicable. 

#### **Declarations** 

##### **Competing interests** 

The authors declare that they have no competing interests. 

##### **Author details** 

1 Graduate School of Information Sciences, Tohoku University, Sendai-shi, Miyagi 980-8579, Japan.<sup>2</sup> Tough Cyberphysical AI Research Center, Tohoku University, Sendai-shi, Miyagi 980-8579, Japan.<sup>3</sup> Graduate School of Engineering, Kobe University, Kobe-shi, Hyogo 657-8501, Japan.<sup>4</sup> Artificial Intelligence Research Center (AIRC), National Institute of Advanced Industrial Science and Technology (AIST), Koto-ku, Tokyo 135-0064, Japan.<sup>5</sup> Mechanical Systems Engineering, Shinshu University, Nagano-shi, Nagano 380-0928, Japan. 6 Graduate School of Information Science and Engineering, Tokyo Institute of Technology, Meguro-ku, Tokyo 152-8552, Japan.<sup>7</sup> Institue of Human Robot Co-Creation, Waseda University, Shinjuku-ku, Tokyo 169-8555, Japan. 

Received: 15 December 2021   Accepted: 1 March 2022 



##### **References** 

1. Ambe Y, Yamamoto T, Kojima S, Takane E, Tadakuma K, Konyo M, Tadokoro S (2016) Use of active scope camera in the Kumamoto earthquake to investigate collapsed houses. In: 2016 IEEE International symposium on safety, security, and rescue robotics (SSRR). pp 21–27 . https:// doi. org/ 10. 1109/ SSRR. 2016. 77842 72 

2. Konyo M, Ambe Y, Nagano H, Yamauchi Y, Tadokoro S, Bando Y, Itoyama K, Okuno HG, Okatani T, Shimizu K, Ito E (2019). ImPACT-TRC Thin Serpentine Robot Platform for Urban Search and Rescue. Springer, Cham, pp 25–76. https:// doi. org/ 10. 1007/ 978-3- 030- 05321-5_2 

3. Mishima D, Aoki T, Hirose S (2006). Development of pneumatically controlled expandable arm for search in the environment with tight access. Springer, Berlin. https:// doi. org/ 10. 1007/ 10991 459_ 49 

4. Tsukagoshi H, Arai N, Kiryu I, Kitagawa A (2011) Smooth creeping actuator by tip growth movement aiming for search and rescue operation. In: 2011 IEEE international conference on robotics and automation. pp 1720–1725. https://doi.org/10.1109/ICRA.2011.5980564 

5. ans LH, Blumenschein EWH, Greer JD, Okamura AM (2017) A soft robot that navigates its environment through growth. Sci Robot 2(8):1081– 1094. https:// doi. org/ 10. 1126/ sciro botics. aan30 28 

6. El-Hussieny H, Mehmood U, Mehdi Z, Jeong S, Usman M, Hawkes EW, Okarnura AM, Ryu J (2018) Development and evaluation of an intuitive flexible interface for teleoperating soft growing robots. In: 2018 IEEE/RSJ International conference on intelligent robots and systems (IROS). pp 4995–5002. https:// doi. org/ 10. 1109/ IROS. 2018. 85938 96 

7. Rico JAS, Hirose S, Yamada H, Endo G, Suzumori K (2016) A novel longreach robot with propulsion through water-jet. In: 2016 IEEE workshop on advanced robotics and its social impacts (ARSO). pp 255–260. https:// doi. org/ 10. 1109/ ARSO. 2016. 77362 91 

8. Rico JAS, Endo G, Hirose S, Yamada H (2017) Development of an actuation system based on water jet propulsion for a slim long-reach robot. ROBOMECH J 4(1):8. https:// doi. org/ 10. 1186/ s40648- 017- 0076-4 

9. Takeichi M, Suzumori K, Endo G, Nabae H (2017) Development of a 20-m-long giacometti arm with balloon body based on kinematic model with air resistance. In: 2017 IEEE/RSJ International conference on intelligent robots and systems (IROS). pp 2710–2716. https:// doi. org/ 10. 1109/ IROS. 2017. 82060 97 

10. Nahar D, Yanik PM, Walker ID (2017) Robot tendrils: Long, thin continuum robots for inspection in space operations. In: 2017 IEEE aerospace conference. pp 1–8. https:// doi. org/ 10. 1109/ AERO. 2017. 79439 40 

11. Wooten M, Frazelle C, Walker ID, Kapadia A, Lee JH (2018) Exploration and inspection with vine-inspired continuum robots. In: 2018 IEEE International conference on robotics and automation (ICRA). pp 1–5. https:// doi. org/ 10. 1109/ ICRA. 2018. 84611 32 

12. Olympus: IPLEX IV9675RX - SV100. https:// www. olymp us- ims. com/ en/ rviprodu cts/ iplex- rx/. Accessed 25 Feb 2022 

13. Horigome A, Yamada H, Endo G, Sen S, Hirose S, Fukushima EF (2014) Development of a coupled tendon-driven 3d multi-joint manipulator. In: 2014 IEEE International conference on robotics and automation (ICRA). pp 5915–5920. https:// doi. org/ 10. 1109/ ICRA. 2014. 69077 30 

14. Horigome A, Endo G, Suzumori K, Nabae H (2016) Design of a weightcompensated and coupled tendon-driven articulated long-reach manipulator. In: 2016 IEEE/SICE International symposium on system integration (SII). pp 598–603. https:// doi. org/ 10. 1109/ SII. 2016. 78440 64 

15. OC Robotics: Series II, X125 System (2016) http:// www. ocrob otics. com/ techn ology-/ series- ii- x125- system/. Accessed 25 Feb 2022 

16. Arnold S, Yamazaki K (2017) Real-time scene parsing by means of a convolutional neural network for mobile robots in disaster scenarios. In: 2017 IEEE International conference on information and automation (ICIA). pp 201–207. https:// doi. org/ 10. 1109/ ICInfA. 2017. 80789 06 

17. Ishii A, Ambe Y, Yamauchi Y, Ando H, Konyo M, Tadakuma K, Tadokoro S (2018) Design and development of biaxial active nozzle with flexible flow channel for air floating active scope camera. In: 2018 IEEE/RSJ International conference on intelligent robots and systems (IROS). pp 442–449. https:// doi. org/ 10. 1109/ IROS. 2018. 85944 37 

18. Whitman J, Zevallos N, Travers M, Choset H Snake (2018) Robot Urban search after the 2017 Mexico City earthquake. In: 2018 IEEE International symposium on safety, security, and rescue robotics (SSRR). pp 1–6. https:// doi. org/ 10. 1109/ SSRR. 2018. 84686 33 

Yamauchi _et al. ROBOMECH Journal             (2022) 9:8_ 

Page 13 of 13 

19. Takemori T, Tanaka M, Matsuno F (2018) Ladder climbing with a snake robot. In: 2018 IEEE/RSJ International conference on intelligent robots and systems (IROS). pp 1–9. https:// doi. org/ 10. 1109/ IROS. 2018. 85944 11 

20. Tanaka M, Tanaka K (2015) Control of a snake robot for ascending and descending steps. IEEE Trans Robot 31(2):511–520. https:// doi. org/ 10. 1109/ TRO. 2015. 24006 55 

21. Kamegawa T, Akiyama T, Suzuki Y, Kishutani T, Gofuku (2020) A threedimensional reflexive behavior by a snake robot with full circumference pressure sensors. In: 2020 IEEE/SICE International symposium on system integration (SII). pp 897–902. https:// doi. org/ 10. 1109/ SII46 433. 2020. 90262 45 

22. Namari H, Wakana, K, Ishikura M, Konyo M, Tadokoro S (2012) Tube-type active scope camera with high mobility and practical functionality. In: 2012 IEEE/RSJ International conference on intelligent robots and systems. pp 3679–3686. https:// doi. org/ 10. 1109/ IROS. 2012. 63861 72 

23. Fukuda J, Konyo M, Takeuchi E, Tadokoro S (2014) Remote vertical exploration by Active Scope Camera into collapsed buildings. In: 2014 IEEE/RSJ International conference on intelligent robots and systems. pp 1882–1888. https:// doi. org/ 10. 1109/ IROS. 2014. 69428 10 

24. Bando Y, Itoyama K, Konyo M, Tadokoro S, Nakadai K, Yoshii K, Kawahara T, Okuno HG (2017) Speech enhancement based on Bayesian low-rank and sparse decomposition of multichannel magnitude spectrograms. IEEE/ ACM Trans Audio Speech Language Process 26(2):215–230 

25. Bando Y, Itoyama K, Konyo M, Tadokoro S, Nakadai K, Yoshii K, Okuno HG (2015) Microphone-accelerometer based 3D posture estimation for a hose-shaped rescue robot. In: 2015 IEEE/RSJ International conference on intelligent robots and systems (IROS). pp 5580–5586. https:// doi. org/ 10. 1109/ IROS. 2015. 73541 68 

26. Bando Y, Ambe Y, Itoyama K, Konyo M, Tadokoro S, Yoshii K, Okuno HG (2018) Multimodal posture estimation of a hose-shaped rescue robot based on an inertial-sound sensor array (in Japanese). In: the robotics and mechatronics conference 2018. pp 2–101 

27. Funamizu T, Nagano H, Konyo M, Tadokoro S (2016) Visuo-haptic transmission of contact information improve operation of active scope camera. In: 2016 IEEE/RSJ International conference on intelligent robots and systems (IROS). pp 1126–1132. https:// doi. org/ 10. 1109/ IROS. 2016. 77591 90 

28. Yamauchi Y, Fujimoto T, Ishii A, Araki S, Ambe Y, Konyo M, Tadakuma K, Tadokoro S (2018) A robotic thruster that can handle hairy flexible cable of serpentine robots for disaster inspection. In: 2018 IEEE/ASME International conference on advanced intelligent mechatronics (AIM). pp 107–113 

### **Publisher’s Note** 

Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations. 



