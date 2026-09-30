
from .base import Matcher
from .sift import SIFTMatcher
from .hopc import HOPCMatcher
from .cfog import CFOGMatcher
from .superpoint_lightglue import SuperPointLightGlueMatcher
from .loftr import LoFTRMatcher


MATCHER_REGISTRY = {
    "sift": SIFTMatcher,
    "hopc": HOPCMatcher,
    "cfog": CFOGMatcher,
    "superpoint_lightglue": SuperPointLightGlueMatcher,
    "loftr": LoFTRMatcher,
}


def create_matcher(name, **kwargs):
    name = name.lower().strip()

    if name not in MATCHER_REGISTRY:
        available = ", ".join(sorted(MATCHER_REGISTRY))
        raise ValueError(
            f"Unknown matcher '{name}'. Available: {available}"
        )

    return MATCHER_REGISTRY[name](**kwargs)


def available_matchers():
    return tuple(sorted(MATCHER_REGISTRY))
