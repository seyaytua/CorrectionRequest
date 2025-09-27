#!/bin/bash

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境が有効化されているか確認
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "仮想環境を有効化しています..."
    source ../venv_grade_correction/bin/activate
fi

# アプリケーションを実行
echo "成績訂正申請システムを起動します..."
python main.py
