from main import *

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import math

# ─────────────────────────── THEME ───────────────────────────
BG        = "#0f172a"
PANEL     = "#1e293b"
PANEL2    = "#273548"
ACCENT    = "#2563eb"
GREEN     = "#22c55e"
ORANGE    = "#f59e0b"
PURPLE    = "#9333ea"
RED       = "#ef4444"
FG        = "#f8fafc"
MUTED     = "#94a3b8"
WHITE_BG  = "#f1f5f9"
DARK_TEXT = "#0f172a"
BTN_STYLE = dict(relief="flat", bd=0, cursor="hand2")

GANTT_COLORS = ["#2563eb","#f59e0b","#22c55e","#9333ea","#ef4444",
                "#06b6d4","#ec4899","#84cc16","#f97316","#a78bfa"]

# ─────────────────────────── ROOT ────────────────────────────
root = tk.Tk()
root.title("Operating System Simulator")
root.geometry("1400x840")
root.configure(bg=BG)
root.resizable(True, True)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=PANEL, foreground=FG,
    fieldbackground=PANEL, rowheight=26,
    borderwidth=0, font=("Segoe UI", 9))
style.configure("Treeview.Heading",
    background="#334155", foreground=FG,
    font=("Segoe UI", 9, "bold"), relief="flat")
style.map("Treeview", background=[("selected", ACCENT)])
style.configure("TCombobox", fieldbackground=PANEL,
    background=PANEL, foreground=FG, arrowcolor=FG)
style.map("TCombobox", fieldbackground=[("readonly", PANEL)])
style.configure("Horizontal.TScrollbar", background=PANEL,
    troughcolor=BG, borderwidth=0, arrowcolor=MUTED)
style.configure("Vertical.TScrollbar", background=PANEL,
    troughcolor=BG, borderwidth=0, arrowcolor=MUTED)

# ─────────────────────────── LAYOUT ──────────────────────────
sidebar = tk.Frame(root, bg=BG, width=215)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main_container = tk.Frame(root, bg=WHITE_BG)
main_container.pack(side="left", fill="both", expand=True)

pages = {}
sidebar_buttons = {}

def show_page(name):
    for f in pages.values():
        f.pack_forget()
    pages[name].pack(fill="both", expand=True)
    for btn_name, btn in sidebar_buttons.items():
        btn.configure(
            bg=ACCENT if btn_name == name else "#1e293b",
            fg="white" if btn_name == name else MUTED)

