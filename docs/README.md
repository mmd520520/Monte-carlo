# docs：技术文档

> 算法说明和参数来源：读懂、修改代码时需要看的东西。项目方案（重构指南）在 [project/public/](../project/public/README.md)。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 算法说明、参数说明已完成 | 马孟帝、Eden Huang | 2026-11-07 |

## 里面有什么

| 文件 | 说明 |
|---|---|
| [algorithm.md](algorithm.md) | 算法说明：模型表示、光子的一生、两种发射方式、归一化、剂量定义、验证结果、MATLAB 对照表 |
| [optical_parameters.md](optical_parameters.md) | 膝关节模型 980 nm 光学参数的文献出处和假设（马孟帝原文，从 5demo 移来）；阶段 2 整理进 `presets/` |
| [assets/](assets/README.md) | 流程图和马孟帝的综述 PDF |

## 怎么用

- 想知道代码每一步在算什么：看 algorithm.md 第 2–4 节。
- 想改光学参数：先看 optical_parameters.md 和 `presets/README.md`。

## 更新记录

- 2026-11-07：阶段 1 移入 assets/ 和 optical_parameters.md；阶段 7 新增 algorithm.md。
- 2026-11-07：重构指南（含网页版）移到 `project/public/`。

## 给 AI 的说明

- 改 `mcsim/kernel.py` 时同步更新 algorithm.md 第 2、3 节。
- 第 6 节的验证数字来自实际运行；重新测量后更新，不要估算。
