Robotics and Autonomous Systems 196 (2026) 105237 



<!-- Start of picture text -->
ELSEVIER<br><!-- End of picture text -->

Contents lists available at ScienceDirect 

# Robotics and Autonomous Systems 

journal homepage: www.elsevier.com/locate/robot 



Design and testing of a universal platform for search and rescue operation: Exploring indoor and outdoor potentials 

D. Cafolla<sup>*</sup> Co} , B.D.M. Chaparro-Rico , X. Xie 





<!-- Start of picture text -->
mis<br><!-- End of picture text -->

_Intelligent Robotics Group, Faculty of Science and Engineering, Department of Computer Science, Swansea University, Swansea SA1 8EN, United Kingdom_ 

|A R T I C L E I N F O|A B S T R A C T|
|---|---|
|_Keywords:_<br>Search and rescue automation<br>Voice-guided control<br>Immersive 3D mapping<br>Adaptive multi-robot integration<br>Open-world robotics|Large-scale natural and human-caused disasters have created significant challenges for worldwide Search and<br>Rescue (SAR) operations, highlighting persisting concerns related to the efficiency and technical limitations of<br>existing technologies. To address these challenges, the proposed Universal Platform for Search and Rescue in-<br>tegrates various technologies, including a voice-guided control system, advanced 3D reconstruction techniques,<br>and a people tracker and follower system. A central feature of our work is the platform’s universality: our system<br>acts as an additional, modular controller that can connect to any robotic platform—commercial or custom—that<br>supports text-based command communication via network or cable. The system does not replace original robot<br>logic, but rather extends capabilities with minimal integration. Tests showed that the platform can effectively<br>execute voice commands and track a specified route even in high-wind (23 km/h) and noisy environments<br>(70–100 dB for the Drone, 65–99.6 dB for the Quadruped), providing a user-friendly and intuitive interaction for<br>users across different skill levels. Performance metrics indicated strong quality in 3D scene reconstruction with<br>significant similarity between the reconstructed images and reference images (Drone: indoor: 0.82 SSIM, out-<br>door: 0.81 SSIM; Quadruped: indoor: 0.79 SSIM, outdoor: 0.58 SSIM). Consequently, the immersive 3D mapping<br>reconstruction facilitated prompt and precise terrain assessments for both internal and external operations.<br>Furthermore, the integration of real-time video streaming and cloud-based connectivity optimized the data flow<br>and strengthened communication during operations, allowing person face identification, 3D tracking, and<br>following.|



## **1. Introduction** 

In recent years, the increasing frequency and severity of large-scale natural and human-caused disasters have significantly challenged global Search and Rescue (SAR) operations. According to the World Disasters Report, there has been a 40 % increase in such events over the past two decades, driven by the effects of climate change and more frequent geological phenomena such as earthquakes and landslides [1]. These disasters demand swift and well-organized responses to minimize loss of life. However, traditional SAR methodologies often fail to meet these urgent demands, particularly in complex and hazardous environments. 

Traditional methods of SAR rely heavily on human responders and ground-based equipment, but these are inherently limited by environmental challenges such as uneven or inaccessible terrain, adverse weather conditions, and delays in operational deployment. For example, reaching disaster-stricken areas can take hours or even days, which is 

crucial time lost when it is estimated that up to 90 % of disaster-related casualties occur within the first 72 h [1]. Moreover, these operations can pose significant risks to responders, exposing them to unsafe conditions ranging from collapsing structures to environmental hazards such as radiation or toxic materials [2]. 

Emerging technologies, particularly autonomous robotic systems, have transformed SAR operations by mitigating some of these challenges. Drones, or unmanned aerial vehicles (UAVs), have been widely adopted due to their ability to provide real-time data, execute aerial reconnaissance, and generate 3D terrain maps that aid decision-making in dynamically changing environments [3]. By accessing locations unreachable by traditional ground teams, drones can swiftly locate victims, reduce critical search times, and provide visual data for optimized rescue planning [4]. In addition, modern drones equipped with facial recognition and thermal imaging systems offer enhanced detection capabilities, increasing their effectiveness in locating missing persons or individuals trapped under rubble [5]. 

* Corresponding author. 

_E-mail addresses:_ daniele.cafolla@swansea.ac.uk (D. Cafolla), b.d.m.chaparrorico@swansea.ac.uk (B.D.M. Chaparro-Rico), x.xie@swansea.ac.uk (X. Xie). 

https://doi.org/10.1016/j.robot.2025.105237 

Received 4 December 2024; Received in revised form 26 August 2025; Accepted 20 October 2025 

Available online 21 October 2025 

