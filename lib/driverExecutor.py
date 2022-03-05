import json, traceback

from selenium import webdriver
from colorama import Fore, Style
from progress.spinner import MoonSpinner

from lib.moduleChecker import clearConsole

def executeScript(**params):
    url = params['url']
    session_path = './sessions/' + params['session']
    driverPath = params['chromedriver']
    platform = params['platform']

    driver = webdriver.Chrome(driverPath, service_log_path=('/dev/null' if platform == 'Linux' else 'NUL'))
    driver.get(url)

    with open(session_path, 'r') as f:
        session = json.load(f)

    for cookie in session:
        if 'sameSite' in cookie:
            if cookie['sameSite'] == 'None' or 'unspecified':
                cookie['sameSite'] = 'Strict'
        driver.add_cookie(cookie)

    'btn btn-solid-primary btn--l btn-solid-primary--disabled rvHxix' # Buy button disabled

    'btn btn-solid-primary btn--l rvHxix' # Buy button active

    clearConsole()
    #  Check acc
    while True:
        spinner = MoonSpinner(Fore.LIGHTYELLOW_EX + 'Loading page, if you stay here too long please refresh the page or stop to change session account')
        htmlsource = driver.page_source
        if 'navbar__username' in htmlsource:
            break
        else:
            spinner.next()

    while True:
        spinner = MoonSpinner(Fore.GREEN + 'Waiting For FlashSale.. Please select all available types on web ')
        htmlsource = driver.page_source
        if 'berakhir dalam' in htmlsource or 'ends in' in htmlsource:
            print(Fore.BLUE + '\n\n\n  [ FlashSale Started. ]\n\n')
            break
        else:
            spinner.next()

    try:
        to_cart = driver.find_element_by_css_selector('button.btn.btn-solid-primary.btn--l.rvHxix')
        to_cart.click()
        print(Fore.LIGHTYELLOW_EX + '\n\n\n  [ added to cart ✔️ ]\n\n')


        # if params['autoCheckout']:
        while True:
            spinner = MoonSpinner(Fore.GREEN + 'Waiting For CheckOut Button ')
            htmlsource = driver.page_source
            if 'class="shopee-button-solid shopee-button-solid--primary"' in htmlsource:
                print(Fore.BLUE + '\n\n\n  [ Success CheckOut ✔️ ]\n\n')
                break
            else:
                spinner.next()

        tombol_checkout = driver.find_element_by_css_selector('button.shopee-button-solid.shopee-button-solid--primary')
        tombol_checkout.click()
    except:
        print(Fore.RED + '\n\n\n  [ we have an error, maybe the item has been sold out ]\n\n')
        print(traceback.format_exc())
    
    input(Fore.GREEN + '[ Press Anykey To Exit This Script ]' + Style.RESET_ALL)
    print(Fore.WHITE + '\n\nBye 👋' + Style.RESET_ALL)

        
    


