# -*- coding: utf-8 -*-
# __init__.py


from .structures import AddrMap, Pca
from .structures import P,C,A
from functools import lru_cache

VERSION = (0, 5, 1)

__version__ = ".".join([str(x) for x in VERSION])


def _data_rows():
    """现行数据优先，兼容历史地址；相同记录只加载一次。"""
    import csv
    from io import TextIOWrapper
    from pkg_resources import resource_stream

    seen = set()
    for filename in ('pca.csv', 'pca_legacy.csv'):
        with resource_stream('cpca.resources', filename) as stream:
            for row in csv.DictReader(TextIOWrapper(stream, encoding='utf8')):
                key = (row['sheng'], row['shi'], row['qu'])
                if key not in seen:
                    seen.add(key)
                    yield row


@lru_cache(maxsize=1)
def _alias_rows():
    import csv
    from io import TextIOWrapper
    from pkg_resources import resource_stream
    with resource_stream('cpca.resources', 'pca_aliases.csv') as stream:
        return tuple(csv.DictReader(TextIOWrapper(stream, encoding='utf8')))


def _data_from_csv() -> (AddrMap, AddrMap, AddrMap, dict):
    # 区名及其简写 -> 相关pca元组
    area_map = AddrMap()
    # 城市名及其简写 -> 相关pca元组
    city_map = AddrMap()
    # (省名全称, 区名全称) -> 相关pca元组
    province_area_map = AddrMap()
    # 省名 -> 省全名
    province_map = {}
    # 数据约定:国家直辖市的sheng字段为直辖市名称, 省直辖县的city字段为空
    for record_dict in _data_rows():
        _fill_province_map(province_map, record_dict)
        _fill_area_map(area_map, record_dict)
        _fill_city_map(city_map, record_dict)
        _fill_province_area_map(province_area_map, record_dict)

    for row in _alias_rows():
        pca = (row['sheng'], row['shi'], row['qu'])
        if row['level'] == 'city':
            city_map.append_relational_addr(row['alias'], pca, C)
        else:
            area_map.append_relational_addr(row['alias'], pca, A)

    return area_map, city_map, province_area_map, province_map


def _fill_province_area_map(province_area_map: AddrMap, record_dict):
    pca_tuple = (record_dict['sheng'], record_dict['shi'], record_dict['qu'])
    key = (record_dict['sheng'], record_dict['qu'])
    # 第三个参数在此处没有意义, 随便给的
    province_area_map.append_relational_addr(key, pca_tuple, P)


def _fill_area_map(area_map: AddrMap, record_dict):
    area_name = record_dict['qu']
    pca_tuple = (record_dict['sheng'], record_dict['shi'], record_dict['qu'])
    area_map.append_relational_addr(area_name, pca_tuple, A)
    # 单字简称（和县→和、凤县→凤）极易命中普通文字，只保留全名。
    if len(area_name) <= 2:
        return
    # 处理区名简写
    if area_name.endswith('市'):
        area_map.append_relational_addr(area_name[:-1], pca_tuple, A)
    elif area_name.endswith('区'):
        area_map.append_relational_addr(area_name[:-1], pca_tuple, A)
    elif area_name.endswith('县'):
        area_map.append_relational_addr(area_name[:-1], pca_tuple, A)
    elif area_name.endswith('镇'):
        area_map.append_relational_addr(area_name[:-1], pca_tuple, A)
    elif area_name.endswith('街道'):
        area_map.append_relational_addr(area_name[:-2], pca_tuple, A)


def _fill_city_map(city_map: AddrMap, record_dict):
    city_name = record_dict['shi']
    pca_tuple = (record_dict['sheng'], record_dict['shi'], record_dict['qu'])
    city_map.append_relational_addr(city_name, pca_tuple, C)
    if city_name.endswith('市'):
        city_map.append_relational_addr(city_name[:-1], pca_tuple, C)
    # 特别行政区
    elif city_name == '香港特别行政区':
        city_map.append_relational_addr('香港', pca_tuple, C)
    elif city_name == '澳门特别行政区':
        city_map.append_relational_addr('澳门', pca_tuple, C)
    

