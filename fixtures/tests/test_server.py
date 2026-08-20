"""fixtures/server.py の契約テスト。

このサーバは教材の演習・プロジェクト・CI が依存する土台なので、
壊れていないことを機械的に確かめる。特に次の 2 点を守る。

1. 決定的であること — 同じ入力からは常に同じ結果が返る
2. 状態を再現できること — loading / empty / error を狙って起こせる
"""

from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import FixtureHandler  # noqa: E402


class ServerTestCase(unittest.TestCase):
    """テストごとにサーバを立てず、クラス単位で 1 度だけ起動する。"""

    server: ThreadingHTTPServer
    thread: threading.Thread
    base: str

    @classmethod
    def setUpClass(cls) -> None:
        FixtureHandler.log_requests = False
        # ポート 0 を渡すと OS が空きポートを割り当てる。
        # 固定ポートにすると、開発中のサーバと衝突して CI が落ちる。
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    # -- ヘルパ ------------------------------------------------------------

    def get(self, path: str, **params) -> tuple[int, object]:
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def get_raw(self, path: str) -> tuple[int, bytes, str]:
        try:
            with urllib.request.urlopen(self.base + path, timeout=10) as response:
                return (
                    response.status,
                    response.read(),
                    response.headers.get("Content-Type", ""),
                )
        except urllib.error.HTTPError as error:
            return error.code, error.read(), error.headers.get("Content-Type", "")


class TestGeocoding(ServerTestCase):
    def test_finds_city_by_english_name(self) -> None:
        status, body = self.get("/v1/search", name="Tokyo")
        self.assertEqual(status, 200)
        self.assertEqual(body["results"][0]["name"], "東京")

    def test_finds_city_by_japanese_name(self) -> None:
        status, body = self.get("/v1/search", name="東京")
        self.assertEqual(status, 200)
        self.assertEqual(body["results"][0]["latitude"], 35.6895)

    def test_search_is_case_insensitive(self) -> None:
        _, lower = self.get("/v1/search", name="tokyo")
        _, upper = self.get("/v1/search", name="TOKYO")
        self.assertEqual(lower["results"], upper["results"])

    def test_no_match_omits_results_key(self) -> None:
        # Open-Meteo は 0 件のとき results キー自体を返さない。
        # この癖まで再現しないと、教材で「空の扱い」を正しく教えられない。
        status, body = self.get("/v1/search", name="存在しない都市")
        self.assertEqual(status, 200)
        self.assertNotIn("results", body)

    def test_count_limits_results(self) -> None:
        _, body = self.get("/v1/search", name="", count=3)
        self.assertNotIn("results", body)
        _, body = self.get("/v1/search", name="s", count=1)
        self.assertLessEqual(len(body.get("results", [])), 1)

    def test_empty_injection_returns_no_results(self) -> None:
        _, body = self.get("/v1/search", name="Tokyo", _empty="1")
        self.assertNotIn("results", body)


