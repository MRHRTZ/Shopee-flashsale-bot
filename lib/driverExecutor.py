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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .utils import decode_network
from lib.moduleChecker import clearConsole

def select_variation(driver, item_details):
    #select all available types on web 
    try:
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
    except:
        pass

def pooling_item(driver, attempt):
    for request in driver.requests:
        if request.response:
            if '/api/v4/item/get?' in request.url:
                item_details = decode_network(request)
    if not item_details or 'data' not in item_details:
        print(Fore.YELLOW + f'  [ Check session failed ({attempt}), next check ... ]')
        attempt += 1
        return attempt, False
    else:
        print(Fore.LIGHTGREEN_EX + f'  [ Check session success ]')
        attempt += 1
        return attempt, item_details['data']

def executeScript(**params):
    clearConsole()
    print(Fore.WHITE + '  [ Initial chrome automation ... ]')

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
        
    # Check account
    print(Fore.YELLOW + '  [ Sign in process ... ]')
    print(Fore.LIGHTYELLOW_EX + '  [ Loading account ... ]')
    pool_account = 0
    pool_account_max = 20
    isLogin = False
    while not isLogin:
        pool_account += 1
        driver.refresh()
        time.sleep(10)
        if pool_account > pool_account_max:
            print(Fore.LIGHTRED_EX + f'  [ Failed Sign in ({pool_account}/{pool_account_max}), please change the session and don\'t logout shopee, exiting ... ]')
            return
        try:
            username = driver.find_element(by=By.CLASS_NAME, value='navbar__username')
            isLogin = True
            print(Fore.GREEN + f'  [ Success Sign in as {username.text} ]')
        except NoSuchElementException:
            print(Fore.LIGHTMAGENTA_EX + f'  [ Failed Sign in ({pool_account}/{pool_account_max}), please resolve recaptha, checking for 10s ... ]')
        except: print(Fore.RED + traceback.format_exc())

    # Detect network
    attempt, item_details = pooling_item(driver, 0)

    # Check item
    if not item_details:
        print(Fore.CYAN + '  [ Item not found, This can happen because login error, checking session ... ]')
        driver.refresh()
        request = driver.wait_for_request('/api/v4/item/get')
        item_details = decode_network(request)
        pool_attempt = 1
        while not item_details:
            time.sleep(10)
            pool_attempt, item_details = pooling_item(driver, pool_attempt)
            if item_details: break;

    # Check is flashsale
    if item_details['flash_sale']:
        if item_details['flash_sale']['stock'] == 0:
            print(Fore.RED + '  [ FlashSale item out of stock. ]')
            return
        print(Fore.BLUE + '  [ FlashSale already started. ]')
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
                desc_attr += f'{Fore.YELLOW}{attr_name}{Fore.WHITE}: {Fore.LIGHTRED_EX}{attr_value}'
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
                print(Fore.BLUE + '  [ FlashSale Started. ]')
                break
            else:
                time.sleep(0.2)
    else:
        # Check stock
        if item_details['stock'] == 0:
            print(Fore.RED + '  [ Item is out of stock ]')
            return
        isbuy = input(Fore.YELLOW + '  This is not an item for flashsale, continue buy? [Y/n] ')
        if isbuy.lower() != 'y': return
        select_variation(driver, item_details)

    # Checkout & Order
    try:
        to_cart_active = 'button.btn.btn-solid-primary.btn--l' 
        to_cart_disable = 'button.btn.btn-solid-primary.btn--l.btn-solid-primary--disabled'
        checkout = 'button.shopee-button-solid.shopee-button-solid--primary'

        # Add to cart
        to_cart = driver.find_element(by=By.CSS_SELECTOR, value=to_cart_active)
        to_cart.click()

        # is added to card
        checkout_check = driver.wait_for_request('/api/v4/cart/add_to_cart')
        checkout_data = decode_network(checkout_check) 
        if checkout_data['error']:
            err_msg = checkout_data['error_msg']
            print(Fore.LIGHTRED_EX + f'  [ {err_msg} ]')
            return
        else:
            print(Fore.LIGHTBLUE_EX + '  [ Added to Cart ✔️ ]')

        if params['autoOrder']: pass

        # Wait for cart page
        driver.wait_for_request('/api/v4/cart/update')
        driver.execute_script('''var minichat = document.querySelector("#shopee-mini-chat-embedded"); minichat.parentNode.removeChild(minichat);''') # Ngahalangan
        checkout_wait = WebDriverWait(driver, 1)
        checkout_button = checkout_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, checkout)))
        checkout_button.click()

        # is checkout
        checkout_check = driver.wait_for_request('/api/v4/cart/checkout')
        checkout_data = decode_network(checkout_check) 
        if checkout_data['error']:
            err_msg = checkout_data['error_message']
            print(Fore.LIGHTRED_EX + f'  [ {err_msg} ]')
            return
        else:
            print(Fore.BLUE + '  [ Success CheckOut, Order by manual quickly! ]')
    except:
        print(Fore.LIGHTRED_EX + '  [ we have an error, please open issue on github. ]\n')
        print(traceback.format_exc())
    
    input(f'  {Fore.GREEN}[ Press Anykey To Exit This Script ]{Fore.WHITE}')
    print(f'  Bye 👋' + Style.RESET_ALL)

