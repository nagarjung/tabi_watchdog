from __future__ import print_function

import sys
import time
import logging
import os
import json
import datetime

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

                self.list_funcs = parse_registry_data(**reg_kwargs)
                logging.info("Completed parsing registry data")
        
        if args.bgp_path == os.path.dirname(event.src_path):

            mrt_files.append(event.src_path)

            if len(mrt_files) == 2:

                logging.info(" two bgp files generated")

                input_kwargs = {"files": mrt_files}                
                input = choose_input(args.input)
                bgp_kwargs = input(args.collector, **input_kwargs)
                
                start = datetime.datetime.now()
                count = 0
                for conflict in detect_hijacks(self.list_funcs, **bgp_kwargs):
                    if conflict["type"] == "ABNORMAL":
                        count += 1
                        logging.info("generating hijacks")
                        print(json.dumps(conflict))

                logging.info("Hijacks completed")
                end = datetime.datetime.now()                
                detection_time = end - start
                
                logging.info("Number of hijacks found are : %s", count)        
                logging.info("BGP Hijacks detecttion time is: %s",detection_time.total_seconds())
                
                #del mrt_files[:]
	
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
