import torch

def test_cuda():
    if torch.cuda.is_available():
        print("CUDA is available!")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs available: {torch.cuda.device_count()}")
        print(f"Current GPU: {torch.cuda.current_device()}")
        print(f"GPU name: {torch.cuda.get_device_name(torch.cuda.current_device())}")

        # Create a random tensor and move it to GPU
        x = torch.rand(3, 3)
        x = x.to('cuda')
        print("Tensor on GPU:", x)
    else:
        print("CUDA is not available!")


if __name__ == "__main__":
    test_cuda()
