**Advanced Robotics** 



**ISSN: (Print) (Online) Journal homepage: https://www.tandfonline.com/loi/tadr20** 



# **Development and evaluation of a search-andrescue robot Paripreksya 2.0 for WRS 2020** 

**Rajesh Kannan Megalingam, Shree Rajesh Raagul Vadivel, Anandu Rajendraprasad, Akhil Raj, Siddharth Baskar & Ragavendra Balasubramani Marutha Babu** 

**To cite this article:** Rajesh Kannan Megalingam, Shree Rajesh Raagul Vadivel, Anandu Rajendraprasad, Akhil Raj, Siddharth Baskar & Ragavendra Balasubramani Marutha Babu (2022): Development and evaluation of a search-and-rescue robot Paripreksya 2.0 for WRS 2020, Advanced Robotics, DOI: 10.1080/01691864.2022.2117575 

**To link to this article:** <u>https://doi.org/10.1080/01691864.2022.2117575</u> 













View supplementary material Published online: 21 Sep 2022. 



Submit your article to this journal 

Article views: 140 



View related articles 



View Crossmark data 

Full Terms & Conditions of access and use can be found at https://www.tandfonline.com/action/journalInformation?journalCode=tadr20 

ADVANCED ROBOTICS https://doi.org/10.1080/01691864.2022.2117575 



FULL PAPER 



## **Development and evaluation of a search-and-rescue robot Paripreksya 2.0 for WRS 2020** 

Rajesh Kannan Megalingam , Shree Rajesh Raagul Vadivel, Anandu Rajendraprasad, Akhil Raj, Siddharth Baskar and Ragavendra Balasubramani Marutha Babu 

HuT Labs, Department of Electronics and Communication Engineering, Amrita Vishwa Vidyapeetham, Amritapuri, India 

##### **ABSTRACT** 

In recent years, the influence of robotics in search-and-rescue missions has become relevant. Robots can provide human rescue teams with valuable information about the disaster area, track victims and speed up the rescue operation. The disaster robot category challenge at the World Robot Summit (WRS) is a platform where emerging technologies in search-and-rescue robot developments are evaluated. This paper describes the design, development and implementation of a teleoperated allterrain search-and-rescue robot, Paripreksya 2.0, for participation in the Standard Disaster Challenge. ~~The robot was integrated with a 4-DoF robotic manipulator for performing dexterity tasks along with~~ tracks and four assistive flippers for locomotion. The design of the robot was done in SolidWorks and the stability constraints of the robot while climbing stairs and slopes are also calculated. The software of the robot was built on the ROS framework. The robot was designed to perform various tasks including staircase climbing, negotiation of obstacles, opening and closing of valves, manoeuvring, plant inspection, etc. Our team has secured the best-in-class dexterity award at the WRS 2020 challenge. The performance of the robot was evaluated using the scores from different challenges held at the WRS competition. 

##### **ARTICLE HISTORY** 

Received 26 February 2022 Revised 21 June 2022 Accepted 18 August 2022 

##### **KEYWORDS** 

WRS 2020; dexterity; ROS; robotic arm; disaster response 

### **1. Introduction** 

Oil and gas plants, nuclear power plants, chemical industries, and machine and tool manufacturing industries contribute to a country achieving self-sufficiency in terms of technology, economic improvement and contribute to technological improvements in agricultural, medical, automobile and other inevitable industries. This makes these industries inevitable. These plants and infrastructures are prone to natural or manmade disasters like fire, explosions, earthquakes or floods that may result in significant economic damages and may even cause death. Several natural and manmade disasters have resulted in the loss of lives and infrastructure. Immediate response in the disaster-hit area can save lives and minimize the aftereffects. Robots can handle harsh environments which cannot be accessed by human beings. Therefore, industries, governments, and researchers are researching and developing robots that are capable of entering the disaster area and carrying out exploration, fire extinguishing, tracking of victims in the disaster fields, mapping, inspection of equipment, etc. Robots can be deployed 

to regions that would be excessively hazardous or slow access. Robots can carry cameras and thermal imagers to supply pictures and live feeds of the site to create situational awareness and identification of casualties. Some UAV models can carry necessities like cell phones, water, food or emergency treatment supplies [1]. An Unmanned Ground Vehicle (UGV) can be built with a higher payload; therefore, it can have multiple sensors. It can be equipped with a robotic arm which can be used to open/close valves and doors, remove debris, etc. UGVs can be used for visual inspections along with mapping, crack or deformation analysis, by using cameras, ultrasonic sensors, laser sensors or even being able to perform cleaning or maintenance [2–4]. In Ref. [5], various locomotion mechanisms for robots are discussed including spherical, legged, wheeled and tracked locomotion. Track-based locomotion mechanisms have lower levels of complexities compared to other locomotion mechanisms. The size and weight of the robot were other factors that affect the robot’s capabilities. In Ref. [6], optimization of the Centre of Gravity (COG) and pitch angle 

> Supplemental data for this article can be accessed here. https://doi.org/10.1080/01691864.2022.2117575 

> © 2022 Informa UK Limited, trading as Taylor & Francis Group and The Robotics Society of Japan 

**CONTACT** Rajesh Kannan Megalingam rajeshm@am.amrita.edu HuT Labs, Department of Electronics and Communication Engineering, Amrita Vishwa Vidyapeetham, Amritapuri 690525, India 

2 R. K. MEGALINGAM ET AL. 

