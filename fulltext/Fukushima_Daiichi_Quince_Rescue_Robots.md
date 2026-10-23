# **Emergency Response to the Nuclear Accident at the Fukushima Daiichi Nuclear Power Plants using Mobile Rescue Robots** 

• • • • • • • • • • • • • • • • • • • • • • • • • • • • • • • • • • • • 

## **Keiji Nagatani, Seiga Kiribayashi, Yoshito Okada, Kazuki Otake, and Kazuya Yoshida**<sup>**∗**</sup> 

_Graduate School of Engineering, Tohoku University, 6-6-01, Aramaki-Aoba, Aoba-ku, Sendai, Miyagi 980-8579, Japan e-mail: keiji@astro.mech.tohoku.ac.jp_ 

## **Satoshi Tadokoro** 

_Graduate School of Information Sciences, Tohoku University, 6-6-01, Aramaki-Aoba, Aoba-ku, Sendai, Miyagi 980-8579, Japan e-mail: tadokoro@astro.mech.tohoku.ac.jp_ 

## **Takeshi Nishimura, Tomoaki Yoshida, and Eiji Koyanagi** 

_Chiba Institute of Technology, 2-17-1, Tsudanuma, Narashino 275-0016, Japan e-mail: koyanagi@furo.org_ 

## **Mineo Fukushima and Shinji Kawatsuma** 

_Japan Atomic Energy Agency, 4-49, Muramatsu, Tokai-mura, Naka-gun, Ibaraki 319-1184, Japan e-mail: fukushima.mineo@jaea.go.jp_ 

Received 13 March 2012; accepted 10 August 2012 

On March 11, 2011, a massive earthquake (magnitude 9.0) and accompanying tsunami hit the Tohoku region of eastern Japan. Since then, the Fukushima Daiichi Nuclear Power Plants have been facing a crisis due to the loss of all power that resulted from the meltdown accidents. Three buildings housing nuclear reactors were seriously damaged from hydrogen explosions, and, in one building, the nuclear reactions became out of control. It was too dangerous for humans to enter the buildings to inspect the damage because radioactive materials were also being released. In response to this crisis, it was decided that mobile rescue robots would be used to carry out surveillance missions. The mobile rescue robots needed could not be delivered to the Tokyo Electric Power Company (TEPCO) until various technical issues were resolved. Those issues involved hardware reliability, communication functions, and the ability of the robots’ electronic components to withstand radiation. Additional sensors and functionality that would enable the robots to respond effectively to the crisis were also needed. Available robots were therefore retrofitted for the disaster reponse missions. First, the radiation tolerance of the electronic componenets was checked by means of gamma ray irradiation tests, which were conducted using the facilities of the Japan Atomic Energy Agency (JAEA). The commercial electronic devices used in the original robot systems operated long enough (more than 100 h at a 10% safety margin) in the assumed environment (100 mGy/h). Next, the usability of wireless communication in the target environment was assessed. Such tests were not possible in the target environment itself, so they were performed at the Hamaoka Daiichi Nuclear Power Plants, which are similar to the target environment. As previously predicted, the test results indicated that robust wireless communication would not be possible in the reactor buildings. It was therefore determined that a wired communication device would need to be installed. After TEPCO’s official urgent mission proposal was received, the team mounted additional devices to facilitate the installation of a water gauge in the basement of the reactor buildings to determine flooding levels. While these preparations were taking place, prospective robot operators from TEPCO trained in a laboratory environment. Finally, one of the robots was delivered to the Fukushima Daiichi Nuclear Power Plants on June 20, 2011, where it performed a number of important missions inside the buildings. In this paper, the requirements for the exploration mission in the Fukushima Daiichi Nuclear Power Plants are presented, the implementation is discussed, and the results of the mission are reported.<sup>⃝C</sup> 2012 Wiley Periodicals, Inc. 

## **1. INTRODUCTION** 

## **1.1. Background** 

∗Webpage: http://www.astro.mech.tohoku.ac.jp/ 

On March 11, 2011, a massive earthquake and accompanying tsunami hit the Tohoku region of eastern Japan, 

Journal of Field Robotics 30(1), 44–63 (2013) ⃝C 2012 Wiley Periodicals, Inc. View this article online at wileyonlinelibrary.com<sup>•</sup> DOI: 10.1002/rob.21439 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **45** 


Figure 1. Rescue mobile robots, called Quince. 

claiming many lives. The number of collapsed houses totaled more than 350,000, and over 20,000 people were confirmed as either missing or dead. The Fukushima Daiichi Nuclear Power Plants also sustained extensive damage in the disaster, which resulted in a total loss of power. Meltdown accidents ensued during which radioactive materials were released. In the final analysis, three buildings housing nuclear reactors were seriously damaged due to hydrogen explosions, and, in one building, the nuclear reactions became out of control. The reactors’ cores are currently being cooled by water and their condition was recently stabilized. This prompted the Japanese Prime Minister to declare an end to the atomic-power accident. However, as of February, 2012, a conclusive solution to the problem remains elusive. 

In this emergency, the objective of the first disaster response mission was to assess the damage to the target environment, including taking dose measurements at the disaster site. However, the site, both outside and inside the buildings housing the nuclear reactors, proved very dangerous for humans because of the potential for high radiation exposure due to the release of radioactive materials. Therefore, exploration using mobile robot technology was crucial for this and subsequent missions. 

The authors’ joint research group, with support from the New Energy and Industrial Technology Development Organization (NEDO), had been researching and developing tracked robots to assist rescue crews in search and rescue missions in dangerous environments, particularly in underground malls (Rohmer et al., 2010). Some of the robots developed, called Quince robots, were designed for practical use in search and rescue missions. The Quince robots are waterproof and highly mobile over rough terrain 

(Figure 1). However, their hardware reliability, communication systems, and basic sensors were considered inadequate for operations as part of the disaster response effort in Fukushima. Furthermore, unlike other disaster situations, this accident resulted in high radiation levels. Without testing, it was impossible to know how long the equipment in the robots could operate in such an extreme environment. Therefore, in March of 2011, in a joint effort with the Tokyo Electric Power Company (TEPCO) and NEDO an urgent project was initiated to retrofit the robots for disaster response missions in the Fukushima Daiichi Nuclear Power Plants. 

## **1.2. Summary of Mission Requirements and Solution** 

At first, the response tasks informally given by TEPCO required that the robot conduct investigations and dose measurement missions inside and outside the reactor buildings. In this mission, the following issues needed to be considered: 

### **1** . **Mobility** 

The robot was expected to traverse bumps, stairs in reactor buildings, and rubble caused by hydrogen explosions. The Quince robot already had the capability to satisfy the above requirements because it was designed for practical use in search and rescue missions (Yoshida et al., 2009). Therefore, the details of Quince’s mobility will not be covered in this paper. 

### **2** . **Radiation hardness** 

In contrast to other disaster situations, one of the aspects of this mission was high radiation exposure. 

_Journal of Field Robotics_ DOI 10.1002/rob 

**46** • _Journal of Field Robotics—2013_ 

At that time, Quince was composed of conventional electronic devices, and there was limited information about how well they would survive exposure to gamma rays. Therefore, the devices’ ability to tolerate radiation needed to be investigated. 

- **3** . **Communication** 

In the NEDO project, a hybrid mesh network was developed, which included both a wired mesh network and a wireless mesh network, for multirobot teleoperation over a wide area (Nagatani et al., 2007). The target enviroment reactor buildings were relatively small compared to what the hybrid network was designed for. However, the reactor buildings contained thick concrete walls that blocked gamma rays, making it highly probable that radio communication would also be inhibited. Therefore, the condition of signal reception inside the buildings needed to be checked. In the case of poor reception, a wired-only communication solution would be required to ensure reliable communication during the mission. 

- **4** . **Mounting sensors** 

One essential requirement in the mission was to have the Quince robot equipped with a dose measurement function, which the robot originally lacked. In addition, 3D mapping was considered to be a very good tool for understanding the disaster environment. Therefore, some modifications to the sensors were required in order to facilitate the mission. 

