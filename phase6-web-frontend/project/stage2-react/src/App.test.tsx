// =====================================================
// App.test.tsx — 主要ユーザーフローのコンポーネントテスト
// =====================================================
//
// このファイルは「何をテストすべきか」の実例です。書き方の説明は
// レッスン 12(フロントエンドのテスト)にあります。
//
// 方針が 2 つあります。
//
// 1. **利用者に見えるもので探す。** クラス名や内部の state ではなく、
//    ラベル、役割(role)、画面の文字で要素を見つけます。実装を書き換えても、
//    利用者から見た振る舞いが同じならテストは通り続けます。
//
// 2. **境界で差し替える。** fetch そのものではなく、api モジュールを
//    差し替えます。差し替える場所が 1 つなら、テストは読みやすく壊れにくい。

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { GeocodingResult, WeatherResponse } from "./types";

// api モジュールを差し替える。実際の通信は起きない。
vi.mock("./api/weather", () => ({
  fetchGeocode: vi.fn(),
  fetchWeather: vi.fn(),
}));

// 差し替えたモジュールを、型を保ったまま取り出す
const { fetchGeocode, fetchWeather } = await import("./api/weather");
const geocodeMock = vi.mocked(fetchGeocode);
const weatherMock = vi.mocked(fetchWeather);

// ---------------------------------------------------------------------------
// テスト用のデータ
//
// 実際のレスポンスをそのまま貼らず、必要な項目だけを組み立てる。
// 何がテストに効いているのかが読み取れるようにするため。
// ---------------------------------------------------------------------------

function makeLocation(name: string): GeocodingResult {
  return {
    name,
    country: "日本",
    country_code: "JP",
    latitude: 35.6895,
    longitude: 139.69171,
    elevation: 40,
  };
}

function makeWeather(temperature: number): WeatherResponse {
  return {
    current: {
      time: "2026-01-01T12:00",
      temperature_2m: temperature,
      apparent_temperature: temperature - 1,
      relative_humidity_2m: 60,
      wind_speed_10m: 10,
      weather_code: 0,
    },
    current_units: { temperature_2m: "°C", wind_speed_10m: "km/h" },
    daily: {
      time: ["2026-01-01"],
      temperature_2m_max: [temperature + 3],
      temperature_2m_min: [temperature - 3],
      weather_code: [0],
    },
  } as unknown as WeatherResponse;
}

/** 解決するタイミングを自分で決められる Promise。loading と競合の検証に使う。 */
function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

/**
 * 「解決を保留し、かつ AbortSignal を尊重する」偽の API。
 *
 * **偽物は、テストしたい軸については本物と同じに振る舞う必要があります。**
 * 本物の `fetchGeocode` は、signal が中断されると AbortError を投げます。
 * それを無視する偽物を使うと、中断されたはずの応答がそのまま返り、
 * 「競合を防げていない」ように見えてしまいます。**アプリではなく偽物の
 * 作りが原因でテストが赤くなる**、最も紛らわしい失敗です。
 */
function abortableDeferred<T>() {
  const { promise, resolve, reject } = deferred<T>();
  const impl = (_arg: unknown, signal?: AbortSignal) => {
    signal?.addEventListener("abort", () => {
      const error = new Error("Aborted");
      error.name = "AbortError";
      reject(error);
    });
    return promise;
  };
  return { impl, resolve };
}

beforeEach(() => {
  localStorage.clear();
  // App は初回マウント時に Tokyo を検索する。既定はそれが成功する状態。
  geocodeMock.mockResolvedValue([makeLocation("東京")]);
  weatherMock.mockResolvedValue(makeWeather(20));
});

afterEach(() => {
  vi.clearAllMocks();
});

// ---------------------------------------------------------------------------

describe("初期表示", () => {
  it("検索フォームが操作できる状態で表示される", async () => {
    render(<App />);
    expect(screen.getByRole("textbox", { name: "都市名" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /検索/ })).toBeInTheDocument();
    // 初回検索の完了を待ってからテストを終える(状態更新の取りこぼしを防ぐ)
    await screen.findByRole("heading", { name: /東京/ });
  });

  it("初回に取得した天気を表示する", async () => {
    render(<App />);
    expect(await screen.findByRole("heading", { name: /東京/ })).toBeInTheDocument();
    expect(await screen.findByText(/20/)).toBeInTheDocument();
  });
});

describe("検索", () => {
  it("入力して送信すると、その都市で検索される", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    geocodeMock.mockResolvedValue([makeLocation("大阪")]);
    weatherMock.mockResolvedValue(makeWeather(25));

    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "大阪");
    await user.click(screen.getByRole("button", { name: /検索/ }));

    expect(await screen.findByRole("heading", { name: /大阪/ })).toBeInTheDocument();
    expect(geocodeMock).toHaveBeenLastCalledWith("大阪", expect.anything());
  });

  it("Enter キーだけで送信できる", async () => {
    // キーボードだけで全操作できることは、この Phase の修了条件でもある。
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    geocodeMock.mockResolvedValue([makeLocation("京都")]);

    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "京都{Enter}");

    expect(await screen.findByRole("heading", { name: /京都/ })).toBeInTheDocument();
  });

  it("空欄では送信できない", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    await user.clear(screen.getByRole("textbox", { name: "都市名" }));
    expect(screen.getByRole("button", { name: /検索/ })).toBeDisabled();
  });
});

