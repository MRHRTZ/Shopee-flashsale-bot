import json, traceback, time

from datetime import datetime
from colorama import Fore, Style
from seleniumwire import webdriver
from seleniumwire.utils import decode
from progress.spinner import MoonSpinner
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lib.moduleChecker import clearConsole

def executeScript(**params):
    process_indicator = 0
    url = params['url']
    session_path = './sessions/' + params['session']
    driverPath = params['chromedriver']
    platform = params['platform']
    variation = params['variation']

    chromeOpts = webdriver.ChromeOptions()
    # chromeOpts.add_argument('--headless')

    driver = webdriver.Chrome(driverPath, options=chromeOpts)
    driver.get(url)

    with open(session_path, 'r') as f:
        session = json.load(f)

    for cookie in session:
        if 'sameSite' in cookie:
            if cookie['sameSite'] == 'None' or 'unspecified':
                cookie['sameSite'] = 'Strict'
        driver.add_cookie(cookie)

    clearConsole()

    # Detect network
    request = driver.wait_for_request('/api/v4/item/get')
    item_details = json.loads(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')))
    
    # Check item
    if not item_details or 'data' not in item_details:
        print(Fore.RED + '\n\n\n  [ Item not found ]\n\n')
        return
    else:
        item_details = item_details['data']

    # Check stock
    if item_details['stock'] == 0:
        print(Fore.RED + '\n\n\n  [ Item is out of stock ]\n\n')
        return

    #  Check account
    while True:
        if process_indicator % 5000 == 0: driver.refresh()
        spinner = MoonSpinner(Fore.LIGHTYELLOW_EX + 'Loading page, if you stay here too long please refresh the page or stop to change session account')
        htmlsource = driver.page_source
        if 'navbar__username' in htmlsource:
            clearConsole()
            break
        else:
            spinner.next()
            process_indicator += 1

    # Check is flashsale
    if not item_details['flash_sale'] and not item_details['upcoming_flash_sale']:
        isbuy = input(Fore.YELLOW + '\n  This is not an item for flashsale, continue buy? [Y/n] ')
        if isbuy.lower() != 'y': return
    elif item_details['flash_sale']:
        if item_details['flash_sale']['stock'] == 0:
            print(Fore.RED + '\n  [ FlashSale item out of stock. ]\n')
            return
        else:
            print(Fore.BLUE + '\n  [ FlashSale already started. ]\n')
    elif item_details['upcoming_flash_sale']:
        item_name = item_details['name']
        shop_loc = item_details['shop_location'] 
        attributes = item_details['attributes']
        desc_attr = ''
        if attributes:
            for attr in attributes:
                attr_name = attr['name']
                attr_value = str(datetime.fromtimestamp(int(attr['value']))) if attr['is_timestamp'] else attr['value']
                desc_attr += f'\n{Fore.YELLOW}{attr_name}{Fore.WHITE}: {Fore.LIGHTRED_EX}{attr_value}'
        start_time = item_details['upcoming_flash_sale']['start_time']
        start_time = datetime.fromtimestamp(start_time)

        while True:
            now = datetime.today()
            raw_remain_time = start_time - now 
            remain_time = str(raw_remain_time).split('.', 2)[0]
            waiting_message = f'''
{Fore.GREEN}{item_name} {Fore.WHITE}[{Fore.YELLOW}{shop_loc}{Fore.WHITE}]

        {Fore.WHITE}Countdown: {Fore.BLUE}{remain_time}
{desc_attr}

{Fore.MAGENTA}Waiting For FlashSale.. 
            '''
            
            clearConsole()
            print(waiting_message)

            if raw_remain_time.total_seconds() <= 0:
                print(Fore.BLUE + '\n  [ FlashSale Started. ]\n')
                break
            else:
                time.sleep(0.2)

    # Checkout & Order (Premium Edition)
    try:
        #select all available types on web 
        for variant in variation:
            variant_selector = f'button.product-variation[aria-label="{variant}"]'
            wait_variant_btn = WebDriverWait(driver, 10)
            variant_button = wait_variant_btn.until(EC.element_to_be_clickable((By.CSS_SELECTOR, variant_selector)))
            variant_button.click()

        to_cart_active = 'button.btn.btn-solid-primary.btn--l' 
        to_cart_disable = 'button.btn.btn-solid-primary.btn--l.btn-solid-primary--disabled'
        checkout = 'button.shopee-button-solid.shopee-button-solid--primary'

        # Add to cart
        to_cart = driver.find_element(by=By.CSS_SELECTOR, value=to_cart_active)
        to_cart.click()
        print(Fore.LIGHTYELLOW_EX + '\n  [ Added to Cart ✔️ ]\n')

        if params['autoOrder']: pass

        # Wait for cart page
        driver.wait_for_request('/api/v4/cart/update')
        driver.execute_script('''var minichat = document.querySelector("#shopee-mini-chat-embedded"); minichat.parentNode.removeChild(minichat);''') # Ngahalangan
        checkout_wait = WebDriverWait(driver, 10)
        checkout_button = checkout_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, checkout)))
        checkout_button.click()
        print(Fore.BLUE + '\n  [ Success CheckOut, Order by manual quickly! ]\n')
    except:
        print(Fore.RED + '\n  [ we have an error, please open issue on github. ]\n')
        print(traceback.format_exc())
    
    input(f'\n  {Fore.GREEN}[ Press Anykey To Exit This Script ]{Fore.WHITE}')
    print(f'\n  Bye 👋' + Style.RESET_ALL)

        
def checkUrl(**params):   
    url = params['url']
    driverPath = params['chromedriver']
    platform = params['platform']

    try:
        chromeOpts = webdriver.ChromeOptions()
        chromeOpts.add_argument('--headless')

        driver = webdriver.Chrome(driverPath, options=chromeOpts)
        driver.get(url)

        # Detect network
        request = driver.wait_for_request('/api/v4/item/get')
        item_details = json.loads(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')))
        
        # Check item
        if not item_details or 'data' not in item_details:
            print(Fore.RED + '\n [ Item not found ]\n')
            return None
        else:
            item_details = item_details['data']

        return item_details
    except Exception as e:
        print(Fore.RED + 'Error:' + str(e) + Style.RESET_ALL)
        return None


