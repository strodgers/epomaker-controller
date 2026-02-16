from importlib.metadata import version, PackageNotFoundError

def retrieve_app_version():
    try:
        return version("EpomakerController")  
    except PackageNotFoundError:
        return "version number not found"
    

if __name__ == "__main__":
    print(retrieve_app_version())