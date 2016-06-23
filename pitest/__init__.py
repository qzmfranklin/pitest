"""Object Oriented Testing framework.

A more comprehensive documentation is slowly brewing.

Features of PITEST:
    - passing in arguments at run time
    - efficient and selective test discovery
    - dependency tracking and parallel testing
    - snake_case instead of camelCase
"""

from .args import Args, ArgsError
from .case import TestCase
from .dag import Dag, DagError
from .deps import Deps
from .discover import Discover, DiscoverError
from .main import Main
from .name import PyName, PyNameError
from .result import CaseResult, SuiteResult
from .runner import Runner0
from .scheduler import Scheduler, SchedulerError
from .suite import TestSuiteBase, TestSuiteBaseError
