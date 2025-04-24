import gymnasium as gym
from gymnasium import spaces
gym.register("SUMO-GUI",entry_point="environment.env:NaviEnv")
env = gym.make("SUMO-GUI",cfg_file="resources/demo.sumocfg",
               net_file="resources/demo.net.xml",render_mode="back",
               total_step=86400,begin_step=0,end_step=86400)
# env = gym.make("SUMO-GUI",cfg_file="resources/demo.sumocfg",
#                net_file="resources/demo.net.xml",render_mode="back")




cnt_list = []
for i in range(1000):
    State , info = env.reset()
    terminated,truncated=False,False
    action_space= spaces.Discrete(info["Edges_Num"])
    print(f"_______________________________{i}_____________________________________________________")
    cnt=0
    while not ( terminated or truncated):
        action = action_space.sample()
        obs,rwd,terminated,truncated,info = env.step(action)
        # print(f"Edge    {info['Current_Edge']}        Target      {info['Target_Edge']}        reward    {rwd}       Edge_Num    {info['Edges_Num']}    Terminated  {terminated}    Truncated   {truncated}")
        cnt+=1
    cnt_list.append(cnt)
    print(max(cnt_list))


