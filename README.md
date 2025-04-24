# TraPy - 基于SUMO和Gym的车辆导航与交通控制仿真环境

## 项目简介

TraPy 是一个基于强化学习的车辆导航与交通控制仿真环境，采用 [SUMO](https://sumo.dlr.de/) 进行城市交通仿真，结合 [Gymnasium](https://gymnasium.farama.org/) 提供的强化学习框架，旨在为交通流优化和路径选择提供一个标准化的实验平台。用户可以在这个环境中训练智能体，以解决城市交通中常见的问题，例如减少交通拥堵、提高路径选择效率、优化交通灯控制等。

## 功能特性

- **多场景仿真支持**：支持基于 SUMO 的各种交通仿真场景，包括复杂城市交通网络和不同的交通控制策略。
- **强化学习支持**：通过 Gymnasium 接口，能够使用强化学习算法（如 DQN、PPO 等）进行智能体训练。
- **交通流优化**：通过强化学习优化交通流、路径选择以及交通灯控制等。
- **灵活的配置**：支持通过配置文件自定义仿真场景、网络结构和智能体训练参数。

## 安装依赖

该项目需要一些外部依赖库。以下是安装步骤：

###  安装 SUMO

SUMO 是开源的交通仿真软件，安装方法请参考 [SUMO 官方文档](https://sumo.dlr.de/docs/Installing/index.html)。

对于 Linux 系统，通常可以通过以下命令安装：

```bash
sudo apt-get install sumo sumo-tools sumo-doc
```

### 安装 Python 依赖

```
pip install gymnasium
```

## 环境配置

### 1. SUMO 配置文件

`cfg_file`：包含SUMO仿真配置的文件路径，例如 `resources/demo.sumocfg`。

`net_file`：定义交通网络的文件路径，例如 `resources/demo.net.xml`。

这些文件定义了仿真环境中的交通网络、交通信号灯控制策略、路径规划策略等。

### 2. 环境参数

- `total_step`：仿真总步数，默认为 86400（一天的仿真）。
- `begin_step`：仿真开始步数，默认为 0。
- `end_step`：仿真结束步数，默认为 86400。

可以根据需要调整这些参数，以便适应不同规模和时长的仿真任务。

## 环境初始化

使用以下代码初始化仿真环境：

```
import gymnasium as gym

env = gym.make("SUMO-GUI", cfg_file="resources/demo.sumocfg", 
               net_file="resources/demo.net.xml", render_mode="back", 
               total_step=86400, begin_step=0, end_step=86400)
```

- `cfg_file`：SUMO 配置文件路径。
- `net_file`：交通网络文件路径。
- `render_mode`：渲染模式（例如 "back" 用于后端渲染）。
- `total_step`：仿真总步数。
- `begin_step`：仿真起始步数。
- `end_step`：仿真结束步数。

## 环境操作

### `reset()`

重置环境并返回初始状态。

```
state, info = env.reset()
```

- **返回值**：
  - `state`：当前的观测数据（邻接矩阵或其他状态信息）。
  - `info`：包含交通网络信息的字典。

### `step(action)`

根据给定的 `action` 执行一步仿真，并返回下一个状态。

```
obs, reward, terminated, truncated, info = env.step(action)
```

- **输入**：
  - `action`：一个整数，表示所选的动作（在可选的边缘索引范围内）。
- **返回值**：
  - `obs`：当前的观测数据（邻接矩阵或其他状态信息）。
  - `reward`：根据当前状态计算的奖励。
  - `terminated`：表示是否达到终止条件（例如达到仿真时间上限）。
  - `truncated`：表示是否达到步数限制。
  - `info`：包含当前仿真信息，如当前边缘、目标边缘、节点信息等。

### `close()`

关闭环境并结束仿真。

```
env.close()
```

## 使用示例

以下是一个完整的使用示例，展示了如何创建仿真环境、执行仿真以及记录每步的结果：

```
import gymnasium as gym

# 创建环境
env = gym.make("SUMO-GUI", cfg_file="resources/demo.sumocfg", 
               net_file="resources/demo.net.xml", render_mode="back", 
               total_step=86400, begin_step=0, end_step=86400)

cnt_list = []
for i in range(1000):
    state, info = env.reset()
    terminated, truncated = False, False
    action_space = spaces.Discrete(info["Edges_Num"])  # 获取可行动作的空间大小
    print(f"_______________________________{i}_____________________________________________________")
    cnt = 0
    while not (terminated or truncated):
        action = action_space.sample()  # 随机选择一个动作
        obs, rwd, terminated, truncated, info = env.step(action)  # 执行动作
        cnt += 1
    cnt_list.append(cnt)
    print(max(cnt_list))  # 打印最大步骤数
```
