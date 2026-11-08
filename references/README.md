# references：第三方资料（文件只在本地）

> 开源程序、安装包、论文和数据集。体积大、不归我们所有，所以不进 git；这里只记清单、版本、许可和下载地址。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 文件在本地 `references/`，已被 `.gitignore` 忽略；待上传企业微信网盘 | Eden Huang | 2026-11-07 |

## 清单

| 本地位置 | 是什么 | 版本 / 许可 | 从哪获取 |
|---|---|---|---|
| `third_party/MCX/` | GPU 体素蒙特卡洛程序源码 | 3.0（v2026），GPLv3 | github.com/fangq/mcx；mcx.space |
| `third_party/MMC/` | 网格蒙特卡洛程序源码 | 3.0.0（v2026），GPLv3 | github.com/fangq/mmc；mcx.space |
| `third_party/MCML/` | 经典分层蒙特卡洛程序（C 语言） | 版权：Univ. of Texas M.D. Anderson Cancer Center | 【上游下载地址待补】；论文 Wang、Jacques、Zheng，1995 |
| `third_party/MCXStudio-win64-v2025.10/` 及同名 `.zip` | MCX/MMC 的 Windows 图形界面安装包，含 `.exe` | 2025.10 | mcx.space |
| `third_party/MCML_MCX_MMC_开源代码压缩包.zip` | 上面三个源码目录的压缩包 | — | 与目录内容重复，可删 |
| `third_party/knee-2016-09/` | SPL 膝关节解剖图谱（3D Slicer 格式） | 3D Slicer License | 【上游地址待补】 |
| `papers/论文.zip` | 41 篇蒙特卡洛与 NIRS 论文，实习生按主题分了文件夹 | 版权归原作者和期刊 | 实习生收集 |
| `papers/Parameter_paper.pdf` | Damagatla 等，人体 5 个部位、10 名受试者的组织光学参数谱，Scientific Data 2026 | 见期刊 | doi:10.1038/s41597-026-06586-9 |
| `data/Parameter_paper_Dataset_invivo_subjects_TDDOS.zip` | 上面论文的数据集，610–1110 nm | 【许可待查】 | 【数据集地址待补，见论文】 |
| `head/head_atlas_3d.html` | 头部图谱三维查看器网页（Plotly），25 MB | — | 实习生生成，生成方式待确认 |
| `head/Improving model-based ….pdf` | Tran、Yan、Fang，Neurophotonics 2020 | 见期刊 | doi:10.1117/1.NPh.7.1.015008 |

## 怎么用

- 需要某个程序或论文：先看本地 `references/`；本地没有，从企业微信网盘下载，或按表里的地址获取。
- 新增第三方资料：放进对应子文件夹，在表里加一行（写清版本和许可）。不要提交到 git。

## 待办

- [ ] 上传到企业微信网盘，填链接：【网盘链接】
- [ ] 补 MCML、膝关节图谱、数据集的上游地址和许可

## 更新记录

- 2026-11-07：从仓库根目录移出 git，集中到本地 `references/`（git 历史里仍有这些文件）。

## 给 AI 的说明

- 本文件是第三方资料的唯一清单。代码里引用第三方方法时，写清版本和许可。
- `references/` 下除本文件外都不能提交。