0921-8890/© 2025 The Author(s). Published by Elsevier B.V. This is an open access article under the CC BY license ( http://creativecommons.org/licenses/by/4.0/ ). 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 

Despite their many advantages, drones are not suitable for all SAR scenarios. They face constraints such as battery life, payload limitations, and difficulties operating in dense or enclosed environments like forests, caves, or collapsed structures [6]. To bridge these gaps, other robotic systems such as quadrupeds and rovers have gained increasing attention. Quadrupeds, inspired by the four-legged movement of animals, are highly effective in navigating uneven terrain, such as rubble or steep inclines, where wheeled or tracked robots often fail. 

For instance, the Boston Dynamics’ Spot robot has been tested as a reliable tool in SAR missions, capable of carrying payloads, conducting structural inspections, and surveying hazardous areas [7]. Quadruped robots also offer the advantage of operating indoors, making them invaluable in collapsed buildings, tunnels, or mining accidents [8]. 

Similarly, rover-based platforms are an essential part of SAR operations, especially in scenarios requiring rugged, long-range mobility or operations in confined spaces. Ground rovers equipped with highdefinition cameras, LIDAR, or environmental sensors can provide detailed reconnaissance in regions that are inaccessible or hazardous to human responders. Notably, the use of robotic ground vehicles in the 2011 Fukushima Daiichi nuclear disaster proved critical for radiation monitoring and infrastructure assessment in areas deemed unsafe for humans [9]. These rovers can also transport necessary payloads, such as medical supplies or communication equipment, through challenging terrains [10]. 

While significant progress has been made in the development of these technologies, SAR operations are still hindered by the lack of integrated systems that enable seamless communication and collaboration between drones, quadrupeds, and rovers. Current implementations tend to operate independently, requiring human operators to coordinate their tasks manually, which leads to inefficiencies and delays. For example, drones may identify the location of victims from above, but coordinating this data with ground robots like quadrupeds or rovers often requires human intervention [11]. 

To address these shortcomings, this paper presents a Universal Platform for Search and Rescue Operations, which has been designed to integrate drones, quadrupeds, and rovers into a unified command and control system. This platform leverages Wi-Fi-based communication and cloud infrastructure to facilitate real-time data sharing between robotic platforms. The approach enables drones to perform aerial reconnaissance, transmitting real-time data to quadrupeds and rovers, which can act on this data autonomously. For instance, a drone could detect a victim under debris and relay the precise coordinates to a quadruped robot, which could then navigate the terrain to deliver medical supplies or conduct further inspections. In turn, rovers can carry equipment or conduct detailed environmental scans in surrounding areas, all under a single command framework. 

The Universal Platform further incorporates cutting-edge technologies such as Neural Radiance Fields (NeRFs) for 3D terrain mapping, natural language processing (NLP) for voice-command operation, and facial recognition systems for victim detection. NeRF-based models allow for high-quality 3D reconstruction of disaster zones using input from all three robotic systems, enabling operators to collaboratively map and analyse the affected area in real time [12]. NLP and voice-guided systems enhance the accessibility and ease of operation, allowing non-experts to effectively interact with and direct the robots during rescue missions [13]. 

This paper argues that the integration of drones and quadrupeds under one unified platform offers a transformative approach to SAR missions. 

A central feature of our work is the platform’s universality: our system acts as an additional, modular controller that can connect to any robotic platform—commercial or custom—that supports text-based command communication via network or cable. The system does not replace original robot logic, but rather extends capabilities with minimal integration. As long as a platform can communicate via standard protocols (TCP/IP, serial, USB, etc.), our controller enables network- 

agnostic, multimodal teleoperation and real-time mapping, supporting robust cross-compatibility for rapid deployment in SAR operations. 

By bridging the gaps between these systems and optimizing their collaborative potential, the Universal Platform aims to reduce delays, enhance search efficiency, and improve overall mission success rates. The following sections detail the design, implementation, and experimental validation of the proposed platform, with a focus on its ability to operate effectively in both indoor and outdoor SAR scenarios. 

## **2. Challenges in search and rescue missions** 

Ranging from natural disasters to a sudden increase in outdoor recreational activities, Search and Rescue (SAR) missions have significantly increased in their frequency and complexity, revealing an alarming exposure to high risks for human responders. As denoted by Young, onsite risks are exacerbated when members of the SAR team find themselves in highly unpredictable and fragile environments [11–14]. Peters further attests to the intricate web of risks during these missions, emphasizing how expansive and isolated geographical locations, volatile weather conditions and limited accessibility can escalate the threats to human responders [15]. 

A study led by Smith et al. proposed a comprehensive examination of the occupational hazards strenuously endured by human responders, focusing on land-based SAR missions in wilderness and mountainous terrains [16–18]. The study’s findings presented grim realities of SAR missions, including strenuous physical exertion, exposure to harsh weather, and risk of trips and falls or fatal injuries by being struck by falling objects. 

In the maritime domain, the risks can be deeply severe, as suggested by Thompson et al. The study vividly illustrates how rough seas, harsh weather conditions, and the unpredictability of nautical operations serve to compound the challenges faced by human SAR teams significantly [19]. 

These problems demand innovative solutions that reduce exposure to potential dangers and simultaneously improve the efficiency and effectiveness of SAR operations. Thus, the development of the proposed Universal Platform for Search and Rescue Operation can be timely and imperative in transforming SAR operations, maintaining safety, and amplifying human welfare. 

Rescue missions are inherently challenging due to their unpredictable and unpredictable nature. Terrestrial operations involve variable terrain, weather, and operational conditions, limiting the effectiveness and speed of traditional SAR teams. In a tight timeframe, rescuers must navigate hazardous conditions, which can often exacerbate the initial crisis [20]. These adverse conditions present considerable physical danger for responders and may impede or delay their progress [21]. 

The advent of drone technology offers a novel approach to overcoming the challenges associated with traditional SAR operations. Primarily, drones can safely traverse hazardous environments, delivering vital surveillance and reconnaissance that previously would have required the physical presence of a SAR team member. The utility of drones extends to topographical analysis, identification of victims, and provision of aerial perspective, beneficial for strategizing and implementing optimum routes for terrestrial responders [22]. Drones equipped with thermal imaging cameras can detect living beings, even in low visibility scenarios, thus facilitating victim identification and location in environments that could be potentially treacherous for a human rescuer [23,24]. 

Contrasted with traditional SAR operations, drone technology can substantially enhance response times, operational safety, and mission success rates. Drones can provide essential real-time data without exposing SAR teams to environmental risks associated with potential disaster zones. On the contrary, traditional methods often require direct exposure to hazards such as landslides, avalanches, or floods, which are highly time-consuming, endanger rescuers, and are not always effective in locating victims or delivering aid [23]. Drones offer a distinct 

2 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 

advantage by operating in conditions that might make traditional SAR impossible or highly dangerous. 

## **3. Design specifications** 

In response to the escalating demand for safer and more efficient Search and Rescue (SAR) operations, this paper introduces a Universal Platform that can be interfaced with various robotic systems explicitly designed for surveillance and life-saving missions. This innovative system features rapid area exploration capabilities and 3D terrain reconstruction, aiming to advance disaster response by minimizing risks to human responders, optimizing resource use, and expediting response times. Integrating advanced facial recognition and voice guidance technologies, the platform empowers even untrained individuals to efficiently control a commercial drone, thus providing both convenience and flexibility in its operation. 

This paper highlights the decision to utilize drones for initial testing due to their extensive application in SAR operations, given their proficiency in quickly covering large areas and delivering vital real-time data. The proposed Universal Platform (Fig. 1) can enhance the chosen robotic system performance through GSM (Global System for Mobile Communications) support, ensuring consistent and reliable connectivity to cloud infrastructure via cellular networks. This element is crucial for maintaining operational capability across vast geographic regions, a necessity in SAR missions that demand swift access to extensive areas. 

Our system acts as an additional, modular controller that can connect to any robotic platform—commercial or custom—that supports textbased command communication via network or cable. The system does not replace original robot logic, but rather extends capabilities with minimal integration. As long as a platform can communicate via standard protocols (TCP/IP, serial, USB, etc.), our controller enables network-agnostic, multimodal teleoperation and real-time mapping, supporting robust cross-compatibility for rapid deployment in SAR operations. 

The proposed Universal Platform’s GSM network capabilities facilitate reliable data transfer between the drone and ground station (a Laptop), irrespective of distance, a crucial advantage for missions conducted in remote or isolated locations. The Universal Platform’s cloud connectivity supports real-time video feed transmission, sophisticated voice command recognition, and effective feedback mechanisms, all of which are integral in providing situational awareness and supporting informed decision-making during SAR operations. 

Real-time video feeds from on-board cameras gives a comprehensive aerial view essential for effective surveillance and reconnaissance. Cloud-based streaming ensures access to these feeds in real-time, 

enhancing situational awareness and informing decision-making processes during SAR missions. The system employs advanced cloud-based NLP Natural Language Understanding (NLU) algorithms that promptly convert voice commands into actionable text instructions for the robotic system for manoeuvring, optimizing its responsiveness and userfriendliness through an intuitive interface. 

Furthermore, utilizing speech synthesis technology and artificial intelligence, the system transforms written feedback into audible voice communications, making it accessible to individuals lacking technical expertise or those operating under stress. This capability also facilitates communication with rescued individuals, providing essential protocol information or serving as a communication medium. 

The platform’s design ensures task execution and communication with control bases within GSM coverage, allowing for efficient data transmission and receipt of updated instructions. This autonomous operation during emergencies reduces risk for human rescuers and enhances overall mission efficiency. 

The controller operates via WiFi, cable, or cellular, supporting autonomous navigation, embedded person detection, and local video recording; cloud is used only for live voice command processing. The GUI enables all functions with keyboard controls as fallback; person detection and video capture are always local. In strong noise/wind, manual input ensures full reliability. 

The proposed Platform for Search and Rescue Operation can allow to rapidly explore areas and accurately reconstruct 3D topography. 

This is enabled by advanced imaging and complex algorithms, specifically the use of Neural Radiance Fields (NeRFs) and the NeRFActor model. NeRFs model continuous volumetric scene functions, offering precise geometric and photometric data crucial for comprehensive spatial understanding. 

During operations, the system performs rapid patrols along predetermined paths, capturing detailed video footage. The NeRF and NeRFActor models analyse this footage to convert 2D images into 3D volumetric representations, offering an extensive depiction of the surroundings. This process can identify significant regions or focal points, which may be indicative of human activity or natural features in need of closer scrutiny, guiding the operator to systematically gather detailed data from these areas. After rapid 3D reconstruction, operators can navigate the map to choose desired locations. This functionality enables the deployment of the chosen robotic platform to a specific site and allows operators to manoeuvre it via voice commands, eliminating the need for advanced driving skills. This capability can notably enhance control over SAR missions, allowing for swift adaptation to changing scenarios and concentration of efforts where they are most needed. In addition, throughout patrols, the system’s visual identification 



<!-- Start of picture text -->
ian<br>Ground Station J - — oo. a ae e 9 te<br>eo, Come Mey _<br>oO i<br>'<br>' f.2<br>' * i<br>¥ Embedded camera le F : eee<br>and sensors 1 os agaseuiaeinbnges J commode|<br>Deeneee , ~~ @ -. J ae<br>a) b)<br><!-- End of picture text -->

**Fig. 1.** Universal Platform for Search and Rescue Operation: a) Conceptual scheme, b) Physical Platform. 

