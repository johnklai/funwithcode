from urllib.request import urlopen
from bs4 import BeautifulSoup
from queue import Queue
from multiprocessing.pool import ThreadPool
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
    
    def worker(ID):
        
        while True: 
            
            #check if there are any websites left to be processed, and get the top one if necessary
            with lock:
                if websites:
                
                    url = websites.get()
                    idle[ID] = False
                
                elif all(idle): 
                    #there are no more websites to process, and none of the other threads are adding links either
                    return
                
                else: 
                    #wait for threads to finish running / more websites to appear
                    continue
            
            page = urlopen(url)
            soup = BeautifulSoup(page)
            
            links = []
            
            #run code here
            
            with lock:
                for link in links:
                    if link not in visited_websites:
                        visited_websites.add(link)
                        websites.put(link)
                idle[ID] = True
                
    websites.put(globalUrl)
    
    ThreadPool(numWorkers).imap_unordered(worker, range(numWorkers))
    
    return visited_websites()
    
