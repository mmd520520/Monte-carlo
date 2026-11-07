# docs：项目文档

> 重构方案、算法说明和参数来源。代码之外需要读的东西都放这里。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 重构指南已完成；算法和参数说明待写 | 光学实习生、Eden Huang | 2026-11-07 |

## 里面有什么

| 文件 | 说明 |
|---|---|
| [REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) | 重构指南：现状诊断、10 条原则、目标结构、文件处置、代码映射、验收标准、执行计划，以及可复用的清单 |
| [REFACTOR_GUIDE_web.html](REFACTOR_GUIDE_web.html) | 网页版重构指南，给不看代码的同事和新手：蒙特卡洛小演示、名词小抄、上手步骤、通用清单。在线版：https://claude.ai/artifact/2PBhj8w4hQ4e2mT3RvH1qD（私有链接，需分享后他人才能打开） |
| `algorithm.md`（待写） | 算法说明，整合根目录的流程图和简介 PDF |
| `optical_parameters.md`（待写） | 组织光学参数和文献出处，整合 `matlab/5demo/光学参数文献_原说明.md` |

## 怎么用

- 第一次接触这个项目：先看网页版，再看 REFACTOR_GUIDE.md 第 1、2 节。
- 准备动代码：看 REFACTOR_GUIDE.md 第 5、7、8 节，按阶段做。

## 更新记录

- 2026-11-07：新增 REFACTOR_GUIDE.md 和网页版。

## 给 AI 的说明

- REFACTOR_GUIDE.md 是项目方案的权威来源；网页版（REFACTOR_GUIDE_web.html）、根目录 README、内部分享 PPT 都从它派生。改它时同步检查这三处；网页版改完要重新发布到同一个链接。
- 第 10 节“待确认事项”有了决定后，把结论写回对应章节，并从表里删掉这一行。