velocity were employed and a prototype of the robot was built to control the flipper and arm position for various staircases. In Ref. [7], a prototype of a search-and-rescue robot is made and tested in an artificially created disaster scenario considering all the parameters like step fields, sand, gravel and rough terrains. To select the type of material cross-sections required at various places in a chassis, in Ref. [8], software tools like ANSYS, CATIA, Solidworks and HYPERMESH were used to select materials for making hybrid chassis. In Ref. [9] an additive manufacturing solution for low-volume, high-value and highly complex parts and products is presented. The strength of the chassis can be increased by adding reinforcements, thus increasing the strength-to-weight ratio in Ref. [10]. In Ref. [11], free vibration of the fixed free beam by using the experimental approach and finite element analysis (FEA) approach using the Ansys program, and the percentage error between the numerical (FEA) approach and the experimental approach are allowed up to 5%–7%. 

Modern-day robotic systems are complex hardware devices, and they comprise multiple sensors, actuators and control devices [12,13]. The robotic systems are usually managed by complex distributed software frameworks like Robot Operating System (ROS) [14,15]. ROS is an open-source software framework for robotic simulations and hardware applications [16,17]. ROS provides multiple software tools like Gazebo, a robot simulator and Rviz – a real-time visualization tool [18]. The community support for ROS is very strong and can contribute effectively to any kind of robotic application. ROS also supports multiple programming languages like C, C++, Python and JavaScript. The control method used for disaster response robots is critical. Most of the disaster response uses teleoperated control. Teleoperation systems allow the operator to remotely control the robot via sensory feedback, mostly vision and effort [19]. Teleoperation systems require a control device like a joystick or keyboard for their operation and it may require a high level of operator expertise [20]. Teleoperated robots are also used in medicine [21], underwater exploration [22], space activities [23], and nuclear operation [24] to perform tasks in environments that are hazardous [25] or inaccessible to humans. The robot may need separate control devices for mobility and dexterity operations. 

This research work involved the development and evaluation of a search-and-rescue robot Paripreksya 2.0 for participating in World Robot Summit (WRS) 2020. Section 2 of this paper discusses the characteristics of a disaster environment, the requirements that a disaster response robot need to exhibit in these environments and related challenges included in WRS 2020. Section 3 details the development process of the robot and analyses 

the mechanical, electrical and software design aspects. Section 4 presents the WRS standard field construction for the remote participation challenge. Section 5 discusses the performance evaluation of the robot based on the results of WRS 2020, and analysing specific traits of the robot that led us to achieve ‘Best-in-class Dexterity Award’. 

### **2. Characteristics of disaster environment and WRS competition challenges** 

Search-and-rescue teams will face different environmental and technical challenges during disaster response. The rescue robots are expected to perform several tasks which exhibit their manoeuvrability, dexterity and inspection ability in unknown environments. Plant inspection is one of those challenges where innovation is required. The disaster response team needs to check the status of the disaster-hit area remotely as it is hazardous to explore manually the disaster-hit areas. The robot inspecting the area needs to give feedback about the area using cameras or other sensors. The challenges include finding cracks in the walls, checking the status of safety switches, checking leakage, etc. Manoeuvrability is considered the most important quality of a disaster response robot. The robot should navigate through different surfaces, negotiate for a path while moving in congested areas and should be able to access different heights like climbing and descending stairs. 

Opening and closing of valves, knobs and levers are another set of challenges that a robot will face in a disaster-hit area. The dexterity of the robot will come into play while considering this challenge. The robot should have the ability to reach a suitable position, hold the valve and operate the valve. Different types of valves and levers may be encountered during the disaster response. WRS provides a different set of tasks for plant inspection robots and standard disaster response robots. These two categories demand some similar set of abilities that the robot needs to have. A plant inspection robot is intended to have traits including manoeuvrability, exploration and surveying abilities, dexterity, fault detection abilities and the ability to act as a plant disaster response robot when required. The main difference between a plant inspection robot and a disaster response is in the level of diversity they face in their operating environment. Plant inspection robot operates in a well-defined and specific environment and their traits may vary based on the type of industry they operate in. The destination, list of operable objects, fault detection routine and disaster response behaviours are predefined. A standard disaster response robot may face a broad range of diversity in case of operating environments. Even though Paripreksya 2.0 is 

ADVANCED ROBOTICS 3 

designed as a disaster response robot, it can also serve as a plant inspection robot. The survey and exploration abilities with image processing techniques can be used for diagnostics and crack identification in industrial plants. The robot is expected to operate valves and levers in any environment. World Robot Summit (WRS) provides different challenges for performance evaluations of rescue robots, by demonstrating their skills in manoeuvring, mobility, dexterity and exploration tests. These challenges necessarily enforce teams to focus on all aspects of required skills while developing rescue robots. The framework is being updated regularly with respect to the latest market demands. WRS 2020 provided an opportunity for our robot to compete with several other robots from all over the world. Taking part in WRS and sticking to the developing frameworks facilitates the advancement and improvement of rescue robots. We participated in WRS 2020, competing in four tasks: Survey-a-Wall task, Catwalk task, Negotiate task and Meter/Valve task with each of them including various test scenarios. 

Survey-a-Wall task tests the robot’s object detection and exploration capability. The cracks, holes or other objects to be detected are replaced by a QR code. The position of these QR codes needs to be mapped by the robot for the virtual reconstruction of the environment. The environment consists of five walls each placed at different orientations. The front and back faces of each wall consist of three target positions: high, centre and low. The wall numbers, inner and outer walls and origin were defined before starting the task. QR codes representing the holes and cracks are positioned as per the predefined location. 

