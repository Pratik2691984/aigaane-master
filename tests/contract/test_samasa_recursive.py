import pytest
from engine import parse
import _samasa

def test_depth_3_tatpurusa_samasa_module():
    # Test _samasa module directly
    node = _samasa.recursive_split_compound("rājaputravadha")
    assert node is not None
    assert node["surface"] == "rājaputravadha"
    assert "components" in node
    assert node["left_stem"] in ["raja", "rāja"]
    assert "putravadha" in node["right_stem"]
    # Check depth-2/3 recursive branch
    assert node["sub_tree"] is not None
    assert node["sub_tree"]["left_stem"] == "putra"

def test_depth_3_parse_integration():
    # End-to-end parse via engine
    doc = parse("rājaputravadha")
    assert doc is not None
    assert doc["schema_version"] == "0.2.0"
    assert len(doc["tokens"]) >= 1
    assert doc["confidence"] > 0.0
