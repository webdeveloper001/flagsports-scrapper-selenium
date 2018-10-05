import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
import json
import pandas as pd
import csv
from collections import defaultdict, namedtuple

from datetime import datetime


whole_data = []

WAIT_TIME = 40 
url = "https://www.flashscore.com/tennis/"

driver = webdriver.Chrome('./chromedriver')

driver.get(url)
print ("Opened")

WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='table-main']")))

print ("table-main loaded")

live_button = driver.find_element_by_xpath('//li[@class="ifmenu-live li1"]//a')
live_button.click()

print("live button click")

WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="table-main"]//table[@class="tennis"]')))

tournaments = driver.find_elements_by_xpath('//div[@class="table-main"]//table[@class="tennis"]')

for tournament in tournaments:
	tournament_name = tournament.find_element_by_xpath('.//thead//span[@class="name"]').text.strip()
	matchs = tournament.find_elements_by_xpath('.//td[contains(@class, "cell_ad time")]/..')

	for match in matchs:
		match.click()

		print "Opened Match"

		WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) == 2)
		driver.switch_to_window(driver.window_handles[1])
		WebDriverWait(driver, 10).until(lambda d: d.title != "")

		WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="summary-content"]//table')))

		player_names = driver.find_elements_by_xpath('//div[@class="tname__text"]/a')
		player1_name = player_names[0].text.strip()
		player2_name = player_names[1].text.strip()

		player_ranks = driver.find_elements_by_xpath('//span[@class="participant-detail-rank"]')
		player1_rank = player_ranks[0].text.strip()
		player2_rank = player_ranks[1].text.strip()

		odds = driver.find_elements_by_xpath('//span[contains(@class, "odds-wrap")]')
		player1_odd = odds[0].get_attribute('class').split('odds-wrap')[-1].strip() + ' ' + odds[0].text
		player2_odd = odds[1].get_attribute('class').split('odds-wrap')[-1].strip() + ' ' + odds[1].text

		pt_b_pt = driver.find_element_by_xpath('//a[@id="a-match-history"]')
		pt_b_pt.click()

		WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="match-history-content"]//div[@class="lines-bookmark"]')))

		sets = driver.find_elements_by_xpath('//div[@id="match-history-content"]//table[@class="parts-first"]')

		sets_handle = driver.find_elements_by_xpath('//div[@id="match-history-content"]//div[@class="lines-bookmark"]//a')

		general_score = ''
		detail = '{'
		first = True

		set_index = 0

		for each_set in sets:

			try:
				sets_handle[set_index].click()
			except:
				pass

			if set_index > 0:
				detail = detail + ","

			set_index = set_index + 1
			
			rounds = each_set.find_elements_by_xpath('.//tr[position()>1]')

			set_name = each_set.find_element_by_xpath('.//tr[1]').text.split('-')[-1].strip()

			detail = detail + '"' + set_name + '": {'

			general_score = general_score + '"' + set_name + '"'

			f_score = ''

			try:
				f_score = each_set.find_elements_by_xpath('.//td[contains(@class, "match-history-score")]')[-1].text
			except:
				pass

			general_score = general_score + ':"' + f_score + '"'

			for idx in range(0, len(rounds), 2):
				serves = rounds[idx].find_elements_by_xpath('.//td[@class="server"]')
				serve = 2
				try:
					serves[0].find_element_by_xpath('.//div[@class="icon-box"]')
					serve = 1
				except:
					serve = 2

				if serve == 1:
					detail = detail + '"'+player1_name+'-'+ str(idx / 2) + '":'
				else:
					detail = detail + '"'+player2_name+'-'+ str(idx / 2) + '":'

				try:
					detail = detail + '"'+rounds[idx+1].find_element_by_xpath('./td').text.strip()+'"'
				except:
					continue

				if idx + 2 != len(rounds):
					detail = detail + ","

			detail = detail + "}"

		detail = detail + "}"

		res = {
			"tournament_name": tournament_name,
			"player1_name": player1_name,
			"player2_name": player2_name, 
			"pre_match_odd": player1_odd + ' - ' + player2_odd,
			"general_score": general_score,
			"detail": detail
		}

		print (res)

		whole_data.append(res)

		driver.close()

		driver.switch_to_window(driver.window_handles[0])


driver.close()
driver.quit()


with open('out-'+datetime.now().strftime("%Y-%m-%d_%H:%M:%S")+'.csv', mode='w') as csv_file:
    fieldnames = ["tournament_name", "player1_name", "player2_name", "pre_match_odd", "general_score", "detail"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in whole_data:
	    writer.writerow(row)

