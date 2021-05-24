import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms


IMAGE_TRANSFORMS  = transforms.Compose([
    transforms.Resize((256, 256)), 
    transforms.ToTensor()
])

class Classifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = nn.MaxPool2d(3, 3)

        self.conv1 = nn.Conv2d(3, 6, 3)        
        self.conv2 = nn.Conv2d(6, 6, 3)
        self.conv3 = nn.Conv2d(6, 12, 3)
        self.conv4 = nn.Conv2d(12, 12, 3)

        self.fc1 = nn.Linear(48, 24)
        self.fc2 = nn.Linear(24, 2)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = self.pool(F.relu(self.conv4(x)))

        x = torch.flatten(x, 1)

        x = F.relu(self.fc1(x))
        x = self.fc2(x)

        return x
