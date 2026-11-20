# Source-View Listing Images

依据商品卖点、中文参考图、实物和指定模特制作本地化商品图。身态马来语流程见 [工作流程](skills/source-view-listing-images/references/shentai-malay-listing.md)。

## 在 Codex 中安装

仓库公开，无需 GitHub 登录。把下面这段发给 Codex。

> 请用 Codex 的 skill-installer 从 https://github.com/vanch007/source-view-listing-images/tree/v1.1.0/skills/source-view-listing-images 安装技能。安装后检查本机技能目录下的 `source-view-listing-images/SKILL.md` 是否存在。若本机已有同名技能，先告诉我路径和版本。

通过安装助手时，参数为 `--repo vanch007/source-view-listing-images --path skills/source-view-listing-images --ref v1.1.0 --method download`。安装完成后开启新对话，必要时重启 Codex。

## 用法

> 使用 $source-view-listing-images 为款号 [款号] 制作马来语商品 Listing 图片。我会提供商品卖点、同款中文参考图和实物图、指定模特图、SKU 色名和尺码表。按身态流程出 8 张主图、9 张独立详情页、每个在售颜色一张 SKU 白底图。给我手机连读预览、图位与卖点对照 PDF 以及待确认的图片。按实物核对颜色和结构，沿用指定模特，缺资料的图位标明缺项。用本机已配置且获准使用的生图工具，先交付审核版。

图片生成需要接收方已有的图像工具。仓库提供的是工作流程、校验脚本和评测示例，本地视觉复核服务可选。商品原图、模特素材及访问凭证由使用者在获授权的工作区内提供。2026-11-20 的 2405 验证记录使用原项目的本地素材，团队不需要该项目即可使用工作流程。

- [技能入口](skills/source-view-listing-images/SKILL.md)
- [评测记录](skills/source-view-listing-images/reports/output_quality_scorecard.md)
