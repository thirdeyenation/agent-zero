import tensorflow as tf
import tf_agents
from tf_agents.environments import suite_gym
from tf_agents.agents.dqn import dqn_agent
from tf_agents.networks import q_network
from tf_agents.utils import common

# Create the environment
env = suite_gym.load('CartPole-v0')

# Create the Q-network
q_net = q_network.QNetwork(
    env.observation_spec(),
    env.action_spec(),
    fc_layer_params=(100, 50),
)

# Create the agent
optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
agent = dqn_agent.DqnAgent(
    env.time_step_spec(),
    env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=tf.Variable(0)
)
agent.initialize()
