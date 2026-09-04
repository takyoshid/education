/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    // ブラウザの API(document、要素、イベント)を Node の中で再現する。
    // これが無いと、コンポーネントを描画した瞬間に document が無いと言われる。
    environment: "jsdom",
    // 各テストの前に、追加のアサーション(toBeInTheDocument など)を読み込む。
    setupFiles: ["./src/setupTests.ts"],
    globals: true,
  },
});
