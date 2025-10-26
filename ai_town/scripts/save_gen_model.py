"""
在联网机器上下载并保存生成模型（transformers）到本地目录，便于拷贝到离线机器。

用法（Windows cmd.exe）：
  .venv\Scripts\activate
  pip install transformers bitsandbytes accelerate
  python ai_town\scripts\save_gen_model.py --model distilgpt2 --out D:\models\distilgpt2

脚本功能：
- 自动检测模型类型：encoder-decoder -> AutoModelForSeq2SeqLM，否则 AutoModelForCausalLM
- 支持从本地路径复制模型（离线机器把缓存目录拷贝到目标）
- 支持低内存加载选项：--low-cpu-mem-usage, --load-in-8bit, --device-map
- 支持 trust_remote_code、use_safetensors
- 支持 --safe-save：仅保存必要文件（保存 state_dict 而非全部分片），注意：8-bit/分片模型不支持 safe-save
- 保存后打印目标目录的文件列表与大小

注意：8-bit 加载需要安装 bitsandbytes，并通常配合 device_map='auto' 使用。safe-save 会把模型移动到 CPU 并保存单个 pytorch_model.bin（可能不如原生 save_pretrained 可分片/跨环境加载）。
"""
import argparse
from pathlib import Path
import os
import shutil
import math


def sizeof_fmt(num, suffix='B'):
    # human readable file size
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"


