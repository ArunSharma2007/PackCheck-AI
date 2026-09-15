import json
import re
from difflib import SequenceMatcher
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RULES_FILE = BASE_DIR / "data" / "rules.json"


def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def keyword_match_score(keyword, text):
    keyword_words = re.findall(r"[a-z0-9]+", keyword.lower())
    text_words = re.findall(r"[a-z0-9]+", text.lower())

    if not keyword_words or not text_words:
        return 0

    keyword_text = " ".join(keyword_words)
    if keyword_text in " ".join(text_words):
        return 1

    window_size = len(keyword_words)
    best_score = 0

    for start in range(len(text_words)):
        window = " ".join(text_words[start:start + window_size])
        if not window:
            continue
        best_score = max(
            best_score,
            SequenceMatcher(None, keyword_text, window).ratio()
        )

    return best_score

def rule_match_score(rule, text):
    keyword_scores = [
        keyword_match_score(keyword, text)
        for keyword in rule.get("keywords", [])
    ]
    best_score = max(keyword_scores, default=0)

    evidence_patterns = rule.get("evidence_patterns", [])
    evidence_hits = sum(
        bool(re.search(pattern, text, re.IGNORECASE))
        for pattern in evidence_patterns
    )
    minimum_evidence = rule.get("minimum_evidence", 1)

    if evidence_hits >= minimum_evidence:
        return 1
    if evidence_hits:
        best_score = max(best_score, 0.7)

    return best_score


def check_compliance(text, readability=None):
    rules = load_rules()
    text_lower = text.lower()

    results = []
    passed = 0
    failed = 0
    manual_review = 0
    partial = 0
    manual_review_credit = 0
    readable_for_manual_credit = len(text_lower.split()) >= 3

    if readability is not None:
        readable_for_manual_credit = (
            float(readability.get("average_confidence", 0)) >= 60
        )

    for rule in rules:
        match_score = rule_match_score(rule, text_lower)
        found = match_score == 1
        partially_found = 0.7 <= match_score < 1
        automatic_status = None

        if rule["rule_id"] == "R9" and readability is not None:
            confidence = float(readability.get("average_confidence", 0))
            if confidence >= 80:
                automatic_status = "PASS"
            elif confidence < 40:
                automatic_status = "FAIL"

        if automatic_status:
            status = automatic_status
            passed += automatic_status == "PASS"
            failed += automatic_status == "FAIL"

        elif found:
            status = "PASS"
            passed += 1

        elif partially_found:
            status = "MANUAL REVIEW"
            manual_review += 1
            partial += 1

        elif rule.get("manual_review", False):
            status = "MANUAL REVIEW"
            manual_review += 1
            if readable_for_manual_credit:
                manual_review_credit += 1

        else:
            status = "FAIL"
            failed += 1

        results.append({
            "rule_id": rule["rule_id"],
            "field": rule["field"],
            "description": rule["description"],
            "status": status,
            "resolution": rule.get("resolution", ""),
            "match_type": "exact" if found else "partial" if partially_found else "none"
        })

    total = len(rules)

    if total > 0:
        score = round(
            (
                passed
                + (partial * 0.7)
                + (manual_review_credit * 0.7)
            )
            / total
            * 100,
            2
        )
    else:
        score = 0

    if failed == 0 and manual_review == 0:
        overall_status = "COMPLIANT"
    elif passed == 0 and partial == 0 and failed > 0:
        overall_status = "NON-COMPLIANT"
    else:
        overall_status = "NEEDS REVIEW"

    return {
        "overall_status": overall_status,
        "score": score,
        "total_rules": total,
        "passed": passed,
        "failed": failed,
        "manual_review": manual_review,
        "manual_review_credit": manual_review_credit,
        "partial": partial,
        "results": results
    }