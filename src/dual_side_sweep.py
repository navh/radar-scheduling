from copy import deepcopy
from task import Task

from copy import deepcopy

from matplotlib import pyplot as plt
import scienceplots

plt.style.use(["science", "ieee"])
import distinctipy

from schedule_dual_side import dual_side_schedule

WINDOW_LENGTH = 1
N = 10
LOADING_RATE = 50  # 50% underloaded to 200% overloaded
N_ACTUAL = int(LOADING_RATE * N / 100)  # TODO: should this be ceil? uncast in matlab
TAU = 1

BORDERS = 10_000

task_list = list(Task() for _ in range(N_ACTUAL))

for task in task_list:
    task.uniform_randomize(
        n=N,
        minimum_t=0,
        maximum_t=WINDOW_LENGTH,
        tau=TAU,
        minimum_priority=1,
        maximum_priority=9,
    )

distinct_colors = distinctipy.get_colors(N_ACTUAL)
for task, color in zip(task_list, distinct_colors):
    task.color = color


border_times = (border / BORDERS for border in range(BORDERS))

schedules = (
    dual_side_schedule(deepcopy(task_list), border_time) for border_time in border_times
)

costs = (sum(task.calculate_cost() for task in schedule) for schedule in schedules)


plt.plot(list(costs))
plt.savefig(f"dual_side_sweep{BORDERS}b{LOADING_RATE}o.svg")
plt.show()