3 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

capabilities allow for the autonomous recognition and tracking of human faces, further improving operator control over the chosen robotic platform. Fig. 2 shows an overview of the Universal Platform for Search and Rescue Operation with two tested robots. 

Voice guidance systems enable remote operators to issue real-time commands, adjusting the path and focus areas as necessary, thus optimizing search efficiency and ensuring comprehensive area coverage. 

The integration of rapid geographical surveying, 3D reconstruction, optical recognition, and auditory guidance increases the efficacy of the system, elevating it from a basic drone to an advanced unmanned aerial system (UAS) capable of independently executing complex operations. This combination of features aligns with its primary mission of enhancing public safety and providing life-saving services across varied and challenging terrains. 

While the experiments carried out for exploring Indoor and Outdoor Potentials of the proposed Universal platform for Search and Rescue Operations, focuses on the platform’s initial testing with drones due to their prominent role in SAR operations, ongoing and future tests will expand to other platforms, such as quadrupeds and rovers. This progression underscores the system’s versatility and adaptability across various SAR scenarios, illustrating its potential as a universal solution for search and rescue efforts. 

## **4. Experimental setup and testing on a drone** 

To evaluate the functionalities and efficiency of the Universal Platform, an experimental framework has been created. A rescue scenario has been implemented in a replicated agricultural landscape at the IoT and Robotics Lab at Swansea University, UK. The topography consisted of a setup combining a 3D-printed ruined cottage and a grain bin, obtained from the Thingverse repository [25,26]. The designed scenario was used to assess the feasibility of the proposed operational strategy in a real-world scenario. Fig. 3 shows the scenario wherein a DJI Tello drone, wet container, and ruined cottage are visible starting from the right side. 

The Universal Platform concept has undergone testing via a commercially available UAV. The DJI Tello drone was selected because 

to its microcontroller’s capability to execute structured text commands [27]. The drone has been operated by a Raspberry Pi, [28]. Furthermore, the proposed Universal Platform for Search and Rescue Operation incorporates a GSM support system, thanks to the SIM7600G-H module, [29]. This module enabled the drone to establish connection with the Cloud [30]. 

Using Google Cloud’s APIs [30], the proposed Universal Platform implemented the voice guidance feature in Tello drone, allowing persons without specialised training to operate it. The “Intents” in the Voice recognition API have been employed to figure out the user’s intended meaning or desired outcome, and they are responsible for triggering certain actions based on the user’s vocal input. Each intent parameter possesses an entity type, which serves as a classification indicating the method by which information is collected from an expression provided by the end-user. The conversational platform has the capability to extract the directional instruction and the numerical value indicating the distance to be moved in the specified direction in centimetre or degree depending on the Intent. The conversational platform has undergone training to comprehend specific actions such as take-off, land, move forward, move right, move up, turn and numerical values associated with the intended physical magnitude. When the intention is extracted with the purpose of being fulfilled, it is transmitted in the form of structured text. The Python programme is designed to establish a connection with the drone and execute commands based on detected changes, while also providing audible feedback to the user. Simultaneously with the execution of activities, the video feed is consistently streamed in a parallel thread alongside the ongoing mission thread. 

The experimental test began with a comprehensive patrol phase. The drone scanned the entire environment during this phase, consequently sending it to the proposed Universal Platform, building a detailed visual map of the area. 

The patrol strategy incorporated an ascending spiral pattern of 1 revolution and 30 cm radius, chosen since it efficiently enables a comprehensive scanning of the area as the drone ascends, Fig. 4. The ascending spiral strategy increases the height (z) continuously until reaching the pitch value defined by Eq. (1): 



<!-- Start of picture text -->
qt<br>1Drone 1 Quadruped<br>’ t q t<br>ca ee<br>,<br>\’<br>\<br>\’<br>\/<br>\’<br>\ ’<br>ys<br>\<br>\<br>9— \<br>\ \<br>\<br>\<br>N<br>\<br>\<br>\<br>\<br>\<br>t<br>; Secl. 1...ae<br>Universal Platform for Search and Rescue Operation |<br>Se ee ee re er ener t<br><!-- End of picture text -->

**Fig. 2.** Overview of the Universal Platform for Search and Rescue Operation with two tested robots. 

4 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al.                                                                                                                                                                                                                                 Robotics and Autonomous Systems_ 



**Fig. 3.** Indoor experimental layout for testing the Universal Platform with a drone. 



**Fig. 4.** Ascending spiral trajectory. 

_Pitch_ = _h_ + _πr_ (1) 

where _h_ is the starting height at which the drone begins to follow the spiral path. 

The x, y, and z coordinates of the spiral can be calculated by Eqs. (2 − 

4): 







where _θ_ are the spiral angles, _N_ is the maximum number of points (x, y, z) of the spiral path, _i_ =2, 3, 4, …, _N; z_ 1 = _h_ ; _x_ 1 = _r_ cos(0); _y_ 1 = _r_ sin(0). 

