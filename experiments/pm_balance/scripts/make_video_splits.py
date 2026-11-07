#!/usr/bin/env python3
"""Freeze a prediction-independent 60/20/20 internal-study video split."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('annotations', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--seed', default='pm-balance-v1')
    args = parser.parse_args()
    raw = args.annotations.read_bytes()
    records = json.loads(raw)
    videos = set()
    for item in records:
        video = item.get('video')
        if not isinstance(video, str) or not video.strip():
            raise ValueError('Every annotation must have a source video path')
        videos.add(video)
    assignments = {}
    for video in sorted(videos):
        digest = hashlib.sha256((args.seed + '\0' + video).encode()).digest()
        fraction = int.from_bytes(digest[:8], 'big') / 2**64
        assignments[video] = 'train' if fraction < .6 else 'dev' if fraction < .8 else 'test'
    payload = {
        'study': 'internal study using official OVO annotations; not an unseen benchmark test',
        'method': 'SHA256(seed + NUL + source video path), first 64 bits; thresholds 0.6/0.8',
        'seed': args.seed,
        'annotation_sha256': hashlib.sha256(raw).hexdigest(),
        'video_identity': 'annotation.video; aliases across different paths require a separate audit',
        'video_counts': dict(Counter(assignments.values())),
        'question_counts': dict(Counter(assignments[x['video']] for x in records)),
        'videos': assignments,
    }
    # Never overwrite a frozen split while rerunning an experiment.
    with args.output.open('x') as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    print(payload['video_counts'], payload['question_counts'])


if __name__ == '__main__':
    main()
