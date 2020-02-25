import time


def main_once(checker, submitter):
    """
    main entry point run checker and submitter once.

    :param checker: Checker.
    :param submitter: Submitter.
    :return: None
    """

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
    realtime main monitor for subway entry_point

    :param checker: Checker.
    :param submitter: Submitter.
    :param sleep_interval: Optional(Union(float, Tuple(float, float))), default 10.
                There are two intervals, one after checker, one after submitter.
                If one number is given, then two intervals are the same.
                If tuple or list of 2 numbers are given, they are explained as
                (after_checker_interval, after_submitter_interval)
    :param loops: Optional(int), default None.
                max loops before exit, none for running forever,
                but the monitor can still quit if no job is running as expected.
    :return: None
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
