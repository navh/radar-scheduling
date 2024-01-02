from copy import deepcopy
from typing import List

from pack_tasks_head_to_tail import pack_tasks_head_to_tail, pack_tasks_tail_to_head
from task import Task


def dual_side(tasks: List[Task], borders: int) -> List[Task]:
    border_schedules = (
        dual_side_schedule(deepcopy(tasks), border / borders)
        for border in range(borders)
    )
    return min(
        border_schedules,
        key=lambda tasks: sum(task.calculate_cost() for task in tasks),
    )


def dual_side_schedule(tasks: List[Task], border: float) -> List[Task]:
    # If more than half of the task is before the border, go to the left
    # tasks_before_border = [
    #     task for task in tasks if ((task.t_scheduled + task.t_dwell / 2)) < border
    # ]
    # TODO: change this so that tasks on border fall onto correct side of border
    tasks_before_border = [task for task in tasks if ((task.t_scheduled)) < border]

    tasks_after_border = [task for task in tasks if task not in tasks_before_border]

    scheduled_tasks_before_border = pack_tasks_tail_to_head(tasks_before_border, border)

    scheduled_tasks_after_border = pack_tasks_head_to_tail(tasks_after_border, border)

    return scheduled_tasks_before_border + scheduled_tasks_after_border
