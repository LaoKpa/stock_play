## Commonly used functions in my exercises

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy import stats


category_full_names = {'vbd':'very big drop', 'bd':'big drop', 'md':'medium drop', 'sd':'small drop',
                       'vbg':'very big gain', 'bg':'big gain', 'mg':'medium gain', 'sg':'small gain'}

def ticker_from_csv(csv_string):
	""" 
	The downloaded files come in the form [ticker].csv. 
	We are just stripping off the csv extension and making the ticker uppercase.
	"""
	stock_name = csv_string.rsplit('.', 1)[0] ## Peel off the ".csv" from the given string
	return stock_name.upper()

def get_price_movements(df, period=1):
	""" Get the movement of a stock that's in a data frame. """
	df = df.sort_index(axis=0) ## We want the dates in ascending order
	movement = np.zeros(int(len(df) / period)) ## Python's int function rounds down
	last_price = -1
	count = 0
	for index, row in df.iterrows():
		if (count % period == 0 and count != 0 ):
			i = int((count / period) - 1)
			movement[i] = 100 * row['close'] / last_price - 100
			last_price = row['close']
		elif (count == 0):
			last_price = row['close']
		count += 1

	return movement

def plot_gaussian(x, x_min=-10, x_max=10, n=10000, fill=False):
	"""
	Expects an np array of movement percentages, 
	plots the gaussian kernel density estimate
	"""

	## Learn the kernel-density estimate from the data
	density = stats.gaussian_kde(x)

	## Evaluate the output on some data points
	xs = np.linspace(x_min, x_max, n)
	y = density.evaluate(xs)

	## Create the plot
	plt.plot(xs, y)
	plt.xlabel('Daily Movement Percentage')
	plt.ylabel('Density')

	if (fill):
		plt.fill_between(xs, 0, y)

def plot_gaussian_categorical(x, x_min=-10, x_max=10, n=10000, title=''):
	"""
	Expects an np array of movement percentages, 
	plots the gaussian kernel density estimate
	"""
	## Learn the kernel-density estimate from the data
	density = stats.gaussian_kde(x)

	## Evaluate the output on some data points
	xs = np.linspace(x_min, x_max, n)
	y = density.evaluate(xs)

	## Create the plot
	plt.plot(xs, y)
	plt.xlabel('Movement Percentage')
	plt.ylabel('Density')

	## Get stats
	mu, sigma = np.mean(x), np.std(x)

	## Plot with conditionals
	plt.fill_between(xs, 0, y, where= xs < mu, facecolor='#eeeedd', interpolate=True) ## Small Drop
	plt.fill_between(xs, 0, y, where= xs < (mu - sigma / 2), facecolor='yellow', interpolate=True) ## Medium Drop
	plt.fill_between(xs, 0, y, where= xs < (mu - sigma), facecolor='orange', interpolate=True) ## Big Drop
	plt.fill_between(xs, 0, y, where= xs < (mu - 2*sigma), facecolor='red', interpolate=True) ## Very big drop

	plt.fill_between(xs, 0, y, where= xs > mu, facecolor='#ebfaeb', interpolate=True) ## Small Gain
	plt.fill_between(xs, 0, y, where= xs > (mu + sigma/2), facecolor='#b5fbb6', interpolate=True) ## Gain
	plt.fill_between(xs, 0, y, where= xs > (mu + sigma), facecolor='#6efa70', interpolate=True) ## Big Gain
	plt.fill_between(xs, 0, y, where= xs > (mu + 2*sigma), facecolor='green', interpolate=True) ## Very Big Gain

	## Label mu and sigma
	plt.text(x_min + 1, max(y) * 0.8, r'$\mu$ = ' + '{0:.2f}'.format(mu))
	plt.text(x_min + 1, max(y) * 0.9, r'$\sigma$ = ' + '{0:.2f}'.format(sigma))
	## Set title if given
	if (len(title) != 0):
		plt.title(title)

