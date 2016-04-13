"""Object Oriented Testing framework.

A more comprehensive documentation is slowly brewing.

Features of PITEST:
    - passing in arguments at run time
    - efficient and selective test discovery
    - dependency tracking and parallel testing
    - snake_case instead camelCase
"""

__all__ = [ 'DAG', 'Discover', 'Main', 'Runner', 'Scheduler', 'Args',
           'TestCaseBase', 'TestSuiteBase', 'TestCaseResult', 'TestSuiteResult' ]

from .args import Args, ArgsError
from .case import TestCaseBase
from .dag import DAG, Py3DAGError
from .discover import Discover, DiscoverError
from .main import Main
from .result import TestCaseResult, TestSuiteResult
from .runner import Runner
from .scheduler import Scheduler, SchedulerError
from .suite import TestSuiteBase, TestSuiteBaseError
