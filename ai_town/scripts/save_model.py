"""
保存 sentence-transformers 模型到本地目录，便于离线机器使用。
用法（Windows cmd.exe）：
  .venv\Scripts\activate
  pip install sentence-transformers
  python ai_town\scripts\save_model.py --model all-MiniLM-L6-v2 --out C:\models\all-MiniLM-L6-v2

默认模型推荐：all-MiniLM-L6-v2（小巧、效果良好，适合体验与资源受限设备）。
"""
import argparse
from sentence_transformers import SentenceTransformer
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='all-MiniLM-L6-v2', help='HF model name (e.g. all-MiniLM-L6-v2)')
    parser.add_argument('--out', type=str, required=True, help='Output directory to save the model')
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f'Loading model {args.model} ...')
    m = SentenceTransformer(args.model)
    print(f'Saving model to {out} ...')
    m.save(str(out))
    print('Done.')

if __name__ == '__main__':
    main()
