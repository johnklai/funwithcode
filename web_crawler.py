from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from queue import Queue
import threading

def run(globalUrl):
    """
    Scrapes all of the links recursively from a given domain name.
    
    Arguments:
    
    globalUrl - the overall domain name (e.g. 'http://www.python.org')
    
    Returns a set of urls
    
    """
    
    
    #initialize stuff
    websites = Queue()
    visited_websites = set()
    numWorkers = 4
    idle = [True]*numWorkers
    
    lock = threading.Lock()
    condition = threading.Condition()
    
    def worker(ID):
        ### COMMENT(JKL): You can do:
        ### print "worker %s starting" % ID (no need for the parens)
        print("worker %s starting" % ID)
        
        while True: 
            
            ### COMMENT(JKL): You can use the 'with' statement in Python to avoid having to call lock.acquire()
            ### and lock.release():
            ### with lock:
            ###   if websites:
            ###     url = websites.get()
            ###   elif all(idle):
            ###     return
            ###   else:
            ###     condition.wait()
            ###     continue
            
            #check if there are any websites left to be processed, and get the top one if necessary
            lock.acquire()
            
            ### COMMENT(JKL): You can do:
            ###     if not website.empty(): (no need for the parens)
            if not(websites.empty()):
                url = websites.get()
                idle[ID] = False
                lock.release()
            
            elif all(idle): 
                
                #there are no more websites to process, and none of the other threads are adding links either
                lock.release()
                return
            else: 
                #wait for threads to finish running / more websites to appear
                with condition:
                    lock.release()
                    condition.wait()
                continue
            
            page = urlopen(url)
            soup = BeautifulSoup(page)
            
            links = []
            
            #process the links
            for link in soup.find_all('a'):
                
                ref = link.get('href')
                new_url = urljoin(url, ref)
                
                #check if it's an internal link
                if new_url.startswith(globalUrl):
                    
                    #add to the queue
                    links.append(new_url)
            
            
            for link in links:
                with lock:
                    if link not in visited_websites:
                        visited_websites.add(link)
                        websites.put(link)

            with lock:
                with condition: 
                    idle[ID] = True      
                    condition.notifyAll()     
                
                
    websites.put(globalUrl)
    visited_websites.add(globalUrl)
    
    threads = [threading.Thread(target=worker,args=(i,)) for i in range(numWorkers)]
    
    for thread in threads:
        thread.start()
        
    for thread in threads:
        thread.join()
    
    return visited_websites
    
if __name__ == '__main__':

    sites = run("http://www.python.org")
    print(len(sites))
    print(sites)
