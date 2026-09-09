import pytest

import cpca


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('address,status,suggestion', [
    ('中山市南朗街道人民路1号', '现行名称', ''),
    ('中山市南朗镇人民路1号', '历史名称', '南朗街道'),
    ('中山市民众镇人民路1号', '历史名称', '民众街道'),
    ('重庆市渝北区人民路1号', '历史名称', ''),
    ('重庆市江北区人民路1号', '历史名称', ''),
    ('宁波市江北区人民路1号', '现行名称', ''),
    ('儋州市国营蓝洋农场人民路1号', '地点名称', ''),
    ('东莞市松山湖人民路1号', '地点名称', ''),
    ('嘉峪关市镜铁区人民路1号', '历史管理名称', ''),
    ('嘉峪关市第一街道人民路1号', '待核验', ''),
    ('上海市渝北区人民路1号', '待核验', ''),
    ('完全未知的地址', '未完整识别', ''),
    ('', '未完整识别', ''),
])
def test_division_status(address, status, suggestion, cut):
    row = cpca.transform([address], cut=cut).iloc[0]
    assert row['识别状态'] == status
    assert row['现行名称建议'] == suggestion
    if status != '现行名称':
        assert row['说明']


def test_status_can_be_disabled_for_existing_consumers():
    assert list(cpca.transform(['南朗镇'], include_status=False).columns) == ['省', '市', '区', '地址']


def test_status_preserves_positions_and_original_name():
    row = cpca.transform(['中山市南朗镇人民路1号'], pos_sensitive=True).iloc[0]
    assert row['区'] == '南朗镇'
    assert row['区_pos'] == 3
    assert row['识别状态'] == '历史名称'


def test_empty_batch_has_schema():
    result = cpca.transform([])
    assert result.empty
    assert '识别状态' in result.columns
