from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import json


def create_webdriver_instance():
    
    firefox_options = webdriver.FirefoxOptions()
    #firefox_profile.set_preference("general.useragent.override", f"{fu}")
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("media.peerconnection.enabled", False)
    
    driver = webdriver.Firefox(r"C:\Users\808944\Desktop\parser\Main", options=firefox_options) #путь к geckodriver.exe для firefox 
    return driver


def twitter_search(driver, search_term):
    url = 'https://twitter.com/search'
    driver.get(url)
    driver.maximize_window()
    sleep(10)

    search_input = driver.find_element(By.XPATH,'//input[@data-testid="SearchBox_Search_Input"]')
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    
    sleep(10)
    return True


def change_page_sort(tab_name, driver):
    sleep(10)
    tab_click = driver.find_element(by=By.LINK_TEXT, value=tab_name).click()
    return tab_click


def generate_tweet_id(tweet):
    return ''.join(tweet)


def scroll_down_page(driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def save_tweet_data_to_json(tweet_data, filepath, mode='a+'):
    
    with open(filepath, mode=mode,encoding='utf-8') as f:
        if mode == 'w':
            pass
        
        if tweet_data:
            header = {'User' : f"{tweet_data[0]}", 
              'Handle' : f"{tweet_data[1]}", 
              'PostDate' : f"{tweet_data[2]}", 
              'TweetText' : f"{tweet_data[3]}", 
              'ReplyCount' : f"{tweet_data[4]}", 
              'RetweetCount' : f"{tweet_data[5]}", 
              'LikeCount' : f"{tweet_data[6]}"
    }
            json.dump(header, f, indent=4, ensure_ascii=False)

def collect_all_tweets_from_current_view(driver, lookback_limit=25):
    page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(card):
    try:
        user = card.find_element(By.XPATH,'.//span').text
    except exceptions.NoSuchElementException:
        user = ""
    except exceptions.StaleElementReferenceException:
        return
    try:
        handle = card.find_element(By.XPATH,'.//span[contains(text(), "@")]').text
    except exceptions.NoSuchElementException:
        handle = ""
    try:
        postdate = card.find_element(By.XPATH,'.//time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        return
    try:
        _comment = card.find_element(By.XPATH,'.//div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        _comment = ""
    try:
        _responding = card.find_element(By.XPATH,'.//div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        _responding = ""
    tweet_text = _comment + _responding
    try:
        reply_count = card.find_element(By.XPATH,'.//div[@data-testid="reply"]').text
    except exceptions.NoSuchElementException:
        reply_count = ""
    try:
        retweet_count = card.find_element(By.XPATH,'.//div[@data-testid="retweet"]').text
    except exceptions.NoSuchElementException:
        retweet_count = ""
    try:
        like_count = card.find_element(By.XPATH,'.//div[@data-testid="like"]').text
    except exceptions.NoSuchElementException:
        like_count = ""

    tweet = (user, handle, postdate, tweet_text, reply_count, retweet_count, like_count)
    return tweet


def main(filepath):
    save_tweet_data_to_json(None, filepath, 'w')  
    last_position = None
    end_of_scroll_region = False
    unique_tweets = set()
    page_sort_list = ["Top", "Latest"]
    
    search_term = input("Введите слова для поиска: ")
    print()
    page_sort = page_sort_list[int(input("Выберите категорию Top(0) или Latest(1): "))]
    print()
    
    driver = create_webdriver_instance()
    twitter_search_page_term = twitter_search(driver, search_term)
    if not twitter_search_page_term:
        return

    change_page_sort(page_sort, driver)

    while not end_of_scroll_region:
        cards = collect_all_tweets_from_current_view(driver)
        for card in cards:
            try:
                tweet = extract_data_from_current_tweet_card(card)
            except exceptions.StaleElementReferenceException:
                continue
            if not tweet:
                continue
            tweet_id = generate_tweet_id(tweet)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet_id)
                save_tweet_data_to_json(tweet, filepath)
        last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
    driver.quit()


if __name__ == '__main__':
    path = r'C:\Users\808944\Desktop\parser\Main\tweet_data_file.json' #путь сохранения файла 
    
    main(path)