# pyxel-playground
pyxelでレトロ風ゲームを作ってみたいリポジトリ
# Pyxel Playground

Pyxel で様々な図形描画やゲームの試作を行うプレイグラウンドプロジェクトです。

## 実行方法 (How to Run)

### Pythonファイルを直接実行する
ソースコードを直接実行する場合は、プロジェクトルートから **モジュールとして** 実行してください。
これにより `sources` パッケージ内のインポートが正しく解決されます。

```bash
# シェイプデモの実行
uv run python -m sources.shape_demo.shape_demo

# または、ルートにあるランチャーを使用
uv run python run_shape_demo.py
```

### パッケージ (.pyxapp) を実行する
作成済みの `.pyxapp` ファイルを実行するには `pyxel play` コマンドを使用します。

```bash
uv run pyxel play pages/shape_demo/shape_demo.pyxapp
```

## パッケージ作成とデプロイ (Packaging & Deployment)

Webブラウザ (Wasm) で動作させるために、アプリケーションをパッケージ化して `pages` ディレクトリに配置します。

### 1. 実行ファイル (.pyxapp) の作成
インポート構造を維持するため、プロジェクトルート (`.`) を起点にパッケージ化します。
その際、ルートからのエントリーポイントとなる一時的なスクリプトを作成します。

```bash
# 1. 一時的な起動スクリプトを作成
echo "from sources.shape_demo.shape_demo import App; App()" > run_shape_demo.py

# 2. パッケージ化 (ルート起点)
uv run pyxel package . run_shape_demo.py

# 3. リネームして配置
mv pyxel-playground.pyxapp pages/shape_demo/shape_demo.pyxapp

# 4. 一時ファイルを削除
rm run_shape_demo.py
```
※ `pages/shape_demo/index.html` からはこのファイル名で参照するように設定します。

pyxelでレトロ風ゲームを作ってみたいリポジトリ
