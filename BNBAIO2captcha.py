import requests
import time
import threading
import webbrowser
import random
from bs4 import BeautifulSoup as bs

current_version = '1.0.0'

proxies = []
apikey = None
site = None

active_threads = 0
captchas_sent = 0

"""
0 - Adidas
1 - Ruvilla
2 - Sneakersnstuff
3 - PalaceSB
4 - YeezySupply
"""

site_names = [
    'Adidas',
    'RuVilla',
    'Sneakersnstuff',
    'PalaceSB',
    'YeezySupply'
]

site_urls = [
    'http://www.adidas.com',
    'http://www.ruvilla.com',
    'http://www.sneakersnstuff.com',
    'http://www.palaceskateboards.com',
    'http://www.yeezysupply.com'
]

solver_urls = None

post_urls = None


def main():
    global solver_urls
    global post_urls
    global apikey
    global site


    print(
        """
  ____  _   _ ____ ___                 _       _
 |  _ \| \ | |  _ \__ \               | |     | |
 | |_) |  \| | |_) | ) |___ __ _ _ __ | |_ ___| |__   __ _
 |  _ <| . ` |  _ < / // __/ _` | '_ \| __/ __| '_ \ / _` |
 | |_) | |\  | |_) / /| (_| (_| | |_) | || (__| | | | (_| |
 |____/|_| \_|____/____\___\__,_| .__/ \__\___|_| |_|\__,_|
                                | |  Twitter - https://twitter.com/hunter_bdm
                                |_|  Github - https://github.com/hunterbdm
        """
    )

    check_updates()

    # Get 2captcha APIKEY
    try:
        apikey_file = open('apikey.txt')
        apikey = apikey_file.read()
        apikey_file.close()
    except:
        print('Unable to read apikey.txt')
        exit()

    print('Got APIKEY:', apikey)
    print('Balance:', get_balance(), '\n')

    # Get proxies
    try:
        proxy_file = open('proxies.txt')
        for proxy in proxy_file.read().splitlines():
            # No lines should have spaces, so remove all of them
            proxy = proxy.replace(' ', '')
            # Now that we removed extra spaces, if there is nothing remaining on that line, we wont add it to the list.
            if not proxy == '':
                proxies.append(proxy)
        proxy_file.close()
        print(len(proxies), 'proxies found.')
        print(proxies)
    except:
        print('Unable to read proxies.txt, continuing without proxies.')

    port = input('Enter BNB server port (At top of BNBAIO log): ')

    solver_urls = [
        'http://bnb.adidas.com:' + port + '/solve',
        'http://bnb.ruvilla.com:' + port + '/solve',
        'http://bnb.sneakersnstuff.com:' + port + '/solve',
        'http://bnb.palaceskateboards.com:' + port + '/solve',
        'http://bnb.yeezysupply.com:' + port + '/solve'
    ]

    post_urls = [
        'http://bnb.adidas.com:' + port + '/res',
        'http://bnb.ruvilla.com:' + port + '/res',
        'http://bnb.sneakersnstuff.com:' + port + '/res',
        'http://bnb.palaceskateboards.com:' + port + '/res',
        'http://bnb.yeezysupply.com:' + port + '/res'
    ]

    for i in range(0, len(site_names)):
        print(i, '-', site_names[i])
    x = int(input('Pick a site: '))
    site = x

    print('Captcha Solver URL:', solver_urls[x])

    x = int(input('How many captchas?: '))

    sitekey = get_sitekey()

    print('Got sitekey', sitekey)

    for i in range(0, int(x)):
        t = threading.Thread(target=get_token_from_2captcha, args=(sitekey,))
        t.daemon = True
        t.start()
        time.sleep(0.1)
    print('Requested ' + str(x) + ' captcha(s).')
    print('Will exit when all captcha solutions arrived.')
    while not active_threads == 0:
        print('-------------------------')
        print('Active Threads          -', active_threads)
        print('Captchas Sent to BNBAIO -', captchas_sent)
        time.sleep(5)

    print('-------------------------')
    print('Active Threads          -', active_threads)
    print('Captchas Sent to BNBAIO -', captchas_sent)


