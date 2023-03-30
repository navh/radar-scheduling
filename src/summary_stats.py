from typing import List

from task import Task


def summary_stats(tasks: List[Task], name: str, max_cost: float):
    executed_count = executed_tasks(tasks)
    n = len(tasks)
    print(
        f"     Executed tasks count: {executed_count}/{n} ({name}) | Dropped tasks count: {n - executed_count}/{n} ({name})"
    )
    print(
        f"     Normalized cost calculated by {name}: {normalized_cost(tasks, max_cost)} (0~1)"
    )


def executed_tasks(tasks: List[Task]):
    return sum(1 for task in tasks if not task.dropped)


def normalized_cost(tasks: List[Task], max_cost: float):
    return sum(task.calculate_cost() for task in tasks) / max_cost
