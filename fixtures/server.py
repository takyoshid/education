#!/usr/bin/env python3
"""教材用のローカル API サーバ。

この教材の演習とプロジェクトは、外部のサービスではなくこのサーバに対して書く。
理由は fixtures/README.md に書いてある。要点だけ言えば、他人のサーバが止まった日に
教材が動かなくなるのを避けるためだ。

依存はゼロ。Python の標準ライブラリだけで動く。

    python3 fixtures/server.py

停止は Ctrl+C。ポートを変えたいときは --port を渡す。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_PORT = 8787

# ---------------------------------------------------------------------------
# 決定的な擬似乱数
#
# 同じ入力からは常に同じ数が出る。天気を「それらしく」見せながら、
# テストと学習者の手元で結果が一致することを保証するために使う。
# random モジュールを使わないのは、グローバルな状態を持たせないため。
# ---------------------------------------------------------------------------


def _seed(*parts: object) -> int:
    joined = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _unit(*parts: object) -> float:
    """0.0 以上 1.0 未満の決定的な値を返す。"""
    return _seed(*parts) / 2**64


def _pick(items: list, *parts: object):
    return items[_seed(*parts) % len(items)]


# ---------------------------------------------------------------------------
# データ読み込み
# ---------------------------------------------------------------------------


def _load_cities() -> list[dict]:
    with (DATA_DIR / "cities.json").open(encoding="utf-8") as handle:
        return json.load(handle)["cities"]


CITIES = _load_cities()

# jsonplaceholder 互換のダミーデータ。決定的に組み立てるので、
# 100 件の JSON をリポジトリに置かなくても毎回同じ結果になる。
_USER_NAMES = [
    ("Leanne Graham", "Bret", "Sincere@april.example"),
    ("Ervin Howell", "Antonette", "Shanna@melissa.example"),
    ("Clementine Bauch", "Samantha", "Nathan@yesenia.example"),
    ("Patricia Lebsack", "Karianne", "Julianne.OConner@kory.example"),
    ("Chelsey Dietrich", "Kamren", "Lucio_Hettinger@annie.example"),
    ("Dennis Schulist", "Leopoldo_Corkery", "Karley_Dach@jasper.example"),
    ("Kurtis Weissnat", "Elwyn.Skiles", "Telly.Hoeger@billy.example"),
    ("Nicholas Runolfsdottir", "Maxime_Nienow", "Sherwood@rosamond.example"),
    ("Glenna Reichert", "Delphine", "Chaim_McDermott@dana.example"),
    ("Clementina DuBuque", "Moriah.Stanton", "Rey.Padberg@karina.example"),
]

_TITLE_WORDS = [
    "sunt aut facere repellat provident",
    "qui est esse",
    "ea molestias quasi exercitationem",
    "eum et est occaecati",
    "nesciunt quas odio",
    "dolorem eum magni eos",
    "magnam facilis autem",
    "dolorem dolore est ipsam",
    "nesciunt iure omnis dolorem",
    "optio molestias id quia eum",
]

_BODY_LINES = [
    "quia et suscipit suscipit recusandae consequuntur expedita",
    "est rerum tempore vitae sequi sint nihil reprehenderit",
    "et iusto sed quo iure voluptatem occaecati omnis",
    "ut aspernatur corporis harum nihil quis provident sequi",
    "repudiandae veniam quaerat sunt sed alias aut fugiat",
]


def _users() -> list[dict]:
    users = []
    for index, (name, username, email) in enumerate(_USER_NAMES, start=1):
        users.append(
            {
                "id": index,
                "name": name,
                "username": username,
                "email": email,
                "phone": f"1-770-736-{8031 + index:04d}",
                "website": f"{username.lower().replace('.', '-')}.example",
                "address": {
                    "street": _pick(
                        ["Kulas Light", "Victor Plains", "Douglas Extension"],
                        "street",
                        index,
                    ),
                    "suite": f"Apt. {100 + index}",
                    "city": _pick(
                        ["Gwenborough", "Wisokyburgh", "McKenziehaven"], "city", index
                    ),
                    "zipcode": f"{92998 + index}-{3874 + index}",
                },
                "company": {
                    "name": _pick(
                        ["Romaguera-Crona", "Deckow-Crist", "Keebler LLC"],
                        "company",
                        index,
                    ),
                    "catchPhrase": "Multi-layered client-server neural-net",
                },
            }
        )
    return users


def _posts() -> list[dict]:
    posts = []
    for post_id in range(1, 101):
        user_id = (post_id - 1) // 10 + 1
        title = _pick(_TITLE_WORDS, "title", post_id)
        body = "\n".join(
            _pick(_BODY_LINES, "body", post_id, line) for line in range(2)
        )
        posts.append(
            {"userId": user_id, "id": post_id, "title": title, "body": body}
        )
    return posts


USERS = _users()
POSTS = _posts()


# ---------------------------------------------------------------------------
# 天気の生成
#
# 緯度・経度・日付から決定的に組み立てる。実在の観測値ではないが、
# 緯度が高いほど寒く、季節で変動し、同じ都市の同じ日には必ず同じ値が出る。
# 「気温が現実的な範囲に収まっているか」を学習者が検算できることが大事なので、
# 完全な乱数にはしていない。
# ---------------------------------------------------------------------------

# WMO weather code。Open-Meteo が返すものと同じ体系。
_WEATHER_CODES = [0, 1, 2, 3, 45, 51, 61, 63, 71, 80, 95]


def _base_temperature(latitude: float, day_of_year: int) -> float:
    """緯度と季節から日平均気温を作る。"""
    # 赤道で約 27 度、極で約 -15 度。
    equator_bias = 27.0 - (abs(latitude) / 90.0) * 42.0
    # 季節変動。北半球と南半球で位相を半年ずらす。
    seasonal_phase = (day_of_year - 196) / 365.0 * 2 * math.pi
    if latitude < 0:
        seasonal_phase += math.pi
    # 高緯度ほど season の振れ幅が大きい。
    amplitude = 3.0 + (abs(latitude) / 90.0) * 14.0
    return equator_bias + amplitude * math.cos(seasonal_phase)


def _daily_weather(latitude: float, longitude: float, day: date) -> dict:
    mean = _base_temperature(latitude, day.timetuple().tm_yday)
    jitter = (_unit("jitter", latitude, longitude, day.isoformat()) - 0.5) * 6.0
    mean += jitter
    spread = 4.0 + _unit("spread", latitude, day.isoformat()) * 5.0
    code = _pick(_WEATHER_CODES, "code", latitude, longitude, day.isoformat())
    return {
        "date": day.isoformat(),
        "max": round(mean + spread / 2, 1),
        "min": round(mean - spread / 2, 1),
        "mean": round(mean, 1),
        "code": code,
        "precipitation": round(
            _unit("precip", latitude, longitude, day.isoformat()) * 12.0, 1
        ),
    }


def _build_forecast(
    latitude: float, longitude: float, timezone_name: str, forecast_days: int
) -> dict:
    today = date.today()
    days = [
        _daily_weather(latitude, longitude, today + timedelta(days=offset))
        for offset in range(forecast_days)
    ]
    now = datetime.now(timezone.utc).replace(microsecond=0, second=0)
    current_day = days[0]
    # 現在気温は最低と最高の間を、時刻に応じて動かす。
    hour_ratio = (math.cos((now.hour - 14) / 24 * 2 * math.pi) + 1) / 2
    current_temp = current_day["min"] + (current_day["max"] - current_day["min"]) * hour_ratio
    humidity = 40 + int(_unit("humidity", latitude, longitude, today.isoformat()) * 55)
    wind = round(_unit("wind", latitude, longitude, today.isoformat()) * 28.0, 1)

    return {
        "latitude": round(latitude, 5),
        "longitude": round(longitude, 5),
        "generationtime_ms": 0.12,
        "utc_offset_seconds": 0,
        "timezone": timezone_name,
        "timezone_abbreviation": timezone_name.split("/")[-1],
        "elevation": 40.0,
        "current_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "apparent_temperature": "°C",
            "relative_humidity_2m": "%",
            "wind_speed_10m": "km/h",
            "weather_code": "wmo code",
        },
        "current": {
            "time": now.strftime("%Y-%m-%dT%H:%M"),
            "temperature_2m": round(current_temp, 1),
            "apparent_temperature": round(current_temp - wind * 0.08, 1),
            "relative_humidity_2m": humidity,
            "wind_speed_10m": wind,
            "weather_code": current_day["code"],
        },
        "daily_units": {
            "time": "iso8601",
            "temperature_2m_max": "°C",
            "temperature_2m_min": "°C",
            "precipitation_sum": "mm",
            "weather_code": "wmo code",
        },
        "daily": {
            "time": [day["date"] for day in days],
            "temperature_2m_max": [day["max"] for day in days],
            "temperature_2m_min": [day["min"] for day in days],
            "precipitation_sum": [day["precipitation"] for day in days],
            "weather_code": [day["code"] for day in days],
        },
    }


# ---------------------------------------------------------------------------
# 検索
# ---------------------------------------------------------------------------


def _search_cities(query: str, count: int) -> list[dict]:
    needle = query.strip().casefold()
    if not needle:
        return []
    matches = []
    for city in CITIES:
        haystack = [city["name"], city["name_en"], *city["aliases"]]
        if any(entry.casefold().startswith(needle) for entry in haystack):
            matches.append(city)
    matches.sort(key=lambda city: -city["population"])
    results = []
    for city in matches[:count]:
        results.append(
            {
                "id": city["id"],
                "name": city["name"],
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "elevation": city["elevation"],
                "country": city["country"],
                "country_code": city["country_code"],
                "admin1": city["admin1"],
                "timezone": city["timezone"],
                "population": city["population"],
            }
        )
    return results


def _city_for(latitude: float, longitude: float) -> dict | None:
    """座標から最も近い都市を返す。timezone を決めるために使う。"""
    best = None
    best_distance = float("inf")
    for city in CITIES:
        distance = (city["latitude"] - latitude) ** 2 + (
            city["longitude"] - longitude
        ) ** 2
        if distance < best_distance:
            best, best_distance = city, distance
    # 1 度四方より遠ければ「知らない座標」とみなす。
    return best if best_distance < 1.0 else None


# ---------------------------------------------------------------------------
# SVG プレースホルダ画像
# ---------------------------------------------------------------------------


def _placeholder_svg(seed: str, width: int, height: int) -> bytes:
    hue = _seed("hue", seed) % 360
    hue2 = (hue + 40) % 360
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="placeholder {seed}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="hsl({hue} 60% 62%)"/>
      <stop offset="100%" stop-color="hsl({hue2} 55% 38%)"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#g)"/>
  <text x="50%" y="50%" fill="rgba(255,255,255,0.85)" font-family="system-ui, sans-serif"
        font-size="{max(12, min(width, height) // 6)}" text-anchor="middle" dominant-baseline="middle">{width}×{height}</text>
</svg>"""
    return svg.encode("utf-8")


