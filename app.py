"""
Super RAG — Cyberpunk Neural Interface
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import random
from pathlib import Path

st.set_page_config(
    page_title="Super RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Outfit:wght@300;400;600;700&display=swap');

:root {
  --void:    #03010a;
  --magenta: #ff2d78;
  --lime:    #00ff88;
  --cyan:    #00d4ff;
  --orange:  #ff6b00;
  --panel:   #080613;
  --border:  #1a0f2e;
  --muted:   #3d2f5a;
  --text:    #e8deff;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background: var(--void);
    color: var(--text);
}
.stApp { background: var(--void); }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: var(--magenta); border-radius: 2px; }

[data-testid="stSidebar"] {
    background: #060410 !important;
    border-right: 1px solid #1a0f2e;
}

.wordmark {
    font-family: 'Orbitron', monospace;
    font-weight: 900;
    font-size: 20px;
    letter-spacing: 0.08em;
    padding: 8px 0 4px 0;
}
.wordmark .rag { color: var(--magenta); text-shadow: 0 0 20px var(--magenta), 0 0 40px var(--magenta); }
.wordmark .super { color: var(--cyan); text-shadow: 0 0 20px var(--cyan); }
.tagline {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 22px;
}

.section-heading {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--magenta);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,45,120,0.5) 0%, transparent 100%);
}

.pipeline-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 13px 16px;
    margin-bottom: 7px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.pipeline-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
    background: var(--muted);
    transition: background 0.3s, box-shadow 0.3s;
}
.pipeline-card.active {
    border-color: var(--cyan);
    box-shadow: 0 0 20px rgba(0,212,255,0.15), inset 0 0 20px rgba(0,212,255,0.03);
}
.pipeline-card.active::before {
    background: var(--cyan);
    box-shadow: 0 0 12px var(--cyan);
    animation: pulse-bar 1s ease-in-out infinite;
}
.pipeline-card.active::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0; left: -100%;
    width: 60%;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.07), transparent);
    animation: scan 1.6s linear infinite;
}
.pipeline-card.done { border-color: #0d2e1a; }
.pipeline-card.done::before { background: var(--lime); box-shadow: 0 0 10px var(--lime); }
.pipeline-card.error::before { background: #ff4444; }

@keyframes scan {
    0%   { left: -100%; }
    100% { left: 200%; }
}
@keyframes pulse-bar {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.phase-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.phase-name { font-weight: 600; font-size: 13px; color: var(--text); }
.phase-status { font-family: 'DM Mono', monospace; font-size: 10px; margin-top: 4px; }
.phase-status.active { color: var(--cyan); }
.phase-status.done   { color: var(--lime); }
.phase-status.idle   { color: var(--muted); }
.phase-status.error  { color: #ff4444; }
.phase-icon {
    position: absolute; right: 14px; top: 50%; transform: translateY(-50%);
    font-size: 17px; opacity: 0.5;
}
.pipeline-card.done .phase-icon { opacity: 1; filter: drop-shadow(0 0 5px var(--lime)); }
.pipeline-card.active .phase-icon {
    opacity: 1;
    animation: float-i 2s ease-in-out infinite;
    filter: drop-shadow(0 0 8px var(--cyan));
}
@keyframes float-i {
    0%,100% { transform: translateY(-50%); }
    50%      { transform: translateY(-60%); }
}

.stat-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin: 14px 0; }
.stat-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 13px 10px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(255,45,120,0.08) 0%, transparent 70%);
}
.stat-value {
    font-family: 'Orbitron', monospace;
    font-size: 22px;
    font-weight: 700;
    color: var(--magenta);
    text-shadow: 0 0 15px var(--magenta);
    line-height: 1;
    animation: count-glow 2s ease-in-out infinite alternate;
}
@keyframes count-glow {
    from { text-shadow: 0 0 8px var(--magenta); }
    to   { text-shadow: 0 0 30px var(--magenta), 0 0 60px rgba(255,45,120,0.4); }
}
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
}

.chat-wrap {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(255,45,120,0.04);
}
.chat-hdr {
    background: #060410;
    border-bottom: 1px solid var(--border);
    padding: 11px 18px;
    display: flex; align-items: center; gap: 10px;
}
.chat-hdr-title {
    font-family: 'Orbitron', monospace;
    font-size: 10px;
    color: var(--magenta);
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.chat-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--lime); box-shadow: 0 0 8px var(--lime);
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.chat-body { padding: 16px 18px; max-height: 390px; overflow-y: auto; }

.msg-user { display:flex; justify-content:flex-end; margin-bottom:13px; animation:sl 0.3s ease; }
@keyframes sl { from{opacity:0;transform:translateX(15px)} to{opacity:1;transform:none} }
.msg-user .bubble {
    background: linear-gradient(135deg, #2d0a1f, #1a0f2e);
    border: 1px solid rgba(255,45,120,0.3);
    border-radius: 14px 14px 2px 14px;
    padding: 10px 14px; max-width: 70%;
    font-size: 13px; line-height: 1.65;
    box-shadow: 0 0 14px rgba(255,45,120,0.08);
}
.msg-ai { display:flex; gap:10px; margin-bottom:13px; animation:sr 0.3s ease; }
@keyframes sr { from{opacity:0;transform:translateX(-15px)} to{opacity:1;transform:none} }
.msg-ai .avatar {
    width:30px;height:30px;
    background:linear-gradient(135deg,#0a1f2d,#0d2640);
    border:1px solid rgba(0,212,255,0.4);
    border-radius:8px;
    display:flex;align-items:center;justify-content:center;
    font-size:13px; flex-shrink:0;
    box-shadow: 0 0 10px rgba(0,212,255,0.2);
}
.msg-ai .bubble {
    background: linear-gradient(135deg, #0a0618, #060410);
    border: 1px solid rgba(0,212,255,0.18);
    border-radius: 2px 14px 14px 14px;
    padding: 10px 14px; max-width: 80%;
    font-size: 13px; line-height: 1.7;
}
.sources { display:flex; flex-wrap:wrap; gap:5px; margin-top:10px; }
.source-tag {
    border-radius:20px; padding:2px 10px;
    font-family:'DM Mono',monospace; font-size:9px;
    letter-spacing:0.05em; cursor:pointer;
    transition: all 0.2s;
}
.source-tag.text   { background:#0a1a2e; border:1px solid var(--cyan); color:var(--cyan); }
.source-tag.visual { background:#1a0a2e; border:1px solid #a855f7; color:#c084fc; }
.source-tag.kg     { background:#1a1000; border:1px solid var(--orange); color:var(--orange); }
.source-tag:hover  { filter:brightness(1.4); transform:translateY(-1px); }

.chunk-card {
    background: #050310;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 11px 14px;
    margin-bottom: 7px;
    font-size: 12px; line-height: 1.7;
    color: #8b7aaa;
    transition: border-color 0.2s, color 0.2s;
}
.chunk-card:hover { border-color: rgba(0,212,255,0.3); color: var(--text); }
.chunk-card.text   { border-left: 3px solid var(--cyan); }
.chunk-card.visual { border-left: 3px solid #a855f7; }
.chunk-card.kg     { border-left: 3px solid var(--orange); }
.chunk-meta {
    font-family:'DM Mono',monospace; font-size:9px;
    color:var(--muted); margin-bottom:5px;
    display:flex; align-items:center; gap:8px;
}
.score-pill {
    background:#0a0618; border:1px solid var(--border);
    border-radius:20px; padding:1px 8px;
    font-size:9px; color:var(--lime);
}

.stButton > button {
    font-family:'Orbitron',monospace !important;
    font-size:11px !important; letter-spacing:0.12em !important;
    background:linear-gradient(135deg,#b01050,#7a0a38) !important;
    color:#fff !important;
    border:1px solid var(--magenta) !important;
    border-radius:6px !important;
    padding:10px 20px !important; font-weight:700 !important;
    width:100%;
    box-shadow:0 0 20px rgba(255,45,120,0.3) !important;
    transition:all 0.2s !important;
}
.stButton > button:hover {
    box-shadow:0 0 40px rgba(255,45,120,0.6) !important;
    transform:translateY(-1px);
}
.stButton > button:disabled {
    background:#0d0a18 !important;
    border-color:var(--border) !important;
    color:var(--muted) !important;
    box-shadow:none !important;
}
.stTextInput > div > div > input {
    background:var(--panel) !important;
    border:1px solid var(--border) !important;
    border-radius:6px !important; color:var(--text) !important;
    font-family:'Outfit',sans-serif !important; font-size:13px !important;
}
.stTextInput > div > div > input:focus {
    border-color:var(--cyan) !important;
    box-shadow:0 0 0 2px rgba(0,212,255,0.15) !important;
}
[data-testid="stFileUploader"] {
    background:#060410 !important;
    border:1px dashed #2a1050 !important;
    border-radius:10px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color:var(--magenta) !important;
    box-shadow:0 0 20px rgba(255,45,120,0.1) !important;
}
.stSelectbox > div > div {
    background:var(--panel) !important;
    border:1px solid var(--border) !important;
    border-radius:6px !important; color:var(--text) !important;
}
.stSlider > div > div > div > div { background:var(--magenta) !important; }
[data-testid="stSidebar"] label { color:#6b5f8a !important; font-size:12px !important; }
.stProgress > div > div > div > div {
    background:linear-gradient(90deg, var(--magenta), var(--cyan)) !important;
}
.streamlit-expanderHeader {
    background:var(--panel) !important;
    border:1px solid var(--border) !important;
    border-radius:6px !important;
    font-family:'DM Mono',monospace !important;
    font-size:11px !important; color:var(--muted) !important;
}
.video-wrap {
    border:1px solid var(--border); border-radius:10px;
    overflow:hidden; background:#000;
    box-shadow:0 0 30px rgba(255,45,120,0.1); margin-bottom:12px;
}
.warn-box {
    background:#0d0a00; border:1px solid #3d2800;
    border-left:3px solid var(--orange);
    border-radius:6px; padding:10px 14px;
    font-family:'DM Mono',monospace; font-size:11px;
    color:var(--orange); margin-bottom:12px;
}
hr { border:none; border-top:1px solid var(--border); margin:14px 0; }
.cfg-heading {
    font-family:'DM Mono',monospace; font-size:9px;
    color:var(--magenta); letter-spacing:0.25em;
    text-transform:uppercase; margin:18px 0 10px 0;
    padding-bottom:6px; border-bottom:1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  NEURAL NETWORK BACKGROUND
# ═══════════════════════════════════════════════════════════
components.html("""
<style>
#neural-bg {
  position:fixed; top:0; left:0;
  width:100vw; height:100vh;
  z-index:0; pointer-events:none;
}
</style>
<canvas id="neural-bg"></canvas>
<script>
const canvas = document.getElementById('neural-bg');
const ctx = canvas.getContext('2d');
function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
resize(); window.addEventListener('resize', resize);

