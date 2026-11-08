"""Interface text in Chinese and English, for the app and the figures.

Chinese is the default. In the Chinese text a few key terms carry their English name, so people
can move between the two vocabularies (光注量率 fluence rate, 体素 voxel, ...).
Preset-specific text (titles, tissue names, notes) lives in the preset YAML as ``*_en`` fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcsim.config import Preset, Tissue

LANGS = ("zh", "en")
LANG_LABELS = {"zh": "中文", "en": "EN"}

# key: (中文, English)
TEXT: dict[str, tuple[str, str]] = {
    # page
    "page_title": ("蒙特卡洛光传输仿真", "Monte Carlo light transport"),
    "title": ("蒙特卡洛（Monte Carlo）光传输仿真", "Monte Carlo light transport simulation"),
    "caption": ("{title} · 基于 {based_on} 移植 · 长度单位 {unit}", "{title} · ported from {based_on} · length unit {unit}"),
    "language": ("语言", "Language"),
    # sidebar
    "settings": ("模拟设置", "Simulation settings"),
    "model": ("模型（preset）", "Model"),
    "preset_knee_980nm": ("膝关节 · 980 nm", "Knee · 980 nm"),
    "preset_skin_500nm": ("皮肤血管 · 500 nm", "Skin with vessel · 500 nm"),
    "voxel_size": ("体素大小（voxel）", "Voxel size"),
    "res_original": ("{size}（原模型）", "{size} (original)"),
    "res_faster": ("{size}（更快）", "{size} (faster)"),
    "res_recommended": ("{size}（推荐）", "{size} (recommended)"),
    "res_matlab_coarse": ("{size}（与 MATLAB 粗网格相同）", "{size} (same as the MATLAB coarse grid)"),
    "res_full_slow": ("{size}（原模型，较慢，约 2 GB 内存）", "{size} (original, slower, about 2 GB memory)"),
    "photons": ("光子数（photons）", "Photons"),
    "seed": ("随机种子（seed）", "Random seed"),
    "source": ("光源", "Light source"),
    "diameter": ("光斑直径 [{unit}]", "Beam diameter [{unit}]"),
    "theta": ("入射角 θ [°]（0 = 垂直）", "Incidence angle θ [°] (0 = normal)"),
    "phi": ("方位角 φ [°]", "Azimuth φ [°]"),
    "has_power": ("设定总功率（用于剂量）", "Set total power (for dose)"),
    "power": ("总功率 [W]", "Total power [W]"),
    "run": ("开始模拟", "Run simulation"),
    # status
    "spinner": ("正在模拟……第一次运行需要编译，约 10 秒", "Simulating… the first run compiles the code (about 10 s)"),
    "param_error": ("参数有问题：{error}", "Invalid settings: {error}"),
    "stale": ("左侧设置已修改，点「开始模拟」用新设置重新计算。下面仍是上一次的结果。",
              "Settings changed. Click “Run simulation” to recompute; the results below are from the previous run."),
    # energy metrics
    "m_absorbed": ("组织吸收", "Absorbed"),
    "m_reflected": ("从表面反射", "Reflected"),
    "m_side": ("从侧面离开", "Side escape"),
    "m_transmitted": ("从底部透射", "Transmitted"),
    "m_specular": ("镜面反射（specular）", "Specular"),
    "m_total": ("合计", "Total"),
    "m_total_help": ("能量守恒自检：包含轮盘赌修正后应等于 100%", "Energy check: should be 100% including the roulette correction"),
    "run_caption": ("能量收支（energy balance）{balance} · {n} 个光子 · 种子 {seed} · 用时 {secs} s · {workers} 路并行 · 体素 {voxel} {unit} · 网格 {shape}",
                    "Energy balance {balance} · {n} photons · seed {seed} · {secs} s · {workers} parallel batches · voxel {voxel} {unit} · grid {shape}"),
    # tabs
    "tab_model": ("组织模型", "Tissue model"),
    "tab_light": ("光分布", "Light distribution"),
    "tab_dose": ("剂量", "Dose"),
    "tab_export": ("导出", "Export"),
    # model tab
    "optics": ("光学参数", "Optical properties"),
    "col_tissue": ("组织", "Tissue"),
    "col_source": ("来源", "Source"),
    "notes": ("注意事项", "Notes"),
    # light tab
    "section_y": ("截面位置 y [{unit}]", "Section at y [{unit}]"),
    "light_caption": ("白线是组织分界。颜色是对数刻度：每差 1 就是 10 倍。光子数少时深处会出现噪点，可增加光子数。",
                      "White lines mark tissue boundaries. The colour scale is logarithmic: one step is a factor of 10. "
                      "With few photons the deep region is noisy; add photons."),
    # dose tab
    "dose_needs_power": ("剂量需要总功率。在左侧勾选「设定总功率」后重新模拟。",
                         "Dose needs the total power. Tick “Set total power” on the left and run again."),
    "depths": ("皮下深度 [{unit}]，逗号分隔", "Depths below the skin [{unit}], comma-separated"),
    "exposure": ("照射时间 [s]", "Exposure time [s]"),
    "radius": ("圆面半径 [{unit}]", "Disk radius [{unit}]"),
    "col_depth": ("皮下深度 [{unit}]", "Depth [{unit}]"),
    "col_axis_h": ("中心轴 H [J/cm²]", "On-axis H [J/cm²]"),
    "col_disk_h": ("圆面平均 H [J/cm²]", "Disk-mean H [J/cm²]"),
    "col_disk_e": ("圆面能量 [J]", "Disk energy [J]"),
    "col_share": ("占总能量", "Share of total"),
    "col_air": ("圆面含空气", "Disk includes air"),
    "yes": ("是", "yes"),
    "dose_caption": ("皮肤表面（中心轴）在 z = {z} {unit}。累计光注量 H（radiant exposure）= 光注量率（fluence rate）× 照射时间，"
                     "是到达该处的光，不是被吸收的能量。模型和参数是简化值，不代表真实患者剂量。",
                     "The skin surface on the beam axis is at z = {z} {unit}. Radiant exposure H = fluence rate × exposure time: "
                     "the light reaching that depth, not the energy absorbed. Model and parameters are simplified; this is not a patient dose."),
    # export tab
    "dl_npz": ("下载结果数据（.npz）", "Download results (.npz)"),
    "dl_json": ("下载本次运行的完整参数（.json，可复现）", "Download the full run settings (.json, reproducible)"),
    "dl_csv": ("下载剂量表（.csv）", "Download the dose table (.csv)"),
    "export_caption": ("所有长度在 .npz 里以 mm 为单位；A 单位 1/mm³，phi 单位 1/mm²，均按每单位入射能量归一化。",
                       "All lengths in the .npz are in mm; A is in 1/mm³ and phi in 1/mm², both per unit incident energy."),
    # figures
    "fig_tissue_title": ("组织模型：y = {y} {unit} 截面", "Tissue model: section at y = {y} {unit}"),
    "fig_tissue_bar": ("组织", "Tissue"),
    "fig_depth_z": ("深度 z [{unit}]", "Depth z [{unit}]"),
    "fig_fluence_rate": ("光注量率（fluence rate）[W/cm²]", "Fluence rate [W/cm²]"),
    "fig_fluence": ("光注量（fluence）[1/mm²，每单位入射能量]", "Fluence [1/mm², per unit incident energy]"),
    "fig_light_title": ("光分布（对数色标）：y = {y} {unit} 截面", "Light distribution (log scale): section at y = {y} {unit}"),
    "fig_axis_title": ("光束中心轴上的光随深度衰减", "Light on the beam axis versus depth"),
    "fig_depth_below": ("皮下深度 [{unit}]", "Depth below the skin [{unit}]"),
    "fig_hover_depth": ("皮下", "depth"),
    "fig_on_axis": ("中心轴", "On axis"),
    "fig_disk_mean": ("圆面平均", "Disk mean"),
    "fig_dose_title": ("累计光注量 H（radiant exposure，照射 {t} s）", "Radiant exposure H ({t} s exposure)"),
    # navigation
    "nav_science": ("科普", "Science"),
    "nav_product": ("产品", "Product"),
    "nav_science_home": ("论文与前沿", "Papers & frontier"),
    "nav_simulator": ("仿真", "Simulation"),
    "nav_validation": ("验证", "Validation"),
    "nav_product_home": ("从研发到产品", "From R&D to product"),
    "nav_muse": ("案例：Muse", "Case: Muse"),
    "nav_headband": ("脑环闭环设计", "Headband loop design"),
    "nav_laser": ("康复激光", "Rehab laser"),
    # science home
    "sci_title": ("科普：方法从哪来，我们复现了什么", "Science: where the method comes from, what we reproduce"),
    "sci_classic": ("我们复现的经典方法", "Classic methods we reproduce"),
    "sci_frontier": ("相关前沿研究", "Related frontier research"),
    "sci_in_tool": ("在本工具里", "In this tool"),
    "sci_open": ("原文", "Source"),
    # validation
    "val_title": ("验证：和独立方法对比", "Validation: against an independent method"),
    "val_mua": ("吸收系数 μa [1/mm]", "Absorption μa [1/mm]"),
    "val_mus": ("散射系数 μs [1/mm]", "Scattering μs [1/mm]"),
    "val_g": ("各向异性 g", "Anisotropy g"),
    "val_n": ("折射率 n", "Refractive index n"),
    "val_d": ("厚度 [mm]", "Thickness [mm]"),
    "val_photons": ("光子数（photons）", "Photons"),
    "val_quantity": ("量", "Quantity"),
    "val_mc": ("蒙特卡洛（本引擎）", "Monte Carlo (this engine)"),
    "val_ad": ("加倍法（参照）", "Adding–doubling (reference)"),
    "val_z": ("差 ÷ 标准误差", "Difference ÷ std. error"),
    "val_R": ("总反射", "Total reflection"),
    "val_T": ("总透射", "Total transmission"),
    "val_A": ("吸收", "Absorbed"),
    "val_ok": ("一致：差值都在 ±3 个标准误差以内。", "Agree: every difference is within ±3 standard errors."),
    "val_check": ("有差值超过 ±3 个标准误差：多跑些光子再看；还超就值得查。", "A difference exceeds ±3 standard errors: run more photons; if it persists, investigate."),
    "val_caption": ("平板宽 41 mm、上下都是空气；{n} 个光子，用时 {secs} s。加倍法用 iadpython（16 和 32 个求积点之差计入参照的误差）。",
                    "Slab 41 mm wide with air on both sides; {n} photons in {secs} s. Adding–doubling via iadpython (the difference between 16 and 32 quadrature points counts as the reference's error)."),
    # product home
    "prod_title": ("产品：从研发到产品", "Product: from R&D to product"),
    # muse case
    "muse_title": ("案例：Muse 头带的个性化体验", "Case: personalization in the Muse headband"),
    "muse_try": ("体验一次训练（示意）", "Try a session (illustrative)"),
    "muse_skill": ("你今天的状态", "How settled you are today"),
    "muse_run": ("换一次训练", "Another session"),
    "muse_time": ("时间 [s]", "Time [s]"),
    "muse_calm_axis": ("平静度", "Calm"),
    "muse_sound": ("背景声音", "Background sound"),
    "muse_birds": ("鸟叫", "Birdsong"),
    "muse_calm_pct": ("平静时间占比", "Time calm"),
    "muse_recoveries": ("走神后拉回", "Recoveries"),
    "muse_report": ("训练后报告", "Session report"),
    "muse_progress": ("连续 10 次训练：基线和进步", "Ten sessions: baseline and progress"),
    "muse_session_n": ("第几次", "Session"),
    "muse_score": ("平静时间占比 [%]", "Time calm [%]"),
    "muse_baseline": ("个人基线（前 3 次平均）", "Personal baseline (mean of first 3)"),
    "muse_disclaimer": ("示意：用随机数模拟，不是 Muse 的算法，也不是真实脑电。目的是让人感受“反馈 → 报告 → 基线”这套体验。",
                        "Illustration: simulated with random numbers; not Muse's algorithm and not real EEG. It shows how feedback → report → baseline feels."),
    # headband loop
    "hb_title": ("脑环：闭环设计画布", "Headband: loop design canvas"),
    "hb_goal": ("场景", "Scenario"),
    "hb_goal_sleep": ("睡眠", "Sleep"),
    "hb_goal_focus": ("专注", "Focus"),
    "hb_goal_relax": ("放松", "Relaxation"),
    "hb_sensors": ("传感器", "Sensors"),
    "hb_s_eeg": ("脑电", "EEG"),
    "hb_s_hr": ("心率", "Heart rate"),
    "hb_s_spo2": ("血氧", "SpO₂"),
    "hb_s_temp": ("红外温度", "Infrared temperature"),
    "hb_s_fnirs": ("近红外脑血氧（fNIRS）", "Near-infrared oxygenation (fNIRS)"),
    "hb_feedback": ("给用户的反馈", "Feedback to the user"),
    "hb_f_sound": ("声音", "Sound"),
    "hb_f_visual": ("画面", "Visuals"),
    "hb_f_none": ("不反馈，只出报告", "None, report only"),
    "hb_light": ("光照干预", "Light intervention"),
    "hb_l_none": ("不照射", "None"),
    "hb_l_fixed": ("固定方案", "Fixed protocol"),
    "hb_l_adaptive": ("按状态自动调整", "Adjusted to the state"),
    "hb_timing": ("什么时候调整", "When to adjust"),
    "hb_t_session": ("每次训练之间", "Between sessions"),
    "hb_t_realtime": ("训练中实时", "In real time"),
    "hb_loop": ("这个闭环", "This loop"),
    "hb_questions": ("这个设计要研发回答的问题", "Questions this design raises for R&D"),
    "hb_download": ("下载这一页（Markdown）", "Download this page (Markdown)"),
    "hb_n_sense": ("测", "Sense"),
    "hb_n_decide": ("判断", "Decide"),
    "hb_n_feedback": ("反馈给人", "Feed back"),
    "hb_n_light": ("调整光照", "Adjust light"),
    "hb_n_user": ("用户", "User"),
    # laser
    "laser_title": ("康复激光：参数 → 表面剂量 → 深层剂量", "Rehab laser: settings → surface dose → dose at depth"),
    "laser_power": ("功率 [W]", "Power [W]"),
    "laser_spot": ("光斑直径 [cm]", "Spot diameter [cm]"),
    "laser_time": ("照射时间 [s]", "Exposure time [s]"),
    "laser_irr": ("表面平均功率密度", "Mean surface irradiance"),
    "laser_surface": ("表面能量密度", "Surface radiant exposure"),
    "laser_depth": ("皮下各深度的累计光注量（膝关节模型，中心轴）", "Radiant exposure below the skin (knee model, beam axis)"),
    "laser_share": ("占表面能量密度", "Share of the surface value"),
    "laser_caption": ("累计光注量 H（radiant exposure）是到达该深度的光，不是被吸收的能量。模型和参数是简化值，只用来比较不同参数组合的相对大小。",
                      "Radiant exposure H is the light reaching that depth, not the energy absorbed. The model and parameters are simplified; use them only to compare settings relative to each other."),
    # private notes
    "internal_notes": ("内部笔记", "Internal notes"),
    "private_missing": ("内部内容在私有空间（project/private/app/），这台电脑上没有，所以不显示。", "Internal content lives in the private space (project/private/app/) and is not on this computer, so it is not shown."),
}


def tr(key: str, lang: str = "zh", **values) -> str:
    """Text for ``key`` in ``lang`` ("zh" or "en"), with ``{placeholders}`` filled in."""
    text = TEXT[key][1 if lang == "en" else 0]
    return text.format(**values) if values else text


def tissue_name(tissue: Tissue, lang: str = "zh") -> str:
    return tissue.name_en if lang == "en" and tissue.name_en else tissue.name


def tissue_source(tissue: Tissue, lang: str = "zh") -> str:
    return tissue.source_en if lang == "en" and tissue.source_en else tissue.source


def preset_title(preset: Preset, lang: str = "zh") -> str:
    return preset.title_en if lang == "en" and preset.title_en else preset.title


def preset_notes(preset: Preset, lang: str = "zh") -> list[str]:
    return preset.notes_en if lang == "en" and preset.notes_en else preset.notes
