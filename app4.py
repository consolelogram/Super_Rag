"""
Super RAG — Professional Multimodal Video Intelligence
Effects inspired by landonorris.com
"""

import streamlit as st
import streamlit.components.v1 as components
import time, random
from pathlib import Path

st.set_page_config(
    page_title="SuperRAG · Video Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════
#  CSS
# ═══════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
  --bg:       #070d19;
  --surf:     #0c1528;
  --surf2:    #111e35;
  --border:   #1c2e4a;
  --border2:  #243650;
  --accent:   #3d7fff;
  --accent2:  #6ea8fe;
  --green:    #22c55e;
  --amber:    #f59e0b;
  --red:      #ef4444;
  --text:     #d4e0f5;
  --text2:    #7a93b8;
  --text3:    #3a5070;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
  cursor: none !important;
}
/* New code - allows the real cursor on interactive elements */
html, body, .stApp {
  cursor: none !important;
}

/* Restore the real cursor over inputs and buttons so you don't get stuck */
button, input, [data-testid="stFileUploader"], label, a {
  cursor: auto !important;
}
.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surf) !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Brand ── */
.brand { padding: 20px 0 4px; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
.brand-name { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; color: #fff; }
.brand-name span { color: var(--accent); }
.brand-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; color: var(--text3);
  letter-spacing: 0.15em; text-transform: uppercase; margin-top: 3px;
}

/* ── Section heading ── */
.sh { display:flex; align-items:center; gap:10px; margin-bottom:14px; }
.sh-text {
  font-family:'JetBrains Mono',monospace;
  font-size:9px; font-weight:500; color:var(--text3);
  letter-spacing:0.2em; text-transform:uppercase; white-space:nowrap;
}
.sh-line { flex:1; height:1px; background:var(--border); }

/* ── Animated page title ── */
.page-title {
  overflow: hidden;
  margin-bottom: 2px;
}
.page-title-inner {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: #fff;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25em;
}
.word {
  display: inline-block;
  overflow: hidden;
}
.word span {
  display: inline-block;
  transform: translateY(110%);
  animation: word-up 0.7s cubic-bezier(0.16,1,0.3,1) forwards;
}
.word:nth-child(1) span { animation-delay: 0.05s; }
.word:nth-child(2) span { animation-delay: 0.15s; }
.word:nth-child(3) span { animation-delay: 0.25s; }
.word:nth-child(4) span { animation-delay: 0.35s; }
@keyframes word-up {
  to { transform: translateY(0); }
}

/* ── Stagger fade-in for cards ── */
.fade-in {
  opacity: 0;
  transform: translateY(18px);
  animation: fade-up 0.55s cubic-bezier(0.16,1,0.3,1) forwards;
}
.fade-in:nth-child(1) { animation-delay: 0.05s; }
.fade-in:nth-child(2) { animation-delay: 0.12s; }
.fade-in:nth-child(3) { animation-delay: 0.19s; }
.fade-in:nth-child(4) { animation-delay: 0.26s; }
.fade-in:nth-child(5) { animation-delay: 0.33s; }
.fade-in:nth-child(6) { animation-delay: 0.40s; }
.fade-in:nth-child(7) { animation-delay: 0.47s; }
@keyframes fade-up {
  to { opacity:1; transform:translateY(0); }
}

/* ── Pipeline cards ── */
.pc {
  background: var(--surf);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px 12px 18px;
  margin-bottom: 6px;
  position: relative; overflow: hidden;
  transition: border-color 0.25s, box-shadow 0.25s, background 0.25s;
}
.pc::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
  background:var(--border2); border-radius:3px 0 0 3px;
  transition:background 0.25s, box-shadow 0.25s;
}
.pc.active {
  border-color:rgba(61,127,255,0.4); background:rgba(61,127,255,0.04);
}
.pc.active::before { background:var(--accent); box-shadow:0 0 8px rgba(61,127,255,0.6); }
.pc.active::after {
  content:''; position:absolute; top:0; bottom:0; left:-100%; width:50%;
  background:linear-gradient(90deg,transparent,rgba(61,127,255,0.06),transparent);
  animation:shimmer 1.8s linear infinite;
}
.pc.done { border-color:rgba(34,197,94,0.2); }
.pc.done::before { background:var(--green); }
.pc.error::before { background:var(--red); }

@keyframes shimmer { 0%{left:-100%} 100%{left:200%} }
@keyframes pulse   { 0%,100%{opacity:1} 50%{opacity:0.4} }

