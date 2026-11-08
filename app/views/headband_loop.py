"""产品 · 脑环闭环设计 / Product · Headband loop design: a canvas that turns a design into R&D questions."""

import streamlit as st

from brand import banner
from common import content, lang, private_content
from mcsim.i18n import tr

L = lang()
GOALS, SENSORS = ["sleep", "focus", "relax"], ["eeg", "hr", "spo2", "temp", "fnirs"]
FEEDBACK, LIGHT, TIMING = ["sound", "visual", "none"], ["none", "fixed", "adaptive"], ["session", "realtime"]

# (condition on the design, 中文, English): each is a question the design hands to R&D or medical affairs
QUESTIONS = [
    (lambda d: d["light"] != "none",
     "多少近红外光能到达皮层？头发、肤色、颅骨厚度影响多大？（仿真：需要头部模型）",
     "How much near-infrared light reaches the cortex? How much do hair, skin tone and skull thickness matter? (simulation: needs a head model)"),
    (lambda d: d["light"] == "adaptive",
     "按什么指标、变化多大才调整光照？需要剂量—效应的数据",
     "Which metric, and how large a change, triggers a change in the light? Needs dose–response data"),
    (lambda d: d["light"] == "fixed",
     "固定方案的剂量依据是什么？Gamma / Alpha 两种模式的剂量怎么比较？",
     "What is the dose basis for a fixed protocol? How do the Gamma and Alpha modes compare in dose?"),
    (lambda d: d["light"] != "none" and ("fnirs" in d["sensors"] or "spo2" in d["sensors"]),
     "治疗光会不会干扰近红外和血氧测量？需要错开时间或波长",
     "Does the treatment light disturb the near-infrared and SpO₂ readings? Needs separate timing or wavelengths"),
    (lambda d: d["light"] != "none" and "temp" in d["sensors"],
     "照射时皮肤温升多少、安全边界在哪？（仿真 + 台架）",
     "How much does the skin warm under the light, and where is the safety limit? (simulation + bench)"),
    (lambda d: d["light"] != "none" and "temp" not in d["sensors"],
     "没有温度传感器时，怎么保证照射安全？",
     "Without a temperature sensor, how is the exposure kept safe?"),
    (lambda d: "fnirs" in d["sensors"],
     "近红外测量主要来自多深？探头距离怎么选？（仿真：需要探测器统计）",
     "How deep does near-infrared sensing reach, and what probe distance to use? (simulation: needs detector tallies)"),
    (lambda d: d["goal"] == "sleep",
     "睡眠分期的准确率能做到多少？（对标：Muse 与多导睡眠图一致 88–96%）",
     "How accurate can sleep staging be? (benchmark: Muse agrees with polysomnography 88–96%)"),
    (lambda d: d["timing"] == "realtime",
     "实时检测的延迟和误判：多快、多准才够用？",
     "Real-time detection: how fast and how accurate is enough?"),
    (lambda d: "eeg" not in d["sensors"],
     "不用脑电，用什么判断大脑状态？",
     "Without EEG, what tells us the brain state?"),
    (lambda d: d["feedback"] == "none",
     "没有实时反馈，用户怎么感觉到在起作用？用什么留住用户？",
     "With no real-time feedback, how does the user feel it working, and what keeps them coming back?"),
    (lambda d: True,
     "宣称边界：健康消费品，还是医疗器械？证据要做到哪一级？",
     "Claims: a wellness product or a medical device? What level of evidence is needed?"),
]

banner(tr("hb_title", L), tr("sub_headband", L), "headband")
st.markdown(content("headband_intro", L))

left, right = st.columns([1, 2])
with left:
    design = dict(
        goal=st.radio(tr("hb_goal", L), GOALS, format_func=lambda k: tr(f"hb_goal_{k}", L), horizontal=True),
        sensors=st.multiselect(tr("hb_sensors", L), SENSORS, default=["eeg", "hr", "spo2", "temp"],
                               format_func=lambda k: tr(f"hb_s_{k}", L)),
        feedback=st.radio(tr("hb_feedback", L), FEEDBACK, format_func=lambda k: tr(f"hb_f_{k}", L)),
        light=st.radio(tr("hb_light", L), LIGHT, index=2, format_func=lambda k: tr(f"hb_l_{k}", L)),
        timing=st.radio(tr("hb_timing", L), TIMING, format_func=lambda k: tr(f"hb_t_{k}", L)),
    )

sensors_txt = "\\n".join(tr(f"hb_s_{k}", L) for k in design["sensors"]) or "—"
goal_label = tr("hb_goal_" + design["goal"], L)
feedback_label = tr("hb_f_" + design["feedback"], L)
timing_label = tr("hb_t_" + design["timing"], L)
light_label = tr("hb_l_" + design["light"], L)
edges = [f'user -> sense [label="{goal_label}"]', "sense -> decide"]
if design["feedback"] != "none":
    edges.append(f'decide -> feedback [label="{feedback_label}"]')
    edges.append("feedback -> user")
if design["light"] != "none":
    edges.append(f'decide -> light [label="{timing_label}"]')
    edges.append("light -> user")
dot = f"""digraph {{
  rankdir=LR; bgcolor="transparent"; node [shape=box, style="rounded,filled", fillcolor="#F6F8FC", color="#0D2472", fontname="Helvetica"];
  edge [color="#8A9BC4", fontcolor="#8A9BC4", fontname="Helvetica", fontsize=10];
  user [label="{tr('hb_n_user', L)}", fillcolor="#E8EDFF"];
  sense [label="{tr('hb_n_sense', L)}\\n{sensors_txt}"];
  decide [label="{tr('hb_n_decide', L)}"];
  feedback [label="{tr('hb_n_feedback', L)}"];
  light [label="{tr('hb_n_light', L)}\\n{light_label}", fillcolor="#E6F7FC", color="#1040C1"];
  {"; ".join(edges)};
}}"""
questions = [zh if L == "zh" else en for cond, zh, en in QUESTIONS if cond(design)]
with right:
    st.markdown(f"**{tr('hb_loop', L)}**")
    st.graphviz_chart(dot, use_container_width=True)
    st.markdown(f"**{tr('hb_questions', L)}**")
    st.markdown("\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1)))

page = [f"# {tr('hb_title', L)}", "",
        f"- {tr('hb_goal', L)}: {tr('hb_goal_' + design['goal'], L)}",
        f"- {tr('hb_sensors', L)}: {', '.join(tr('hb_s_' + k, L) for k in design['sensors']) or '—'}",
        f"- {tr('hb_feedback', L)}: {tr('hb_f_' + design['feedback'], L)}",
        f"- {tr('hb_light', L)}: {tr('hb_l_' + design['light'], L)}",
        f"- {tr('hb_timing', L)}: {tr('hb_t_' + design['timing'], L)}", "",
        f"## {tr('hb_questions', L)}", ""] + [f"{i}. {q}" for i, q in enumerate(questions, 1)]
st.download_button(tr("hb_download", L), "\n".join(page), file_name="headband_loop.md")

notes = private_content("product_notes", L)
with st.expander(tr("internal_notes", L), expanded=False):
    if notes:
        st.markdown(notes)
    else:
        st.caption(tr("private_missing", L))
