"""
清理 ai_town/data 目录中未被 manifest 引用的文件。

用法（在项目根并激活 venv 下运行）：
  python ai_town\scripts\clean_data_dir.py [--delete]

行为：
- 读取 ai_town/data/index_manifest.json，收集所有被引用的文件名（vectors、index_safe、index_original、index）；
- 列出 data 目录中所有文件；
- 对未被引用的文件，默认将其移动到 ai_town/data/backup_<timestamp> 目录（即备份而非删除）；
- 如果传入 --delete，则在创建备份后永久删除这些未引用文件（备份仍保留）；
- 打印操作摘要，便于你确认。

注：脚本只在 ai_town/data 下操作，不会触及其他路径。建议先运行不带 --delete 的默认模式，确认备份内容再决定是否永久删除。
"""
from pathlib import Path
import json
import argparse
import shutil
import datetime

DATA_DIR = Path(__file__).resolve().parents[2] / 'ai_town' / 'data'
MANIFEST = DATA_DIR / 'index_manifest.json'


def main():
    parser = argparse.ArgumentParser(description='Clean unreferenced files in ai_town/data')
    parser.add_argument('--delete', action='store_true', help='Permanently delete unreferenced files after backing up')
    args = parser.parse_args()

    if not DATA_DIR.exists():
        print(f'DATA_DIR not found: {DATA_DIR}')
        return

    if not MANIFEST.exists():
        print(f'Manifest not found: {MANIFEST}. Nothing to reference; aborting.')
        return

    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))

    # 收集被引用的文件名
    referenced = set()
    for k, v in manifest.items():
        for key in ('vectors', 'index_safe', 'index_original', 'index'):
            val = v.get(key)
            if val:
                referenced.add(val)

    # Always keep manifest itself
    referenced.add(MANIFEST.name)

    # 列出 data 目录文件
    all_files = [p for p in DATA_DIR.iterdir() if p.is_file()]

    unreferenced = [p for p in all_files if p.name not in referenced]

    if not unreferenced:
        print('No unreferenced files found in', DATA_DIR)
        return

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = DATA_DIR / f'backup_{ts}'
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(f'Found {len(unreferenced)} unreferenced file(s). Moving to backup: {backup_dir}')
    for p in unreferenced:
        try:
            shutil.move(str(p), str(backup_dir / p.name))
            print('Moved:', p.name)
        except Exception as e:
            print('Failed to move', p.name, ':', e)

    if args.delete:
        print('\n--delete specified: permanently removing files in backup directory...')
        for p in backup_dir.iterdir():
            try:
                p.unlink()
                print('Deleted:', p.name)
            except Exception as e:
                print('Failed to delete', p.name, ':', e)
        print('Deletion completed. Backup directory remains (may be empty):', backup_dir)
    else:
        print('\nBackup completed. To permanently delete these files, re-run with --delete.')


if __name__ == '__main__':
    main()
