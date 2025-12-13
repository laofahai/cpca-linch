#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 xiangyuecn/AreaCity-JsSpider-StatsGov 的数据转换为 cpca 项目所需的格式

数据源: https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov
下载地址: https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov/releases

使用方法:
1. 下载 ok_data_level3-4.csv.7z 并解压
2. 将 ok_data_level3.csv 和 ok_data_level4.csv 放到本脚本同目录
3. 运行: python3 convert_data.py
4. 生成的 pca_new.csv 替换 cpca/resources/pca.csv
"""

import csv
import os
import subprocess
import sys
import urllib.request
import tempfile


DATA_URL = "https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov/releases/download/2023.240319.250114/ok_data_level3-4.csv.7z"

# 不设区的地级市（直筒子市），需要把镇街作为区级处理
# https://zh.wikipedia.org/wiki/不设区的市_(地级市)
DIRECT_CITIES = {
    '东莞市': '广东省',
    '中山市': '广东省',
    '儋州市': '海南省',
    '嘉峪关市': '甘肃省',
}


def download_and_extract():
    """下载并解压最新数据"""
    print("下载数据...")
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "data.7z")

    try:
        urllib.request.urlretrieve(DATA_URL, zip_path)
        print(f"  下载完成: {zip_path}")
    except Exception as e:
        print(f"  下载失败: {e}")
        print(f"  请手动下载: {DATA_URL}")
        return None, None

    print("解压数据...")
    try:
        subprocess.run(["7z", "x", zip_path, f"-o{temp_dir}"], check=True, capture_output=True)
        csv3_path = os.path.join(temp_dir, "ok_data_level3.csv")
        csv4_path = os.path.join(temp_dir, "ok_data_level4.csv")
        if os.path.exists(csv3_path) and os.path.exists(csv4_path):
            print(f"  解压完成")
            return csv3_path, csv4_path
    except FileNotFoundError:
        print("  错误: 需要安装 7z 命令")
        print("  Ubuntu/Debian: sudo apt install p7zip-full")
        print("  macOS: brew install p7zip")
    except Exception as e:
        print(f"  解压失败: {e}")

    return None, None


def load_level_data(filepath):
    """加载行政区划层级数据"""
    data = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[int(row['id'])] = {
                'id': int(row['id']),
                'pid': int(row['pid']),
                'deep': int(row['deep']),
                'name': row['name'],
                'ext_name': row['ext_name']
            }
    return data


def get_parent_chain(data, item_id):
    """获取父级链条，返回 ext_name 列表"""
    chain = []
    current_id = item_id
    while current_id in data:
        item = data[current_id]
        chain.append(item['ext_name'])
        if item['pid'] == 0:
            break
        current_id = item['pid']
    return list(reversed(chain))


def convert_to_pca(level3_data, level4_data, output_path):
    """转换为 pca.csv 格式（无经纬度）"""
    results = []

    # 处理三级数据（省市区）
    for item_id, item in level3_data.items():
        deep = item['deep']
        chain = get_parent_chain(level3_data, item_id)

        # 跳过省级（deep=0）
        if deep == 0:
            continue

        if deep == 1:
            # 市级
            sheng = chain[0] if len(chain) > 0 else ''
            shi = chain[1] if len(chain) > 1 else ''
            qu = ''
            # 直辖市特殊处理
            if sheng in ['北京市', '天津市', '上海市', '重庆市']:
                shi = sheng
            results.append({'country': '中国', 'sheng': sheng, 'shi': shi, 'qu': qu})

        elif deep == 2:
            # 区县级
            sheng = chain[0] if len(chain) > 0 else ''
            shi = chain[1] if len(chain) > 1 else ''
            qu = chain[2] if len(chain) > 2 else ''
            # 直辖市特殊处理
            if sheng in ['北京市', '天津市', '上海市', '重庆市']:
                shi = sheng
            # 跳过区名和市名相同的记录（直筒子市）
            if qu == shi:
                continue
            results.append({'country': '中国', 'sheng': sheng, 'shi': shi, 'qu': qu})

    # 处理四级数据中的直筒子市镇街
    for item_id, item in level4_data.items():
        deep = item['deep']

        # 只处理 deep=3 的镇街数据
        if deep != 3:
            continue

        chain = get_parent_chain(level4_data, item_id)
        if len(chain) < 4:
            continue

        sheng = chain[0]
        shi = chain[1]
        # chain[2] 是虚拟的区级（和市同名），跳过
        zhen = chain[3]

        # 只处理直筒子市的镇街
        if shi in DIRECT_CITIES and DIRECT_CITIES[shi] == sheng:
            results.append({'country': '中国', 'sheng': sheng, 'shi': shi, 'qu': zhen})

    # 按省市区排序
    results.sort(key=lambda x: (x['sheng'], x['shi'], x['qu']))

    # 写入 CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['country', 'sheng', 'shi', 'qu']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return len(results)


def main():
    # 检查是否有本地数据文件
    csv3_path = 'ok_data_level3.csv'
    csv4_path = 'ok_data_level4.csv'

    if not os.path.exists(csv3_path) or not os.path.exists(csv4_path):
        print("未找到本地数据文件，尝试下载...")
        csv3_path, csv4_path = download_and_extract()
        if not csv3_path or not csv4_path:
            print("\n请手动下载数据:")
            print(f"  1. 访问 {DATA_URL}")
            print("  2. 解压得到 ok_data_level3.csv 和 ok_data_level4.csv")
            print("  3. 将文件放到本脚本同目录")
            print("  4. 重新运行本脚本")
            sys.exit(1)

    print("加载三级行政区划数据...")
    level3_data = load_level_data(csv3_path)
    print(f"  共 {len(level3_data)} 条记录")

    print("加载四级行政区划数据...")
    level4_data = load_level_data(csv4_path)
    print(f"  共 {len(level4_data)} 条记录")

    print("转换数据...")
    output_path = 'pca_new.csv'
    count = convert_to_pca(level3_data, level4_data, output_path)
    print(f"  输出 {count} 条记录到 {output_path}")

    # 统计
    stats3 = {0: 0, 1: 0, 2: 0}
    for item in level3_data.values():
        stats3[item['deep']] = stats3.get(item['deep'], 0) + 1

    # 统计直筒子市镇街数量
    direct_city_towns = 0
    for item in level4_data.values():
        if item['deep'] == 3:
            chain = get_parent_chain(level4_data, item['id'])
            if len(chain) >= 2:
                shi = chain[1]
                sheng = chain[0]
                if shi in DIRECT_CITIES and DIRECT_CITIES[shi] == sheng:
                    direct_city_towns += 1

    print(f"\n统计:")
    print(f"  省级: {stats3[0]} 个")
    print(f"  市级: {stats3[1]} 个")
    print(f"  区县级: {stats3[2]} 个")
    print(f"  直筒子市镇街: {direct_city_towns} 个")

    print(f"\n完成! 请将 {output_path} 复制到 cpca/resources/pca.csv")


if __name__ == '__main__':
    main()