def _fill_province_map(province_map, record_dict):
    sheng = record_dict['sheng']
    if sheng not in province_map:
        province_map[sheng] = sheng
        # 处理省的简写情况
        # 普通省分 和 直辖市
        if sheng.endswith('省') or sheng.endswith('市'):
            province_map[sheng[:-1]] = sheng
        # 自治区
        elif sheng == '新疆维吾尔自治区':
            province_map['新疆'] = sheng
        elif sheng == '内蒙古自治区':
            province_map['内蒙古'] = sheng
        elif sheng == '广西壮族自治区':
            province_map['广西'] = sheng
            province_map['广西省'] = sheng
        elif sheng == '西藏自治区':
            province_map['西藏'] = sheng
        elif sheng == '宁夏回族自治区':
            province_map['宁夏'] = sheng
        # 特别行政区
        elif sheng == '香港特别行政区':
            province_map['香港'] = sheng
        elif sheng == '澳门特别行政区':
            province_map['澳门'] = sheng


area_map, city_map, province_area_map, province_map = _data_from_csv()

# 直辖市
munis = {'北京市', '天津市', '上海市', '重庆市'}


def is_munis(city_full_name):
    return city_full_name in munis


myumap = {
    '南关区': '长春市',
    '南山区': '深圳市',
    '宝山区': '上海市',
    '市辖区': '东莞市',
    '普陀区': '上海市',
    '朝阳区': '北京市',
    '河东区': '天津市',
    '白云区': '广州市',
    '西湖区': '杭州市',
    '铁西区': '沈阳市'
}


def transform(location_strs, umap=myumap, index=[], cut=True, lookahead=8, pos_sensitive=False, open_warning=True, include_status=True):
    """将地址描述字符串转换以"省","市","区"信息为列的DataFrame表格
        Args:
            locations:地址描述字符集合,可以是list, Series等任意可以进行for in循环的集合
                      比如:["徐汇区虹漕路461号58号楼5楼", "泉州市洛江区万安塘西工业区"]
            umap:自定义的区级到市级的映射，优先满足原文明确的省份约束；缺省使用内置映射并提示歧义
            index:可以通过这个参数指定输出的DataFrame的index,默认情况下是range(len(data))
            cut:是否使用分词，默认使用，分词模式速度较快，但是准确率可能会有所下降
            lookahead:只有在cut为false的时候有效，表示最多允许向前看的字符的数量
                      默认值为8是为了能够发现"新疆维吾尔族自治区"这样的长地名
                      如果你的样本中都是短地名的话，可以考虑把这个数字调小一点以提高性能
            pos_sensitive:如果为True则会多返回三列，分别提取出的省市区在字符串中的位置，如果字符串中不存在的话则显示-1
            open_warning: 是否打开umap警告, 默认打开
            include_status: 默认追加识别状态、说明、现行名称建议；False保持原有列结构
        Returns:
            一个Pandas的DataFrame类型的表格，如下：
               |省    |市   |区    |地址                 |
               |上海市|上海市|徐汇区|虹漕路461号58号楼5楼  |
               |福建省|泉州市|洛江区|万安塘西工业区        |
    """

    from collections.abc import Iterable

    if not isinstance(location_strs, Iterable):
        from .exceptions import InputTypeNotSuportException
        raise InputTypeNotSuportException(
            'location_strs参数必须为可迭代的类型(比如list, Series等实现了__iter__方法的对象)')

    import pandas as pd

    result = pd.DataFrame([_handle_one_record(addr, umap, cut, lookahead, pos_sensitive, open_warning) for addr in location_strs], index=index) \
             if index else pd.DataFrame([_handle_one_record(addr, umap, cut, lookahead, pos_sensitive, open_warning) for addr in location_strs])
    columns = ['省', '市', '区', '地址']
    if pos_sensitive:
        columns += ['省_pos', '市_pos', '区_pos']
    statuses = [_division_status(row) for row in result.to_dict('records')] if include_status else []
    result = result.reindex(columns=columns)
    if include_status:
        for i, column in enumerate(('识别状态', '说明', '现行名称建议')):
            result[column] = [status[i] for status in statuses]
    return result


@lru_cache(maxsize=1)
def _division_status_map():
    return {(row['sheng'], row['shi'], row['qu']):
            (row.get('status') or '现行名称', row.get('note', ''), row.get('current_name', ''))
            for row in _data_rows()}


