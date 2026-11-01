SEVERITY_WEIGHTS = {"informational": 5, "low": 20, "medium": 50, "high": 75, "critical": 95}


def classify_score(score: float) -> str:
    if score >= 90: return "critical"
    if score >= 75: return "high"
    if score >= 50: return "medium"
    if score >= 25: return "low"
    return "informational"


def score_alert(base: float, frequency: int = 1, correlated: bool = False) -> tuple[float, list[str]]:
    reasons = [f"base detection weight {base:.0f}"]
    score = min(100.0, base + min(20, max(0, frequency - 1) * 5) + (10 if correlated else 0))
    if frequency > 1: reasons.append(f"{frequency} related events increased frequency risk")
    if correlated: reasons.append("related activity sequence was correlated")
    return score, reasons