# ---------------------------------------------------------------------------
# HTTP ハンドラ
# ---------------------------------------------------------------------------


class FixtureHandler(BaseHTTPRequestHandler):
    server_version = "CurriculumFixtures/1.0"
    protocol_version = "HTTP/1.1"

    # 学習中はリクエストが流れる様子が見えたほうがよいので既定は True。
    # テストからは False にして出力を黙らせる。
    log_requests = True

    # -- 共通のヘルパ ------------------------------------------------------

    def _send(
        self,
        status: int,
        body: bytes,
        content_type: str = "application/json; charset=utf-8",
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        # ブラウザの fetch から直接叩けるようにする。
        # 学習用のローカルサーバなので全許可でよい。
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, status: int, payload: object, **kwargs) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._send(status, body, **kwargs)

    def _error(self, status: int, message: str) -> None:
        self._send_json(status, {"error": True, "reason": message})

    def log_message(self, fmt: str, *args) -> None:
        # 既定の実装は stderr に書く。学習中は素直に stdout へ出したい。
        if self.log_requests:
            print("  " + fmt % args)

    # -- 障害注入 ----------------------------------------------------------

    def _apply_fault_injection(self, params: dict[str, list[str]]) -> bool:
        """`_delay` / `_fail` / `_empty` を処理する。

        レスポンスを送ったら True を返す。呼び出し側はそこで打ち切る。
        loading・error・empty の状態を確実に再現するための仕組みで、
        実在の API では狙って起こせない。
        """
        delay_ms = params.get("_delay", ["0"])[0]
        try:
            delay = min(float(delay_ms), 30_000) / 1000.0
        except ValueError:
            delay = 0.0
        if delay > 0:
            time.sleep(delay)

        if "_fail" in params:
            raw = params["_fail"][0] or "500"
            try:
                status = int(raw)
            except ValueError:
                status = 500
            if not 400 <= status <= 599:
                status = 500
            self._error(status, f"障害注入 (_fail={status}) により失敗しました")
            return True
        return False

    # -- メソッド ----------------------------------------------------------

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(204, b"", content_type="text/plain")

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = parse_qs(parsed.query, keep_blank_values=True)

        if self._apply_fault_injection(params):
            return

        try:
            self._route_get(path, params)
        except Exception as exc:  # 学習用サーバなので原因を隠さず返す
            self._error(500, f"{type(exc).__name__}: {exc}")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = parse_qs(parsed.query, keep_blank_values=True)

        if self._apply_fault_injection(params):
            return

        length = int(self.headers.get("Content-Length") or 0)
        raw_body = self.rfile.read(length) if length else b""
        try:
            parsed_body = json.loads(raw_body) if raw_body else None
        except json.JSONDecodeError:
            parsed_body = None

        if path in ("/post", "/anything"):
            self._send_json(
                200,
                {
                    "args": {key: values[0] for key, values in params.items()},
                    "data": raw_body.decode("utf-8", "replace"),
                    "json": parsed_body,
                    "headers": dict(self.headers),
                    "method": "POST",
                    "url": f"http://{self.headers.get('Host')}{self.path}",
                },
            )
            return

        if path == "/posts":
            new_id = len(POSTS) + 1
            created = {"id": new_id, **(parsed_body or {})}
            self._send_json(201, created)
            return

        self._error(404, f"POST {path} は用意されていません")

    # -- ルーティング ------------------------------------------------------

    def _route_get(self, path: str, params: dict[str, list[str]]) -> None:
        if path == "/":
            self._send_json(200, _index_document())
            return

        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        # --- Open-Meteo 互換 ---
        if path == "/v1/search":
            name = params.get("name", [""])[0]
            count = _clamp_int(params.get("count", ["10"])[0], 1, 100, 10)
            results = _search_cities(name, count)
            if "_empty" in params:
                results = []
            payload: dict = {"generationtime_ms": 0.08}
            # Open-Meteo は結果ゼロのとき results キー自体を返さない。
            # 空配列と「キーなし」の両方を扱えるようにするのは実務でも必要になる。
            if results:
                payload["results"] = results
            self._send_json(200, payload)
            return

        if path == "/v1/forecast":
            latitude = _parse_float(params.get("latitude", [None])[0])
            longitude = _parse_float(params.get("longitude", [None])[0])
            if latitude is None or longitude is None:
                self._error(400, "latitude と longitude は必須です")
                return
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                self._error(400, "latitude / longitude が範囲外です")
                return
            forecast_days = _clamp_int(
                params.get("forecast_days", ["7"])[0], 1, 16, 7
            )
            city = _city_for(latitude, longitude)
            timezone_name = params.get("timezone", [None])[0] or (
                city["timezone"] if city else "UTC"
            )
            if timezone_name == "auto":
                timezone_name = city["timezone"] if city else "UTC"
            self._send_json(
                200, _build_forecast(latitude, longitude, timezone_name, forecast_days)
            )
            return

        # --- jsonplaceholder 互換 ---
        if path == "/users":
            self._send_json(200, [] if "_empty" in params else USERS)
            return

        match = re.fullmatch(r"/users/(\d+)", path)
        if match:
            user_id = int(match.group(1))
            user = next((u for u in USERS if u["id"] == user_id), None)
            if user is None:
                self._error(404, f"user {user_id} は存在しません")
            else:
                self._send_json(200, user)
            return

        if path == "/posts":
            items = POSTS
            if "userId" in params:
                wanted = _parse_int(params["userId"][0])
                items = [post for post in items if post["userId"] == wanted]
            items = _paginate(items, params)
            if "_empty" in params:
                items = []
            self._send_json(200, items)
            return

        match = re.fullmatch(r"/posts/(\d+)", path)
        if match:
            post_id = int(match.group(1))
            post = next((p for p in POSTS if p["id"] == post_id), None)
            if post is None:
                self._error(404, f"post {post_id} は存在しません")
            else:
                self._send_json(200, post)
            return

        # --- httpbin 互換 ---
        if path in ("/get", "/anything"):
            self._send_json(
                200,
                {
                    "args": {key: values[0] for key, values in params.items()},
                    "headers": dict(self.headers),
                    "method": "GET",
                    "url": f"http://{self.headers.get('Host')}{self.path}",
                },
            )
            return

        if path == "/response-headers":
            extra = {key: values[0] for key, values in params.items()
                     if not key.startswith("_")}
            self._send_json(200, extra, extra_headers=extra)
            return

        match = re.fullmatch(r"/status/(\d{3})", path)
        if match:
            status = int(match.group(1))
            self._send_json(status, {"status": status})
            return

        match = re.fullmatch(r"/delay/(\d+)", path)
        if match:
            time.sleep(min(int(match.group(1)), 30))
            self._send_json(200, {"delayed": int(match.group(1))})
            return

        # --- プレースホルダ画像 ---
        match = re.fullmatch(r"/photos/([^/]+)/(\d{1,4})/(\d{1,4})", path)
        if match:
            seed, width, height = match.group(1), int(match.group(2)), int(match.group(3))
            body = _placeholder_svg(seed, width, height)
            self._send(200, body, content_type="image/svg+xml; charset=utf-8")
            return

        self._error(404, f"GET {path} は用意されていません。/ で一覧を確認できます")


