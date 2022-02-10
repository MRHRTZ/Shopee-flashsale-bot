import importlib.util, sys, subprocess, json, os

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def readFileJson(file):
    f = open(file, 'r')
    data = json.loads(f.read())
    f.close()

    return data

def writeFileJson(obj, file):
    jsonObj = json.dumps(obj, indent = 4)
    
    with open("sample.json", "w") as outfile:
        outfile.write(jsonObj)

def checkModules(name):
    if name in sys.modules:
        print(f"{name!r} installed ✔️")
    elif (spec := importlib.util.find_spec(name)) is not None:
        # If you choose to perform the actual import ...
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        print(f"{name!r} installed ✔️")
    else:
        print(f"{name!r} not found, installing ⚠️")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


        
        