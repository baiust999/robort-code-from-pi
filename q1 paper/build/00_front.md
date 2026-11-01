# A Low-Cost Fail-Safe Teleoperated Rescue Robot with Two-Way Victim Audio and Video: Firmware-Bounded Stop, Supervised Recovery and Measured Resource Cost

Chinmoy Sarkar, Sadman Adib, Sadia Sultana

[AUTHOR INPUT REQUIRED: confirm author-name spelling and order; affiliations; corresponding author and e-mail; ORCID iDs.]

## Abstract

Rescue robots are usually teleoperated over radio links that fail, and low-cost platforms rarely report how their stop behaviour or victim communication performs on their own hardware. We present a teleoperated rescue robot built from commodity parts and evaluate three of its properties. An Arduino UNO runs the motor firmware, and a Raspberry Pi 4 runs three isolated processes for control, two-way WebRTC audio and video, and supervision, on a local Wi-Fi network with no Internet uplink. A dead-man timer in the firmware removes motor drive when valid commands stop arriving, independently of the Pi and the link. Timed on the control process's event log, drive was removed within 2042 ms of the last command in 30 of 30 trials (mean 2022.5 ms), below an analytical bound of about 2060 ms. The watchdog restored service with a new process identifier in 30 of 30 SIGKILL trials (95% Wilson lower bound 88.6%), with mean recovery times of 12.8 to 16.0 s. One operator media session used 62.9% of one core on the media process while the control process stayed below 4%, provided the Pi had an adequate supply; the original power bank under-volted under the same load. The itemized parts cost about USD 310 (37,158 BDT). The stop figure is the time at which drive is removed, not a wheel-stop time or a stopping distance. Control latency over Wi-Fi, media delay and quality, an end-to-end field trial and an operator usability study have not yet been measured.

## Index Terms

Dead-man timer, edge computing, fail-safe control, fault tolerance, Raspberry Pi, search and rescue robotics, teleoperation, WebRTC.
