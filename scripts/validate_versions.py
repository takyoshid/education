#!/usr/bin/env python3
"""versions.md と、実際の設定・要件記述が一致していることを検査する。

版の数字はこの教材で最も早く腐る情報なので、1 箇所(versions.md)に集めてある。
集めただけでは、そこと実物がずれたときに誰も気づかない。この検査がその番人になる。

**レッスン本文は対象外にしてある。** 本文に出てくる「Python 3.7 以降 dict は順序を保つ」
のような記述は歴史的事実であり、表に合わせて書き換えるべきものではない。
理由は versions.md の「ただし、すべての版数をここに集めるわけではありません」を参照。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSIONS_FILE = ROOT / "versions.md"


# ---------------------------------------------------------------------------
# versions.md の読み取り
# ---------------------------------------------------------------------------


def load_declared_versions() -> dict[str, str]:
    """versions.md の表から {ツール名: 版} を読む。"""
    text = VERSIONS_FILE.read_text(encoding="utf-8")
    versions: dict[str, str] = {}
    # 「## 表」から次の見出しまでを対象にする。
    section = text.split("## 表", 1)[1].split("\n## ", 1)[0]
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("ツール", "---"):
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue
        # 「3.12 以上」→「3.12」
        match = re.match(r"([0-9]+(?:\.[0-9]+)*)", cells[1])
        if match:
            versions[cells[0]] = match.group(1)
    return versions


def major(version: str) -> str:
    return version.split(".", 1)[0]


def minor(version: str) -> str:
    parts = version.split(".")
    return ".".join(parts[:2])


# ---------------------------------------------------------------------------
# 個別の検査
# ---------------------------------------------------------------------------


def check_workflow(declared: dict[str, str]) -> list[str]:
    """CI のセットアップ版が表と一致しているか。"""
    errors: list[str] = []
    path = ROOT / ".github/workflows/curriculum-quality.yml"
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)

    # python-version: ["3.12", "3.13"] — 最小版が表と一致し、
    # かつ「1 つ上」も検査されていること。
    matrices = re.findall(r'python-version:\s*\[([^\]]+)\]', text)
    if not matrices:
        errors.append(f"{rel}: python-version のマトリクスが見つからない")
    for raw in matrices:
        found = re.findall(r'"([0-9]+\.[0-9]+)"', raw)
        if not found:
            errors.append(f"{rel}: python-version を読み取れない: [{raw}]")
            continue
        want = minor(declared["Python"])
        if found[0] != want:
            errors.append(
                f"{rel}: python-version の最小が {found[0]}。"
                f"versions.md は Python {want} なので一致させること"
            )
        if len(found) < 2:
            errors.append(
                f"{rel}: python-version が {found} の 1 つだけ。"
                "学習者は最新版を入れることが多いので、新しい版も検査すること"
            )

    for tool, key in (("Node.js", "node-version"), ("Ruby", "ruby-version")):
        found = re.findall(rf'{key}:\s*"([0-9]+(?:\.[0-9]+)*)"', text)
        if not found:
            errors.append(f"{rel}: {key} が見つからない")
            continue
        want = declared[tool]
        for value in found:
            if not value.startswith(major(want)):
                errors.append(
                    f"{rel}: {key} が {value}。versions.md は {tool} {want}"
                )
    return errors


def check_package_json(declared: dict[str, str]) -> list[str]:
    """package.json の依存が表と一致しているか。"""
    errors: list[str] = []
    targets = [
        "phase6-web-frontend/project/stage2-react/package.json",
        "phase6-web-frontend/exercises/solutions/ex06-react-solution/package.json",
    ]
    # package.json のキー -> versions.md のツール名
    watched = {
        "react": "React",
        "react-dom": "React",
        "@types/react": "React",
        "@types/react-dom": "React",
        "typescript": "TypeScript",
        "vite": "Vite",
    }
    for name in targets:
        path = ROOT / name
        if not path.exists():
            errors.append(f"{name}: 検査対象だが存在しない")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        for key, tool in watched.items():
            if key not in deps:
                continue
            want = declared[tool]
            # "^19.0.0" / "~5.7.2" から数字だけ取り出す
            actual = re.sub(r"^[^0-9]*", "", deps[key])
            if not actual.startswith(want):
                errors.append(
                    f"{name}: {key} が {deps[key]}。"
                    f"versions.md は {tool} {want} なので一致させること"
                )
    return errors


def check_docker_images(declared: dict[str, str]) -> list[str]:
    """Docker イメージのタグが表と一致しているか。"""
    errors: list[str] = []
    want = declared["PostgreSQL"]
    pattern = re.compile(r"postgres:([0-9]+)(?:[-.][A-Za-z0-9.-]+)?")
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir() or "node_modules" in path.parts or ".git" in path.parts:
            continue
        if path.suffix not in {".md", ".yml", ".yaml"}:
            continue
        if path == VERSIONS_FILE:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for found in pattern.findall(text):
            if found != major(want):
                errors.append(
                    f"{path.relative_to(ROOT)}: postgres:{found} を参照している。"
                    f"versions.md は PostgreSQL {want}"
                )
    return errors


# 「この版を使う」と宣言している記述を拾うためのパターン。
#
# 版が `3.12` のように細かく指定されているか、`18+` `16 以上` のように
# 下限として書かれている場合だけを対象にする。「Python 3」のような
# 言語そのものを指す言い方は、版の指定ではないので拾わない。
DECLARATION_PATTERN = re.compile(
    r"(Python|Node\.js|PostgreSQL|React|TypeScript|Vite)"
    r"[  ]*v?"
    r"("
    r"[0-9]+\.[0-9]+(?:\.[0-9]+)?"   # 3.12 / 5.7.2
    r"|[0-9]+(?=[  ]*(?:\+|以上|系))"  # 18+ / 16 以上 / 19 系
    r")"
)

# 歴史的事実を述べている行を見分けるための語。
#
# 「dict が挿入順を保つのは Python 3.7 以降」は要件ではない。
# こういう文の版数を表に合わせて書き換えると、その書き方が存在する理由が消える。
# 検査する場所を絞ってもなお本文の引用が混ざりうるので、ここでも守る。
#
# 要件を述べるときは「以上」を使い、歴史を述べるときは「以降」を使う、
# という書き分けが教材内で保たれていることが前提になっている。
HISTORICAL_MARKERS = (
    "以降",
    "より前",
    "未満",
    "で導入",
    "で追加",
    "が追加",
    "から使え",
    "から利用",
    "廃止",
    "予定",
    "時代",
    "保つ",
    "書き換えてはいけない",
)


def _is_historical(line: str) -> bool:
    return any(marker in line for marker in HISTORICAL_MARKERS)

# 要件記述を検査するファイル。ここに挙げた場所だけが「表と一致すべき」対象。
# レッスン本文を入れていないのは意図的(versions.md の説明を参照)。
REQUIREMENT_TARGETS = [
    "README.md",
    "longitudinal-project/README.md",
    "fixtures/README.md",
    # ポートフォリオの README 例。学習者がそのまま写すので、
    # ここに書かれた版が教材の他の場所と食い違っていると恥ずかしい。
    "phase12-projects-oss/lessons/04-portfolio.md",
]


def _phase_readme_prerequisites() -> list[tuple[str, str]]:
    """各 Phase README の「前提知識」節を (表示名, 本文) で返す。"""
    sections: list[tuple[str, str]] = []
    for path in sorted(ROOT.glob("phase*/README.md")):
        text = path.read_text(encoding="utf-8")
        if "## 前提知識" not in text:
            continue
        body = text.split("## 前提知識", 1)[1].split("\n## ", 1)[0]
        sections.append((f"{path.relative_to(ROOT)} の「前提知識」", body))
    return sections


def _capstone_sections() -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    capstone = ROOT / "phase12-projects-oss/capstone"
    if not capstone.exists():
        return sections
    for path in sorted(capstone.glob("*.md")):
        sections.append((str(path.relative_to(ROOT)), path.read_text(encoding="utf-8")))
    return sections


def _allowed_versions(declared: dict[str, str]) -> dict[str, set[str]]:
    """ツールごとに、書かれていてよい版の集合を組み立てる。

    Python だけは CI が複数版で検査しているので、その一覧も許す。
    「最小版は 3.12 だが 3.13 でも通ることを確かめている」という記述は正しい。
    """
    allowed = {tool: {version} for tool, version in declared.items()}
    workflow = (ROOT / ".github/workflows/curriculum-quality.yml").read_text(
        encoding="utf-8"
    )
    for raw in re.findall(r'python-version:\s*\[([^\]]+)\]', workflow):
        allowed["Python"].update(re.findall(r'"([0-9]+\.[0-9]+)"', raw))
    return allowed


def check_requirement_statements(declared: dict[str, str]) -> list[str]:
    """「この版を使う」と宣言している箇所が表と一致しているか。"""
    errors: list[str] = []
    allowed = _allowed_versions(declared)

    sections: list[tuple[str, str]] = []
    for name in REQUIREMENT_TARGETS:
        path = ROOT / name
        if path.exists():
            sections.append((name, path.read_text(encoding="utf-8")))
    sections.extend(_phase_readme_prerequisites())
    sections.extend(_capstone_sections())

    for label, text in sections:
        for line in text.splitlines():
            if _is_historical(line):
                continue
            for tool, found in DECLARATION_PATTERN.findall(line):
                candidates = allowed.get(tool)
                if candidates is None:
                    continue
                # 表が「3.12」なら 3.12 でも 3.12.1 でもよい。
                # 表が「19」なら 19 系すべてを許す。
                if any(
                    found == want
                    or found.startswith(want + ".")
                    or major(found) == want
                    for want in candidates
                ):
                    continue
                errors.append(
                    f"{label}: {tool} {found} を指定している。"
                    f"versions.md は {tool} {declared[tool]}"
                )
    return errors


def check_versions_file_is_referenced() -> list[str]:
    """versions.md が README から辿れること。孤立した表は更新されなくなる。"""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    if "versions.md" in text:
        return []
    return ["README.md: versions.md への導線がない。辿れない表は更新されなくなる"]


# ---------------------------------------------------------------------------


def main() -> int:
    declared = load_declared_versions()
    required = {"Python", "Node.js", "PostgreSQL", "React", "TypeScript", "Vite", "Ruby"}
    missing = required - declared.keys()
    if missing:
        print(f"versions.md の表に {sorted(missing)} がありません。", file=sys.stderr)
        return 1

    errors: list[str] = []
    errors += check_workflow(declared)
    errors += check_package_json(declared)
    errors += check_docker_images(declared)
    errors += check_requirement_statements(declared)
    errors += check_versions_file_is_referenced()

    if errors:
        print(f"バージョンの不一致が {len(errors)} 件あります:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "\nversions.md の表を直すか、指摘された箇所を表に合わせてください。",
            file=sys.stderr,
        )
        return 1

    declared_text = ", ".join(f"{k} {v}" for k, v in declared.items())
    print(f"バージョンの整合を確認しました ({declared_text})。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
