#!/usr/bin/env python3
"""Match resume draft against job description: score and reorder skills."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_DRAFT = "output/resume.draft.json"
DEFAULT_JD = "output/job.jd.txt"
DEFAULT_CONTEXT = "output/job.context.json"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else project_root() / path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_keyword_data() -> dict:
    path = data_dir() / "jd_keywords.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_jd_corpus(jd_text: str, context: dict | None) -> str:
    parts = [jd_text.lower()]
    if context:
        parts.extend(k.lower() for k in context.get("keywords", []))
        for cluster in context.get("dominant_clusters", []):
            parts.extend(t.lower() for t in cluster.get("matched_terms", []))
    return " ".join(parts)


def tokenize_skill(skill: str) -> list[str]:
    tokens: list[str] = []
    lowered = skill.lower()
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", lowered):
        if len(word) >= 2:
            tokens.append(word)
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", skill):
        tokens.append(chunk)
    return tokens


def score_text_against_jd(text: str, corpus: str, keyword_data: dict) -> tuple[float, list[str]]:
    lowered_text = text.lower()
    matched: list[str] = []
    score = 0.0

    for term in keyword_data.get("tech_terms", []):
        t_lower = term.lower()
        if t_lower in corpus and (t_lower in lowered_text or term in text):
            score += 2.0
            matched.append(term)

    for token in tokenize_skill(text):
        if token.lower() in corpus:
            score += 1.0
            if token not in matched:
                matched.append(token)

    # Boost if skill line contains JD-heavy cluster terms
    for cluster_id, terms in keyword_data.get("clusters", {}).items():
        cluster_hits_in_jd = sum(1 for t in terms if t.lower() in corpus or t in corpus)
        if cluster_hits_in_jd == 0:
            continue
        cluster_hits_in_skill = sum(
            1 for t in terms if t.lower() in lowered_text or t in text
        )
        if cluster_hits_in_skill:
            score += cluster_hits_in_skill * 0.5

    return score, matched[:10]


def score_skill_list(skills: list[str], corpus: str, keyword_data: dict) -> list[dict]:
    scored = []
    for idx, skill in enumerate(skills):
        if not isinstance(skill, str) or not skill.strip():
            continue
        score, matched = score_text_against_jd(skill, corpus, keyword_data)
        scored.append(
            {
                "index": idx,
                "skill": skill,
                "score": round(score, 2),
                "matched_terms": matched,
            }
        )
    scored.sort(key=lambda x: (-x["score"], x["index"]))
    return scored


def score_experience_items(
    items: list[dict],
    corpus: str,
    keyword_data: dict,
    text_fields: list[str],
    label: str,
) -> list[dict]:
    results = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        combined = " ".join(str(item.get(f, "")) for f in text_fields)
        score, matched = score_text_against_jd(combined, corpus, keyword_data)
        results.append(
            {
                "type": label,
                "index": idx,
                "title": item.get(text_fields[0]) or item.get("company_name") or item.get("project_name"),
                "score": round(score, 2),
                "matched_terms": matched,
            }
        )
    results.sort(key=lambda x: (-x["score"], x["index"]))
    return results


def apply_skill_reorder(data: dict, scored: list[dict]) -> list[str]:
    notes: list[str] = []
    if not scored:
        return notes
    new_order = [s["skill"] for s in scored]
    old_skills = data.get("skillList") or []
    if new_order != old_skills:
        data["skillList"] = new_order
        notes.append(f"已按 JD 匹配度重排 skillList（共 {len(new_order)} 项）")
    return notes


def main() -> None:
    parser = argparse.ArgumentParser(description="JD-match skills and experiences against job description")
    parser.add_argument("draft", type=Path, nargs="?", default=DEFAULT_DRAFT)
    parser.add_argument("--jd", type=Path, default=DEFAULT_JD, help="Job description text file")
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT, help="job.context.json")
    parser.add_argument("--apply", action="store_true", help="Apply skill reorder to draft JSON")
    parser.add_argument("--write", action="store_true", help="Write changes (requires --apply)")
    parser.add_argument("--reorder-work", action="store_true", help="Also reorder workExpList by JD score")
    parser.add_argument("--reorder-projects", action="store_true", help="Also reorder projectList by JD score")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    args = parser.parse_args()

    draft_path = resolve_path(args.draft)
    jd_path = resolve_path(args.jd)
    ctx_path = resolve_path(args.context)

    if not draft_path.exists():
        print(f"草稿不存在: {draft_path}", file=sys.stderr)
        sys.exit(2)
    if not jd_path.exists():
        print(f"JD 未找到: {jd_path}", file=sys.stderr)
        print("请先运行 save_jd.py 或由用户提供目标岗位描述", file=sys.stderr)
        sys.exit(2)

    data = load_json(draft_path)
    jd_text = jd_path.read_text(encoding="utf-8")
    context = load_json(ctx_path) if ctx_path.exists() else None
    keyword_data = load_keyword_data()
    corpus = build_jd_corpus(jd_text, context)

    skills = data.get("skillList") or []
    scored_skills = score_skill_list(skills, corpus, keyword_data)
    scored_work = score_experience_items(
        data.get("workExpList") or [],
        corpus,
        keyword_data,
        ["company_name", "department_name", "work_desc"],
        "workExpList",
    )
    scored_projects = score_experience_items(
        data.get("projectList") or [],
        corpus,
        keyword_data,
        ["project_name", "project_role", "project_desc", "project_content"],
        "projectList",
    )

    report: dict[str, Any] = {
        "jd_path": str(jd_path),
        "dominant_clusters": (context or {}).get("dominant_clusters", []),
        "skills": scored_skills,
        "work_experience": scored_work,
        "projects": scored_projects,
        "suggestions": [],
    }

    if scored_skills and scored_skills[0]["score"] > 0:
        report["suggestions"].append(
            f"技能「{scored_skills[0]['skill'][:40]}…」与 JD 匹配度最高，已/建议置顶"
        )
    if context and context.get("title"):
        position = (data.get("profile") or {}).get("position", "")
        if position and context["title"] not in position:
            report["suggestions"].append(
                f"可考虑将 profile.position 与目标岗位对齐：{context['title']}"
            )

    apply_notes: list[str] = []
    if args.apply:
        apply_notes.extend(apply_skill_reorder(data, scored_skills))
        if args.reorder_work and scored_work:
            order = [data["workExpList"][w["index"]] for w in scored_work]
            if order != data.get("workExpList"):
                data["workExpList"] = order
                apply_notes.append("已按 JD 匹配度重排 workExpList")
        if args.reorder_projects and scored_projects:
            order = [data["projectList"][p["index"]] for p in scored_projects]
            if order != data.get("projectList"):
                data["projectList"] = order
                apply_notes.append("已按 JD 匹配度重排 projectList")
        if args.write and apply_notes:
            draft_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["applied"] = apply_notes

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=== JD 技能匹配（按相关度排序）===")
        for s in scored_skills[:10]:
            terms = ", ".join(s["matched_terms"][:5]) or "—"
            print(f"  [{s['score']}] {s['skill'][:60]}  ← {terms}")
        if apply_notes:
            print("\n已应用:")
            for n in apply_notes:
                print(f"  - {n}")

    sys.exit(0)


if __name__ == "__main__":
    main()
