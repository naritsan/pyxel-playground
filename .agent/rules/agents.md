---
trigger: always_on
---

- AGENTS.md - Project Developer Guide

このプロジェクトの開発ルールと運用コマンドのメモです。

## ディレクトリ構成とインポート
- **ソースコード**: `sources/` ディレクトリ配下に配置します。
- **共有ライブラリ**: `sources/utils/` に配置し、他ファイルからは `from sources.utils import ...` でインポートします。
- **インポートの注意**: `sources` をパッケージルートとして扱うため、Pythonスクリプトを実行する際は必ず **プロジェクトルート** から実行し、`-m` オプションを使用するか、ルートにあるランチャースクリプトを経由してください。

## コマンドリファレンス

### 1. Pythonファイルの実行 (.py)
`sources` 以下のファイルを直接指定して (`python sources/...`) 実行すると `ModuleNotFoundError` になります。
以下のいずれかの方法で実行してください。

```bash
# 推奨: モジュールモードで実行
uv run python -m sources.shape_demo.shape_demo

# ランチャー経由で実行（もしあれば）
uv run python run_shape_demo.py
```

### 2. アプリケーションのパッケージ化 (.pyxapp)
Webデプロイ用にパッケージ化する際は、ディレクトリ階層 (`sources/...`) を維持するために **ルートディレクトリ (`.`)** を起点にします。
また、ルートからの適切なインポートを行うため、一時的な起動スクリプト (`run_shape_demo.py` 等) をルートに作成して、それをエントリーポイントとして指定してください。

```bash
# 例: 一時スクリプト作成 -> パッケージ化 -> 削除
echo "from sources.shape_demo.shape_demo import App; App()" > run_shape_demo.py
uv run pyxel package . run_shape_demo.py
mv pyxel-playground.pyxapp pages/shape_demo/shape_demo.pyxapp
rm run_shape_demo.py
```

### 3. Webページへのデプロイ
1. 上記手順で `.pyxapp` を作成（デフォルト名は `pyxel-playground.pyxapp`）。
2. `docs/pages/<app_name>/` ディレクトリへ移動・リネーム。
   ```bash
   mv pyxel-playground.pyxapp docs/pages/shape_demo/shape_demo.pyxapp
   ```
3. `docs/pages/<app_name>/index.html` で `<pyxel-play name="shape_demo.pyxapp">` を指定。

### 4. パッケージのローカル実行
パッケージが正しく動作するか確認するには：
```bash
uv run pyxel play docs/pages/shape_demo/shape_demo.pyxapp
```

## AI Agent向けルール
- **コマンド実行後の確認**: `run_command` を使用した際は、必ず終了コードやファイルの存在を確認してからユーザーに完了報告をすること。
- **Webデプロイ時の確認**: `import sources...` がパッケージ内で解決可能か、ディレクトリ構造を意識すること。