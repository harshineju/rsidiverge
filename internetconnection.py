import urllib.request


def internet_on():
    try:
        print(urllib.request.urlopen('http://google.com', timeout=2))
        return True
    except:
        print("not connected to internet")
        return False

internet_on()