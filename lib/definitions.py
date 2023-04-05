import collections
import xml.etree.ElementTree as xml
import time
import inquirer
import json
import os
import platform
import wget

from requests import get, post
from colorama import Fore, Style
from zipfile import ZipFile
from lib.driverExecutor import executeScript, checkUrl

def initProgram():
    clearConsole()
    settings = readFileJson('./config/index.json')
    title = headerOutput(autoCheckout=settings['autoCheckout'], autoOrder=settings['autoOrder'], chromedriver=settings['chromedriver'],
                         session=settings['session'], urlTarget=settings['url'], options=settings['options'], justTitle=False)
    print(title)

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def readDir(path):
    return os.listdir(path)

def readFileJson(file):
    f = open(file, 'r')
    data = json.loads(f.read())
    f.close()

    return data

def writeFileJson(obj, file):
    jsonObj = json.dumps(obj, indent=4)

    with open(file, "w") as outfile:
        outfile.write(jsonObj)


def headerOutput(autoCheckout, autoOrder, chromedriver, session, urlTarget, options=[], justTitle=True):
    string = f'''
{Fore.LIGHTBLACK_EX}==========================================================
#              {Fore.RED}Shopee Fs Bot {Fore.LIGHTBLACK_EX}- {Fore.WHITE}By MRHRTZ                 {Fore.LIGHTBLACK_EX}#
# ====================================================== #
'''
    if not justTitle:
        string += f'''
{Fore.GREEN}Platform        :{Style.RESET_ALL} {(Fore.BLUE + platform.system() + Style.RESET_ALL)}
{Fore.GREEN}Session Name    :{Style.RESET_ALL} {(Fore.BLUE + session + Style.RESET_ALL) if session not in [None, ''] else (Fore.YELLOW + '[Select Session Account]' + Style.RESET_ALL)}
{Fore.GREEN}Shopee Item Url :{Style.RESET_ALL} {(Fore.BLUE + urlTarget + Style.RESET_ALL) if urlTarget not in [None, ''] else (Fore.YELLOW + '[Insert Flashsale Shopee URL]' + Style.RESET_ALL)}
{Fore.GREEN}Chromedriver    :{Style.RESET_ALL} {(Fore.BLUE + chromedriver + Style.RESET_ALL) if chromedriver not in [None, ''] else (Fore.YELLOW + '[Select Chromedriver]' + Style.RESET_ALL)}
{Fore.GREEN}Auto Checkout   :{Style.RESET_ALL} {'✔️' if autoCheckout else '❌'}
{Fore.GREEN}Auto Order      :{Style.RESET_ALL} {'✔️' if autoOrder else '❌'} {Fore.LIGHTRED_EX}[This Feature Will Added Soon]
'''
        if len(options) != 0:
            string += f'{Fore.LIGHTBLACK_EX}# ===================== [ Options ] ==================== #\n'
            for i in range(len(options)):
                string += f'''
{Fore.GREEN + options[i][0]} :{Style.RESET_ALL} {(Fore.BLUE + options[i][1] + Style.RESET_ALL) if options[i][1] not in [None, ''] else (Fore.YELLOW + '-' + Style.RESET_ALL)}'''

    return string


def getWebdriverList(webdriver = 'chrome'):
    if webdriver == 'chrome':
        chromeDriverUrl = 'https://chromedriver.storage.googleapis.com/'
        fetchChromeDriver = get(chromeDriverUrl).text
        webdriverListXml = xml.fromstring(fetchChromeDriver)
        webdriverList = {}
        for i in range(4, len(webdriverListXml)):
            for content in webdriverListXml[i]:
                if '/chrome' in content.text: 
                    driverKey = content.text.split('/')[1]
                    driverVersion = content.text.split('/')[0]
                    driverUrl = chromeDriverUrl + content.text 
                    if 'win' in driverKey:
                        if driverVersion in webdriverList:
                            webdriverList[driverVersion]['Windows'] = driverUrl
                        else:
                            webdriverList[driverVersion] = {}
                            webdriverList[driverVersion]['Windows'] = driverUrl
                    elif 'linux' in driverKey:
                        if driverVersion in webdriverList:
                            webdriverList[driverVersion]['Linux'] = driverUrl
                        else:
                            webdriverList[driverVersion] = {}
                            webdriverList[driverVersion]['Linux'] = driverUrl
                    elif 'mac64.' in driverKey:
                        if driverVersion in webdriverList:
                            webdriverList[driverVersion]['Darwin'] = driverUrl
                        else:
                            webdriverList[driverVersion] = {}
                            webdriverList[driverVersion]['Darwin'] = driverUrl
                    elif 'mac64_m1' in driverKey:
                        if driverVersion in webdriverList:
                            webdriverList[driverVersion]['Darwin_m1'] = driverUrl
                        else:
                            webdriverList[driverVersion] = {}
                            webdriverList[driverVersion]['Darwin_m1'] = driverUrl
        webdriverList = collections.OrderedDict(sorted(webdriverList.items()))
        writeFileJson(webdriverList, './webdriver/chromedriver.json')
        return webdriverList
    if webdriver == 'firefox':
        return ['firefox']
    if webdriver =='safari':
        return ['safari']
    if webdriver == 'ie':
        return ['ie']


