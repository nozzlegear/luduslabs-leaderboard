import sys
from urllib import request
import requests
import asyncio
import concurrent.futures
import json
import time

MAX_WORKERS = 10


def clean_string(x):
    return x.strip().strip('"').strip("'").lower()


    
if __name__ == "__main__":
    fileName = sys.argv[1]
    outputFile = sys.argv[2]
    zone = sys.argv[3]
    token = sys.argv[4]


    headers = {'Authorization' : 'Bearer %s'%token}
        
    baseUrl = ('https://<zone>.api.blizzard.com/profile/wow/character/' + \
              '<server>/<name>?namespace=profile-<zone>&locale=en_US')\
              .replace('<zone>', zone)

    params = {'namespace': 'profile-%s'%zone,
              'locale': 'en_US'}


    def api_call(url):
        for k in range(3):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=3)
                content = response.content
                break
            except:
                print('Failed: %s %i'%(url, k))

            content = b''
            
        return content
    

    with open(fileName, 'r', errors='replace', encoding='utf-8') as f:
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
    charData = [k.result().decode('utf-8') for k in futures]
    toc = time.time()

#    charData = [api_call(url).decode('utf-8') for url in urls]

    print('Elapsed time: %.2f s'%(toc-tic))

    with open(outputFile, 'w') as f:
        json.dump(charData, f)
