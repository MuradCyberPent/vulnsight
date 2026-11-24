from app.core.database import SessionLocal
from app.core.models import Finding, Scan, User
from tests.conftest import make_user


def test_register_validation(client):
    r = client.post("/api/auth/register", json={"username": "x", "email": "bad", "password": "short"})
    assert r.status_code == 422


def test_password_is_hashed(client):
    make_user(client, "hashy")
    db = SessionLocal()
    u = db.query(User).filter_by(username="hashy").first()
    assert u.password_hash.startswith("$2") and "password123" not in u.password_hash
    db.close()


def test_duplicate_user(client):
    make_user(client, "dupe")
    r = client.post("/api/auth/register", json={"username": "DUPE", "email": "other@example.com", "password": "password123"})
    assert r.status_code == 409


def test_login_lockout(client):
    make_user(client, "locky")
    for _ in range(5):
        assert client.post("/api/auth/login", data={"username": "locky", "password": "nope"}).status_code == 401
    # now locked, even with the right password
    assert client.post("/api/auth/login", data={"username": "locky", "password": "password123"}).status_code == 429


def test_requires_login(client):
    assert client.get("/api/scans").status_code == 401
    assert client.get("/api/scans", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_scope_guard_api(client):
    h = make_user(client, "scopey")
    no = client.post("/api/scans", json={"target": "8.8.8.8", "authorized": False}, headers=h)
    assert no.status_code == 400
    local = client.post("/api/scans", json={"target": "127.0.0.1", "authorized": True}, headers=h)
    assert local.status_code == 400 and "blocked" in local.json()["detail"]


def _scan(db, user_id, findings):
    s = Scan(user_id=user_id, target="example.com", resolved_ip="1.2.3.4", profile="quick", authorized=True,
             status="completed", risk_score=10)
    db.add(s)
    db.commit()
    for sev, key in findings:
        db.add(Finding(scan_id=s.id, category="Web", severity=sev, title=key, key=key))
    db.commit()
    return s.id


def test_isolation_and_compare(client):
    ha, hb = make_user(client, "alice"), make_user(client, "bob")
    db = SessionLocal()
    alice = db.query(User).filter_by(username="alice").first()
    s1 = _scan(db, alice.id, [("High", "a"), ("Low", "b")])
    s2 = _scan(db, alice.id, [("Low", "b"), ("Medium", "c")])
    db.close()

    # bob cannot see alice's scan
    assert client.get(f"/api/scans/{s1}", headers=hb).status_code == 404
    assert client.get(f"/api/scans/{s1}/report?format=txt", headers=hb).status_code == 404
    assert client.delete(f"/api/scans/{s1}", headers=hb).status_code == 404
    assert client.get("/api/scans", headers=hb).json() == []

    r = client.get(f"/api/scans/compare?a={s1}&b={s2}", headers=ha).json()
    assert [i["key"] for i in r["new"]] == ["c"]
    assert [i["key"] for i in r["fixed"]] == ["a"]
    assert [i["key"] for i in r["unchanged"]] == ["b"]


def test_admin_only(client):
    h = make_user(client, "plain")
    assert client.get("/api/admin/users", headers=h).status_code == 403
    db = SessionLocal()
    db.query(User).filter_by(username="plain").first().role = "admin"
    db.commit()
    db.close()
    assert client.get("/api/admin/users", headers=h).status_code == 200


def test_html_report_escapes(client):
    h = make_user(client, "xss")
    db = SessionLocal()
    uid = db.query(User).filter_by(username="xss").first().id
    sid = _scan(db, uid, [("Info", "k")])
    db.query(Finding).filter_by(scan_id=sid).first().details = "<script>alert(1)</script>"
    db.commit()
    db.close()
    html = client.get(f"/api/scans/{sid}/report?format=html", headers=h).text
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html