- **5** . **Hardware reliability** 

In the mission, the operators were designated to be TEPCO employees, rather than engineers familiar with the design and development of Quince. This meant that the robot would need to be controllable by novice operators. Furthermore, once the robot was given to TEPCO, maintenance or any changes requiring physical contact with the robot would not be permitted. This is because the robot would be exposed to radiation during the mission, making it unsafe for human contact after delivery to TEPCO. Considering the above situation, assurance was needed that the hardware used for the robot was sufficiently reliable. Significant effort was devoted to rebuilding Quince to meet these requirements, but details are omitted from this report due to their relative triviality. [Some examples of the improvements made are described in Nagatani et al. (2011b).] 

TEPCO provided a formal mission description at the beginning of May, 2011, during the retrofitting stage. The main mission was identical to the informal mission specifications determined prior to the rebuilding project, but it included additional tasks: (1) a contaminated-watersampling task and (2) a water gauge installation task in the basement of the reactor buildings. For this extra mission, the following issues needed to be considered: 

- **1** . **Function for water gauge installation** 

   - The new tasks required a scooping motion for contaminated water in the basement, and the installation of a water gauge. The system needed to be implemented rapidly, so a simple two-degrees-of-freedom (2-DOF) manipulator was used for both tasks. 

- **2** . **Countermeasures against overweight** 

   - Due to the additional equipment mass and the new requirement to traverse downstairs to the basement of the building, new complications arose. The angle of the stairs to the basement (42<sup>◦</sup> ) was steeper than that of the stairs to the upper floors (40<sup>◦</sup> ). Thus, countermeasures against imbalance needed to be considered. 

In this paper, the process of retrofitting pre-existing robots and supporting key personnel in response to this nuclear emergency situation is detailed. A step-by-step explanation is provided for how each of the above objectives was fulfilled. Finally, a field report on actual missions conducted by the Quince rescue robot in the Fukushima Daiichi Nuclear Power Plants is included. 

## **1.3. Related Work** 

In this section, other work related to the 2011 Fukushima disaster response project is analyzed. Prior to the crisis at the Fukushima Daiichi nuclear plants, the world faced only two such serious nuclear accidents: the Three Mile Island Unit-2 (TMI-2) on March 28, 1979, and the Chernobyl reactor unit 4 in March of 1986. In both accidents, teleoperated robots were used for recovery operations. 

Hess and Metzger (1985) reported on the steady progress at TMI-2 and how some of the activities of the robots aided the recovery. A detailed report about the robotic system used in TMI-2 is also given in Foltman (1986). According to these reports, several types of teleoperated robots were used not only for photographic/radiological inspection, but also for work such as concrete sampling and a decontamination task using a high-pressure scrubber. In the Fukushima Daiichi nuclear plants, these types of working robots will be necessary in the near future. However, the current requirement is an inspection task to obtain information about the environment. In particular, one of the features of the Fukushima case was the task of carrying out inspections through very narrow and steep stairs. 

In contrast to TMI-2, it was very difficult to obtain extensive information about robotic activities at Chernobyl. On page 9 in Bennett and Posey (1997), there is a small report that indicates that sophisticated robotic machinery failed due to high radiation. This led to the use of simple robots with interchangeable parts and a common vehicle platform for tasks such a dust suppression, bore hole sampling, grasping, air sampling, sawing, loading cranes, and scooping up samples. In the target environment in the Fukushima project, the anticipated dose rate was not as 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **47** 

high as that in Chernobyl, so the above problem was not an issue. However, the potential for this kind of problem needs to be taken into consideration for future missions. 

After the Chernobyl accident, some teleoperated robots were applied to survey and maintain the nuclear facilities. Oak Ridge National Laboratory developed robots for decontamination and decommissioning projects in the Chicago Pile #5 (CP-5) research reactor, located at Argonne National Laboratory in the United States (Noakes et al., 2000; 2011). They used several robotic systems, such as a dual arm work platform, a tracked vehicle for sampling and characterization, and a remote underwater characterization system. 

In Japan, after the criticality accident in 1999 in Tokaimura, six robots were developed for nuclear facility emergency preparedness (Mano, 2001). These robots were typically locomoted on tracks, equipped with manipulators, and weighed over 200 kg. The objectives of these robots were to open doors, to open/close valves, to carry heavy loads, and to decontaminate target environments. These robots were not maintained and, as a result, there were no robots serviceable enough to be used in the Fukushima Daiichi Power Plants. However, even if those robots had been maintained, they would have been too heavy for use in the target environment. 

In recent years, research and development of small surveillance robots has been actively carried out, and highly reliable robots such as Packbot are now available (Yamauchi, 2004). This robot was evaluated in real disaster environments and on battlefields. In fact, it was the first robot to enter the reactor buildings in the Fukushima Daiichi nuclear plants. However, TEPCO currently uses Quince robots more frequently because of problems such as stair traversability and wireless communication. Furthermore, the Quince robot was easier to retrofit because its engineers live in Japan. Other high-performance surveillance robots include HELIOS, developed by Prof. Hirose’s group (Ueda et al., 2010), and ROBHAZ, developed by KIST (Lee et al., 2004). However, these robots were not used in the Fukushima Daiichi nuclear plants. 

## **2. RADIATION HARDNESS** 

The first task in retrofitting the Quince robot was to determine its tolerance of radiation. It is often stated quite generally that the parts most vulnerable to radiation in conventional machines are the electronic components, particularly semiconductors. However, at the beginning of this project, not enough information was available about the radiation hardness of conventional electronic components. 

The first step, therefore, was to obtain information on the radiation hardness of conventional electronic components from the developers of micro artificial satellites at Tohoku University and the University of Tokyo. According to the information received, conventional CPUs, such as the Hitachi H8 and PIC microcontroller, are capable of with- 

standing a total dose of 10 krad (=100 Gy). However, there were no results for higher-performance CPUs, such as Pentium or Atom, as they had not been tested. 

Results of gamma ray irradiation tests for conventional electronic components were subsequently obtained from a report put out by the Manufacturing Science and Technology Center (MSTC) (Mano, 2001). The tests were conducted for the development of radiation-proof robots to respond to criticality accidents. According to the report, the weakest components were electronic devices, and a conventional notebook PC (specifically, Toshiba Dynabook: Mobile Pentium III, 600 MHz) encountered problems after a total dose of 23 Gy. However, the manufacturing process for the CPU was 0.18 _μ_ m, which is much wider than the current manufacturing process, e.g., Atom’s 45 nm. 

Therefore, at the beginning of this project, gamma ray irradiation tests for the electronic components used in the Quince robot were conducted. The results of the tests are summarized in this section. [A detailed report is given in Nagatani et al. (2011a).] 

## **2.1. Thickness of the Lead Plate** 

Before the gamma ray irradiation test, the required thickness of a potential lead plate used to protect the electronic components from gamma rays was discussed. If the electronic components were found to be too weak against the radiation to be useful, lead plate shielding was initially considered to be an option. This would come with a disadvantage of reduced mobility due to the extra mass. 

A gamma ray radiation shield ratio of 10% was selected as the objective for determining the required lead plate thickness. The total penetration probability determination is shown as follows: 

- **1** . Settlement of major nuclear species 

   - In Table 5 of the press releases of the Nuclear and Industrial Safety Agency (NISA) (Nuclear and Agency, 2011), nuclear species are listed in this accident. In these species, Cesium-134 and Cesium-137 were selected on the condition that (1) the half-life of a radioisotope was longer than one year and (2) the radioactive level was over 1 _._ 0 × 10<sup>16</sup> Bq. The penetration capability of Cesium-134 (beta ray) is smaller than that of Cesium137 (gamma ray). Therefore, shielding priority was set to Cesium-137. 

- **2** . Acquisition of each penetration probability of nuclear species The penetration probability data for Cesium-137 could be obtained from textbook resources (N.S.T. Center, 2001). The data obtained are shown in Table I. 

