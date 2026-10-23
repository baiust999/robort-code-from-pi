# **A SYSTEM FOR HIGH PRECISION GLASS-TO-GLASS DELAY MEASUREMENTS IN VIDEO COMMUNICATION** 

_Christoph Bachhuber and Eckehard Steinbach_ 

Technical University of Munich 

Chair of Media Technology 

Munich, Germany 

## **ABSTRACT** 

Ultra low delay video transmission is becoming increasingly important. Video-based applications with ultra low delay requirements range from teleoperation scenarios such as controlling drones or telesurgery to autonomous control of dynamic processes using computer vision algorithms applied on real-time video. To evaluate the performance of the video transmission chain in such systems, it is important to be able to precisely measure the glass-to-glass (G2G) delay of the transmitted video. In this paper, we present a low-complexity system that takes a series of pairwise independent measurements of G2G delay and derives performance metrics such as mean delay or minimum delay etc. from the data. The precision is in the sub-millisecond range, mainly limited by the sampling rate of the measurement system. In our implementation, we achieve a G2G measurement precision of 0.5 milliseconds with a sampling rate of 2kHz. 

**_Index Terms_ —** Video signal processing, Glass-to-glass delay measurement, video delay distribution 

## **1. INTRODUCTION** 

With the advent of 5G networks [1] and the prospects of the tactile internet [2] End-to-End (E2E) delays of 1 millisecond are requested for communication systems of the future. These ultra low delay systems enable applications such as networked control for fast assembly robots, highly dynamic teleoperation [3] in virtual or augmented reality[4], car-toX communication [5, 6] to improve safety and efficiency in transport, and many more. 

In all these scenarios, ultra low delay video transmission is an important component. Therefore, we need a precise measurement of the E2E video delay. For video transmission systems, which presents the video to a user on a display, this is called Glass-to-Glass (G2G) delay. It describes the time from when the photons of a visible event pass through the lens of a camera until the corresponding photons of the event shown on a display pass through the display glass. 

The G2G measurements are preferably non-intrusive, such that they can be applied to a wide range of systems. 

|Author|Auto-<br>matic|Non-<br>Intru-<br>sive|De-<br>corre-<br>lated|Cost|Pre-<br>cision|
|---|---|---|---|---|---|
|Hill/MC [7, 8]|no|yes|no|med|low|
|Jacobs [9]|no|yes|no|med|high|
|Sielhorst [10]|yes|yes|no|med|low|
|Boyaci [11]|yes|no|no|none|low|
|Jansen [12]|yes|yes|no|high|low|
|Our method|yes|yes|yes|low|high|


**Table 1** : Comparison of delay measurement methods. Justification of the classification is given in Section 1.1. Our method is presented in Section 2. 

Furthermore, a video camera typically has a fixed refresh rate, producing new images in constant time intervals. Real world events are virtually never synchronized to the camera frame capture time instances. To make realtime measurements, real-world events have to be triggered. Because of this non-deterministic G2G delay values are obtained. By repeating the measurement process several times, a distribution of delay values is obtained. 

Measuring partial delays such as the processing delay on a camera or the encoding latency is a standard task in system design. For both, the signal propagation time through the circuit has to be measured. But there are few approaches available to measure the G2G latency of the more complex system of an entire video transmission chain. This measurement also comprises delays from data transmission between processing blocks and the synchronization effects between blocks operating at fixed rate. 

## **1.1. Related Work** 

Several methods to measure G2G delay in video transmission have previously been proposed. An overview of their system characteristics is given in Table 1. 

The approaches in [7, 8] rely on the presentation of a running clock, for example on a computer screen. This clock is 

�������������������������������������� 

��������� 

���� 

