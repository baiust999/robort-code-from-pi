## VII. FUTURE WORK

Each direction below starts from a limitation in Section VI-C. Any direction that adds automated behaviour keeps the firmware dead-man independent of the new function and re-tests its stop interval after each change.

*Physical and end-to-end measurement.* The first step is to close the pending measurements: wheel-stop time, and the distance covered after drive is removed, filmed at 240 fps with every stop logged by P1 (E4), glass-to-glass video and audio delay with one and two viewers (E5) and the media-isolation test (E16), each judged against the criterion fixed in Table XVII. An end-to-end field trial with a role-played victim on a fixed course, under ethics approval, would then test the find-and-talk task as a whole. Control latency over Wi-Fi and operator usability were not evaluated; a usability study should fix the target interval width on the mean System Usability Scale (SUS) score [@brooke1996] before recruiting operators. The dashboard heartbeat should be moved off throttleable browser timers and its delivered interval logged, since Section V-A showed that the margin of the window depends on it.

*Fault coverage.* Injected hangs beyond the E16 freeze, camera and microphone loss and network faults would extend the SIGKILL-only campaign of Section V-C. P1 should reopen a re-enumerated serial device without a restart, and the fast PANIC notice should be forwarded to the dashboard instead of waiting for the next telemetry frame.

*Communication range.* The range sweep should continue to the failure point and add obstructed links, with repeated bursts at fixed stations, a pre-registered usable-range criterion, recorded router position and channel, and a scan of neighbouring networks. Wireless relays between operator and robot have been proposed for SAR [@schneider2016]; a relay or mesh is outside the present single-cell design.

*Localization.* GPS is the only position source. The drive motors carry encoders whose outputs are not yet read; wheel odometry, an inertial sensor and a GPS track filter that accounts for satellite count would address the drift of Section V-F, and the telemetry log should record six decimal places.

*Security.* TLS on both ports, per-operator credentials instead of one shared key, and a mandatory sequence check would remove the trusted-network assumption of Section III-H.

*Victim-finding aids.* The aids of Section III-K need evaluation before any claim: the person detector scored box by box on a labelled frame set captured through the robot's own video path, stratified by posture, occlusion, illumination and distance, with its false-alarm rate on person-free video; a within-subjects victim-communication study, under ethics approval, comparing speech alone, the repeating voice message and tap-to-answer questions for a participant who cannot speak; intelligibility of the voice message through the robot speaker in noise; and the processor cost of these aids on P2.
