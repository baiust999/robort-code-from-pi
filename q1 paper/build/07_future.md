## VII. FUTURE WORK

Each direction below starts from a limitation in Section VI-C. Any direction that adds automated behaviour keeps the firmware dead-man independent of the new function and re-tests its stop interval after each change.

*Physical and end-to-end measurement.* The first step is to close the pending measurements: wheel-stop time and stopping distance filmed at 240 fps with every stop logged by P1 (E3, E4), glass-to-glass video and audio delay with one and two viewers (E5), the media-isolation test (E16) and the field trial once ethics approval is in place (E13), each judged against the criterion fixed in Table XVII. Control latency over Wi-Fi and operator usability were not evaluated; a usability study should fix the target interval width on the mean System Usability Scale (SUS) score [@brooke1996] before recruiting operators. The dashboard heartbeat should be moved off throttleable browser timers and its delivered interval logged, since Section V-A showed that the margin of the window depends on it.

*Fault coverage.* Injected hangs beyond the E16 freeze, camera and microphone loss and network faults would extend the SIGKILL-only campaign of Section V-C. P1 should reopen a re-enumerated serial device without a restart, and the fast PANIC notice should be forwarded to the dashboard instead of waiting for the next telemetry frame.

*Communication range.* The range sweep should continue to the failure point and add obstructed links, with repeated bursts at fixed stations, a pre-registered usable-range criterion, recorded router position and channel, and a scan of neighbouring networks. Wireless relays between operator and robot have been proposed for SAR [@schneider2016]; a relay or mesh is outside the present single-cell design.

*Localization.* GPS is the only position source. The drive motors carry encoders whose outputs are not yet read; wheel odometry, an inertial sensor and a GPS track filter that accounts for satellite count would address the drift of Section V-F, and the telemetry log should record six decimal places.

*Security.* TLS on both ports, per-operator credentials instead of one shared key, and a mandatory sequence check would remove the trusted-network assumption of Section III-H.

*Victim-finding aids.* The aids of Section III-K need evaluation before any claim: detection and false-alarm rates on disaster-like scenes, intelligibility of the voice message through the robot speaker in noise, and whether a frightened or injured person can read and use the answer buttons.
