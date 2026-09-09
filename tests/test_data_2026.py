"""Regression cases for the 2026 data refresh and reproducible conversion."""
import csv
from pathlib import Path

import pytest

import cpca
from scripts.update_pca_data import convert_to_pca


@pytest.mark.parametrize("cut", [False, True])
@pytest.mark.parametrize("city,area", [
    ("和田地区", "和安县"),
    ("和田地区", "和康县"),
    ("喀什地区", "岑岭县"),
    ("重庆市", "两江新区"),
])
def test_new_divisions(city, area, cut):
    province = "重庆市" if city == "重庆市" else "新疆维吾尔自治区"
    address = city + area + "人民路1号"
    result = cpca.transform([address], cut=cut).iloc[0]
    assert (result["省"], result["市"], result["区"]) == (province, city, area)
    assert result["地址"] == "人民路1号"


def test_current_data_has_no_duplicates_or_retired_chongqing_districts():
    with Path("cpca/resources/pca.csv").open(encoding="utf-8") as f:
        rows = [tuple(row.values()) for row in csv.DictReader(f)]
    assert len(rows) == len(set(rows))
    assert ("中国", "重庆市", "重庆市", "江北区") not in rows
    assert ("中国", "重庆市", "重庆市", "渝北区") not in rows
    assert ("中国", "浙江省", "宁波市", "江北区") in rows


def test_converter_adds_official_supplements_idempotently(tmp_path):
    province = {"id": 65, "pid": 0, "deep": 0,
                "name": "新疆", "ext_name": "新疆维吾尔自治区"}
    city = {"id": 6532, "pid": 65, "deep": 1,
            "name": "和田", "ext_name": "和田地区"}
    county = {"id": 653228, "pid": 6532, "deep": 2,
              "name": "和康", "ext_name": "和康县"}
    source = {r["id"]: r for r in [province, city, county]}
    output = tmp_path / "pca.csv"
    convert_to_pca(source, {}, output)
    with output.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert sum(r["qu"] == "和康县" for r in rows) == 1
    assert sum(r["qu"] == "和安县" for r in rows) == 1
    assert sum(r["qu"] == "岑岭县" for r in rows) == 1


@pytest.mark.parametrize("city,area", [
    ("中山市", "沙溪镇"), ("东莞市", "南城街道"),
    ("儋州市", "那大镇"), ("嘉峪关市", "新城镇"),
])
def test_direct_city_towns_preserved(city, area):
    result = cpca.transform([city + area + "人民路1号"], cut=False).iloc[0]
    assert (result["市"], result["区"]) == (city, area)


@pytest.mark.parametrize("cut", [False, True])
@pytest.mark.parametrize("province,city,area", [
    ("重庆市", "重庆市", "江北区"),
    ("重庆市", "重庆市", "渝北区"),
    ("广东省", "中山市", "南朗镇"),
    ("广东省", "东莞市", "松山湖"),
    ("海南省", "儋州市", "洋浦经济开发区"),
])
def test_legacy_addresses_keep_original_names(province, city, area, cut):
    result = cpca.transform([city + area + "人民路1号"], cut=cut).iloc[0]
    assert (result["省"], result["市"], result["区"]) == (province, city, area)
    assert result["地址"] == "人民路1号"