Catwalk task tests the robot’s manoeuvrability. In this task, the robot needs to ascend and descend stairs to access high ground. This task tests how easily the robot will be able to move through flat terrain, flat terrain with small-to-medium obstacles and inclined terrain with a ramp and uneven terrains. Each step in the staircase has a vertical distance of 0.2 m and a horizontal distance of 0.24 m which makes 40<sup>o</sup> inclination. The tracked wheels and assistive flipper arm ensure contact throughout approaching, climbing and landing. The motors need to provide the torque required to climb the 40<sup>o</sup> inclination. The weight and position of the Center of Gravity also need to be optimized to avoid tipping the robot. Negotiate task tests the ability of robots to navigate in a disaster field with collapsed items that are moveable or negotiated. The test environment involves fixed bars along with movable vertical and diagonal sticks. The robot should be capable of moving in this constrained environment. 

The Meter/Valve task deals with the dexterity of the robot. Objects such as pipes, doors and wooden blocks are considered for manipulation and inspection tasks. 

The robot should inspect, touch, rotate and extract pipes that are placed in various arrangements. Lever valves and round handles are used. Thus, the robot should open doors with lever handles and successfully enter the room. In the Negotiate task, the robot needs to be manoeuvred through a congested passage with protruding objects. This challenge evaluates how effectively the robot can avoid obstacles and find a way through the given passage. In each task, the operator controls the robot remotely with feedback from the camera for as many iterations as possible in a limited time which will be examined by the test administrator. By evaluating the performance of the robot in these tasks, we can compare hardware and software standards among other participants. 

### **3. Design and analysis of the robot** 

The design section covers the mechanical, electronic and software designs of Paripreksya 2.0. The robot was designed in such a way that it includes all qualities required for the WRS 2020 competition and has provisions for future developments. 

#### **_3.1. Mechanical design_** 

This section discusses the system requirements by analysing the various tasks performed by the rescue robot. The rescue robot needs to overcome obstacles and maintain its horizontal balance during inspection and mapping. Embedding two pairs of assistive flipper mechanisms helps in controlling the centre of mass (COM) to avoid backflipping. This was helpful when the robot moves on uneven terrains and views the objects at certain angles that are required for inspection tasks. The robot was expected to run in harsh environments that contain gaps, staircases, irregularly shaped barriers, and various surface materials. Thus, employing tracked belts for the drive and flipper wheel increases the traction capabilities since the robot creates more contact with terrains. The robot was equipped with five degrees of freedom arm and cameras for performing manipulation, inspection and exploration tasks. The functionality of the robot depends on several factors such as size, weight, location of COM and flipper’s geometry. Figure 1a shows the solid works design of Paripreksya 2.0. All components, equipment and fasteners of the robot were designed and modelled in SolidWorks for initial assessments and weight estimation. Figure 1b shows the image of the actual robot. 

The locomotion system consists of four DC motors with planetary gearboxes (2 for flippers and 2 for traction), 2 customized worm gears, 2 bevel gears, 4 flipper shafts, 16 polyamide pulleys and 6 polyurethane tracks. The two drive motors and one flipper motor was placed in 

4 R. K. MEGALINGAM ET AL. 



<!-- Start of picture text -->
wd<br>Gripper aie ot 2<br>‘e oe<br>—tensioner Po JF@ af<br>=y4<br>(a) (b)<br><!-- End of picture text -->

**Figure 1.** (a) SolidWorks model of Paripreksya 2.0. (b) Pariprekshya 2.0. 



<!-- Start of picture text -->
Ev,<br>Main track alia pecs setetene<br>Flipper shaft ars ) f<br>: I;<br>Coupler<br>my.<br>Worm eReoa»<br>cr ———fpPs |i<br>" an of _<br>2 “abana<br>(a) (b)<br><!-- End of picture text -->

**Figure 2.** (a) Locomotion mechanism SolidWorks design. (b) Locomotion mechanism. 

the front to maintain the COM in the optimum position which will be discussed later front and lower as possible, thus avoiding backflipping. Figure 2a depicts the locomotion mechanism, in which each pair of flippers are driven by one worm gear. Similarly, the drive at each side of the body was driven by one bevel gear. The bevel gearbox was coupled to the pulley, which drives all tracks on that side. The flipper shaft passes through the pulleys and one end of the flipper shaft was coupled to the worm gearbox through a coupler and the other end was connected to the flipper plate. The tension of the tracks was adjusted by using the bolts in the flipper. Figure 2b shows the drive train of the actual robot. The worm gearbox, chassis and flipper arm are made of aluminium and mild steel to make the structure weightless and reliable in the long run. 

#### **_3.1.1. Torque requirement analysis_** 

After the initial estimation of the dimensions and weight of the robot from the SolidWorks model, we selected the appropriate motor and gearbox requirements considering the commercially available components in 

the market. For input power calculation, we selected the two most challenging scenarios that are performed in missions: lifting the robot with flippers and climbing the staircase. As they require the highest power consumption, flippers assist the robot during climbing an obstacle above a certain height, climbing stairs and negotiating obstacles by lifting the robot. The most challenging situation was chosen as the flippers extend fully and the entire robot weight was balanced by the robot. Table 1 shows the symbols used for dynamic modelling. 

Figure 3 represents the free body diagram of the robot for torque calculation. From Figure 3, forces along the _y_ axis<sup>�</sup> x _Fy_ = 0 _WR_ ∗ _g_ = _F_ 1 + _F_ 2 (1) 

The moment at the back flipper is as follows: 





ADVANCED ROBOTICS 5 



<!-- Start of picture text -->
—<br>at tr<br><!-- End of picture text -->

**Figure 3.** Free body diagram for flipper torque calculation. 

**Table 1.** Symbol definition. 

