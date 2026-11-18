# 英文版与跨版本同步

当前状态（2026-11-18）：COSSI 英文全文 v0.6 已完成编辑评审并获作者接受；Community 英文仍为 planned。本文继续作为跨语言维护规范，当前成果与证据见 [双语专题及合稿记录](../../reviews/2026-11-18-bilingual-annual-changes.md)。

## 共同正文先行

英文稿对应同一`content_id`的中文正文与数据，不按COSSI／Community复制两份翻译。图号、指标编码、统计窗口、来源、已批准的限制说明须一一对应；英文排版造成页数不同可以接受，内容映射必须完整。各自封面、编委会、机构介绍与发行说明随后单独组合。

翻译时依次记录`planned`、`translating`、`editorial_review`、`accepted_baseline`；正式发布另记`publication_status`与日期。任何语言的编辑通过不自动升级数据核验状态。

## 最小追踪字段

| 字段 | 用途 |
| --- | --- |
| `source_content_id` | 共同研究内容的确切版本 |
| `source_language` / `language` | 来源与目标语言 |
| `source_unit_id` | 章／节／图／表／前置单元的稳定编号 |
| `source_sha256` | 识别已翻译的确切原文 |
| `translation_status` | 未开始、翻译、编辑复核或接受 |
| `reviewed_by` / `reviewed_on` | 记录实际完成的复核，不预填 |
| `source_changed` | 原文变化后标记是否需要重新核对 |

## 术语与机构名称

[术语起始表](terminology.json)仅整理已有获批文本的名称及状态，供翻译使用。COSSI Edition和Community Edition是发行标签；CCOSI仍指专委会，不为COSSI虚构机构英文全称。

新增专委会介绍采用`CAST UN Consultative Committee on Open Source Innovation (CCOSI)`。旧版共同致谢仍有`CAST Advisory Committee on Open Source Innovation`这一历史英文表述；英文版后续修订仍须按最新版机构介绍核对，并记录原文差异，不在冻结的中文成品中静默替换。

秘书长联系方式保持：王伟，华东师范大学数据学院，wwang@dase.ecnu.edu.cn。英文单位和职务措辞以实际确认的正式表达为准，不根据中文自行加头衔。封面Logo原则上复用原标识；需要英文专用组合时另行记录版式评审。

## 发布检查

英文稿接受前，逐图核对数值、单位、分母、年份和预测起点；区分主统计期、历史材料、外部窗口和期后观察。检查译文是否扩大中国贡献、开放程度、机构地位或因果判断。最终再核对中英文目录、图表编号、引用和各发行版本的前置信息。