- **3** . Thickness choice for each nuclear species According to the table, 2.0-cm-thick lead is required to provide a shield ratio of 10% against Cesium-137. Therefore, a 2-cm-thick lead plate was tentatively selected as a requirement. 

_Journal of Field Robotics_ DOI 10.1002/rob 

**48** • _Journal of Field Robotics—2013_ 

**Table I.** Radiation transmittance for gamma rays (Cesium137). 

|t<br>(cm)|iron<br>trans.|t<br>(cm)|lead<br>trans.|t<br>(cm)|concrete<br>trans.|
|---|---|---|---|---|---|
|0.0|1.00|0.0|1.00|0|1.00|
|0.5|9.34E-1|0.2|8.46E-1|5|8.69E-1|
|1.0|8.58E-1|0.3|7.77E-1|10|6.36E-1|
|2.0|6.78E-1|0.4|7.12E-1|15|4.17E-1|
|5.0|2.48E-1|0.5|6.50E-1|20|2.55E-1|
|8.0|7.29E-2|1.0|4.05E-1|25|1.49E-1|
|10.0|3.02E-2|2.0|1.46E-1|30|8.40E-2|
|12.0|1.21E-2|3.0|5.03E-2|35|4.62E-2|
|14.0|4.75E-3|4.0|1.69E-2|40|2.48E-2|


Initially these results had dramatic implications for the final mass of the robot. If the electronic components of Quince did, in fact, need a lead plate shielding, the entire project may have been in jeopardy, as the key feature of Quince is its light weight. This was the state of the project when actual gamma ray irradiation testing began. 

## **2.2. Target Electronic Components** 

The gamma ray irradiation tests conducted for the electronic components in the Quince robot are presented here. The robot’s main controller mounted an Atom-based embedded CPU board (SBC84823 with AtomZ510PT: AXIOMTEK Co. Ltd.), and three two-channel motor driver boards (V-8 with SH7147: Technocraft). For cable communication, a POE power-feeding device (PoE-ZS251T: Techno Broad) was tested. [In the end, a DSL Modem was selected (NVF-200: HYTEC INTER Co., Ltd.), but this device was not included in the irradiation test.] The mounted sensors were CCD cameras (Axis 212: Axis Inc. and CYRC51KD: Panasonic Corp.) and laser range sensors (URG04LN, UTM-30LX, UXM-30LN: Hokuyo, and Eco-scan FX8: The Nippon Signal Co., Ltd.). 

## **2.3. Irradiation Test Method** 

The gamma ray irradiation test was conducted at one of the Cobalt-60 gamma ray irradiation facilities of the Takasaki Advanced Radiation Research Institute of the Japan Atomic Energy Agency (JAEA). These facilities are available not only for JAEA, but also for users from universities, private companies, and public institutes. 

In the irradiation test, three line-shaped Cobalt-60 radiation sources were used. These sources are typically located in an underground pool for safety. When a test starts, the sources emerge at the center of the shielded experiment area on a lifting mechanism. 

The dose rate of the gamma rays was adjusted by changing the distance from the radiation sources. The strength theoretically decreases in proportion to the dis- 

tance from the source squared. Therefore, the Cobalt-60, 20 Gy/h gamma ray points were set at 0.66 m from the source, and 40 Gy/h gamma ray points were set at 0.45 m from the source, concentrically. 

According to past research, a typical conventional device has a total dose durability of 100 Gy. The intitial plan only included testing of the CPU board because the CPU board was anticipated to be the most susceptible to gamma ray irradiation. Therefore, a 5-h gamma ray irradiation test was conducted for CPU devices at 0.66 m from the source on the first day (April 15, 2011). In this case, the total dose was 100 Gy. 

After the experiment conducted on the first day, it was found that 100 Gy was not sufficient to disable all of the electronic components. Furthermore, there was the additional requirement of checking the range sensors. Therefore, on the second day (April 20, 2011), an additional 5-h gamma ray irradiation test was conducted. To conduct the 200 Gy irradiation test, the CPU devices were located 0.66 m from the source (20 Gy/h). Additional devices, such as range sensors, were located 0.45 m from the source (40 Gy/h). Thus, the total dose for all devices was 200 Gy. 

A photograph of the test configuration is shown in Figure 2. The sources of radiation were placed in the cylindrical mesh at the center of the photograph. For all of the devices, the electronic parts were placed perpendicular to the source so that the configuration of each device would face the worst-case condition. Figure 3 shows the layout of the devices and the experimental facility. Personnel and the laptop PCs used to check the status of the devices were isolated from the radiation source by very thick walls. 

During the irradiation test, the following tests were conducted to confirm normal performance of the devices: 

- **1** . **Ping test for each device** 

The LAN cables were connected from the monitoring laptop PC to the target CPU board and other devices 


Figure 2. Device configuration for the gamma ray irradiation test. 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **49** 


Figure 3. Layout of devices and experimental facility. 

that had a communication function. If one of the devices did not reply, it was considered a radiation-induced malfunction; if all devices did not reply, the malfunction was assumed to occur at the LAN HUB, battery, or DC-DC converter. In the latter case, the entire test would be suspended in order to confirm the source of the malfunction. 

- **2** . **Reboot test for CPU board** 

Even if the compact flash card (CF card) mounted on the target CPU board got damaged, the board itself could continue to operate. This is due to the fact that the CF card is typically used only in the booting sequence of the CPU board in the Quince system. Therefore, the display cable and the reset signal cable from the CPU board to the monitoring laptop PC were extended. Then, once every 30 min, a reset signal was sent to the CPU board to confirm whether the Operating System had booted up. 

- **3** . **Sensing test** 

The Panasonic CCD camera used in Quince was connected to the LAN via a video server (Axis 282). The wide-angle camera (Axis 212) also used the LAN connection. Therefore, viewing tests were conducted on the cameras via the LAN cable. In addition, the 2D range scanners and the 3D scanner were connected to the monitoring laptop PC to enable the sensing results to be viewed. 

- **4** . **Motor driver test** 

The motor driver in the Quince robot communicated with the CPU board via a Controller Area Network 

(CAN). Therefore, the CAN cable and a serial cable were connected to the monitoring laptop PC, and the CAN communication packets were observed using dummy data. A motor rotation test was not conducted, as the preparations for such a test would have required excessive time, and, generally, motors are more tolerant than standard electronic devices. 

## **2.4. Irradiation Test Results** 

The total dose for each component in the irradiation test is shown in Table II. Note that, for URG-04LN and the CCD camera, the total doses were logged while they were malfunctioning. To measure the total dose for each component, alanine dosimeters, called Aminograys, were used. They can obtain the total dose by measuring the radical amount in alanine crystals using electron spin resonance (ESR). The error is specified to be within 3%. 

At a total dose of 124.2 Gy, the sensor data from the URG-04LN sensor ceased. (When the sensor was inspected later, it was found to have malfunctioned.) 

Up to a total dose of approximately 140.0 Gy, the picture obtained from the CCD camera (CY-RC51KD, Panasonic) was very clear. However, after 140.0 Gy, it began changing gradually to a bluish tinge, and completely stopped displaying data after its battery was replaced at a total dose of 169.0 Gy. As the video server was still working correctly, it was concluded that the CCD camera itself was broken. 

Contrary to expectations, the other devices functioned properly after a total dose of approximately 200 Gy. Recently, the Axis 212 was evaluated and was found to be malfunctioning. Therefore, it is assumed that it was very close to its breaking point after the 200 Gy irradiation test. 

## **2.5. Discussion** 

After the irradiation tests, some of the devices in the Quince robot were replaced for additional missions, but there was insufficient time to test all the devices. However, the irradiation test covered the vital components in the Quince robot, and this was considered to be a minimal validation. 

Making the conclusion, based on the results of a single test, that the devices which survived have a typical durability of 200 Gy would be erroneous because electronic devices may have individual differences. However, without the time to conduct multiple tests, the electronic devices in the Quince robot were considered durable to at least 100 Gy and potentially higher. 

In the initial stage of the disaster response at the Fukushima Daiichi Nuclear Power Plants, the maximum dose in the target environment was around 100 mGy/h. This meant that almost all of the electronic devices in the Quince robot would work for more than 100 h at a 10% safety margin. 