|Symbols|Definition|
|---|---|
|_WR_|The total weight of the robot with arm at the centre of mass<br>(44 kg)|
|_Fa_|Flipper arm length (0.28 m)|
|_x_1|Distance between the centre of mass and point of contact with<br>ground (0.36 m)|
|_x_2|Distance between the two contact points (0.98 m)|
|_L_1|The location of C.G from the end contact point during stair<br>case climbing in_x-_axis (0.15 m)|
|_L_2|The location of C.G from the end contact point during stair<br>case climbing in_y-_axis varies during the motion (m)|
|_N_|The normal force from the staircase on the robot (N)<br>|
|_Ff_|Frictional force from the staircase on the robot (N)<br>|
|_θ_<br>|Maximum Inclination angle of staircase the robot can climb<br>(degree)<br>|
|˙_xc_<br>|Velocity of COM in_x_-direction (m)<br>|
|˙_yc_|Velocity of COM in_y_-direction (m)|
|_M_<br>˙|Mass of the robot (kg)|
|_φ_|Angular velocity of the drive wheel (degree/s)<br>|
|I|Area moment of inertia of the wheels and track (kgm<sup>2</sup>)|
|_W_|Weight of the robot|
|_F_LO|Forces in the longitudinal direction|
|r|Radius of the wheel (9 cm)|
|V|Linear velocity of the robot (0.5 m/s)|
|_T_|Torque applied to the drive unit|



From (1) and (2), the torque required by the flippers is T = _F_ 2 ∗ _Fa_ = 75 Nm 

The GR-EP-45 Gimson High power DC motor with a planetary gearbox with 188:1 reduction coupled to the worm gear 30:1 reduction was selected for the flipper mechanism. The motor provides a continuous torque of 0.015 Nm coupled to the planetary gearbox and the worm gear produces 84.6 Nm. The worm gear and planetary gearbox have an efficiency of 93% and 97%, respectively, which makes the final output torque 75.5 Nm. 

During the climbing of the staircase, the robot needs to be stable and the motors need to provide the necessary torque for the robot to climb the staircase. To ensure the stability of the robot, the tipping angle was calculated by deriving the dynamic model. The centre of mass location was determined using SolidWorks. 



<!-- Start of picture text -->
4 i<br>oo A<br>&<br><!-- End of picture text -->

**Figure 4.** Free body diagram for staircase climbing scenario. 

The centre of gravity is a critical element when determining the stability of during staircase climbing. By manipulating the location of COM, we can prevent the robot from tipping over and rolling over. This tip-over stability during staircase climbing was determined by dynamic modelling. Figure 4 shows the free-body diagram of the robot during the staircase climbing scenario. 

Summation of forces in the vertical direction is given by 



6 R. K. MEGALINGAM ET AL. 

Summation of forces in the horizontal direction is given by 







The moment at end of the robot flipper is as follows: 



Then, the system tip-back occurs when 





Here, _L_ 2 remains constant throughout the motion of the robot. As the robot climbs the staircase, the end contact point keeps changing and _L_ 1 varies continuously. Thus, the stability of the robot was determined by the flipper angle as it affects _L_ 1. For the WRS challenge, the angle of the staircase required to climb was 40°. The robot was designed to climb 45° to demonstrate a stable performance during the competition. The robot was analysed for approaching, climbing and descending the stairs. The flipper arm length was optimized to 0.28 m by trial and error method using SolidWorks. The torque requirement of the robot while climbing the staircase in the dynamic model was derived using the Euler Lagrangian method [26]. 

Equations (6) and (7) represent the Kinematics equations 



From the Euler Lagrangian method, we get: 





From (8), we get: 









_Iφ_<sup>¨</sup> = _T_ − _(L_ 3 − _L_ 2 _)(Mv_ ˙ + _W_ sin _θ)_ 



_Iφ_<sup>¨</sup> = _T_ − _M(L_ 3 − _L_ 2 _)_<sup>2 ¨</sup> _φ_ − _W(L_ 3 − _L_ 2 _)_ sin _θ_ 





Equations (10) and (11) are the dynamic model equations of the robot. By integrating twice, we get the position of the robot as a function of time. So the required motor torque was found based on which torque gives the desired velocity and position as a function of time. Thus, we require 20 Nm of output torque by considering the desired locomotion speed to be higher than 0.5 m/s. Since two DC motors are considered for the locomotion, 10 Nm should be provided by each motor. The GR-EP-45 Gimson High power DC motor with a planetary gearbox with 188:1 reduction coupled to the bevel gear 4:1 reduction was selected for each chassis. The motor provides 0.015 Nm continuous torque and the planetary and bevel gear makes it 11.28 Nm. The bevel gear and planetary gearbox have an efficiency of 93% and 97%, respectively, which makes 10.5 Nm torque available to the drive wheels which is greater than the required torque. After the design and torque calculation, the robot proceeded for purchase and fabrication. 

#### **_3.2. Design of robotic arm_** 

The arm is an essential component of the robot as it has to operate valves, open/close doors and pick/place objects. In this section, we explain the mechanical design, actuator selection, and the workspace of the manipulator. Figure 5 represents the reference frames and joint angle of the robotic arm. As depicted in Figure 5, it was a 4-DOF arm made of rotational joints, including the gripper’s jaw. For all of the joints, DC motors were selected because of their high resolution, output torque and compact design. Links are made of steel and aluminium to provide a rigid structure and it also has the advantage of availability and manufacturability. Links 1 and 2 set the orientation of the whole arm relative to the robot; Links 3 and 4 are mainly in the operation of the end-effector. Link 

ADVANCED ROBOTICS 7 