def categorize_movements(movements, n_cats=8):
	"""
	Given an array of movements, return an array of categories based on how relatively large the movements are.
	The default number of categories is 8.
	"""
	mu, sigma = np.mean(movements), np.std(movements)
	categories = []

	if (n_cats == 8):
		for i in range(len(movements)):
			if (movements[i] <= (mu - 2*sigma)):
				categories.append('vbd') ## very big drop
			elif (movements[i] <= (mu - sigma)):
				categories.append('bd')  ## big drop
			elif (movements[i] <= (mu - sigma/2)):
				categories.append('md')  ## medium drop
			elif (movements[i] < mu):
				categories.append('sd')  ## small drop
			elif (movements[i] >= (mu + 2*sigma)):
				categories.append('vbg') ## very big gain
			elif (movements[i] >= (mu + sigma)):
				categories.append('bg')  ## big gain
			elif (movements[i] >= (mu + sigma/2)):
				categories.append('mg')  ## medium gain
			elif (movements[i] >= mu):
				categories.append('sg')  ## small gain

	elif (n_cats == 4):
		for i in range(len(movements)):
			if (movements[i] <= (mu - sigma)):
				categories.append('bd')  ## big drop
			elif (movements[i] < mu):
				categories.append('sd')  ## small drop
			elif (movements[i] >= (mu + sigma)):
				categories.append('bg')  ## big gain
			elif (movements[i] >= mu):
				categories.append('sg')  ## small gain

	else:
		raise ValueError('Currently only 4 and 8 categories are supported')

	return categories

def count_movement_category(categories, cat_to_count):
	count = 0
	for i in range(len(categories)):
		if categories[i] == cat_to_count:
			count = count + 1
	return count

def count_two_day_trends(trends, trend_to_count):
	raise NameError('Renamed to count_trends')

def count_trends(trends, trend_to_count):
	count = 0
	for i in range(len(trends)):
		if trends[i] == trend_to_count:
			count = count + 1
	return count

def get_two_day_trends(categories):
	two_day_trends = []
	for i in range(len(categories) - 1):
		two_day_trends.append(categories[i] + '_' + categories[i+1])
	return two_day_trends

def get_three_day_trends(categories):
	three_day_trends = []
	for i in range(len(categories) - 2):
		three_day_trends.append(categories[i] + '_' + categories[i+1] + '_' + categories[i+2])
	return three_day_trends

def plot_two_day_probability_bar_graph(previous_day, count, two_day_trends, cat_probs, n_cats=8, show_baseline=True):
	two_day_probs = []
	if (n_cats == 8):
		all_categories = ['vbd', 'bd', 'md', 'sd', 'sg', 'mg', 'bg', 'vbg']
	elif(n_cats == 4):
		all_categories = ['bd', 'sd', 'sg', 'bg']
	for next_day in all_categories:
		two_day_name = previous_day +'_' + next_day
		two_day_count = count_trends(two_day_trends, two_day_name)
		two_day_prob = two_day_count / count
		two_day_probs.append(two_day_prob)

	plt.figure(figsize=(11,4))
	if (n_cats == 8):
		categories = ('Very Big Drop', 'Big Drop', 'Medium Drop', 'Small Drop', 'Small Gain', 'Medium Gain', 'Big Gain', 'Very Big Gain')
		ind = np.arange(8)
	elif (n_cats == 4):
		categories = ('Big Drop', 'Small Drop', 'Small Gain', 'Big Gain')
		ind = np.arange(4)
	width = 0.25

	if (show_baseline):
		orig_pl = plt.bar(ind+width, cat_probs, width, color='b', label='Original')
	conditioned_pl = plt.bar(ind, two_day_probs, width, color='r', label='After a ' + category_full_names[previous_day])

	plt.text(0.5, max(two_day_probs) * .95, 'n = ' + '{0:d}'.format(count), ha='center', va='center', weight='medium')

	plt.ylabel('Probabilities')
	plt.title('Probabilities of each Category')
	plt.xticks(ind+width, categories)
	plt.legend()
	#plt.show()

#######################
## Practice 10
#######################
def run_random_walks(starting_value, stride_length, p, n_steps, n_trials):
	"""
	Run 1D random walks with the following parameters:
	  starting_value -- Value on the number line at which to start the random walk
	  stride_length  -- Size of our steps in either direction
	  p              -- Probability of success
	  n_trials       -- Number of trials to run
	  n_steps        -- Number of steps to take on our random walk
	  
	NOTE: 0 will be an absorbing state. Meaning that if we hit 0 we're stuck there

	Returns the trial_results, which contains the results of each random walk
	"""
	trial_results = []

	for i in range(n_trials):
		values = []
		value = starting_value
		for j in range(n_steps):
			values.append(value)
			if (value <= 0):
				value = 0
			elif (random.random() < p):
				value += stride_length
			else:
				value -= stride_length
		trial_results.append(values)

	return trial_results

