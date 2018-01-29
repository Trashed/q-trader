from agent.agent import Agent
from functions import *
import sys
import requests
import json

if len(sys.argv) != 4:
	print "Usage: python train.py [stock] [window] [episodes]"
	exit()

stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

# Get bitcoin price in dollars
resp = requests.get(url="https://api.coinmarketcap.com/v1/ticker/bitcoin/")
data = json.loads(resp.text)
btcToUsd = float(data[0]['price_usd'])

agent = Agent(window_size)
data = getStockDataVec(stock_name)
l = len(data) - 1
batch_size = 32

for e in xrange(episode_count + 1):
	print "Episode " + str(e) + "/" + str(episode_count)
	state = getState(data, 0, window_size + 1)

	print "state " + str(state)

	total_profit = 0
	agent.inventory = []

	for t in xrange(l):
		action = agent.act(state)

		# sit
		next_state = getState(data, t + 1, window_size + 1)
		reward = 0

		if action == 1: # buy
			agent.inventory.append(data[t] * btcToUsd)
			print "Buy: " + formatPrice(data[t] * btcToUsd)

		elif action == 2 and len(agent.inventory) > 0: # sell
			bought_price = agent.inventory.pop(0)
			current_price = data[t] * btcToUsd
			reward = max(current_price - bought_price, 0)
			total_profit += current_price - bought_price
			print "Sell: " + formatPrice(current_price) + " | Profit: " + formatPrice(current_price - bought_price)

		done = True if t == l - 1 else False
		agent.memory.append((state, action, reward, next_state, done))
		state = next_state

		if done:
			print "--------------------------------"
			print "Total Profit: " + formatPrice(total_profit)
			print "--------------------------------"

		if len(agent.memory) > batch_size:
			agent.expReplay(batch_size)

	if e % 10 == 0:
		agent.model.save("models/model_ep" + str(e))