<!-- Start of picture text -->
vn<br>yw * Link eS<br>we a i<br>ve, [ ie < 0p [A<br>cS Ve, vs 8 | OZ er“te<br>=1<br><!-- End of picture text -->

**Figure 5.** Robotic arm with reference frame and joint angle. 



<!-- Start of picture text -->
CPF inka ;<br>: ui<br>a K— Link 3<br>i fee Link’2 yon ee<br>\ Ree<br>Screw joint i : ,<br>» Pon. ———® ‘Linear joint<br>,<br>Paid 3: g Sih: . q<br>, eg Re 4 :<br>rs y) Fixed Link %<br>. */ “ “=<br><!-- End of picture text -->

**Figure 6.** 4 D-o-F Robotic arm. 

1 was directly fixed to the motor placed under the platform of the robot. The platform was fixed to the chassis, this helps to improve rigidity and provide smooth motion 

by transferring the bending load to the chassis and the motor experiences only the radial force. Link 2 consists of a steel rod and a prismatic slider which was connected to a screw joint driven by the motor. This linear actuator motor drives the slider through the screw threads and pulls/pushes the circular rod. This mechanism provides high efficiency, high resolution and precise motion with very less backlash for the manipulator. Figure 6 shows the image of the actual robotic arm. Link 3 consists of a DC motor coupled with a spur gear (12:1) gear ratio. Link 4 was made of an L clamp made of aluminium with a DC motor and a coupler. A lightweight 3D-printed plastic gripper with a servo motor was used as the end effector. 

#### **_3.3. Hardware architecture_** 

The robot was developed as a teleoperated robot. A host PC was required to control the robot from a distant place. An Intel NUC powered by an Intel i7 processor was used as the master device. A joystick connected to the host PC was used for teleoperation control. Host PC communicates with Intel NUC using Wi-Fi communication. Two sub-controller circuits that control the drive motors are flippers and a robotic manipulator. The sub-controller circuits are controlled by teensy 3.6. The power supply was divided into two sections. A 24 V LiPO battery provides power for the Intel NUC. A 12 V LiPO battery powers up drive motors, flipper motors and manipulator actuators. Two DC-to-DC step-down converters are used to provide 19 V input and 5 V input. The manipulator control circuit uses two different types of drivers for the robotic arm. The arm base motor, yaw motor and gripper servo motor are controlled by 5 V motor drivers. The linear actuator was controlled using a 12 V motor driver. Two RGB cameras are used in the robot, one mounted on the body and another mounted on the end effector. The body camera and end-effector camera are interfaced 

8 R. K. MEGALINGAM ET AL. 



<!-- Start of picture text -->
Left Drive Motor<br>Body Camera ae ae<br>EndCamera effector , usecommunion EES Motor(4)driver {_teft fipper Motor_]<br>Intel Right flipper Motor<br>NUC<br>Host PC Robotic Arm<br>Joystick<br>Linear Actuator Motor<br>Buck converter(24 v to<br>Battery(24v) i) MotorRoboticdriver-1 Arm<br>Buck converter(12v to<br>Sv)<br>Battery(12 v)<br>—<br><!-- End of picture text -->

**Figure 7.** Hardware architecture. 



<!-- Start of picture text -->
use<br>Body Camera] °™munictton Body Camera<br>= node<br>End effector camera a MotorDrivedriver& tippercontrol<br>rosserat<br>Host PC Control ROS Master communication<br>Signal<br>ROS Slave reception<br>Robotic manipulator<br>7 control<br>node camera node<br>cont<br>Joystick Data Goatol<br><!-- End of picture text -->

**Figure 8.** Software architecture. 

using USB communication with Intel NUC. Figure 7 represents the hardware architecture of the robot. 

#### **_3.4. Software architecture_** 

The software can be divided into three sections, which are master control, motor/flipper driver control and robotic manipulator control. The master control software runs on Intel NUC. Master control software includes ROS master node, data acquisition nodes and control signal receiver node. Data acquisition nodes include a body camera node and an end-effector camera node. Endeffector camera data were given to a QR code scanner 

node which reads the QR code using an Open CVbased image recognition algorithm. The QR code recognition algorithm can be modified with any image recognition algorithm to detect cracks, holes, leakage, fire, etc., within a disaster-hit environment. Multiple rosserial nodes are present to communicate with driver/flipper control and robotic manipulator control. Control signal receiver nodes take in data published from the host PC, and these data were used for controlling flippers, drive motors and robotic arm. An ROS-based joy_node was used to acquire data from the joystick. The joystick was connected to the host PC which was used for visualization and teleoperation. Host PC communicates with Intel 

ADVANCED ROBOTICS 9 



