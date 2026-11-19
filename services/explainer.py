from models import Alert

NEXT_STEPS = {
    "critical": "Investigate immediately and take corrective action.",
    "warning": "Review the affected system and monitor the metric closely.",
    "info": "Review the metric and confirm whether any action is needed.",
}


def generate_explanation(alert: Alert) -> str:
    """Build an explanation from the alert's own fields using fixed rules.

    Args:
        alert: Alert whose severity, source, title, metric name, metric value,
            and threshold determine the explanation.

    Returns:
        Text comparing the metric value with its threshold, recommending a next
        step based on severity, and reporting acknowledgement. A truthy optional
        resolved_by value is uppercased; otherwise, the acknowledgement text is
        "Not yet acknowledged". No external AI or LLM service is called.

    Raises:
        KeyError: If the severity is not critical, warning, or info.
    """
    if alert.metric_value > alert.threshold:
        comparison = "exceeded"
    elif alert.metric_value < alert.threshold:
        comparison = "fell below"
    else:
        comparison = "reached"

    next_step = NEXT_STEPS[alert.severity]
    explanation = (
        f'This {alert.severity} alert from {alert.source} is titled "{alert.title}". '
        f"The {alert.metric_name} metric {comparison} its threshold: the current value is "
        f"{alert.metric_value}, compared with a threshold of {alert.threshold}. "
        f"Recommended next step: {next_step}"
    )
    resolved_by = getattr(alert, "resolved_by", None)
    acknowledgement = resolved_by.upper() if resolved_by else "Not yet acknowledged"
    return explanation + f" Acknowledged by: {acknowledgement}."