def _division_status(row):
    """按完整省市区归属判断，不能仅凭同名区县宣称匹配正确。"""
    if isinstance(row.get('_ambiguity'), str) and row['_ambiguity']:
        return ('存在歧义', row['_ambiguity'], '')
    key = tuple(row.get(field, '') for field in ('省', '市', '区'))
    if all(isinstance(value, str) and value for value in key):
        status = _division_status_map().get(key)
        if status is not None:
            return status
    known = [(i, value) for i, value in enumerate(key)
             if isinstance(value, str) and value]
    if len(known) >= 2 and not any(
            all(candidate[i] == value for i, value in known)
            for candidate in _division_status_map()):
        return ('待核验', '识别出的行政层级互相矛盾，请核对原地址或自定义映射。', '')
    if not all(isinstance(value, str) and value for value in key):
        return ('未完整识别', '未取得完整省市区归属；不能据此判断名称是否现行。', '')
    return _division_status_map().get(
        key, ('待核验', '识别出的省市区组合不在数据表中，请核对地址或自定义映射。', ''))


def _handle_one_record(addr, umap, cut, lookahead, pos_sensitive, open_warning):
    """处理一条记录"""

    # 空记录
    if not isinstance(addr, str) or addr == '' or addr is None:
        empty = {'省': '', '市': '', '区': ''}
        if pos_sensitive:
            empty['省_pos'] = -1
            empty['市_pos'] = -1
            empty['区_pos'] = -1
        return empty

    # 地名提取
    pca, addr = _extract_addr(addr, cut, lookahead)

    ambiguity = ''
    if umap is myumap and not pca.city and pca.area and pca.area in area_map:
        candidates = sorted({r[C] for r in area_map.get_relational_addrs(pca.area)
                             if not pca.province or r[P] == pca.province})
        if len(candidates) > 1:
            ambiguity = '同名区候选城市：' + '、'.join(candidates) + '；请补充城市或传入 umap。'

    _fill_city(pca, umap, open_warning)

    _fill_province(pca)

    result = pca.propertys_dict(pos_sensitive)
    result["地址"] = addr
    if ambiguity:
        result['_ambiguity'] = ambiguity

    return result


def _fill_province(pca):
    """填充省"""
    if (not pca.province) and pca.city and (pca.city in city_map):
        pca.province = city_map.get_value(pca.city, P)


def _fill_city(pca, umap, open_warning):
    """填充市"""
    if not pca.city:
        # 显式省份先约束候选；默认/自定义映射均不能跨省强行补全。
        if pca.area and pca.province:
            key = (pca.province, pca.area)
            if key in province_area_map:
                if province_area_map.is_unique_value(key):
                    pca.city = province_area_map.get_value(key, C)
                else:
                    candidates = {r[C] for r in province_area_map.get_relational_addrs(key)}
                    if len(candidates) == 1:
                        pca.city = next(iter(candidates))
                    elif umap.get(pca.area) in candidates:
                        pca.city = umap[pca.area]
            return
        # 从 区 映射
        if pca.area:
            # 从umap中映射
            if umap.get(pca.area):
                pca.city = umap.get(pca.area)
                return
            if pca.area in area_map and area_map.is_unique_value(pca.area):
                pca.city = area_map.get_value(pca.area, C)
                return

        if open_warning:
            import logging
            logging.warning("%s 无法映射, 建议添加进umap中", pca.area)


def _extract_addr(addr, cut, lookahead):
    """提取地址中的省,市,区名称
       Args:
           addr:原始地址字符串
           cut: 是否分词
       Returns:
           [sheng, shi, qu, (sheng_pos, shi_pos, qu_pos)], addr
    """
    return _jieba_extract(addr) if cut else _full_text_extract(addr, lookahead)


@lru_cache(maxsize=1)
def _address_tokenizer():
    """独立词典避免修改调用方的全局 jieba 分词行为。"""
    import jieba
    tokenizer = jieba.Tokenizer()
    names = {row[field] for row in _data_rows()
             for field in ('sheng', 'shi', 'qu') if row[field]}
    names.update(row['alias'] for row in _alias_rows())
    for name in sorted(names):
        tokenizer.add_word(name, freq=100000)
    return tokenizer