filmed, the video of it transmitted and displayed by the video transmission system under test. Another camera films both the real clock and the clock displayed by the video transmission system. By comparing the clock states in the resulting image, the G2G delay can be obtained. These methods suffer from many issues: without image processing algorithms, the calculation of the delay has to be done manually by reading the numbers from the final image. For the measurement system, one has to purchase an additional camera to record the entire scene. Further, the achievable precision is low because the monitor displaying the running clock and the second camera are refreshed at their individual frame rates, e.g. _f_ Dis = _f_ Cam = 60Hz. 

Jacobs et al. [9] set the basis for our system: the authors use a blinking light-emitting diode (LED) in the field of view of the camera as signal generator and tape a photoelectric sensor to where the LED is shown on the display. The LED triggers an oscilloscope which also records the signals from the photoelectric sensor. This allows them to manually extract the G2G delay of individual samples. The problem is that this method is not automated on a simple circuitry and therefore requires high effort and expensive equipment. 

Sielhorst et al. [10] propose a system that comprises moving LEDs. From the position difference of the LEDs in the actual world and on the video, the delay is automatically computed by employing a computer vision algorithm. This method does not include the exposure delay of the camera since the source continuously creates events (new translation positions). Furthermore, they use a recording rate of the measurement camera of at most 200 Hz. This introduces an average imprecision of 5 milliseconds. 

Boyaci et al. [11] measure the capture-to-display latency between a caller and a callee in a video conferencing application. They embed timing information in the form of an EAN-8 barcode in the recorded frames. This information is decoded on the callee PC and compared to the internal clock in software. The method is constrained to desktop computers, since it is intrusive and requires custom software to be executed on the caller and callee machines. The authors assume synchronized clocks and take no further analyses or measures to ensure synchronization. Finally, the method does not include the delay introduced by the graphics buffer and the display, since the timestamp is compared to the current time immediately after decoding. 

Jansen et al. [12] utilize QR codes to mark time. A measurement system feeds QR codes from a display to the camera of the system under test, from which the video is displayed and again recorded by the measurement system. The measurement system decodes the QR code and computes the G2G delay. The problem is that a camera is not a time-precise recording tool. Further, a computer or laptop and a camera have to be used as measurement system, which constitutes one of the most expensive options here. 


**Fig. 1** : Delay measurement principle 

## **1.2. Contribution** 

We propose a G2G delay measurement system that unifies most of the benefits of the existing systems as shown in Table1. It is an advancement of Jacobs’ [9] system and comprises an LED as light source and a phototransistor (PT) as light detector. The actual LED can cover only a small area of the video image to not bias the coding process. The analysis of the data is not done manually with an oscilloscope, but automatically with a microcontroller board. We propose a theoretical model for G2G delay and relate initial measurements obtained with the new system to it. 

The remainder of this paper is organized as follows: Section 2 describes the system principle, the hardware and software implementation and a theoretical model for delay. Section 3 presents and discusses results obtained with the measurement system. Section 4 summarizes the results and gives an outlook to future work in this field. 

## **2. SYSTEM DESCRIPTION** 

## **2.1. Concept and Realization** 

The G2G delay measurement process is based upon the idea that the video transmission system delays the propagation of light, as depicted in Figure 1. An initially disabled light source is put in the field of view of the camera. After enabling the light source, the video transmission system requires the G2G delay _T_ to transmit this information to the display, which is picked up by the light sink. The proposed approach assumes an ideal system without any reaction delay within the light source and sink and with no noise. 

We created a prototype with an Arduino _⃝_ R Uno. It is depicted in Figure 2. It can be connected to a PC using USB or to mobile devices using bluetooth. An LED acts as light source in the field of view of the camera. In LEDs, the time between the start of an electrical current pulse and the start of emission of photons is typically below one microsecond. Since our measurements are in the order of milliseconds, the delay from the LED is negligible. The light sink is a phototransistor (PT) which has a rise and fall time of 10 microseconds, which is also small compared to the G2G delay we want to be able to measure. To suppress noise we are using the detection algorithm proposed in Section 2.2. 

���� 


**Fig. 2** : Prototype 

## **2.2. Signal Processing** 

