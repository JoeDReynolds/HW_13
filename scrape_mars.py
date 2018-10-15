#Dependencies
import time
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import json
import numpy as np
import pandas as pd
import pymongo

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.mars_db
#URLs of Sites to be scraped

def init_browser():
	executable_path = {'executable_path':'chromedriver.exe'}
	return Browser('chrome', **executable_path, headless=False)

def scrape():

	browser = init_browser()
	# Create Mars Data Dictionary to insert to MongoDB
	mars_data = {}

	news_url = 'https://mars.nasa.gov/news/'
	jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
	weather_url = 'https://twitter.com/marswxreport?lang=en'
	facts_url ='https://space-facts.com/mars/'
	usgs_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

	# Retrieve pages with the requests module

	news_response = requests.get(news_url)
	jpl_response = requests.get(jpl_url)
	weather_response = requests.get(weather_url)

	# Create BeautifulSoup objects; parse with 'html.parser'

	news_soup = bs(news_response.text, 'html.parser')
	weather_soup = bs(weather_response.text, 'html.parser')

	#Set Up Splinter Browser
	browser.visit(news_url)

	news_html = browser.html

	news_soup = bs(news_html, 'html.parser')

	news_title = news_soup.find('div', class_='content_title').text

	#Scrape Teaser Body
	news_p = news_soup.find('div', class_='rollover_description_inner').text

	browser.visit(jpl_url)

	#Click on Featured Image
	browser.visit(jpl_url)
	time.sleep(2)
	browser.click_link_by_partial_text('FULL IMAGE')
	time.sleep(2)
	browser.click_link_by_partial_text('more info')
	time.sleep(2)
	browser.click_link_by_partial_text('.jpg')

	#Save HTML of the page to variable

	html = browser.html

	#Use bs to save image url

	jpl_soup = bs(html, 'html.parser')
	featured_image_url = jpl_soup.find("img")["src"]

	import re
	mars_weather= weather_soup.find(string=re.compile("Sol"))

	tables = pd.read_html(facts_url)
	facts_df = tables[0]
	facts_df.to_html('facts.html')

	#Create List of Mars Hemisphers to iterate over and dictionary to save the results
	mars_hemis = ["Valles Marineris Hemisphere", "Cerberus Hemisphere", "Schiaparelli Hemisphere", "Syrtis Major Hemisphere"]
	hemisphere_image_urls = []

	browser.visit(usgs_url)

	hemisphere_image_urls = []
	for i in range (4):
		time.sleep(2)
		images = browser.find_by_tag('h3')
		images[i].click()
		html = browser.html
		soup = bs(html, 'html.parser')
		partial = soup.find("img", class_="wide-image")["src"]
		img_title = soup.find("h2",class_="title").text
		img_url = 'https://astrogeology.usgs.gov'+ partial
		hemi_data = {"title":img_title,"img_url":img_url}
		hemisphere_image_urls.append(hemi_data)
		browser.back()


	mars_data["news_title"] = news_title
	mars_data["summary"] = news_p
	mars_data["featured_image_url"] = featured_image_url
	mars_data["mars_weather"] = mars_weather
	mars_data["mars_table"] = facts_df
	mars_data['mars_hemis'] = hemisphere_image_urls
	return mars_data