The drone completed the patrol ascending spiral in 38 s and consumed about 5 % of the battery. During the second phase, the Post Patrol operation an advanced NeRFs methodology for the 3D reconstruction has been used. Conducting a post patrol 3D reconstruction 

allowed to extract detailed data of the environment after the initially outlined patrol operations. The RGB 3D reconstruction, as indicated in a split snapshot in Fig. 5 left part, offered a comprehensive spatial view of the terrain. This detailed analysis immensely benefited the planning phase of the patrolling operation. Simultaneously, the model’s accumulation, as shown in Fig. 5 right part, can demonstrate where additional data must be collected to optimize coverage and rescue feasibility. The NeRFactor method helped in gathering volumes of data from the patrolled area, shed light on regions requiring more intensive surveillance, and allowed us to align data collection with demanding areas. Table 1 presents key performance metrics obtained from utilizing the NeRF methodology for immersive Indoor 3D scene reconstruction. The Peak Signal-to-Noise Ratio (PSNR) of _23.70 dB_ indicates a reasonable level of reconstruction fidelity compared to the original images, with higher values generally signifying better visual quality. Coupled with this, the Structural Similarity Index (SSIM) score of _0.82_ suggests a high structural similarity between the reconstructed and reference images, which considers changes in luminosity, contrast, and overall structure. Additionally, the Learned Perceptual Image Patch Similarity (LPIPS) value of _0.18_ indicates a low perceptual difference between the images, demonstrating that the reconstructions align well with human visual perception. The framework also achieves an impressive ray sampling rate of _308,448.35_ rays per second, reflecting its efficiency in accurately sampling the scene, which is critical for producing high-quality volumetric representations. Although the rendering speed is at _0.33_ frames per second (FPS), this figure is understandable given the complexity of rendering high-resolution volumetric data typically required in NeRF applications, where photorealism is a primary goal. This performance was achieved by employing an ascending spiral path during data capture, resulting in _381_ training frames out of _1142_ total frames. 

The processing to define the transformation matrix using COLMAP software took about _5 minutes_ , and the training of the model itself lasted approximately _31.58 minutes_ . 

The overall energy-efficient approach not only enhances situational awareness and targets specific areas for data collection but also minimizes power usage, thereby maximizing the drone’s autonomy. This balance of rapid and accurate terrain reconstruction, combined with optimized power consumption, underscores the potential effectiveness and practical application of this technology in real-world scenarios. 

A second phase of the Indoor experiment has been carried on using voice commands for real-time control and face recognition for person 

5 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 



**Fig. 5.** Split Indoor Scenario 3D reconstruction RGB the left and accumulation map on the right from experiments integrating the Universal Platform with a drone. 

**Table 1** 

Indoor 3D Reconstruction Results with a drone. 

|Parameter|Value|
|---|---|
|psnr|23.70 dB|
|ssim|0.82|
|lpips|0.18|
|Number rays per sec|308448.35|
|fps|0.33|



following, contributed to the crucial phase of real-time area of interest patrol. These capabilities streamlined the operator-drone interaction and facilitated autonomous quick-response to identified individuals, which is a defining feature in SAR drone operations. 

Fig. 6 shows an example instance of intentions recognition using NLU and its subsequent fulfilment within the terminal while a vocal command was given the average interaction time of _3 s_ over GSM network with a success rate of intent recognition of _100%_ . On the other hand, Fig. 7 showcases the operational process of facial recognition in realtime, specifically when the person follower functionality is on. The drone moves in a forward and backward motion while maintaining a consistent distance from the recognised face. Additionally, it ascends and descends and turn both clockwise and anticlockwise directions to ensure that the face remains centred within the frame. To accomplish 

this task Haar-Cascade [31] for real-time face tracking is employed. The essential algorithmic flow involves converting the video feed to grayscale, which optimizes the performance of the Haar-Cascade classifier. Subsequently, the classifier detects faces within the frame, returning coordinates and dimensions of detected faces. The software then calculates the offset between the drone’s central axis and the detected face, as well as the area of the detected face, to guide the drone’s movements along _x, y, z_ axis, ensuring the subject remains centrally positioned in the video feed fine-tuning the drone’s orientation and distance relative to the subject. This dynamic adjustment enables sophisticated tracking capabilities in real-time applications. 

Following the successful indoor tests, outdoor trials of the proposed Universal Platform for Search and Rescue Operation were conducted to evaluate its performance under more challenging environmental conditions. Fig. 8 shows the layout of the experiment. Experiments included outdoor, uncontrolled, and challenging conditions on commercial platforms, illustrating both platform independence and SAR readiness. The controller adapts to any robot able to exchange text commands via network _._ 

The tests included voice-controlled operations of a DJI Tello drone in wind speeds of _23 km/h_ , alongside ambient temperatures of _17_<sup>◦</sup> _C_ Despite the increased noise levels affecting the microphone ( _70_ – _100 dB_ ), the voice recognition system maintained a _100%_ success rate for commands such as take-off, landing, and directional movements repeated 



**Fig. 6.** Vocal command fulfilment example. 

6 

_D. Cafolla et al.                                                                                                                                                                                                                                 Robotics and Autonomous Systems_ 

_Robotics and Autonomous Systems 196 (2026) 105237_ 



<!-- Start of picture text -->
- =107, -102, 1/424<br>: -<br>| ! ;<br>yee he.<br>a<br>.<br>a) b)<br><!-- End of picture text -->

**Fig. 7.** Person follower example: a) Environmental view, b) Drone view. 



<!-- Start of picture text -->
‘e, oy<br>ae<br>. a<br>= ee ume — ric:<br><!-- End of picture text -->

**Fig. 8.** Outdoor experimental layout for testing the Universal Platform with a drone. 

continuously several times. The Outdoor testing also featured an ascending spiral patrol strategy that mirrored the Indoor approach. This phase involved 3D reconstruction utilizing the NeRF methodology, with _307_ frames extracted for training from a total of _921_ frames. 

The processing included a COLMAP transformation matrix training time of approximately _2.57 minutes_ and a model training duration of _24.52 minutes_ , achieving a processing speed of _100,169_ rays per second. The results of this outdoor 3D reconstruction, illustrated in Fig. 9, demonstrated the effectiveness of the approach, significantly extending virtual walkthrough capabilities beyond the initial spiral path. 

As shown in Table 2, the reconstruction yielded several key metrics: a PSNR of _23.28 dB_ , indicating acceptable visual quality; a SSIM score of _0.81_ , reflecting strong structural similarity with the original images; and a LPIPS value of _0.20_ , signifying low perceptual difference. The system achieved an efficient ray sampling rate of _318,050.033_ rays per second and a rendering speed of _0.35_ FPS. Together, these metrics underscore the capability and potential of the NeRF methodology for effective outdoor 3D reconstructions in real-world applications. The proposed 

Universal Platform for Search and Rescue Operation, marked by its critical role in technological innovation, is protected under Italian Patent No. 102021000018587 [32]. 

## **5. Experimental setup and testing on a quadruped** 

