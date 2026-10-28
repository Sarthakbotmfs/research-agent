from app.core.security import calculate_content_hash, is_safe_url


def test_is_safe_url_valid_https():
    safe, msg = is_safe_url("https://example.com/article/12345")
    assert safe is True


def test_is_safe_url_disallowed_schemes():
    safe, msg = is_safe_url("file:///etc/passwd")
    assert safe is False
    assert "disallowed scheme" in msg.lower()

    safe, msg = is_safe_url("gopher://127.0.0.1:70")
    assert safe is False

    safe, msg = is_safe_url("ftp://ftp.example.com/file.txt")
    assert safe is False


def test_is_safe_url_blocks_localhost():
    safe, msg = is_safe_url("http://localhost:8000/admin")
    assert safe is False
    assert "prohibited hostname" in msg.lower() or "blocked" in msg.lower()

    safe, msg = is_safe_url("http://127.0.0.1:5000/api")
    assert safe is False
    assert "blocked" in msg.lower()


def test_is_safe_url_blocks_private_networks():
    # 10.x.x.x
    safe, _ = is_safe_url("http://10.0.0.1/status")
    assert safe is False

    # 192.168.x.x
    safe, _ = is_safe_url("http://192.168.1.100/router")
    assert safe is False

    # 172.16.x.x
    safe, _ = is_safe_url("http://172.16.0.5:8080/")
    assert safe is False


def test_is_safe_url_blocks_cloud_metadata():
    safe, _ = is_safe_url("http://169.254.169.254/latest/meta-data/")
    assert safe is False

    safe, _ = is_safe_url("http://metadata.google.internal/computeMetadata/v1/")
    assert safe is False


def test_calculate_content_hash():
    text = "Empirical study on developer productivity."
    hash1 = calculate_content_hash(text)
    hash2 = calculate_content_hash(text)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length