The voltage dropping over the PT is sampled at 2kHz in our prototype. The resolution of the voltage is 10 bit, resulting in 1024 brightness levels. To extract the time at which the event appears on the display, the sample data undergoes a two-step processing: first, a maximum smoothing filter and second a rising edge detection algorithm are applied (both steps are described below). The algorithm has been validated by comparing the resulting G2G delays with manually read values from an oscilloscope which is connected to the LED and PT. 

The maximum smoothing is required to suppress wrong detections caused by pulse width modulation (PWM) of LCD display backlight or short light pulses in CRT and plasma monitors. The filter has two tasks: smooth the signal from unwanted waves and let the resulting signal increase immediately if the input signal increases. This is solved by the maximum filter with length _k_ . For every new raw sample _ai_ , the maximum 


of itself and the previous _k_ samples is stored in the processed value _bi_ . 

To automatically find the sample at which a consistent increase of the sample values is initiated, we apply a rising edge detection based on slope thresholding on the processed samples _bi_ . An increase of a cumulative 20 brightness levels over the duration of 3 subsequent samples or the same increase within one sample to the next triggers the flag that the picture of the lit up LED can now be seen on the display. These parameters make the algorithm robust against noise from external lighting and panel refresh on one hand. On the other hand, it enables us to reliably recognize the lighting up of the LED in typical measurement environments without further precautions. 

With constant inter-measurement intervals, a measurement sequence of a simple Camera to PC setup exhibits 

strong correlations between measurement samples, considerably reducing their significance. This is because of the constantly changing phase shifts between the sampling processes in the camera and display. To avoid these correlations, we use random inter-measurement intervals. 

## **2.3. Delay Distribution** 

To explain the G2G measurements obtained with the proposed system, we model the G2G delay distribution of a simple raw video transmission system consisting of a camera, a PC and a display. We first define three partial delays: the camera sampling delay _p_ Cam( _t_ ) _∼U_ ( _t_ min _, f_ Cam<sup>_−_1+</sup><sup>_t_min) con-</sup> tributed by the camera sampling is uniformly distributed because the turn-on time of the LED is independent of the frame period _f_ Cam<sup>_−_1of the camera.The LED has to light up at least</sup> _t_ min before the end of a frame period _f_ Cam<sup>_−_1to be part of the</sup> current frame. This frame is read out of the sensor and transmitted at the end of the current frame period, leading to a delay in the interval [ _t_ min _, f_ Cam<sup>_−_1].If the LED turns on later than</sup> that during the current frame period, the light-up information is transmitted at the end of the next frame period, causing a delay in ] _f_ Cam<sup>_−_1</sup><sup>_, f −_</sup> Cam<sup>1+</sup><sup>_t_min]. These two possibilities together</sup> form the uniform distribution of _p_ Cam( _t_ ) as seen in the beginning of this paragraph. The occurrence of the second possibility has two reasons: first, it either lights up so late during the exposure that the corresponding relatively dark depiction on the display will not trigger the rising edge detection. Second, the LED can light up during a frame period after the exposure has ended. The minimum exposure required for triggering and the difference between a frame period _f_ Cam<sup>_−_1andtheex-</sup> posure time add up to _t_ min. 

The display refresh also contributes a uniform delay _p_ Ref ( _t_ ) _∼U_ (0 _, f_ Dis<sup>_−_1),upperboundedbytheinverseofthe</sup> display refresh rate _f_ Dis<sup>_−_1.This delay is uniformly distributed</sup> because the display refreshes independently of when the computer fills the graphics buffer. 

All remaining parts like the processing in the camera, PC and display and the interface delays are modeled to be deterministic and are thus represented by one variable _p_ Proc( _t_ ) _∼ δ_ ( _t_ Proc). In reality, there will be deviations from the ideal deterministic delay for example because we do not use a realtime operating system. 

Since the G2G-delay _T_ is the sum of these three mutually independent delays, the corresponding probability distribution 