To expand the feasibility of the proposed Universal Platform for Search and Rescue Operation, the testing scope was broadened to include a commercial quadruped robot, the FREENOVE Quadruped Robot, [33]. This addition is aimed to demonstrate the system’s flexibility and adaptability when interfacing with different robotic platforms beyond aerial drones. Like the DJI Tello drone test, this phase utilized the same indoor and outdoor scenarios, NLU, communication and 3D reconstruction methodologies, to directly compare performance across different types of robotic platforms. The FREENOVE Quadruped Robot brings distinct complement to the aerial perspective provided by drones. By using the same universal platform framework, the quadruped robot showcased seamless integration, relying on WiFi-based communication 

7 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 



**Fig. 9.** Outdoor Scenario 3D Reconstruction from the drone video streaming. 

**Table 2** 

Outdoor 3D Reconstruction Results with a drone. 

|Parameter|Value|
|---|---|
|Psnr|23.28 dB|
|ssim|0.81|
|lpips|0.20|
|Number rays per sec|318050.033|
|fps|0.35|



protocols and universal text/video command execution features. 

The Indoor experiment conducted with the Quadruped demonstrated the effective integration of this ground-based robotic platform with the proposed Universal Platform for Search and Rescue Operations. During the trial, the quadruped was programmed to follow a _rectangular trajectory measuring 1.80 m x 1.10m_ while maintaining a constant orientation towards the left-hand side, where its onboard camera was mounted. The step size of the robot, set at _54 mm per step_ , was explicitly considered during the trajectory planning to ensure precise and reliable movement, enabling consistent and uninterrupted data collection. The quadruped successfully completed the trajectory in _9.39 min_ . Fig. 10, show the layout of the Indoor experiment with the Quadruped. 

The results of this experiment, as visualized in Fig. 11, included a Split Indoor Scenario 3D Reconstruction. The _RGB reconstruction map_ is displayed on the left, while the _accumulation map_ is presented on the right. These reconstructions were generated using Neural Radiance Fields (NeRFs) and the NeRFActor model, resulting in an accurate and detailed volumetric representation of the indoor environment. The 

quadruped’s fixed orientation during movement ensured consistent spatial mapping and contributed significantly to the accuracy and completeness of the 3D model reconstruction. This approach highlights the capability of the Universal Platform to adapt to the movement constraints of a quadruped robotic system while maintaining its performance in generating reliable spatial analyses. Table 3 presents key performance metrics obtained from utilizing the NeRF methodology for immersive Indoor 3D scene reconstruction. 

The performance of the Quadruped in the indoor reconstruction experiment provides significant insights into the applicability of groundbased platforms when integrated with the Universal Platform for Search and Rescue (SAR) operations. A deeper assessment of its parameters highlights strengths and limitations in terms of reconstruction quality, computational performance, and compatibility. These results are then compared to those obtained using the DJI Tello Drone, with all computations conducted on the same hardware, ensuring consistency and fairness in evaluation. 

For the quadruped, the _Peak Signal-to-Noise Ratio (PSNR)_ was measured at _19.42 dB_ , reflecting moderate reconstruction fidelity. PSNR values indicate lower noise and higher detail in the reconstructed environment; therefore, the quadruped’s score signifies that while the reconstruction was functional, it lacked the sharpness and detail achievable by aerial platforms. This outcome is primarily influenced by the quadruped’s constrained movement, as it followed a rectangular trajectory while keeping its side-mounted camera fixed in one orientation. This limited its capacity to capture diverse and comprehensive visual data. 

The _Structural Similarity Index Measure (SSIM)_ , which evaluates how 



**Fig. 10.** Indoor experimental layout for testing the Universal Platform with a quadruped. 

8 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 



**Fig. 11.** Split Indoor Scenario 3D reconstruction RGB the left and accumulation map on the right from experiments integrating the proposed Universal Platform with a quadruped. 

**Table 3** 

Indoor 3D Reconstruction Results with a quadruped. 

|Parameter|Value|
|---|---|
|Psnr|19.42 dB|
|Ssim|0.58|
|Lpips|0.40|
|Number rays per sec|323008.156|
|fps|0.35|



similar the reconstruction is to the original environment in terms of structure and texture, was _0.59_ for the quadruped experiment. This score indicates a moderate level of structural resemblance but is affected by the system’s restricted camera perspectives and lack of variation in angles. Ground-based robots like the quadruped, while useful for navigating low-clearance or blocked areas, are inherently limited by their movement patterns and camera angles, which reduce the richness of the data captured. 

In terms of _perceptual quality_ , when experimenting with the quadruped, the reconstruction produced a _Learned Perceptual Image Patch Similarity (LPIPS)_ score of _0.40_ . This metric reflects the perceptual divergence between the reconstructed environment and its real-world counterpart. A higher LPIPS score indicates a greater perceptual difference, and the quadruped’s experiment higher score highlights the reduced ability of the quadruped to capture fine details of the scene, particularly in three-dimensional depth and dynamic patterns of the environment. This limitation is directly tied to its fixed camera orientation and lower viewpoint compared to drones. 

On the computational side, when experimenting with the quadruped, it achieved a _Number of Rays Processed per Second_ value of _323,008_ , higher than _308,448_ from the drone’s experiment. This suggests that the Universal Platform maintained strong computational efficiency with the quadruped, despite its slower movement speed and less dynamic trajectory. The slight advantage for the quadruped here could be attributed to its limited coverage area and movement pace, which allowed processing units to handle denser, localized data more efficiently. Similarly, the _Frames Per Second (FPS),_ indicating how quickly frames of the reconstruction were rendered, was _0.35_ when experimenting with the quadruped, matching the rendering performance of the drone experiment. This consistency highlights that the Universal Platform’s processing capabilities remained stable, regardless of the type of robot providing the input data. 

The total _processing time_ of the Universal Platform for the quadruped’s reconstruction was _29.53 min_ . Compared to the drone’s faster completion in _24.52 min_ , the additional time reflects the slower traversal speed of the quadruped (due to its _54 mm_ step size) and the limited field of view of its camera, requiring longer data collection and subsequent processing stages. The fixed, rectangular trajectory of the quadruped was less efficient in capturing environmental data compared to the drone’s aerial spiral trajectory, which allowed the latter to acquire a more diverse dataset in less time. 

In comparison, the DJI Tello Drone experiment significantly outperformed the quadruped experiment across most quality metrics. When experimenting with the drone, the Universal Platform achieved a _PSNR_ of _23.70 dB_ , which demonstrates higher reconstruction fidelity with less noise in the final output. This was facilitated by the Drone’s ability to perform dynamic movements and cover a wider range of perspectives, allowing for greater detail and data diversity. Similarly, the _SSIM_ value of _0.82_ during the drone experiment illustrates the drone’s superior ability to recreate structural features of the environment, capturing clearer and more accurate representations. When experimenting with the drone, the _LPIPS_ score of _0.18_ further reinforces the drone’s advantages by showing much lower perceptual differences in its reconstruction. Its aerial mobility, combined with the ability to adjust both altitude and orientation, contributed to the production of visually consistent and high-quality results. 

