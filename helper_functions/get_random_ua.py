# make sure you've done: git clone https://github.com/tamimibrahim17/List-of-user-agents.git at this point so the txt files are in your directory

import logging
import numpy as np

def get_random_ua(browser):
    random_ua = ''
    ua_file = f'{browser}.txt'.title()

    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
    except Exception as ex:
        logging('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua
