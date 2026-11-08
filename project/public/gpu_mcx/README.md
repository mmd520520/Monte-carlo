# gpu_mcx：GPU 加速调研（MCX）

> 怎么把 Qianqian Fang 教授的 MCX 接进我们的框架，用 GPU 跑光子。可行性已在 Mac 上验证。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 调研完成，接入未开始 | 【马孟帝】、Eden Huang | 2026-11-07 |

## 里面有什么

| 文件 | 说明 |
|---|---|
| [GUIDE.md](GUIDE.md) | 调研和接入方案：实测结果、MCX 家族、与我们引擎的对比、数据怎么对应、验收标准、硬件、许可、分步计划 |
| `poc_mcxcl_slab.py` | 可行性脚本：同一块平板用加倍法、MCX-CL、我们的引擎各算一次，比结果和用时 |

## 怎么用

```bash
uv run --with pmcxcl --with pmcx python project/public/gpu_mcx/poc_mcxcl_slab.py
```

苹果芯片的 Mac 用 `pmcxcl`（GPU，OpenCL）；有 NVIDIA 显卡时把脚本里的 `import pmcxcl as mcx` 换成 `import pmcx as mcx`。

## 更新记录

- 2026-11-07：建立；Apple M4 Pro 上 MCX-CL 跑通，结果与加倍法、我们的引擎一致。

## 给 AI 的说明

- MCX 是 GPLv3，只作为可选依赖，不要加进 `pyproject.toml` 的默认依赖。
- 接入代码放 `mcsim/backends/`，不要放在这个文件夹。