class TestForecast(ServerTestCase):
    TOKYO = {"latitude": 35.6895, "longitude": 139.69171}

    def test_returns_open_meteo_shape(self) -> None:
        status, body = self.get("/v1/forecast", **self.TOKYO, forecast_days=7)
        self.assertEqual(status, 200)
        for key in ("current", "current_units", "daily", "daily_units", "timezone"):
            self.assertIn(key, body)
        for key in ("temperature_2m", "relative_humidity_2m", "wind_speed_10m",
                    "weather_code", "time"):
            self.assertIn(key, body["current"])
        for key in ("time", "temperature_2m_max", "temperature_2m_min", "weather_code"):
            self.assertIn(key, body["daily"])

    def test_daily_arrays_have_matching_length(self) -> None:
        _, body = self.get("/v1/forecast", **self.TOKYO, forecast_days=5)
        daily = body["daily"]
        lengths = {len(values) for values in daily.values()}
        self.assertEqual(lengths, {5})

    def test_first_day_is_today(self) -> None:
        _, body = self.get("/v1/forecast", **self.TOKYO)
        self.assertEqual(body["daily"]["time"][0], date.today().isoformat())

    def test_max_is_never_below_min(self) -> None:
        _, body = self.get("/v1/forecast", **self.TOKYO, forecast_days=16)
        highs = body["daily"]["temperature_2m_max"]
        lows = body["daily"]["temperature_2m_min"]
        for high, low in zip(highs, lows):
            self.assertGreaterEqual(high, low)

    def test_is_deterministic(self) -> None:
        # 同じ座標・同じ日なら、何度呼んでも日別の値は変わらない。
        # 学習者の手元と模範解答が食い違わないための保証。
        _, first = self.get("/v1/forecast", **self.TOKYO)
        _, second = self.get("/v1/forecast", **self.TOKYO)
        self.assertEqual(first["daily"], second["daily"])

    def test_colder_at_higher_latitude(self) -> None:
        # 気温が緯度に反応することを確かめる。学習者が結果を見て
        # 「でたらめな数字ではない」と分かることに意味がある。
        _, singapore = self.get("/v1/forecast", latitude=1.28967, longitude=103.85007)
        _, reykjavik = self.get("/v1/forecast", latitude=64.13548, longitude=-21.89541)
        self.assertGreater(
            singapore["daily"]["temperature_2m_max"][0],
            reykjavik["daily"]["temperature_2m_max"][0],
        )

    def test_temperatures_stay_in_plausible_range(self) -> None:
        for latitude, longitude in [(35.6895, 139.69171), (64.13548, -21.89541),
                                    (1.28967, 103.85007), (-33.86785, 151.20732)]:
            _, body = self.get(
                "/v1/forecast", latitude=latitude, longitude=longitude, forecast_days=16
            )
            for value in body["daily"]["temperature_2m_max"]:
                self.assertTrue(-60 <= value <= 60, f"{value} is not plausible")

    def test_missing_coordinates_is_client_error(self) -> None:
        status, body = self.get("/v1/forecast", latitude=35.6895)
        self.assertEqual(status, 400)
        self.assertTrue(body["error"])

    def test_out_of_range_coordinates_is_client_error(self) -> None:
        status, _ = self.get("/v1/forecast", latitude=999, longitude=0)
        self.assertEqual(status, 400)

    def test_timezone_auto_resolves_to_nearest_city(self) -> None:
        _, body = self.get("/v1/forecast", **self.TOKYO, timezone="auto")
        self.assertEqual(body["timezone"], "Asia/Tokyo")


class TestPlaceholderData(ServerTestCase):
    def test_users_list(self) -> None:
        status, body = self.get("/users")
        self.assertEqual(status, 200)
        self.assertEqual(len(body), 10)
        self.assertEqual(body[0]["id"], 1)

    def test_single_user(self) -> None:
        status, body = self.get("/users/3")
        self.assertEqual(status, 200)
        self.assertEqual(body["id"], 3)

    def test_unknown_user_is_404(self) -> None:
        status, _ = self.get("/users/999")
        self.assertEqual(status, 404)

    def test_posts_list(self) -> None:
        status, body = self.get("/posts")
        self.assertEqual(status, 200)
        self.assertEqual(len(body), 100)

    def test_posts_filtered_by_user(self) -> None:
        _, body = self.get("/posts", userId=2)
        self.assertEqual(len(body), 10)
        self.assertTrue(all(post["userId"] == 2 for post in body))

    def test_pagination(self) -> None:
        _, page1 = self.get("/posts", _page=1, _limit=3)
        _, page2 = self.get("/posts", _page=2, _limit=3)
        self.assertEqual(len(page1), 3)
        self.assertEqual(len(page2), 3)
        self.assertNotEqual(page1[0]["id"], page2[0]["id"])

    def test_pagination_past_the_end_is_empty(self) -> None:
        _, body = self.get("/posts", _page=99, _limit=10)
        self.assertEqual(body, [])

    def test_single_post(self) -> None:
        status, body = self.get("/posts/1")
        self.assertEqual(status, 200)
        self.assertEqual(body["id"], 1)

    def test_data_is_deterministic(self) -> None:
        _, first = self.get("/posts/42")
        _, second = self.get("/posts/42")
        self.assertEqual(first, second)


