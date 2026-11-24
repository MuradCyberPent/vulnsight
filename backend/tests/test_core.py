import pytest

from app.modules.scanning.checks.cve import is_affected, detect_software
from app.modules.scanning.checks.ports import parse_ports
from app.modules.users.scan_permission import ScopeError, normalize_target, validate_target
from app.modules.analysis.scoring import compute_risk


def f(sev):
    return {"severity": sev}


def test_scoring_levels():
    assert compute_risk([]) == (0, "Low")
    assert compute_risk([f("Low")] * 3)[1] == "Low"
    assert compute_risk([f("Critical")])[1] == "High"           # one critical is never "Low"
    assert compute_risk([f("Critical")] * 2)[1] == "Critical"
    assert compute_risk([f("Critical")] * 10)[0] == 100          # capped


def test_version_compare():
    assert is_affected("7.2", "0", "7.8")
    assert not is_affected("7.8", "0", "7.8")
    assert is_affected("2.4.49", "2.4.49", "2.4.51")
    assert not is_affected("2.4.48", "2.4.49", "2.4.51")
    assert is_affected("9.7", "8.5", "9.8")
    assert not is_affected("9.8", "8.5", "9.8")


def test_detect_software():
    found = detect_software([("x", "Server: nginx/1.18.0"), ("y", "SSH-2.0-OpenSSH_8.9p1")])
    assert found == {"nginx": "1.18.0", "OpenSSH": "8.9"}


def test_parse_ports():
    assert parse_ports("22,80,100-102", 100) == [22, 80, 100, 101, 102]
    for bad in ("abc", "0", "70000", "1-5000"):
        with pytest.raises(ValueError):
            parse_ports(bad, 2000)


def test_normalize_target():
    assert normalize_target("https://Example.com:8443/a/b") == "example.com"
    assert normalize_target("example.com/path") == "example.com"
    assert normalize_target("10.0.0.5:22") == "10.0.0.5"


def test_scope_guard():
    for bad in ("127.0.0.1", "192.168.1.5", "10.0.0.1", "localhost", "169.254.169.254", "224.0.0.1", "not a host!"):
        with pytest.raises(ScopeError):
            validate_target(bad, allow_private=False)
    assert validate_target("127.0.0.1", allow_private=True)["ip"] == "127.0.0.1"
    with pytest.raises(ScopeError):  # cloud metadata is blocked even in lab mode
        validate_target("169.254.169.254", allow_private=True)
    assert validate_target("8.8.8.8", allow_private=False)["is_ip"]