describe("5 つの状態", () => {
  it("loading — 取得中はそれと分かる表示になる", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    // 解決を保留して、loading の瞬間で止める
    const pending = deferred<GeocodingResult[]>();
    geocodeMock.mockReturnValue(pending.promise);

    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "札幌{Enter}");

    expect(await screen.findByRole("button", { name: /検索中/ })).toBeDisabled();
    expect(screen.getByRole("textbox", { name: "都市名" })).toBeDisabled();

    pending.resolve([makeLocation("札幌")]);
    await screen.findByRole("heading", { name: /札幌/ });
  });

  it("empty — 見つからないときは、その旨を伝える", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    geocodeMock.mockRejectedValue(new Error("「asdf」が見つかりませんでした。"));

    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "asdf{Enter}");

    expect(await screen.findByText(/見つかりませんでした/)).toBeInTheDocument();
  });

  it("error — 通信に失敗したときは、その旨を伝える", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    geocodeMock.mockRejectedValue(new Error("HTTP 503: Service Unavailable"));

    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "Tokyo{Enter}");

    expect(await screen.findByText(/503/)).toBeInTheDocument();
  });

  it("empty と error を同じ文言で片付けない", async () => {
    // 「見つからない」と「通信できない」は、利用者が取るべき行動が違う。
    // 別の言葉になっていることを確かめる。
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });
    const input = screen.getByRole("textbox", { name: "都市名" });

    geocodeMock.mockRejectedValue(new Error("「asdf」が見つかりませんでした。"));
    await user.clear(input);
    await user.type(input, "asdf{Enter}");
    const emptyText = (await screen.findByText(/見つかりませんでした/)).textContent;

    geocodeMock.mockRejectedValue(new Error("HTTP 503: Service Unavailable"));
    await user.clear(screen.getByRole("textbox", { name: "都市名" }));
    await user.type(screen.getByRole("textbox", { name: "都市名" }), "Tokyo{Enter}");
    const errorText = (await screen.findByText(/503/)).textContent;

    expect(emptyText).not.toEqual(errorText);
  });
});

describe("競合するリクエスト", () => {
  it("古い応答が、新しい検索結果を上書きしない", async () => {
    // このテストが、このファイルで最も重要。
    //
    // 検索中は入力欄が無効になるので、フォームからは二重に送信できない。
    // しかし**履歴のボタンは無効になっていません。**つまり「遅い検索の最中に
    // 履歴から別の都市を選ぶ」という操作は、利用者が普通に行えます。
    //
    // このとき、先に始めた遅い応答が後から返ると、素朴な実装では
    // 画面が古い結果に書き換わります。通信が常に速い開発環境では
    // まず再現しない不具合で、**狙って起こさない限り見つかりません。**
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    // 大阪も検索して、履歴に 2 件ためる
    geocodeMock.mockResolvedValue([makeLocation("大阪")]);
    weatherMock.mockResolvedValue(makeWeather(25));
    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "大阪{Enter}");
    await screen.findByRole("heading", { name: /大阪/ });

    // 履歴から「東京」を選ぶ。この応答をわざと遅らせる
    const slowTokyo = abortableDeferred<GeocodingResult[]>();
    geocodeMock.mockImplementationOnce(slowTokyo.impl as never);
    await user.click(screen.getByRole("button", { name: "東京" }));

    // 応答を待たずに、履歴から「大阪」を選ぶ(履歴ボタンは無効化されていない)
    geocodeMock.mockResolvedValue([makeLocation("大阪")]);
    weatherMock.mockResolvedValue(makeWeather(25));
    await user.click(screen.getByRole("button", { name: "大阪" }));
    await screen.findByRole("heading", { name: /大阪/ });

    // ここで、遅れていた東京の応答が返る
    slowTokyo.resolve([makeLocation("東京")]);

    // 画面は大阪のまま。東京に戻ってはいけない
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /大阪/ })).toBeInTheDocument();
    });
    expect(screen.queryByRole("heading", { name: /東京/ })).not.toBeInTheDocument();
  });
});

describe("検索履歴", () => {
  it("検索した都市が履歴に残り、クリックで再検索できる", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("heading", { name: /東京/ });

    geocodeMock.mockResolvedValue([makeLocation("大阪")]);
    weatherMock.mockResolvedValue(makeWeather(25));
    const input = screen.getByRole("textbox", { name: "都市名" });
    await user.clear(input);
    await user.type(input, "大阪{Enter}");
    await screen.findByRole("heading", { name: /大阪/ });

    // 履歴のボタンとして東京が残っている
    const historyButton = await screen.findByRole("button", { name: "東京" });

    geocodeMock.mockResolvedValue([makeLocation("東京")]);
    weatherMock.mockResolvedValue(makeWeather(20));
    await user.click(historyButton);

    expect(await screen.findByRole("heading", { name: /東京/ })).toBeInTheDocument();
  });
});