_Journal of Field Robotics_ DOI 10.1002/rob 

**50** • _Journal of Field Robotics—2013_ 

**Table II.** Total dose for each device and resulting condition. 

|Device|Total dose (Gy)|Condition|
|---|---|---|
|CPU board, POE device|206.0|It survived.|
|Motor driver boards|206.0|It survived.|
|Laser scanner, UXM-30LN|229.0|It survived.|
|Laser scanner, UTM-30LX|no data|It survived.|
|Laser scanner, Eco-scan FX8|225.0|It survived.|
|CCD Camera, Axis 212|219.5|It survived.|
|Laser scanner, URG-04LN|124.2|It broke after 124.2 Gy.|
|CCD Camera, CY-RC51KD|169.0|It broke after 169.0 Gy.|


On the basis of the above discussion, it was concluded that the Quince robot did not require any lead protection for conventional missions in the target environment. 

Note that the above devices were conventional, non– radiation-proof products. Furthermore, it was not possible to perform, sufficient number of tests for statistical proof of radiation hardness. Therefore, the above results can be used as a reference but they are not guaranteed to be valid in all conditions. 

## **3. MOUNTING SENSORS ON THE QUINCE ROBOT** 

The second task in retrofitting Quince was the mounting of sensors on the robot. In this section, the sensors that were mounted on the Quince robot are introduced. Figure 4 shows the sensor data received. The numbers in the figure correspond to the numbered explanations below. Note that the display is as was proposed at the beginning of May, 2011 (dual-display system), and the display in the final proposal is shown in Figure 11. 

In the original project, the following sensors were mounted on the Quince robot in preparation for a disaster response in underground malls: 

### **1** . **Attitude sensor** 

To understand the pose of the Quince robot during teleoperation, an inertial measurement unit was mounted on it. The unit consisted of a triaxial accelerometer and three gyroscopes. Thus, when the robot moved, three gyroscopes measured its attitude by integration of angular velocities based on quaternion representation. When the robot stopped, the accelerometer canceled temperature drift errors in the gyroscopes. Based on the information received, the measured attitude was displayed in an operator’s display shown in Figure 4-(1). The upper section of the figure shows the tilt angle of the robot and the angles of the subtracks, while the lower section of the figure shows the roll and pitch angles of the robot. **2** . **Front, rear, and overhead cameras** 

- To understand the surrounding environment, three small cameras (CY-RC51KD, Panasonic) were mounted. Two cameras were situated at the front and rear, while 

the last one was attached to the pole to obtain an overhead view. These views are displayed in Figure 4-(2) (front view), Figure 4-(3) (rear view), and Figure 4-(4) (overhead view). As is typical, their display quality was low. However, update time was very small, less than 30 ms for smooth operation. 

The above sensors were the minimum requirement for exploration in disaster environments. In the urgent project to retrofit the Quince robot for disaster response missions in the Fukushima Daiichi Nuclear Power Plants, the following sensors were added: 

### **1** . **Dosimeter** 

Dose measurement was one of the most basic and important tasks in this mission. However, the original Quince robot did not have dose measurement sensors. Hence, a dosimeter manufacturer and model were issued by TEPCO (CPXANRFA-30, Fuji Electric Co., Ltd.), as it was believed that sensing values and errors should be the same as those for the devices used by plant workers. Therefore, the digital dosimeter was mounted at a height of 1.2 m, which is almost the same height as that of the most important internal organs in the human body. To read the value displayed on this sensor, a CCD camera pointed at the dosimeter was used. In Figure 4, a value for the dosimeter is not displayed, as this display was for the trial test phase; you can, however, see a zero value for the dosimeter shown in Figure 11-(8) for the final test. In one of the actual missions, it was confirmed that the dosimeter measured over 200 mGy/h in the unit 2 building, shown in Section 7.5. 

### **2** . **Main camera** 

In the original Quince robot, typically an optional pantilt-zoom camera, Axis 213 PTZ, would be mounted. However, this camera had movable parts that might have been broken easily. Furthermore, it was not waterproof, and it would have been difficult to make it waterproof because of the movable parts. Therefore, it was replaced with an Axis 212 PTZ camera. This camera uses a wide-angle lens combined with a three-mega-pixel sensor and realizes instant 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **51** 


Figure 4. Display layout of the initial operation software (dual display system version): (1) Attitude sensor, (2) front camera view, (3) rear camera view, (4) overhead camera view, (5) temperature display, (6) battery indicator, (7) main camera view, (8) 3D image obtained by 3D laser range scanner. 

_Journal of Field Robotics_ DOI 10.1002/rob 

**52** • _Journal of Field Robotics—2013_ 


Figure 5. (a) Swing motion of 2D laser range scanner (left), (b) gimbal mechanism of the scanner (center), and (c) 3D map of stairs obtained by the 3D laser range scanner (right) (Yoshida et al., 2010). 

pan/tilt/zoom by clipping an image from the highresolution image without any mechanical motion. Figure 4-(7) shows the main camera’s view. In the final version discussed in Section 5, two Axis 212 cameras were placed in both forward-facing and backwardfacing directions, shown in Figure 11-(2) and (3). The high-resolution photographs in Figure 14 were taken using this camera. 

- **3** . **Laser range scanner** 

To obtain 3D images for navigation, a 3D laser range scanner was used. There were some commercial 3D laser range scanners available, but they were too heavy to mount on such small mobile robots. Therefore, an internally developed 3D scanner was mounted. The mechanism of the scanner included a 2D commercial laser scanner (UTM-30LX, Hokuyo Co., Ltd.) with a custom gimbals-mechanism, which output full 3D data, as shown in Figure 5 (Yoshida et al., 2010). In the end, TEPCO did not permit the use of the laser range scanner because the main mission did not include 3D scanning of the building, and more particularly, there was no space to mount the scanner on one robot. 

- **4** . **LED light** 

To obtain useful images when using the cameras in a dark environment, lighting is very important. At the beginning of implementation, a battery-powered commercial flashlight was attached. However, this arrangement proved troublesome. Therefore, two LED-array lights (7 W each) were mounted in the front and at the back, along with additional IDX batteries (IDX Endura 7, 14.8 V, 4.8 Ah). 

- **5** . **Temperature sensors for motors** 

To avoid the motors breaking down, real-time knowledge of motor temperature was very important, particularly in teleoperation. Therefore, on each of the Quince robots, a temperature sensor was attached to each motor to monitor its condition. An automated motor-shutdown-function that would shut down the 

motor based on the information received could also have been implemented. However, it was decided that human judgment of whether to continue the mission or to break to cool down the motors was the superior solution. Figure 4-(5) gives a snapshot of the temperature of each motor. 

## **4. COMMUNICATION** 

The third task in retrofitting Quince was that of communication inside and outside the damaged reactor buildings. For the operator’s safety, the operation box used to control the robot needed to be located as far away from the target area as possible. However, the walls in the buildings were very thick in order to shield personnel from radioactive rays. Furthermore, there was a reactor vessel and also higher elevations. In such an unfriendly environment for transmitting and receiving radio waves, it was impossible to guarantee that wireless communication would be possible, particularly inside the buildings. In this section, wireless communication tests that were conducted in a reactor building are reported, and the cable/wireless hybrid network used with the Quince is introduced. 

## **4.1. High-power Wireless Communication Device** 

The key question to be answered was, “Is it possible for the Quince robot to use wireless communication inside a building of the Fukushima Daiichi Nuclear Plants?” The standard set of wireless communication devices mounted on a Quince robot was assumed to be insufficient inside and outside of the target environment. To extend its communication distance, the basic approach was to use more powerful radio wave energy. Japanese radio law is very strict with regard to the output of electrical field strength because of the small land area. Of course, much depends on the antenna, but generally, 10 mW is taken as the maximum. In this case, 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **53** 

the wireless communication distance for household devices is a maximum of 50 m. 