def run_random_walks_kelly(starting_value, p, n_steps, n_trials):
	"""
	Run 1D random walks with the following parameters:
	  starting_value -- Value on the number line at which to start the random walk
	  stride_length  -- Size of our steps in either direction
	  p              -- Probability of success
	  n_trials       -- Number of trials to run
	  n_steps        -- Number of steps to take on our random walk
	  
	NOTE: 0 will be an absorbing state. Meaning that if we hit 0 we're stuck there
	
	Returns the trial_results, which contains the results of each random walk
	"""
	trial_results = []

	for i in range(n_trials):
		values = []
		value = starting_value
		for j in range(n_steps):
			values.append(value)
			stride_length = int((2 * p - 1) * value) ## Kelly
			if (value <= 0):
				value = 0
			elif (random.random() < p):
				value += stride_length
			else:
				value -= stride_length
		trial_results.append(values)

	return trial_results

def run_gaussian_random_walks(starting_value, mu, sigma, n_steps, n_trials):
	"""
	Run 1D random gaussian walks with the following parameters:
	  starting_value -- Value on the number line at which to start the random walk
	  mu             -- Average percent value of stride length
	  sigma          -- Average percent standard deviation
	  n_trials       -- Number of trials to run
	  n_steps        -- Number of steps to take on our random walk
	  
	NOTE: 0 will be an absorbing state. Meaning that if we hit 0 we're stuck there
	
	Returns the trial_results, which contains the results of each random walk
	We are assuming no "edge" to tilt things in our favor
	"""
	trial_results = []

	for i in range(n_trials):
		step_multipliers = np.random.normal(mu, sigma, n_steps) / 100
		values = []
		value = starting_value
		for j in range(n_steps):
			values.append(value)
			if (value <= 0):
				value = 0
			value = value + step_multipliers[j] * value
		trial_results.append(values)

	step_multipliers
	return trial_results

def categorize_movement(movement, mu, sigma, n_cats=4):
	if not (n_cats == 4):
		raise ValueError('Only 4 categories supported at this time')

	if (movement <= (mu - sigma)):
		category = 'bd'  ## big drop
	elif (movement <= mu):
		category = 'sd'  ## small drop
	elif (movement >= (mu + sigma)):
		category = 'bg'  ## big gain
	elif (movement >= mu):
		category = 'sg'  ## small gain

	return category

def choose_category(labels, probabilities):
	num = np.random.rand(1)[0]
	for i in range(len(probabilities)):
		num = num - probabilities[i]
		if num <= 0:
			return labels[i]
		
	## Probabilities didn't sum perfectly to one
	return np.random.choice(labels, 1)[0]

def generate_next_two_day_step(previous_step, two_day_probs, mu, sigma):
	conditional_probabilities = {'bd':two_day_probs[0:4], 
								 'sd':two_day_probs[4:8],
								 'sg':two_day_probs[8:12],
								 'bg':two_day_probs[12:16]}
	conditional_probability = conditional_probabilities[categorize_movement(previous_step, mu, sigma)]
	
	choice = choose_category(['bd', 'sd', 'sg', 'bg'], conditional_probability)
	
	random_samples = np.random.normal(mu, sigma, 1000)
	
	## Draw on random samples until we get a result of the correct category
	for i in range(len(random_samples)):
		if (categorize_movement(random_samples[i], mu, sigma) == choice):
			#print(choice)
			#print(random_samples[i])
			return random_samples[i]
		
	## Very unlikely to happen, but will catch in the case none of the samples have the category we're looking for
	return 0

def get_probabilities(two_day_trends, categories, n_categories=4):
	two_day_probs = []
	if (n_categories == 4):
		all_categories = ['bd', 'sd', 'sg', 'bg']
	else:
		raise ValueError('Only four categories are supported at this time')
		
	for first_day in all_categories:
		first_day_count = count_movement_category(categories, first_day)
		for next_day in all_categories:
			two_day_name = first_day +'_' + next_day
			two_day_count = count_trends(two_day_trends, two_day_name)
			two_day_prob = two_day_count / first_day_count
			two_day_probs.append(two_day_prob)

	return two_day_probs

