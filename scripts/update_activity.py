from __future__ import annotations

import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


USER = "subean-choi"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "activity-lotus.svg"
COLORS = ["#FF5CA8", "#E7B72B", "#F0F6FC"]


def fetch_events() -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN")
    request = urllib.request.Request(
        f"https://api.github.com/users/{USER}/events/public?per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "subean-choi-profile-activity",
        },
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def counts_by_day(events: list[dict], days: int = 21) -> list[tuple[datetime, int]]:
    now = datetime.now(timezone.utc)
    floor = now.date() - timedelta(days=days - 1)
    counter: Counter[str] = Counter()
    for event in events:
        created_at = event.get("created_at")
        if not created_at:
            continue
        day = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
        if day >= floor:
            counter[day.isoformat()] += 1
    return [
        (datetime.combine(floor + timedelta(days=i), datetime.min.time()), counter[(floor + timedelta(days=i)).isoformat()])
        for i in range(days)
    ]


def render(rows: list[tuple[datetime, int]]) -> str:
    max_count = max((count for _, count in rows), default=0)
    total = sum(count for _, count in rows)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bars = []
    labels = []
    for idx, (day, count) in enumerate(rows):
        x = 52 + idx * 43.5
        height = 14 if count == 0 else 26 + (count / max(max_count, 1)) * 100
        y = 315 - height
        color = COLORS[idx % len(COLORS)] if count else "#30363D"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="24" height="{height:.1f}" rx="2" fill="{color}" opacity="{1 if count else .7}"/>'
            f'<rect x="{x + 7:.1f}" y="{y - 8:.1f}" width="10" height="5" fill="{color}" opacity="{.9 if count else .35}"/>'
        )
        if idx in (0, 5, 10, 15, 20):
            labels.append(f'<text x="{x + 12:.1f}" y="344" text-anchor="middle" fill="#8B949E" font-size="11">{day.strftime("%m/%d")}</text>')

    return f'''<svg width="1200" height="420" viewBox="0 0 1200 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">공개 활동 기록</title>
  <desc id="desc">최근 21일 동안의 공개 GitHub 활동 기록입니다.</desc>
  <defs>
    <pattern id="ledger" width="29" height="29" patternUnits="userSpaceOnUse"><path d="M29 0H0V29" fill="none" stroke="#30363D" opacity=".28"/></pattern>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#FF5CA8"/><stop offset="1" stop-color="#E7B72B"/></linearGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="frame"><rect x="2" y="2" width="1196" height="416" rx="10"/></clipPath>
  </defs>
  <rect width="1200" height="420" rx="12" fill="#0D1117"/>
  <rect x="2" y="2" width="1196" height="416" rx="10" fill="none" stroke="#30363D" stroke-width="2"/>
  <rect x="2" y="2" width="1196" height="416" rx="10" fill="url(#ledger)" clip-path="url(#frame)"/>
  <path d="M2 2H1198" stroke="url(#edge)" stroke-width="8"/>
  <g font-family="Arial, Helvetica, sans-serif">
    <text x="48" y="58" fill="#8B949E" font-size="14" font-weight="700" letter-spacing="5">03 / 활동 기록</text>
    <text x="48" y="113" fill="#F0F6FC" font-size="46" font-weight="900" letter-spacing="-1">공개 활동 기록</text>
    <text x="50" y="144" fill="#FF5CA8" font-family="Noto Sans KR, Arial, sans-serif" font-size="14" letter-spacing="2">최근 21일 / 공개 활동 {total:02d}건</text>
    <text x="1150" y="57" text-anchor="end" fill="#8B949E" font-family="Noto Sans KR, Arial, sans-serif" font-size="12">갱신 {updated}</text>
  </g>
  <g>{''.join(bars)}</g>
  <g font-family="Courier New, monospace">{''.join(labels)}</g>
  <path d="M48 365H976" stroke="#30363D" stroke-width="2"/>
  <text x="48" y="394" fill="#C9D1D9" font-family="Noto Sans KR, Arial, sans-serif" font-size="14" letter-spacing="2">최근 21일의 공개 이벤트를 날짜별로 집계합니다</text>

  <g transform="translate(1030 172)">
    <circle cx="54" cy="62" r="68" fill="#FF5CA8" opacity=".08" filter="url(#glow)"/>
    <path d="M54 0C78 32 78 55 54 78C30 55 30 32 54 0Z" fill="#FF5CA8"/>
    <path d="M0 33C35 36 54 54 54 91C21 84 4 65 0 33Z" fill="#B83F7A"/>
    <path d="M108 33C73 36 54 54 54 91C87 84 104 65 108 33Z" fill="#B83F7A"/>
    <path d="M-9 85C26 73 52 84 64 118C27 121 2 109-9 85Z" fill="#F0F6FC"/>
    <path d="M117 85C82 73 56 84 44 118C81 121 106 109 117 85Z" fill="#F0F6FC"/>
    <path d="M20 124H88" stroke="#E7B72B" stroke-width="5"/>
    <circle cx="54" cy="62" r="83" fill="none" stroke="#30363D" stroke-dasharray="4 9">
      <animateTransform attributeName="transform" type="rotate" from="0 54 62" to="360 54 62" dur="22s" repeatCount="indefinite"/>
    </circle>
  </g>
  <rect x="0" y="0" width="1200" height="2" fill="#FF5CA8" opacity=".8">
    <animate attributeName="y" values="8;410;8" dur="7s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;.6;0" dur="7s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


def main() -> None:
    events = fetch_events()
    OUT.write_text(render(counts_by_day(events)), encoding="utf-8")


if __name__ == "__main__":
    main()

