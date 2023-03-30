# In this paper, there are 8 states and 4 actions.
# The states define the environment setup for the agent to learn.
# The definition of all the states is provided below:
# State 1: sum(t_dwell) >= L and mean(t_start) <= 0.5 and sum(conflict) <= 10
# State 2: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) <= 10
# State 3: sum(t_dwell) >= L and mean(t_start) >  0.5 and sum(conflict) <= 10
# State 4: sum(t_dwell) >= L and mean(t_start) <= 0.5 and sum(conflict) >  10
# State 5: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) >  10
# State 6: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) >  10 # This is state 5 again?
# State 7: sum(t_dwell) <  L and mean(t_start) >  0.5 and sum(conflict) >  10
# State 8: others.

# I'm finding order in the paper difficult to reason about, I'll be doing:

# State 1: sum(t_dwell) >= L and mean(t_start) <= 0.5 and sum(conflict) <= 10
# State 2: sum(t_dwell) >= L and mean(t_start) <= 0.5 and sum(conflict) >  10
# State 3: sum(t_dwell) >= L and mean(t_start) >  0.5 and sum(conflict) <= 10
# State 4: sum(t_dwell) >= L and mean(t_start) >  0.5 and sum(conflict) >  10
# State 5: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) <= 10
# State 6: sum(t_dwell) <  L and mean(t_start) <= 0.5 and sum(conflict) >  10
# State 7: sum(t_dwell) <  L and mean(t_start) >  0.5 and sum(conflict) <= 10
# State 8: sum(t_dwell) <  L and mean(t_start) >  0.5 and sum(conflict) >  10


from pathlib import Path
from time import time_ns

import distinctipy

from scenario import Scenario
from task import Task

N_ACTUAL = 10
WINDOW_LENGTH = 1  # L in the above
TAU = 1

states_remaining = [1, 2, 3, 4, 5, 6, 7, 8]

# TODO: make this an absolute path instead of relative
dir_name = f"./eight_scenarios/run_{time_ns()}"
Path(dir_name).mkdir(parents=True, exist_ok=False)

while states_remaining:
    task_list = list(Task() for _ in range(N_ACTUAL))

    for task in task_list:
        task.uniform_randomize(
            n=N_ACTUAL,
            minimum_t=0,
            maximum_t=WINDOW_LENGTH,
            tau=TAU,
            minimum_priority=1,  # TODO: minimum priority 0? Priorities as floats?
            maximum_priority=9,
        )

    distinct_colors = distinctipy.get_colors(N_ACTUAL)

    for task, color in zip(task_list, distinct_colors):
        task.color = color

    state_number = 1
    if sum(task.t_dwell for task in task_list) < WINDOW_LENGTH:
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

    if state_number in states_remaining:
        states_remaining.remove(state_number)

        scene = Scenario()
        scene.tasks_from_tasklist(task_list)

        file = Path(dir_name + f"/state_{state_number}.json")
        with file.open(mode="w") as f:
            f.write(scene.tasks_to_scenario_specification())