# ─────────────────────────── HELPERS ─────────────────────────
def dark_btn(parent, text, cmd, color=ACCENT, width=14, pad=(4,4)):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  width=width, **BTN_STYLE, padx=8, pady=5)
    b.bind("<Enter>", lambda e: b.config(bg=_darken(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b

def _darken(hex_color):
    h = hex_color.lstrip('#')
    r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    r,g,b = max(0,r-30),max(0,g-30),max(0,b-30)
    return f"#{r:02x}{g:02x}{b:02x}"

def entry_box(parent, default="", width=8):
    e = tk.Entry(parent, width=width, bg=PANEL2, fg=FG,
                 insertbackground=FG, relief="flat",
                 font=("Segoe UI", 10), bd=5)
    e.insert(0, default)
    return e

def combo_box(parent, values, width=18, default=0):
    cb = ttk.Combobox(parent, values=values, width=width,
                      state="readonly", font=("Segoe UI", 10))
    cb.current(default)
    return cb

def section_label(parent, text, bg=WHITE_BG):
    tk.Label(parent, text=text, bg=bg, fg=DARK_TEXT,
             font=("Segoe UI", 15, "bold")).pack(anchor="nw", padx=20, pady=(14,6))

def lbl(parent, text, bg=WHITE_BG, fg=DARK_TEXT, size=9, bold=False):
    font = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=font)

def make_tree(parent, columns, col_widths=None, height=7):
    t = ttk.Treeview(parent, columns=columns, show="headings", height=height)
    for i,c in enumerate(columns):
        t.heading(c, text=c)
        w = col_widths[i] if col_widths else 90
        t.column(c, width=w, anchor="center", minwidth=40)
    return t

# ═══════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════
dashboard = tk.Frame(main_container, bg=WHITE_BG)
pages["Dashboard"] = dashboard

section_label(dashboard, "Dashboard")

card_frame = tk.Frame(dashboard, bg=WHITE_BG)
card_frame.pack(fill="x", padx=14, pady=(0,8))
for i in range(4):
    card_frame.columnconfigure(i, weight=1)

card_data = [
    ("Total Processes",   "5",   ACCENT),
    ("Running Processes", "2",   GREEN),
    ("Waiting Processes", "3",   ORANGE),
    ("CPU Utilization",   "65%", PURPLE),
]
for i,(title,value,color) in enumerate(card_data):
    c = tk.Frame(card_frame, bg=color, height=100)
    c.grid(row=0, column=i, padx=6, sticky="nsew")
    c.pack_propagate(False)
    tk.Label(c, text=value, bg=color, fg="white",
             font=("Segoe UI",24,"bold")).pack(pady=(14,2))
    tk.Label(c, text=title, bg=color, fg="white",
             font=("Segoe UI",9)).pack()
    tk.Label(c, text="View Details", bg=color, fg="#bfdbfe",
             font=("Segoe UI",8,"underline")).pack()

# Mid row: sparkline + pie
mid = tk.Frame(dashboard, bg=WHITE_BG)
mid.pack(fill="x", padx=14, pady=4)

chart_frame = tk.Frame(mid, bg=PANEL)
chart_frame.pack(side="left", fill="both", expand=True, padx=(0,8))
lbl(chart_frame,"CPU Utilization",PANEL,FG,10,True).pack(anchor="nw",padx=10,pady=(8,0))
cpu_canvas = tk.Canvas(chart_frame, bg=PANEL, height=140, highlightthickness=0)
cpu_canvas.pack(fill="x", padx=10, pady=6)

def draw_sparkline():
    cpu_canvas.delete("all")
    w = cpu_canvas.winfo_width() or 400
    if w < 10: return
    h = 110
    pts = [65,72,58,80,70,90,75,65,82,68,74,60,85]
    for lvl,txt in [(0,"0%"),(25,"25%"),(50,"50%"),(75,"75%"),(100,"100%")]:
        y = h - (lvl/100)*h + 10
        cpu_canvas.create_line(0,y,w,y,fill="#334155",dash=(3,5))
        cpu_canvas.create_text(w-26,y-6,text=txt,fill=MUTED,font=("Segoe UI",7))
    n = len(pts)
    coords = []
    for i,v in enumerate(pts):
        coords += [i*(w/(n-1)), h-(v/100)*h+10]
    cpu_canvas.create_line(*coords,fill=ACCENT,width=2,smooth=True)
    for i,lbl_t in enumerate([0,10,20,30,40,50,60]):
        cpu_canvas.create_text(i*(w/6),h+16,text=str(lbl_t),fill=MUTED,font=("Segoe UI",7))

pie_frame = tk.Frame(mid, bg=PANEL, width=230)
pie_frame.pack(side="left")
pie_frame.pack_propagate(False)
lbl(pie_frame,"Process Status",PANEL,FG,10,True).pack(anchor="nw",padx=10,pady=(8,0))
pie_c = tk.Canvas(pie_frame, bg=PANEL, width=220, height=130, highlightthickness=0)
pie_c.pack()

def draw_pie():
    pie_c.delete("all")
    data = [("Running",2,GREEN),("Waiting",3,ORANGE),("Terminated",0,RED)]
    total = sum(d[1] for d in data) or 1
    start, cx, cy, r = -90, 70, 65, 52
    for name,val,clr in data:
        ext = (val/total)*360
        if ext > 0:
            pie_c.create_arc(cx-r,cy-r,cx+r,cy+r,start=start,extent=ext,fill=clr,outline="")
            start += ext
    for i,(name,val,clr) in enumerate(data):
        y = 24+i*30
        pie_c.create_rectangle(128,y,140,y+12,fill=clr,outline="")
        pie_c.create_text(144,y+6,text=f"{name} ({val})",fill=FG,font=("Segoe UI",8),anchor="w")

dashboard.after(250, draw_sparkline)
dashboard.after(250, draw_pie)

lbl(dashboard,"Recent Processes",WHITE_BG,DARK_TEXT,10,True).pack(anchor="nw",padx=20,pady=(8,2))
dash_tree = make_tree(dashboard,
    ("PID","Process Name","Status","Arrival Time","Burst Time","Priority"),
    [55,120,90,100,90,80], height=5)
dash_tree.pack(fill="x",padx=20,pady=(0,4))

for pid,name,status,arr,burst,pri in [
    ("P1","Process 1","Running","0","10","2"),
    ("P2","Process 2","Waiting","1","5","1"),
    ("P3","Process 3","Running","2","8","3"),
    ("P4","Process 4","Waiting","3","6","2"),
    ("P5","Process 5","Waiting","4","4","1"),
]:
    iid = dash_tree.insert("","end",values=(pid,name,status,arr,burst,pri))
    dash_tree.item(iid,tags=(status,))
dash_tree.tag_configure("Running",foreground=GREEN)
dash_tree.tag_configure("Waiting",foreground=ORANGE)

lbl(dashboard,"● System Ready",WHITE_BG,GREEN,9).pack(anchor="sw",padx=20,pady=6)

# ═══════════════════════════════════════════════════════════════
#  CPU SCHEDULING
# ═══════════════════════════════════════════════════════════════
cpu_page = tk.Frame(main_container, bg=WHITE_BG)
pages["CPU Scheduling"] = cpu_page

section_label(cpu_page, "CPU Scheduling – Gantt Chart")

# Controls
ctrl = tk.Frame(cpu_page, bg=WHITE_BG)
ctrl.pack(fill="x", padx=20, pady=(0,6))

lbl(ctrl,"Algorithm",WHITE_BG,DARK_TEXT,9,True).grid(row=0,column=0,padx=(0,4))
cpu_algo = combo_box(ctrl,["FCFS","Round Robin"],width=16)
cpu_algo.grid(row=0,column=1,padx=(0,16))
lbl(ctrl,"Time Quantum",WHITE_BG,DARK_TEXT,9,True).grid(row=0,column=2,padx=(0,4))
quantum_e = entry_box(ctrl,"2",width=5)
quantum_e.grid(row=0,column=3,padx=(0,16))

dark_btn(ctrl,"Add Process",  lambda:add_cpu_process(),  GREEN,  12).grid(row=0,column=4,padx=3)
dark_btn(ctrl,"Remove",       lambda:remove_cpu_process(),RED,    9).grid(row=0,column=5,padx=3)
dark_btn(ctrl,"Run",          lambda:run_cpu_scheduling(),ACCENT,10).grid(row=0,column=6,padx=3)
dark_btn(ctrl,"Reset",        lambda:reset_cpu(),         "#475569",8).grid(row=0,column=7,padx=3)

# Body: left = table, right = gantt+metrics
cpu_body = tk.Frame(cpu_page, bg=WHITE_BG)
cpu_body.pack(fill="both", expand=True, padx=20, pady=4)
cpu_body.columnconfigure(0, weight=1)
cpu_body.columnconfigure(1, weight=1)

# --- Left: Process Table ---
left_cpu = tk.Frame(cpu_body, bg=WHITE_BG)
left_cpu.grid(row=0, column=0, sticky="nsew", padx=(0,10))

lbl(left_cpu,"Process Table",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))
cpu_tree = make_tree(left_cpu,
    ("PID","Arrival Time","Burst Time","Priority"),
    [70,110,110,90], height=9)
cpu_tree.pack(fill="x")

default_procs = [("P1",0,5,2),("P2",1,3,1),("P3",2,8,3),("P4",3,6,2),("P5",4,4,1)]
for r in default_procs:
    cpu_tree.insert("","end",values=r)

cpu_counter = [6]

def get_cpu_procs():
    out = []
    for item in cpu_tree.get_children():
        v = cpu_tree.item(item,"values")
        try:
            out.append(Process(v[0], int(v[1]), int(v[2])))
        except (ValueError, IndexError):
            pass
    return out

def add_cpu_process():
    pid = f"P{cpu_counter[0]}"; cpu_counter[0] += 1
    cpu_tree.insert("","end",values=(pid,0,4,1))

def remove_cpu_process():
    for s in cpu_tree.selection(): cpu_tree.delete(s)

def reset_cpu():
    for item in cpu_tree.get_children(): cpu_tree.delete(item)
    for r in default_procs: cpu_tree.insert("","end",values=r)
    gantt_canvas.delete("all")
    gantt_time_canvas.delete("all")
    for v in metric_vars.values(): v.set("—")

# --- Right: Gantt + Metrics ---
right_cpu = tk.Frame(cpu_body, bg=WHITE_BG)
right_cpu.grid(row=0, column=1, sticky="nsew")

lbl(right_cpu,"Gantt Chart",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))

