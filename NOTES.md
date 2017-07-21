AIMA
----


percept = Environment.percept(agent): lists things agent sees at location
program = Agent.program(percept): return string with action to take based on percept
Environment.execute_action(agent, action): do something, like agent.movedown

Environment.run -> self.step -> Agent.program(self.percept(agent)), self.execute_action -> Agent.someaction



Animat
------

Environment.step -> Agent.step -> Environment.takeAction (returns a reward)

Agent.step could be Agent.program? Should take percept as argument


A VirtualEnvironment has *one* Agent
VirtualEnvironment.createAgent -> VirutalEnvironment.createNetwork -> SensorNode(lambda t: VirtualEnvironment.readSensor(cell)) -> Network(conf, sensors, motors, objective)
VirtualEnvironment.readSensor -> VirtualEnvironment.currentCell -> self.world(self.agent.position)

VirtualEnvironment.readSensor could be AIMAEnvironment.percept()
VirtualEnvironment.currentCell could be AIMAEnvironment.list_things_at()

Agent.step():
  Network.tick()
  Check if sensors has changed
  endLearning()
  Get current cell
  action = Network.getBestAction(needs)
  prediction = Network.predictR(action)
  reward = Environment.takeAction(action)
  surprise = relative_surprise(prediction, reward)
  beginLearning(surprise, reward, action, prediction)
  updateNeeds(reward)

Agent.beginLearning(surprise, reward, action, prediction):
  Agent.updateSurpriseMatrix(surprise, reward, action, number of predictions)

Agent.updateSurpriseMatrix(surprise, reward, action, number of predictions):

Network.tick():
  increase time
  store sensors in previousSensors
  call Node.tick(time) for all sensors
  call Node.tick(time) for all top nodes

Node.tick(time):
  call Node.tick(time) for all inputs

SensorNode.tick(time):
  return true if seeing the block the sensor is configured for and set node to active, deactivate otherwise and return false


AndNode.tick(time):
  get active input nodes
  activate/deactivate node
  return boolean

NAndNode:


SEQNode:


  Node
   ^
   | inherits
   |
SensorNode


Necessary changes
=================

VirtualEnvironment.createAgent (and createNetwork) should be moved to Agent module (if a factory is needed at all)

Network.getBestAction in Agent.step should be replaced with Agent.program:
 - Agent.step must split into two steps, first action=Agent.program(Environment.percept) and then Environment.executeAction(agent, action)
 - now: score,action,Q = self.network.getBestAction(self.needs); reward = Environment.takeAction(self, action)

VirtualEnvironment.takeAction should be moved to Agent

VirtualEnvironment.readSensor should be replaced with percept

In Agent should sensors be used and not references to VirtualEnvironment





