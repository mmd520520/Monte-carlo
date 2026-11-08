# project/public：可以公开的项目资料

> 项目方案和调研，进 git，任何人都能看。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 重构指南已完成；GPU 加速调研完成 | 马孟帝、Eden Huang | 2026-11-07 |

## 里面有什么

| 文件 | 说明 |
|---|---|
| [REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) | 重构指南：现状诊断、10 条原则、目标结构、文件处置、代码映射、验收标准、执行计划，以及可复用的清单 |
| [REFACTOR_GUIDE_web.html](REFACTOR_GUIDE_web.html) | 网页版重构指南，给不看代码的同事和新手：蒙特卡洛小演示、名词小抄、上手步骤、通用清单。在线版：https://claude.ai/artifact/2PBhj8w4hQ4e2mT3RvH1qD（私有链接，分享后别人才能打开） |
| [gpu_mcx/](gpu_mcx/README.md) | GPU 加速调研：Qianqian Fang 的 MCX 怎么接进我们的框架；Mac 上的可行性实测 |

## 怎么用

- 第一次接触这个项目：先看网页版，再看 REFACTOR_GUIDE.md 第 1、2 节。
- 准备动代码：看 REFACTOR_GUIDE.md 第 5、7、8 节，再看 [docs/algorithm.md](../../docs/algorithm.md)。

## 更新记录

- 2026-11-07：从 `docs/` 移来。
- 2026-11-07：新增 gpu_mcx/。

## 给 AI 的说明

- REFACTOR_GUIDE.md 是项目方案的权威来源；网页版、根目录 README 都从它派生。改它时同步检查这两处；网页版改完要重新发布到同一个链接。
- 第 10 节“待确认事项”有了决定后，把结论写回对应章节，并从表里删掉这一行。
- 这里只放能公开的内容。判断规则见 [project/README.md](../README.md)。