def check_updates():
    # Check if the current version is outdated
    try:
        response = requests.get('https://raw.githubusercontent.com/hunterbdm/BNBAIO2captcha/master/README.md')
    except:
        print('Unable to check for updates.')
        return

    # If for some reason I forget to add the version to readme I dont want it to fuck up
    if 'Latest Version' in response.text:
        # Grab first line in readme. Will look like this 'Latest Version: 1.0.0.0'
        latest = (response.text.split('\n')[0])
        # Will remove 'Latest Version: ' from string so we just have the version number
        latest = latest[(latest.index(':') + 2):]
        if not latest == current_version:
            print('You are not on the latest version.')
            print('Your version:', current_version)
            print('Latest version:', latest)
            x = input('Would you like to download the latest version? (Y/N) ').upper()
            while not x == 'Y' and not x == 'N':
                print('Invalid input.')
                x = input('Would you like to download the latest version? (Y/N) ').upper()
            if x == 'N':
                return
            print('You can find the latest version here https://github.com/hunterbdm/BNBAIO2captcha')
            webbrowser.open('https://github.com/hunterbdm/ANBAIO2captcha')
            exit()
        print('No updates currently available. Version:', current_version)
        return
    print('Unable to check for updates.')
    return


def get_balance():
    session = requests.Session()
    session.verify = False
    session.cookies.clear()

    while True:
        data = {
            'key': apikey,
            'action': 'getbalance',
            'json': 1,
        }
        response = session.get(url='http://2captcha.com/res.php', params=data)
        if "ERROR_WRONG_USER_KEY" in response.text or "ERROR_KEY_DOES_NOT_EXIST" in response.text:
            print('Incorrect APIKEY, exiting.')
            exit()

        try:
            json = response.json()
        except:
            time.sleep(3)
            continue

        if json['status'] == 1:
            balance = json['request']
            return balance


def get_token_from_2captcha(sitekey):
    """
    All credit here to https://twitter.com/solemartyr, just stole this from his script
    """
    global active_threads

    active_threads += 1

    session = requests.Session()
    session.verify = False
    session.cookies.clear()
    pageurl = site_urls[site]

    while True:
        data = {
            'key': apikey,
            'action': 'getbalance',
            'json': 1,
        }
        response = session.get(url='http://2captcha.com/res.php', params=data)
        if "ERROR_WRONG_USER_KEY" in response.text or "ERROR_KEY_DOES_NOT_EXIST" in response.text:
            print('Incorrect APIKEY, exiting.')
            exit()

        captchaid = None
        proceed = False
        while not proceed:
            data = {
                'key': apikey,
                'method': 'userrecaptcha',
                'googlekey': sitekey,
                'proxy': 'localhost',
                'proxytype': 'HTTP',
                'pageurl': pageurl,
                'json': 1
            }

            if not len(proxies) == 0:
                # We will just pick randomly from the list because it doesn't matter if we use one more than others.
                data['proxy'] = random.choice(proxies)

            response = session.post(url='http://2captcha.com/in.php', data=data)
            try:
                json = response.json()
            except:
                time.sleep(3)
                continue

            if json['status'] == 1:
                captchaid = json['request']
                proceed = True
            else:
                time.sleep(3)
        time.sleep(3)

        token = None
        proceed = False
        while not proceed:
            data = {
                'key': apikey,
                'action': 'get',
                'json': 1,
                'id': captchaid,
            }
            response = session.get(url='http://2captcha.com/res.php', params=data)
            json = response.json()
            if json['status'] == 1:
                token = json['request']
                proceed = True
            else:
                time.sleep(3)

        if token is not None:
            send_captcha(token, sitekey)
            return


def get_sitekey():
    try:
        session = requests.Session()
        session.verify = False
        session.cookies.clear()
        resp = session.get(solver_urls[site])
        soup = bs(resp.text, "html.parser")
        sitekey = soup.find("div", class_="g-recaptcha")["data-sitekey"]
        if sitekey is None:
            print('Unable to get sitekey, server may be down.')
            exit()
        return sitekey
    except:
        print('Unable to get sitekey, server may be down.')
        return None


def send_captcha(captcha_response, sitekey):
    global active_threads
    global captchas_sent

    try:
        session = requests.Session()
        session.verify = False
        session.cookies.clear()

        post_url = post_urls[site]

        data = {
            'res': captcha_response,
            'key': sitekey
        }
        resp = session.post(post_url, data=data)
        if resp.status_code is 200:
            active_threads -= 1
            captchas_sent += 1
            return
    except:
        print('Unable to send captcha, server may be down.')
        active_threads -= 1
        return None


if __name__ == "__main__":
    main()
