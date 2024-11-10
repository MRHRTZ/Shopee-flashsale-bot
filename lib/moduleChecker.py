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
        try:
            module_version = sys.modules[name].__version__
            print(f"{name!r} installed ✔️ (version {module_version})")
        except AttributeError:
            print(f"{name!r} installed ✔️ (version unknown)")
    elif (spec := importlib.util.find_spec(name.split('==')[0])) is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name.split('==')[0]] = module
        spec.loader.exec_module(module)
        try:
            installed_version = module.__version__
            required_version = name.split('==')[1] if '==' in name else None
            if required_version and installed_version != required_version:
                print(f"{name.split('==')[0]!r} version mismatch ⚠️ (installed: {installed_version}, required: {required_version}), reinstalling")
                subprocess.check_call([sys.executable, "-m", "pip", "install", name])
            else:
                print(f"{name.split('==')[0]!r} installed ✔️ (version {installed_version})")
        except AttributeError:
            print(f"{name.split('==')[0]!r} installed ✔️ (version unknown)")
    else:
        print(f"{name!r} not found, installing ⚠️")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


        
        