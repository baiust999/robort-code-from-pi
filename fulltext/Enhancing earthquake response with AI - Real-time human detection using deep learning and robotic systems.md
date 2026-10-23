Contents lists available at ScienceDirect [URL 🔗](www.sciencedirect.com/science/journal/25901230)

## Results in Engineering

[journal homepage: www.sciencedirect.com/journal/results-in-engineering](https://www.sciencedirect.com/journal/results-in-engineering)

Research paper

## Enhancing earthquake response with AI: Real-time human detection using deep learning and robotic systems☆

Anirudh Raghavan a,b [URL 🔗](#page-0)

, Yukteshwar Ramesh a,c, H Shyam a, Berlin Hency V a,* [URL 🔗](#page-0)

Malka N. Halgamuge d [URL 🔗](#page-0)

## ARTICLE INFO

Keywords: Earthquake rescue system (ERS) Earthquake debris Detect human victims Deep learning Computer vision YOLOv8 Transfer learning

real-time alerts

## ABSTRACT

This paper presents a practical AI-enabled Earthquake Rescue System (ERS), which applies a deep learning technology-based computer vision to identify the trapped human victims under the rubble caused by an earth­ quake. In the traditional rescue operation, the physical characteristics of a voice, motion, and temperature are employed to locate the trapped victims. However, the effectiveness of the rescue operation is low because the traditional characteristics are not effective in earthquake rescue scenarios. To overcome the limitations of the traditional rescue operation, this work proposes an AI-enabled rescue operation based on the application of a YOLOv8 model to identify the trapped victims under the rubble caused by an earthquake. The proposed model applies a dataset of 6837 images to fine-tune a pretrained YOLOv8 model through transfer learning. The experimental results show that the proposed model has achieved a mean average precision of 93.1%, recall of 90.5%, F1-score of 90%, precision of 98.2% in face detection, 94.6% in palm detection, and 88.7% in the detection of other body parts. The fine-tuned model is then implemented on a low-cost NVIDIA Jetson Nano, which is integrated with a mobile robotic vehicle and a camera. The system facilitates near real-time analysis and cloud-based alert transmission to aid the rescue teams in quickly locating the possible location of survivors. The results obtained demonstrate the possibility of implementing lightweight AI-assisted rescue systems to improve the efficiency of earthquake rescue operations.

injured, displaced, or made homeless because of these disasters [4]. As shown in Fig. 1 and Fig. 2 [5,6], earthquake activity remains a regular occurrence worldwide, presenting ongoing challenges to disaster pre­ paredness and response efforts. [URL 🔗](#page-0)

Among the most important issues arising after an earthquake is the identification and rescue of affected individuals trapped under the collapsed buildings and debris. Conventional search and rescue opera­ tions employ physical sensing technologies such as voice detection, motion detection, and thermal imaging to detect affected individuals [7–9]. Though these methods can be employed to assist rescue teams, they are often susceptible to range constraints, environmental noise, and high false positives in rubble environments. Visual inspection by rescue [URL 🔗](#page-0)

## 1. Introduction

Earthquakes are one of the most destructive natural disasters, which can cause severe casualties and damage to infrastructure. In India alone, more than 35,400 earthquake-related deaths have been recorded since 1950 [1]. There have been many large earthquakes in the past few de­ cades, including the 2004 Indian Ocean earthquake, which caused more than 225,000 deaths and is one of the deadliest earthquakes in history [2]. More recently, the 2023 Turkey-Syria earthquake led to at least 59, 259 deaths, emphasizing the ongoing global threat of seismic disasters [3]. In total, earthquakes contribute to a substantial number of disaster-related deaths globally, and millions of people have been [URL 🔗](#page-0)

E-mail address: berlinhency.victor@vit.ac.in (B.H. V). [URL 🔗](mailto:berlinhency.victor@vit.ac.in)

[https://doi.org/10.1016/j.rineng.2026.110608](https://doi.org/10.1016/j.rineng.2026.110608)

Received 1 September 2025; Received in revised form 21 March 2026; Accepted 17 April 2026

Available online 18 April 2026

2590-1230/© 2026 The Authors. Published by Elsevier B.V. This is an open access article under the CC BY-NC-ND license ( http://creativecommons.org/licenses/by- [URL 🔗](http://creativecommons.org/licenses/by-nc-nd/4.0/)

[nc-nd/4.0/ ).](http://creativecommons.org/licenses/by-nc-nd/4.0/)


teams is also a time-consuming and dangerous process, especially in debris fields with unstable terrain. This highlights the need for the development of automated systems that can assist rescue teams in quickly locating possible positions of affected individuals.

Recent breakthroughs in computer vision and deep learning have made it possible to develop automated detection systems that can detect objects and humans in complex visual scenes. However, most existing human detection models consider that the human body is mostly visible in the image. In earthquake debris scenarios, victims are partially hid­ den, and only small visible features such as faces, hands, or other body parts are visible through the rubble. In such cases, generic object detection models may not work well, and thus there is a need for debris- specific object detection models that can detect partially hidden human features.

In this paper, we explore a vision-based victim detection system that can be implemented on low-cost embedded systems for practical search and rescue applications. We test the performance of several YOLO-based

has

object detection models, particularly focusing on YOLOv8, which has

shown better detection accuracy and efficiency than previous YOLO models [10,11]. To make the model debris-specific, we build a debris-specific dataset with partially hidden human features that belong to four classes: face, palm, other body parts, and no human [12–14]. The YOLOv8 model is then fine-tuned using transfer learning [7,12–15] to make it more accurate in detecting highly occluded rubble. [URL 🔗](#page-0)

The trained model is then tested on a low-cost NVIDIA Jetson Nano embedded system to determine if a compact RGB-based computer vision system can offer real-time detection hints for rescuers working in disaster scenarios. Through the integration of deep learning-based detection and embedded computing, the proposed system is expected to enable quicker victim identification and better situational awareness for earthquake rescue missions.

The novelty of the proposed work is not the development of a new

the

object detection algorithm. The novelty of the proposed work is the

system-level integration of deep learning and a custom made debris- related dataset, for earthquake rescue applications. The proposed sys­ tem is different from traditional human detection methods, which

the

require the human object to be fully visible. In the proposed system, the

focus is on the detection of partially visible human features such as faces,

the

palms, and other body parts, which are expected to be visible in the

debris. In addition, the proposed system is deployed on an NVIDIA Nano-class embedded system with an IoT-based alert system.

The major contributions of the proposed work can be described as

follows:

- 1. Debris-Specific Dataset for Partial Human Detection: A specific dataset of 6837 images was created to represent the partially visible features of humans, such as the face, palm, and other body parts, which can be used to train the model to detect partially visible humans in the debris.

- 2. Transfer Learning Adaptation for the Debris Environment: A YOLOv8-s model was adapted for the debris environment for the detection of partially visible human figures based on the character­ istics of the face, palm, and other body parts.

- 3. Embedded Real-Time Deployment for the Rescue Mission: The pro­ posed model has been successfully deployed for the real-time detection of the victims in the debris using a low-cost NVIDIA Nano board embedded in the robotic platform. While a robotic platform is incorporated in the system design, its role in this study is limited to demonstrating the feasibility of deploying the trained model on a low-cost embedded device (Jetson Nano).

- 4. IoT-Based Alert System for the Rescue Mission: The proposed model has been successfully integrated for the IoT-based alert system for the rescue teams based on the real-time notification of the possible location of the victims. the

This proposed work uses the Logitech C270 digital HD camera to

the

record the live feed as the robot moves within the rubble, and the

camera is connected to the NVIDIA Jetson Nano, in which the YOLOv8 runs. When a human is identified, the human detection data is uploaded to the cloud and displayed in the mobile application. Partial human feature detection under debris and embedded deployment remain rela­ tively underexplored.

The paper is structured as follows: Section II reviews the literature on Human Detection, Deep Learning, and Transfer Learning techniques. Section III outlines the architecture of the proposed system. Section IV describes the materials and methods used, such as Data acquisition,

the

creation of dataset, and work methodology. Section V presents the

implementation and results.

## 2. Literature survey

Recent studies have attempted to examine the possibility of using

*Fig. 1. Deaths due to earthquake across India from 2010 to 2022.*


advanced technologies such as robotics, unmanned aerial vehicles (UAVs), computer vision, and Internet of Things (IoT) technology to

enhance the efficiency of the rescue process. For instance, there are

are

studies that have attempted to propose the possibility of using UAVs to detect victims using both RGB and thermal images [16]. Similarly, there are studies that have attempted to develop robotic solutions to localize victims using robots with camera sensors and deep learning algorithms [17]. Additionally, there are studies that have attempted to develop an integrated disaster response system using computer vision and cloud communication technology to enhance the efficiency of the emergency response process. [URL 🔗](#page-0)

Effectively detecting human presence in earthquake-struck envi­ ronments is a complex challenge that requires addressing various pa­ rameters. Existing methods fall into three categories: (i) sensor-based detection, (ii) CNN-based detection, and (iii) YOLO-based real-time systems. However, none address the combination of partial visibility, embedded deployment, and real-time alerting under constrained hard­ ware. Existing research has explored the use of physical characteristics, such as body parts, voice, motion, and temperature, to identify human victims [15]. Table 1 summarizes the most widely used detection pa­ rameters and their corresponding data acquisition devices. [URL 🔗](#page-0)

The literature review reveals that while various techniques, such as voice processing, thermal imaging, and motion sensors, have been explored for human detection in disaster scenarios, they often suffer from limitations like interference, limited range, and high false-positive rates. The UAV-based human search system with an array microphone for human voice detection, proposed in [7] and [8], combines voice detection and camera detection for victim identification. [URL 🔗](#page-0)

of

However, the use of a microphone has the disadvantage of a lot of

noise, and the audio quality may deteriorate as the distance increases. In [9], the proposed system utilizes a thermal sensor, camera module, and [URL 🔗](#page-0)

for

ultrasonic sensor to detect humans using thermal sensor readings for

human heat signature detection. Once the heat signature of a human is detected, the camera captures an image of the environment and trans­ mits it to a command centre for monitoring the robot's movement. The ultrasonic sensor detects obstacles in the robot's path. Nevertheless, there are several objects emitting infrared energy, making it challenging to detect human heat signatures, and the system also faces limitations in

detection range and environmental interference. The ultrasonic sensor can be used in combination with the live video feed of the camera and microwave radar, as proposed in [21]. Yet, the disadvantage of this approach is the potential for false alarms by detecting any object as a person. Therefore, the implementation of real-time object detection using deep learning is likely to be more effective than detecting humans based solely on physical parameters such as voice and motion. [URL 🔗](#page-0)

In this work, a custom RGB image-based dataset is used to detect human victims in scenarios of unstructured building collapses. Once the dataset is acquired, the features of the dataset must be learned to accurately identify the victims. Deep learning algorithms, which are primarily used in image and video analysis, can automatically identify patterns in images and categorize them accordingly. Table 2 presents the multiple DL techniques used for various applications. [URL 🔗](#page-0)

Several studies [19,22], and [28] have proposed the use of con­ volutional neural networks (CNNs) for human victim detection. In [19], various CNN variants, including ResNet-5, Inception-3, and AlexNet, were compared to machine learning models like SVM and ANN, and the CNN models demonstrated superior image classification accuracy. Similarly, [22] utilized a single-shot multibox detector (SSD) based on CNN to detect damaged structures, while [28] combined a CNN-based ResNet-5 model for feature extraction with a Random Forest decision tree classifier to identify different human body parts. However, a key limitation of these CNN-based approaches is their reliance on two separate frameworks for localization and detection, which can be time-consuming. In contrast, [7,15] and [23] have explored the use of the YOLOv3 object detection model for human detection in natural disaster environments. Furthermore, [14] compared YOLO v5 and its predecessor versions, finding that YOLO v5 was faster in terms of frames per second (FPS) in live streams. Building on this, [12] and [13] have deployed the YOLOv5 model using transfer learning for human detec­ tion in surveillance systems. [URL 🔗](#page-0)

of

Recent studies have highlighted the potential of the YOLO family of

deep learning models in improving the accuracy and speed of human identification [10,11,27]. However, the application of these advanced [URL 🔗](#page-0)

of

object detection models, particularly YOLOv8, in the specific context of

earthquake debris environments remains largely unexplored. Although various studies have been conducted on the use of deep learning

*Fig. 2. Global yearly earthquake rate from 2000 to 2023.*


*Table 1 Human detection parameters and their data acquisition devices.*

| Human detection Data acquisition Features found and their effectiveness parameter device |
| --- |
| Voice Microphone Voice processing is done to detect human words & a speech recognition model is deployed to recognize the words & relay them back to the rescue team [7,8]. Audio captured using the microphone is passed through an audio detection architecture to detect human voices [15]. A keyword spotting system is implemented to localize any audible survivor [18]. Drawback of using a microphone is that it is prone to a lot of interference and as distance increases, it may not be able to capture the audio. Image/Video Camera Camera attached with UAV for detecting humans on the ground [7]. An IP camera mounted on the mobile robot will provide the command centre with an online vision of the real condition at the disaster site [9]. Using RGB images, human detection algorithms can detect humans in applications like surveillance systems [12]. Live camera feed will observe indoor spaces and detect a group of people [14]. A human detection architecture breaks down the video feed into small frames and analyses them for the presence of any human [16]. Life victim/survivor localization [18]. Images from the damaged areas are collected and are classified whether survivors are present or not [19]. Camera for live streaming and to detect a person stuck under debris of the disaster [20]. ESP camera module used to provide live streaming for the persons monitoring the disaster area. A limitation of this is that ESP camera has only 2MP and does not provide clear feed of the visuals [21]. Aerial imagery for detecting the building damages using single shot multibox detector [22]. Images from raspberry pi camera used to classify the disaster and detect victims [23]. Thermal camera Used for live streaming and detecting human heat signatures thereby detecting humans. Disadvantage of this camera is that it is more expensive than normal visible light cameras [13]. Motion PIR PIR sensors are used to detect the presence of humans at various locations, including beneath debris caused by natural disasters [24]. There are high chances of false alarms due to factors like variable surrounding heat and sunlight intensity. Ultrasonic Detects any obstacle ahead of the robot and notifies the robot [9]. It is primarily utilized for navigation, identifying obstacles along its path. When an obstacle is detected, it sends a notification to the controlling device [21]. Challenges like limited range for detection, and environmental interferences can be faced. Radar It identifies human presence within its operational range by detecting |

Table 1 (continued )

| Human detection Data acquisition Features found and their effectiveness parameter device |
| --- |
| movement in objects beneath the soil [21]. Utilizes Doppler Radar to detect human presence in various locations, including beneath debris caused by natural disasters [24]. A limitation of this would be potential false alarms by detecting any other object as a human. UWB Uses UWB impulse Cayenne radar to locate unseen survivors trapped within building debris [18]. Ultra-wideband radar for human vital sign detection [25]. UWB radar offers high spatial resolution with ultrashort pulses and can detect vital signs like breathing, heartbeat, and body movements [26]. Limited range and chances of interference with other devices in the same frequency range are the challenges. RFID To gather all victim and survivor tags within the sensor's maximum radius [18]. Heat signature Thermal sensor Infrared energy is monitored for detecting humans [9]. This method has a flaw as a large number of objects would be emitting infrared energy making it difficult for detecting human heat signatures. Environmental Temperature To detect the surrounding temperature conditions sensor [15]. CO sensor To monitor the concentration of Carbon monoxide in the surroundings [15]. |

techniques for human detection in surveillance and earthquake sce­ narios, most of the techniques presented so far focus on detecting completely visible human bodies. However, during an earthquake, the victims' bodies may be partially occluded by debris, with only small visible parts of the human body, such as the face or hands, being visible. Additionally, most of the techniques presented so far have been designed for high-performance computing platforms, which may not be suitable for use on embedded platforms. Thus, the need arises for a lightweight system that can be used for detecting victims during earthquakes. This paper proposes a customized version of the YOLOv8 algorithm for detecting human victims during earthquakes. The algorithm will be deployed on an embedded platform running on a Jetson Nano.

In summary, the key conclusions drawn from the literature review

are:

(i) Multiple studies have employed RGB images for detecting victims.

(ii) YOLO object detection models have demonstrated relative

effectiveness in terms of computational speed and time compared to

CNN-based models.

(iii) The YOLOv8 model has shown an edge over other YOLO variants

in terms of frames per second (FPS) and accuracy.

## 3. Architecture

The proposed architecture of the ERS (as shown in Fig. 3) aims to locate earthquake victims trapped under debris by combining a deep learning model with a NVIDIA Jetson Nano board. At the core of this system is the YOLOv8 model, a pre-trained object detection network specialized in identifying human features even in challenging environ­ ments. To enhance its accuracy in debris scenarios, the model is further trained on a custom dataset encompassing "face," "palm," "other body parts," and "no human" categories. " By tailoring the dataset to the spe­ cific conditions encountered in earthquake aftermath, the YOLOv8 [URL 🔗](#page-0)


Table 2 Various Model based approaches used for surveillance & detection of objects/ humans.

Table 2 (continued )

Model Type Model Name Input

Features/ Purpose

Type

Transfer

YOLOv3

RGB image

Dataset source

Model Type Model Name Input

Features/ Purpose

Dataset source

Type

preserve feature information, an improved feature fusion method, and a new network structure called DC module

A real time object detection model is used to detect humans using the YOLOv3 model. But these previous YOLO versions have been found to use a single framework for localisation and detection but tend to have a lower accuracy and slower inference speed. Smart fire detection

MS COCO

learning (2020) [7] [URL 🔗](#page-0)

Transfer

YOLOv5

Thermal A real-time and RGB aerial

MS COCO

learning (2022) [12] [URL 🔗](#page-0)

image

surveillance system was deployed using the YOLOv5 model.

Transfer

YOLOv5

Thermal The YOLOv5

ASL-TID

learning (2023) [13] [URL 🔗](#page-0)

Image

model is trained (Autonomous

on a custom dataset to enable real- time human detection for surveillance purposes. Pre trained YOLO versions were compared for real time human detection. YOLOv3 was implemented for detecting human victims in environments affected by natural disasters. CNN variants

System Lab Thermal Infrared Dataset), OSU

Deep

YOLOv8

RGB

Manually prepared

Learning (2023) [10] [URL 🔗](#page-0)

system based on dataset

the YOLOv8 deep learning

comprising of non-fire and

Deep

YOLOv3, YOLOv4, YOLOv5, YOLOv3-Tiny, YOLOv4-Tiny

RGB

MS COCO

learning, Transfer learning (2023) [14] Transfer [URL 🔗](#page-0)

algorithm with fire videos and

4 layers: application, IoT, fog, and

images are used for training and

cloud & focuses testing on applications like smart government, traffic, hospitals, & homes

YOLOv3

RGB

MS COCO

learning (2022) [15] [URL 🔗](#page-0)

Deep

YOLOv8 Res2Net & C2f modules

RGB

Improvements

Publicly

Learning (2023) [11] [URL 🔗](#page-0)

to the YOLOv8 available object detection student model to better classroom

Deep

CNN, ResNet- RGB 50, Inception- V3, AlexNet, SVM, ANN

Hybrid

learning, Machine learning, and Transfer learning (2020) [19] [URL 🔗](#page-0)

were compared (collected from

detect student behaviours in the classroom. Introduces a C2f_Res2block module combining the Res2Net & C2f modules. It also includes an efficient multi- scale attention (EMA) module & multi-headed self-attention (MHSA) mechanism to the backbone network. Small-size

behaviour dataset (SCB Dataset)

with ML methods for detecting humans in an earthquake scenario. However, the CNN uses 2 frameworks for localisation and detection making it a time- consuming process. Single Shot Multibox Detector for Building damage detection in post-disaster aerial imagery. Multi-Task

multiple sources)

Deep

Single Shot Multibox Detector

RGB

Drexel University and NOAA (USA agency)

Learning (2019) [22] [URL 🔗](#page-0)

Deep

YOLOv8

RGB

Visdrone

Learning (2023) [27] [URL 🔗](#page-0)

object detection dataset

algorithm called DC-

Pascal VOC2007 &

YOLOv8 based Tinyperson

Deep

MobileNetv2, RGB YOLOv3

Hybrid

on a camera sensor. Improvements of DC-YOLOv8 include a modified down sampling method called MDC to better

datasets

Learning, Machine Learning (2022) [23] [URL 🔗](#page-0)

Learning model (collected from

using MobileNetv2 for real-time disaster classification, and YOLOv3 for object detection.

multiple sources)

(continued on next page)


*Table 2 (continued )*

| Model Type Model Name Input Features/ Dataset source Type Purpose |
| --- |
| Deep ResNet-50, RGB Combining Hybrid Learning, CNN, deep learning (collected from Machine Random features with multiple Learning, Forest decision trees to © sources) Transfer Decision tree identify disaster Learning classification victims under (2023) debris, using a N [28] pre-trained model for for feature extraction, and Random Forest classification. Deep Faster R-CNN RGB Human Thermal UAV Learning detection in in dataset [29] aerial SAR imagery Transformer- VE-DINO RBG Transformer- Custom based deep based object disaster learning detection imagery [30] model designed dataset to improve detection of of partially occluded humans in in complex disaster environments using visibility- enhanced feature learning. |

in for

model can more effectively identify even small human signatures in

hard-to-reach areas, giving it a distinct advantage in the search for

survivors. The robotic platform is equipped with a Logitech C270 digital HD camera, which captures the live video feed within the rubble. This

the

camera is connected to the NVIDIA Jetson Nano board, which runs the

YOLOv8 model. Upon detecting a human victim, the YOLOv8 model triggers the transmission of the detection data to the cloud, where it is stored in a Firebase real-time database.

The data, which includes information about the detected class ('face', 'palm', 'other-body-parts') along with the date and time of detection, is

the

then accessed by a custom-built mobile application. This allows the

rescue team to receive real-time alerts, expediting their response and

the

simplifying decision-making, potentially saving lives. The use of the

NVIDIA Jetson Nano board is advantageous due to its small size, low power consumption, and ability to run multiple neural networks and algorithms, making it an efficient single board computer for this appli­ cation. The Logitech C270 camera was selected for its high resolution

(1280

720) and 30 fps video capture capabilities, ensuring reliable

x

the

data acquisition for the deep learning model. The specifications of the

in

Logitech C270 digital HD camera are detailed in

[Table 3.](#page-0)

## 4. Materials and methods

This research aims to detect human victims in an earthquake- affected environment where individuals may be trapped under debris. The study aims to validate the presence of human victims by identifying any visible body parts.

## 4.1. Dataset creation and preprocessing

Data sources and licensing: We curated a set of publicly available images depicting earthquake-like debris with partially visible human features for research-only model development; we do not redistribute these images. To expand coverage of poses, occlusions, lighting condi­ tions, and camera angles, we generated additional synthetic images and performed data augmentation (e.g., rotations, flips, blur, and intensity jitter). The final dataset comprises 6837 images across four classes:

{face, palm, other-body-parts, no-human}. Images were resized to 416

416 and split into train/val/test

=

limited and may not fully reflect generalization. Future work will adopt larger independent test sets and cross-validation. We (i) used transfer learning from general-domain pretraining, and (ii) report class-wise metrics. Fig. 4 summarises the end-to-end data pipeline. [URL 🔗](#page-0)

The images were classified under four data classes: face, no-human,

x is

[87/12/1] %. The test split (1%) is

*3*

*Table 3*

*Specifications of the camera used.*

| Camera Specification |
| --- |
| Camera resolution 3-megapixel (1280 720) Pixel size 2.8 µm x 2.8 µm Video recording 30 fps at 720p HD |

*Fig. 3. Architecture of the earthquake rescue system.*


palm, other-body-parts. Then each of the images in these classes un­ derwent pre-processing as shown in Fig. 5, including augmentation based on lighting conditions, rotations and flip-overs of the robot and intensity variations of the camera module and environmental conditions [URL 🔗](#page-0)

to form the final multiclass (4 classes) dataset with 6837 images as

as

represented in Table 4. Finally, the images were resized to 416 416 to [URL 🔗](#page-0)

We

meet the input requirement of the pre-trained YOLOv8 model. We

selected 416 416 as the input resolution to balance detection accuracy with the computational limitations of the Jetson Nano, where lower resolution provided faster inference speed and stable real-time perfor­ mance. The above-mentioned augmentation steps would help the model train for various conditions and positions in which the human victim would be trapped.

## 4.2. YOLOv8 pre-trained model for human detection

The YOLO (You Only Look Once) family of deep learning models are known for their efficient and real-time object detection capabilities. They achieve this through a unified network that predicts both object class and localization in a single pass through an image, unlike earlier methods that tackled them separately. This results in faster processing and higher efficiency. YOLO models come in different versions, each offering a trade-off between speed and accuracy. They are often pre- trained on large datasets, allowing them to tackle various object detection tasks. Additionally, they can be fine-tuned on custom data to improve detection of specific objects, making them a popular choice for diverse applications. YOLOv8 (You Only Look Once, version 8) is a powerful model for object detection, particularly excelling in human detection. The PyTorch framework used by this model results in a clean and well-structured codebase, which simplifies model training, infer­ ence, and deployment compared to the C-based Darknet framework used in previous YOLO versions. This makes YOLOv8 more accessible for a broader range of developers. There are 5 model variants (n, s, m, l, and x) offering a wide range of trade-offs between speed and accuracy. The

smaller models (n, s, and m) can achieve high frame rates on CPUs or

or

low-power devices, making them ideal for applications like mobile ob­ ject detection. The larger models (l and x) boast impressive mean Average Precision (mAP) scores on benchmark datasets, making them suitable for tasks requiring high detection precision. Additionally, YOLOv8 excels at transfer learning, allowing users to fine-tune a pre- trained model on their custom dataset containing specific objects of interest, such as humans in particular poses or activities, to tailor the model to their specific needs. Fig. 6 presents a detailed illustration of the YOLOv8 architecture [31], providing a comprehensive view of its so­ phisticated design and enhancing understanding of its capabilities in our specific application of human detection in disaster scenarios. This detailed figure provides a comprehensive visual representation of the model's architecture, highlighting key components such as the con­ volutional layers, feature extraction mechanisms, and output structures. [URL 🔗](#page-0)

The architecture consists of several key components:

- Backbone: The backbone network, composed of multiple con­ volutional layers, is responsible for feature extraction from the input data. It gradually decreases spatial dimensions while enhancing the depth of the feature maps. the

- Head: The head of the YOLOv8 model, which includes components like up sample layers, concatenation operations, and detection heads, integrates features from different scales to enhance detection performance.

- Details Panel: This section provides a granular view of the internal operations, including bottlenecks, CSP (Cross Stage Partial) layers, and SPPF (Spatial Pyramid Pooling - Fast) layers, which contribute to efficient feature aggregation and improved model accuracy.

- bounding boxes, object classes, and confidence scores, enabling the model to detect human features accurately in various scenarios. Output Structures: The output layers are designed to predict the

The YOLOv8-s variant was trained on the custom dataset using transfer learning. In comparison with its previous models, the YOLOv8 variant has higher accuracy with minimal training in terms of the epochs

*Fig. 4. Data acquisition and pre-processing.*


Data pre-processing

*Original Image*

*Augmented Images*

*Fig. 5. Data augmentation.*

*Table 4 Prepared dataset.*

| Type / No. of images taken Source of data |
| --- |
| Real world images from google 215 Synthetic images from Gretel.AI through prompts 865 Augmented data (using Roboflow and Albumentations) 5757 Final dataset 6837 |

required to train the model. Among the YOLOv8 family the YOLOv8-s variant utilises the least amount of computational time compared to higher variants of YOLOv8 family while having a high accuracy and precision rate.

## 4.3. Transfer learning

The YOLOv8 object detection model was trained with transfer

learning to modify a pretrained model for the earthquake debris detection task. The pretrained YOLOv8-s model, which was pretrained on the COCO dataset, was utilized as the initial model for training. Although the COCO dataset provides a generic person class, it does not consider the partially observable human attributes like faces or hands that could be visible in the debris environment. Thus, transfer learning was employed to fine-tune the pretrained model with the custom debris dataset created in this research. Fig. 7 shows the transfer learning pro­ cess followed. The dataset was downloaded from Roboflow in YOLO format and utilized to train the model with the Ultralytics YOLOv8 training script. The dataset provides four classes for object detection: face, palm, other-body-parts, and no-human. When training the model, [URL 🔗](#page-0)

the

the pretrained weights of the YOLOv8-s model were utilized as the

initialization, which enabled the network to maintain the general visual feature representations learned from the large-scale COCO dataset while modifying the model to suit the debris task. In the training process, the pre-trained weights helped the network preserve low-level features like edges and textures, and the subsequent layers were fine-tuned to detect

*Fig. 6. The architecture of YOLOv8.*


*Fig. 7. Transfer learning process of YOLOv8 with custom dataset.*

debris-specific patterns and partially visible human features in the custom dataset. This approach of transfer learning helps the model perform well in detection even with a small size of the custom dataset.

To enhance the reproducibility of the proposed approach, the training parameters employed for the YOLOv8 model are presented in Table 5. The parameters were chosen according to the computational requirements of the Jetson Nano deployment platform and the debris dataset. [URL 🔗](#page-0)

## 4.4. Hardware materials

The hardware components of the system include the NVIDIA Jetson Nano board, which acts as the central processing unit, and the Logitech C270 digital HD camera with a resolution of 1280 720 pixels and a frame rate of 30 fps. The Jetson Nano board was integrated with a 4- wheeled robotic vehicle equipped with side shaft motors and motor drivers, providing the necessary mobility and control for the search and rescue operations. The side shaft motors used had a shaft diameter of 6 mm, producing an effective 300 RPM at 12 V and 10 Kg-cm of torque, and ran smoothly from 12 V to 18 V voltage range, providing a wide range of RPM and torque. The L298N motor drivers used offered a voltage range of 5 V - 35 V, consumed 2A of current, and had a maximum power consumption of 25 W. Fig. 8 shows the ERS robot. [URL 🔗](#page-0)

## 4.5. Operational conditions and boundary assumptions

The performance results achieved in the research have been obtained based on specific operational assumptions related to the constructed dataset. The system assumes the availability of partially visible human features in the debris environment captured through the RGB imagery. The evaluation conditions can be described as follows:

*Table 5 YOLOv8 configuration parameters.*

| Parameter Value Justification |
| --- |
| Model YOLOv8-s Selected for its balance between detection architecture accuracy and computational efficiency for embedded deployment. Input image 416 416 Provides a trade-off between detection size accuracy and inference speed on embedded hardware. Batch size 16 Ensures stable gradient updates while remaining within GPU memory limits during training in Google Colab. Optimizer AdamW Provides efficient convergence during transfer learning and improves generalization. Initial learning 0.00125 (auto- Automatically determined by the Ultralytics rate selected) training pipeline to optimize convergence. Weight decay 0.0005 Regularization parameter used to reduce overfitting. Number of 40 Empirically sufficient for convergence given epochs the dataset size (6837 images). IoU threshold 0.5 Used for evaluating object detection performance (mAP@0.5). Confidence 0.25 Ensures that only reliable detections are threshold considered for alert generation. |

- 1. Lighting Conditions: The dataset includes various images collected from different online sources and generated through various methods with different lighting conditions. However, extreme low light, high dust, or smoke may affect the performance of the detec­ tion system.

- 2. Occlusion Levels: The dataset includes various images where the level of occlusion of the human features such as faces, palms, and other body parts is partially visible in the debris environment. However, the detection performance may decrease if the level of occlusion is high or the visible area is extremely low.

- 3. Image Sources: The training dataset has been constructed based on a combination of various images collected from the internet and various scenes generated through various methods to simulate the earthquake debris environment. However, the scenarios and situa­ tions may vary in the real environment.

- 4. Debris Complexity: The dataset includes various images representing a moderate level of debris complexity with cluttered backgrounds such as rubble, broken objects, and other debris.

These boundary conditions establish the environment in which the values of mAP and recall performance were measured. Real-world ap­ plications may pose other difficulties that would make it necessary to expand the dataset and evaluation of the system.

## 4.6. Software tools

Gretel.AI was used to create synthetic images for the dataset. Roboflow was used to separate the images into different classes and label them. Roboflow, along with the Python library Albumentations, was used for data pre-processing, which included various augmentations such as intensity variation, blurring, horizontal flip, vertical flip, rota­ tion, and resizing.

The YOLOv8 model was trained in a Google Colab environment using Python 3.9 on the custom dataset prepared. The detection results were sent to the Firebase real-time database. MIT App Inventor was used to create a mobile application with a login page, live detections, and a history of previous detections, which were extracted from the Google Firebase real-time database.

## 5. Implementation and results

## 5.1. Evaluation protocol

We report mAP@0.5 (mAP50), precision, recall, and F1 on a held-out test set. We use IoU threshold 0.5, NMS IoU 0.7, and confidence threshold 0.25. We ablate thresholds in the supplement. The proposed model was trained and validated in Google Colab environment and the trained model was implemented on a Jetson Nano. The YOLOv8 model was trained on the custom dataset and achieved an overall mean average precision (mAP) of 93.1% and a recall of 90.5%. Specifically, the model performed with a precision of 98.2%, 94.6%, and 88.7% for the 'Face', 'Palm', and 'Other body parts' classes, respectively. Table 6 represents the mean average precision (mAP), recall, F1 scores and precision values of the overall dataset as well as class wise data. [URL 🔗](#page-0)


*Fig. 8. ERS Robot.*

## 5.2. Analysis of “no human” class performance

Although the proposed model performs well on overall accuracy (mAP 93.1% and recall 90.5%), the “No Human” class has relatively poor detection performance compared to the human-feature classes. As indicated in Table 6, the “No Human” class has precision of 75.3%, recall of 79.1%, mAP of 84.3%, and F1 score of 77.1%, which are lower compared to the Face, Palm, and Other Body Parts classes. [URL 🔗](#page-0)

Several factors may contribute to this performance difference:

- 1. Class imbalance in the dataset: The dataset is mainly concerned with the detection of human-feature information like faces, palms, and body parts in the debris environment. Consequently, the amount of data for the “No Human” background class is relatively small, which may affect the model’s ability to be trained on a wide range of negative examples. This may cause the model to have a high number of false positives when complex debris patterns are like human features.

- 2. Visual similarity between debris textures and human features: Debris environment in earthquake situations could have irregular textures such as crushed concrete, twisted metal, and broken material, which could have some resemblance to human skin tones or clothing patterns.

- 3. Ambiguity in negative samples: The “No Human” images could still contain objects or shapes that could resemble human features, especially in the cluttered rubble environment. This would make it even more difficult for the model to learn the differences between human and non-human visual patterns.

Potential mitigation strategies: Future work could aim to solve these problems in several ways. There could be an increase in the number and variety of background images in the “No Human” category, which would help the model distinguish between debris and human features. Hard negative mining could also be employed to train the model on difficult negative examples. Finally, the addition of other sensing modalities,

*Table 6 The validation results of the proposed method.*

| Classes Precision (%) Recall (%) mAP (%) F1 Score (%) |
| --- |
| Face 98.2 98.5 98.6 98.3 Palm 94.6 95.9 96.9 95.3 Other Body Parts 88.7 88.6 92.6 88.6 No Human 75.3 79.1 84.3 77.1 All 89.2 90.5 93.1 90 |

such as thermal or depth cameras, could help to eliminate visual am­ biguities in the disaster environment.

## 5.3. Runtime and complexity on Jetson Nano

Time efficiency is a critical parameter in earthquake search and rescue operations, where rapid victim identification can significantly improve the survival rate. To evaluate the viability of the proposed system, the YOLOv8-s model (with roughly 11.1 M parameters) was developed on an NVIDIA Jetson Nano (4 GB) embedded system, accompanied by a Logitech C270 RGB camera operating at 720p. The entire processing pipeline, from image acquisition to alert generation, was performed on the Jetson Nano board. The experimental results show that the system takes about 80–140 ms per frame for end-to-end pro­ cessing, which corresponds to 7–12 FPS. This enables the robotic system to scan the surrounding environment continuously as it moves through the debris to identify possible victims in near real-time. In addition to local victim detection, the system transmits the result of the detection to a cloud-hosted Firebase database for remote monitoring of the system through a mobile app. The updates are sent approximately once every second, while the mobile application checks for updates every five seconds. This enables the rescue team to be alerted on time regarding the possible location of the survivors. The memory required by the deployed model on the Jetson Nano is approximately 22 MB, which indicates that the system can run efficiently under the computational constraints of low-power embedded systems. The above experiments have confirmed that it is feasible to use light deep learning models for quick victim identification and quick decision-making.

## 5.4. Model result comparison

Table 7 compares the validation results of general pre-trained YOLO models (YOLOv8, YOLOv9, YOLOv11, and YOLOv12) applied directly to our labelled test set, with no fine-tuning, against the proposed transfer learning-based YOLOv8 model trained on our custom dataset. The pre- trained models achieved poor performance, with mAP50 scores be­ tween 17.0% and 18.6%, since they were trained on broad datasets and are not suited for disaster-specific conditions where only partial human features are visible under debris. This comparison is not intended as a [URL 🔗](#page-0)

of of

direct benchmark but as a sanity check to highlight the importance of

fine-tuning. In contrast, our fine-tuned YOLOv8 achieved an mAP50 of

93.1%, along with high precision and recall, demonstrating that domain adaptation is essential for reliable victim detection in earthquake scenarios.


## Table 7

Validation results highlighting the underperformance of general pre-trained YOLO models and the necessity of fine-tuning for disaster-specific conditions.

| Model type Precision (%) Recall mAP F1 Score (%) (%) (%) |
| --- |
| YOLOv8 27.2 29.9 17.8 28.5 YOLOv9 26.6 29.3 17.0 27.9 YOLOv11 29.0 26.8 17.3 27.9 YOLOv12 28.7 28.5 18.6 28.6 Transfer learning approach 89.2 90.5 93.1 89.8 |

A comparison is made in Table 8 with pre-trained object detection models. The proposed model designed to detect humans inside an earthquake debris environment is compared with other human detection models for various natural disasters. The comparative analysis table shows that the proposed YOLOv8 model for victim detection under earthquake environment has a higher mean average precision (mAP) of 93.1% when compared to the other human victim detection models. The model was deployed on the Jetson Nano, and test images were fed to the model to assess its performance. Figs. 9a and 9b show the results of the model on the test images. [URL 🔗](#page-0)

To ensure fairness, we report two views: (A) Prior-reported precision from related work (not directly comparable across datasets), and (B) Our re-evaluation of YOLOv8 on our test set under the stated protocol (precision, recall, mAP@0.5 (mAP50), F1). This separates literature numbers from our task-specific results.

The trained YOLOv8 model was deployed on the NVIDIA Jetson Nano board, which was integrated with the Logitech C270 digital HD camera and the 4-wheeled robotic vehicle. The live video feed captured from within the simulated earthquake debris environment is shows in Fig. 9c. [URL 🔗](#page-0)

When the YOLOv8 model detects a human, the data is sent to the Firebase real-time database. The 'No human' class serves to minimize false-positive detections, and the output of this class was not sent to the database. A collection named "IoT" was created with sub-collections corresponding to the different classes: "face", "other-body-parts", and "palm". This collection stores the exact time and date of the last five detection histories for each class, with "Detection 1″ being the most recent. Another collection, "user", consists of the saved username and password required for the app login, as shown in Figs. 10a and Fig. 10b. [URL 🔗](#page-0)

In the app created using MIT App Inventor [34], authorized users can log in and choose to view either the live detection information or the detection history. Every five seconds, the real-time data is fetched from the database and updated in the app, as shown in Fig.s 11a and Fig. 11b [URL 🔗](#page-0)

The trained YOLOv8 model was deployed on the NVIDIA Jetson

## Table 8

Comparison of detection models. Panel A prior-reported results (not directly comparable). Panel B our YOLOv8 results on our test set (precision/recall/ mAP50/F1).

| Algorithm Application Avg. Precision/ References |
| --- |
| YOLOv3 Real-time survivor detection 70.1% [15] (Search & rescue) ResNet-50 [CNN] Post disaster decision system 90.8% [19] Inception-V3 [CNN] Post disaster decision system 87.2% [19] AlexNet [CNN] Post disaster decision system 79.6% [19] YOLOv4 Human detection on drone images 60% [32] (Search & rescue) YOLOv5 Human detection from drone (Search & 59.1% [33] rescue) Faster R-CNN (ResNet- Human detection in aerial thermal 55.7% [29] 50) images for search-and-rescue scenarios VE-DINO (Transformer- Detection of occluded humans in 61.5% [30] based detector) disaster environments YOLOv8 (proposed Human detection under earthquake 93.1% model) debris environment |

Nano board, which was integrated with the Logitech C270 digital HD camera and the 4-wheeled robotic vehicle. During testing, the system was able to successfully detect human features in the live video feed captured from within the simulated earthquake debris environment.

Upon detection, the relevant data, including the detected class and timestamp, was transmitted to the cloud-based Firebase real-time database, which was then displayed in the custom-built mobile appli­ cation[35]. This allowed the rescue team to receive real-time alerts and efficiently coordinate the search and rescue efforts. [URL 🔗](#page-0)

## 6. Discussion

This study developed a robotic search and rescue system that le­ verages the YOLOv8 deep learning model to rapidly detect the presence of human victims in earthquake-struck environments. The key meth­ odological contribution was the creation of a custom dataset and the application of transfer learning to fine-tune the YOLOv8 model for improved accuracy in identifying human features, such as faces, palms, and other body parts, within the debris.

The system achieved impressive performance metrics, including a mean average precision (mAP) of 93.1%, a recall of 90.5%, and an F-1 score of 90% in detecting human victims. These results demonstrate the potential of deep learning-based object detection techniques, particu­ larly the YOLOv8 model, to enhance search and rescue operations in the aftermath of earthquakes. By automating the detection process and providing real-time alerts, the system can expedite decision-making and increase the chances of survival for trapped victims [36–38]. [URL 🔗](#page-0)

The primary strength of this study lies in the integration of advanced computer vision and deep learning technologies within a robotic plat­ form, enabling rapid and accurate identification of human victims in challenging debris environments. The customized dataset and the application of transfer learning contributed to the model's superior performance compared to its predecessors. However, the system's reli­ ance on a single visual sensor and the lack of autonomous navigation capabilities may limit its adaptability to more complex and dynamic disaster scenarios.

To further improve the robustness and versatility of the system, future research should explore the incorporation of additional sensor modalities, such as thermal imaging and motion detection, to enhance victim detection capabilities. Developing autonomous navigation algo­ rithms and ensuring interoperability with existing search and rescue frameworks could also enhance the system's practical deployment and integration with emergency response operations. Additionally, expanding the dataset to include a broader range of environmental conditions and conducting field trials in real-world earthquake-affected areas would provide valuable insights into the system's performance and operational challenges.

The integration of YOLOv8-based deep learning and IoT technologies within a robotic search and rescue system demonstrates the potential to revolutionize post-earthquake disaster response efforts. By automating the detection of human victims and providing real-time alerts, this innovative approach can streamline decision-making, reduce risks to human rescuers, and ultimately increase the chances of survival for those trapped under earthquake debris.

Limitation of this Study:

1. Dataset Representativeness: The dataset, which is proposed to represent the partially visible human features under the debris, consists of a combination of curated images. The images may not represent the real-world variations of the disaster. There are various factors like dust, smoke, wet surfaces, shiny objects, and lighting, which may affect the performance of the system. Hence, the mAP of 93.1% is obtained under similar conditions to the test dataset. The performance of the system may be improved by incorporating images of real-world disaster environments.


*Fig. 9a. The results of the model on test images.*

*Fig. 9b. The results of the model on test images.*

- 2. Limited Sensor Modalities: The current system utilizes a single RGB camera (Logitech C270) for the visual perception of the disaster. RGB images may not perform well under poor lighting or visually complex environments. The performance of the system may be improved by incorporating other sensing modalities like thermal camera, depth sensor, or motion sensor. be

- victims remaining undetected by the system. In the search and rescue environments, the system may miss the victims, who may remain trapped. 3. Risk of False Negatives in Victim Detection: The system achieved a recall of 90.5%. This means there is a possibility of one out of ten ten

- 4. Lack of Autonomous Navigation: The robotic platform employed in the research must be manually controlled to move through a debris field. Hence, the system is more suited to act as an assisting

perception tool instead of a completely autonomous rescue robot. The addition of autonomous navigation methods such as SLAM- based exploration would help the system to efficiently search through a wide area of a disaster scenario.

- 5. Hardware Durability and Mobility Constraints: The hardware used in the proposed system, such as the Jetson Nano board and the Logitech C270 camera, may not be suitable to operate in a harsh debris field. In the real-world system, the hardware should be more robust to operate in a harsh debris field. The hardware should be able to withstand dust, among other debris. The hardware should also be able to withstand impact. The locomotion mechanism should also be more robust to operate in the debris field. The mechanism should be a tracked mechanism. be be


*Fig. 9c. The results of the model from live capturing.*

*Fig. 10a. Firebase Real-time dataset.*

*Fig. 10b. Firebase Real-time dataset.*


*Fig. 11a. MIT app interface.*

*Fig. 11b. MIT app interface.*

6. Limited Real-World Validation: The performance evaluation of the YOLOv8 model is primarily based on the custom dataset and

simulated environments. Conducting field trials or case studies in real-world earthquake-affected areas could provide valuable insights


into the system's practical efficacy and identify any additional challenges that may arise during deployment.

By addressing these limitations, the researchers can strengthen the overall research methodology and enhance the potential impact of the proposed robotic search and rescue system for human victim detection in earthquake debris environments.

Reproducibility and data availability:

The custom dataset, model training code, and trained model weights are available upon request. Experiments were performed on a Jetson Nano (JetPack 4.6) and in Colab (Python 3.9) using Ultralytics YOLOv8- s, with key libraries including torch 2.x, opencv-python, numpy, and firebase-admin.

## 7. Conclusion and future scope

This paper presents an Earthquake Rescue System (ERS) that is founded on deep learning and computer vision, a YOLOv8 model that is fine-tuned to detect partially buried human victims under debris. By specifically aiming to identify isolated human features like the face, palm, and other body parts, the model was able to achieve high per­ formance scores, including a mean average precision (mAP50) of 93.1%, a recall rate of 90.5%, and an F1 score of 90%, despite deteriorated visual conditions. Our efforts span from building an augmented, realistic dataset to real-time detector deployment in a mobile robotic platform. The experimental setup using a Jetson Nano and Logitech C270 camera demonstrates the feasibility of deploying AI-based victim detection in real-world rescue operations.

Aside from its technical achievement, this study also has several broader implications:

- 1. It verifies the effectiveness of transfer learning on a custom dataset tailored to disaster situations.

- 2. It explains the potential of using low-cost, lightweight hardware with current deep learning frameworks to produce deployable and affordable search and rescue technology.

- 3. It lays the foundation for AI-assisted rescue systems, reducing danger to human personnel and response time.

However, several limitations were found. The current system relies on one camera sensor and lacks autonomous navigation, an aspect that may affect its adaptability in highly unstructured or cluttered settings. Testing also occurred within a controlled setting using artificially generated earthquake images, which, although useful for purposes of validation, do not best represent the uncertainty of real disaster areas.

To make the ERS more robust and deployable, the future agenda

should focus on:

- 1. Multi-modal sensor fusion: Adding thermal cameras, LiDAR, or microphones to identify victims in low visibility or noisy environments.

- 2. Autonomous navigation: Equipping the system with SLAM- based or deep reinforcement learning-based mobility to navigate autonomously without human input.

- 3. Field testing in real environments: Collaborating with emer­ gency services or rescue simulations to conduct field testing under real post-disaster conditions. This includes building a more robust platform to move through a debris-field and conducting a compre­ hensive evaluation of the robotic platform including aspects such as mobility, terrain adaptability, load capacity, and robustness in complex debris environments

- 4. Scalability: Researching deployment via aerial vehicles (UAVs) or swarm robots to cover larger search areas in a shorter period of time.

- 5. Interoperability: Building the system to be compatible with existing emergency communication standards and rescue facilities.

In conclusion, this study proves that customized deep learning models combined with low-cost hardware and real-time processing can immensely boost post-disaster earthquake rescue operations. Over­ coming some of the major limitations and broadening the abilities of the system, this methodology has the potential to turn into a critical device for emergency response agencies globally. Additionally, this provides new opportunities for inter-disciplinary collaborations between disaster management, robotics, and artificial intelligence, ultimately leading to safer, faster, and smarter rescue operations.

## CRediT authorship contribution statement

Anirudh Raghavan: Writing – review & editing, Writing – original draft, Visualization, Validation, Software, Resources, Methodology, Investigation, Formal analysis, Data curation, Conceptualization. Yuk­ teshwar Ramesh: Writing – review & editing, Writing – original draft, Visualization, Validation, Software, Resources, Methodology, Investi­ gation, Formal analysis, Data curation, Conceptualization. H Shyam:

Writing

Validation, Software, Resources, Methodology, Investigation, Formal analysis, Data curation, Conceptualization. Berlin Hency V: Supervi­

sion, Project administration, Funding acquisition.

uge:

–

review & editing, Writing – original draft, Visualization,

Malka N. Halgam­

Writing

–

review

&

editing, Supervision.

## Declaration of competing interest

The authors declare the following financial interests/personal re­ lationships which may be considered as potential competing interests: BERLIN HENCY V reports financial support was provided by Tamil Nadu State Council for Science and Technology. If there are other au­ thors, they declare that they have no known competing financial in­ terests or personal relationships that could have appeared to influence the work reported in this paper.

## Data availability

Data will be made available on request.

## References

- [[1] https://www.worlddata.info/asia/india/earthquakes.php.](https://www.worlddata.info/asia/india/earthquakes.php)

- [[2] https://www.britannica.com/event/Indian-Ocean-tsunami-of-2004.](https://www.britannica.com/event/Indian-Ocean-tsunami-of-2004)

- [[3] https://www.india.com/news/world/year-ender-2023-major-earthquakes-th at-shook-the-world-in-2023-6591272/.](https://www.india.com/news/world/year-ender-2023-major-earthquakes-that-shook-the-world-in-2023-6591272/)

- [[4] https://www.statista.com/statistics/268029/natural-disasters-by-death -toll-since-1980/#:~:text=The%20Haiti%20earthquake,1980%20and%202022% 2C%20and%20the.](https://www.statista.com/statistics/268029/natural-disasters-by-death-toll-since-1980/#:~:text=The%20Haiti%20earthquake,1980%20and%202022%2C%20and%20the)

- [[5] https://www.statista.com/statistics/1007245/india-number-of-deaths-due-to- earthquakes/.](https://www.statista.com/statistics/1007245/india-number-of-deaths-due-to-earthquakes/)

- [[6] https://www.statista.com/statistics/263105/development-of-the-number-of-earth quakes-worldwide-since-2000/.](https://www.statista.com/statistics/263105/development-of-the-number-of-earthquakes-worldwide-since-2000/)

- [7] Y. Yamazaki, C. Premachandra, C.J. Perea, Audio-processing-based Human detection at disaster sites with unmanned aerial vehicle, IEEE Access. 8 (2020) 101398–101405. https://doi/10.1109/ACCESS.2020.2998776.

- [8] Y. Yamazaki, M. Tamaki, C. Premachandra, C.J. Perera, S. Sumathipala, B. H. Sudantha, Victim detection using UAV with on-board voice recognition system, in: 2019 Third IEEE International Conference on Robotic Computing (IRC), Naples, Italy, 2019, pp. 555–559, https://doi.org/10.1109/IRC.2019.00114.

- [9] Mohamed, I. & Lim, L. & Kun, & Mohamed, N. (2020). An embedded autonomous search and rescue mobile robotic system for alive human detection. 10.21884/IJM TER.2020.7022.0CLWX.

- [10] F.M. Talaat, H. ZainEldin, An improved fire detection approach based on YOLO-v8 for smart cities, Neural Comput. Applic. 35 (2023) 20939–20954, https://doi.org/ 10.1007/s00521-023-08809-1.

- [11] H. Chen, G. Zhou, H. Jiang, Student behavior detection in the classroom based on improved YOLOv8, Sensors 23 (20) (2023) 8385, https://doi.org/10.3390/ s23208385.

- [12] A.J. Mantau, I.W. Widayat, J.-S. Leu, M. K¨oppen, A Human-detection method based on YOLOv5 and transfer learning using thermal image data from UAV perspective for surveillance system, Drones 6 (2022) 290, https://doi.org/ 10.3390/drones6100290.

- [13] A.& Khalfaoui, A. Badri, I. El Mourabit, An improved YOLOv5 for real-time human detection in infrared images, Indones J. Electr. Eng. Comput. Sci. 32 (2023) 1078, https://doi.org/10.11591/ijeecs.v32.i2.pp1078-1085.


- [14] M.S¸. Gündüz, G. Is¸ık, A new YOLO-based method for real-time crowd detection from video and performance analysis of YOLO models, J. Real-Time Image Proc. 20 (2023) 5, https://doi.org/10.1007/s11554-023-01276-w.

- [15] K. Sharma, R. Doriya, S.K. Pandey, A. Kumar, G.R. Sinha, Dadheech P. Real-time survivor detection system in SaR missions using robots, Drones 6 (8) (2022) 219, https://doi.org/10.3390/drones6080219.

- [16] M.H. Yousefi, B. Behnam, S. Farahani, An auxiliary framework to facilitate earthquake search and rescue operations in urban regions, Nat. Hazards 120 (2024) 11107–11131, https://doi.org/10.1007/s11069-024-06619-9.

- [17] M. Statheropoulos, A. Agapiou, G.C. Pallis, et al., Factors that affect rescue time in urban search and rescue (USAR) operations, Nat. Hazards 75 (2015) 57–69, https://doi.org/10.1007/s11069-014-1304-3.

- [18] B.P.A. Rohman, M.B. Andra, H.F. Putra, D.H. Fandiantoro, M. Nishimoto, Multisensory surveillance drone for survivor detection and geolocalization in complex post-disaster environment, in: IGARSS 2019 - 2019 IEEE International Geoscience and Remote Sensing Symposium, Yokohama, Japan, 2019, pp. 9368–9371, https://doi.org/10.1109/IGARSS.2019.8899804.

- [19] N. Chaudhuri, I. Bose, Exploring the role of deep neural networks for post-disaster decision support, Decis. Support. Syst. 130 (2020) 113234, https://doi.org/ 10.1016/j.dss.2019.113234.

- [20] M.S. Mhaske, S.S. Raut, H. Chavan, An IoT based Human detection quadruped bot for rescue, Int. Res. J. Eng. Technol. IRJET 7 (04) (2020). https://www.irjet. net/archives/V7/i4/IRJET-V7I4371.pdf.

- [21] M. Justine Mr., D. Kichu Mr., S. Sreeraj Mr., T. Tomin Mr., R. Renju Mr., Human detection system using Iot, Int. J. Eng. Res. Technol. IJERT 11 (01) (2023). June 2023, https://www.ijert.org/human-detection-system-using-iot.

- [22] Y. Li, W. Hu, H. Dong, X. Zhang, Building damage detection from post-event aerial imagery using single shot multibox detector, Appl. Sci. 9 (6) (2019) 1128, https:// doi.org/10.3390/app9061128.

- [23] Y.J. Wong, M.-L. Tham, B.-H. Kwan, E.M.A. Gnanamuthu, Y. Owada, An optimized multi-task learning model for disaster classification and victim detection in federated learning environments, IEEE Access. 10 (2022) 115930–115944, https:// doi.org/10.1109/ACCESS.2022.3218655.

- [24] A. Joseph, V. Parmar, V. Bagyaveereswaran, Design of Human detection robot for natural calamity rescue operation, in: 2019 Innovations in Power and Advanced Computing Technologies (i-PACT), Vellore, India, 2019, pp. 1–5, https://doi.org/ 10.1109/i-PACT44901.2019.8959959.

- [25] Y. Rong, R. Gutierrez, K.V. Mishra, D.W. Bliss, Noncontact vital sign detection with UAV-borne radars: an overview of recent advances, IEEE Veh. Technol. Mag. 16 (3) (Sept. 2021) 118–128, https://doi.org/10.1109/MVT.2021.3086442.

- [26] J. Li, L. Liu, Z. Zeng, F. Liu, Advanced signal processing for vital sign extraction with applications in UWB radar detection of trapped victims in complex environments, IEEE J. Sel. Top. Appl. Earth. Obs. Remote Sens. 7 (3) (March 2014) 783–791, https://doi.org/10.1109/JSTARS.2013.2259801.

- [27] H. Lou, X. Duan, J. Guo, H. Liu, J. Gu, L. Bi, H. Chen, DC-YOLOv8: small-size object detection algorithm based on camera sensor, Electronics 12 (10) (2023) 2323, https://doi.org/10.3390/electronics12102323.

- [28] G. Seeja, A.S.A. Doss, V.B. Hency, A novel approach for disaster victim detection under debris environments using decision tree algorithms with deep learning features, IEEE Access. 11 (2023) 54760–54772, https://doi.org/10.1109/ ACCESS.2023.3281461.

- [29] K.R. Akshatha, A.K. Karunakar, S.B. Shenoy, A.K. Pai, N.H. Nagaraj, S.S. Rohatgi, Human detection in aerial thermal images using faster R-CNN and SSD algorithms, Electronics 11 (7) (2022) 1151, https://doi.org/10.3390/electronics11071151.

- [30] Z.-A. Zhao, S. Wang, M.-X. Chen, Y.-J. Mao, A.C.-H. Chan, D.K.-H. Lai, D.W.- C. Wong, J.C.-W. Cheung, Enhancing human detection in occlusion-heavy disaster scenarios: a visibility-enhanced DINO (VE-DINO) model with reassembled occlusion dataset, Smart Cities 8 (1) (2025) 12, https://doi.org/10.3390/ smartcities8010012.

- [[31] https://blog.roboflow.com/whats-new-in-yolov8/.](https://blog.roboflow.com/whats-new-in-yolov8/)

- [32] S. Sambolek, M. Ivasic-Kos, Automatic person detection in search and rescue operations using deep CNN detectors, IEEE Access. 9 (2021) 37905–37922, https://doi.org/10.1109/ACCESS.2021.3063681.

- [33] F. Zaman, N. Tahir, Y. Yusoff, M. Thamrin, Norashikin, A.H. Hasmi, Human detection from drone using you only look once (YOLOv5) for search and rescue operation, J. Adv. Res. Appl. Sci. Eng. Technol. 30 (2023) 222–235, https://doi. org/10.37934/araset.30.3.222235.

- [[34] R.H. Saputra, W. Waziana, Utilizing the Mit app inventor tools AS a learning MEDIA information to create android-based applications, Asia Inf. Syst. J. 2 (1) (2023).](http://refhub.elsevier.com/S2590-1230(26)01642-7/sbref0031)

- [35] Y. Tai, T.-T. Yu, Using smartphones to locate trapped victims in disasters, Sensors 22 (19) (2022) 7502, https://doi.org/10.3390/s22197502.

- [36] R. Damaˇseviˇcius, N. Bacanin, S. Misra, From sensors to safety: internet of emergency services (IoES) for emergency response and disaster management, J. Sens. Actuator. Netw. 12 (3) (2023) 41, https://doi.org/10.3390/jsan12030041.

- [37] M.-S.& Hong, R. Akerkar, Victim detection platform in IoT paradigm, Concurr. Comput.: Pract. Exp. (2019), https://doi.org/10.1002/cpe.5254.

- [38] K. Kucuk, C. Bayilmis, A.F. Sonmez, et al., Crowd sensing aware disaster framework design with IoT technologies, J. Ambient Intell. Hum. Comput. 11 (2020) 1709–1725, https://doi.org/10.1007/s12652-019-01384-1.
