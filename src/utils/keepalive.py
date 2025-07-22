import os
import time
import random
import requests
import threading
import logging
from datetime import datetime

class KeepAlive:
    def __init__(self, app_url=None):
        self.app_url = app_url or os.environ.get('RENDER_EXTERNAL_URL') or 'https://bankingsystem-0ybm.onrender.com/'
        self.endpoint = '/health'
        self.enabled = self._should_enable()
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
    def _should_enable(self):
        return (os.environ.get('RENDER') or 'onrender.com' in self.app_url) # ONLY RUN IN PROD MODE
    
    def start(self):
        if not self.enabled: 
            self.logger.info("kepe alive disabled | not in prod mode)"); 
            return
        if self.running: 
            self.logger.warning("| OK | keep alive alr RUNNING"); 
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"banking system keep_aliev started -- {self.app_url}")
    
    def stop(self):
        self.running = False
        if self.thread: 
            self.logger.info("| STOPPED | keep alive stopped")
    
    def _keep_alive_loop(self):
        while self.running:
            try:
                ping = requests.get(
                    f"{self.app_url}{self.endpoint}",
                    timeout=10,
                    headers={
                        'uAgent': 'banking-keepalive/1.0',
                        'xKeepAlive': 'true'
                    }
                )
                
                if ping.status_code == 200:
                    self.logger.info("| OK | banking system self ping successful")
                else:
                    self.logger.warning(f"| WARNING | ping returned {ping.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"| X | banking sys self ping failed: {e}")
            except Exception as e:
                self.logger.error(f"| ERR | unexepcted err in keep alive: {e}")
            
            if self.running:
                wait_time = random.randint(60,540)  # 1-9 mins
                mins, secs = divmod(wait_time,60)
                self.logger.info(f"waiting {mins} mins {secs} secs til next ping")
                
                for _ in range(wait_time):
                    if not self.running:
                        break
                    time.sleep(1)

def setup_keepalive(app):
    keepalive = KeepAlive()
    
    def start_delayed():
        time.sleep(90)  # let server get ready
        keepalive.start()
    
    if keepalive.enabled: # strt on bg thread
        thread = threading.Thread(target=start_delayed, daemon=True)
        thread.start()
    
    import atexit
    atexit.register(keepalive.stop)
    return keepalive