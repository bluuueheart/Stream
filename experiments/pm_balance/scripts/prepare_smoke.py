#!/usr/bin/env python3
"""Fetch one official pre-chunked OVO clip with a bounded HTTP range request."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION_SHA = 'dc4a90daf26764dc8ab8b228ea4af864ba2ea50c2833ead8c9af6573f78ccf97'
CLIP_SHA = '3b4d65372c7229a8a3e911d3e61dc814f7c4545a1d270500973bcdc6fd53a724'
COMMIT = 'c34093f9a072d93f9e1c6b923446dfba71f4528e'


def fetch(url, digest, byte_range=None):
    headers = {'Range': byte_range} if byte_range else {}
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as response:
        if byte_range and (response.status != 206 or
                           response.headers.get('Content-Range', '').split('/')[0] !=
                           'bytes ' + byte_range.removeprefix('bytes=')):
            raise ValueError('Server did not honor the requested byte range')
        # A failed range request must never download the entire 10GB archive part.
        limit = 57464390 if byte_range else 20_000_000
        data = response.read(limit + 1)
    if len(data) > limit or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('Downloaded data failed size/hash validation')
    return data


def main():
    target = ROOT / 'data/smoke'
    target.mkdir(parents=True, exist_ok=True)
    annotations = fetch(
        f'https://raw.githubusercontent.com/JoeLeelyf/OVO-Bench/{COMMIT}/data/ovo_bench_new.json',
        ANNOTATION_SHA)
    selected = [x for x in json.loads(annotations) if x['id'] == 35]
    if len(selected) != 1 or selected[0]['realtime'] != 82:
        raise ValueError('Unexpected smoke annotation')
    clips = target / 'chunked_videos'
    clips.mkdir(exist_ok=True)
    clip = clips / '35.mp4'
    if not clip.exists() or hashlib.sha256(clip.read_bytes()).hexdigest() != CLIP_SHA:
        data = fetch(
            'https://huggingface.co/datasets/JoeLeelyf/OVO-Bench/resolve/main/'
            'chunked_videos.tar.partaa?download=true', CLIP_SHA,
            'bytes=1024-57465413')
        clip.write_bytes(data)
    (target / 'annotations.json').write_text(json.dumps(selected, indent=2) + '\n')
    print(f'Prepared one EPM question at {target}; runtime validation only.')


if __name__ == '__main__':
    main()