<!-- Start of picture text -->
(CX LIA Cee re<br>(a) (b)<br><!-- End of picture text -->

**Figure 9.** (a) Negotiate task field set-up. (b) Robot taking test run of Negotiate task. 

NUC via Wi-Fi communication as an ROS slave device. Figure 8 represents the Software architecture of the robot. 

### **4. Field construction for WRS remote participation challenge** 

Our team has competed in the remote participation category, due to covid-19 restrictions during the competition time. The construction of the competition field was the first hurdle we faced during the preparation phase. The WRS committee has provided the dimensions for the construction of the field. The details of each field are described in this section. 



**Figure 10.** Survey-a-Wall field set-up. 

#### **_4.1. Negotiate task_** 

The required field for Negotiate task was a 2.4 m × 4.8 m rectangular field. The robot has to move through a fixed path in which protruding obstacles are present. The obstacles are pipes, which can move in one direction. PVC pipes of 60 mm diameter are used to make the movable obstacle. These pipes were fixed stands of 1.2 m height and 1.2 m width. The stands are made from hollow square-type metal pipes. Figure 9a represents the field constructed for Negotiate task and Figure 9b shows the robot during a test run of Negotiate task. 



**Figure 11.** Robot taking test run of Survey-a-Wall task. 

#### **_4.2. Survey-a-Wall task_** 

The Survey-a-Wall task involves the inspection of a wall placed in a 4.8 m × 4.8 m field. The robot has to scan the QR code placed in different places on the wall. The wall was constructed from a five-layer foldable frame made from hollow square-type metal pipes. Multi-wood sheets of 5-mm thickness were screwed on each foldable layer. Four of the five layers, which are 1, 3, 4 and 5 have the same dimension of 1.8 m height and 0.9 m width. The second layer was of size 1.8 m height and 1.2 m width. Figure 10 shows the Survey-a-Wall task set-up and Figure 11 shows the robot during the trial run. 

#### **_4.3. Meter/Valve task_** 

In the Meter/Valve task, the robot needs to read multiple pressure gauges fixed on three-layered structures made from PVC pipe. The height of the structure was 0.9 m and the width was 0.6 m. There were six pressure gauges, two valves and two levers attached to this structure. The field was divided into two sides and the robot can operate five targets on one side. The PVC structure was placed in a rectangular field of dimension 2.4 m × 3.6 m. The PVC structure was fixed on a 1.2 m × 1.2 m square wooden sheet using C-clamps. Figure 12a shows the Meter/Valve 

10 R. K. MEGALINGAM ET AL. 



<!-- Start of picture text -->
ies wl = ay |S J —<br>(a) (b)<br><!-- End of picture text -->

**Figure 12.** (a) Meter/valve set-up. (b) Robot taking test run for Meter/valve task. 

set-up and Figure 12b shows the robot operating a lever during the test run. 

#### **_4.4. Catwalk task_** 

The Catwalk task was meant to test the ability of robots to ascend and descend to higher grounds via staircases. The staircase and higher ground were set up in a rectangular field of size 3.6 m × 2.4 m. Hollow square-type metal pipes are used for the construction of the frame. The frame has a height of 1 m from the ground and a width of 1 m. The stairs have a width of 0.95 m. Wooden sheets are screwed to make the steps. Each step has a width of 0.24 m and a height of 0.2 m. Figure 13 shows the field set-up for the catwalk task and Figure 14 shows the robot during the trial run. 



<!-- Start of picture text -->
ow Se<br>hal uA<br>ore He Ae<br><!-- End of picture text -->

**Figure 13.** Field set-up for Catwalk task. 

### **5. Results and discussions based on the robot’s performance at WRS 2020** 

Our team competed in the remote participation category and we had to submit video footage of each task from four different perspectives and combine them together in a single video. The first perspective was the wideangle view of the field, the second perspective was the close-up of the robot performing the task, the third one was the view of the operator and operating device and the last one was the screen output visible to the operator. 

The robot first attempted the surveying task. The robot has to scan the QR codes on the survey wall within 15 min. The total number of QR codes available on the wall was 30. The robot has to read the QR codes and plot the coordinates to form a map of the wall. Our robot 



<!-- Start of picture text -->
|<br>/jT-hEEYi= Ty) .<br>|)<br>i Lal<br>ik | =<<br><!-- End of picture text -->

**Figure 14.** Robot taking test run for Catwalk. 

finished the task in 9 min 43 s. The robot scanned 28 QR codes out of 30 and created corresponding markers in Rviz. The total points achieved as per rule was 

ADVANCED ROBOTICS 11 



**Figure 15.** Competition footage view of Survey-a-Wall task. 



**Figure 16.** Competition footage view of Negotiate task. 

28. Figure 15 shows the view of competition footage of surveying tasks. 

The second task we attempted was the negotiation challenge. The robot completed the first repetition within 3 min 13 s. The robot completed the second repetition in 5 min 16 s due to some technical issues. The total time taken for the competition was 8 min 29 s. The point achieved as per the rule was 2. Figure 16 shows the robot performing the Negotiate task. 

The performance of the robot in the Meter/Valve task was impressive compared to other tasks. The robot attempted three repetitions in 15 min. For the first attempt, the robot completed all 10 targets from both sides. The first repetition took 7 min 30 s for completion. In the second repetition, the robot completed five targets from one side and three targets from the other 

side, achieving eight points. For the last repetition, the robot was able to complete three targets from one side only. The total points achieved from 3 repetitions was 21 as per the rule. Figure 17 shows the robot performing the Meter/Valve task. 

The last task, we attempted was the Catwalk task. The robot was able to complete two successful repetitions within 6 min 52 s. The point for this task was calculated as (number of repetitions × height of stairs)/total time. The robot achieved 0.29 points as per the rule. Figure 18 shows the robot performing the Catwalk task. 

The results from WRS 2020 remote participation challenge show that Pariprekshya has faced difficulties in avoiding obstacles in the congested areas due to its size. The robot was only able to complete two repetitions within the allocated time. Similar difficulties due to size 

12 R. K. MEGALINGAM ET AL. 



<!-- Start of picture text -->
By 3 : Pa<br>al oe me, —<br>q CI<br><!-- End of picture text -->

**Figure 17.** Competition footage view of Meter/Valve task. 



<!-- Start of picture text -->
alo ma == C __—|<br>4). 4A |e | 1<br>iY.GELAo eee iST= antl<br>7<br>a= a<br>\<br><!-- End of picture text -->

**Figure 18.** Competition footage view of Catwalk task. 

and weight were evident in the Catwalk challenge. The robot was able to climb the stairs at an average speed of 0.29 m/s. The performance in the surveying task was also affected by the size and speed, but even then the robot was able to read all QR codes within the allocated time. The robot performed well in the Meter/Valve task with a score of 21 targets within the allocated time. The robot overcame its limitation in speed with a high level of dexterity in this task. The scores of other teams that competed in the WRS 2020 remote competition were not yet available and we compared the performance of Paripreksya 2.0 with similar results from WRS 2018. The unique design of the 4-DoF robotic arm contributed significantly to achieving the dexterity in this task. Paper [27] presents a plant inspection robot which competed in WRS 2018. Their team have done a faster inspection of 

