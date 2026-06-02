import json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "validate_newsletters.py"


def run(env=None):
    return subprocess.run([sys.executable, str(SCRIPT)],
                          capture_output=True, text=True, env=env)


def _env(tmp_path, registry):
    import os
    bad = tmp_path / "registry.json"
    bad.write_text(json.dumps(registry))
    e = dict(os.environ)
    e["NEWSLETTER_REGISTRY"] = str(bad)
    return e


def _base():
    return json.load(open(ROOT / "renderers/email/newsletters/registry.json"))


def test_real_registry_passes():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("OK"), r.stdout


def test_unknown_slot_fails(tmp_path):
    reg = _base()
    reg["newsletters"]["kitchen-station"]["slots"]["not-a-real-slot"] = "x"
    r = run(_env(tmp_path, reg))
    assert r.returncode == 1
    assert "not-a-real-slot" in r.stdout


def test_unknown_product_ref_fails(tmp_path):
    reg = _base()
    reg["newsletters"]["kitchen-station"]["product"] = "does-not-exist"
    r = run(_env(tmp_path, reg))
    assert r.returncode == 1
    assert "does-not-exist" in r.stdout


def test_unknown_hero_asset_fails(tmp_path):
    reg = _base()
    reg["newsletters"]["kitchen-station"]["heroAsset"] = "no-such-asset"
    r = run(_env(tmp_path, reg))
    assert r.returncode == 1
    assert "no-such-asset" in r.stdout


def test_missing_template_path_fails(tmp_path):
    reg = _base()
    reg["hubspot"].pop("templatePath", None)
    r = run(_env(tmp_path, reg))
    assert r.returncode == 1
    assert "templatePath" in r.stdout
