from pydantic import ConfigDict

from agent_barbell.agent.runtime_state import RuntimeState
from agent_barbell.model import Barbell
from agent_barbell.portfolio_manager import PortfolioManager
from agent_barbell.risk_manager import RiskManager


class BarbellRuntimeState(RuntimeState):
    """Per-conversation handle onto the managers a tool is allowed to touch.

    Ported from yieldseeker-app/api/agent_hack/agent/ys_runtime_state.py. Note what is absent:
    no execution manager and no signer. A tool physically cannot size or place a trade.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    barbell: Barbell
    portfolioManager: PortfolioManager
    riskManager: RiskManager