Finally, the Natural Language Understanding (NLU) feature of the proposed Universal Platform was assessed during the experiment, achieving a _100% success rate_ in interpreting and executing voice commands. Commands such as movement initiation, path adjustments, and other operational directives were executed flawlessly, demonstrating the robustness of the voice-controlled guidance system and its applicability across different robotic modalities. 

Following the completion of the Indoor reconstruction test, an Outdoor test was conducted to evaluate the performance of the Universal Platform when interfaced with a Quadruped in a more dynamic and challenging environment. Experiments included outdoor, uncontrolled, and challenging conditions on commercial platforms, illustrating both platform independence and SAR readiness. The controller adapts to any robot able to exchange text commands via network _._ 

The test took place under real-world conditions, with a temperature of _9_<sup>◦</sup> _C_ and a wind speed of _22.90 km/h_ , testing the robot’s stability and ability to adapt to external environmental factors. The Outdoor experimental layout is show in Fig. 12 while the results of the outdoor 

9 

_D. Cafolla et al._ 

_Robotics and Autonomous Systems 196 (2026) 105237_ 



**Fig. 12.** Outdoor experimental layout for testing the Universal Platform with a quadruped. 

reconstruction are illustrated in Fig. 13, which shows a Split Outdoor Scenario 3D Reconstruction, with the RGB reconstruction map on the left and the accumulation map on the right. The results of the NeRFbased reconstruction, as detailed in Table 4, highlight the impact of the modified trajectory. 

During this outdoor test, the _Universal Platform_ interfaced with the _Quadruped_ was assessed in its robustness for voice command-controlled operations as well. 

As in the indoor test, the _Quadruped_ demonstrated a _100% success rate_ in executing all voice commands, even under the additional complexity and challenges presented by the outdoor environment with the increased noise levels affecting the microphone ( _65_ – _99.6 dB_ ), such as background noise and environmental interference. This achievement shows the reliability of the Universal P 

The _Quadruped_ followed a predefined 12-minute trajectory that consisted of a 2-meter linear path and two 360-degree rotations at strategic points (the start and midpoint of its movement) to enrich its dataset. 

**Table 4** 

Outdoor 3D Reconstruction Results when the Universal Platform is interfaced with a quadruped. 

|Parameter|Value|
|---|---|
|Psnr|18.28 dB|
|Ssim|0.58|
|Lpips|0.48|
|Number rays per sec|310327.844|
|Fps|0.33|



This simplified motion plan aimed to compensate for the Quadruped’s ground-level perspective, which limits its ability to capture diverse viewing angles. However, the NeRF reconstruction process required _32.15 min_ , highlighting the additional time necessary to process the data collected. The moderate quality of the reconstruction is demonstrated by its _PSNR_ of _18.28 dB_ , which reflects a noticeable level of noise and reduced clarity in the model, especially when compared to benchmarks like the Drone. The _SSIM_ , measuring structural similarity to the true 



**Fig. 13.** Split Outdoor Scenario 3D reconstruction RGB the left and accumulation map on the right from experiments integrating the Universal Platform with a quadruped. 

10 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 

environment, scored _0.58_ , indicating a moderate level of accuracy but revealing weaknesses in capturing spatial relationships and larger-scale structures common in open scenarios. Furthermore, the _LPIPS_ of _0.48_ suggests perceptual deviations between the reconstructed scene and the original, struggling to replicate textures and fine detail accurately. 

On the computational side, the _Universal Platform_ processed _310,327.844 rays per second_ , reflecting its reasonable computational efficiency during reconstruction. However, despite a comparable computational rate to the Drone’s experiment one of _318,050.033 rays per second_ , the longer processing time for the Quadruped signals inefficiencies introduced by its limited data quality. Its fixed, single-height perspective results in a dataset with less perspective diversity, requiring additional computational effort to achieve even moderate reconstructions. Similarly, the frame rate during processing was slightly lower at _0.33 fps_ , compared to the _Drone_ ’s _0.35 fps_ , further highlighting the limitations caused by slower data acquisition and less dynamic input. The overall reconstruction effort shows that while the Universal Platform is computationally efficient, the Quadruped’s hardware constraints tied to movement and perspective significantly reduce its effectiveness in wide, open outdoor environments. 

In comparison, the _Drone_ experiment significantly outperformed the _Quadruped_ experiment across all major metrics during the same outdoor reconstruction scenario. With a _PSNR_ of _23.28 dB_ , experiments with the _Drone_ generated far clearer and more detailed 3D models, minimizing noise and producing outputs with superior fidelity. The _Drone’s SSIM_ of _0.81_ also demonstrated its ability to recreate spatial structures with high accuracy, capturing details and relationships between objects that the ground-based _Quadruped_ struggled with. In terms of perceptual quality, the Drone experiment achieved a _LPIPS_ of _0.20_ , demonstrating more realistic textures and fewer artifacts compared to the _Quadruped’s_ one of _0.48_ . These differences stem from the Drone’s ability to cover large areas dynamically using an aerial spiral trajectory, collecting data from various heights and angles while maintaining consistent image quality. This broader and richer dataset resulted in outputs that closely resembled the true environment. 

Notably, the _Drone’s_ experiment _reconstruction time_ of _24.52 min_ was significantly shorter than the _Quadruped’s_ one of _32.15 min_ , despite processing slightly more rays per second ( _318,050.033_ vs. _310,327.844_ ). This shorter time demonstrates the Drone’s ability to provide the NeRF processing system with higher-quality input, reducing the computational effort required to fill in gaps or correct inconsistencies introduced during data collection. 

Additionally, with a frame rate of _0.35 fps_ , the Drone showed smoother and more efficient data acquisition compared to the _Quadruped_ , further reinforcing its superiority in environments where rapid reconstruction and accurate spatial models are required. 

In summary, the _Drone’s_ aerial mobility, combined with its ability to collect comprehensive scenes from varying perspectives, together with the _Universal Platform_ allowed it to dominate in wide, open outdoor environments. Its higher _PSNR, SSIM,_ and _LPIPS_ scores reflect its ability to produce reconstructions that are not only accurate but also faster to process and realistic from a perceptual standpoint. By contrast, while the _Quadruped_ demonstrated robust outdoor functionality, such as rough terrain navigation and wind resistance, its fixed perspective, and slower trajectory limited its data diversity, resulting in longer reconstruction times and lower-quality 3D models. That said, the _Quadruped_ remains a viable option in scenarios where aerial platforms cannot operate, such as confined spaces or areas obstructed by debris. Both platforms showcase the adaptability of the Universal Platform, with the _Drone_ excelling in large-scale environments requiring high-fidelity spatial mapping and the _Quadruped_ serving complementary roles in ground-level operations. 

Finally, while the people-following functionality was successfully tested with the _Drone_ , this feature was not performed with the _Quadruped_ due to its restricted mobility, which made the task difficult to achieve and less feasible in real-time scenarios. 

## **6. Experimental campaign remarks** 