In this emergency situation, special permission from the Ministry of Internal Affairs and Communications in Japan was obtained to use high-power radio waves. 2.4 GHz Contec devices (an FX-DS540-STDM child device with a dipole antenna for the robot, and an FX-DS540-LNKM-S parent device with a Yagi antenna for the operation box) and 1 W boosters for each were selected. In a preliminary experiment, it was confirmed that the Quince could be teleoperated at a distance of 2 km from the operation box (lineof-sight) using these devices. This confirmed that it was possible to use this set of wireless devices outdoor. However, there was no confirmation with regard to indoor use, particularly inside a reactor building. 

## **4.2. Wireless Communication Tests in a Reactor Building** 

It was not possible to take the robots into the Fukushima Daiichi Nuclear Power Plants for the wireless communication test. Therefore, the Hamaoka Nuclear Power Plants agreed to allow high-power wireless communication tests to be conducted in their facilities. Such a request was only approved due to the extraordinary circumstances at the time and would not be a viable solution in predisaster development. 

In the experiment, 2.4 GHz wireless devices, shown in the previous section, and a commercial video signal transmitter that used an ultrahigh frequency (UHF) radio were tested. The 2.4 GHz parent device and the video signal receiver were located in a fixed location, while the 2.4 GHz child device and the video transmitter were placed in different locations in order to assess the level of communication between them. 

Figure 6 gives an overview of the resulting wireless communication area for the 2.4 GHz devices on the first floor of the Hamaoka Nuclear Power Plants. In the figure, the parent device is located on the left side, indicated as 


Figure 6. Overview of the wireless communication area in the Hamaoka Daiichi Nuclear Power Plants. 

“OP,” and the numbers in the rectangular boxes indicate the serial numbers of the check positions. The area colored in light gray signifies that stable communication was possible there, the area colored in standard gray signifies that communication was unstable there, and the area colored in dark gray signifies that communication proved impossible in that area. In addition, the child device was carried upstairs and its communication capability was assessed. The result was that stable communication was not guaranteed higher than three floors up. The coverage area of the video signal transmitter (UHF radio) was a little better, but the overall trend was almost the same as that for 2.4 GHz. 

The above results were virtually consistent with the initial estimation, and proved that the high-power wireless communication devices used previously in Quince would not work in reactor buildings, including Fukushima Daiichi. Therefore, other communication approaches had to be considered. 

## **4.3. The Cable Communication System** 

To enable secure reliable communication inside the reactor building, a communication system was configured using a cable/wireless hybrid network, which was a simple version of the hybrid mesh network developed in NEDO’s project. Figure 7 gives an overview of the authors’ proposal at the beginning of May, 2011. (Note that the proposed configuration had been extensively revised because the situation had changed in Fukushima.) Two of the robots developed—a cable-laying robot and an exploration robot—are shown in Figure 8. 

The control boxes for the robots were situated outside the building, and a 200 m twisted-pair metal cable and very high-bit-rate Digital Subscriber Line (VDSL) devices (NVF200LS and NVF-200R: NetSys) were used to establish communication between the control boxes and the device that was located in front of the airlock (on the outside). Between the cable robot and the device located in front of the airlock (on the inside), a 500 m twisted-pair metal cable was also used with the VDSL devices. 

The airlock had double-entry doors to prevent radioactive materials from being released from the reactor building. Therefore, they were kept closed at all times. To communicate through the airlock, 2.4 GHz wireless communication devices (FXDS540STDMS, Contec Co., Ltd.) were used. In the actual implementation, the wireless communication through the airlock was bypassed by keeping the door slightly ajar to facilitate the cable. 

The cable on the robot was reeled out when the robot moved forward. For the returning motion of the cable robot, the reel could be rewound on an operator’s command. There was the possibility to install a tension control mechanism in this function, but rapid development required precluded this. When an operator sent a rewind command to the robot, the rewind function was activated. 

_Journal of Field Robotics_ DOI 10.1002/rob 

**54** • _Journal of Field Robotics—2013_ 


Figure 7. Overview of the proposed configuration for the dual-robot system. 


The torque of the rewind mechanism had a limitation in order to eliminate the risk of tensile cutting of the cable. Figure 9 shows the cable reel-out/rewind mechanism that was mounted on the cable robot. 

Between the cable robot and the exploration robot, 2.4 GHz wireless communication was used. The radio field strength of the communication was beyond the limitation set by Japanese law (10 mW/MHz), with the permission of 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **55** 

(a) 


Figure 9. Cable reel-out mechanism: (a) Side-view of the mechanism, (b) top-view of the mechanism, and (c) an overview of the mechanism that was mounted on the rear of the Quince robot. 

the Japanese government. This enabled 2 km teleoperation of the robot from an unobstructed view outside. 

## **4.4. Discussion** 

For teleoperation communication, it was concluded that a wireless network would be useless in a reactor building in the initial stage of disaster response. Therefore, cable communication was chosen for the robot, but cable entanglement was considered a new risk of the repurposed system. In fact, during operations the robot used in Fukushima did end up getting stuck on the third floor of the second reactor building, shown in Section 7.5. However, the robot had been able to complete many missions before that incident. So, despite these troubles, the authors still believe that this choice of communication method was best. 

## **5. EXTRA MISSION STATEMENT** 

At the beginning of May, 2011, the demand in the field had changed, and an official urgent mission was proposed by TEPCO. This involved an exploration of the basement of the reactor buildings and the installation of water gauges. In addition, the mission needed to be performed by a single robot because the dual robot system was too complicated for novice operators, and they would have to be operated in limited space. This resulted in significant changes in the robot system, which involved an extra redesign project. 

To complete the extra mission, the following functions needed to be considered: 

- **1** . Water gauge installation function, 

- **2** . Countermeasures against overweight, and 

- **3** . Improvement of teleoperation software. 

## **5.1. Crane Function for the Water Gauge** 

In this project, the robotic system needed to be developed rapidly in order to respond to the given mission as soon as possible. Therefore, it was decided to develop a very simple 2 DOF manipulator to install water gauges just for this mission. Figure 10 (left) gives an illustration of the mission scenario, while Figure 10 (right) shows a photograph of the manipulator that was developed for handling the target water gauge. It had two actuators for pitch angle and yaw angle. The top limb of the manipulator was supported by a parallel linkage, and the tip of the manipulator was always positioned perpendicular to the bottom plane of the robot. A CCD camera and a LED light (1 W) were mounted at the tip, and the water gauge was reeled out. 

To install a water gauge in the contaminated water in the basement of the reactor building, a reel-out mechanism for the cable of the gauge was needed. Therefore, a crane mechanism was installed at the tip of the manipulator to realize these functions. 

## **5.2. Countermeasures against Overweight** 

After development of the above mechanisms, including the 2 DOF manipulator, the weight of the robot increased to approximately 50 kg. It was obviously overweight because the original Quince robot was 27 kg. Furthermore, the extra mission included an exploration of the basement of the reactor buildings, and the stair angle was steeper than that of the other stairs to the upper floors. In the initial laboratory test, it was found that the Quince robot experienced difficulty climbing up the stairs. 

To resolve the above problems, the following operations were performed: 

_Journal of Field Robotics_ DOI 10.1002/rob 

**56** • _Journal of Field Robotics—2013_ 


Figure 10. Illustration of the mission scenario using a 2 DOF manipulator (left) and the developed 2 DOF manipulator with water gauge (right). 

- **1** . Load mitigation and heat check of motors The reduction ratios of the locomotion motors were increased to mitigate load. In addition, heat sensors were placed on the motors to regulate their temperatures and increase their reliability. 

- **2** . Substitution of long subtracks In the initial laboratory test of steep stair-climbing using the Quince robot with the 2 DOF manipulator, it slipped many times. Therefore, for pressure dispersion, the conventional front subtracks were replaced with long subtracks with embedded counterweights. By extension of the subtracks, three edges of stairs were consistently caught by the tracks, and stability improved significantly. 

## **5.3. Improvement of Teleoperation Software** 

