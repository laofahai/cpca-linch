"""Public-interface regressions reproduced from upstream issues."""
import pytest

import cpca


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('text,expected,detail', [
    ('吉林通化市东昌区江南大街', ('吉林省', '通化市', '东昌区'), '江南大街'),
    ('吉林省朝阳区人民路1号', ('吉林省', '长春市', '朝阳区'), '人民路1号'),
    ('上海市山西北路1号', ('上海市', '上海市', ''), '山西北路1号'),
    ('上海市虹口区四川北路1号', ('上海市', '上海市', '虹口区'), '四川北路1号'),
    ('启东市台湾风情街', ('江苏省', '南通市', '启东市'), '台湾风情街'),
    ('海南万宁市人民路1号', ('海南省', '万宁市', ''), '人民路1号'),
    ('安徽省和县人民路1号', ('安徽省', '马鞍山市', '和县'), '人民路1号'),
    ('甘肃省合作市人民路1号', ('甘肃省', '甘南藏族自治州', '合作市'), '人民路1号'),
    ('深圳南山科技园', ('广东省', '深圳市', '南山区'), '科技园'),
    ('西安雁塔区人民路1号', ('陕西省', '西安市', '雁塔区'), '人民路1号'),
    ('上海市南京西路1号', ('上海市', '上海市', ''), '南京西路1号'),
    ('合肥市和平路1号', ('安徽省', '合肥市', ''), '和平路1号'),
    ('四川省成都市合作路1号', ('四川省', '成都市', ''), '合作路1号'),
    ('启东台湾风情街1号', ('江苏省', '南通市', '启东市'), '台湾风情街1号'),
    ('朝阳区长春市人民路1号', ('吉林省', '长春市', '朝阳区'), '人民路1号'),
    ('北京市朝阳区路家村1号', ('北京市', '北京市', '朝阳区'), '路家村1号'),
    ('河北省新乐市东路村1号', ('河北省', '石家庄市', '新乐市'), '东路村1号'),
    ('南山科技园1号', ('广东省', '深圳市', '南山区'), '科技园1号'),
    ('徐汇漕河泾开发区1号', ('上海市', '上海市', '徐汇区'), '漕河泾开发区1号'),
    ('西安市陕西省雁塔区人民路1号', ('陕西省', '西安市', '雁塔区'), '人民路1号'),
    ('朝阳北京望京1号', ('北京市', '北京市', '朝阳区'), '望京1号'),
])
def test_hierarchical_address_parsing(text, expected, detail, cut):
    row = cpca.transform([text], cut=cut, pos_sensitive=True).iloc[0]
    assert tuple(row[k] for k in ('省', '市', '区')) == expected
    assert row['地址'] == detail


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('text', ['合作共赢', '经济和信息化厅、省经济合作局', '凤北路22号', '和'])
def test_no_short_alias_in_ordinary_text(text, cut):
    row = cpca.transform([text], cut=cut, open_warning=False).iloc[0]
    assert row['区'] == ''
    assert row['地址'] == text


@pytest.mark.parametrize('cut', [True, False])
def test_province_restricts_custom_mapping(cut):
    row = cpca.transform(['吉林省朝阳区'], umap={'朝阳区': '北京市'}, cut=cut).iloc[0]
    assert (row['省'], row['市'], row['区']) == ('吉林省', '长春市', '朝阳区')


@pytest.mark.parametrize('cut', [True, False])
def test_embedded_address_positions(cut):
    text = '地址是吉林通化市东昌区江南大街'
    row = cpca.transform([text], cut=cut, pos_sensitive=True).iloc[0]
    assert (row['省'], row['市'], row['区']) == ('吉林省', '通化市', '东昌区')
    assert (row['省_pos'], row['市_pos'], row['区_pos']) == (3, 5, 8)
    assert row['地址'] == text


def test_partial_hierarchy_conflict_is_flagged():
    row = cpca.transform(['青海师范大学成都校区']).iloc[0]
    assert row['识别状态'] == '待核验'


@pytest.mark.parametrize('cut', [True, False])
def test_space_stops_prefix_truncation(cut):
    row = cpca.transform(['江苏省南京市 鼓楼区人民路1号'], cut=cut, pos_sensitive=True).iloc[0]
    assert row['区'] == '鼓楼区'
    assert row['区_pos'] == 7
    assert row['地址'] == ' 鼓楼区人民路1号'


