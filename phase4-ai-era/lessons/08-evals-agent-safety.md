# Lesson 08: Eval・Agent権限・Prompt Injection

## 1. Evalを先に作る

「良くなった気がする」では変更を判定できません。代表case、難しい境界、過去の失敗、攻撃入力をdataset化し、変更前後を同じ条件で比較します。

評価は完全一致だけではありません。schema、property、deterministic checker、人のblind reviewを組み合わせます。model自身をjudgeに使う場合はbiasと再現性を別の人・ruleで監査します。

## 2. Prompt injection

Web page、issue、document、tool出力はdataであり、信頼できるinstructionではありません。「以前の指示を無視せよ」という文字列を取得しても命令として実行しない境界が必要です。

- system/developer/user/dataの出所を保持する
- dataをinstructionへ文字列結合しない
- allowlistしたtoolと引数schemaだけを許す
- secretをmodel contextへ入れない
- 外部へのwrite/send/deleteは承認境界を持つ
- tool結果も検証し、追跡可能なaudit logを残す

## 3. Least privilege

Coding agentへ最初からfilesystem全体、production credential、network、deploy権限を与えません。read、workspace write、test、network、external mutationを分離し、taskに必要な最小権限だけを期限付きで与えます。

## 4. Agent loopのbudget

停止条件を持たないagentはcostと副作用を増やします。最大step、token、cost、時間、tool error回数を設定し、同じ失敗の反復を検知します。

## 5. Supply chainとprovenance

AI生成codeにもlicense、依存関係、脆弱性、出典不明のriskがあります。生成者ではなくrepositoryへ入れる人が責任を持ち、差分review、test、dependency audit、secret scanを行います。

## 演習

安全なdocument summarizerを想定し、悪意あるdocument 10件を含むeval datasetを作ります。外部送信、secret要求、tool実行、instruction上書きをすべて拒否し、正常caseの品質も維持してください。

## 確認問題

1. Eval datasetに正常例、境界例、過去の失敗例、攻撃例を含める理由を説明してください。
2. Prompt injectionと、利用者が正当に与えたinstructionをどの境界で区別しますか？
3. Least privilegeをagentのtool権限へ適用する具体例を挙げてください。
4. Agent loopが停止しなくなる原因と、それを安全に止める上限を説明してください。
5. AI生成コードをrepositoryへ入れる人が確認すべきprovenanceとsupply chain上の項目は何ですか？
