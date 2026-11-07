#!/usr/bin/env python3
"""Check the BF16 attention and vocabulary projection used by Qwen3-VL-8B."""
import torch
from flash_attn import flash_attn_func


def main():
    print(f'torch={torch.__version__}, CUDA={torch.version.cuda}', flush=True)
    print(f'GPU={torch.cuda.get_device_name(0)}', flush=True)
    with torch.inference_mode():
        x = torch.randn(1, 32, 4, 128, device='cuda', dtype=torch.bfloat16)
        y = flash_attn_func(x, x, x)
        torch.cuda.synchronize()
        assert torch.isfinite(y).all()
        print('FlashAttention BF16: PASS', flush=True)
        del x, y
        # Reproduces a CUDA 12.1 vocabulary-projection SIGFPE on this H20.
        projection = torch.nn.Linear(4096, 151936, bias=False,
                                     device='cuda', dtype=torch.bfloat16)
        x = torch.zeros(1, 1, 4096, device='cuda', dtype=torch.bfloat16)
        y = projection(x)
        torch.cuda.synchronize()
        assert y.shape == (1, 1, 151936) and torch.count_nonzero(y) == 0
        print('Qwen BF16 vocabulary projection: PASS', flush=True)


if __name__ == '__main__':
    main()
