import torch
from ultralytics import YOLO


def main():
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = YOLO('yolov9c.pt')          # load a pretrained model (recommended for training)

    try:
        # model.train(device=device, data='config.yaml', epochs=325, batch=-1)  # train the model
        model.train(device=device, data='config.yaml', epochs=100, batch = -1)
    except Exception as e:
        print("Error: ", str(e))
        raise


if __name__ == "__main__":
    main()
