# 双版本共享构建源码

Community 与 COSSI 共用印刷页 1—118 的六章、附录和致谢。Community 固定于获批四标识全文 v1.4（140 页）；COSSI 的页面验收目标为获批两标识全文 v1.6（142 页）。`COSSI` 是用户指定的发行名称；机构正文和原始标识缩写仍为 `CCOSI`。

本目录只保存可编辑 Python、JSON、SVG 和依赖说明，不包含 PDF、字体、原始图片或 ZIP。PDF 必须输出到 Git 仓库之外。

## 构建环境与外部输入

验证环境为 Python 3.12、PyMuPDF 1.26.6、fontTools 4.61.1；精确依赖见 `requirements.txt`。程序不联网获取素材。

`input-materials.json` 固定批准制品、Community 母稿、5 项外部素材和 4 项 Noto CJK 字体的 SHA256。任何缺失或不匹配均在生成 PDF 之前报错，不回退到近似图片或字体。

外部素材目录应含：

| 文件 | 用途 |
|---|---|
| `cover-baseline.png` | 原四标识封面主视觉；仅底部标识带用原生 PDF 图形重新排版 |
| `body-baseline.pdf` | 已批准内页装饰波纹，仅裁取页脚装饰区域 |
| `ccosi.png` | CCOSI 原始透明标识 |
| `siri-white.png` | 奇点智能研究院原始透明标识 |
| `committee-photo.jpg` | 专委会合影，原生 PDF 裁切，不改动图片像素 |

四个字体集合为 `NotoSansCJK-Regular.ttc`、`NotoSansCJK-Bold.ttc`、`NotoSerifCJK-Regular.ttc`、`NotoSerifCJK-Bold.ttc`。优先从素材目录的 `fonts/` 子目录读取；否则通过 `fontconfig` 的 `fc-match` 查找本机安装，再核对 SHA256 与简体中文集合索引 2。字体不进入仓库。子集化保留 `retain_gids=True`，避免阅读器中的 CFF 字形错映射。

原始母稿与资产应由项目既有批准材料取得。源目录只登记文件名及指纹，不记录账户标识或制作机器路径。

## 统一命令

以下命令从本目录执行，示例输入和输出均为仓库外路径：

```bash
python build.py --distribution community --language zh-CN \
  --community-baseline /data/GOSD_2026_Essential_Full_Print_v1.4.pdf \
  --output /data/rebuilt/GOSD_2026_Community_zh-CN.pdf

python build.py --distribution cossi --language zh-CN \
  --community-baseline /data/GOSD_2026_Essential_Full_Print_v1.4.pdf \
  --assets-dir /data/gosd-approved-assets \
  --output /data/rebuilt/GOSD_2026_COSSI_zh-CN.pdf
```

Community 在核对完整母稿 SHA256 后原样复制，制品字节保持不变。COSSI 在临时目录生成获批五页前置内容，再替换封面、关于页及编委会，在编委会之后插入专委会两页介绍；正文完全从同一个 Community 母稿导入，不重新排版。

COSSI 封面沿用 v1.6 的精确光学参数：CCOSI 宽 75 pt、顶部 773.1 pt；奇点可见宽 128.5 pt、顶部 772 pt；两者间距 38 pt、组合居中。机构标识不重绘或变形。前置页码、目录、书签和内链按插入两页联动，保留原 79 条外链并增加秘书长邮箱链接。

`--language en` 明确拒绝构建并显示 `planned`，不会创建输出。英文内容和版式尚无获批制品，不能把中文稿改名充作英文版。

输出 PDF 同目录生成 `.build.json`，分别标识 `approved_artifact_exact_copy` 与 `reconstructed_from_approved_page_sources`，记录批准制品与本次输出的独立哈希。COSSI 重建稿不声称与批准 v1.6 的 PDF 字节或附件全集相同：它保留注明 Baseline 的历史 v1.4 装配源，另附本次重建装配记录；原批准制品仍由 `input-materials.json` 中的 v1.6 哈希唯一确定。

## 验证

```bash
python verify.py --distribution cossi \
  --rebuilt /data/rebuilt/GOSD_2026_COSSI_zh-CN.pdf \
  --approved /data/GOSD_2026_Essential_Full_Print_v1.6.pdf \
  --qa /data/rebuilt/cossi-page-verification.json
```

`verify.py` 先核对批准参考 PDF 的固定哈希，再逐页比较文字与 72 dpi 绘制像素，并核对书签、页标签、全部内外链接。Community 还必须通过完整 PDF 字节一致性。验证报告记录每页像素哈希，任何差异返回非零退出码；可用 `--dpi` 提高渲染分辨率。

2026-11-16 的实际重建验证：Community 140 页原字节复制；COSSI 142 页文字、72 dpi 绘制像素、123 条书签、页标签与 216 条链接全部和批准稿一致。批准制品与重建制品的身份应分开记录。

## 编辑边界

- `content/` 保存编委名单、专委会介绍及原材料来源指纹。
- `diagrams/` 保存可编辑 SVG、与原生绘制共用的 JSON 和图件生成脚本；工作体系图的 JSON 是 PDF 的实际绘制输入，修改时应同步生成 SVG。
- `frontmatter/build_layout.py` 生成结构化排版指令；`frontmatter/render.py` 以嵌入字体和原生图形生成前置页。
- `merge.py` 是统一入口调用的内部装配阶段，不是独立对外接口。

实际可复现路径为上述 PyMuPDF 原生排版。临时生成的 `frontmatter.tex` 只是中文友好的辅助设计稿，尚未覆盖全部原生图形，不宣称可用它独立重建等价 PDF。此构建器以批准的 Community PDF 保存现有全文，亦不宣称从仓库中的章节源码重新计算全书数据或重新审批研究结论。
