## **University of Nebraska - Lincoln DigitalCommons@University of Nebraska - Lincoln** 

CSE Conference and Workshop Papers Computer Science and Engineering, Department of 

#### 2010 

# Survivor Buddy and SciGirls: Affect, Outreach, and Questions 

Robin R. Murphy _Texas A&M University_ , murphy@cse.tamu.edu 

Vasant Srinivasan 

_Texas A&M University_ 

Negar Rashidi 

_Texas A&M University_ 

Brittany Duncan 

_University of Nebraska-Lincoln_ , bduncan@unl.edu 

Aaron Rice 

_Texas A&M University_ 

**_See next page for additional authors_** 

Follow this and additional works at: http://digitalcommons.unl.edu/cseconfwork 

Murphy, Robin R.; Srinivasan, Vasant; Rashidi, Negar; Duncan, Brittany; Rice, Aaron; Henkel, Zachary; Garza, Marco; Nass, Cliff; Groom, Victoria; Zourntos, Takis; Daneshwar, Roozbeh; and Prasad, Sharath, "Survivor Buddy and SciGirls: Affect, Outreach, and Questions" (2010). _CSE Conference and Workshop Papers_ . 243. http://digitalcommons.unl.edu/cseconfwork/243 

This Article is brought to you for free and open access by the Computer Science and Engineering, Department of at DigitalCommons@University of Nebraska - Lincoln. It has been accepted for inclusion in CSE Conference and Workshop Papers by an authorized administrator of DigitalCommons@University of Nebraska - Lincoln. 

##### **Authors** 

Robin R. Murphy, Vasant Srinivasan, Negar Rashidi, Brittany Duncan, Aaron Rice, Zachary Henkel, Marco Garza, Cliff Nass, Victoria Groom, Takis Zourntos, Roozbeh Daneshwar, and Sharath Prasad 

This article is available at DigitalCommons@University of Nebraska - Lincoln: http://digitalcommons.unl.edu/cseconfwork/243 

