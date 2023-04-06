import json, traceback, time
import inquirer

from datetime import datetime
from colorama import Fore, Style
from seleniumwire import webdriver
from seleniumwire.utils import decode
from progress.spinner import MoonSpinner
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as WebDriverWaitUI 
from selenium.common.exceptions import TimeoutException

from .utils import decode_network
from lib.moduleChecker import clearConsole

def select_variation(driver, item_details):
    #select all available types on web 
    variation = item_details['tier_variations']
    variation_selections = []
    if len(variation) > 0:
        for variant in variation:
            variant_name = variant['name']
            select_variant = []
            for i in range(len(variant['options'])):
                if not variant['summed_stocks'] or variant['summed_stocks'][i] > 0:
                    select_variant.append(variant['options'][i])
            list_variant = [
            inquirer.List(
                f'variant-{i}', message=variant_name, choices=select_variant)
            ]

            _prompt = inquirer.prompt(list_variant)
            selected_variant = _prompt[f'variant-{i}']
            variation_selections.append(selected_variant)

        for variant in variation_selections:
            variant_selector = f'button.product-variation[aria-label="{variant}"]'
            wait_variant_btn = WebDriverWait(driver, 10)
            variant_button = wait_variant_btn.until(EC.element_to_be_clickable((By.CSS_SELECTOR, variant_selector)))
            variant_button.click()
                
def executeScript(**params):
    clearConsole()
    print(Fore.YELLOW + '[ Initial chrome automation... ]\n\n')

    process_indicator = 0
    url = params['url']
    session_path = './sessions/' + params['session']
    driverPath = params['chromedriver']
    platform = params['platform']
    variation = params['variation']

    chromeOpts = webdriver.ChromeOptions()
    # chromeOpts.add_argument('--headless')
    chromeOpts.add_argument("--window-size=1280,720")

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
    print(Fore.YELLOW + '  [ Sign in process ... ]')

    # Check account
    try:
        print(Fore.LIGHTYELLOW_EX + '  [ Loading account ... ]\n')
        delay = 3
        waitAcc = WebDriverWaitUI(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'navbar__username')))
        print(Fore.GREEN + '  [ Success Sign in. ]\n')
    except TimeoutException:
        pass
    
    # Detect network
    request = driver.wait_for_request('/api/v4/item/get', 60)
    item_details = decode_network(request)
    for key, value in item_details.items():
        print(f'    {Fore.WHITE}{key}{Fore.RED}: {Fore.GREEN}:{value}')

    # Check item
    if not item_details or 'data' not in item_details:
        print(Fore.CYAN + '\n  [ Item not found, This can happen because login error, attempting second phase in 10 sec ... ]\n')
        driver.refresh()
        time.sleep(5)
        request = driver.wait_for_request('/api/v4/item/get')
        item_details = decode_network(request)
        for request in driver.requests:
            if request.response:
                if '/api/v4/item/get?' in request.url:
                    # print(
                    #     request.url,
                    #     request.response.status_code,
                    #     request.response.headers['Content-Type']
                    # )
                    item_details = decode_network(request)
        if not item_details or 'data' not in item_details:
            print(Fore.RED + '\n  [ Second phase failed! ]\n')
            return
        else:
            item_details = item_details['data']
    else:
        item_details = item_details['data']

    # Check is flashsale
    if 'flash_sale' not in item_details and 'upcoming_flash_sale' not in item_details:
        # Check stock
        if item_details['stock'] == 0:
            print(Fore.RED + '\n\n\n  [ Item is out of stock ]\n\n')
            return
        isbuy = input(Fore.YELLOW + '\n  This is not an item for flashsale, continue buy? [Y/n] ')
        if isbuy.lower() != 'y': return
        select_variation(driver, item_details)
    elif item_details['flash_sale']:
        if item_details['flash_sale']['stock'] == 0:
            print(Fore.RED + '\n  [ FlashSale item out of stock. ]\n')
            return
        print(Fore.BLUE + '\n  [ FlashSale already started. ]\n')
        select_variation(driver, item_details)
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

        select_variation(driver, item_details)

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
    # TODO: Resolve Captcha !!!!

    process_indicator = 0 
    url = params['url']
    driverPath = params['chromedriver']
    platform = params['platform']
    session_path = './sessions/' + params['session']

    try:
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

        # Check account
        while True:
            if process_indicator % 5000 == 0: driver.refresh()
            print(Fore.LIGHTYELLOW_EX + 'Loading page, if you stay here too long please refresh the page or stop to change session account')
            htmlsource = driver.page_source
            if 'navbar__username' in htmlsource:
                clearConsole()
                break
            else:
                time.sleep(0.5)
                clearConsole()
                process_indicator += 1

        # Detect network
        request = driver.wait_for_request('/api/v4/item/get')
        item_details = json.loads(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')))
        
        # Check item
        print(item_details)
        if not item_details or 'data' not in item_details:
            print(Fore.RED + '\n [ Item not found ]\n')
            return None
        else:
            item_details = item_details['data']

        return item_details
    except Exception as e:
        print(Fore.RED + 'Error:' + str(e) + Style.RESET_ALL)
        return None