is the convolution of them. The G2G delay distribution approximates an isosceles trapezoid shape that is centered around the mean _t_ Proc + _t_ min + 2 _f_ Cam1<sup>+</sup> 2 _f_ <u>1Dis</u><sup>with minimum</sup> delay _t_ Proc+ _t_ min and maximum latency _t_ Proc+ _t_ min+ _f_ Cam1<sup>+</sup> _f_ Dis1<sup>.In real measurements, the non-deterministic processing</sup> delay will smoothen the nooks of the shape. 

���� 2134 

## **3. MEASUREMENTS** 

We present measurements conducted with our prototype described in Section 2. The video transmission system is a Fedora 20 PC with an AlliedVision Guppy PRO F-031C IEEE 1394 camera and a Samsung 2233BW monitor at _f_ Dis = 60Hz. We parametrized the camera such that the exposure time is, with a negligibly small difference below the millisecond order, equal to the frame period. As displaying software, we use coriander 2.0.2. 

The G2G delay distribution of 250 measurements with _f_ Cam = 50Hz is shown in Figure 3a. The delay is at minimum 19.1ms= _t_ Proc + _t_ min. The sum elements can not be distinguished using the data produced by the proposed measurement system. With this minimum delay, it takes at minimum 19.1ms from an event taking place until it is shown on the display. This can also be thought of as the best case measurement. The opposite, the maximum delay is 52.4ms= _t_ Proc + _t_ min + _f_ Cam1<sup>+</sup> _f_ Dis1<sup>, representing the worst case delay</sup> from the event until the display of it. The 95% confidence interval from fitting a Student’s _t_ -distribution to the histogram in Figure 3a for the mean ranges from 32.4ms to 34.1ms. The standard deviation is 6.9ms. The histogram in Figure 3a also confirms the assumptions from Section 2.3: it approximates an isosceles trapezoid and has a width of 52 _._ 4ms _−_ 19 _._ 1ms = 33 _._ 3ms. This is a few milliseconds smaller than _f_ Cam1<sup>+</sup> _f_ Dis1<sup>_≈_</sup> 20ms + 16 _._ 7ms = 36 _._ 7ms because the ideal worst and best case delays are so improbable that they did not occur in this series of measurements. Performing more measurements reduces the difference in width between theory and practical measurements. But with an increasing number of measurements, the difference only approximates zero, but does not perfectly equal it. This is why we did not perform more measurements here. 

In Figure 3b, we plot maximum G2G delay, the bounds for the 95% confidence interval for estimating the mean, the minimum delay and the standard deviation of the delay as a function of the frame rate of the camera. For every frame rate setting, 250 G2G measurements have been performed. The statistics of the measurements in Figure 3a can be seen at 50Hz in Figure 3b. All statistics are monotonically decreasing with ascending frame rates. This is because _f_ Cam<sup>_−_1,</sup> influencing the camera sampling delay, gets smaller. _t_ min decreases because with ascending frame rates, we increase the gain of the camera sensor, which allows the LED to be turned on later during exposure and still be detected by the PT. The 95% confidence interval for the mean estimation lies between the curves MeanUpper and MeanLower. The delay distributions of the different frame rates resemble the distribution in Figure 3a, thus providing no further insight and are therefore not depicted. 

The triple **(minimum delay / mean delay / maximum delay)** sufficiently describes the G2G delay characteristics of a system, so this is the metric we report. For the 


(b) G2G delay measurement distribution characteristics for different frame rates of the camera 

**Fig. 3** : Measurements 

_f_ Cam = 25Hz and _f_ Cam = 300Hz camera frame rates, these are (24 _._ 8 _/_ 50 _._ 4 _/_ 78 _._ 7)ms and (8 _._ 1 _/_ 15 _._ 5 _/_ 23)ms, respectively. For _f_ Cam = 25Hz, the width of the histogram, which is the difference between minimum and maximum delay, is 53.9ms, approximating _f_ Cam1<sup>+</sup> _f_ Dis1<sup>_≈_40ms + 16</sup><sup>_._7ms=56</sup><sup>_._7ms.</sup> An analog approximation holds over all measured camera frequencies, which again confirms the model from Section 2.3. 