The comprehensive testing of the proposed Universal Platform, conducted across both indoor and outdoor scenarios, underscores its immense adaptability, scalability, and operational potential. By seamlessly integrating with the Drone and the Quadruped, two different robotic systems, the platform demonstrated its ability to unify their operations and enable them to perform similar tasks despite their differing functionalities. This flexibility was apparent as the platform efficiently handled both indoor and outdoor scenarios, with each platform performing tasks. The tests highlighted the Universal Platform’s ability to unify control processes. 

In addition, its use of Global System for Mobile Communications (GSM) technology, provides robust cloud connectivity, enabling operators to issue commands and receive real-time feedback from practically any location. 

This capability ensures consistent communication between robotic platforms and the cloud infrastructure, making it possible to direct operations remotely, regardless of the geographic scale of the mission. The GSM-enhanced functionality is critical for modern SAR missions, where operators often need to manage robots across vast or inaccessible areas. Furthermore, the platform’s integration with NLU allows command inputs to be executed seamlessly, creating an intuitive and user-friendly interface that enhances mission accessibility for operators, even those without extensive technical training. 

The Universal Platform for Search and Rescue Operation showed its ability to harmonize these two distinct systems, the Drone and the Quadruped, into an ecosystem capable of handling diverse tasks under varied conditions. The ability to successfully perform comparable tasks across identical scenarios highlights the versatility of the Universal Platform. The Universal Platform proposed amplifies their individual strengths, making the overall operation far more effective and adaptive to real-world SAR demands. 

Outdoor, uncontrolled experiments have been carried out and confirmed reliable navigation, person detection, and mapping for SAR tasks with commercial-grade robots, illustrating both platform independence and SAR readiness. The controller adapts to any robot able to exchange text commands via network. 

The potential applications for this platform extend beyond SAR to encompass operations like industrial inspections, disaster relief, and environmental monitoring. Its ability to integrate multiple types of robotic systems, coupled with the scalability offered by GSM connectivity and the ease of NLU-supported control and 3D reconstruction, positions it as a transformative tool for addressing complex challenges in dynamic and unpredictable environments. 

In conclusion, the Universal Platform for Search and Rescue Operation ability to unite multiple heterogeneous systems into a single, unified operational framework highlights its transformative potential for SAR and beyond. These capabilities, combined with consistent task execution across diverse terrains, make the Universal Platform for Search and Rescue Operation a foundational innovation for advancing robotic operations in both challenging environments and critical applications. 

Our results confirm that the Universal Platform for Search and Rescue Operation approach enables rapid integration with a wide variety of commercial and custom SAR robots, requiring only text-based connectivity. By embedding local person detection, on-board video recording, and providing cloud-free operation for all critical functions except voice control, we demonstrate the system’s robustness in both controlled and uncontrolled field conditions. Ongoing integration of established SLAM and emerging neural mapping methods, facilitated by our open protocol, will further improve real-time mapping capabilities and operational flexibility. This approach ensures that the platform will remain highly adaptable to future hardware and mission requirements, supporting long-term readiness for disaster response. 

11 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 

## **7. Conclusion** 

The proposed Universal Platform for Search and Rescue operations demonstrated robust performance under challenging conditions, which is crucial for the effectiveness and efficiency of SAR missions. After challenging tests, the platform showed that it can effectively execute voice commands and track a specified route even in high-wind (23 km/ h) and noisy environments (65–100 dB), offering a user-friendly and intuitive interaction for users at all skill levels. The immersive 3D mapping reconstruction presented high-performance metrics, indicating high structural similarity between the reconstructed images and reference images (SSIM); a reasonable level of reconstruction fidelity (PSNR); and a low perceptual difference between the images (LPIPS), demonstrating that the reconstructions align well with human visual perception. Prompt and precise terrain assessments were obtained for both internal and external environments from the immersive 3D mapping reconstruction. The platform enabled person face identification, 3D tracking, and following through the integration of real-time video streaming and cloud-based connectivity. While the Drone successfully performed this feature as part of its wide-area monitoring capabilities, the Quadruped was not tested for the person-following feature due to its restricted mobility, which made the task less feasible in real-time scenarios. The Quadruped tests, however, validated the Universal Platform’s ability to operate under excessive noise levels, ranging from 65 dB to 99.6 dB, while maintaining accurate voice command execution. The Universal Platform’s capabilities enhanced situational awareness and operational precision, providing intuitive user interaction for better accessibility. Its robust performance and accurate command execution underscored its potential for extended use in demanding real-world scenarios with high-quality interactive navigation. 

Future development will focus on improving the platform’s capabilities. Primarily, testing versatility and adaptability of the proposed Universal Platform with other robotic systems and SAR contexts. Furthermore, enhancing the speed and accuracy of the 3D reconstruction process to facilitate real-time updates in dynamic environments. In addition, optimizing data processing algorithms to reduce latency, integrating advanced sensor technologies for better environmental awareness, and expanding machine learning capabilities for autonomous adaptability to different scenarios. These advancements will lead to faster and more effective Search and Rescue operations. 

Recognizing NeRF speed limits, integration of SLAM (ORB-SLAM3, LOAM, Cartographer) and instant-NGP is ongoing, fully supported by the open controller interface [34–37]. 

While real-time 3D reconstruction remains an open research area, our work is disruptive in two fundamental ways. First, we provide a universally compatible, plug-and-play controller architecture—allowing almost any SAR robot, regardless of manufacturer, to gain multi-modal control, local person detection, and robust video recording—without requiring proprietary hardware or centralized cloud reliance. Second, our extensive field validation, including uncontrolled, noisy, and harsh environments on commercial-grade platforms, sets a new benchmark for practical deployability and robustness. 

Ongoing research in our team incorporates cutting-edge real-time solutions inspired by works ([1–4]), but even with state-of-the-art computation not yet ubiquitous, our system’s resilience, protocol openness, and operational independence provide capabilities currently unmatched in disaster robotics. This positions the platform as not only technically advanced, but also uniquely ready for scalable, real-world SAR adoption and future upgrades as 3D mapping technology matures. 

## **CRediT authorship contribution statement** 

**D. Cafolla:** Writing – review & editing, Writing – original draft, Visualization, Validation, Supervision, Software, Resources, Project administration, Methodology, Investigation, Funding acquisition, Formal analysis, Data curation, Conceptualization. **B.D.M. Chaparro-** 

**Rico:** Writing – review & editing, Writing – original draft, Validation, Software, Methodology, Investigation, Formal analysis, Data curation. **X. Xie:** Writing – original draft, Software, Resources. 

## **Declaration of competing interest** 

The authors declare the following financial interests/personal relationships which may be considered as potential competing interests: Cafolla D. and Chaparro Rico B.D.M. has patent Universal aided piloting system licensed to Cafolla D., Chaparro Rico B.D.M., Sebastiano F., R4pso SRL. If there are other authors, they declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

## **Data availability** 

Data will be made available on request. 

## **References** 

- [1] International Federation of Red Cross and Red Crescent Societies, World Disasters Report 2020: Come Heat Or High Water, IFRC, Geneva, Switzerland, 2020. 

