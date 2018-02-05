#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:00:36 2018

@author: jobi03
"""
#%%
from selenium import webdriver
from time import sleep
from timeit import default_timer
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium.webdriver.common.keys import Keys
#%% 
start = default_timer()
driver = webdriver.Chrome(executable_path="./chromedriver/chromedriver")
curWindowHndl = driver.current_window_handle
main_page = 'https://www.google.com.au/search?rlz=1C5CHFA_enAU773AU773&tbm=lcl&ei=3UdjWuLyEMKF8wW1qKqoDA&q=hair+salon+in+sydenham&oq=hair+salon+in+sydenham&gs_l=psy-ab.12...0.0.0.23053.0.0.0.0.0.0.0.0..0.0....0...1c..64.psy-ab..0.0.0....0.kIBjYREgQ90#rlfi=hd:;si:;mv:!1m3!1d9898.745892773277!2d151.16557966931157!3d-33.913372321572545!3m2!1i780!2i574!4f13.1'
#%% lists
salon_names = []
locations = []
ratings = []
reviewer_rate = []
reviews = []
meters = []
websites = []
schedules =  []
#%%make soup
def make_soup(page): 
    driver.get(page)
    sleep(2)
    html = driver.page_source
    soups = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
    return soups
#%%function for getting reviews
#def scrape_review():
def scrape_review(salon_name,location,rating,meter,schedule,website):
      
    main_info = driver.find_element_by_class_name('xpdopen')
    
    try:
        main_info.find_element_by_partial_link_text('More Google reviews').click()
        sleep(2)
        
        #how many reviews
        review_scores= driver.find_element_by_class_name('review-score-container')
        review_counter = review_scores.find_element_by_class_name('_yz')
        review_nums = review_counter.text.split(' ')
        review_num = int(review_nums[0])
        
        #if more review needs 
        if review_num > 10:
            driver.find_element_by_class_name('loris').click()
            sleep(1)
            driver.find_element_by_class_name('loris').click()
            sleep(1)
        
       
        d = driver.find_element_by_class_name('review-dialog-list')
        
        #rate of the reviewer
        for e in d.find_elements_by_class_name('_Rps'):
            f = e.find_element_by_tag_name('g-review-stars')
            g = f.get_attribute('innerHTML').split('"')
            reviewer_rate.append(g[3])
            
            
        for rows in d.find_elements_by_class_name('_ucl'):
            
            
            #review
            if rows.get_attribute('textContent') == '':
                reviews.append('No Review')
            else:
                try:
                    h = rows.find_element_by_class_name('review-full-text')
                    reviews.append(h.get_attribute('textContent'))
                except:
                    reviews.append(rows.get_attribute('textContent'))
            
            salon_names.append(salon_name)
            locations.append(location)
            ratings.append(rating)
            meters.append(meter)
            schedules.append(schedule)   
            websites.append(website)    
        
        driver.back()
            

    except:
        reviews.append('No Reviews')
        reviewer_rate.append('No Reviews')
        salon_names.append(salon_name)
        locations.append(location)
        ratings.append(rating)
        meters.append(meter)
        schedules.append(schedule) 
        websites.append(website)
        
    
    
#%%
def get_salons_info():
    
       
    schedule= ''
    a = driver.find_element_by_class_name('xpdopen')
    
    #name of salon   
    salon_name = a.find_element_by_class_name('_Q1n').text
    
    #website
    side = driver.find_element_by_class_name('_mdf')
    sides = side.find_elements_by_class_name('_ldf')
    if len(sides) == 2:
        web = sides[0].find_element_by_class_name('ab_button')
        website = (web.get_attribute('href'))
    else:
        website = 'No Websites'
        
    b = a.find_element_by_class_name('_RBg')
    
    for k in b.find_elements_by_class_name('mod'):
        try:
            l = k.find_element_by_class_name('_xdb')
            #address
            if l.text == 'Address:':
                location = k.find_element_by_class_name('_Xbe').text
            
            #schedule
            if l.text == 'Hours:':
                k.find_element_by_class_name('_vap').click()
                sleep(1)
                schedule = k.find_element_by_class_name('_Y0c').text
        except:
            pass
        
    if schedule == '':
        schedule = 'No Schedules'
    
    #ratings
    try:
        rating = a.find_element_by_class_name('rtng').text
    except:
        rating = 'No Ratings'
    
    #distance
    c = a.find_elements_by_class_name('_eMw')
    meter = (c[1].text)
    
    return salon_name,location,rating,meter,schedule,website
          
#%%
def scrape_results():
    for result in driver.find_elements_by_class_name('_iPk'):
        result.click()
        sleep(2)
        
        salon_name,location,rating,meter,schedule,website = get_salons_info() 
        
        scrape_review(salon_name,location,rating,meter,schedule,website)              
#%%
def save_to_csv():
    df = pd.DataFrame()
    df['Salon_Names'] = salon_names
    df['Address'] = locations
    df['Distance'] = meters
    df['Websites'] = websites
    df['Ratings'] = ratings
    df['Schedules'] = schedules
    df['Reviews'] = reviews
    df['Reviewers_Rate'] = reviewer_rate
    
    df.to_csv('Reviews.csv')

#%%Main

#Load result page
soup = make_soup(main_page)
sleep(2)
driver.refresh()
sleep(2)

scrape_results()

       
   

try:
    while driver.find_element_by_css_selector('#pnnext').is_displayed() == True:
        driver.find_element_by_css_selector('#pnnext').click()
        sleep(2)
        scrape_results()
except:
    #saving to csv file
    save_to_csv()

    