def print_dir_tree(path: Path):
    print(f"Saved files in: {path}")
    for root, _, files in os.walk(path):
        for f in files:
            fp = Path(root) / f
            try:
                size = fp.stat().st_size
                rel = fp.relative_to(path)
                print(f" - {rel} ({sizeof_fmt(size)})")
            except Exception:
                print(f" - {fp} (size unknown)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='distilgpt2', help='HuggingFace model name (e.g. distilgpt2 or google/flan-t5-small) or local path')
    parser.add_argument('--out', type=str, required=True, help='Output directory to save the model')
    parser.add_argument('--trust-remote-code', action='store_true', help='Pass trust_remote_code=True to from_pretrained (needed for some community models)')
    parser.add_argument('--low-cpu-mem-usage', action='store_true', help='Use low_cpu_mem_usage=True when loading model to reduce peak RAM')
    parser.add_argument('--use-safetensors', action='store_true', help='Try to use safetensors when downloading/saving if supported')
    parser.add_argument('--device', choices=['cpu', 'cuda', 'auto'], default='auto', help='Move model to device after loading (may increase memory usage).')
    parser.add_argument('--load-in-8bit', action='store_true', help='Load model in 8-bit using bitsandbytes (requires bitsandbytes installed)')
    parser.add_argument('--device-map', type=str, default='auto', help="Device map to pass to from_pretrained (e.g. 'auto' or 'cpu'). Use 'none' to skip")
    parser.add_argument('--safe-save', action='store_true', help='Save a compact single-file state_dict (pytorch_model.bin) + config + tokenizer. Not supported for 8-bit models.')
    parser.add_argument('--to-fp16', action='store_true', help='When doing safe-save, convert weights to fp16 to reduce size (may reduce fidelity).')
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    model_spec = args.model

    # 如果 model_spec 指向本地路径，直接复制（支持离线机器将已有缓存拷贝到目标）
    local_path = Path(model_spec)
    if local_path.exists():
        print(f'Detected local model path: {local_path}. Copying to {out} ...')
        try:
            if local_path.is_file():
                shutil.copy2(str(local_path), str(out))
            else:
                shutil.copytree(str(local_path), str(out), dirs_exist_ok=True)
            print('Copy complete.')
            print_dir_tree(out)
        except Exception as e:
            raise RuntimeError(f'Failed to copy local model: {e}')
        return

    print(f'Loading model config for {model_spec} ...')
    try:
        from transformers import AutoConfig, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
    except Exception as e:
        raise RuntimeError(f'transformers is required: {e}')

    try:
        cfg = AutoConfig.from_pretrained(model_spec, trust_remote_code=args.trust_remote_code)
    except Exception as e:
        raise RuntimeError(f'Failed to load model config for "{model_spec}". Check network or model name. Original error: {e}')

    is_seq2seq = getattr(cfg, 'is_encoder_decoder', False)
    print(f'Model config loaded. is_encoder_decoder={is_seq2seq}')

    print(f'Loading tokenizer for {model_spec} ...')
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_spec, trust_remote_code=args.trust_remote_code)
    except Exception as e:
        raise RuntimeError(f'Failed to load tokenizer for "{model_spec}". Original error: {e}')

    print(f'Preparing to load model weights for {model_spec} ...')
    load_kwargs = {}
    if args.low_cpu_mem_usage:
        load_kwargs['low_cpu_mem_usage'] = True
    if args.use_safetensors:
        load_kwargs['use_safetensors'] = True
    if args.trust_remote_code:
        load_kwargs['trust_remote_code'] = True

    # bitsandbytes / 8-bit
    if args.load_in_8bit:
        try:
            import bitsandbytes as bnb  # noqa: F401
        except Exception as e:
            raise RuntimeError(f'bitsandbytes is required for --load-in-8bit: {e}')
        load_kwargs['load_in_8bit'] = True
        # 推荐 device_map=auto when using 8-bit
        if args.device_map and args.device_map.lower() != 'none':
            load_kwargs['device_map'] = args.device_map
        else:
            load_kwargs['device_map'] = 'auto'

    # device_map non-8bit
    elif args.device_map and args.device_map.lower() != 'none':
        # if user explicitly provided device_map and not using 8-bit
        load_kwargs['device_map'] = args.device_map

    try:
        if is_seq2seq:
            model = AutoModelForSeq2SeqLM.from_pretrained(model_spec, **load_kwargs)
        else:
            model = AutoModelForCausalLM.from_pretrained(model_spec, **load_kwargs)
    except Exception as e:
        raise RuntimeError(f'Failed to load model weights for "{model_spec}". You may be offline or the model name is incorrect. Original error: {e}')

    # 如果用户请求 safe-save，但模型是 8-bit 或者使用分片/特殊构造，则拒绝
    if args.safe_save and args.load_in_8bit:
        raise RuntimeError('safe-save is not supported for models loaded in 8-bit (bitsandbytes). Disable --load-in-8bit or omit --safe-save.')

    # 尝试将模型移动到指定设备（仅在非 8-bit 且模型在 CPU 上时）
    if args.device != 'cpu' and not args.load_in_8bit:
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            if args.device == 'cuda' and not has_cuda:
                print('Warning: --device cuda specified but CUDA not available. Falling back to cpu.')
                target_device = 'cpu'
            elif args.device == 'auto':
                target_device = 'cuda' if has_cuda else 'cpu'
            else:
                target_device = 'cpu'
            if target_device == 'cuda':
                print('Moving model to CUDA ...')
                model.to('cuda')
            else:
                print('Using CPU for model.')
                model.to('cpu')
        except Exception as e:
            print(f'Warning: unable to move model to device: {e}. Continuing and saving model on disk.')

    # 保存：safe-save 与 默认 save_pretrained 两种方式
    print(f'Saving model and tokenizer to {out} ...')
    try:
        if args.safe_save:
            # 安全保存：保存 config + tokenizer + 单文件 state_dict (可选 fp16)
            try:
                import torch
            except Exception as e:
                raise RuntimeError(f'torch is required for safe-save: {e}')

            # 确保模型在 CPU
            try:
                model.to('cpu')
            except Exception:
                pass

            if args.to_fp16:
                try:
                    model.half()
                except Exception:
                    print('Warning: failed to convert model to fp16. Continuing with original dtype.')

            # 导出 state_dict
            state_dict = model.state_dict()
            target_file = out / 'pytorch_model.bin'
            torch.save(state_dict, target_file)
            # 保存 config/tokenizer
            try:
                cfg.save_pretrained(str(out))
            except Exception:
                # 如果 cfg 不是 Transformers Config 对象，忽略
                pass
            tokenizer.save_pretrained(str(out))
        else:
            # 默认保存（保留 transformers 的 save_pretrained 行为，包含可能的分片文件）
            model.save_pretrained(str(out))
            tokenizer.save_pretrained(str(out))
    except Exception as e:
        raise RuntimeError(f'Failed to save model/tokenizer to "{out}": {e}')

    # 打印目标目录文件列表与大小
    try:
        print_dir_tree(out)
    except Exception:
        pass

    print('Done.')


if __name__ == '__main__':
    main()
