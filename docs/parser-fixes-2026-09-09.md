# 0.5.1 解析修复记录

本次落实上游筛查中的解析问题，不移植不适用本 fork 的 adcode/绘图补丁。

## 已落实与边界

| 上游问题 | 0.5.1 处理结果 | 验收例子 |
| --- | --- | --- |
| [#89](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/89) 省市同名简称 | 吉林/海南优先按省简称识别，城市简称优先于同名区简称 | 吉林通化市→吉林省/通化市；西安雁塔区→陕西省/西安市/雁塔区 |
| [#92](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/92)、[#39](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/39)、[#69](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/69) 道路干扰 | 简称紧接典型道路后缀时不作为区划；完整行政名不受此过滤 | 山西北路、四川北路、台湾风情街、合作路保留在详细地址中；朝阳区路家村仍可识别朝阳区 |
| [#125](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/125)、[#108](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/108)、[#88](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/88) 重名歧义 | 明确省份优先于 umap；默认映射存在多个候选时返回存在歧义和候选城市 | 吉林省朝阳区→长春；江苏省鼓楼区提示南京/徐州；单写朝阳区保留北京默认值并提示北京/长春 |
| [#46](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/46)、[#126](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/126) 普通文字误匹配 | 不生成单字县区简称；无省市上下文的县区简称需要后续行政名称或地址线索 | 合作共赢、经济和信息化厅、省经济合作局、和、凤北路不再误取合作市/和县/凤县 |
| [#56](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/56)、[#28](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/28) 层级校验 | 区为空时也核验已得到的省市组合；保留原识别结果并标待核验 | 青海师范大学成都校区不再仅提示未完整识别；没有实现机构真实地址查询 |
| [#105](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/105)、[#72](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/72)、[#106](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/106)、[#85](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/85) 简称 | 新增 10 条显式地址别名，覆盖已复现的简称；不是全部自治州/县简称 | 黔南、黔南州、西双版纳、西双版纳州、阿拉善、呼市、红河州、兰坪县、元江县、前郭县 |
| [#40](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/40)、[#58](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/58)、[#64](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/64) 历史名称 | 补充大厂区、梅列区，分别建议六合区、三元区；旧名仍原样返回 | 大厂区凤北路22号→南京市/大厂区/历史名称；梅列区→三明市/梅列区/历史名称 |

“存在歧义”在本库使用内置默认映射时出现；显式传入有效 umap 视为调用方已选择城市。umap 不能覆盖原文明确省份。提示不改变列数，`include_status=False` 仍保持原输出列结构。

区在市前、市在省前的旧输入顺序继续支持；正文中的地址位置仍相对原文计数，且不会截掉正文前缀。空格仍中断“连续地址前缀”的截断。

## 名称来源

别名表 `cpca/resources/pca_aliases.csv` 只保存地址识别映射；这里的“别名”不代表每个都是法定简称。目标全名与父级均核对现行数据表。

| 名称 | 依据 |
| --- | --- |
| 黔南/黔南州 | [州政府文件中的全名与黔南州](https://www.qiannan.gov.cn/zwgkztym/zrmzfbgs_085412/zfxxgk_06874/fdzdgknr_08954/zcwj_085412/202011/P020200923449921469770.pdf)；[税务地区简称表中黔南州/黔南](https://guangdong.chinatax.gov.cn/gdsw/zjfg/2011-02/23/content_783485c676b54d0e9c3e9975917375ca.shtml)，旧税务文件仅作别名使用证据 |
| 西双版纳/西双版纳州 | [云南省司法厅官方使用](https://sft.yn.gov.cn/pf/yunnan/ZhouFuPuFa/2023022930.shtml)，前者按官方行文中的地名代称作为地址别名，不声称查到法定简称声明 |
| 阿拉善 | [税务机关正文明确简称](https://neimenggu.chinatax.gov.cn/xwdt/mtsd/202106/t20210603_750672.html) |
| 呼市 | [湖南省工信厅正文明确简称](https://gxt.hunan.gov.cn/xxgk_71033/gzdt/rdjj/202307/t20230705_29392922.html) |
| 红河州 | [州发改委文件](https://www.hh.gov.cn/info/203592/1264482.htm) |
| 兰坪县 | [云南自然资源厅同篇标题简称与正文全名](https://dnr.yn.gov.cn/html/2017/zhengfucaigou_0907/12901.html) |
| 元江县 | [县政府管理办法](https://www.yjx.gov.cn/yjxzfxxgk/xxgfxwjjml1/20121113/1313906.html) |
| 前郭县 | [吉林省政府项目主体介绍](https://www.jl.gov.cn/szfzt/tzcj/zdxm/qcjlbj/202604/t20260423_3626301.html) |
| 大厂区合并入六合区 | [南京市政府城市沿革](https://www.nanjing.gov.cn/zzb/njgl/csgk/qhrk_72673/202509/t20250919_5653035.html) |
| 梅列区合并入三元区 | [福建省民政厅区划代码变更表](https://mzt.fujian.gov.cn/gk/tzgg/202109/t20210906_5682052.htm) |

## 验证与仍未做的事项

160 项测试通过，包含恢复一个原先因测试函数重名被覆盖的 lookahead 测试。对 3266 条现行/兼容区县名称分别构造“省+市+区”和“市+区”地址，每种匹配模式 6532 条，两种模式合计 13064 次；与 0.5.0 解析代码对比，旧版正确而新版错误的省市区组合为 0。这不是对真实地址总体准确率的统计。

仍未实现：全国历史区划全集、全国简称全集、多地点抽取、建筑物反查、无上下文普通词的完美判定、省直辖县统一层级重构。与普通词重合的名称仍可能误匹配，“现行名称”仍只证明返回组合存在，不能作为输入地址真实有效的证明。