.pc-num { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3); letter-spacing:0.12em; margin-bottom:2px; }
.pc-name { font-size:12px; font-weight:600; color:var(--text); }
.pc-status { font-family:'JetBrains Mono',monospace; font-size:10px; margin-top:3px; }
.pc-status.idle   { color:var(--text3); }
.pc-status.active { color:var(--accent2); animation:pulse 1.2s ease infinite; }
.pc-status.done   { color:var(--green); }
.pc-status.error  { color:var(--red); }
.pc-icon { position:absolute; right:12px; top:50%; transform:translateY(-50%); font-size:16px; opacity:0.3; transition:opacity 0.25s; }
.pc.done .pc-icon  { opacity:0.9; }
.pc.active .pc-icon { opacity:0.9; animation:bob 2s ease-in-out infinite; }
@keyframes bob { 0%,100%{transform:translateY(-50%)} 50%{transform:translateY(-58%)} }

/* ── Stat cards ── */
.stat-row { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin:14px 0 0; }
.sc {
  background:var(--surf); border:1px solid var(--border);
  border-radius:8px; padding:14px 12px; text-align:center; position:relative; overflow:hidden;
}
.sc::after {
  content:''; position:absolute; inset:0;
  background:radial-gradient(ellipse at 50% -20%,rgba(61,127,255,0.07) 0%,transparent 65%);
  pointer-events:none;
}
.sc-val { font-size:24px; font-weight:700; color:#fff; letter-spacing:-0.04em; line-height:1; }
.sc-lbl { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3); text-transform:uppercase; letter-spacing:0.15em; margin-top:5px; }

/* ── Chat ── */
.chat-wrap { background:var(--surf); border:1px solid var(--border); border-radius:10px; overflow:hidden; }
.chat-hdr {
  background:var(--surf2); border-bottom:1px solid var(--border);
  padding:11px 16px; display:flex; align-items:center; gap:8px;
}
.chat-hdr-dot { width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 6px var(--green); animation:pulse 2.5s ease infinite; }
.chat-hdr-title { font-size:12px; font-weight:600; color:var(--text); letter-spacing:-0.01em; }
.chat-hdr-badge {
  margin-left:auto; font-family:'JetBrains Mono',monospace;
  font-size:9px; color:var(--text3); background:var(--bg);
  border:1px solid var(--border); border-radius:20px; padding:2px 8px;
}
.chat-body { padding:16px; max-height:400px; overflow-y:auto; }

.msg-u { display:flex; justify-content:flex-end; margin-bottom:12px; animation:fadein 0.25s ease; }
.msg-u .bbl {
  background:var(--accent); border-radius:12px 12px 2px 12px;
  padding:9px 13px; max-width:72%; font-size:13px; line-height:1.6; color:#fff;
}
.msg-a { display:flex; gap:9px; margin-bottom:12px; animation:fadein 0.25s ease; align-items:flex-start; }
.msg-a .av {
  width:28px; height:28px; flex-shrink:0;
  background:var(--surf2); border:1px solid var(--border2);
  border-radius:7px; display:flex; align-items:center; justify-content:center;
  font-size:12px; color:var(--accent2);
}
.msg-a .bbl {
  background:var(--bg); border:1px solid var(--border);
  border-radius:2px 12px 12px 12px;
  padding:9px 13px; max-width:82%; font-size:13px; line-height:1.7; color:var(--text);
}
@keyframes fadein { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none} }

