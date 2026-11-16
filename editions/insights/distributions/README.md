# GOSD 2026：COSSI 与 Community 发行版本

发行管理 v1.0 · 2026-11-16。两条发行版本共用精要版研究内容，中文基线已由作者指定，英文版筹备中。仓库归档不等同于机构正式发布。

| 发行版本 | 定位 | 封面标识（从左至右） | 中文基线 | 英文状态 |
| --- | --- | --- | --- | --- |
| [COSSI](cossi/zh-CN/README.md) | 中国科协牵头的发行版本，由开源创新专委会组织相关工作 | CCOSI、奇点智能研究院 | 全文 v1.6，142页 | [筹备中](cossi/en/README.md) |
| [Community](community/zh-CN/README.md) | X-lab、奇点智能研究院、CCOSI、开源社等社区与机构共同建设的发行版本 | X-lab、奇点智能研究院、CCOSI、开源社 | 此前四Logo全文 v1.4，140页 | [筹备中](community/en/README.md) |

**COSSI是作者指定的发行名称；CCOSI是机构Logo和最新版介绍中的英文缩写。** 目录ID分别为`cossi`和`community`，不把机构名称、Logo或正文中的CCOSI改写为COSSI。Community明确采用此前四Logo版本，不是从当前两Logo版本重新换封面后生成的另一稿。

## 四个独立维度

| 维度 | 当前值 | 管理方式 |
| --- | --- | --- |
| 内容版型 | `essential`（精要版，工作区`insights`） | 六章、附录、数据与研究主张共用 |
| 发行版本 | `cossi`、`community` | 分开维护封面、联署、编委会、机构介绍及前置编排 |
| 语言 | `zh-CN`、`en` | 中文已有基线；英文先登记来源与翻译状态 |
| 输出格式 | PDF优先；Web后续 | 以同一内容和发行配置生成，不因格式另立研究版本 |

不建立两条长期正文分支。今后的内容修订先形成共同基线，再分别生成两种发行版本；某一版本尚未完成同步时，必须保留其原内容版本号，不把较旧成品标为最新。语言和发行版本可以独立推进，但必须记录所依据的共同内容基线。

## 已固定的两份中文制品

- [版本注册表](registry.json)：统一入口，记录发行名称、语言状态和各自配置。
- [共同正文基线](shared/content-baseline.json)：两版印刷页1—118完全一致，含六章、附录和致谢。Community位于物理21—138页，COSSI位于23—140页；内封底、封底亦一致。
- [逐页比对记录](shared/body-equivalence.json)：118页文字、内容流及36 dpi渲染逐页核对，均一致。
- [两版重建验收](shared/build-verification.json)：Community完整文件保持一致，COSSI全部142页文字、72 dpi图像及导航与获批稿一致。
- [COSSI中文配置](cossi/zh-CN/edition.json)与[Community中文配置](community/zh-CN/edition.json)：完整PDF的文件名、SHA-256、页码与前置差异。
- [2026-11-16作者决定与边界](../reviews/2026-11-16-distribution-baselines.md)。

版本号`v1.6`、`v1.4`继承对应成品历史，不是两条发行路线的质量高低或研究结论先后。正式发布日期未确定，本次只登记已接受的编辑基线与发行定位；数据、许可和争议项沿用原报告核验状态。

Community旧版致谢中的中国科协指导、专委会牵头编写等角色继续保留。“牵头编写”与“社区共同建设／发行”是不同层面的描述，不通过改名删除原有编写贡献。

## 后续英文版

[英文转写与同步规范](shared/translation-policy.md)要求两种发行版本共用英文正文和术语表，只翻译各自前置信息。当前两个`en`配置均为`planned`，没有英文PDF、页数或完成日期。翻译、编辑校对、数据核对和发行审核分别登记，不能把配置文件、术语参考或机器翻译视为英文版已经完成。

## 源码、构建与边界

[共享构建源码](shared/source/README.md)包含两种中文发行版本的统一入口、COSSI获批前置内容、原生矢量图和外部素材校验清单。两种输出使用相同的Community v1.4全文作为正文输入，COSSI仅替换／插入已批准前置页并更新导航。重建输出按页面与导航验收，不承诺PDF封装字节与历史成品相同。

PDF、字体、原始图片／附件和压缩包不入库。构建需要仓库外的已批准PDF与素材，程序按指纹核验；没有这些输入时只能读取和编辑源码，不能声称已重建全文。既有[整书源归档](../../../reports/print-v1.1/README.md)保持为v1.1历史，不冒充当前v1.4或v1.6完整数据源。

提交前运行：

```bash
python editions/insights/distributions/check_registry.py
python editions/insights/scripts/check_sources.py
python brand/osdgs/v2.0/source/verify_assets.py
python brand/osdgs/identity/v0.1/source/verify_assets.py
git diff --check
```

[返回精要版入口](../README.md)