Published in: Proceedings of the 5th ACM/IEEE international conference on Human-robot interaction (HRI '10), 

IEEE Press Piscataway, NJ, USA, pp 127-128. © 2010 

### **Survivor Buddy and SciGirls: Affect, Outreach, and Questions** 

Robin Murphy,Vasant Srinivasan, Negar Rashidi, Brittany Duncan, Aaron Rice, Zachary Henkel, Marco Garza Computer Science and Engineering Texas A and M University College Station, TX- 77843 

Cliff Nass, Victoria Groom Takis Zourntos, CHIME Lab Roozbeh Daneshwar, Stanford University Sharath Prasad Stanford, CA. 94305-2050 Electrical & Computer Engineering Texas A& M University College Station, TX 77843 

**_Abstract_ —This paper describes the Survivor Buddy human-robot interaction project and how it was used by four middle-school girls to illustrate the scientific process for an episode of “SciGirls”, a Public Broadcast System science reality show. Survivor Buddy is a four degree of freedom robot head, with the face being a MIMO 740 multi-media touch screen monitor. It is being used to explore consistency and trust in the use of robots as social mediums, where robots serve as intermediaries between dependents (e.g., trapped survivors) and the outside world (doctors, rescuers, family members). While the SciGirl experimentation was neither statistically significant nor rigorously controlled, the experience makes three contributions. It introduces the Survivor Buddy project and social medium role, it illustrates that human-robot interaction is an appealing way to make robotics more accessible to the general public, and raises interesting questions about the existence of a minimum set of degrees of freedom for sufficient expressiveness, the relative importance of voice versus non-verbal affect, and the range and intensity of robot motions.** 

**_Keywords-_ assistive robots, human-robot interaction, gaze and gestures, interaction styles, robots, user interfaces** 

##### I.  INTRODUCTION 

Robots are being considered for applications where they serve as proxies for humans interacting with another human (point of injury care). Consider that two trapped Australian miners requested MP3 players with a Foo Fighters Album while waiting for rescue [1]. In these domains, the human (“dependent”) is connected to multiple other humans (“controllers”) via the robot proxy for long periods of time. The literature already shows that the dependent in search and rescue scenarios will respond to the robot socially [2], [3], raising the possibility that people become distrustful as well as cognitively confused by a robot that presents a different affect for different controllers rather than a consistent communication strategy. 

The Survivor Buddy project, which is investigating a formal, comprehensive communication strategy for HRI combining verbal and non-verbal affect, was recently used for an episode of the Public Broadcasting System (PBS) “science reality” TV show called SciGirls to be aired in February 2010. In each SciGirls episode, a set of 3 or 4 middle school girls are paired with mentors to design, implement, conduct and analyse a scientific experiment. In this episode, four girls worked with the Survivor Buddy multi-media, social robot “head.” The Survivor Buddy head has a LCD screen to permit the survivor to videoconference with responders (or family), watch live TV or listen to music. The first version of the head has four degrees of freedom emulating the range and speed of human head movements. 

The SciGirls programmed affective behaviours and voices for the Survivor Buddy then tested them with their friends. 

##### II. RELATED WORK 

Survivor Buddy is intended to be a _social medium_ , serving as a multimedia link to the outside world and a form of expression for surrogate operation by remote humans communicating with the victim. Work by Nass shows that even when technologies lack explicit social cues, people respond to them as social entities [4]. The Computers as Social Actors paradigm suggests that individuals automatically apply a wide range of social responses to technologies [5], [4]. Research performed under this paradigm has shown that even computer experts are polite to computers [6], apply gender stereotypes to computers [7], and are motivated by feelings of moral obligation toward computers [8]. Computer users identify a computer’s “personality” as submissive or dominant and as in human-human interaction, respond more favourably to one with a personality similar to their own [9], [10]. Even unintentional cues of social identity elicit powerful attitudinal and behavioural responses from humans. 

##### III. QUASI-EXPERIMENTAL DESIGN, IMPLEMENTATION AND ANALYSIS 

Four different independent variables were considered with the focus eventually landing on _personality_ . The final study design featured a single factor (extroversion) with two levels (extrovert vs. introvert).In discussions with the four girls, it was decided that the study task needed to feature the robot’s voice and affective behaviours designed by the girls earlier in filming as part of their introduction to robotics. The girls also learned the need for participant’s experiences to be identical for both conditions, except for the personality manipulation. Tic-tac-toe was selected because it was game that could be rigged, so that any differences in attitudes toward the robot were attributable to the manipulation, not participant performance in the game. 

The prototype version of Survivor Buddy was teleoperated with an affective behavioural interface and a verbal interface 





Fig.1- View from SB Webcam     Fig.2-View of experimental layout 

978-1-4244-4893-7/10/$25.00 © 2010 IEEE 

127 

The affective behavioural interface consisted of a button menu of the behaviours (YES, NO, SURPRISE, SAD) and two variations (extraand introverted) created by the SciGirls. The behaviours were developed by the girls using the Microsoft Robotics Developer Studio (MRDS).The voice interface was implemented using the Center for Spoken Language (CSLU) Toolkit [11]. The extraversion team modified the voice to be higher, speak faster, and have more variation while the introversion team made the voice a bit higher and faster than the default but less than the extravert voice and somewhat slower. 

Two of the featured girls remained in the room taking notes on the participant’s behaviour, while the final featured girl used a laptop to select and play the robots utterances. After the game one of the girls escorted the participants to a separate room where they completed the questionnaire. The questionnaire featured a total of six items. Instructions at the top of the questionnaire told participants to indicate how well each of the words described the robot they interacted with. Each item featured a five-point unipolar scale ranging from Not at all to extremely. To determine if there were any personality-attraction effects, the four girls also rated their friends extroversion, indicating how reserved and outgoing each of their friends was on a five point scale. These scores were used to group each of the participants into one of three categories corresponding to low, medium, and high extroversion. Since the girls were not yet familiar with statistical methods, the girls calculated condition averages for each of the six questionnaire items. The greatest difference between group averages was for the reserved and outgoing measures. The girl’s analysis also suggested that participants preferred the extroverted robot, regardless of participant personality, but that participants with middling extroversion scores liked the robot the most. 

###### IV. OBSERVATIONS 

While the experimentation was not statistically significant, the design process combined with the reaction of the SciGirls and their friend suggest three research questions. First, the SciGirl affective designs favoured some degrees of freedom over others (as seen from table 1), posing the question of _is a minimal set or a preference ordering of degrees of freedom for an affective robot head?_ Identification of such a set could allow the mechanical design to be more cost-effective and allow HRI researchers to focus on creating a satisfactory set of behaviours around this minimal set. Second, an examination of the sessions 

captured by the Survivor Buddy’s webcam showed that the SciGirls’ friends fixated on the stationary robot head rather than the external speakers, with the exception of the first group which could see the SciGirls. This raises the question of _is voice more important than non-verbal cues for certain situations?_ If voice is more important than nonverbal cues, it may be a more cost-effective way to make existing non-anthropomorphic robots socially consistent or to reduce costs in new robots. Fig. 2 shows one group clearly looking at robot but as can be seen from Fig. 1, this is almost 90<sup>_◦_</sup> from the actual source of the voice. But the relative contribution of voice versus nonverbal cues remains unclear. Third, the SciGirls experimentation with introverted and extroverted characteristics highlight that there is no understanding of _what is the right range and velocity of motion?_ Is duplicating human motion sufficient or even desirable? This is important because it informs mechanical design. 

TABLE I 

JOINT RANGE ASSOCIATED WITH EACH BEHAVIOR 

||Pan|Tilt|Roll|Translate|
|---|---|---|---|---|
|Yese||± 50<sup>_◦_</sup>|||
|Yesi||||± 7 Cm|
|Noe|± 90<sup>_◦_</sup>||||
|Noi|± 60<sup>◦</sup>||||
|Surprisee||- 60<sup>◦</sup>|||
|Surprisei||- 30<sup>◦</sup>|||
|Sade||+20<sup>◦</sup>|-45<sup>◦</sup>|- 7 Cm|
|Sade|+60<sup>◦</sup>|+20<sup>◦</sup>||- 7 Cm|
|Sadi||+15<sup>◦</sup>||- 4.6 Cm|



VI. ACKNOWLEDGMENTS 

This work was supported in part by NSF Grant IIS-0905485 “The Social Medium is the Message” and by a HRI grant from Microsoft External Research. The authors would like to thank Prof. Karen Butler-Perry; Allan Branch; Ross Flach and Chris Addock at the Oran W. Nicks Low Speed Wind Tunnel, Apoorv Bansal and Hariharan Subramanian for their assistance with the construction and programming of the Survivor Buddy prototype, the girls and PBS film crew Marissa Blahnik and Angie Prindle who made the SciGirls filming a meaningful experience . 

###### REFERENCES 

- [1] B. I. News, “Dave grohl to meet trapped miners http://news.bbc.co.uk/2/hi/entertainment/5301658.stm,”Aug. 2006. 

- [2] C. Bethel, C. Bringes, and R. R. Murphy, “Non-facial and non-verbal affective expression in appearance-constrained robots for use in victim management (video abstract)” _ACM SIGART/SIGINT Human-Robot Interaction_ , 2009. 

- [3] T. Fincannon, L. E. Barnes, R. R. Murphy, and D. L. Riddle, “Evidence of the need for social intelligence in rescue robots,” in _IEEE/RSJ International Conference on International Conference on Intelligent Robots and Systems (IROS 2004)_ , vol. 2, 2004, pp. 1089 – 1095. 

- [4] B. Reeves and C. Nass, _The media equation: how people treat computers, television, and new media like real people and places_ . Cambridge University Press New York, NY, USA, 1996. 

- [5] C. Nass and Y. Moon, “Machines and mindlessness: Social responses to computers,” _Journal of Social Issues_ , vol. 56, no. 1, pp. 81–103, 2000. 

- [6] C. Nass, Y. Moon, and P. Carney, “Are people polite to computers? responses to computer-based interviewing systems,” _Journal of Applied Social Psychology_ , vol. 29, no. 5, pp. 1093–1110, 1999. 

- [7] E.-J. Lee, C. Nass, and S. Brave, “Can computer-generated speech have gender? an experimental test of gender stereotypes.” in _CHI 2000_ . The Hague, The Netherlands: ACM Press, 2000, pp. 329–336. 

- [8] B. J. Fogg and C. Nass, “Do users reciprocate to computers?” in _ACMCHI_ , 1997. 

- [9] Y. Moon and C. Nass, “How ”real” are computer personalities psychological responses to personality types in human-computer interaction,” _Communication Research_ , vol. 23, no. 6, pp. 651–674, 1996 

- [10] C. Nass, Y. Moon, B. J. Fogg, B. Reeves, and D. C. Dryer, “Can computer personalities be human personalities?” _International Journal of Human-Computer Studies_ , vol. 43, no. 2, pp. 223–239, 1995. 

- [11] Center for Spoken Languages (CLSU) Toolkit. Oregon Graduate Institute and Health and Science University, 2009. 

128 