the environment with the help of UAV and had an added advantage in gauge reading compared to Paripreksya 2.0. In the case of the valve opening task, the UGV mentioned in Ref. [27] was not able to open/close both round valves and levers (0 out of 6 valves). But Paripreksya was able to operate both rounded and lever-type valves. The inspection speed of Paripreksya was less compared to the robot system mentioned in Ref. [27]. Paripreksya was able to read all the gauges three times within 15 min of the task time. 

### **6. Conclusions** 

A disaster response robot was designed and developed for deployment in disaster-hit areas to speed up the rescue process. The robot was designed to exhibit necessary 

ADVANCED ROBOTICS 13 

properties like manoeuvrability, dexterity, surveying, etc. Our robot participated in WRS 2020 competition in the standard disaster response category, and competed in four different tasks: Survey-a-Wall task, Meter/Valve task, Catwalk task and Negotiate task. Since we participated in the remote competition category, we constructed competition fields for each task as per WRS rules. The robot’s ability to inspect a large area was evident from the Survey of a Wall task. The robot was able to detect 28 QR codes and the coordinates are marked on the map. The robot’s ability to move in congested spaces was limited due to its size and weight. The robot was able to climb the stairs and access high ground at an average speed of 0.29 m/s, which was comparatively less. The WRS 2020 results show that the robot’s manoeuvrability needed to be improved. The robot has achieved an impressive score of 21 targets in the Meter/Valve task and our team has got the ‘Best-in-class Dexterity’ award in the remote participation category for this task. Further development like autonomous navigation feature can be included in the robot by the addition of 3D LiDAR and Sonar sensors. The robot’s ability to sense, track and locate victims in the disaster-hit area can be added as an improvement over the existing features. 

### **Disclosure statement** 

No potential conflict of interest was reported by the author(s). 

### **Notes on contributors** 

**_Rajesh Kannan Megalingam_** is the Director of HuT Labs and an assistant professor in the ECE department at Amrita Vishwa Vidyapeetham University, India. He received his bachelor’s degree in engineering from the College of Engineering, Guindy, Chennai, and his master’s degree and PhD from the Amrita Vishwa Vidyapeetham University, Kollam, India. His research areas include Low Power VLSI, Design for Manufacturing and Embedded Systems. He has 7.5 years of work experience and 15 years of research experience. He has worked as a VLSI Design and Verification Engineer at various companies like STMicro Electronics, Insilicon Incorporation, etc., in Bay Area, California, for 6 years. He has published more than 140 research papers at various international conferences, journals and book chapters. He has won several awards including the IEEE Undergraduate Teaching Award 2020, the Outstanding Branch Counselor and Advisor award from IEEE, NJ, USA, the Outstanding Branch Counselor Award from IEEE Kerala Section, Award of Excellence from Amrita University. He is currently leading several research projects in robotics and automation. He has five patents filed in his name. 

**_Shree Rajesh Raagul Vadivel_** received his B.E. degree in electrical engineering from Anna University, Tamil Nadu, India, in 2016, and the M.Tech. degree in digital manufacturing degree in a work-integrated learning program from BITS Pilani University, Pilani, India, in 2020. He worked as an application engineer with Sixth Sense Robotics and Automation Pvt. Ltd., Chennai, India. He is currently working as a Robotic 

Engineer with Humanitarian Technology Labs (HuT Labs) at Amrita Vishwa Vidyapeetham University, Amritapuri, India. His research interests include nonlinear control, adaptive control and system identification. 

**_Anandu Rajendraprasad_** is working as a research assistant at HuT Labs, Amrita Vishwa Vidyapeetham University, India. He received his B.Tech degree in electronics and communication engineering from Cochin University of Science and Technology, Kerala, India, in 2017, and received his M.Tech degree in embedded systems from the APJ Abdul Kalam Technological University, Kerala, India, in 2019. His research areas include robotics, embedded systems and mathematical Modelling in robotics. 

**_Akhil Raj_** was born in Kerala, India, in 1996. He received his B.Tech. degree in electronics and communication engineering from Amrita Vishwa Vidyapeetham University, Kerala, India, in 2018. He is currently working as a Research Assistant at HuT Labs, Amrita Vishwa Vidyapeetham, Kollam, India. He has published two research papers at reputed IEEE conferences. His research areas include robotics, android app development and automation. 

**_Siddharth Baskar_** is a research assistant at the Humanitarian Technology (HuT) Labs at Amrita University. He received his B Tech degree in mechanical engineering from the Amrita school of engineering, Bangalore, India, in 2020. His research interests include FEA, Dynamic analysis, Design and assembly of robotic components. 

**_Ragavendra Balasubramani Marutha Babu_** is working as a research assistant at HuT Labs, Amrita Vishwa Vidyapeetham University, India. He received his B.Tech degree in electronics and instrumentation engineering from the Amrita Vishwa Vidyapeetham University, Coimbatore, India, in 2021. His research areas include robotics, embedded systems and machine learning. 

### **ORCID** 

_Rajesh Kannan Megalingam_ http://orcid.org/0000-0003 -1097-5576 

### **References** 

- [1] Jones J, Conley L, Ackerman R, et al. SMART fire figurehting: the use of unmanned aircraft systems in the fire service. 2015. 

- [2] Yao F, et al. Automatic concrete tunnel inspection robot system. Adv Robot. 2003;17(4):319–337. 

- [3] Bekhit A, Dehghani A, Richardson R. Kinematic analysis and locomotion strategy of a pipe inspection robot concept for operation in active pipelines. Int J Mech Eng Mechatron. 2012;1(2):15–27. 