const COLORS = ['#ff2d78','#00d4ff','#00ff88','#ff6b00','#a855f7'];
const nodes = Array.from({length:60}, ()=>({
  x: Math.random()*canvas.width,
  y: Math.random()*canvas.height,
  vx: (Math.random()-.5)*.3,
  vy: (Math.random()-.5)*.3,
  r: Math.random()*1.8+0.8,
  phase: Math.random()*Math.PI*2,
  col: COLORS[Math.floor(Math.random()*COLORS.length)]
}));

function draw(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  nodes.forEach(n=>{
    n.x+=n.vx; n.y+=n.vy; n.phase+=0.018;
    if(n.x<0||n.x>canvas.width)  n.vx*=-1;
    if(n.y<0||n.y>canvas.height) n.vy*=-1;
  });
  for(let i=0;i<nodes.length;i++){
    for(let j=i+1;j<nodes.length;j++){
      const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
      const d=Math.sqrt(dx*dx+dy*dy);
      if(d<130){
        ctx.beginPath();
        ctx.moveTo(nodes[i].x,nodes[i].y);
        ctx.lineTo(nodes[j].x,nodes[j].y);
        ctx.strokeStyle=nodes[i].col;
        ctx.globalAlpha=(1-d/130)*0.1;
        ctx.lineWidth=0.7;
        ctx.stroke();
      }
    }
  }
  nodes.forEach(n=>{
    const g=(Math.sin(n.phase)+1)/2;
    ctx.globalAlpha=0.35+g*0.45;
    ctx.beginPath();
    ctx.arc(n.x,n.y,n.r+g*1.5,0,Math.PI*2);
    ctx.fillStyle=n.col;
    ctx.shadowColor=n.col;
    ctx.shadowBlur=8+g*14;
    ctx.fill();
    ctx.shadowBlur=0;
  });
  ctx.globalAlpha=1;
  requestAnimationFrame(draw);
}
draw();
</script>
""", height=0)


# ═══════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════
PHASE_IDS = ["splicer","stt","vlm","kg","vectordb","visualdb","rag"]
for k,v in {
    "pipeline_ran": False,
    "processing": False,
    "phase_states": {p:"idle" for p in PHASE_IDS},
    "phase_msgs":   {p:""    for p in PHASE_IDS},
    "stats": {"chunks":0,"entities":0,"vectors":0},
    "chat_history": [],
    "video_name": "",
}.items():
    if k not in st.session_state: st.session_state[k] = v


# ═══════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════
PHASE_META = [
    ("splicer",  "P1",  "Video Splicer",        "Splitting into temporal chunks",    "🎬"),
    ("stt",      "P2A", "Speech-to-Text",        "Transcribing audio via Whisper",    "🎙️"),
    ("vlm",      "P2B", "Vision-Language Model", "Analysing frames with VLM",         "👁️"),
    ("kg",       "P3",  "Knowledge Graph",       "Extracting entities & relations",   "🕸️"),
    ("vectordb", "P4A", "Vector Database",       "Embedding & indexing text chunks",  "🧬"),
    ("visualdb", "P4B", "Visual Database",       "Embedding visual features",         "🖼️"),
    ("rag",      "P5",  "RAG Engine",            "Initialising retrieval engine",     "⚡"),
]
STATUS_ICONS = {"idle":"○","active":"◉","done":"✓","error":"✗"}
MOCK_ANSWERS = [
    {"text":"The speaker explains dense passage retrieval at 02:14, describing how a vector index is queried at inference time to surface relevant passages. They contrast this with pure parametric memory and highlight latency trade-offs.",
     "sources":[{"label":"02:14–02:38","type":"text"},{"label":"Frame 134","type":"visual"},{"label":"LLM→retrieval","type":"kg"}]},
    {"text":"Three limitations are discussed: (1) retrieval latency on long corpora, (2) context window constraints, and (3) semantic drift when query embeddings misalign with indexed passages. Hybrid BM25 + dense retrieval is suggested as mitigation.",
     "sources":[{"label":"05:50–06:20","type":"text"},{"label":"07:02–07:15","type":"text"},{"label":"Entity: BM25","type":"kg"}]},
    {"text":"The diagram at 04:30 shows a two-stage pipeline: coarse retriever selects top-k candidates, then a cross-encoder re-ranker scores them. This improves precision without full dense search over the entire corpus.",
     "sources":[{"label":"04:30–04:55","type":"text"},{"label":"Frame 271","type":"visual"}]},
]


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════
def run_pipeline(name):
    for i,(pid,*_) in enumerate(PHASE_META):
        st.session_state.phase_states[pid]="active"
        st.session_state.phase_msgs[pid]="Processing..."
        time.sleep([1.0,2.2,2.5,1.6,1.2,1.0,0.7][i])
        # ── Wire your real calls here ──
        # e.g. from splicer import splice_video; splice_video(...)
        st.session_state.phase_states[pid]="done"
        st.session_state.phase_msgs[pid]="Complete"
    st.session_state.stats={"chunks":random.randint(18,45),"entities":random.randint(120,340),"vectors":random.randint(800,2400)}
    st.session_state.pipeline_ran=True
    st.session_state.processing=False

def render_phase(pid,num,name,desc,icon):
    state=st.session_state.phase_states[pid]
    msg=st.session_state.phase_msgs[pid]
    st.markdown(f"""
    <div class="pipeline-card {state}">
        <div class="phase-label">{num}</div>
        <div class="phase-name">{name}</div>
        <div class="phase-status {state}">{STATUS_ICONS[state]} {msg if msg else desc}</div>
        <div class="phase-icon">{icon}</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  ANIMATED WAVEFORM
