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
    # TODO: realtime always-on monitor version of main
    # naive version
    i = 0
    try:
        while (not loops) or (i < loops):
            checker()
            time.sleep(sleep_interval)
            submitter()
            time.sleep(sleep_interval)
            i += 1
    except KeyboardInterrupt as e:
        print("Quit the main job")
        exit(0)
