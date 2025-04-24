import os
import sys
import traci
import sumolib
import numpy as np
from sumolib.net import edge,node
from traci import edge
from typing import Optional
import gymnasium as gym
from gymnasium import spaces
# >python D:\sumo\tools\randomTrips.py -n demo.net.xml -r demo.rou.xml -b 0 -e 86400 --insertion-rate 20000
class NaviEnv(gym.Env):
    metadata = { "render_modes": ["GUI", "back"]}


    def __init__(self,cfg_file,net_file,render_mode,total_step: Optional[int]=86400,begin_step:Optional[int]=0,end_step:Optional[int]=86400):
        super(NaviEnv,self).__init__()

        self.accumulative_step_in_sumo=0
        if render_mode=="GUI":
            self.sumoBinary = "sumo-gui"
        else:
            self.sumoBinary = "sumo"
        self.traci_cmd = [self.sumoBinary,"-c", cfg_file, "-b",str(begin_step),"-e",str(end_step)]
        # self.traci_cmd = [self.sumoBinary, "-c", cfg_file]
        self.net = sumolib.net.readNet(net_file)
        self.junctions = self.net.getNodes()
        self.junctions_nums = len(self.junctions)
        self.edges = self.net.getEdges()
        # 待解决
        # numedges要用sumolib读，用traci读不正确
        self.edges_nums = len(self.edges)

        self.total_step_in_sumo=min(total_step,end_step-begin_step)

        self.action_space=spaces.Discrete(self.edges_nums)
        self.observation_space=spaces.Box(low=0,high=np.inf,shape=(self.edges_nums,self.edges_nums),dtype=np.float64)
        print("Success init")


    def _getEdgesAvgWaitingTime(self):
        waiting_time = []

        # 此处不可使用traci.edge.getEstimatePassTime
        for e in self.edges:
            theory_min_pass_time = min(int(e.getLength() / e.getSpeed()),self.total_step_in_sumo)

            # if traci.edge.getLastStepVehicleNumber(e.getID()) == 0:
            #     real_avg_pass_time = theory_min_pass_time
            # else:
            #     real_avg_pass_time = int(traci.edge.getWaitingTime(e.getID())/traci.edge.getLastStepVehicleNumber(e.getID()))
            real_avg_pass_time = theory_min_pass_time
            if traci.edge.getLastStepMeanSpeed(e.getID()) == 0:
                if traci.edge.getLastStepVehicleNumber(e.getID()) != 0:
                    real_avg_pass_time = min(int(traci.edge.getWaitingTime(e.getID())/traci.edge.getLastStepVehicleNumber(e.getID())),86400)
            waiting_time.append(max(real_avg_pass_time, theory_min_pass_time))
        return waiting_time

    def __getEdgeAvgWaitingTime(self,e):
        # theory_min_pass_time = int(e.getLength() / e.getSpeed())
        # if traci.edge.getLastStepMeanSpeed(e.getID()) == 0:
        #     real_avg_pass_time = int(e.getLength() / e.getSpeed())
        # else:
        #     real_avg_pass_time = int(e.getLength() / traci.edge.getLastStepMeanSpeed(e.getID()))
        # return max(real_avg_pass_time, theory_min_pass_time)
        theory_min_pass_time = min(int(e.getLength() / e.getSpeed()), self.total_step_in_sumo)
        real_avg_pass_time = theory_min_pass_time
        if traci.edge.getLastStepMeanSpeed(e.getID()) == 0:
            if traci.edge.getLastStepVehicleNumber(e.getID()) != 0:
                real_avg_pass_time = min(
                    int(traci.edge.getWaitingTime(e.getID()) / traci.edge.getLastStepVehicleNumber(e.getID())), 86400)
        return max(real_avg_pass_time, theory_min_pass_time)

    def _getEdgesVehicleNums(self):
        vehicle_nums=[]
        for e in self.edges:
            vehicle_nums.append(traci.edge.getLastStepVehicleNumber(e.getID()))
        return vehicle_nums

    def _getAdjMatrix(self):
        adj_M = np.zeros([self.edges_nums,self.edges_nums])
        for e in self.edges:
            e_index = self.edges.index(e)
            adj_list_per_edge = e.getOutgoing()
            for adj_e in adj_list_per_edge:
                adj_M[e_index][self.edges.index(adj_e)]=self.__getEdgeAvgWaitingTime(adj_e)
        return adj_M

    # 下面为action【NWSE】，已弃用
    # def __calculateTheta(self,vec):
    #     ref_vec=np.array([0,1])
    #     theta = np.arctan2(np.linalg.det([ref_vec, vec]), np.dot(ref_vec, vec))
    #     if -np.pi/4 <= theta < np.pi/4:
    #         return "N"
    #     if np.pi/4<= theta < np.pi*3/4:
    #         return "W"
    #     if (np.pi*3/4<= theta) or (-np.pi <= theta <-np.pi*3/4):
    #         return "S"
    #     return "E"

    # def _directionWrapper(self):
    #     to_node_coord_current = np.array(self._edge_current.getToNode().getCoord())
    #     # print(type(self._edge_current))
    #     direction={}
    #     for i in self._edge_current.getOutgoing():
    #         # print(type(i.getToNode()))
    #         tmp_vec=np.array(i.getToNode().getCoord()) - to_node_coord_current
    #         d = self.__calculateTheta(tmp_vec)
    #         direction[d] = i
    #     return direction

    # def _applyAction(self,action):
    #     assert action in self.action_space,f"the action{action} is not in action_Space"
    #
    #     direction = self._directionWrapper()
    #     assert direction is not None,f"The Direction is Null, check map your defined or the edge the agent arrived now"
    #
    #     consuming_time = int(self.waiting_time[self.edges.index(self._edge_current)])
    #     self.accumulative_step_in_sumo += consuming_time
    #
    #     while consuming_time > 0:
    #         self.traci_conn.simulationStep()
    #         consuming_time -= 1
    #
    #     try:
    #         if action == 0:
    #             self._edge_current = direction["N"]
    #         if action == 1:
    #             self._edge_current = direction["W"]
    #         if action == 2:
    #             self._edge_current = direction["S"]
    #         if action == 3:
    #             self._edge_current = direction["E"]
    #
    #     except:
    #         self._edge_current = direction[next(iter(direction))]

    def _applyAction(self,action):
        # 检查action取值是否在space内
        assert action in self.action_space,f"Action {action} is invalid"
        if self.edges[action] in self._edge_current.getOutgoing():
            self._edge_prev = self._edge_current
            consuming_time = int(self.waiting_time[self.edges.index(self._edge_current)])
            self.accumulative_step_in_sumo += consuming_time

            # 勿改
            while consuming_time > 0:
                self.traci_conn.simulationStep()
                consuming_time -= 1

            self._edge_current = self.edges[action]
            return False
        else:
            # print(f"Action {action} lead to a wrong edge")
            return True

    def _get_reward(self):
        if self._edge_prev is None:
            self._edge_prev = self._edge_current
        reward = 0
        distance_current =np.power( np.array(self._edge_current.getFromNode().getCoord())-np.array(self._edge_target.getFromNode().getCoord()),2).sum()**0.5
        distance_prev = np.power( np.array(self._edge_prev.getFromNode().getCoord())-np.array(self._edge_target.getFromNode().getCoord()),2).sum()**0.5
        distance_prev_current = np.power( np.array(self._edge_prev.getFromNode().getCoord())-np.array(self._edge_current.getFromNode().getCoord()),2).sum()**0.5
        if distance_current < distance_prev:
            DistR = 1
        else:
            DistR =- 1
        DCI = np.abs(distance_current-distance_prev)/self._edge_prev.getLength()
        CongeP = self.traci_conn.edge.getLastStepVehicleNumber(self._edge_current.getID())

        reward = -CongeP + DCI * DistR
        if self._edge_current in self._edge_path:
            reward -=5
        return reward

    def _judgeTruncated (self):
        if self.accumulative_step_in_sumo >= self.total_step_in_sumo:
            return True
        return False

    def _judgeTerminated(self):
        if self._edge_current == self._edge_target:
            return True
        return False

    def reset(self):

        self._edge_prev = None
        self.traci_conn = traci

        # 误改
        if traci.isLoaded():
            traci.close()

        self.traci_conn.start(self.traci_cmd)

        # 拉state
        self.waiting_time = self._getEdgesAvgWaitingTime()
        obs = self._getAdjMatrix()

        self._edge_current = np.random.choice(self.edges)
        self._edge_target = np.random.choice(self.edges)
        self._edge_path=[]
        while self._edge_current == self._edge_target:
            self._edge_current = np.random.choice(self.edges)
            self._edge_target = np.random.choice(self.edges)

        # 待解决
        return obs,   {"Edge_Info" : self.edges, "Junction_Info":self.junctions,"Current_Edge":self._edge_current,"Target_Edge":self._edge_target,"Edges_Num":self.edges_nums,"num":self._getEdgesVehicleNums()}

    def step(self, action):
        self._edge_path.append(self._edge_current)
        terminated = False
        truncated = False
        # 采取动作，推进仿真
        truncated = self._applyAction(action)

        # 拉新state
        self.waiting_time = self._getEdgesAvgWaitingTime()
        obs = self._getAdjMatrix()

        # 奖励计算
        reward = self._get_reward()

        # 判断边界条件/阶段条件
        terminated = terminated or self._judgeTerminated()
        truncated = truncated or self._judgeTruncated()

        if terminated:
            reward += 20
        if truncated:
            reward -= 100

        # 待解决
        return obs  ,   reward  ,   terminated  , truncated,    {"Edge_Info" : self.edges, "Junction_Info":self.junctions,"Current_Edge":self._edge_current,"Target_Edge":self._edge_target,"Edges_Num":self.edges_nums,"num":self._getEdgesVehicleNums()}

    def close(self):
        self.traci_conn.close()