# ═══════════════════════════════════════════════════════════
def waveform_widget(active=False):
    col = "#00d4ff" if active else "#1a0f2e"
    anim = "animation:wave var(--d) ease-in-out infinite alternate;" if active else ""
    bars = "".join(
        f'<div style="width:4px;border-radius:2px;background:{col};box-shadow:0 0 6px {col};height:{4 if not active else 8}px;--d:{0.3+i*0.06:.2f}s;--h:{6+abs(14-i)*2}px;{anim}"></div>'
        for i in range(30)
    )
    components.html(f"""
    <style>
    @keyframes wave {{ from{{height:3px}} to{{height:var(--h)}} }}
    </style>
    <div style="display:flex;gap:3px;align-items:center;height:34px;padding:4px 2px;
                background:#060410;border:1px solid #1a0f2e;border-radius:6px;
                margin:6px 0;padding:4px 8px;overflow:hidden">
        {bars}
    </div>""", height=44)


# ═══════════════════════════════════════════════════════════
#  KG NODE CANVAS
# ═══════════════════════════════════════════════════════════
def kg_viz():
    components.html("""
<canvas id="kg" style="width:100%;height:130px;display:block;"></canvas>
<script>
(function(){
const c=document.getElementById('kg');
c.width=c.parentElement.offsetWidth||280; c.height=130;
const ctx=c.getContext('2d'), W=c.width, H=130;
const labels=['RAG','VLM','Whisper','FAISS','Chunks','Entities','KG','CLIP'];
const cols=['#ff2d78','#00d4ff','#00ff88','#ff6b00','#00d4ff','#ff2d78','#00ff88','#a855f7'];
const nodes=labels.map((l,i)=>({
  x:30+(i%4)*((W-60)/3), y:28+Math.floor(i/4)*72,
  vx:(Math.random()-.5)*.35, vy:(Math.random()-.5)*.35,
  label:l, col:cols[i], phase:Math.random()*Math.PI*2
}));
const edges=[[0,1],[0,2],[0,3],[0,4],[4,2],[4,6],[6,5],[1,7],[3,4],[5,6]];
function frame(){
  ctx.clearRect(0,0,W,H);
  nodes.forEach(n=>{
    n.x+=n.vx; n.y+=n.vy; n.phase+=0.02;
    if(n.x<18||n.x>W-18) n.vx*=-1;
    if(n.y<18||n.y>H-18) n.vy*=-1;
  });
  edges.forEach(([a,b])=>{
    const g=(Math.sin(nodes[a].phase)+1)/2;
    ctx.beginPath(); ctx.moveTo(nodes[a].x,nodes[a].y); ctx.lineTo(nodes[b].x,nodes[b].y);
    ctx.strokeStyle=nodes[a].col; ctx.globalAlpha=0.12+g*0.14; ctx.lineWidth=1; ctx.stroke();
  });
  nodes.forEach(n=>{
    const g=(Math.sin(n.phase)+1)/2;
    ctx.globalAlpha=0.75+g*0.25;
    ctx.beginPath(); ctx.arc(n.x,n.y,4+g*2,0,Math.PI*2);
    ctx.fillStyle=n.col; ctx.shadowColor=n.col; ctx.shadowBlur=8+g*14; ctx.fill(); ctx.shadowBlur=0;
    ctx.globalAlpha=0.65;
    ctx.fillStyle='#e8deff'; ctx.font='8px DM Mono,monospace'; ctx.textAlign='center';
    ctx.fillText(n.label,n.x,n.y-9);
  });
  ctx.globalAlpha=1; requestAnimationFrame(frame);
}
frame();
})();
</script>""", height=138)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="wordmark"><span class="super">SUPER</span><span class="rag">RAG</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Multimodal Neural Retrieval</div>', unsafe_allow_html=True)

    st.markdown('<div class="cfg-heading">⬡ Ingestion</div>', unsafe_allow_html=True)
    chunk_size    = st.slider("Chunk size (sec)", 5, 60, 15, 5)
    whisper_model = st.selectbox("Whisper model", ["tiny","base","small","medium","large"], index=2)
    vlm_backend   = st.selectbox("VLM backend", ["LLaVA-7B","Qwen-VL","InternVL2"])

    st.markdown('<div class="cfg-heading">⬡ Retrieval</div>', unsafe_allow_html=True)
    embed_model  = st.selectbox("Embedding model", ["nomic-embed-text","bge-large-en","text-embedding-3-small"])
    top_k        = st.slider("Top-k", 1, 20, 5)
    use_reranker = st.toggle("Cross-encoder reranker", value=True)
    use_kg       = st.toggle("Knowledge graph fusion", value=True)

    st.markdown('<div class="cfg-heading">⬡ Live Graph Preview</div>', unsafe_allow_html=True)
    kg_viz()


