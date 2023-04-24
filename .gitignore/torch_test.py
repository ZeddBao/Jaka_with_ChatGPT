import torch

print(torch.__version__)  # 显示版本
print("gpu", torch.cuda.is_available())
