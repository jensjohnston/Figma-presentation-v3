#!/usr/bin/env python3
"""Tests for tools/validate_assets.py — fixture-driven via ASSETS_LIBRARY env var."""
import json, os, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "validate_assets.py"


def run(env=None):
    return subprocess.run([sys.executable, str(SCRIPT)],
                          capture_output=True, text=True, env=env)


def _env(tmp_path, library, prefs=None):
    lib = tmp_path / "library.json"
    lib.write_text(json.dumps(library))
    e = dict(os.environ)
    e["ASSETS_LIBRARY"] = str(lib)
    p = tmp_path / "preferences.json"
    if prefs is not None:
        p.write_text(json.dumps(prefs))
    e["ASSETS_PREFERENCES"] = str(p)  # points at a missing file when prefs is None
    return e


def _good_asset():
    return {
        "nodeId": "1:1",
        "tags": ["product", "purifier"],
        "description": "Spirit purifier front view on white",
        "source": {"type": "figma"},
        "visual": {
            "aspect": 1.5, "orientation": "landscape", "tone": "light",
            "subject": "center", "suitability": ["card", "hero"], "quality": "high",
        },
    }


def _base():
    return {"assetPageId": "51124:14", "assetPageName": "Brand Assets",
            "assets": {"spirit-front": _good_asset()}}


def test_good_library_passes(tmp_path):
    r = run(_env(tmp_path, _base()))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("OK"), r.stdout


def test_missing_visual_fails(tmp_path):
    lib = _base()
    del lib["assets"]["spirit-front"]["visual"]
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "visual" in r.stdout


def test_missing_source_fails(tmp_path):
    lib = _base()
    del lib["assets"]["spirit-front"]["source"]
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "source" in r.stdout


def test_bad_tone_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["tone"] = "bright"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "tone" in r.stdout


def test_orientation_aspect_mismatch_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["orientation"] = "portrait"  # aspect 1.5
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "orientation" in r.stdout


def test_empty_suitability_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["suitability"] = []
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "suitability" in r.stdout


def test_duplicate_nodeid_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-side"] = _good_asset()  # same nodeId "1:1"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "duplicate nodeId" in r.stdout


def test_unknown_source_type_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["source"]["type"] = "dropbox"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "source.type" in r.stdout


def test_corrupt_orientation_reports_once(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["orientation"] = "sideways"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert r.stdout.count("orientation") == 1


def test_empty_visual_dict_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"] = {}
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "aspect" in r.stdout


def test_real_library_passes():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("OK"), r.stdout


def _good_prefs():
    return {
        "imagePicks": [
            {"context": {"role": "hero", "topic": "spirit purifier", "slot": "full-bleed"},
             "chosen": "spirit-front", "rejected": [], "date": "2026-06-11"}
        ],
        "templatePicks": [
            {"context": {"contentShape": "4 items, image-rich", "deck": "demo"},
             "chosen": "template-bento4", "rejected": ["pillar-grid-4up-image"],
             "date": "2026-06-11"}
        ],
    }


def test_good_preferences_pass(tmp_path):
    r = run(_env(tmp_path, _base(), prefs=_good_prefs()))
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_preferences_file_passes(tmp_path):
    r = run(_env(tmp_path, _base()))  # prefs=None -> env points at missing file
    assert r.returncode == 0, r.stdout + r.stderr


def test_unknown_image_pick_fails(tmp_path):
    prefs = _good_prefs()
    prefs["imagePicks"][0]["chosen"] = "no-such-asset"
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 1
    assert "no-such-asset" in r.stdout


def test_unknown_template_pick_fails(tmp_path):
    prefs = _good_prefs()
    prefs["templatePicks"][0]["chosen"] = "template-does-not-exist"
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 1
    assert "template-does-not-exist" in r.stdout


def test_custom_template_pick_passes(tmp_path):
    prefs = _good_prefs()
    prefs["templatePicks"][0]["chosen"] = "custom"  # escape-hatch builds log as "custom"
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 0, r.stdout + r.stderr


def test_null_image_picks_passes(tmp_path):
    prefs = _good_prefs()
    prefs["imagePicks"] = None
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_chosen_fails_clearly(tmp_path):
    prefs = _good_prefs()
    del prefs["imagePicks"][0]["chosen"]
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 1
    assert "missing 'chosen'" in r.stdout
