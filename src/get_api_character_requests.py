import sys
from urllib import request
import requests
import asyncio
import concurrent.futures
import json

MAX_WORKERS = 50

def clean_string(x):
    return x.strip().strip('"').strip("'").lower()



if __name__ == "__main__":

    fileName = sys.argv[1]
    outputFile = sys.argv[2]
    token = sys.argv[3]

    headers = {'Authorization' : 'Bearer %s'%token}

    if fileName.startswith('tmp/eu'):
        zone = 'eu'
    else:
        zone = 'us'
        
    baseUrl = ('https://<zone>.api.blizzard.com/profile/wow/character/' + \
              '<server>/<name>?namespace=profile-<zone>&locale=en_US')\
              .replace('<zone>', zone)

    params = {'namespace': 'profile-%s'%zone,
              'locale': 'en_US'}
    
    def api_call(url):
        response = requests.get(url, headers=headers, params=params)
        return response.content
        
    with open(fileName, 'r') as f:
        data = f.readlines()

    urls = []
    for line in data:
        cleanName = clean_string(line.split(',')[0])
        cleanServer = clean_string(line.split(',')[1])
        name = request.quote(cleanName.encode('utf-8'))
        server = request.quote(cleanServer.encode('utf-8'))
        url = baseUrl.replace('<name>', name).replace('<server>', server)
        urls.append(url)

    # running asynchronous requests to avoid having run time increase linearly
    # with the number of requests
    # https://skipperkongen.dk/2016/09/09/easy-parallel-http-requests-with-python-and-asyncio
    async def main():
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    api_call,
                    url
                )
                for url in urls]

        return futures

    import time
    tic = time.time()
    loop = asyncio.get_event_loop()
    futures = loop.run_until_complete(main())
    charData = [k.result().decode('utf8') for k in futures]
    toc = time.time()

    print('Elapsed time: %.2f s'%(toc-tic))

    with open(outputFile, 'w') as f:
        json.dump(charData, f)
