"""
在联网机器上下载并保存生成模型（transformers）到本地目录，便于拷贝到离线机器。
用法（Windows cmd.exe）：
  .venv\Scripts\activate
  pip install transformers
  python ai_town\scripts\save_gen_model.py --model distilgpt2 --out D:\models\distilgpt2
"""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='distilgpt2', help='HuggingFace model name (e.g. distilgpt2)')
    parser.add_argument('--out', type=str, required=True, help='Output directory to save the model')
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f'Loading model {args.model} ...')
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained(args.model)
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    print(f'Saving model to {out} ...')
    model.save_pretrained(str(out))
    tokenizer.save_pretrained(str(out))
    print('Done.')


if __name__ == '__main__':
    main()
