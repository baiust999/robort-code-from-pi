## VII. FUTURE WORK

Each direction below starts from a limitation in Section VI-C. Any direction that adds automated behaviour keeps the firmware dead-man independent of the new function and re-tests its stop interval after each change.

*Physical and end-to-end measurement.* The first step is to close the pending measurements: wheel-stop time and stopping distance filmed at 240 fps with every stop logged by P1 (E3, E4), key-press-to-wheel latency over Wi-Fi (E2), glass-to-glass video and audio delay with one and two viewers (E5), and the field trial and usability study once ethics approval is in place (E13, E14). The dashboard heartbeat should be moved off throttleable browser timers and its delivered interval logged, since Section V-A showed that the margin of the window depends on it.

*Ablations and fault coverage.* The three planned ablations, together with injected hangs, camera and microphone loss and network faults, would show what each mechanism contributes. P1 should reopen a re-enumerated serial device without a restart, and the fast PANIC notice should be forwarded to the dashboard instead of waiting for the next telemetry frame.

*Communication range.* The range sweep should continue to the failure point and add obstructed links, with repeated bursts at fixed stations, a pre-registered usable-range criterion, recorded router position and channel, and a scan of neighbouring networks. Wireless relays between operator and robot have been proposed for SAR [@schneider2016]; a relay or mesh is outside the present single-cell design.

*Localization.* GPS is the only position source. The drive motors carry encoders whose outputs are not yet read; wheel odometry, an inertial sensor and a GPS track filter that accounts for satellite count would address the drift of Section V-F, and the telemetry log should record six decimal places.

*Security.* TLS on both ports, per-operator credentials instead of one shared key, and a mandatory sequence check would remove the trusted-network assumption of Section III-H.

*Victim-finding aids.* The aids of Section III-K need evaluation before any claim: detection and false-alarm rates on disaster-like scenes, intelligibility of the voice message through the robot speaker in noise, and whether a frightened or injured person can read and use the answer buttons.