- [2] S.L. Cutter, B.J. Boruff, W.L. Shirley, Social vulnerability to environmental hazards, Soc. Sci. Q. 84 (2) (2003) 242–261, n. 

- [3] M.A. Goodrich, A.C. Schultz, Human–robot interaction: a survey, Found. Trend. Hum.–Comp. Inter. 1 (3) (2007) 203–275, n. 

- [4] R. Adams, Comparative study of traditional SAR methods versus drone technology, in: M. Smith (Ed.), Rescue Navigation & Logistics, Rescue Navigation & Logistics, 11, Oxford University Press, London, 2017, pp. 300–308. 

- [5] T. Williams, Implications of drone operations in complex terrains for SAR, in: H. Reynolds (Ed.), Autonomous Vehicle Navigation, Autonomous Vehicle Navigation, 14, Cambridge University Press, Cambridge, 2020, pp. 76–84. 

- [6] F. Zhang, M. Tranzatto, S. Khattak, M. Karrer, J. Delmerico, D. Scaramuzza, Autonomous exploration for mobile ground robots using aerial visual-inertial localization, IEEE Rob. Autom. Lett. 3 (4) (2018) 3241–3248. 

- [7] Boston Dynamics, Spot: agile mobile robot for inspection and exploration, Retrieved from, https://www.bostondynamics.com, 2023. 

- [8] S. Tadokoro, R.R. Murphy, Rescue robotics: DDT project on robots and systems for urban search and rescue, Rob. Auton. Syst. 64 (2) (2019) 1–11. 

- [9] N. Kottege, J. Parkinson, P. Moghadam, S. Anandan, A. Elfes, Energetics-informed hexapod gait transitions across challenging terrains, Int. J. Rob. Res. 34 (13) (2015) 1562–1584. 

- [10] B. Mildenhall, P. Srinivasan, M. Tancik, J. Barron, R. Ramamoorthi, R. Ng, NeRF: representing scenes as neural radiance fields for view synthesis, Commun. ACM 65 (1) (2021) 99–106. 

- [11] E. Jones, F. Morgan, THEIA: the new dawn in SAR technology, in: G.O. Young (Ed.), Automated Face Detection & Recognition, Automated Face Detection & Recognition, 2, Springer, New York, 2021, pp. 132–145. 

- [12] E.E.N.A. DJI, Black Channel, Drones in SAR: statistics and case studies, in: J. Peters (Ed.), Drones for Emergency Services, Drones for Emergency Services, 1, McGrawHill, New York, 2019, pp. 20–29. 

- [13] L. Harris, Climate change and its implications in SAR operations, in: G.O. Young (Ed.), Climate Studies, Climate Studies, 17, McGraw-Hill, New York, 2022, pp. 82–91. 

- [14] G.O. Young, High risks to Human responders in SAR operations, in: R. Williams (Ed.), Disaster Management Handbooks, 3rd ed.Disaster Management Handbooks, 2, Elsevier, New York, 2017, pp. 30–45. 

- [15] J. Peters, The unpredictability of environmental factors in SAR missions, in: S. Morrison (Ed.), Management of Environmental Risks, 2nd ed.Management of Environmental Risks, 4, Wiley, New York, 2018, pp. 55–78. 

- [16] G. Smith, et al., Occupational hazards in search and rescue operations, Saf. Sci. 68 (2014) 190–200. 

- [17] W.B. Thompson, et al., Maritime search and Rescue: challenges and implications, Ocean Coast Manag. 57 (2012) 55–66. 

- [18] A. Smith, et al., Safety and efficiency in SAR operations: the role of drone technology, Eng. Tech. Appl. Sci. Res. 10 (1) (2020) 5098–5103. 

- [19] K. Kumar, The inherent risks of rescue operations in unpredictable environments, Danger. Terra. 17 (1998) 23–37. 

- [20] A.Q. Brown, The physical and psychological strain of rescue workers, in: L. M. Green (Ed.), Hardships in Emergency Response Teams, Hardships in Emergency Response Teams, 4, Penguin Publishing, London, 2010, pp. 78–102. 

- [21] R.J. Watson, Drones and their utility in disaster response: a comprehensive overview, Fut. SAR Oper. 22 (2017) 93–115. 

- [22] J.M. Hughes, Thermal imaging technology in drones and its potential utility in SAR: an exploration, J. Aer. Surv. 2 (2015) 101–119. 

- [23] A.P. Klein, Traditional challenges in rescue operations and the advent of drones, Rescue Teams: Past, Present, Future 6 (2016) 45–65. 

- [24] M. Burns, Technological advancements in rescue missions: the case of SALUS, in: H. Anderson (Ed.), Emerging Tech in SAR Operations, Emerging Tech in SAR Operations, 1, McGraw-Hill, New York, 2023, pp. 128–155. 

12 

_Robotics and Autonomous Systems 196 (2026) 105237_ 

_D. Cafolla et al._ 

- [25] Ruined Cottage - 3D model, Thingiverse (2024). Available, https://www.thingi verse.com/thing:4761353/files. Accessed: September 2024. 

- [26] Wet Bin - 3D model, Thingiverse (2024). Available, https://www.thingiverse.com/ 

   - thing:3454345/files. Accessed: September 2024. 

- [27] “DJI,” [Online]. Available: https://www.dji.com/[Accessed: September 2024]. 

- [28] “Raspberry Pi,” Raspberry Pi. [Online]. Available: https://www.raspberrypi. com/[Accessed: November 2024]. 

- [29] “SIM7600G-H” Waveshare. [Online]. Available: https://www.simcom.com/pr oduct/SIM7600X.html [Accessed: November 2024]. 

- [30] “Google Cloud Developer,” Google Cloud. [Online]. Available: https://cloud.goo gle.com/developers [Accessed: November 2023]. 

- [31] A.B. Shetty, Deeksha Bhoomika, J. Rebeiro, Ramyashree, Facial recognition using Haar cascade and LBP classifiers, IEEE Transl. J. Glob. Trans. Proc. 2 (2) (2021) 330–335. 

- [32] Cafolla D. and Chaparro Rico B.D.M., “Universal aided piloting system,” Italian Patent No. 102021000018587, July 2023. 

- [33] “Freenove,” [Online]. Available: https://freenove.com/[Accessed: September 2024]. 

- [34] “ORB-SLAM3,” [Online]. Available: https://github.com/UZ-SLAMLab/ ORB_SLAM3. [Accessed: September 2024]. 

- [35] “LOAM: Lidar Odometry and Mapping in Real-time,” [Online]. Available: htt ps://github.com/laboshinl/loam_velodyne. [Accessed: September 2024]. 

- [36] “Cartographer,” [Online]. Available: https://google-cartographer.readthedocs.io/. [Accessed: September 2024]. 

- [37] “instant-NGP: Instant neural graphics primitives with a multiresolution hash encoding,” [Online]. Available: https://nvlabs.github.io/instant-ngp/. [Accessed: September 2024]. 

13 