# ---------------------------------------------------------------------------
# 小さなユーティリティ
# ---------------------------------------------------------------------------


def _parse_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_int(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _clamp_int(raw: str, low: int, high: int, fallback: int) -> int:
    value = _parse_int(raw)
    if value is None:
        return fallback
    return max(low, min(high, value))


def _paginate(items: list[dict], params: dict[str, list[str]]) -> list[dict]:
    limit = _parse_int(params.get("_limit", [None])[0])
    page = _parse_int(params.get("_page", [None])[0])
    if limit is None and page is None:
        return items
    limit = limit or 10
    page = page or 1
    start = (page - 1) * limit
    return items[start : start + limit]


def _index_document() -> dict:
    return {
        "name": "教材用ローカル API サーバ",
        "why": "外部サービスの寿命に教材を縛られないため。詳細は fixtures/README.md",
        "endpoints": {
            "GET /v1/search?name=Tokyo&count=5": "都市名 → 座標 (Open-Meteo Geocoding 互換)",
            "GET /v1/forecast?latitude=&longitude=&forecast_days=7": "座標 → 天気 (Open-Meteo Forecast 互換)",
            "GET /users": "ユーザ一覧",
            "GET /users/{id}": "ユーザ 1 件",
            "GET /posts?userId=&_page=&_limit=": "投稿一覧",
            "GET /posts/{id}": "投稿 1 件",
            "POST /posts": "投稿の作成",
            "GET /get": "リクエストの内容をそのまま返す",
            "POST /post": "リクエストの内容をそのまま返す",
            "GET /response-headers?X-Foo=bar": "指定したヘッダを付けて返す",
            "GET /status/{code}": "指定した HTTP ステータスを返す",
            "GET /delay/{seconds}": "指定秒待ってから返す",
            "GET /photos/{seed}/{width}/{height}": "プレースホルダ画像 (SVG)",
        },
        "fault_injection": {
            "_delay=1500": "1500ms 待ってから応答する。loading 状態の確認に使う",
            "_fail=500": "指定したステータスで失敗する。error 状態の確認に使う",
            "_empty=1": "結果が 0 件の応答を返す。empty 状態の確認に使う",
        },
        "note": "これらは全てのエンドポイントで使える。実在の API では狙って起こせない状態を、確実に再現するための仕組み。",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), FixtureHandler)
    base = f"http://{args.host}:{args.port}"
    print(f"教材用 API サーバを起動しました: {base}")
    print(f"エンドポイント一覧: {base}/")
    print("停止するには Ctrl+C を押してください。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n停止しました。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
