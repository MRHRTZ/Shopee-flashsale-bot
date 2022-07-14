import time
from lib.moduleChecker import checkModules, readFileJson, clearConsole

if __name__ == '__main__':
    clearConsole()
    config = readFileJson('./config/index.json')
    print('[ 🏁 ] Checking module packages...\n')
    time.sleep(1)
    for i in config['modules']:
        time.sleep(0.2)
        checkModules(i)
    clearConsole()
    from lib.definitions import initProgram, checkChromeDriver, menu
    checkChromeDriver()
    initProgram()
    menu()