def test_repeated_city_is_not_scanned_from_inside():
    row = cpca.transform(['天津市天津市和平区人民路1号'], cut=False).iloc[0]
    assert (row['省'], row['市'], row['区']) == ('天津市', '天津市', '和平区')


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('text,expected', [
    ('黔南都匀市人民路1号', ('贵州省', '黔南布依族苗族自治州', '都匀市')),
    ('西双版纳景洪市人民路1号', ('云南省', '西双版纳傣族自治州', '景洪市')),
    ('阿拉善阿拉善左旗人民路1号', ('内蒙古自治区', '阿拉善盟', '阿拉善左旗')),
    ('呼市新城区人民路1号', ('内蒙古自治区', '呼和浩特市', '新城区')),
    ('云南红河州蒙自市人民路1号', ('云南省', '红河哈尼族彝族自治州', '蒙自市')),
    ('兰坪县人民路1号', ('云南省', '怒江傈僳族自治州', '兰坪白族普米族自治县')),
    ('元江县人民路1号', ('云南省', '玉溪市', '元江哈尼族彝族傣族自治县')),
    ('前郭县人民路1号', ('吉林省', '松原市', '前郭尔罗斯蒙古族自治县')),
])
def test_reviewed_aliases(text, expected, cut):
    row = cpca.transform([text], cut=cut).iloc[0]
    assert tuple(row[k] for k in ('省', '市', '区')) == expected
    assert row['地址'] == '人民路1号'


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('text,city,area,current', [
    ('大厂区凤北路22号', '南京市', '大厂区', '六合区'),
    ('梅列区人民路1号', '三明市', '梅列区', '三元区'),
])
def test_reviewed_historical_names(text, city, area, current, cut):
    row = cpca.transform([text], cut=cut).iloc[0]
    assert (row['市'], row['区']) == (city, area)
    assert row['识别状态'] == '历史名称'
    assert row['现行名称建议'] == current


def test_default_mapping_discloses_ambiguity():
    row = cpca.transform(['朝阳区人民路1号']).iloc[0]
    assert row['市'] == '北京市'  # 保留已有默认输出，但不再伪装成确定结果。
    assert row['识别状态'] == '存在歧义'
    assert '北京市' in row['说明'] and '长春市' in row['说明']


def test_province_narrows_ambiguity_candidates():
    row = cpca.transform(['江苏省鼓楼区人民路1号']).iloc[0]
    assert row['市'] == ''
    assert row['识别状态'] == '存在歧义'
    assert '南京市' in row['说明'] and '徐州市' in row['说明']
    assert '福州市' not in row['说明']


def test_explicit_valid_mapping_resolves_ambiguity():
    row = cpca.transform(['江苏省鼓楼区'], umap={'鼓楼区': '南京市'}).iloc[0]
    assert row['市'] == '南京市'
    assert row['识别状态'] == '现行名称'


def test_alias_targets_exist_in_current_data():
    current = {(r['sheng'], r['shi'], r['qu']) for r in cpca._data_rows()}
    for row in cpca._alias_rows():
        assert (row['sheng'], row['shi'], row['qu']) in current


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('text,expected,detail,positions', [
    ('黑龙江省西安人民路1号', ('黑龙江省', '牡丹江市', '西安区'), '人民路1号', (0, -1, 4)),
    ('江苏省新北人民路1号', ('江苏省', '常州市', '新北区'), '人民路1号', (0, -1, 3)),
    ('湖南省资阳人民路1号', ('湖南省', '益阳市', '资阳区'), '人民路1号', (0, -1, 3)),
    ('朝阳 北京市望京1号', ('北京市', '北京市', '朝阳区'), ' 北京市望京1号', (3, 3, 0)),
    ('朝阳-北京市望京1号', ('北京市', '北京市', '朝阳区'), '-北京市望京1号', (3, 3, 0)),
    ('台州路桥区人民路1号', ('浙江省', '台州市', '路桥区'), '人民路1号', (-1, 0, 2)),
    ('西安市陕西雁塔区人民路1号', ('陕西省', '西安市', '雁塔区'), '人民路1号', (3, 0, 5)),
])
def test_review_hierarchy_regressions(text, expected, detail, positions, cut):
    row = cpca.transform([text], cut=cut, pos_sensitive=True).iloc[0]
    assert tuple(row[k] for k in ('省', '市', '区')) == expected
    assert row['地址'] == detail
    assert tuple(row[k] for k in ('省_pos', '市_pos', '区_pos')) == positions
    assert row['识别状态'] == '现行名称'


@pytest.mark.parametrize('cut', [True, False])
@pytest.mark.parametrize('text,detail', [
    ('辽宁省朝阳 北京路1号', ' 北京路1号'),
    ('朝阳 北京路1号', ' 北京路1号'),
])
def test_reverse_parent_lookahead_does_not_use_road_name(text, detail, cut):
    row = cpca.transform([text], cut=cut).iloc[0]
    assert (row['省'], row['市'], row['区']) == ('辽宁省', '朝阳市', '')
    assert row['地址'] == detail
    assert row['识别状态'] == '未完整识别'