- [4] Matthies L, et al. A portable, autonomous, urban reconnaissance robot. Rob Auton Syst. 2002;40(2–3):163–172. 

- [5] Nie C, Corcho XP, Spenko M. Robots on the move: versatility and complexity in mobile robot locomotion. Rob Autom Mag IEEE. 2013;20(4):72–82. doi:10.1109/MRA. 2013.2248310. 

- [6] Mitriakov A, Papadakis P, Mai Nguyen S, et al. Staircase negotiation learning for articulated tracked robots 

14 R. K. MEGALINGAM ET AL. 

with varying degrees of freedom. 2020 IEEE International Symposium on Safety, Security, and Rescue Robotics (SSRR), 2020, pp. 394–400. doi:10.1109/SSRR50563.2020. 9292594. 

- [7] Megalingam RK, Geesala R, Pasumarthi RK, et al. Search and rescue robot with a 4 flipper mechanism. 2020 Fourth International Conference on Inventive Systems and Control (ICISC), 2020, pp. 785–789. doi:10.1109/ICISC47916.2020.9171124. 

- [8] Bhatnagar U, Chaturvedi P, Gupta A. Analysis and Proposed Fabrication of Four- Wheeler Chassis. 2018 International Conference on Automation and Computational Engineering (ICACE), 2018, pp. 40–44. doi:10.1109/ ICACE.2018.8686993. 

- [9] Calignano F, et al. Overview on additive manufacturing technologies. in Proc IEEE. April 2017;105(4):593–612. doi:10.1109/JPROC.2016.2625098. 

- [10] Rasana N, Jayanarayanan K, Mohan HT, et al. Static and dynamic mechanical properties of nanosilica and multiwalled carbon nanotube reinforced acrylonitrile butadiene styrene composites: theoretical mechanism of nanofiller reinforcement. Iran Polym J. 2021;30:1211–1225. doi:10.1007/s13726-021-00962-5. 

- [11] Chaphalkar SP, Khetre SN, Meshram AM. Modal analysis of cantilever beam structure using finite element analysis and experimental analysis. Am J Eng Res. 2015;4(10):178–185. 

- [12] Frei R, Serugendo GDM. The future of complexity engineering. Cent Eur J Eng. 2012;2(2):164–188. 

- [13] Siciliano B, Khatib O. Handbook of robotics. Berlin Heidelberg: Springer; 2008. 

- [14] Stoy K, Christensen D, Brandt D. Self ReconFigureurable robots: an introduction. London: MIT Press; 2010. 

- [15] Ben-Ari M, Mondada F. Elements of robotics [online]. Springer; 2018. 

- [16] Megalingam RK, Rajendraprasad A, Manoharan SK. Comparison of planned path and travelled path using ROS navigation stack. 2020 International Conference for Emerging Technology (INCET), 2020, pp. 1–6. doi:10.1109/INCET49848.2020.9154132. 

- [17] Megalingam RK, Rajendraprasad A, Raj A, et al. SelfE: a self-driving wheelchair for elders and physically challenged. Int J Intell Robot Appl. 2021;5:477–493. doi:10.1007/s41315-021-00209-9. 

- [18] Marian M, Stîngă F, Georgescu M-T, et al. A ROSbased Control Application for a Robotic Platform Using the Gazebo 3D Simulator. 2020 21th International Carpathian Control Conference (ICCC), 2020, pp. 1–5. doi:10.1109/ICCC49264.2020.9257256. 

- [19] Baklouti S, Gallot G, Viaud J, et al. On the improvement of ROS-based control for teleoperated yaskawa robots. Appl Sci. 2021;11(16):7190. doi:10.3390/app11167 190. 

- [20] Hedayati H, Walker M, Szafir D. Improving collocated robot teleoperation with augmented reality. Proceedings of the 2018 ACM/IEEE International Conference on Human-Robot Interaction, Chicago, IL, USA, 5–8 March 2018; pp. 78–86. 

- [21] Taylor RH, Funda J, Eldridge B, et al. A telerobotic assistant for laparoscopic surgery. IEEE Eng Med Biol Mag. 1995;14:279–288. 

- [22] Yoerger D, Slotine JJ. Supervisory control architecture for underwater teleoperation. Proceedings of the 1987 IEEE International Conference on Robotics and Automation, Raleigh, NC, USA, 31 March–3 April 1987; Volume 4, pp. 2068–2073. 

- [23] Menchaca-Brandan MA, Liu AM, Oman CM, et al. Influence of perspective-taking and mental rotation abilities in space teleoperation”, Proceedings of the ACM/IEEE International Conference on Human-Robot Interaction, Arlington, VA, USA, 10–12 March 2007; pp. 271– 278. 

- [24] Clement G, Vertut J, Fournier R, et al. An overview of CAT control in nuclear services. Proceedings of the 1985 IEEE International Conference on Robotics and Automation, St. Louis, MO, USA, 25–28 March 1985; Volume 2, pp. 713–718. 

- [25] Smith FM, Backman DK, Jacobsen SC. Telerobotic manipulator for hazardous environments. J Robot Syst. 1992;9:251–260. 

- [26] Endo D, Watanabe A, Nagatani K. Stair climbing control for 4-DOF tracked vehicle based on internal sensors. J Rob. 2017;2:18. Article ID 3624589, 2017. 

- [27] Miura H, Watanabe A, Okugawa M, et al. Plant inspection by using a ground vehicle and an aerial robot: lessons learned from plant disaster prevention challenge in world robot summit 2018. Adv Robot. 2020;34(2):104–118. doi:10.1080/01691864.2019.1690575. 