/* ── Source tags ── */
.srcs { display:flex; flex-wrap:wrap; gap:5px; margin-top:9px; }
.stag { font-family:'JetBrains Mono',monospace; font-size:9px; border-radius:4px; padding:2px 8px; cursor:default; }
.stag.text   { background:rgba(61,127,255,0.1);  border:1px solid rgba(61,127,255,0.25); color:var(--accent2); }
.stag.visual { background:rgba(139,92,246,0.1);  border:1px solid rgba(139,92,246,0.25); color:#a78bfa; }
.stag.kg     { background:rgba(245,158,11,0.1);  border:1px solid rgba(245,158,11,0.25); color:#fcd34d; }

/* ── Chunk cards ── */
.ck {
  background:var(--bg); border:1px solid var(--border); border-radius:8px;
  padding:11px 14px; margin-bottom:7px;
  font-size:12px; line-height:1.7; color:var(--text2);
  position:relative; overflow:hidden; transition:border-color 0.2s,color 0.2s;
}
.ck:hover { border-color:var(--border2); color:var(--text); }
.ck::before { content:''; position:absolute; left:0; top:0; bottom:0; width:3px; }
.ck.text::before   { background:var(--accent); }
.ck.visual::before { background:#8b5cf6; }
.ck.kg::before     { background:var(--amber); }
.ck-meta { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3); margin-bottom:5px; display:flex; align-items:center; gap:8px; }
.ck-score { background:var(--surf2); border:1px solid var(--border); border-radius:4px; padding:1px 6px; color:var(--green); font-size:9px; }

/* ── Mag button ── */
.stButton > button {
  font-family:'Inter',sans-serif !important; font-size:13px !important; font-weight:600 !important;
  background:var(--accent) !important; color:#fff !important;
  border:none !important; border-radius:8px !important;
  padding:10px 20px !important; width:100%;
  letter-spacing:-0.01em !important;
  box-shadow:0 1px 3px rgba(0,0,0,0.3),0 4px 16px rgba(61,127,255,0.2) !important;
  transition:box-shadow 0.18s ease, background 0.18s ease !important;
  position:relative; overflow:hidden;
}
.stButton > button:hover {
  background:#5590ff !important;
  box-shadow:0 2px 6px rgba(0,0,0,0.3),0 8px 28px rgba(61,127,255,0.4) !important;
}
.stButton > button:disabled {
  background:var(--surf2) !important; color:var(--text3) !important; box-shadow:none !important;
}

/* ── Input ── */
.stTextInput > div > div > input {
  background:var(--surf) !important; border:1px solid var(--border) !important;
  border-radius:8px !important; color:var(--text) !important;
  font-family:'Inter',sans-serif !important; font-size:13px !important;
  padding:10px 14px !important; transition:border-color 0.2s,box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
  border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(61,127,255,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color:var(--text3) !important; }

/* ── Selects / sliders ── */
.stSelectbox > div > div {
  background:var(--bg) !important; border:1px solid var(--border) !important;
  border-radius:6px !important; color:var(--text) !important; font-size:13px !important;
}
.stSlider > div > div > div > div { background:var(--accent) !important; }
[data-testid="stSidebar"] label,.stSlider label,.stSelectbox label { color:var(--text2) !important; font-size:12px !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background:var(--surf) !important; border:1px dashed var(--border2) !important;
  border-radius:10px !important; transition:border-color 0.2s,box-shadow 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(61,127,255,0.08) !important;
}

/* ── Progress / expander ── */
.stProgress > div > div > div > div { background:linear-gradient(90deg,var(--accent),#60a5fa) !important; border-radius:4px !important; }
.streamlit-expanderHeader {
  background:var(--surf) !important; border:1px solid var(--border) !important; border-radius:8px !important;
  font-family:'JetBrains Mono',monospace !important; font-size:11px !important; color:var(--text2) !important;
}

/* ── Misc ── */
.vw { border:1px solid var(--border); border-radius:8px; overflow:hidden; background:#000; margin-bottom:10px; }
.wbox { background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.2); border-left:3px solid var(--amber); border-radius:6px; padding:10px 13px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#d4a017; margin-bottom:12px; }
.drop-zone { border:1px dashed var(--border2); border-radius:10px; padding:36px 20px; text-align:center; background:var(--surf); margin-bottom:14px; }
.drop-icon { font-size:26px; margin-bottom:8px; opacity:0.5; }
.drop-title { font-size:13px; font-weight:600; color:var(--text2); margin-bottom:4px; }
.drop-sub { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3); letter-spacing:0.12em; }
.chat-empty { text-align:center; padding:44px 20px; }
.chat-empty-icon { font-size:26px; margin-bottom:10px; opacity:0.4; }
.chat-empty-txt { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--text3); letter-spacing:0.1em; }
.cfg-label { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3); letter-spacing:0.18em; text-transform:uppercase; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid var(--border); }
hr { border:none; border-top:1px solid var(--border); margin:14px 0; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  ALL JS EFFECTS (single component call)
# ═══════════════════════════════════════
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
/* ── Custom Cursor ── */
#cursor-dot {
  position: fixed;
  width: 6px; height: 6px;
  background: #fff;
  border-radius: 50%;
  pointer-events: none;
  z-index: 999999;
  transform: translate(-50%, -50%);
  transition: transform 0.08s ease, background 0.2s;
  mix-blend-mode: difference;
}
#cursor-ring {
  position: fixed;
  width: 32px; height: 32px;
  border: 1.5px solid rgba(255,255,255,0.45);
  border-radius: 50%;
  pointer-events: none;
  z-index: 9999999;
  transform: translate(-50%, -50%);
  transition: width 0.25s ease, height 0.25s ease, border-color 0.25s ease, opacity 0.25s;
  mix-blend-mode: difference;
}
body.cursor-hover #cursor-ring {
  width: 48px; height: 48px;
  border-color: rgba(61,127,255,0.7);
}
body.cursor-click #cursor-dot { transform:translate(-50%,-50%) scale(1.8); }

/* ── Page loader ── */
#loader {
  position: fixed; inset: 0;
  background: #070d19;
  z-index: 999999;
  display: flex; align-items: center; justify-content: center;
  flex-direction: column;
  gap: 16px;
  transition: opacity 0.6s ease;
}
#loader.hide { opacity: 0; pointer-events: none; }
.loader-logo {
  font-family: 'Inter', sans-serif;
  font-size: 22px; font-weight: 700;
  color: #fff; letter-spacing: -0.03em;
  opacity: 0;
  animation: logo-in 0.5s 0.2s cubic-bezier(0.16,1,0.3,1) forwards;
}
.loader-logo span { color: #3d7fff; }
.loader-bar-wrap {
  width: 180px; height: 2px;
  background: #1c2e4a; border-radius: 2px; overflow: hidden;
}
.loader-bar {
  height: 100%; width: 0%;
  background: linear-gradient(90deg, #3d7fff, #60a5fa);
  border-radius: 2px;
  animation: bar-fill 1.2s 0.3s cubic-bezier(0.4,0,0.2,1) forwards;
}
.loader-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; color: #3a5070;
  letter-spacing: 0.2em; text-transform: uppercase;
  opacity: 0; animation: logo-in 0.4s 0.5s forwards;
}
@keyframes logo-in { to { opacity: 1; } }
@keyframes bar-fill { to { width: 100%; } }

/* ── Marquee ── */
.marquee-wrap {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 28px;
  background: #0c1528;
  border-top: 1px solid #1c2e4a;
  overflow: hidden;
  z-index: 9000;
  display: flex; align-items: center;
}
.marquee-track {
  display: flex; gap: 0;
  animation: marquee 28s linear infinite;
  white-space: nowrap;
}
.marquee-item {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; color: #3a5070;
  letter-spacing: 0.2em; text-transform: uppercase;
  padding: 0 32px;
}
.marquee-item b { color: #3d7fff; font-weight: 500; }
.marquee-sep { color: #1c2e4a; padding: 0 4px; }
@keyframes marquee { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
</style>
</head>
<body>

<!-- Cursor -->
<div id="cursor-dot"></div>
<div id="cursor-ring"></div>

<!-- Page Loader -->
<div id="loader">
  <div class="loader-logo">Super<span>RAG</span></div>
  <div class="loader-bar-wrap"><div class="loader-bar"></div></div>
  <div class="loader-tag">Multimodal Video Intelligence</div>
</div>

<!-- Marquee -->
<div class="marquee-wrap">
  <div class="marquee-track" id="mq"></div>
</div>

<script>
// ── Loader ──
setTimeout(() => {
  const loader = document.getElementById('loader');
  if (loader) {
    loader.classList.add('hide');
    setTimeout(() => loader.remove(), 700);
  }
}, 1600);

// ── Cursor ──
const dot  = document.getElementById('cursor-dot');
const ring = document.getElementById('cursor-ring');
let mx = -100, my = -100;
let rx = -100, ry = -100;

document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
document.addEventListener('mousedown', () => document.body.classList.add('cursor-click'));
document.addEventListener('mouseup',   () => document.body.classList.remove('cursor-click'));

// Smooth ring follow
function animCursor() {
  rx += (mx - rx) * 0.12;
  ry += (my - ry) * 0.12;
  dot.style.left  = mx + 'px';
  dot.style.top   = my + 'px';
  ring.style.left = rx + 'px';
  ring.style.top  = ry + 'px';
  requestAnimationFrame(animCursor);
}
animCursor();

// Hover detection — broadcast to parent
function broadcastHover(on) {
  try { window.parent.document.body.classList.toggle('cursor-hover', on); } catch(e){}
}
document.addEventListener('mouseover',  e => { if(e.target.tagName==='BUTTON'||e.target.tagName==='A') broadcastHover(true); });
document.addEventListener('mouseout',   e => { if(e.target.tagName==='BUTTON'||e.target.tagName==='A') broadcastHover(false); });

// ── Magnetic buttons ──
function initMagnetic() {
  const btns = window.parent.document.querySelectorAll('button, [data-testid="stFileUploader"]');
  btns.forEach(btn => {
    btn.addEventListener('mousemove', function(e) {
      const r = this.getBoundingClientRect();
      const cx = r.left + r.width  / 2;
      const cy = r.top  + r.height / 2;
      const dx = (e.clientX - cx) * 0.25;
      const dy = (e.clientY - cy) * 0.25;
      this.style.transform = `translate(${dx}px, ${dy}px)`;
    });
    btn.addEventListener('mouseleave', function() {
      this.style.transform = '';
      this.style.transition = 'transform 0.4s cubic-bezier(0.34,1.56,0.64,1)';
    });
    btn.addEventListener('mouseenter', function() {
      this.style.transition = 'transform 0.1s ease';
    });
  });
}

// Retry magnetic init until buttons exist
let magRetry = 0;
function tryMagnetic() {
  try {
    const btns = window.parent.document.querySelectorAll('button');
    if (btns.length > 0) { initMagnetic(); }
    else if (magRetry++ < 20) { setTimeout(tryMagnetic, 300); }
  } catch(e) {}
}
setTimeout(tryMagnetic, 800);

// ── Scroll-triggered animations ──
function initScrollReveal() {
  try {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    const cards = window.parent.document.querySelectorAll('.pc, .sc, .ck, .chat-wrap');
    cards.forEach((el, i) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(16px)';
      el.style.transition = `opacity 0.55s ${i*0.07}s cubic-bezier(0.16,1,0.3,1), transform 0.55s ${i*0.07}s cubic-bezier(0.16,1,0.3,1)`;
      observer.observe(el);
    });
  } catch(e) {}
}
setTimeout(initScrollReveal, 1200);

// ── Repelling particles background ──
const cvs = document.createElement('canvas');
cvs.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;';
document.body.appendChild(cvs);
const ctx = cvs.getContext('2d');

function resize() { cvs.width = window.innerWidth; cvs.height = window.innerHeight; }
resize(); window.addEventListener('resize', resize);

const mouse = { x: -9999, y: -9999 };
window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });

const N = 65, REPEL_R = 110, REPEL_F = 0.16;
const particles = Array.from({ length: N }, () => {
  const x = Math.random() * cvs.width;
  const y = Math.random() * cvs.height;
  return { x, y, ox:x, oy:y, vx:0, vy:0, r:Math.random()*1.3+0.5, alpha:Math.random()*0.28+0.06 };
});

function tick() {
  ctx.clearRect(0, 0, cvs.width, cvs.height);
  particles.forEach(p => {
    const dx = p.x - mouse.x, dy = p.y - mouse.y;
    const d = Math.sqrt(dx*dx+dy*dy);
    if (d < REPEL_R && d > 0) {
      const f = (REPEL_R-d)/REPEL_R;
      p.vx += (dx/d)*f*REPEL_F;
      p.vy += (dy/d)*f*REPEL_F;
    }
    p.vx = (p.vx + (p.ox-p.x)*0.016) * 0.88;
    p.vy = (p.vy + (p.oy-p.y)*0.016) * 0.88;
    p.x += p.vx; p.y += p.vy;
    p.ox += (Math.random()-.5)*0.15;
    p.oy += (Math.random()-.5)*0.15;
    p.ox = Math.max(10, Math.min(cvs.width-10, p.ox));
    p.oy = Math.max(10, Math.min(cvs.height-10, p.oy));
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
    ctx.fillStyle = `rgba(100,160,255,${p.alpha})`;
    ctx.fill();
  });
  for (let i=0;i<N;i++) for (let j=i+1;j<N;j++) {
    const dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
    const d=Math.sqrt(dx*dx+dy*dy);
    if (d<105) {
      ctx.beginPath();
      ctx.moveTo(particles[i].x,particles[i].y);
      ctx.lineTo(particles[j].x,particles[j].y);
      ctx.strokeStyle=`rgba(61,127,255,${(1-d/105)*0.1})`;
      ctx.lineWidth=0.7; ctx.stroke();
    }
  }
  requestAnimationFrame(tick);
}
tick();

// ── Marquee ──
const items = [
  '<span class="marquee-item"><b>SuperRAG</b> — Multimodal Video Intelligence</span><span class="marquee-sep">·</span>',
  '<span class="marquee-item">Speech-to-Text <b>·</b> Vision Language Models <b>·</b> Knowledge Graphs</span><span class="marquee-sep">·</span>',
  '<span class="marquee-item">Vector DB <b>·</b> Visual DB <b>·</b> Cross-Encoder Reranking</span><span class="marquee-sep">·</span>',
  '<span class="marquee-item"><b>Whisper</b> · CLIP · FAISS · ChromaDB · Ollama</span><span class="marquee-sep">·</span>',
  '<span class="marquee-item">Ask anything about your <b>video</b></span><span class="marquee-sep">·</span>',
];
const mq = document.getElementById('mq');
// duplicate for seamless loop
const full = [...items,...items,...items,...items].join('');
mq.innerHTML = full + full;
</script>
</body>
</html>
""", height=0)


# ═══════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════
PHASE_IDS = ["splicer","stt","vlm","kg","vectordb","visualdb","rag"]
for k,v in {
    "pipeline_ran":False,"processing":False,
    "phase_states":{p:"idle" for p in PHASE_IDS},
    "phase_msgs":{p:"" for p in PHASE_IDS},
    "stats":{"chunks":0,"entities":0,"vectors":0},
    "chat_history":[],"video_name":"",
}.items():
    if k not in st.session_state: st.session_state[k]=v

PHASE_META=[
    ("splicer","01","Video Splicer","Splitting video into temporal chunks","▣"),
    ("stt","02","Speech-to-Text","Transcribing audio via Whisper","◎"),
    ("vlm","03","Vision-Language Model","Analysing frames with VLM","◈"),
    ("kg","04","Knowledge Graph","Extracting entities & relations","⬡"),
    ("vectordb","05","Vector Database","Embedding & indexing text chunks","◫"),
    ("visualdb","06","Visual Database","Embedding visual features (CLIP)","◰"),
    ("rag","07","RAG Engine","Initialising retrieval engine","◆"),
]
STATUS={"idle":"—","active":"●","done":"✓","error":"✗"}
MOCKS=[
    {"text":"At 02:14, the speaker explains dense passage retrieval — how a vector index is queried at inference time to surface relevant passages before generation. They contrast this with pure parametric memory and discuss latency trade-offs for production deployments.",
     "sources":[{"label":"02:14 – 02:38","type":"text"},{"label":"Frame 134","type":"visual"},{"label":"LLM → retrieval","type":"kg"}]},
    {"text":"Three primary limitations are addressed: (1) retrieval latency on large corpora, (2) context window constraints, and (3) semantic drift when query embeddings fail to align with the indexed passage distribution. Hybrid BM25 + dense retrieval is proposed as a mitigation.",
     "sources":[{"label":"05:50 – 06:20","type":"text"},{"label":"07:02 – 07:15","type":"text"},{"label":"Entity: BM25","type":"kg"}]},
    {"text":"The architecture diagram at 04:30 shows a two-stage pipeline: a coarse ANN retriever selects top-k candidates, then a cross-encoder re-ranker scores each against the query — yielding significantly higher precision without exhaustive dense search over the entire corpus.",
     "sources":[{"label":"04:30 – 04:55","type":"text"},{"label":"Frame 271","type":"visual"}]},
]

def run_pipeline(name):
    for i,(pid,*_) in enumerate(PHASE_META):
        st.session_state.phase_states[pid]="active"
        st.session_state.phase_msgs[pid]="Running…"
        time.sleep([0.9,2.0,2.3,1.5,1.1,0.9,0.6][i])
        st.session_state.phase_states[pid]="done"
        st.session_state.phase_msgs[pid]="Complete"
    st.session_state.stats={"chunks":random.randint(18,45),"entities":random.randint(120,340),"vectors":random.randint(800,2400)}
    st.session_state.pipeline_ran=True
    st.session_state.processing=False

def render_phase(pid,num,name,desc,icon):
    state=st.session_state.phase_states[pid]
    msg=st.session_state.phase_msgs[pid]
    st.markdown(f"""
    <div class="pc {state} fade-in">
      <div class="pc-num">PHASE {num}</div>
      <div class="pc-name">{name}</div>
      <div class="pc-status {state}">{STATUS[state]}&ensp;{msg if msg else desc}</div>
      <div class="pc-icon">{icon}</div>
    </div>""",unsafe_allow_html=True)

def waveform(active=False):
    col="#3d7fff" if active else "#1c2e4a"
    anim="animation:wv var(--d) ease-in-out infinite alternate;" if active else ""
    bars="".join(f'<div style="width:3px;border-radius:2px;flex-shrink:0;background:{col};height:{3+abs(16-i)*1.5:.0f}px;--d:{0.28+i*0.055:.2f}s;{anim}"></div>' for i in range(32))
    components.html(f"""
    <style>@keyframes wv{{from{{height:3px}}to{{height:var(--h,14px)}}}}</style>
    <div style="display:flex;gap:2px;align-items:center;height:30px;padding:4px 10px;
                background:#0c1528;border:1px solid #1c2e4a;border-radius:6px;margin:6px 0;overflow:hidden;">
      {bars}
    </div>""",height=40)

def kg_canvas():
    components.html("""
<canvas id="kg" style="width:100%;height:118px;display:block;border-radius:6px;"></canvas>
<script>
(function(){
  const c=document.getElementById('kg');
  c.width=c.parentElement.offsetWidth||260; c.height=118;
  const ctx=c.getContext('2d'),W=c.width,H=118;
  const labels=['RAG','VLM','Whisper','FAISS','Chunks','Entities','KG','CLIP'];
  const cols=['#3d7fff','#60a5fa','#22c55e','#f59e0b','#60a5fa','#3d7fff','#22c55e','#8b5cf6'];
  const nodes=labels.map((l,i)=>({x:28+(i%4)*((W-56)/3),y:22+Math.floor(i/4)*68,vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.25,label:l,col:cols[i],phase:Math.random()*Math.PI*2}));
  const edges=[[0,1],[0,2],[0,3],[0,4],[4,2],[4,6],[6,5],[1,7],[3,4],[5,6]];
  function frame(){
    ctx.clearRect(0,0,W,H);
    nodes.forEach(n=>{n.x+=n.vx;n.y+=n.vy;n.phase+=0.016;if(n.x<14||n.x>W-14)n.vx*=-1;if(n.y<14||n.y>H-14)n.vy*=-1;});
    edges.forEach(([a,b])=>{const g=(Math.sin(nodes[a].phase)+1)/2;ctx.beginPath();ctx.moveTo(nodes[a].x,nodes[a].y);ctx.lineTo(nodes[b].x,nodes[b].y);ctx.strokeStyle=nodes[a].col;ctx.globalAlpha=0.08+g*0.1;ctx.lineWidth=.7;ctx.stroke();});
    nodes.forEach(n=>{const g=(Math.sin(n.phase)+1)/2;ctx.globalAlpha=0.5+g*0.4;ctx.beginPath();ctx.arc(n.x,n.y,3.5+g*1.5,0,Math.PI*2);ctx.fillStyle=n.col;ctx.shadowColor=n.col;ctx.shadowBlur=5+g*9;ctx.fill();ctx.shadowBlur=0;ctx.globalAlpha=0.5;ctx.fillStyle='#7a93b8';ctx.font='8px JetBrains Mono,monospace';ctx.textAlign='center';ctx.fillText(n.label,n.x,n.y-8);});
    ctx.globalAlpha=1;requestAnimationFrame(frame);
  }
  frame();
})();
</script>""",height=126)


# ═══════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-name">Super<span>RAG</span></div>
      <div class="brand-tag">Multimodal Video Intelligence</div>
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="cfg-label">Ingestion</div>',unsafe_allow_html=True)
    chunk_size    = st.slider("Chunk size (sec)",5,60,15,5)
    whisper_model = st.selectbox("Whisper model",["tiny","base","small","medium","large"],index=2)
    vlm_backend   = st.selectbox("VLM backend",["LLaVA-7B","Qwen-VL","InternVL2"])

    st.markdown('<div class="cfg-label" style="margin-top:18px">Retrieval</div>',unsafe_allow_html=True)
    embed_model  = st.selectbox("Embedding model",["nomic-embed-text","bge-large-en","text-embedding-3-small"])
    top_k        = st.slider("Top-k",1,20,5)
    use_reranker = st.toggle("Cross-encoder reranker",value=True)
    use_kg       = st.toggle("Knowledge graph fusion",value=True)

    st.markdown('<div class="cfg-label" style="margin-top:18px">Knowledge Graph</div>',unsafe_allow_html=True)
    kg_canvas()


# ═══════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════
left, right = st.columns([1,1.9],gap="large")

with left:
    st.markdown("""
    <div class="page-title">
      <div class="page-title-inner">
        <div class="word"><span>Video</span></div>
        <div class="word"><span>Input</span></div>
      </div>
    </div>""",unsafe_allow_html=True)
    st.markdown('<div class="sh"><div class="sh-line"></div></div>',unsafe_allow_html=True)

    uploaded=st.file_uploader("video",type=["mp4","mov","avi","mkv","webm"],label_visibility="collapsed")

    if uploaded:
        tmp=Path("/tmp")/uploaded.name
        tmp.write_bytes(uploaded.read())
        st.session_state.video_name=uploaded.name
        st.markdown('<div class="vw">',unsafe_allow_html=True)
        st.video(str(tmp))
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:var(--text3);margin-bottom:12px;">📁 {uploaded.name}</div>',unsafe_allow_html=True)
        if st.button("▶  Run Pipeline",disabled=st.session_state.processing):
            for pid in PHASE_IDS:
                st.session_state.phase_states[pid]="idle"
                st.session_state.phase_msgs[pid]=""
            st.session_state.pipeline_ran=False
            st.session_state.processing=True
            st.session_state.chat_history=[]
            st.rerun()
    else:
        st.markdown("""
        <div class="drop-zone">
          <div class="drop-icon">▣</div>
          <div class="drop-title">Drop your video here</div>
          <div class="drop-sub">MP4 · MOV · AVI · MKV · WEBM</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("""
    <div class="sh" style="margin-top:6px">
      <div class="sh-text">Pipeline</div>
      <div class="sh-line"></div>
    </div>""",unsafe_allow_html=True)

    if st.session_state.processing:
        for pid,num,name,desc,icon in PHASE_META: render_phase(pid,num,name,desc,icon)
        waveform(active=(st.session_state.phase_states.get("stt")=="active"))
        run_pipeline(st.session_state.video_name)
        st.rerun()
    else:
        for pid,num,name,desc,icon in PHASE_META: render_phase(pid,num,name,desc,icon)
        if st.session_state.phase_states.get("stt")=="done": waveform(active=False)

    if st.session_state.pipeline_ran:
        s=st.session_state.stats
        st.markdown(f"""
        <div class="stat-row">
          <div class="sc fade-in"><div class="sc-val">{s['chunks']}</div><div class="sc-lbl">Chunks</div></div>
          <div class="sc fade-in"><div class="sc-val">{s['entities']}</div><div class="sc-lbl">Entities</div></div>
          <div class="sc fade-in"><div class="sc-val">{s['vectors']}</div><div class="sc-lbl">Vectors</div></div>
        </div>""",unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="page-title">
      <div class="page-title-inner">
        <div class="word"><span>Query</span></div>
        <div class="word"><span>Interface</span></div>
      </div>
    </div>""",unsafe_allow_html=True)
    st.markdown('<div class="sh"><div class="sh-line"></div></div>',unsafe_allow_html=True)

    if not st.session_state.pipeline_ran:
        st.markdown('<div class="wbox">Run the pipeline first to activate the query interface.</div>',unsafe_allow_html=True)

    hist_count=len([t for t in st.session_state.chat_history if t["role"]=="user"])
    chat_inner=""
    if not st.session_state.chat_history:
        chat_inner='<div class="chat-empty"><div class="chat-empty-icon">◈</div><div class="chat-empty-txt">Ask anything about the video</div></div>'
    else:
        for turn in st.session_state.chat_history:
            if turn["role"]=="user":
                chat_inner+=f'<div class="msg-u"><div class="bbl">{turn["content"]}</div></div>'
            else:
                srcs=""
                if "sources" in turn:
                    srcs='<div class="srcs">'+"".join(f'<span class="stag {s["type"]}">{s["label"]}</span>' for s in turn["sources"])+'</div>'
                chat_inner+=f'<div class="msg-a"><div class="av">◈</div><div class="bbl">{turn["content"]}{srcs}</div></div>'

    st.markdown(f"""
    <div class="chat-wrap">
      <div class="chat-hdr">
        <div class="chat-hdr-dot"></div>
        <div class="chat-hdr-title">RAG Session</div>
        <div class="chat-hdr-badge">{hist_count} queries</div>
      </div>
      <div class="chat-body">{chat_inner}</div>
    </div>""",unsafe_allow_html=True)

    c1,c2=st.columns([5,1])
    with c1:
        query=st.text_input("q",placeholder="What topics are discussed? What happens at 3:20?",
                            label_visibility="collapsed",disabled=not st.session_state.pipeline_ran,key="query_input")
    with c2:
        send=st.button("Send",disabled=not st.session_state.pipeline_ran)

    if send and query:
        st.session_state.chat_history.append({"role":"user","content":query})
        with st.spinner("Retrieving…"):
            time.sleep(0.6)
            result=random.choice(MOCKS)
        st.session_state.chat_history.append({"role":"assistant","content":result["text"],"sources":result["sources"]})
        st.rerun()

    if st.session_state.pipeline_ran and st.session_state.chat_history:
        st.markdown("---")
        st.markdown('<div class="sh"><div class="sh-text">Retrieved Context</div><div class="sh-line"></div></div>',unsafe_allow_html=True)
        for ck in [
            {"type":"text","meta":f"Chunk #{random.randint(10,30)} · {random.randint(1,8):02d}:{random.randint(0,59):02d}","score":round(random.uniform(0.84,0.97),3),"content":"Speaker introduces dense passage retrieval, contrasting embedding similarity with lexical overlap. Semantic vectors capture query intent more reliably than BM25 on out-of-vocabulary terms."},
            {"type":"visual","meta":f"Frame {random.randint(100,400)} · t={random.randint(60,400)}s","score":round(random.uniform(0.71,0.88),3),"content":"Slide: two-stage retrieval — coarse ANN retrieval → cross-encoder re-ranking. Diagram: Query Encoder → FAISS Index → Re-ranker → Generator."},
            {"type":"kg","meta":f"KG subgraph · {random.randint(3,8)} hops","score":round(random.uniform(0.62,0.82),3),"content":"RAG → uses → Dense Retrieval → implemented with → FAISS. BM25 ←[alt]→ Dense Retrieval. Cross-encoder ←[improves]→ Precision@k."},
        ]:
            st.markdown(f"""
            <div class="ck {ck['type']} fade-in">
              <div class="ck-meta">{ck['meta']}<span class="ck-score">{ck['score']}</span></div>
              {ck['content']}
            </div>""",unsafe_allow_html=True)

        with st.expander("Retrieval diagnostics"):
            st.json({"embedding_model":embed_model,"top_k":top_k,"reranker":use_reranker,"kg_fusion":use_kg,
                     "latency_ms":{"vector_search":round(random.uniform(18,55),1),"visual_search":round(random.uniform(22,70),1),
                                   "kg_traversal":round(random.uniform(8,30),1),
                                   "reranking":round(random.uniform(35,110),1) if use_reranker else "skipped",
                                   "generation":round(random.uniform(280,850),1)}})
