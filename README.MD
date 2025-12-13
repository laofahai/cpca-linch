# cpca-linch

一个用于从简体中文地址字符串中提取省、市、区信息的 Python 模块。

```python
import cpca

df = cpca.transform(["徐汇区虹漕路461号58号楼5楼", "广东省中山市沙溪镇云汉轻纺城"])
print(df)
```

输出：

```
     省    市    区              地址
0  上海市  上海市  徐汇区  虹漕路461号58号楼5楼
1  广东省  中山市  沙溪镇       云汉轻纺城
```

## 安装

```bash
pip install cpca-linch
```

## 项目来源

本项目 fork 自 [DQinYuan/chinese_province_city_area_mapper](https://github.com/DQinYuan/chinese_province_city_area_mapper)，感谢原作者的贡献。

### 主要改进

1. **更新行政区划数据至 2025 年最新版本**
   - 数据来源：[xiangyuecn/AreaCity-JsSpider-StatsGov](https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov)
   - 原数据为 2019 年版本，已严重过时

2. **支持不设区的地级市（直筒子市）的镇街识别**
   - 东莞市、中山市、儋州市、嘉峪关市的镇街现在可以作为区级识别
   - 例如：`中山市沙溪镇` 可正确识别

3. **移除经纬度数据**
   - 简化数据结构，减少包体积

## 数据更新

项目提供了数据更新脚本 `scripts/update_pca_data.py`，可用于后续更新行政区划数据：

```bash
cd scripts
python update_pca_data.py
# 生成的 pca_new.csv 替换 cpca/resources/pca.csv
```

## 使用方法

### 基本用法

```python
import cpca

location_str = ["徐汇区虹漕路461号58号楼5楼", "泉州市洛江区万安塘西工业区", "朝阳区北苑华贸城"]
df = cpca.transform(location_str)
print(df)
```

### 全文模式（更准确）

```python
df = cpca.transform(location_str, cut=False)
```

### 处理重名区县

中国存在重名的区县（如"朝阳区"在北京和长春都有），可通过 `umap` 参数指定映射：

```python
df = cpca.transform(["鼓楼区软件大道89号"], umap={"鼓楼区": "南京市"})
```

### 获取位置信息

```python
df = cpca.transform(location_str, pos_sensitive=True)
# 返回额外的 省_pos, 市_pos, 区_pos 列
```

## 数据接口

```python
from cpca import area_map, city_map, province_area_map

# 查询含有"鼓楼区"的全部地址
area_map.get_relational_addrs('鼓楼区')
# [('江苏省', '南京市', '鼓楼区'), ('江苏省', '徐州市', '鼓楼区'), ...]

# 查询含有"江苏省"和"鼓楼区"的全部地址
province_area_map.get_relational_addrs(('江苏省', '鼓楼区'))
# [('江苏省', '南京市', '鼓楼区'), ('江苏省', '徐州市', '鼓楼区')]
```

## License

MIT
