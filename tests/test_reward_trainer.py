import pytest
import torch

from reward_modeling.preference_dataset import PreferenceDataset
from reward_modeling.reward_model import RewardModel
from reward_modeling.reward_trainer import RewardTrainer


@pytest.fixture()
def preference_dataset(preference, env):
    preferences = [preference, preference, preference]
    return PreferenceDataset(preferences=preferences)


@pytest.fixture()
def reward_trainer(env):
    reward_model = RewardModel(env)
    return RewardTrainer(reward_model)


@pytest.mark.skip(reason="Behavior is currently not deterministic. See issue #26")
def test_training_has_effect_on_all_model_parameters(reward_trainer, preference_dataset):
    """
    Testing whether parameters change uses code from  / is based on
    https://github.com/suriyadeepan/torchtest/blob/66a2c8b669aa23601f64e208463e9449ffc135da/torchtest/torchtest.py#L106
    """

    # TODO: Clarify if the following modifications to torch have an effect on other tests
    torch.manual_seed(42)
    torch.set_deterministic(d=True)

    params = [param for param in reward_trainer.choice_model.named_parameters() if param[1].requires_grad]
    initial_params = [(name, param.clone()) for (name, param) in params]

    reward_trainer.train(preference_dataset)

    for (_, p0), (name, p1) in zip(initial_params, params):
        assert not torch.equal(p0, p1)
