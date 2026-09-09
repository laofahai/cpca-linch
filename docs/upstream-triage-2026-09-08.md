# 原项目 issues / PR 筛查

检查日期：2026-09-08。对象：[DQinYuan/chinese_province_city_area_mapper](https://github.com/DQinYuan/chinese_province_city_area_mapper)。

扫描 118 个 issue 索引（71 open、47 closed），重点读取高相关正文和评论，进行 53 条地址 × 两种模式的定向复现；没有逐个核验所有图片附件。扫描全部 15 个 PR（8 open、4 closed、3 merged），深入查看 #133、#124、#103 差异及 #99 文件范围。本轮仅分析上游，不替上游发评论、开 issue 或合并 PR。

本 fork 使用 jieba / 全文扫描和省市区名称表；上游部分 PR 面向 adcodes / Aho-Corasick 实现，不能直接合并。本报告中的“已覆盖”只指列出的具体用例。

## 建议优先处理

| 顺序 | 问题与来源 | 本 fork 的复现证据 | 建议处理 |
| --- | --- | --- | --- |
| 1 | 省市层级冲突：[吉林简称 #89](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/89) | 两模式中“吉林通化市东昌区江南大街”均得到吉林省 / 吉林市 / 东昌区 | 后续明确城市应纠正前面的歧义简称；层级匹配需联合判断 |
| 1 | 道路名称干扰：[山西北路 #92](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/92)、[台湾风情街 #39](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/39)、[已关闭 #69](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/69) | “上海市山西北路”默认得到山西省 / 上海市；“启东市台湾风情街”得到台湾省 / 南通市 / 启东市 | 确立省市区后保护详细地址，不能让路名和机构名反向污染区划；上游关闭不代表 fork 已修 |
| 1 | 默认映射忽略明确省份：[歧义 #125](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/125)、[提示 #108](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/108)、[同名区 #88](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/88) | “吉林省朝阳区”两模式均得到吉林省 / 北京市 / 朝阳区 | 省区联合判断优先于默认 umap；无上下文的同名区应提示歧义，之后再做候选列表 |
| 2 | 普通文本误匹配：[合作 #46](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/46)、[非地址 #126](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/126) | “合作共赢”得到合作市；“经济和信息化厅、省经济合作局”得到安徽省 / 马鞍山市 / 和县 | 限制单字简称及孤立普通词匹配，引入上下文约束；别只过滤“县”一个脏数据 |
| 3 | 自治州、盟、县和俗称：[州盟 #105](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/105)、[云南 #72](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/72)、[呼市 #106](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/106)、[多类简称 #101](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/101)、[前郭县 #85](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/85) | 黔南、西双版纳、阿拉善、兰坪县、元江县、前郭县等识别不全；全文模式西双版纳可误取西区 | 建显式、可审查的简称表，放在歧义和层级约束之后处理 |
| 3 | 部分层级校验：[校验 #56](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/56)、[跨省校区 #28](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/28) | 完整非法组合已标待核验；“青海师范大学成都校区”默认出现青海省 / 成都市 / 空，仅标未完整识别 | 即使区为空，也可核验已取得的省市是否矛盾；不要自动纠正不明确地址 |
| 4 | 历史名称覆盖：[大厂区 #40](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/40)、[曾用地名 #58](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/58)、[已关闭 #64](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/64) | “大厂区凤北路22号”错误识别为陕西省 / 宝鸡市 / 凤县；梅列区旧地址也存在问题 | 逐项核验补充历史词表，不能把当前 13 条兼容记录宣传为全国历史区划支持 |

根因集中在 `cpca/__init__.py` 的 `_fill_city`、`_jieba_extract`、`_full_text_extract` 以及过短简称生成规则。

**当前新增的“现行名称”只表示返回的省市区组合命中本项目现行快照，不代表原始输入被正确理解。** 上述“合作共赢”“和县”误识别仍可能得到这个状态。本轮没有修复这批解析算法问题。

## 已覆盖或部分覆盖，避免重复开发

| 上游问题 | 当前结论 |
| --- | --- |
| [数据更新 #76](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/76)、[#75](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/75)、[#65](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/65) | 本轮完成固定 2026 上游快照、官方补丁、来源和更新流程记录；非实时全国完整性保证 |
| [那曲 #132](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/132)、[龙华 #113](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/113)、[坪山龙华 #97](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/97)、[漠河 #87](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/87)、[当涂 #98](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/98) | 两种模式下所测具体用例均可识别 |
| [直管镇城市 #131](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/131)、[#112](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/112) | 东莞南城街道、中山沙溪镇已支持；洋浦为地点名称、嘉峪关雄关区为历史管理名称，不能都当现行县区 |
| [假县归重庆 #95](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/95) | 原问题不复现；普通文字误匹配仍需处理 |
| [高淳 #60](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/60)、[异常 #71](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/71)、[浦东 #36](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/36)、[天津 #42](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/42) | 所测原文不复现，先保留回归样例，无须照搬修复 |
| [省直辖县 #35](https://github.com/DQinYuan/chinese_province_city_area_mapper/issues/35) | 仙桃、神农架等能补省，但当前放市列、区为空；需要先统一输出层级口径 |

## PR 处理意见

| PR | 状态 | 建议 |
| --- | --- | --- |
| [#124 删除重庆“县”伪节点](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/124) | Open | 不直接合并。本 fork 没有该 adcodes 行；“县”“某县”“未知县某地址”两种模式均未误报重庆。保留脏节点治理思路 |
| [#103 杭州行政区调整](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/103) | Open | 不直接合并。钱塘区、临平区、临安区等现有表已覆盖；PR 的经纬度不适用本项目 |
| [#133 根据 adcode 返回全称](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/133) | Open | 暂缓。本 fork 无行政区划代码字段或 adcode 查询 API；只有明确代码查询需求时再建模，7 行补丁不能单独使用 |
| [#99 无法登录跳转](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/99) | Open | 不合并。实际跨大量文件引入 addressparser 等变动，与标题不符，上游维护者也要求拆分；本项目无该登录服务 |
| [#120 certifi](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/120)、[#118 Pillow](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/118)、[#116 py](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/116)、[#111 NumPy](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/111) | Open | 不锁回这些旧目标版本。按本项目真实依赖重新整理开发环境与锁文件 |
| [#109](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/109)、[#104](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/104)、[#100](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/100) | Closed / Merged | 旧 Pillow 更新，同上，不逐个移植 |
| [#80 换源锁文件](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/80)、[#73 setup 格式整理](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/73) | Closed / Merged | 以本项目现代打包与验证需求重整，不照搬旧源和格式提交 |
| [#5](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/5)、[#4](https://github.com/DQinYuan/chinese_province_city_area_mapper/pull/4) | Merged / Closed | 详细地址列已存在，不重复实现 |

## 本项目额外维护事项

下次发布前建议处理：`pkg_resources` 与 `setuptools.command.test` 弃用、setup.py 导入 cpca 导致构建期依赖运行环境。当前测试/打包是在 setuptools 80.10.2 环境中通过，不代表最新依赖可用。

`Pipfile` 仍声明 Python 3.7，包含已不在核心源码中的绘图工具；旧锁文件含 NumPy 1.17.2、pandas 0.25.1、Pillow 6.1.0 等。应按实际用途重建开发依赖，而不是采纳上游几年前的单包升级目标。这里仅确认版本陈旧，未做漏洞扫描。

多地址抽取（#114/#117）、全国乡镇与建筑物定位（#96/#48/#90/#31/#34）、绘图与经纬度（#123/#129/#29/#115）属于扩展范围；pyahocorasick 安装（#107/#102）不适用当前架构。暂不建议为解决上游问题而重新引入这些能力。

建议下一批先处理“省市层级约束 + 明确上下文优先 + 道路名保护”，然后处理“普通词/短简称误匹配”，最后扩充简称和历史词表。

2026-09-09 发布准备跟进：已修复构建时导入 cpca，移除废弃 test command，加入隔离构建 CI；运行依赖暂限定 setuptools<82，pkg_resources 的彻底迁移与旧 Pipfile 清理仍待处理。