class TestRequestEcho(ServerTestCase):
    def test_get_echoes_query_and_headers(self) -> None:
        status, body = self.get("/get", hello="world")
        self.assertEqual(status, 200)
        self.assertEqual(body["args"]["hello"], "world")
        self.assertEqual(body["method"], "GET")
        self.assertIn("Host", body["headers"])

    def test_post_echoes_json_body(self) -> None:
        payload = json.dumps({"name": "Ada"}).encode()
        request = urllib.request.Request(
            self.base + "/post",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read())
        self.assertEqual(body["json"], {"name": "Ada"})
        self.assertEqual(body["method"], "POST")

    def test_response_headers_endpoint_sets_headers(self) -> None:
        url = self.base + "/response-headers?" + urllib.parse.urlencode(
            {"X-Powered-By": "curriculum"}
        )
        with urllib.request.urlopen(url, timeout=10) as response:
            self.assertEqual(response.headers.get("X-Powered-By"), "curriculum")

    def test_status_endpoint_returns_requested_code(self) -> None:
        for code in (200, 404, 500, 503):
            status, _ = self.get(f"/status/{code}")
            self.assertEqual(status, code)


class TestFaultInjection(ServerTestCase):
    def test_fail_returns_requested_error(self) -> None:
        status, body = self.get("/posts", _fail=503)
        self.assertEqual(status, 503)
        self.assertTrue(body["error"])

    def test_fail_defaults_to_500(self) -> None:
        status, _ = self.get("/users", _fail="")
        self.assertEqual(status, 500)

    def test_fail_rejects_non_error_codes(self) -> None:
        # 2xx を _fail に渡しても「成功した失敗」にはしない。
        status, _ = self.get("/users", _fail=200)
        self.assertEqual(status, 500)

    def test_empty_returns_no_items(self) -> None:
        _, body = self.get("/posts", _empty=1)
        self.assertEqual(body, [])
        _, body = self.get("/users", _empty=1)
        self.assertEqual(body, [])

    def test_delay_actually_waits(self) -> None:
        import time

        started = time.monotonic()
        status, _ = self.get("/users", _delay=400)
        elapsed = time.monotonic() - started
        self.assertEqual(status, 200)
        self.assertGreaterEqual(elapsed, 0.35)

    def test_fault_injection_works_on_every_endpoint(self) -> None:
        for path in ("/v1/search", "/v1/forecast", "/users", "/posts", "/get"):
            status, _ = self.get(path, _fail=500)
            self.assertEqual(status, 500, f"{path} ignored _fail")


class TestPlaceholderImages(ServerTestCase):
    def test_returns_svg(self) -> None:
        status, body, content_type = self.get_raw("/photos/seed1/400/200")
        self.assertEqual(status, 200)
        self.assertIn("image/svg+xml", content_type)
        self.assertIn(b"<svg", body)

    def test_dimensions_are_honoured(self) -> None:
        _, body, _ = self.get_raw("/photos/seed1/640/360")
        self.assertIn(b'width="640"', body)
        self.assertIn(b'height="360"', body)

    def test_same_seed_gives_same_image(self) -> None:
        _, first, _ = self.get_raw("/photos/abc/100/100")
        _, second, _ = self.get_raw("/photos/abc/100/100")
        self.assertEqual(first, second)

    def test_different_seeds_give_different_images(self) -> None:
        _, first, _ = self.get_raw("/photos/abc/100/100")
        _, second, _ = self.get_raw("/photos/xyz/100/100")
        self.assertNotEqual(first, second)

    def test_has_accessible_label(self) -> None:
        # 教材は一貫してアクセシビリティを要求する。
        # 教材が配る画像自体がそれを守っていないと筋が通らない。
        _, body, _ = self.get_raw("/photos/abc/100/100")
        self.assertIn(b'role="img"', body)
        self.assertIn(b"aria-label", body)


class TestServiceBasics(ServerTestCase):
    def test_health(self) -> None:
        status, body = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_index_lists_endpoints(self) -> None:
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("endpoints", body)
        self.assertIn("fault_injection", body)

    def test_unknown_path_is_404_with_reason(self) -> None:
        status, body = self.get("/nope")
        self.assertEqual(status, 404)
        self.assertIn("reason", body)

    def test_cors_headers_present(self) -> None:
        # ブラウザの fetch から直接叩けないと、Phase 6 の演習が成立しない。
        with urllib.request.urlopen(self.base + "/health", timeout=10) as response:
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")


if __name__ == "__main__":
    unittest.main(verbosity=2)