To carry out the extra mission, the additional mechanisms were mounted on the robot. Furthermore, TEPCO required a single cable robot with small operation display. Therefore, the teleoperation software was also significantly modified. Figure 11 shows a display layout for the cable robot on which the 2 DOF manipulator was mounted. 

Additionally, to enable the robot to return up the stairs, a reverse mode that facilitated the switching of the front and rear cameras was installed, which flipped the posedisplay of the robot between left and right, and sent inverted commands to the robot. Thus, when the operators changed to the reverse mode, they were able to control the robot as if the rear of the robot was its front. To perform tangle-free movement of the communication cable, the operator used the manual rewind function of the cable. Figure 12 illustrates and explains this function. 

The above functions, including the 2 DOF manipulator and the new human interface, were tested in a laboratory environment and the operations were confirmed. 

## **6. LABORATORY TESTS** 

Before delivering the Quince robot, a number of tests were performed in a laboratory setting. In this section, the tests performed before delivery of the Quince robot to TEPCO are described. 

## **6.1. Traversal Test in Rough Terrains** 

At the beginning of this project, it was assumed that the robot should be able to overcome rubble-strewn areas to enter the reactor buildings. Therefore, traversal tests in a concrete block field and random step field (Jacoff et al., 2003) were performed to confirm the traversability of the surfaces and the durability of the robot in the initial stage. The robot’s mobility system was already capable of scaling 42 cm step heights, therefore the most important result of the tests was a measure of reliability with all the devices mounted. In the middle stage, the robot mounted a variety of devices. The weight of the robot was higher than past operations, but it was understood that there would be no rubble-strewn area before entering the buildings. Therefore, no severe traversal tests in rough terrains were performed in the second half. 

## **6.2. Traversal Test on Stairs** 

When the official urgent mission proposal from TEPCO was received, it was understood that stairs were the most difficult to traverse in real missions. Therefore, a test 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **57** 


Figure 11. Display layout of the operation software for the cable robot with a 2 DOF manipulator: (1) overhead camera view, (2) rear camera view, (3) front camera view, (4) pose of robot (pitch) and subtracks, (5) pose of robot (roll), (6) battery indicator and temperature display, (7) pose of 2 DOF manipulator, (8) dosimeter view, (9) crane camera view, (10) LED light switch, (11) total data acquisition button, (12) mission timer, (13) button to return subtracks to prescribed pose. 


Figure 12. In normal mode (shown on the left), the robot moves forward when the joystick is moved forward. In this case, the forward camera is shown on the right side. Once the operator changes to reverse mode (as shown on the right), the joystick operation is reversed. In this case, the location of the main camera images is also reversed. 

_Journal of Field Robotics_ DOI 10.1002/rob 

**58** • _Journal of Field Robotics—2013_ 


Figure 13. Test stairs. 

staircase was built, as shown in Figure 13. The size, material, and surface of the stairs were designed to exactly match those of the staircase in the reactor buildings in order to duplicate the actual environment as closely as possible. The Quince robot had difficulty climbing the stairs due to the large-rounded stair edges made by the checkered steel plate. Based on the above tests, the surface patterns of tracks were improved by trial and error. Eventually, the robot succeeded in climbing up the stairs safely. This was a very important test for the preparation of real missions because it was the requirement for approval from TEPCO to use the robot in the reactor buildings. In the real missions, there were reports of slippage of the Quince robot on stairs, but the details were never divulged. 

## **6.3. Teleoperation Tests and Training** 

After receiving the official mission proposal, two robot operators were assigned from TEPCO and were trained in teleoperation of the Quince robot. First, they learned the basic manner of the robot’s operation on a simple flat surface and easy stairs using direct sight information. They then were trained in the operation of the robot using only computer display information, as shown in Figure 11. The environment was made dark for some of the tests to simulate the inside of the reactor buildings. The operators were then required to operate the Quince robot with LED lights. 

Finally, they performed simulated runs to install a water level gauge. The runs were conducted on stairs in university buildings. It was a completely different situation from the real missions, but the test was able to confirm 

whether the mounted devices worked well or not. The total period of training lasted six weeks. 

## **7. THE REAL MISSIONS** 

On June 20, 2011, the Quince robot was delivered to TEPCO, and a total of six missions involving the Quince robot were conducted in the damaged reactor buildings in the Fukushima Daiichi Power Plants. Before the actual missions, more than ten practice tests were performed in the reactor building of unit 5, which had not been seriously damaged. This section is a report on the actual missions that were conducted in the damaged reactor buildings. 

## **7.1. The First Mission—June 24, 2011** 

The first mission using the Quince robot was conducted on June 24, 2011, in the reactor building of unit 2. The objective of the mission was to install a water level gauge in the contaminated water pool on the basement floor. At that time, to cool down the fuel core of the reactor building, water was being injected continuously, and it had accumulated on the basement floor. Surveillance of the amount of contaminated water was an urgent mission as it was feared that the water could overflow and spill into the sea. The Quince robot was fully equipped with a 2 DOF manipulator and a water level gauge to conduct the mission. 

The target environment was completely dark, so the robot used LED lights to obtain the environment information. First, the robot entered the building and went down one flight of stairs to the basement. The operator found that the size of the landing was much narrower than indicated in the information provided in advance by TEPCO. Because of the lack of space, the robot could not turn. The operator then abandoned the exploration and returned the robot to the first floor. Next, the operator tried to go down another flight of stairs to the basement, but the same problem occurred on the landing. Finally, the operator gave up on the installation of the water gauge. The total mission time was 95 min, the total traveling distance was approximately 182 m, and the maximum dose rate was 65 mGy/h at the landing of the first stairs to the basement. 

The size-disparity of the landings was due to the use of outdated drawings of the building. There were more recent drawings that had been updated after construction had been done on the staircase, but they had been lost in the tsunami. As a result, the Quince robot could not accomplish the objective of the first mission. 

## **7.2. The Second Mission—July 8, 2011** 

The second mission was conducted on July 8, 2011, in the reactor building of unit 2 (Tokyo Electric Power Company, 2011a; 2011c). The objectives of the mission were to measure the radiation levels of the upper floors and to sample the dust in the air in the building. In this mission, the Quince 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **59** 

robot was equipped with two timer-triggered air pumps for the dust sampling tasks. The crane and the winch for water gauge installation were removed because they were not required for this mission. The target environment was completely dark, so the robot used LED lights to obtain information about the environment. 

In this mission, the operator attempted to reach the third floor, but it took 66 min because of slippage on the staircase. The air had a lot of moisture, and the surface of the stairs was wet. The air dust samplers were activated on the second and the third floors, and the basic task was completed in the mission. 

On the way back to the entry point, the robot faced a dangerous situation. The temperature of its motor driver reached 50<sup>◦</sup> C, after which the automated safety shutdown was engaged. In the experimental setting, it was able to reboot after the temperature decreased more than 5<sup>◦</sup> C. However, in this case, the temperature never decreased because of the high air temperature. There was no direct measurement of the air temperature, but the thermometer on one motor driver indicated 40<sup>◦</sup> C. This was assumed to be the same as the air temperature because the driver was rarely used in the mission and it was located on the upper structure of the robot. 

To solve the problem, a low-level reboot command was sent to the motor driver boards directly from the operator. It was a delicate operation because keyboard command codes needed to be sent from a user debugging interface. Because of the temperature safety function, the above reboot operation was repeated several times until the robot returned to the entry point. While descending the stairs from the third to the first floor, the robot slipped twice because of the loss of motor power. Eventually, the robot returned to the entry point. For this mission, the total mission time was 193 min, the total distance traveled was approximately 230 m, and the maximum dose rate was 50 mGy/h on the second floor. 

distance traveled was approximately 130 m, and the maximum dose rate was 54 mGy/h at the front of the pile of rubble on the way to the third floor. 

Figure 14 shows the high-resolution photographs captured by the wide-angle camera on the Quince robot. The photograph on the left shows the piping of the core spray system. It was captured next to the primary containment vessel. The photograph on the right, showing the pile of rubble blocking the stair, was captured on the middle of the stairs to the third floor. 

