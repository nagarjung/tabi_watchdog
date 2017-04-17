from __future__ import print_function

import sys
import time
import logging
import os
import json
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tabi.emulator import parse_registry_data
from tabi.emulator import detect_hijacks

def choose_input(input):
    if input == "mabo":
        from tabi.input.mabo import mabo_input
        return mabo_input

    elif input == "bgpreader":
        from tabi.input.bgpreader import bgpreader_input
        return bgpreader_input

    else:
        raise ValueError("unknown input type {}".format(input))


def registry_kwargs(file_path):

    if os.path.basename(file_path) == "routes.csv":
        kwargs["irr_ro_file"] = os.path.basename(file_path)

    if os.path.basename(file_path) == "roa.csv":
        kwargs["rpki_roa_file"] = os.path.basename(file_path)

    if os.path.basename(file_path) == "maintainers.csv":
        kwargs["irr_mnt_file"] = os.path.basename(file_path)        

    if os.path.basename(file_path) == "organisations.csv":
        kwargs["irr_org_file"] = os.path.basename(file_path)
    
    return kwargs


class PollingHandler(FileSystemEventHandler):

    def on_created(self, event):
        
        super(PollingHandler, self).on_created(event)
	
        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)    	
        
        if args.registry_path == os.path.dirname(event.src_path):
            reg_kwargs = registry_kwargs(event.src_path)

            if len(reg_kwargs) == 4:
                print (reg_kwargs)
                print ("Completed parsing registry data")

        if args.bgp_path == os.path.dirname(event.src_path):
            print ("bgp event")

	
if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--collector",
                        help="collector name from where the log files are",
                        default="none")
    parser.add_argument("-i", "--input",
                        help="MRT parser, e.g. 'mabo'",
                        default="mabo")
    
    parser.add_argument("--registry-path",
                        help="enter the path for registry data")

    parser.add_argument("--bgp-path",
                        help="enter the path for bgp rib and update files")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="more logging")
    

    args = parser.parse_args()    
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    kwargs = {}
    mrt_files = []
    observers = []
    
    targets = []
    
    event_handler = PollingHandler()
    observer = Observer()        
    targets.append(args.registry_path)
    targets.append(args.bgp_path)
    
    for path in targets:
        targetPath = str(path)
        observer.schedule(event_handler, targetPath, recursive=False)
        observers.append(observer)
    
    observer.start()

    try:
        while True:            
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
