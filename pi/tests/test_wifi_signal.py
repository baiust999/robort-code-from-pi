"""Wi-Fi signal telemetry: read, flag, and log signal_dbm honestly.

The dashboard's bars are only as trustworthy as this value. A link that has
gone down must come through as None (shown as NO SIGNAL), never as the last
good reading, and the log must record it so a distance sweep can be analysed.
"""

from pathlib import Path

from common import protocol, wifi
from p1_control.telemetry_log import CSV_COLUMNS, TelemetryLog

PROC = """\
Inter-| sta-|   Quality        |   Discarded packets               | Missed | WE
 face | tus | link level noise |  nwid  crypt   frag  retry   misc | beacon | 22
 wlan0: 0000   58.  -52.  -256        0      0      0    494      0        0
"""


def fake_system(tmp_path: Path, operstate: str = "up", proc: str = PROC) -> dict:
    proc_path = tmp_path / "wireless"
    proc_path.write_text(proc)
    iface_dir = tmp_path / "net" / "wlan0"
    iface_dir.mkdir(parents=True)
    (iface_dir / "operstate").write_text(operstate + "\n")
    return {"proc_path": proc_path, "sys_net": tmp_path / "net"}


def test_reads_signal_level_in_dbm(tmp_path):
    assert wifi.read_signal_dbm("wlan0", **fake_system(tmp_path)) == -52.0


def test_link_down_reports_none_not_the_last_level(tmp_path):
    # /proc still carries -52 here; operstate says the link is gone.
    assert wifi.read_signal_dbm("wlan0", **fake_system(tmp_path, operstate="down")) is None


def test_missing_interface_reports_none(tmp_path):
    assert wifi.read_signal_dbm("wlan1", **fake_system(tmp_path)) is None


def test_interface_absent_from_proc_reports_none(tmp_path):
    header_only = "\n".join(PROC.splitlines()[:2]) + "\n"
    assert wifi.read_signal_dbm("wlan0", **fake_system(tmp_path, proc=header_only)) is None


def flags_for(signal):
    snapshot = {"gps_fix": True, "signal_dbm": signal}
    return protocol.compute_alert_flags(snapshot, protocol.DEFAULT_THRESHOLDS)


def bit(name: str) -> int:
    return 1 << protocol.ALERT_BITS[name]


def test_strong_signal_sets_no_signal_bits():
    assert flags_for(-52.0) & (bit("signal_warn") | bit("signal_crit")) == 0


def test_weak_signal_sets_warn():
    assert flags_for(-72.0) & bit("signal_warn")
    assert not flags_for(-72.0) & bit("signal_crit")


def test_very_weak_signal_sets_crit_only():
    assert flags_for(-85.0) & bit("signal_crit")
    assert not flags_for(-85.0) & bit("signal_warn")


def test_no_link_sets_crit():
    assert flags_for(None) & bit("signal_crit")


def test_signal_is_the_last_log_column(tmp_path):
    assert CSV_COLUMNS[-1] == "signal_dbm"
    path = tmp_path / "telemetry.log"
    log = TelemetryLog(path, protocol.DEFAULT_THRESHOLDS, period_ms=0)
    log.open()
    log.write({"seq": 1, "signal_dbm": -61.0})
    log.write({"seq": 2, "signal_dbm": None})
    log.close()

    _, strong, lost = path.read_text().splitlines()
    assert strong.split(",")[-1] == "-61"
    assert lost.split(",")[-1] == ""