From the data obtained on this mission, TEPCO came to understand that the core spray system was alive, and that the dose rate was relatively low around the piping of the system. Therefore, restoration of the spray system process was planned, and it was reactivated by plant workers on September 1, 2011 (Tokyo Electric Power Company, 2011b; 2011c). It was one of the biggest successes in the use of the Quince robots. 

## **7.4. The Fourth and Fifth Missions—September 22 and 24, 2011** 

The fourth and fifth missions were conducted on September 22 and 24, 2011. The objectives of these missions were to inspect the first floor of the reactor buildings of units 2 and 3. The missions were a part of the preparation for the project to investigate the inside of the primary containment vessel using a borescope. The Quince robot explored the target areas, obtained many photographs, and measured the dose rate of the workplaces of the plant workers. The above missions were completed without any trouble. For the fourth mission, the total mission time was 80 min and the total distance traveled was approximately 100 m. For the fifth mission, the total mission time was 90 min and the total distance traveled was approximately 160 m. 

## **7.5. The Sixth Mission—October 20, 2011** 

## **7.3. The Third Mission—June 26, 2011** 

The third mission was conducted on June 26, 2011 (Tokyo Electric Power Company, 2011c) in the reactor building of unit 3, which was heavily damaged from hydrogen explosions. The objectives of the mission were to investigate the damage done to the piping of the core spray system and to measure the dose level around the facility. 

The target environment was dark, but there was partial lighting from holes in the damaged ceiling. Therefore, the robot basically navigated using LED lights to obtain information about the environment. In this mission, the Quince robot explored the second floor smoothly and captured high-resolution photographs of the target facilities, such as the core spray system. After surveillance of the second floor, the robot tried to go up to the third floor, but it faced a huge pile of rubble in the middle of the landing. Finally, it returned to the entry point without trouble. For this mission, the total mission time was 105 min, the total 

The sixth mission was conducted on October 20, 2011, in the unit 2 building. The objectives of the mission were to investigate the damage to the facility on the third floor and to inspect the fuel pool on the fifth floor. In this mission, air temperature measurement was also requested, and so a conventional thermometer was installed on the Quince robot in view of a spare camera on the robot. The camera image was displayed on the operator console. 

The target environment was dark from the first floor to the fourth floor, but sunlight got into the fifth floor as the blowout panel was open. The Quince robot climbed the stairs and reached the third floor. It then approached the target facility, took some photographs, and measured the dose level. On the fifth floor, the Quince robot went to the lid of the primary containment vessel, measured dose rate and temperature, and took photographs. Around the lid, the dosimeter on the Quince robot showed very high radiation levels (over 250 mGy/h). 

_Journal of Field Robotics_ DOI 10.1002/rob 

**60** • _Journal of Field Robotics—2013_ 


Figure 14. High-resolution photos taken in unit 3. The frame on the left shows the piping of the core spray system; the frame on the right shows rubble blocking the staircase to the third floor. 

After the inspection of the fifth floor, the Quince robot tried to return to the entry point. However, the communication cable got snagged on the piping on the third floor and jammed in the cable reel. As a result, the communication cable could not be rewound. In the end, the surveillance mission was completed successfully, but up to this point in time, the Quince robot has not been retrieved. For this mission, the total mission time was 138 min and the total distance traveled was approximately 408 m. 

## **8. CONCLUSION AND FUTURE WORK** 

## **8.1. Conclusion** 

In this paper, the missions assigned by TEPCO as part of the disaster response effort in the Fukushima Daiichi Nuclear Power Plants were described, and the results of a retrofitting of the rescue robot to enable it to perform those missions were reported. 

The tests and retrofitting included the following items: 

- **1** . radiation tolerance tests, 

- **2** . additional hardware and sensors, 

- **3** . a long cable/wireless hybrid network, 

- **4** . construction of a 2 DOF manipulator, 

- **5** . an additional crane function for a water gauge/ sampling bottle, 

- **6** . improvement of the teleoperation software, and 

- **7** . countermeasures against overweight. 

During this project, difficulties were faced in putting the research projects to practical use. Lessons learned from the project are itemized as follows: 

- **1** . **Precise communication between researchers and users** Precise communication between researchers and users is very important. At the beginning of the project, there was no precise communication with the user (TEPCO), because there was no official mission proposal from them. At that time, the robot had to be prepared to function in a wide range of possibilities, largely based on guess work, which included developments that would ultimately turn out to be irrelevant. Eventually, precise communication with TEPCO was established and the team was able to focus the development of the Quince robot in the right direction. 

_Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **61** 

- **2** . **Education of users in simulated environments** In the initial phase, users do not know how useful robots are, and researchers do not understand what is actually required in the field. Furthermore, in typical cases, the user operates the robots and the researcher cannot enter the field. Therefore, education of users in simulated environments using actual robots is very important in order to bridge the divide. There were significant delays before receiving any official mission proposal from TEPCO because decision makers at TEPCO did not understand what the Quince robot could do. After receiving the official proposal, there was difficulty tuning available technological offerings to fit TEPCO’s requirements. Documents, slides, and detailed explanations were not effective in conveying the capabilities of the robot. Furthermore, the target environment was severely restricted because of radiation, and it was similarly difficult for the authors to fully grasp the requirements from the field site. The breakthrough came during the training of TEPCO’s operators. In the simulated disaster environment, allowing them to operate the Quince robot gave them direct knowledge of the robot’s capabilities. After that, their operation experience provided clearer requirements from the field, and the obstacles preventing the operators from utilizing the robot’s abilities became more clear. 

- **3** . **Lack of field knowledge for researchers** Typically, researchers propose technologies based on wishful thinking and guess work. These technologies are not always appropriate when deployed in field sites. In this project, there were some technologies developed that ultimately were not adopted by TEPCO: (1) They did not trust autonomy, either full or shared. In this project, a shared autonomy system that controls subtracks automatically based on sensory information is proposed (Okada et al., 2011). This can significantly reduce the operator’s workload. However, the operators from TEPCO wanted to have fine granular control of each actuation. (2) They did not adopt a 3D laser range scanner. In teleoperation, the authors believe 3D information helps operators to better understand the surrounding environment. However, the operators from TEPCO were not interested because they were already intimately familiar with the target environment. (3) They did not adopt the dual-robot system. A dualrobot system (wired and wireless) was proposed at the beginning of the project, as shown in Section 4.3. However, the dual-robot system required twice the number of operators and workers. This would have doubled the total amount of human radiation exposure. 

Some of the above lessons learned are limited to this project only. However, the same situations can be assumed to occur in the practical use of robotic technologies. It is hoped that this field report and the lessons learned will help in such situations. 

## **8.2. Future Work** 

As shown in the previous section, the missions that were assigned to the Quince robot were completed, and they contributed significantly to recovery work at the plant. At the same time, the problems detailed below became evident during the missions. 

### Communication cable 

The most significant problem was the communication cable. The cable-rewinding device on the Quince robot did not work properly at the end of the sixth mission. In the end, the cable became useless and the Quince robot was not retrieved. 

In the initial implementation of the Quince robot, preemptive movement was the first priority. Furthermore, it was assumed that the communication cable was disposable during each mission, and so no rewinding function was installed in the early stage of the Quince robot retrofitting project. However, to enable a switchback motion for the robot in confined environments, an ad hoc rewinding function was eventually added. However, it did not have the ability to wind the cable evenly, so rewinding was thought to be only possible up to 20 m. Practically, the device worked much better than initially anticipated, and sometimes it rewound over 200 m of cable in the trial runs. Therefore, over 20 m of rewinding operation was typically performed during the actual missions. From the point of view of safety, a 20 m maximum rewind should still have been set. 

### Unknown environment 

The size of the landing for the stairs leading to the basement was reported as being 91 cm in width by TEPCO. A mock environment was built with the same size as reported, and the Quince robot was tested in this mock environment. However, the actual width was 71 cm in the nuclear plant. As a result, the first mission was not completed. The size data given by TEPCO were based on the drawings made when the building was first constructed, but repeated modifications to the building had subsequently reduced the width of the landing. However, all information about such modification had been washed away by the tsunami. It was considered that this situation had been unavoidable in this case, but more accurate information would have definitely helped to ensure mission success. 

