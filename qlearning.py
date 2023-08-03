import random
import runner

class QBot(runner.HdxNode):
    def __init__(self, qnode, params):
        super().__init__('q_bot')
        self.qnode = qnode
        self.params = params
        self.q_table = QTable(qnode, params)
        self.loops = 0
        self.total_reward = 0
        self.action = 0
        self.create_timer(0.10, self.timer_callback)

    def timer_callback(self):
        if not self.qnode.action_in_progress():
            state = self.qnode.read_state()
            if state is not None:
                self.loops += 1
                reward = self.qnode.read_reward()
                self.total_reward += reward
                print(f"{self.loops}: s:{state} a:{self.action} r:{reward} ({self.total_reward})")
                self.action = self.q_table.sense_act_learn(state, reward)
                self.qnode.act(self.action)

    def add_self_recursive(self, executor):
        executor.add_node(self)
        self.qnode.add_self_recursive(executor)

    def print_status(self):
        print(f"Total updates: {self.loops}")
        print(f"Total reward:  {self.total_reward}")
        print(f"q-values: {self.q_table.q}")
        print(f"visits:   {self.q_table.visits}")
    

class QParameters:
    def __init__(self):
        self.target_visits = 1
        self.epsilon = 0.0
        self.discount = 0.5
        self.rate_constant = 10


class QTable:
    def __init__(self, qnode, params):
        self.q = [[0.0] * qnode.num_actions() for i in range(qnode.num_states())]
        self.visits = [[0] * qnode.num_actions() for i in range(qnode.num_states())]
        self.target_visits = params.target_visits
        self.epsilon = params.epsilon
        self.discount = params.discount
        self.rate_constant = params.rate_constant
        self.last_state = 0
        self.last_action = 0

    def sense_act_learn(self, new_state, reward):
        alpha = self.learning_rate(self.last_state, self.last_action)
        update = alpha * (self.discount * self.q[new_state][self.best_action(new_state)] + reward)
        self.q[self.last_state][self.last_action] *= 1.0 - alpha
        self.q[self.last_state][self.last_action] += update

        self.visits[self.last_state][self.last_action] += 1
        if self.is_exploring(new_state):
            new_action = self.least_visited_action(new_state)
        else:
            new_action = self.best_action(new_state)

        self.last_state = new_state
        self.last_action = new_action
        return new_action

    def learning_rate(self, state, action):
        return self.rate_constant / (self.rate_constant + self.visits[state][action])

    def best_action(self, state):
        best = 0
        for action in range(1, len(self.q[state])):
            if self.q[state][best] < self.q[state][action]:
                best = action
        return best

    def is_exploring(self, state):
        return min(self.visits[state]) < self.target_visits or random.random() < self.epsilon

    def least_visited_action(self, state):
        least_visited = 0
        for action in range(1, len(self.visits[state])):
            if self.visits[state][least_visited] > self.visits[state][action]:
                least_visited = action
        return least_visited

