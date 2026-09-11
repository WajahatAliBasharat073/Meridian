"""Shared policy constants used by more than one engine.

Small on purpose: this exists only for values that genuinely are the
same policy decision applied in two places, not a general dumping
ground. Before adding to it, check whether the two constants really are
one policy or just coincidentally the same number.
"""

from __future__ import annotations

# The "don't characterise a pattern from too little data" bar. punctuality.py
# (focus-session start times) and theory_pace.py (question-timing pace) both
# independently defined this as 5 before this was pulled out -- it is one
# policy decision (refuse an insight below 5 real samples), not two.
MIN_SAMPLES_FOR_INSIGHT = 5
