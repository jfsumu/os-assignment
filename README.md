# Mini Operating System Simulator

An interactive, multi-threaded GUI application built with Python and Tkinter that simulates core operating system concepts. This simulator visualizes complex OS mechanisms—ranging from low-level CPU scheduling pipelines to high-level file allocation patterns—using clean animations, dynamic tables, and responsive dark-themed dashboards.

![System State](https://img.shields.io/badge/System_State-Ready-22c55e?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-2563eb?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/UI_Framework-Tkinter-9333ea?style=for-the-badge)

---

## ⊞ Project Features & Architecture

The simulator bridges backend architectural algorithms with an event-driven frontend canvas interface. It includes six foundational OS modules:

### 1. ⚙ CPU Scheduling
* **Algorithms:** First-Come, First-Served (FCFS) and Round Robin (RR) with a configurable time quantum.
* **Visualization:** Renders a dynamic **Gantt Chart** with precise time-ticks, horizontal scroll handling, and real-time computation of metrics:
  * Average Waiting Time ($T_w$)
  * Average Turnaround Time ($T_{at}$)
  * CPU Utilization %
  * Throughput (processes/unit time)

### 2. ▣ Memory Management (Paging Trace)
* **Algorithms:** First-In, First-Out (FIFO) and Least Recently Used (LRU) page replacement.
* **Visualization:** Employs a matrix grid step-trace. Pages causing a **Page Fault** are highlighted in a deep-blue cell state, showing exactly how frames change over a space-separated reference string.

### 3. ⟳ Process Synchronization (Dining Philosophers)
* **Mechanics:** Simulates asynchronous resource contention among $N$ philosophers sitting around a circular table.
* **Concurrency:** Runs each philosopher on a distinct `threading.Thread` with custom speed controls.
* **Deadlock Prevention:** Implements asymmetric lock acquisition (even-indexed philosophers pick up Left-then-Right, odd-indexed pick up Right-then-Left) to break circular wait conditions.

### 4. ⛔ Deadlock Handling (Banker's Algorithm)
* **Mechanics:** Resource-allocation state tracking for safe/unsafe vector conditions.
* **Metrics:** Evaluates process matrices ($\text{Max}$, $\text{Allocation}$, and $\text{Need}$) against an $\text{Available}$ resource vector to determine if a state is stable or represents a deadlock.

### 5. 📁 File Management (Disk Allocation)
* **Strategies:** Sequential (contiguous) vs. Indexed file allocation.
* **Visualization:** Maps file logical structures directly down onto a simulated 30-block hardware track grid, complete with color-keyed multi-format file blocks.

---

## 🛠 Tech Stack & UI Styling

The interface is decoupled into a clean modular structure using an asynchronous UI model:
