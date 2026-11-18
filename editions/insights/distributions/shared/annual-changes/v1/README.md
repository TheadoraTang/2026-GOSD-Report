# 2025–2026：全球开源的八大变化 / Eight shifts in global open source

已批准双语增量 v1.0.0 · 2026-11-18。中文专题 v0.5 / COSSI 全文 v1.7；英文专题 v0.1 / COSSI 全文 v0.6。

| 内容 | 中文 | English |
| --- | --- | --- |
| 可直接阅读的文字 | [中文正文](zh-CN/README.md) | [English copy](en/README.md) |
| 结构化编辑入口 | [content.json](zh-CN/content.json) | [content.json](en/content.json) |
| 排版 | A4 纵向；四幅组合图＋四项分析 | Native A3 portrait; four charts and four analyses |
| 全文页码 | 物理 13–14；xi–xii | Physical 14–15; xiii–xiv |
| 全文总页数 | 144 | 158 |

数字仅维护在 [chart-data.json](shared/chart-data.json)。[双语单元对应表](shared/bilingual-alignment.json) 记录八项译文与中文原文的指纹。[manifest.json](manifest.json) 固定版本、输入/成品指纹和页面位置；[证据台账](shared/evidence-ledger-en.json)、[中文证据索引](review/zh-evidence-index.json) 和 [源数据记录](shared/source-records.json) 说明每项对象、时期及限制。主期保持 2025-07-01 至 2026-06-30，不将外部报告年度、历史月榜和期后快照混算。

## 八项内容

1. GitHub 开发活动增长与 AI 工作流 / Activity and AI-assisted workflows.
2. 代码、模型、数据资产 / Code, models and datasets.
3. 全球南方的不同增长路径 / Global South participation.
4. 中国地区贡献序列的交叉 / China's contribution-series crossover.
5. 杭州模型复用 / Hangzhou and model reuse.
6. 华为与微软的月榜交叉 / Huawei's monthly lead.
7. 开放原子与 Apache 的月榜交叉 / OpenAtom's monthly crossover.
8. Agent 技术全景的新创建仓库 / Repository creation in the agent stack.

## 从固定输入复建

依赖 Python 3.11+、PyMuPDF 1.26.6、NumPy、fontTools、ReportLab、XeLaTeX/TikZ/fontspec，以及系统 Noto Sans CJK、Noto Serif CJK、Noto Sans、Liberation Serif 字体。字体文件不随仓库分发，默认系统路径见生成脚本。

```bash
python build.py --language zh-CN   --zh-baseline /external/GOSD_2026_Essential_COSSI_zh-CN_v1.6.pdf   --output-dir /external/rebuild-zh
python build.py --language en   --zh-baseline /external/GOSD_2026_Essential_COSSI_zh-CN_v1.6.pdf   --en-baseline /external/GOSD_2026_COSSI_EN_Full_Print_v0.5.pdf   --output-dir /external/rebuild-en
```

构建器先校验母稿 SHA-256，再在临时目录恢复原版排版与合稿结构。企业/项目 Logo 按内容哈希从中文母稿提取，英文背景从英文母稿提取；地图从已登记 SVG 转为临时 PDF，不将第三方原件或生成 PDF 写入 Git。英文插图和中文共用数字源，英文单位和文案独立。

构建后检查所有继承页面、目录/页码/书签/链接、专题文字与字体；输出全文、两页专题及核验记录。PDF 封装、生成时间和源码附件可能使重建哈希不同于已交付成品，分别登记。此入口复建的是本次增量，既有全文以固定 PDF 为输入。

```bash
python check_data.py
python ../../../check_registry.py
```

## 证据与版本边界

GitHub 包含私有仓库，四项活动各自使用尺度；同比与 AI 使用同时上升不证明因果。HF 增幅来自约数。六国不代表全部全球南方；中国序列不与 GitHub 单平台国家榜混算。五城下载量不是独立用户量。企业月榜不替代全年榜。LF 汇总有标签重叠。48/86=55.8% 是创建年代比例，2025/2026 名单更替率尚未计算。

`review/` 保存先前交付时的核验快照，其中历史“待评审”状态由 [本次批准记录](../../../../reviews/2026-11-18-bilingual-annual-changes.md) 取代，保留其当时含义。本轮不刷新原始数据，不宣称全部旧章节事实已重新验证。
