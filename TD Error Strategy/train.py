import torch
from agent import Agent
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import json
import time
import gym

env = gym.make('LunarLander-v2')
#env = gym.make('MountainCar-v0')
env.seed(0)

agent = Agent(state_size= env.observation_space.shape[0], action_size=env.action_space.n, seed=3)

n_episodes=10
max_t=200
eps_start=1.0
eps_end=0.01
eps_decay=0.9995
def dqn():
    
    scores = []                        # list containing scores from each episode
    scores_window = deque(maxlen=100)  # last 100 scores
    eps = eps_start                    # initialize epsilon
    max_score = 200.0
    for i_episode in range(1, n_episodes+1):
        #env.render()
        state = env.reset()
        # print(type(state))
        # quit()
        score = 0
        for t in range(max_t):
            
            action = agent.act(state, eps)
            next_state, reward, done, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)
            state = next_state
            score += reward
            
            if done:
                break
              
        scores_window.append(score)       
        scores.append(score)              
        eps = max(eps_end, eps_decay*eps)  # decrease epsilon
        #print("\nRewards: ",reward,"\n")
        print('\rEpisode {}\tAverage Score: {:.2f}'.format(
            i_episode, np.mean(scores_window)), end="")
        if i_episode % 100 == 0:
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(
                i_episode, np.mean(scores_window)))

        if np.mean(scores_window) >= max_score:
            max_score = np.mean(scores_window)
            print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(
                i_episode-100, np.mean(scores_window)))
            torch.save(agent.qnetwork_local.state_dict(), "checkpoint_td_"+str(agent.td_)+".pth")

    return scores

start_time = time.time()
scores = dqn()
end_time = time.time()

scores_dqn_np = np.array(scores)
np.savetxt("scores_td_"+str(agent.td_)+".txt", scores_dqn_np)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "Execution time: %d hours : %02d minutes : %02d seconds" % (hour, minutes, seconds)

n = end_time-start_time
train_time = convert(n)
print(train_time)

train_info_dictionary = {'algorithm': 'DQN_dual_mem', 'eps_start': eps_start, 'eps_end': eps_end,
                         'eps_decay': eps_decay, 'episodes': n_episodes, 'train_time': train_time,
                         'len1':agent.lenmem1, 'len3':agent.lenmem2, 'loss':agent.td_, 'pop counter': agent.counter}

train_info_file = open('info_td_'+str(agent.td_)+'.json', 'w')
json.dump(train_info_dictionary, train_info_file)
train_info_file.close()

def moving_average(a, n=100):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


scores_ma_dqn = moving_average(scores, n=100)

fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores_ma_dqn)), scores_ma_dqn)
plt.ylabel('Reward')
plt.xlabel('Episode')
plt.show()
