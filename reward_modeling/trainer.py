import torch
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data
from torch.utils.tensorboard import SummaryWriter

from reward_modeling.models.choice import Choice


class Trainer:
    def __init__(self, reward_model, learning_rate=1e-3, summary_writing_interval=100, batch_size=16):
        self.choice_model = Choice(reward_model)
        self.optimizer = optim.Adam(self.choice_model.parameters(), lr=learning_rate)
        self.criterion = F.binary_cross_entropy
        self.batch_size = batch_size
        self.writer = SummaryWriter()
        self.writing_interval = summary_writing_interval

    def train(self, preference_dataset, epochs=1):
        # TODO: Set sensible batch size value, possibly as param
        train_loader = torch.utils.data.DataLoader(dataset=preference_dataset, batch_size=self.batch_size)

        running_loss = 0.
        for epoch in range(epochs):

            for i, data in enumerate(train_loader, 0):
                queries, choices = data

                self.optimizer.zero_grad()

                choice_predictions = self.choice_model(queries).double()
                loss = self.criterion(choice_predictions, choices)

                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()

                if self._is_writing_iteration(i):
                    iteration = self._calculate_iteration(epoch, i, train_loader)
                    self.write_summary(running_loss, iteration)
                    running_loss = 0.0

    def _is_writing_iteration(self, i):
        return i % self.writing_interval == self.writing_interval - 1

    @staticmethod
    def _calculate_iteration(epoch, i, train_loader):
        return epoch * len(train_loader) + i

    def write_summary(self, running_loss, iteration):
        self.writer.add_scalar('training loss',
                               running_loss / self.writing_interval,
                               iteration)