def checkChromeDriver():
    settings = readFileJson('./config/index.json')
    chromeDriver = settings['chromedriver']
    chromeDir = readDir('./webdriver')
    _platform = platform.system()

    print('[🏁] Checking ChromeDriver...\n')
    time.sleep(1)
    print(f'{Fore.BLUE}Your platform is {_platform}')

    if chromeDriver.split('/')[-1] in chromeDir:
        print(f"{Fore.WHITE}{chromeDriver!r} installed ✔️")
        time.sleep(1)
    else:
        print(
            f'{Style.RESET_ALL}Chromedriver is not detected, {Fore.YELLOW}Installing.. ⚠️\n')
        versions = getWebdriverList()
        select_version = [inquirer.List(
            'version', message='Select chromedriver version based on your chrome app installed.', choices=[version for version in versions])]
        answers = inquirer.prompt(select_version)

        print('\n{0}Downloading ChromeDriver {1} v{2}{3}\n'.format(
            Fore.BLUE, _platform, answers['version'], Fore.LIGHTRED_EX))

        driverURL = readFileJson('./webdriver/chromedriver.json')
        driverURL = driverURL[answers['version']][_platform]
        zipName = driverURL.split('/')[-1]

        zipPath = './webdriver/' + zipName
        wget.download(driverURL, out=zipPath)

        with ZipFile(zipPath, 'r') as zip_ref:
            zip_ref.extractall(path='webdriver/',)

        os.remove(zipPath)

        print(Fore.WHITE + '\nInstalled ✔️')

        if _platform == 'Windows':
            platform_ext = '.exe'
        else:
            platform_ext = ''

        settings['chromedriver'] = './webdriver/chromedriver' + platform_ext

        writeFileJson(settings, './config/index.json')

def menu():
    initProgram()

    selector = [
        '1. START COUNTDOWN',
        '2. OPTIONS',
        '3. RESET',
        '4. EXIT'

    ]
    list_menu = [
        inquirer.List(
            'main', message='Welcome to FS Bot, Select one..', choices=selector)
    ]

    _menu = inquirer.prompt(list_menu)
    choice = _menu['main']

    if '1' in choice:
        start_countdown()
    elif '2' in choice:
        menu_options()
    elif '3' in choice:
        reset_settings()
    elif '4' in choice:
        print(Fore.WHITE + 'See ya 👋' + Style.RESET_ALL)

def menu_options():
    initProgram()

    selector = [
        '2.1 Select session',
        '2.2 Set Shopee Flashsale URL',
        '2.3 Back To Menu'
    ]
    list_opt = [
        inquirer.List('opt', message='Options', choices=selector)
    ]

    _opt = inquirer.prompt(list_opt)
    choice = _opt['opt']

    if '2.1' in choice:
        select_session()
    elif '2.2' in choice:
        set_url()
    elif '2.3' in choice:
        menu()

def reset_settings():
    answer = inquirer.prompt(
        [inquirer.Confirm('check', message='Are you sure to reset settings?')])
    settings = readFileJson('./config/index.json')

    if answer['check']:
        settings['session'] = ''
        settings['url'] = ''
        writeFileJson(settings, './config/index.json')
        menu()
    else:
        menu()

def set_url():
    settings = readFileJson('./config/index.json')
    settings['platform'] = platform.system()

    URL = [inquirer.Text('url', message='Insert Shopee Flashsale URL')]
    answer = inquirer.prompt(URL)['url']
    settings['url'] = answer
    print(f'\n{Fore.LIGHTYELLOW_EX}Checking url ...\n')
    item_detail = checkUrl(**settings)
    if item_detail:
        variation = item_detail['tier_variations']
        print(variation)
        sel_variation_list = []
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
                sel_variation_list.append(selected_variant)
        settings['variation'] = sel_variation_list
        variation_str = f' {Fore.RED}| {Fore.WHITE}'.join(sel_variation_list)
        print(f'{Fore.GREEN}Saving{Fore.WHITE}: {Fore.BLUE}{item_detail["name"]}\n{Fore.WHITE}{variation_str}')
        time.sleep(3)
        writeFileJson(settings, './config/index.json')
        menu()
    else:
        print(f'{Fore.RED}Invalid URL!\n')
        set_url()

def select_session():
    session = readDir('./sessions')
    settings = readFileJson('./config/index.json')
    settings['platform'] = platform.system()

    session_selector = []
    for i in session:
        if '.json' in i:
            session_selector.append(i)

    if len(session_selector) == 0:
        clearConsole()
        print(Fore.LIGHTRED_EX +
              '[ There is no account session, see README.md for steps to add session ]\n\n')
        input(Fore.GREEN + '[Back]' + Style.RESET_ALL)
        menu()
    else:
        list_session = [
            inquirer.List(
                'session', message='Select your account session', choices=session_selector)
        ]

        _session = inquirer.prompt(list_session)
        choice = _session['session']

        settings['session'] = choice
        writeFileJson(settings, './config/index.json')

        menu()

def start_countdown():
    settings = readFileJson('./config/index.json')
    settings['platform'] = platform.system()

    if not settings['session']:
        clearConsole()
        print(Fore.LIGHTRED_EX +
              '[ There is no account session, see README.md for steps to add session ]\n\n')
        input(Fore.GREEN + '[ Back ]' + Style.RESET_ALL)
        menu()
    elif not settings['url']:
        clearConsole()
        print(Fore.LIGHTRED_EX +
              '[ Please Insert Shopee Flashsale Item URL ]\n\n')
        input(Fore.GREEN + '[ Back ]' + Style.RESET_ALL)
        menu()
    else:
        clearConsole()
        print(Fore.YELLOW + '[ Initial chrome automation... ]\n\n')
        executeScript(**settings)


# print(headerOutput(chromedriver='', session='', urlTarget='', options=[], justTitle=False))