def _address_match(word, addr, pos, result):
    """两种扫描方式共享上下文规则；返回字段和全名，不修改结果。"""
    import re

    if not word:
        return None
    tail = addr[pos + len(word):]
    is_full = (word in province_map and province_map[word] == word
               or word in city_map and city_map.get_full_name(word) == word
               or word in area_map and area_map.get_full_name(word) == word)
    # 山西北路、台湾风情街是道路名，而不是新的行政片段。
    if not is_full and re.match(r'^(?:[东西南北中]?(?:路|街|巷|大道|大街|胡同)|风情街)', tail):
        return None

    # 吉林/海南首先作为省简称，避免被同名城市、区抢先占用。
    area_province = (result.area and word in province_map
                     and any(r[P] == province_map[word]
                             for r in area_map.get_relational_addrs(result.area)))
    if (word in province_map and not result.province
            and (is_full or area_province or not (result.city or result.area))):
        full = province_map[word]
        return ('city', full) if is_munis(full) else ('province', full)
    # 朝阳北京等区在市前的写法：后续明确父级可以消解当前简称的层级歧义。
    next_parent = False
    if word in city_map and word in area_map:
        parents = area_map.get_relational_addrs(word)
        for n in range(2, min(len(tail), 12) + 1):
            following = tail[:n]
            if (following in city_map and any(r[C] == city_map.get_full_name(following) for r in parents)
                    or following in province_map and any(r[P] == province_map[following] for r in parents)):
                next_parent = True
                break
    if (word in city_map and not result.city and not next_parent
            and (word not in area_map or area_map.get_full_name(word) != word)):
        field, full = 'city', city_map.get_full_name(word)
    elif word in area_map and not result.area:
        field, full = 'area', area_map.get_full_name(word)
    elif word in city_map and not result.city:
        field, full = 'city', city_map.get_full_name(word)
    else:
        return None

    if result.area and not is_full:
        # 区在前时，只接受与该区归属一致的城市简称，防止正文污染。
        if field != 'city' or not any(r[C] == full for r in area_map.get_relational_addrs(result.area)):
            return None

    if word != full and not (result.province or result.city):
        # 无上级上下文的县区简称需独立出现或紧接一个行政名称。
        # 城市简称仍允许作为地址起点（如深圳南山）。
        if field == 'area' and tail.strip():
            has_next_division = any(
                tail[:n] in area_map or tail[:n] in city_map or tail[:n] in province_map
                for n in range(2, min(len(tail), 12) + 1))
            has_street = re.match(r'^[\u4e00-\u9fff]{1,8}(?:路|街|巷|大道|小区|园|开发区|村)', tail)
            if not (has_next_division or has_street):
                return None
    return field, full


def _jieba_extract(addr):
    """基于包含区划全名的结巴词典进行提取"""

    result = Pca()

    pos = 0
    truncate = 0

    def _set_pca(pca_property, name, full_name):
        """pca_property: 'province', 'city' or 'area'"""
        if not getattr(result, pca_property):
            setattr(result, pca_property, full_name)
            setattr(result, pca_property + "_pos", pos)
            if is_munis(full_name):
                setattr(result, "province_pos", pos)
            nonlocal truncate
            if pos == truncate:
                truncate += len(name)

    for word in _address_tokenizer().cut(addr):
        match = _address_match(word, addr, pos, result)
        if match:
            _set_pca(match[0], word, match[1])
        
        pos += len(word)

    return result, addr[truncate:]


def _full_text_extract(addr, lookahead):
    """全文匹配进行提取"""

    result = Pca()

    truncate = 0

    def _set_pca(pca_property, pos, name, full_name):
        """pca_property: 'province', 'city' or 'area'"""
        def _defer_set():
            if not getattr(result, pca_property):
                setattr(result, pca_property, full_name)
                setattr(result, pca_property + "_pos", pos)
                if is_munis(full_name):
                    setattr(result, "province_pos", pos)
                nonlocal truncate
                if pos == truncate:
                    truncate += len(name)
            return len(name)
        return _defer_set

    # i为起始位置
    i = 0
    while i < len(addr):
        # 用于设置pca属性的函数
        defer_fun = None
        token_length = 1
        # l为从起始位置开始的长度,从中提取出最长的地址
        for length in range(1, lookahead + 1):
            if i + length > len(addr):
                break
            word = addr[i:i + length]
            if word in province_map or word in city_map or word in area_map:
                token_length = length
                match = _address_match(word, addr, i, result)
                defer_fun = _set_pca(match[0], i, word, match[1]) if match else None

        if defer_fun:
            i += defer_fun()
        else:
            # 被上下文拒绝的完整地名也作为一个词跳过，不能再从内部误取津市等。
            i += token_length

    return result, addr[truncate:]
