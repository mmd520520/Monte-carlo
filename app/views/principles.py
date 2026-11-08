"""科普 · 技术原理 / Science · How it works: the algorithm as a flowchart, the formulas, parallelism and GPU,
and where the engine can be improved. Long text lives in app/content/principles_*.md."""

import streamlit as st

from common import content, lang
from mcsim import load_preset, simulate
from mcsim.i18n import tr

L = lang()


def t(key: str) -> str:
    """Interface text as a Graphviz label: escaped quotes, line breaks as \\n."""
    return tr(key, L).replace('"', '\\"').replace("\n", "\\n")


STYLE = """bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#F4F6F8", color="#1B2A3A", fontname="Helvetica", fontsize=11];
  edge [color="#8A93A0", fontcolor="#8A93A0", fontname="Helvetica", fontsize=10];"""
TALLY = 'fillcolor="#F6E7E9", color="#A51C30"'
DECISION = 'shape=diamond, style="filled", fillcolor="#E8ECF1"'


def photon_flow() -> str:
    """One photon packet, step by step, as in mcsim/kernel.py run_batch()."""
    yes, no = t("tp_yes"), t("tp_no")
    return f"""digraph {{
  rankdir=TB; {STYLE}
  launch [label="{t('tp_n_launch')}"];
  hop [label="{t('tp_n_hop')}"];
  voxel [label="{t('tp_n_voxel')}"];
  move [label="{t('tp_n_move')}", {TALLY}];
  hit [label="{t('tp_n_hit')}", {DECISION}];
  grid [label="{t('tp_n_grid')}", {DECISION}];
  escape [label="{t('tp_n_escape')}", {TALLY}];
  index [label="{t('tp_n_index')}", {DECISION}];
  fresnel [label="{t('tp_n_fresnel')}", {DECISION}];
  reflect [label="{t('tp_n_reflect')}"];
  refract [label="{t('tp_n_refract')}"];
  skinair [label="{t('tp_n_skinair')}", {DECISION}];
  skinout [label="{t('tp_n_skinout')}", {TALLY}];
  next [label="{t('tp_n_next')}"];
  spin [label="{t('tp_n_spin')}"];
  low [label="{t('tp_n_low')}", {DECISION}];
  roulette [label="{t('tp_n_roulette')}", {DECISION}];
  dead [label="{t('tp_n_dead')}", shape=oval];
  normalise [label="{t('tp_n_normalise')}", {TALLY}];

  launch -> hop -> voxel -> move -> hit;
  hit -> spin [label="{no}"];
  hit -> grid [label="{yes}"];
  grid -> escape [label="{yes}"];
  grid -> index [label="{no}"];
  index -> fresnel [label="{yes}"];
  index -> skinair [label="{no}"];
  fresnel -> reflect; fresnel -> refract;
  reflect -> voxel [style=dashed];
  refract -> skinair;
  skinair -> skinout [label="{yes}"];
  skinair -> next [label="{no}"];
  next -> voxel [style=dashed];
  spin -> low;
  low -> hop [label="{no}", style=dashed];
  low -> roulette [label="{yes}"];
  roulette -> hop [label="{t('tp_n_survive')}", style=dashed];
  roulette -> dead [label="{t('tp_n_die')}"];
  escape -> dead; skinout -> dead;
  dead -> launch [label="{t('tp_n_nextphoton')}", style=dashed];
  dead -> normalise [label="{t('tp_n_alldone')}"];
}}"""


def batch_flow() -> str:
    """Batches, seeds and threads, as in mcsim/runner.py simulate()."""
    return f"""digraph {{
  rankdir=LR; {STYLE}
  photons [label="{t('tp_p_photons')}", shape=oval];
  split [label="{t('tp_p_split')}"];
  seed [label="{t('tp_p_seed')}"];
  threads [label="{t('tp_p_threads')}"];
  merge [label="{t('tp_p_merge')}"];
  result [label="{t('tp_p_result')}", {TALLY}];
  gpu [label="{t('tp_p_gpu')}", style="rounded,dashed", fillcolor="transparent"];
  photons -> split -> seed -> threads -> merge -> result;
  seed -> gpu [style=dashed, label="{t('tp_p_plan')}"];
  gpu -> merge [style=dashed];
}}"""