def run_two_day_momentum_simulation(prior_daily_movements, starting_value, mu, sigma, n_steps, n_trials):
	## Get categories and trends
	prior_movement_categories = categorize_movements(prior_daily_movements, n_cats=4)
	prior_two_day_trends = get_two_day_trends(prior_movement_categories)
	two_day_probs = get_probabilities(prior_two_day_trends, prior_movement_categories)
	
	trials = []
	for i in range(n_trials):
		first_step = generate_next_two_day_step(prior_daily_movements[-1], two_day_probs, mu, sigma)
		#print(first_step)
		steps = [first_step]

		for i in range(n_steps - 1):
			steps.append(generate_next_two_day_step(steps[i], two_day_probs, mu, sigma))
		
		trials.append(simulate_movements(steps, starting_value))

	return trials

def get_three_day_probabilities(three_day_trends, two_day_name, categories, n_categories=4):
	"""Returns the probability distribution for the third day given the previous two"""
	two_day_probs = []
	if (n_categories == 4):
		all_categories = ['bd', 'sd', 'sg', 'bg']
	else:
		raise ValueError('Only four categories are supported at this time')
		
	three_day_counts = []
	total = 0
	for next_day in all_categories:
		three_day_name = two_day_name + '_' + next_day
		three_day_count = count_trends(three_day_trends, three_day_name)
		total += three_day_count
		three_day_counts.append(three_day_count)

	three_day_probs = []
	[three_day_probs.append(three_day_counts[i] / total) for i in range(len(three_day_counts))]
	return three_day_probs

def generate_next_three_day_step(step_before_last, previous_step, three_day_probability, mu, sigma):
	two_day_name = categorize_movement(step_before_last, mu, sigma) + '_' + categorize_movement(previous_step, mu, sigma)
	choice = choose_category(['bd', 'sd', 'sg', 'bg'], three_day_probability)
	random_samples = np.random.normal(mu, sigma, 1000)
	
	## Draw on random samples until we get a result of the correct category
	for i in range(len(random_samples)):
		if (categorize_movement(random_samples[i], mu, sigma) == choice):
			return random_samples[i]
		
	## Very unlikely to happen, but will catch in the case none of the samples have the category we're looking for
	return 0

def run_three_day_momentum_simulation(prior_daily_movements, starting_value, mu, sigma, n_steps, n_trials):
	## Get categories and trends
	prior_movement_categories = categorize_movements(prior_daily_movements, n_cats=4)
	prior_three_day_trends = get_three_day_trends(prior_movement_categories)
	
	trials = []
	
	## Collect a dictionay of three day probabilities
	all_categories = ['bd', 'sd', 'sg', 'bg']
	three_day_probs = {}
	for first_day in all_categories:
		for next_day in all_categories:
			two_day_name = first_day + '_' + next_day
			three_day_probs[two_day_name] = get_three_day_probabilities(prior_three_day_trends, two_day_name, prior_movement_categories)
	
	## Generate steps based on the movements of the prior two days
	for i in range(n_trials):
		two_day_name = categorize_movement(prior_daily_movements[-2], mu, sigma) + '_' + categorize_movement(prior_daily_movements[-1], mu, sigma)
		three_day_prob = three_day_probs[two_day_name]
		first_step = generate_next_three_day_step(prior_daily_movements[-2], prior_daily_movements[-1], three_day_prob, mu, sigma)
		
		two_day_name = categorize_movement(prior_daily_movements[-2], mu, sigma) + '_' + categorize_movement(prior_daily_movements[-1], mu, sigma)
		three_day_prob = three_day_probs[two_day_name]
		second_step = generate_next_three_day_step(prior_daily_movements[-1], first_step, three_day_prob, mu, sigma)
		
		steps = [first_step, second_step]

		for i in range(n_steps - 2):
			two_day_name = categorize_movement(steps[i], mu, sigma) + '_' + categorize_movement(steps[i+1], mu, sigma)
			three_day_prob = three_day_probs[two_day_name]
			steps.append(generate_next_three_day_step(steps[i], steps[i+1], three_day_prob, mu, sigma))
		
		trials.append(simulate_movements(steps, starting_value))

	return trials