### Carrying method 

The Quince robot was either carried on a stretcher or transported by manually holding on to each subtrack. A stretcher could not always be used because of the narrow corners on the way to the entry point. However, after the mission in the reactor building, contaminated dust stuck to 

_Journal of Field Robotics_ DOI 10.1002/rob 

**62** • _Journal of Field Robotics—2013_ 

the tracks of the Quince robot. Consequently, when the operators held on to the subtracks and transported the Quince robot, they were exposed to the radiation source at a very close range. The method of carrying the robot needed to be modified in order to avoid exposing the carriers in the next version of Quince robots. 

### Additional components 

Sampling of the dust in the air of the reactor building was requested after the Quince robot was delivered to the site. In the second mission, it was conducted with two timerdriven pumps attached to the Quince robot. The timer had to have a margin that ensured the robot’s arrival at the designated position. This made the mission time much longer. Furthermore, air temperature measurement was also requested on the sixth mission. To satisfy the request, a conventional thermometer was attached to the Quince robot in view of a spare camera. The temperature value was recorded on the screen capture of the operator console. Both of the functions described above had not been requested at the time the Quince robot was retrofitted in the laboratory. It would have been helpful if the task definitions, particularly hardware-related tasks, had all been defined before robot delivery. 

At present, TEPCO requires the use of an alternative Quince robot. Therefore, a revised Quince robot is currently in development which will address the issues described above. 

## **ACKNOWLEDGMENTS** 

We would like to thank the Takasaki Advanced Radiation Research Institute, whose prompt action with regard to irradiation testing was very helpful for the retrofitting of our robot. We would also like to thank NEDO and TEPCO for going ahead with this research. 

## **REFERENCES** 

- Bennett, P.C., & Posey, L.D. (1997). Rhobot: Radiation hardened robotics. Sandia Report from Sandia National Laboratories, Nuclear Safety Technology Center, Tokyo, Japan. 

- Foltman, A.J. (1986). Proceedings of the workshop on requirements of mobile teleoperators for radiological emergency response and recovery. Workshop on requirements of mobile teleoperators for radiological emergency response and recovery, Argonne National Laboratory, Argonne, IL (pp. 1–189). 

- Hess, C.J., & Metzger, S.W. (1985). Steady progress at tmi-2. IAEA Bulletin, 27, 16–22. 

- Jacoff, A., Messina, E., Weiss, B.A., Tadokoro, S., & Nakagawa, Y. (2003). Test arenas and performance metrics for urban search and rescue robots. In Proceedings of the IEEE/RSJ International Conference on Intelligent Robots and Systems, pp. 3396–3403. 

- Lee, W., Kang, S., Kim, M., & Park, M. (2004). Robhaz-dt3: Teleoperated mobile platform with passively adaptive double-track for hazardous environment applications. In Proceedings of the IEEE/RSJ International Conference on Intelligent Robots and Systems, pp. 33–38. 

- Mano, T. (2001). A grant-aided project report of disaster prevention system of nuclear plants in 2000 (in Japanese). Manufacturing Science and Technology Center. 

- Nagatani, K., Kiribayashi, S., Okada, Y., Otake, K., Yoshida, K., Tadokoro, S., Nishimura, T., Yoshida, T., Koyanagi, E., Fukushima, M., & Kawatsuma, S. (2011a). Gamma-ray irradiation test of electric components of rescue mobile robot quince—Toward emergency response to the nuclear accident at Fukushima Daiichi Nuclear Power Station on March 2011. In Safety, Security and Rescue Robotics, Workshop, 2011 IEEE International, pp. 56–60. 

- Nagatani, K., Kiribayashi, S., Okada, Y., Tadokoro, S., Nishimura, T., Yoshida, T., Koyanagi, E., & Hada, Y. (2011b). Redesign of rescue mobile robot quince—Toward emergency response to the nuclear accident at Fukushima Daiichi Nuclear Power Station on March 2011. In Safety, Security and Rescue Robotics, Workshop, 2011 IEEE International, pp. 13–18. 

- Nagatani, K., Yoshida, K., Kiyokawa, K., Yagi, Y., Adachi, T., Saitoh, H., Suzuki, T., & Takizawa, O. (2007). Development of a networked robotic system for disaster mitigation—System description of multi-robot system and report of performance tests. In Proceedings of the 6th International Conference on Field and Service Robotics, pp. 333–342. 

- Noakes, M.W., Burgess, T.W., & Rowe, J.C. (2011). Remote systems experience at the Oak Ridge National Laboratory. A summary of lessons learned. In ANS EPRRSD-13th Robotics & Remote Systems for Hazardous Environments, 11th Emergency Preparedness & Response, CD-ROM. 

- Noakes, M.W., Haley, D.C., & Vagnetti, R. (2000). Deployment of remote systems in U.S. Department of Energy decontaminaton and decommissioning projects. 

- N.S.T. Center (2001). Working-level manual of shielding calculation for radiation facility (in Japanese). 

- Nuclear and Agency, I.S. (2011). Evaluation of the core of a nuclear reactor in the building 1, 2, and 3 in Fukushima Daiichi Nuclear Power Station, Tokyo Electric Power Company (in Japanese). Press Release: http://www.meti .go.jp/press/2011/06/20110606008/20110606008-2.pdf. 

- Okada, Y., Nagatani, K., Yoshida, K., Tadokoro, S., Yoshida, T., & Koyanagi, E. (2011). Shared autonomy system for tracked vehicles on rough terrain based on continuous three-dimensional terrain scanning. Journal of Field Robotics, 28(6), 875–893. 

- Rohmer, E., Yoshida, T., Ohno, K., Nagatani, K., Tadokoro, S., & Konayagi, E. (2010). Quince: A collaborative mobile robotic platform for rescue robots research and development. In Proceedings of the 5th International Conference on the Advanced Mechatronics (ICAM2010), pp. 225– 230. 

- Tokyo Electric Power Company (2011a). Plant Status of Fukushima Daiichi Nuclear Power Station (as of 

   - _Journal of Field Robotics_ DOI 10.1002/rob 

_Nagatani et al.: Emergency Response to the Fukushima Nuclear Accident using Rescue Robots_ • **63** 

- 3:00 pm, July 8). Press Release. http://www.tepco .co.jp/en/press/corp-com/release/11070808-e.html. 

- Tokyo Electric Power Company (2011b). Plant Status of Fukushima Daiichi Nuclear Power Station (as of 

- 3:00 pm, Sep. 1). Press Release. http://www.tepco .co.jp/en/press/corp-com/release/11090104-e.html. 

- Tokyo Electric Power Company (2011c), Record from March 11, 2011 to December 31, 2011, Press Release. http://www .tepco.co.jp/en/press/corp-com/release/betu1 ~~2 e~~ /images/ 120409e0202.pdf. 

- Ueda, K., Guarnieri, M., Hodoshima, R., Fukushima, E.F., & Hirose, S. (2010). Improvement of the remote operability for the arm-equipped tracked vehicle helios ix. In Proceedings of IEEE/RSJ International Conference on Intellegent Robots and Systems, pp. 363–369. 

- Yamauchi, B. (2004). Packbot: A versatile platform for military robotics. Proceedings of SPIE, 5422, 228– 237. 

- Yoshida, T., Nagatani, K., Koyanagi, E., Hada, Y., Ohno, K., Maeyama, S., Akiyama, H., Yoshida, K., & Tadokoro, S. (2009). Field experiment on multiple mobile robots conducted in an underground mall. In Field and Service Robotics, 62, 365– 367. 

- Yoshida, T., Irie, K., Koyanagi, E., & Tomono, M. (2010). A sensor platform for outdoor navigation using gyroassisted odometry and roundly-swinging 3d laser scanner. In The 2010 IEEE/RSJ International Conference on Intelligent Robots and Systems, pp. 1414– 1420. 

_Journal of Field Robotics_ DOI 10.1002/rob 