# ═══════════════════════════════════════════════════════════
#  MAIN LAYOUT
# ═══════════════════════════════════════════════════════════
left, right = st.columns([1, 1.85], gap="large")

# ────────────── LEFT ──────────────
with left:
    st.markdown('<div class="section-heading">Input</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("video", type=["mp4","mov","avi","mkv","webm"], label_visibility="collapsed")

    if uploaded:
        tmp = Path("/tmp") / uploaded.name
        tmp.write_bytes(uploaded.read())
        st.session_state.video_name = uploaded.name
        st.markdown('<div class="video-wrap">', unsafe_allow_html=True)
        st.video(str(tmp))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:10px;color:#3d2f5a;margin-bottom:12px">📁 {uploaded.name}</div>', unsafe_allow_html=True)

        if st.button("⚡  ENGAGE PIPELINE", disabled=st.session_state.processing):
            for pid in PHASE_IDS:
                st.session_state.phase_states[pid]="idle"
                st.session_state.phase_msgs[pid]=""
            st.session_state.pipeline_ran=False
            st.session_state.processing=True
            st.session_state.chat_history=[]
            st.rerun()
    else:
        st.markdown("""
        <div style="border:1px dashed #2a1050;border-radius:10px;padding:38px 20px;
                    text-align:center;background:#060410;margin-bottom:16px">
            <div style="font-size:30px;margin-bottom:10px;
                        filter:drop-shadow(0 0 14px #ff2d78);animation:float-i 3s ease-in-out infinite">🎬</div>
            <div style="font-size:14px;font-weight:600;color:#6b5f8a;margin-bottom:4px">Drop your video here</div>
            <div style="font-family:DM Mono,monospace;font-size:10px;color:#2a1f40;letter-spacing:0.15em">
                MP4 · MOV · AVI · MKV · WEBM
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    if st.session_state.processing:
        for pid,num,name,desc,icon in PHASE_META:
            render_phase(pid,num,name,desc,icon)
        waveform_widget(active=st.session_state.phase_states.get("stt")=="active")
        run_pipeline(st.session_state.video_name)
        st.rerun()
    else:
        for pid,num,name,desc,icon in PHASE_META:
            render_phase(pid,num,name,desc,icon)
        if st.session_state.phase_states.get("stt")=="done":
            waveform_widget(active=False)

    if st.session_state.pipeline_ran:
        s=st.session_state.stats
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card"><div class="stat-value">{s['chunks']}</div><div class="stat-label">Chunks</div></div>
            <div class="stat-card"><div class="stat-value">{s['entities']}</div><div class="stat-label">Entities</div></div>
            <div class="stat-card"><div class="stat-value">{s['vectors']}</div><div class="stat-label">Vectors</div></div>
        </div>""", unsafe_allow_html=True)


# ────────────── RIGHT ──────────────
with right:
    st.markdown('<div class="section-heading">Neural Query Interface</div>', unsafe_allow_html=True)

    if not st.session_state.pipeline_ran:
        st.markdown('<div class="warn-box">⚡ Engage the pipeline first to activate querying.</div>', unsafe_allow_html=True)

    # Build chat
    chat_inner = ""
    if not st.session_state.chat_history:
        chat_inner = """
        <div style="text-align:center;padding:48px 20px">
            <div style="font-size:34px;margin-bottom:12px;
                        filter:drop-shadow(0 0 14px #00d4ff)">🔮</div>
            <div style="font-family:DM Mono,monospace;font-size:11px;
                        color:#3d2f5a;letter-spacing:0.1em">
                Ask anything about your video
            </div>
        </div>"""
    else:
        for turn in st.session_state.chat_history:
            if turn["role"]=="user":
                chat_inner+=f'<div class="msg-user"><div class="bubble">{turn["content"]}</div></div>'
            else:
                srcs=""
                if "sources" in turn:
                    srcs='<div class="sources">'+"".join(
                        f'<span class="source-tag {s["type"]}">{s["label"]}</span>'
                        for s in turn["sources"]
                    )+'</div>'
                chat_inner+=f'<div class="msg-ai"><div class="avatar">✦</div><div class="bubble">{turn["content"]}{srcs}</div></div>'

    st.markdown(f"""
    <div class="chat-wrap">
        <div class="chat-hdr">
            <div class="chat-dot"></div>
            <div class="chat-hdr-title">RAG Session Live</div>
        </div>
        <div class="chat-body">{chat_inner}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns([5,1])
    with c1:
        query=st.text_input("q",placeholder="What topics are covered? What's shown at 3:20?",
                            label_visibility="collapsed",
                            disabled=not st.session_state.pipeline_ran,key="query_input")
    with c2:
        send=st.button("Ask →",disabled=not st.session_state.pipeline_ran)

    if send and query:
        st.session_state.chat_history.append({"role":"user","content":query})
        with st.spinner("Retrieving…"):
            time.sleep(0.7)
            result=random.choice(MOCK_ANSWERS)
        st.session_state.chat_history.append({"role":"assistant","content":result["text"],"sources":result["sources"]})
        st.rerun()

    if st.session_state.pipeline_ran and st.session_state.chat_history:
        st.markdown("---")
        st.markdown('<div class="section-heading">Retrieved Context</div>', unsafe_allow_html=True)

        for chunk in [
            {"type":"text",  "meta":f"Chunk #{random.randint(10,30)} · {random.randint(1,8):02d}:{random.randint(0,59):02d}","score":round(random.uniform(0.82,0.97),3),"content":"Speaker introduces dense passage retrieval, contrasting embedding similarity with lexical overlap on out-of-vocabulary queries."},
            {"type":"visual","meta":f"Frame {random.randint(100,400)} · t={random.randint(60,400)}s","score":round(random.uniform(0.70,0.88),3),"content":"Slide: two-stage retrieval — coarse ANN retrieval → cross-encoder re-ranking. Labels: Query Encoder, FAISS Index, Re-ranker, Generator."},
            {"type":"kg",    "meta":f"KG subgraph · {random.randint(3,8)} hops","score":round(random.uniform(0.60,0.82),3),"content":"RAG → uses → Dense Retrieval → implemented with → FAISS. BM25 ←[alt]→ Dense Retrieval. Cross-encoder ←[improves]→ Precision@k."},
        ]:
            st.markdown(f"""
            <div class="chunk-card {chunk['type']}">
                <div class="chunk-meta">{chunk['meta']}<span class="score-pill">{chunk['score']}</span></div>
                {chunk['content']}
            </div>""", unsafe_allow_html=True)

        with st.expander("Retrieval diagnostics"):
            st.json({"embed_model":embed_model,"top_k":top_k,"reranker":use_reranker,"kg_fusion":use_kg,
                     "latency_ms":{"vector_search":round(random.uniform(18,60),1),"visual_search":round(random.uniform(25,80),1),
                                   "kg_traversal":round(random.uniform(10,35),1),
                                   "reranking":round(random.uniform(40,120),1) if use_reranker else "skipped",
                                   "generation":round(random.uniform(300,900),1)}})
