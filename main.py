
"""
Mini Operating System Simulator
Implements:
1. CPU Scheduling (FCFS, Round Robin)
2. Memory Management (First Fit, Best Fit)
3. Page Replacement (FIFO, LRU)
"""

from collections import deque



# MODULE 1: CPU SCHEDULING


class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst


def fcfs(processes):
    processes = sorted(processes, key=lambda p: p.arrival)

    time = 0
    results = []
    gantt = []

    for p in processes:
        if time < p.arrival:
            time = p.arrival

        start = time
        finish = time + p.burst

        waiting = start - p.arrival
        turnaround = finish - p.arrival

        results.append((p.pid, waiting, turnaround))
        gantt.append((p.pid, start, finish))

        time = finish

    return results, gantt


def round_robin(processes, quantum):
    queue = deque()
    processes = sorted(processes, key=lambda p: p.arrival)

    remaining = {p.pid: p.burst for p in processes}
    completion = {}

    time = 0
    i = 0
    gantt = []

    while i < len(processes) or queue:

        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time = processes[i].arrival
            continue

        p = queue.popleft()

        run = min(quantum, remaining[p.pid])
        start = time
        time += run
        remaining[p.pid] -= run

        gantt.append((p.pid, start, time))

        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if remaining[p.pid] > 0:
            queue.append(p)
        else:
            completion[p.pid] = time

    results = []
    for p in processes:
        tat = completion[p.pid] - p.arrival
        wt = tat - p.burst
        results.append((p.pid, wt, tat))

    return results, gantt



# MODULE 2: MEMORY


def first_fit(blocks, processes):
    blocks = blocks[:]
    allocation = [-1] * len(processes)

    for i, p in enumerate(processes):
        for j in range(len(blocks)):
            if blocks[j] >= p:
                allocation[i] = j
                blocks[j] -= p
                break

    return allocation


def best_fit(blocks, processes):
    blocks = blocks[:]
    allocation = [-1] * len(processes)

    for i, p in enumerate(processes):
        best = -1

        for j in range(len(blocks)):
            if blocks[j] >= p:
                if best == -1 or blocks[j] < blocks[best]:
                    best = j

        if best != -1:
            allocation[i] = best
            blocks[best] -= p

    return allocation


# MODULE 3: PAGE REPLACEMENT

def fifo_page_replacement(reference, frames):
    memory = []
    faults = 0

    for page in reference:
        if page not in memory:
            faults += 1

            if len(memory) < frames:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)

    return faults


def lru_page_replacement(reference, frames):
    memory = []
    faults = 0

    for page in reference:
        if page in memory:
            memory.remove(page)
            memory.append(page)
        else:
            faults += 1

            if len(memory) < frames:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)

    return faults



# MODULE 4: SYNCHRONIZATION


import threading
import time

class DiningPhilosophers:

    def __init__(self, n=5):
        self.n = n
        self.forks = [threading.Lock() for _ in range(n)]

    def philosopher(self, i):

        left = self.forks[i]
        right = self.forks[(i + 1) % self.n]

        print(f"Philosopher {i} is Thinking")

        with left:
            with right:
                print(f"Philosopher {i} is Eating")
                time.sleep(1)

        print(f"Philosopher {i} Finished Eating")

    def run(self):

        threads = []

        for i in range(self.n):
            t = threading.Thread(
                target=self.philosopher,
                args=(i,)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()



# MODULE 5: DEADLOCK


def bankers_algorithm(allocation,
                      maximum,
                      available):

    n = len(allocation)
    m = len(available)

    need = [
        [
            maximum[i][j] - allocation[i][j]
            for j in range(m)
        ]
        for i in range(n)
    ]

    finish = [False] * n
    safe_sequence = []

    work = available[:]

    while len(safe_sequence) < n:

        found = False

        for i in range(n):

            if not finish[i]:

                possible = True

                for j in range(m):
                    if need[i][j] > work[j]:
                        possible = False
                        break

                if possible:

                    for j in range(m):
                        work[j] += allocation[i][j]

                    safe_sequence.append(i)
                    finish[i] = True
                    found = True

        if not found:
            return False, []

    return True, safe_sequence



# MODULE 6: FILE MANAGEMENT


class SequentialAllocation:

    def __init__(self, total_blocks):

        self.disk = ["FREE"] * total_blocks

    def allocate(self,
                 filename,
                 size):

        count = 0
        start = -1

        for i in range(len(self.disk)):

            if self.disk[i] == "FREE":

                if count == 0:
                    start = i

                count += 1

                if count == size:

                    for j in range(start,
                                   start + size):

                        self.disk[j] = filename

                    return True

            else:
                count = 0

        return False

    def display(self):

        print("\nDisk Blocks")

        for i, block in enumerate(self.disk):
            print(f"{i}: {block}")


# DEMO


if __name__ == "__main__":

    print("\n===== CPU Scheduling =====")

    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8)
    ]

    result, gantt = fcfs(processes)

    print("\nFCFS Results")
    for r in result:
        print(r)

    print("Gantt:", gantt)

    result, gantt = round_robin(processes, quantum=2)

    print("\nRound Robin Results")
    for r in result:
        print(r)

    print("Gantt:", gantt)

    print("\n===== Memory Management =====")

    blocks = [100, 500, 200, 300, 600]
    proc_mem = [212, 417, 112, 426]

    print("First Fit:", first_fit(blocks, proc_mem))
    print("Best Fit :", best_fit(blocks, proc_mem))

    print("\n===== Page Replacement =====")

    reference = [7, 0, 1, 2, 0, 3, 0, 4]

    print("FIFO Faults:", fifo_page_replacement(reference, 3))
    print("LRU Faults :", lru_page_replacement(reference, 3))

    print("\n===== Synchronization =====")

    dp = DiningPhilosophers()
    dp.run()

    print("\n===== Banker's Algorithm =====")

    allocation = [
        [0,1,0],
        [2,0,0],
        [3,0,2],
        [2,1,1],
        [0,0,2]
    ]

    maximum = [
     [7,5,3],
        [3,2,2],
        [9,0,2],
        [2,2,2],
        [4,3,3]
    ]

    available = [3,3,2]

    safe, seq = bankers_algorithm(
        allocation,
        maximum,
        available
    )

    print("Safe State:", safe)

    if safe:
        print("Safe Sequence:",
              " -> ".join(
               f"P{i}" for i in seq
            ))

    print("\n===== File Management =====")

    disk = SequentialAllocation(20)

    disk.allocate("File1", 5)
    disk.allocate("File2", 4)

    disk.display()