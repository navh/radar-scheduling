from copy import deepcopy
from time import time_ns
from typing import List

from tqdm import tqdm

from schedule_dual_side_with_rsst import dual_side_with_rsst
from schedule_earliest_deadline import schedule_earliest_deadline
from schedule_earliest_start_time import earliest_start_time
from schedule_front_line_assembly import front_line_assembly
from schedule_random_shifted_start_time import random_shifted_start_time
from summary_stats import executed_tasks, normalized_cost
from task import Task

import pandas as pd

from multiprocessing import Pool
import os


class SampleSettings:
    def __init__(
        self,
        sample_number: int,
        itr_rsst: int,
        total_borders: int,
        itr_rsst_dualside: int,
        n_actual: int,
        window_length: float,
        tau: float,
    ):
        self.sample_number = sample_number
        self.itr_rsst = itr_rsst
        self.total_borders = total_borders
        self.itr_rsst_dualside = itr_rsst_dualside
        self.n_actual = n_actual
        self.window_length = window_length
        self.tau = tau


class Stats:
    def __init__(
        self,
        method: str,
        sample_number: int,
        state: int,
        n: int,
        executed_tasks: int,
        normalized_cost: float,
        est_cost: float,
        time: int,
        loading_rate: float,
    ):
        self.method = method
        self.sample_number = sample_number
        self.state = state
        self.n = n
        self.executed_tasks = executed_tasks
        self.normalized_cost = normalized_cost
        self.est_ratio = normalized_cost / est_cost
        self.time = time
        self.loading_rate = loading_rate


def get_state_number(task_list: List[Task], window_length: float):
    # State 1: sum(t_dwell) >= L and mean(t_start) <= 0.5 and sum(conflict) <= 10
    # State 2: sum(t_dwell) >= L and mean(t_start) <= 0.5 and sum(conflict) >  10
    # State 3: sum(t_dwell) >= L and mean(t_start) >  0.5 and sum(conflict) <= 10
    # State 4: sum(t_dwell) >= L and mean(t_start) >  0.5 and sum(conflict) >  10
    # State 5: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) <= 10
    # State 6: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) >  10
    # State 7: sum(t_dwell) <  L and mean(t_start) >  0.5 and sum(conflict) <= 10
    # State 8: sum(t_dwell) <  L and mean(t_start) >  0.5 and sum(conflict) >  10
    state_number = 1
    if sum(task.t_dwell for task in task_list) < window_length:
        state_number += 4

    if (sum(task.t_start for task in task_list) / len(task_list)) > 0.5:
        state_number += 2

    conflict_count = 0
    for i, i_task in enumerate(task_list):
        i_head = i_task.t_start
        i_tail = i_task.t_start + i_task.t_dwell
        for j_task in task_list[i + 1 :]:
            j_head = j_task.t_start
            j_tail = j_task.t_start + j_task.t_dwell
            if (i_head <= j_tail) and (i_tail >= j_head):
                conflict_count += 1
    if conflict_count > 10:
        state_number += 1
    return state_number


def run_schedules(settings: SampleSettings) -> List[Stats]:
    samples = list()
    task_list = list(Task() for _ in range(settings.n_actual))

    for task in task_list:
        task.uniform_randomize(
            n=settings.n_actual,
            minimum_t=0,
            maximum_t=settings.window_length,
            tau=settings.tau,
            minimum_priority=1,  # TODO: minimum priority 0? Priorities as floats?
            maximum_priority=9,
        )

    state_number = get_state_number(task_list, settings.window_length)
    max_drop_cost = sum(task.drop_cost() for task in task_list)
    loading_rate = sum(task.t_dwell for task in task_list) / settings.window_length

    # ---------------------------a1. Earliest Start Time (EST) Scheduling --------------
    tic = time_ns()

    tasks_scheduled = earliest_start_time(deepcopy(task_list))

    time = time_ns() - tic

    est_cost = normalized_cost(tasks_scheduled, max_drop_cost)

    samples.append(
        Stats(
            "EST",
            settings.sample_number,
            state_number,
            settings.n_actual,
            executed_tasks(tasks_scheduled),
            est_cost,
            est_cost,
            time,
            loading_rate,
        )
    )

    # -------------------------------a2. Earliest Deadline (ED) Scheduling -------------
    tic = time_ns()

    tasks_scheduled = schedule_earliest_deadline(deepcopy(task_list))

    time = time_ns() - tic

    samples.append(
        Stats(
            "ED",
            settings.sample_number,
            state_number,
            settings.n_actual,
            executed_tasks(tasks_scheduled),
            normalized_cost(tasks_scheduled, max_drop_cost),
            est_cost,
            time,
            loading_rate,
        )
    )

    # -------------------------------b. Random Shifted Start Time (RSST) Scheduling ----
    tic = time_ns()

    tasks_scheduled = random_shifted_start_time(deepcopy(task_list), settings.itr_rsst)

    time = time_ns() - tic

    samples.append(
        Stats(
            "RSST",
            settings.sample_number,
            state_number,
            settings.n_actual,
            executed_tasks(tasks_scheduled),
            normalized_cost(tasks_scheduled, max_drop_cost),
            est_cost,
            time,
            loading_rate,
        )
    )

    # -------------------------------c. Dual-Side Scheduling with RSST (DSS) -----------
    tic = time_ns()

    tasks_scheduled = dual_side_with_rsst(
        deepcopy(task_list), settings.itr_rsst_dualside, settings.total_borders
    )
    time = time_ns() - tic

    samples.append(
        Stats(
            "DSS",
            settings.sample_number,
            state_number,
            settings.n_actual,
            executed_tasks(tasks_scheduled),
            normalized_cost(tasks_scheduled, max_drop_cost),
            est_cost,
            time,
            loading_rate,
        )
    )

    # d. front line assembly
    tic = time_ns()

    tasks_scheduled = front_line_assembly(deepcopy(task_list))

    time = time_ns() - tic

    samples.append(
        Stats(
            "FLA",
            settings.sample_number,
            state_number,
            settings.n_actual,
            executed_tasks(tasks_scheduled),
            normalized_cost(tasks_scheduled, max_drop_cost),
            est_cost,
            time,
            loading_rate,
        )
    )
    return samples


def counter():
    n = 0
    while True:
        yield n
        n += 1


if __name__ == "__main__":
    run_settings = list()
    count = counter()
    SAMPLES = 1_000_000
    for i in range(1, 1 + SAMPLES):
        run_settings.append(
            SampleSettings(
                sample_number=next(count),
                itr_rsst=1000,
                itr_rsst_dualside=50,
                total_borders=10,
                n_actual=10,
                window_length=1,
                tau=1,
            )
        )

    samples = list()
    with Pool(os.cpu_count()) as pool:
        for subsamples in tqdm(
            pool.imap_unordered(
                run_schedules,
                run_settings,
            ),
            total=len(run_settings),
        ):
            samples.extend(sample.__dict__ for sample in subsamples)

    pd.DataFrame(samples).to_parquet("./data/test7.parquet", index=False)
