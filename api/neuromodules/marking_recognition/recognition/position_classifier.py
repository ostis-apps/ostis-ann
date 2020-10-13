import torch
import torch.nn.functional as F


class FastClassifier(torch.nn.Module):
    def __init__(self):
        """
        In the constructor we instantiate two nn.Linear modules and assign them as
        member variables.
        """
        super(FastClassifier, self).__init__()
        self.conv1 = torch.nn.Conv2d(1, 8, 5, stride=5)
        self.pool1 = torch.nn.MaxPool2d(2)
        self.conv2 = torch.nn.Conv2d(8, 16, 5)
        self.pool2 = torch.nn.MaxPool2d(2)
        self.conv3 = torch.nn.Conv2d(16, 32, 5)
        self.linear1 = torch.nn.Linear(9*9*32, 128)
        self.linear2 = torch.nn.Linear(128, 4)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = F.relu(self.conv2(x))
        x = self.pool2(x)
        x = self.conv3(x)
        x = x.view(-1, 9*9*32)
        x = F.relu(self.linear1(x))
        x = F.dropout(x)
        x = F.log_softmax(self.linear2(x), dim=1)
        return x