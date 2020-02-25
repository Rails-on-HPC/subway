import time


def main_once(
    checker, submitter
):  ## preprocesser is once for all and hence not include in main

    ######
    # check part
    ######

    print("------begin checker------")
    checker()

    ######
    # submit part
    ######

    print("------begin submitter------")
    submitter()


def main_rt(checker, submitter, sleep_interval=10, loops=None):
    """
    
    :param checker:
    :param submitter:
    :param sleep_interval:
    :param loops:
    :return:
    """
    # TODO: better way for realtime always-on monitor version of main?
    # naive version
    i = 0
    if isinstance(sleep_interval, tuple) or isinstance(sleep_interval, list):
        after_checker_interval, after_submitter_interval = sleep_interval
    else:
        after_checker_interval = after_submitter_interval = sleep_interval
    try:
        while (not loops) or (i < loops):
            print("------begin checker------")
            checker()
            time.sleep(after_checker_interval)
            print("------begin submitter------")
            submitter()
            time.sleep(after_submitter_interval)
            i += 1
    except KeyboardInterrupt as e:
        print("Quit the main job")
        exit(0)