# Scrollable Gantt area
gantt_outer = tk.Frame(right_cpu, bg=PANEL, height=90)
gantt_outer.pack(fill="x")
gantt_outer.pack_propagate(False)

gantt_canvas = tk.Canvas(gantt_outer, bg=PANEL, height=65, highlightthickness=0)
gantt_hscroll = ttk.Scrollbar(gantt_outer, orient="horizontal",
                               command=gantt_canvas.xview)
gantt_canvas.configure(xscrollcommand=gantt_hscroll.set)
gantt_hscroll.pack(side="bottom", fill="x")
gantt_canvas.pack(fill="both", expand=True)

# Time-tick canvas (fixed, no scroll needed — ticks drawn on gantt canvas itself)
gantt_time_canvas = tk.Canvas(right_cpu, bg=WHITE_BG, height=20, highlightthickness=0)
gantt_time_canvas.pack(fill="x")

def draw_gantt(gantt_data):
    gantt_canvas.delete("all")
    gantt_time_canvas.delete("all")
    if not gantt_data:
        return

    total_time = gantt_data[-1][2]
    if total_time == 0:
        return

    BLOCK_W = 54   # pixels per time unit
    MARGIN_L = 10
    bar_top, bar_bot = 8, 56

    pid_colors = {}
    ci = 0
    for pid,_,__ in gantt_data:
        if pid not in pid_colors:
            pid_colors[pid] = GANTT_COLORS[ci % len(GANTT_COLORS)]
            ci += 1

    canvas_w = MARGIN_L + total_time * BLOCK_W + MARGIN_L

    for pid, start, end in gantt_data:
        x1 = MARGIN_L + start * BLOCK_W
        x2 = MARGIN_L + end   * BLOCK_W
        clr = pid_colors[pid]
        gantt_canvas.create_rectangle(x1, bar_top, x2-1, bar_bot,
                                       fill=clr, outline="white", width=1)
        cx = (x1+x2)//2
        gantt_canvas.create_text(cx, (bar_top+bar_bot)//2,
                                   text=pid, fill="white",
                                   font=("Segoe UI",9,"bold"))

    # Time ticks on bottom of gantt_canvas
    ticks = sorted(set([s for _,s,__ in gantt_data] + [gantt_data[-1][2]]))
    for t in ticks:
        x = MARGIN_L + t * BLOCK_W
        gantt_canvas.create_line(x, bar_bot, x, bar_bot+6, fill=MUTED, width=1)
        gantt_canvas.create_text(x, bar_bot+14, text=str(t),
                                   fill=MUTED, font=("Segoe UI",8))

    gantt_canvas.configure(scrollregion=(0, 0, canvas_w, 90))

lbl(right_cpu,"Metrics",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(10,4))
metrics_panel = tk.Frame(right_cpu, bg=PANEL)
metrics_panel.pack(fill="x")

metric_vars = {}
for m in ["Average Waiting Time","Average Turnaround Time","CPU Utilization","Throughput"]:
    rf = tk.Frame(metrics_panel, bg=PANEL)
    rf.pack(fill="x", padx=12, pady=4)
    tk.Label(rf, text=m+":", bg=PANEL, fg=MUTED,
             font=("Segoe UI",9), width=24, anchor="w").pack(side="left")
    var = tk.StringVar(value="—")
    tk.Label(rf, textvariable=var, bg=PANEL, fg=FG,
             font=("Segoe UI",9,"bold")).pack(side="left")
    metric_vars[m] = var

def run_cpu_scheduling():
    procs = get_cpu_procs()
    if not procs:
        messagebox.showwarning("No Processes","Add at least one process first.")
        return
    algo = cpu_algo.get()
    if algo == "FCFS":
        result, gantt_data = fcfs(procs)
    else:
        try:
            q = int(quantum_e.get())
            if q <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error","Enter a positive integer for quantum.")
            return
        result, gantt_data = round_robin(procs, q)

    draw_gantt(gantt_data)

    avg_wt  = sum(r[1] for r in result) / len(result)
    avg_tat = sum(r[2] for r in result) / len(result)
    total_t = gantt_data[-1][2] if gantt_data else 1
    util    = (sum(p.burst for p in procs) / total_t) * 100
    thruput = len(procs) / total_t

    metric_vars["Average Waiting Time"].set(f"{avg_wt:.2f}")
    metric_vars["Average Turnaround Time"].set(f"{avg_tat:.2f}")
    metric_vars["CPU Utilization"].set(f"{util:.2f}%")
    metric_vars["Throughput"].set(f"{thruput:.4f} proc/unit time")

# ═══════════════════════════════════════════════════════════════
#  MEMORY MANAGEMENT – PAGING
# ═══════════════════════════════════════════════════════════════
memory_page = tk.Frame(main_container, bg=WHITE_BG)
pages["Memory Management"] = memory_page

section_label(memory_page, "Memory Management – Paging")

mem_ctrl = tk.Frame(memory_page, bg=WHITE_BG)
mem_ctrl.pack(fill="x", padx=20, pady=(0,6))
lbl(mem_ctrl,"Total Frames",WHITE_BG,DARK_TEXT,9,True).grid(row=0,column=0,padx=(0,4))
frames_e = entry_box(mem_ctrl,"3",width=4)
frames_e.grid(row=0,column=1,padx=(0,16))
lbl(mem_ctrl,"Page Replacement",WHITE_BG,DARK_TEXT,9,True).grid(row=0,column=2,padx=(0,4))
mem_algo = combo_box(mem_ctrl,["FIFO","LRU"],width=10)
mem_algo.grid(row=0,column=3,padx=(0,16))
lbl(mem_ctrl,"Reference String",WHITE_BG,DARK_TEXT,9,True).grid(row=0,column=4,padx=(0,4))
ref_entry = entry_box(mem_ctrl,"7 0 1 2 0 3 0 4",width=26)
ref_entry.grid(row=0,column=5,padx=(0,16))
dark_btn(mem_ctrl,"Run",lambda:run_memory_paging(),ACCENT,8).grid(row=0,column=6,padx=3)

# Body
mem_body = tk.Frame(memory_page, bg=WHITE_BG)
mem_body.pack(fill="both", expand=True, padx=20, pady=4)
mem_body.columnconfigure(0, weight=3)
mem_body.columnconfigure(1, weight=1)

left_mem = tk.Frame(mem_body, bg=WHITE_BG)
left_mem.grid(row=0, column=0, sticky="nsew", padx=(0,10))

lbl(left_mem,"Page Frames Trace",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))

mem_outer = tk.Frame(left_mem, bg=PANEL)
mem_outer.pack(fill="both", expand=True)
mem_canvas = tk.Canvas(mem_outer, bg=PANEL, height=220, highlightthickness=0)
mem_hscroll = ttk.Scrollbar(mem_outer, orient="horizontal", command=mem_canvas.xview)
mem_canvas.configure(xscrollcommand=mem_hscroll.set)
mem_hscroll.pack(side="bottom", fill="x")
mem_canvas.pack(fill="both", expand=True)

right_mem = tk.Frame(mem_body, bg=WHITE_BG)
right_mem.grid(row=0, column=1, sticky="nsew")

lbl(right_mem,"Statistics",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))
stats_panel = tk.Frame(right_mem, bg=PANEL)
stats_panel.pack(fill="x")

mem_stat_vars = {}
for s in ["Total References","Page Faults","Page Fault Rate","Hits","Hit Rate"]:
    rf = tk.Frame(stats_panel, bg=PANEL)
    rf.pack(fill="x",padx=10,pady=5)
    tk.Label(rf,text=s+":",bg=PANEL,fg=MUTED,font=("Segoe UI",9),width=17,anchor="w").pack(side="left")
    var = tk.StringVar(value="—")
    tk.Label(rf,textvariable=var,bg=PANEL,fg=FG,font=("Segoe UI",9,"bold")).pack(side="left")
    mem_stat_vars[s] = var

def fifo_lru_trace(ref, frames, algo):
    memory, faults, trace = [], 0, []
    for page in ref:
        if page in memory:
            if algo == "LRU":
                memory.remove(page); memory.append(page)
            trace.append((list(memory)+[None]*(frames-len(memory)), False))
        else:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
            else:
                memory.pop(0); memory.append(page)
            trace.append((list(memory)+[None]*(frames-len(memory)), True))
    return faults, trace

def draw_mem_trace(ref_str, trace, frames):
    mem_canvas.delete("all")
    COL_W = 40
    ROW_H = 30
    OX    = 28
    OY    = 20
    n     = len(ref_str)
    canvas_w = OX + n*COL_W + 10
    canvas_h = OY + frames*ROW_H + 30

    # column headers = reference string
    for i,page in enumerate(ref_str):
        cx = OX + i*COL_W + COL_W//2
        mem_canvas.create_text(cx, OY-8, text=str(page),
            fill=FG, font=("Segoe UI",9,"bold"))

    # frame row labels
    for r in range(frames):
        mem_canvas.create_text(14, OY+r*ROW_H+ROW_H//2,
            text=f"F{r}", fill=MUTED, font=("Segoe UI",8,"bold"))

    # cells
    for i,(snap,is_fault) in enumerate(trace):
        cx = OX + i*COL_W
        for r in range(frames):
            cy = OY + r*ROW_H
            fill = "#1e3a5f" if is_fault else "#1e293b"
            mem_canvas.create_rectangle(cx+1,cy+1,cx+COL_W-1,cy+ROW_H-1,
                fill=fill, outline="#334155", width=1)
            val = snap[r]
            if val is not None:
                color = "#93c5fd" if is_fault else FG
                mem_canvas.create_text(cx+COL_W//2, cy+ROW_H//2,
                    text=str(val), fill=color, font=("Segoe UI",9,"bold"))

        # Fault marker row
        fy = OY + frames*ROW_H + 6
        mem_canvas.create_text(cx+COL_W//2, fy+6,
            text="F" if is_fault else "·",
            fill=RED if is_fault else MUTED,
            font=("Segoe UI",9,"bold"))

    mem_canvas.configure(scrollregion=(0,0,canvas_w,canvas_h))

def run_memory_paging():
    try:
        frames = int(frames_e.get())
        ref_str = [int(x) for x in ref_entry.get().split()]
        if frames <= 0 or not ref_str: raise ValueError
    except ValueError:
        messagebox.showerror("Error","Enter a valid frame count and reference string (space-separated integers).")
        return
    algo = mem_algo.get()
    faults, trace = fifo_lru_trace(ref_str, frames, algo)
    hits = len(ref_str) - faults
    mem_stat_vars["Total References"].set(str(len(ref_str)))
    mem_stat_vars["Page Faults"].set(str(faults))
    mem_stat_vars["Page Fault Rate"].set(f"{faults/len(ref_str)*100:.2f}%")
    mem_stat_vars["Hits"].set(str(hits))
    mem_stat_vars["Hit Rate"].set(f"{hits/len(ref_str)*100:.2f}%")
    draw_mem_trace(ref_str, trace, frames)

# ═══════════════════════════════════════════════════════════════
#  PROCESS SYNCHRONIZATION – DINING PHILOSOPHERS
# ═══════════════════════════════════════════════════════════════
sync_page = tk.Frame(main_container, bg=WHITE_BG)
pages["Process Synchronization"] = sync_page

section_label(sync_page, "Process Synchronization – Dining Philosophers")

sync_body = tk.Frame(sync_page, bg=WHITE_BG)
sync_body.pack(fill="both", expand=True, padx=20, pady=4)
sync_body.columnconfigure(0, weight=2)
sync_body.columnconfigure(1, weight=1)

phil_canvas = tk.Canvas(sync_body, bg=PANEL, height=390, highlightthickness=0)
phil_canvas.grid(row=0, column=0, sticky="nsew", pady=4)
phil_canvas.bind("<Configure>", lambda e: draw_phils())

log_frame = tk.Frame(sync_body, bg=WHITE_BG)
log_frame.grid(row=0, column=1, sticky="nsew", padx=(12,0))
lbl(log_frame,"Log",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w")
log_text = scrolledtext.ScrolledText(log_frame, bg=PANEL, fg=FG,
    font=("Consolas",9), width=30, height=20, bd=0, state="disabled")
log_text.pack(fill="both", expand=True)
log_text.tag_configure("think",  foreground=FG)
log_text.tag_configure("hungry", foreground=ORANGE)
log_text.tag_configure("eat",    foreground=GREEN)

# Legend
leg = tk.Frame(sync_page, bg=WHITE_BG)
leg.pack(anchor="w", padx=20)
for txt,clr in [("Thinking","#64748b"),("Hungry",ORANGE),("Eating",GREEN)]:
    tk.Frame(leg,bg=clr,width=14,height=14).pack(side="left",padx=(0,4))
    lbl(leg,txt).pack(side="left",padx=(0,16))

sync_ctrl = tk.Frame(sync_page, bg=WHITE_BG)
sync_ctrl.pack(fill="x", padx=20, pady=8)
lbl(sync_ctrl,"Number of Philosophers",WHITE_BG,DARK_TEXT,9,True).pack(side="left",padx=(0,4))
num_phil_cb = combo_box(sync_ctrl,["3","4","5","6","7"],width=5)
num_phil_cb.current(2)
num_phil_cb.pack(side="left",padx=(0,20))
lbl(sync_ctrl,"Simulation Speed",WHITE_BG,DARK_TEXT,9,True).pack(side="left",padx=(0,4))
speed_var = tk.DoubleVar(value=1.0)
tk.Scale(sync_ctrl,from_=0.2,to=3.0,resolution=0.2,orient="horizontal",
    variable=speed_var, bg=WHITE_BG,fg=DARK_TEXT,troughcolor=PANEL,
    length=130,showvalue=False,highlightthickness=0).pack(side="left",padx=(0,20))
dark_btn(sync_ctrl,"Start",  lambda:start_phils(), GREEN,  9).pack(side="left",padx=3)
dark_btn(sync_ctrl,"Pause",  lambda:pause_phils(), ORANGE, 9).pack(side="left",padx=3)
dark_btn(sync_ctrl,"Reset",  lambda:reset_phils(), "#475569",8).pack(side="left",padx=3)

phil_states = []
phil_status = {}
phil_running = [False]
phil_paused  = [False]
phil_n       = [5]
speed_ref    = [1.0]

PHIL_STATE_COLORS = {"thinking":"#64748b","hungry":ORANGE,"eating":GREEN}

def log_phil(phil_id, state):
    phil_status[phil_id] = state

    def _do():
        log_text.configure(state="normal")
        log_text.delete("1.0", "end")

        for pid in sorted(phil_status.keys()):
            status = phil_status[pid]

            tag = "think"
            if status == "Hungry":
                tag = "hungry"
            elif status == "Eating":
                tag = "eat"

            log_text.insert("end", f"P{pid+1} : {status}\n", tag)

        log_text.configure(state="disabled")

    root.after(0, _do)

def draw_phils():
    phil_canvas.delete("all")
    n = phil_n[0]
    w = phil_canvas.winfo_width()  or 500
    h = phil_canvas.winfo_height() or 390
    cx = w // 2
    cy = h // 2
    R  = min(w, h) // 3
    R  = max(100, min(R, 160))
    pr = 30
    # table
    phil_canvas.create_oval(cx-70,cy-70,cx+70,cy+70,fill="#334155",outline="#475569",width=2)
    phil_canvas.create_text(cx,cy,text="Table",fill=MUTED,font=("Segoe UI",10))
    for i in range(n):
        angle = math.radians(-90 + i*(360/n))
        px = cx + R*math.cos(angle)
        py = cy + R*math.sin(angle)
        state = phil_states[i] if i < len(phil_states) else "thinking"
        clr   = PHIL_STATE_COLORS.get(state,"#64748b")
        phil_canvas.create_oval(px-pr,py-pr,px+pr,py+pr,fill=clr,outline="white",width=2)
        phil_canvas.create_text(px,py,text=f"P{i+1}",fill="white",font=("Segoe UI",10,"bold"))
        # fork
        fa = math.radians(-90+(i+0.5)*(360/n))
        fx = cx + (R*0.52)*math.cos(fa)
        fy = cy + (R*0.52)*math.sin(fa)
        phil_canvas.create_line(fx-8,fy,fx+8,fy,fill="#94a3b8",width=3)
        phil_canvas.create_line(fx,fy-8,fx,fy+8,fill="#94a3b8",width=3)

def phil_worker(i, n, forks):
    left  = forks[i]
    right = forks[(i+1)%n]
    while phil_running[0]:
        phil_states[i] = "thinking"
        log_phil(i, "Thinking")
        root.after(0, draw_phils)
        time.sleep(0.5/speed_ref[0])
        if not phil_running[0]: break
        phil_states[i] = "hungry"
        log_phil(i, "Hungry")
        root.after(0, draw_phils)
        first,second = (left,right) if i%2==0 else (right,left)
        with first:
            with second:
                if not phil_running[0]: break
                while phil_paused[0]: time.sleep(0.05)
                phil_states[i] = "eating"
                log_phil(i, "Eating")
                root.after(0, draw_phils)
                time.sleep(1.0/speed_ref[0])
        log_phil(i, "Thinking")

def start_phils():
    if phil_running[0]: return
    n = int(num_phil_cb.get())
    phil_n[0] = n
    phil_states.clear()
    phil_states.extend(["thinking"]*n)
    phil_status.clear()
    for i in range(n):
        phil_status[i] = "Thinking"
    phil_running[0] = True
    phil_paused[0]  = False
    speed_ref[0]    = speed_var.get()
    log_text.configure(state="normal"); log_text.delete("1.0","end"); log_text.configure(state="disabled")
    forks = [threading.Lock() for _ in range(n)]
    draw_phils()
    for i in range(n):
        threading.Thread(target=phil_worker, args=(i,n,forks), daemon=True).start()

def pause_phils():
    phil_paused[0] = not phil_paused[0]

def reset_phils():
    phil_running[0] = False
    phil_paused[0]  = False
    phil_states.clear()
    phil_status.clear()
    n = int(num_phil_cb.get())
    phil_n[0] = n
    phil_states.extend(["thinking"]*n)
    root.after(150, draw_phils)
    log_text.configure(state="normal"); log_text.delete("1.0","end"); log_text.configure(state="disabled")

draw_phils()

# ═══════════════════════════════════════════════════════════════
#  DEADLOCK HANDLING – BANKER'S ALGORITHM
# ═══════════════════════════════════════════════════════════════
deadlock_page = tk.Frame(main_container, bg=WHITE_BG)
pages["Deadlock Handling"] = deadlock_page

section_label(deadlock_page, "Deadlock Handling – Banker's Algorithm")

dl_body = tk.Frame(deadlock_page, bg=WHITE_BG)
dl_body.pack(fill="both", expand=True, padx=20, pady=4)
dl_body.columnconfigure(0, weight=1)
dl_body.columnconfigure(1, weight=3)

# Left: available resources
left_dl = tk.Frame(dl_body, bg=WHITE_BG)
left_dl.grid(row=0,column=0,sticky="nsew",padx=(0,10))
lbl(left_dl,"Available Resources",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,6))

avail_frame = tk.Frame(left_dl, bg=PANEL)
avail_frame.pack(fill="x")

# header
hdr = tk.Frame(avail_frame, bg=PANEL)
hdr.pack(fill="x",padx=10,pady=(6,0))
for t,w2 in [("Resource",80),("Total",60),("Available",80)]:
    tk.Label(hdr,text=t,bg="#334155",fg=FG,font=("Segoe UI",9,"bold"),
             width=w2//8,anchor="w").pack(side="left",padx=2)

res_totals = [10,5,7]
avail_entries = []
for i,name in enumerate(["A","B","C"]):
    rf = tk.Frame(avail_frame, bg=PANEL)
    rf.pack(fill="x",padx=10,pady=3)
    tk.Label(rf,text=name,bg=PANEL,fg=MUTED,font=("Segoe UI",9),width=8,anchor="w").pack(side="left",padx=2)
    tk.Label(rf,text=str(res_totals[i]),bg=PANEL,fg=FG,font=("Segoe UI",9),width=6,anchor="w").pack(side="left",padx=2)
    e = entry_box(rf, ["3","3","2"][i], width=5)
    e.pack(side="left",padx=2)
    avail_entries.append(e)

# Right: process table
right_dl = tk.Frame(dl_body, bg=WHITE_BG)
right_dl.grid(row=0,column=1,sticky="nsew")
lbl(right_dl,"Process Table",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))

bk_tree = make_tree(right_dl,
    ("Process","Max A","Max B","Max C","Alloc A","Alloc B","Alloc C","Need A","Need B","Need C"),
    [72,65,65,65,65,65,65,65,65,65], height=6)
bk_tree.pack(fill="x")

bk_alloc = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
bk_max   = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]

def refresh_banker():
    for item in bk_tree.get_children(): bk_tree.delete(item)
    for i in range(len(bk_alloc)):
        need = [bk_max[i][j]-bk_alloc[i][j] for j in range(3)]
        bk_tree.insert("","end",values=(
            f"P{i}",*bk_max[i],*bk_alloc[i],*need))

refresh_banker()

# Safe sequence bar
seq_lbl_frame = tk.Frame(deadlock_page, bg=WHITE_BG)
seq_lbl_frame.pack(fill="x",padx=20,pady=(8,2))
lbl(seq_lbl_frame,"Safe Sequence",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w")

seq_var = tk.StringVar(value="Click 'Check Safe State' to run the algorithm")
seq_disp = tk.Label(deadlock_page, textvariable=seq_var,
    bg=PANEL, fg=GREEN, font=("Segoe UI",12,"bold"),
    padx=14, pady=10, anchor="w")
seq_disp.pack(fill="x",padx=20,pady=2)

status_var = tk.StringVar(value="")
status_lbl = tk.Label(deadlock_page, textvariable=status_var,
    bg=WHITE_BG, font=("Segoe UI",10,"bold"), anchor="e")
status_lbl.pack(fill="x",padx=20)

def run_banker():
    try:
        avail = [int(avail_entries[j].get()) for j in range(3)]
    except ValueError:
        messagebox.showerror("Error","Enter valid integers for available resources.")
        return
    safe, seq = bankers_algorithm(bk_alloc, bk_max, avail)
    if safe:
        seq_var.set("  →  ".join(f"P{i}" for i in seq))
        seq_disp.config(fg=GREEN)
        status_var.set("✔  System is in Safe State")
        status_lbl.config(fg=GREEN)
    else:
        seq_var.set("No safe sequence – DEADLOCK detected!")
        seq_disp.config(fg=RED)
        status_var.set("✘  System is NOT in Safe State")
        status_lbl.config(fg=RED)

btn_row = tk.Frame(deadlock_page, bg=WHITE_BG)
btn_row.pack(padx=20, pady=6, anchor="w")
dark_btn(btn_row,"Check Safe State", run_banker, ACCENT, 18).pack(side="left",padx=(0,8))
dark_btn(btn_row,"Reset", lambda:[seq_var.set("Click 'Check Safe State' to run the algorithm"),
    status_var.set(""), seq_disp.config(fg=GREEN), refresh_banker()], "#475569", 8).pack(side="left")

# ═══════════════════════════════════════════════════════════════
#  FILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════
file_page = tk.Frame(main_container, bg=WHITE_BG)
pages["File Management"] = file_page

section_label(file_page, "File Management – Disk Allocation")

file_body = tk.Frame(file_page, bg=WHITE_BG)
file_body.pack(fill="both", expand=True, padx=20, pady=4)
file_body.columnconfigure(0, weight=1)
file_body.columnconfigure(1, weight=1)

# Left: directory + index block table
left_file = tk.Frame(file_body, bg=WHITE_BG)
left_file.grid(row=0,column=0,sticky="nsew",padx=(0,10))

lbl(left_file,"Directory",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))
dir_tree = make_tree(left_file,("File Name","Start Index Block","File Size (KB)"),
                     [120,130,110], height=5)
dir_tree.pack(fill="x")

lbl(left_file,"Index Block Table",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(10,4))
idx_tree = make_tree(left_file,("Index Block","Block Pointers"),[100,220], height=5)
idx_tree.pack(fill="x")

# Right: disk canvas
right_file = tk.Frame(file_body, bg=WHITE_BG)
right_file.grid(row=0,column=1,sticky="nsew")

lbl(right_file,"Disk Blocks",WHITE_BG,DARK_TEXT,10,True).pack(anchor="w",pady=(0,4))
disk_outer = tk.Frame(right_file, bg=PANEL)
disk_outer.pack(fill="both",expand=True)
disk_canvas = tk.Canvas(disk_outer, bg=PANEL, height=180, highlightthickness=0)
disk_canvas.pack(fill="both",expand=True,padx=6,pady=6)

leg2 = tk.Frame(right_file, bg=WHITE_BG)
leg2.pack(anchor="w",pady=4)

FILE_COLORS = {
    "File1.txt":"#22c55e","File2.pdf":"#2563eb",
    "Image.png":"#f59e0b","Doc.docx":"#9333ea","FREE":"#334155"
}
DEFAULT_FILES = [("File1.txt",12),("File2.pdf",20),("Image.png",8),("Doc.docx",15)]

def run_file_alloc(algo):
    total = 30
    for item in dir_tree.get_children(): dir_tree.delete(item)
    for item in idx_tree.get_children():  idx_tree.delete(item)

    if algo == "Indexed":
        alloc_obj = IndexedAllocation(total)
        for fname,fsize in DEFAULT_FILES:
            alloc_obj.allocate(fname, max(1,fsize//3))
        disk = alloc_obj.disk
        for fname,blocks in alloc_obj.index_table.items():
            start = blocks[0] if blocks else "—"
            dir_tree.insert("","end",values=(fname,start,len(blocks)*3))
            ptrs = "  ".join(str(b) for b in blocks[:8])
            if len(blocks)>8: ptrs += " …"
            idx_tree.insert("","end",values=(start,ptrs))
    else:
        alloc_obj = SequentialAllocation(total)
        for fname,fsize in DEFAULT_FILES:
            alloc_obj.allocate(fname, max(1,fsize//3))
        disk = alloc_obj.disk
        cur, start_i = None, 0
        for i,b in enumerate(disk):
            if b != cur:
                if cur and cur != "FREE":
                    size = i-start_i
                    dir_tree.insert("","end",values=(cur,start_i,size*3))
                    idx_tree.insert("","end",values=(start_i,f"Blocks {start_i}–{i-1}"))
                cur = b; start_i = i

    draw_disk(disk, total)

    for w2 in leg2.winfo_children(): w2.destroy()
    tk.Frame(leg2,bg="#334155",width=14,height=14).pack(side="left",padx=(0,3))
    tk.Label(leg2,text="Free Block",bg=WHITE_BG,fg=DARK_TEXT,font=("Segoe UI",8)).pack(side="left",padx=(0,10))
    for fname,_ in DEFAULT_FILES:
        clr = FILE_COLORS.get(fname,"#888")
        tk.Frame(leg2,bg=clr,width=14,height=14).pack(side="left",padx=(0,3))
        tk.Label(leg2,text=fname,bg=WHITE_BG,fg=DARK_TEXT,font=("Segoe UI",8)).pack(side="left",padx=(0,10))

def draw_disk(disk, total):
    disk_canvas.delete("all")
    w = disk_canvas.winfo_width() or 380
    if w < 30: w = 380
    COLS = 10
    BW = max(26, (w-20)//COLS)
    BH = 34
    for i,block in enumerate(disk):
        row = i//COLS; col = i%COLS
        x1 = 8 + col*BW; y1 = 6 + row*(BH+4)
        x2, y2 = x1+BW-3, y1+BH
        clr = FILE_COLORS.get(block,"#334155")
        disk_canvas.create_rectangle(x1,y1,x2,y2,fill=clr,outline="#0f172a",width=1)
        disk_canvas.create_text((x1+x2)//2,(y1+y2)//2,text=str(i),
            fill="white",font=("Segoe UI",8))

file_ctrl = tk.Frame(file_page, bg=WHITE_BG)
file_ctrl.pack(fill="x",padx=20,pady=6)
dark_btn(file_ctrl,"Sequential Allocation",lambda:run_file_alloc("Sequential"),ACCENT,20).pack(side="left",padx=(0,8))
dark_btn(file_ctrl,"Indexed Allocation",   lambda:run_file_alloc("Indexed"),   GREEN, 18).pack(side="left",padx=(0,8))
dark_btn(file_ctrl,"Reset",lambda:run_file_alloc("Indexed"),"#475569",8).pack(side="left")

file_page.after(350, lambda: run_file_alloc("Indexed"))

# ═══════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════
settings_page = tk.Frame(main_container, bg=WHITE_BG)
pages["Settings"] = settings_page
section_label(settings_page,"Settings")
lbl(settings_page,"Theme and preferences — coming soon.",WHITE_BG,MUTED,11).pack(pady=20,padx=20)

# ═══════════════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════════════
about_page = tk.Frame(main_container, bg=WHITE_BG)
pages["About"] = about_page
section_label(about_page,"About")
tk.Label(about_page,
    text=(
        "Mini Operating System Simulator\n\n"
        "Modules implemented:\n"
        "  •  CPU Scheduling         — FCFS, Round Robin\n"
        "  •  Memory Management      — First Fit, Best Fit\n"
        "  •  Page Replacement       — FIFO, LRU  (with visual trace)\n"
        "  •  Process Synchronization— Dining Philosophers (animated)\n"
        "  •  Deadlock Detection     — Banker's Algorithm\n"
        "  •  File Management        — Sequential & Indexed Allocation"
    ),
    bg=WHITE_BG, fg=DARK_TEXT, font=("Segoe UI",11),
    justify="left").pack(anchor="w",padx=40,pady=16)

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR NAV
# ═══════════════════════════════════════════════════════════════
tk.Label(sidebar, text="OS Simulator", bg=BG, fg="white",
         font=("Segoe UI",13,"bold")).pack(pady=(20,16))

NAV = [
    ("⊞  Dashboard",              "Dashboard"),
    ("⚙  CPU Scheduling",         "CPU Scheduling"),
    ("▣  Memory Management",      "Memory Management"),
    ("⟳  Process Synchronization","Process Synchronization"),
    ("⛔  Deadlock Handling",      "Deadlock Handling"),
    ("📁  File Management",        "File Management"),
    ("⚒  Settings",               "Settings"),
    ("ℹ  About",                  "About"),
]
for label,name in NAV:
    btn = tk.Button(sidebar, text=label, anchor="w",
        bg="#1e293b", fg=MUTED, relief="flat", bd=0,
        padx=14, pady=9, font=("Segoe UI",9), cursor="hand2",
        command=lambda n=name: show_page(n))
    btn.pack(fill="x", padx=8, pady=2)
    sidebar_buttons[name] = btn

tk.Label(sidebar, text="● System Ready", bg=BG, fg=GREEN,
         font=("Segoe UI",9)).pack(side="bottom", pady=16)

# ─────────────────────────── START ───────────────────────────
show_page("Dashboard")

# Deferred redraws after window is fully rendered
root.after(300, draw_sparkline)
root.after(300, draw_pie)
root.after(300, draw_phils)

root.mainloop()