## **4. CONCLUSIONS** 

We proposed an inexpensive, automatic and highly precise G2G delay measurement system. It unifies advantages of previously proposed implementations and can be used to independently assess bigger, more complex video transmission systems. Furthermore, we briefly discussed the origins of delay in video transmission and showed that the measurements fit to the proposed model. 

���� 

## **5. REFERENCES** 

- [1] Federico Boccardi, Robert W Heath, Aurelie Lozano, Thomas L Marzetta, and Petar Popovski, “Five disruptive technology directions for 5g,” _IEEE Communications Magazine_ , vol. 52, no. 2, pp. 74–80, 2014. 

- [2] Gerhard P Fettweis, “The tactile internet: Applications and challenges,” _IEEE Vehicular Technology Magazine_ , vol. 9, no. 1, pp. 64–70, 2014. 

   - [11] Omer Boyaci, Andrea Forte, Salman Abdul Baset, and Henning Schulzrinne, “vdelay: A tool to measure capture-to-display latency and frame rate,” in _Multimedia, 2009. ISM’09. 11th IEEE International Symposium on_ . IEEE, 2009, pp. 194–200. 

   - [12] Jack Jansen and Dick CA Bulterman, “User-centric video delay measurements,” in _Proceeding of the 23rd ACM Workshop on Network and Operating Systems Support for Digital Audio and Video_ . ACM, 2013, pp. 37–42. 

- [3] Mitchell JH Lum, Diana CW Friedman, Hawkeye HI King, Regina Donlin, Ganesh Sankaranarayanan, Timoty J Broderick, Mika N Sinanan, Jacob Rosen, and Blake Hannaford, “Teleoperation of a surgical robot via airborne wireless radio and transatlantic internet links,” in _Field and service robotics_ . Springer, 2008, pp. 305– 314. 

- [4] Curtis W Nielsen, Michael Goodrich, Robert W Ricks, et al., “Ecological interfaces for improving mobile robot teleoperation,” _IEEE Transactions on Robotic_ , vol. 23, no. 5, pp. 927–941, 2007. 

- [5] Klaus David and Alexander Flach, “Car-2-x and pedestrian safety,” _IEEE Vehicular Technology Magazine_ , vol. 5, no. 1, pp. 70–76, 2010. 

- [6] Andreas Festag, Roberto Baldessari, Wenhui Zhang, Long Le, Amardeo Sarma, and Masatoshi Fukukawa, “Car-2-x communication for safety and infotainment in europe,” _NEC Technical Journal_ , vol. 3, no. 1, pp. 21– 26, 2008. 

- [7] Rhys Hill, Christopher Madden, Anton van den Hengel, Henry Detmold, and Anthony Dick, “Measuring latency for video surveillance systems,” in _Digital Image Computing: Techniques and Applications, 2009. DICTA’09._ IEEE, 2009, pp. 89–95. 

- [8] John MacCormick, “Video chat with multiple cameras,” in _Proceedings of the 2013 conference on Computer supported cooperative work companion_ . ACM, 2013, pp. 195–198. 

- [9] Marco C Jacobs, Mark A Livingston, et al., “Managing latency in complex augmented reality systems,” in _Proceedings of the 1997 symposium on Interactive 3D graphics_ . ACM, 1997, pp. 49–ff. 

- [10] Tobias Sielhorst, Wu Sa, Ali Khamene, Frank Sauer, and Nassir Navab, “Measurement of absolute latency for video see through augmented reality,” in _Proceedings of the 2007 6th IEEE and ACM International Symposium on Mixed and Augmented Reality_ . IEEE Computer Society, 2007, pp. 1–4. 

���� 