def cpu_vs_gpu() -> str:
    """How the same transport is spread over CPU cores today and over GPU threads in MCX."""
    return f"""digraph {{
  rankdir=TB; compound=true; {STYLE}
  subgraph cluster_cpu {{ label="CPU"; color="#8A93A0"; fontname="Helvetica";
    cpu [label="{t('tp_g_cpu')}", shape=oval];
    cpu_work [label="{t('tp_g_cpu_work')}"];
    cpu_tally [label="{t('tp_g_cpu_tally')}", {TALLY}];
    cpu_merge [label="{t('tp_g_cpu_merge')}"];
    cpu -> cpu_work -> cpu_tally -> cpu_merge; }}
  subgraph cluster_gpu {{ label="GPU"; color="#8A93A0"; fontname="Helvetica";
    gpu [label="{t('tp_g_gpu')}", shape=oval];
    gpu_work [label="{t('tp_g_gpu_work')}"];
    warp [label="{t('tp_g_warp')}", {DECISION}];
    gpu_tally [label="{t('tp_g_gpu_tally')}", {TALLY}];
    copy [label="{t('tp_g_copy')}"];
    gpu -> gpu_work -> warp -> gpu_tally -> copy; }}
}}"""


@st.cache_data(show_spinner=False, max_entries=1)
def benchmark(nonce: int) -> dict:
    """Small timed run on the machine serving the app (knee, 2.5 mm voxels)."""
    simulate(load_preset("knee_980nm", photons=2_000, seed=1, stride=2), workers=0)  # compile / load the cache
    photons = 200_000  # same conditions as the first row of the measured table
    r = simulate(load_preset("knee_980nm", photons=photons, seed=1, stride=2), workers=0)
    return {"rate": photons / r.elapsed_s, "workers": r.workers, "kernel": r.transport_s / r.elapsed_s,
            "faces": r.counters["boundary_events"] / photons, "scatter": r.counters["scattering_events"] / photons}


st.title(tr("tp_title", L))
st.markdown(content("principles_intro", L))

flow, math_tab, speed, roadmap = st.tabs([tr("tp_tab_flow", L), tr("tp_tab_math", L), tr("tp_tab_speed", L),
                                          tr("tp_tab_roadmap", L)])
with flow:
    st.subheader(tr("tp_flow_one", L))
    st.graphviz_chart(photon_flow(), use_container_width=True)
    st.caption(tr("tp_flow_legend", L))
    st.markdown(content("principles_flow", L))
with math_tab:
    st.markdown(content("principles_math", L))
with speed:
    st.subheader(tr("tp_flow_many", L))
    st.graphviz_chart(batch_flow(), use_container_width=True)
    st.markdown(content("principles_speed", L))
    if st.button(tr("tp_bench", L), help=tr("tp_bench_help", L)):
        st.session_state["tp_bench_nonce"] = st.session_state.get("tp_bench_nonce", 0) + 1
    if "tp_bench_nonce" in st.session_state:
        with st.spinner(tr("spinner", L)):
            b = benchmark(st.session_state["tp_bench_nonce"])
        c = st.columns(5)
        c[0].metric(tr("tp_bench_rate", L), f"{b['rate']:,.0f}")
        c[1].metric(tr("tp_bench_threads", L), b["workers"])
        c[2].metric(tr("tp_bench_faces", L), f"{b['faces']:.0f}")
        c[3].metric(tr("tp_bench_scatter", L), f"{b['scatter']:.0f}")
        c[4].metric(tr("tp_bench_kernel", L), f"{b['kernel']:.0%}", help=tr("tp_bench_kernel_help", L))
    st.subheader(tr("tp_gpu_title", L))
    st.graphviz_chart(cpu_vs_gpu(), use_container_width=True)
    st.caption(tr("tp_gpu_legend", L))
    st.markdown(content("principles_gpu", L))
with roadmap:
    st.markdown(content("principles_roadmap", L))
