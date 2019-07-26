import os
import pickle
import multiprocessing

# ------------------------------------------------------------------------------
class ProcessData(object):
    # --------------------------------------------------------------------------
    def __init__(self, args):
        self._max_mu_values = 8
        self.memory_usage = list()
        self.args = args

    # --------------------------------------------------------------------------
    def add_memory_usage(self, count_bytes):
        if count_bytes > 0:
            mu = self.memory_usage
            if len(mu) > self._max_mu_values:
                mu = mu[-self._max_mu_values:]
            mu.append(count_bytes)

    # --------------------------------------------------------------------------
    def avg_memory_usage(self):
        mu = self.memory_usage
        if len(mu) > 0:
            return sum(mu) / len(mu)

# ------------------------------------------------------------------------------
class SessionData(object):
    # --------------------------------------------------------------------------
    def __init__(self):
        self._processes = dict()

    # --------------------------------------------------------------------------
    def process_data(self, proc):
        uid = proc.command_uid()
        try:
            return self._processes[uid]
        except KeyError:
            pd = ProcessData(proc.args())
            self._processes[uid] = pd
            return pd

# ------------------------------------------------------------------------------
def load_user_data():
    try: return pickle.load(open('atmost.ld.data', 'r'))
    except: return SessionData()

# ------------------------------------------------------------------------------
def save_user_data(user_data):
    pickle.dump(user_data, open('atmost.ld.data', 'w'))

# ------------------------------------------------------------------------------
def is_linker(proc):
    linker_names = [
        'x86_64-linux-gnu-gold',
        'x86_64-linux-gnu-ld',
        'gold',
        'ld'
    ]
    return proc.basename() in linker_names

# ------------------------------------------------------------------------------
def let_process_go(user_data, procs):
    proc = procs.current()
    if is_linker(proc):
        args = proc.args()
        actp = procs.active()
        let_go = False
        if len(actp) < 1:
            let_go = True
        else:
            avg_usage = user_data.process_data(proc).avg_memory_usage()
            try:
                avail_mem  = procs.total_memory()
                for other in actp:
                    avail_mem -= user_data.process_data(other).avg_memory_usage()
                avail_mem = (avail_mem + procs.available_memory()) * 0.45

                print(avail_mem, avg_usage)
                if avail_mem > avg_usage:
                    let_go = True
            except: pass

        if let_go:
            for i in xrange(1, len(args)):
                if args[i] in ["-o", "--output"]:
                    print("linking|%d|: %s" % (1+len(actp), args[i+1]))
            return True
        return False

    return len(procs.active()) <  multiprocessing.cpu_count()

# ------------------------------------------------------------------------------
def process_finished(user_data, proc):
    if is_linker(proc):
        args = proc.args()
        pd = user_data.process_data(proc)
        pd.add_memory_usage(proc.max_memory_bytes())
        for i in xrange(1, len(args)):
            if args[i] in ["-o", "--output"]:
                avg_usage = pd.avg_memory_usage() / (1024*1024)
                print("linked: %s (used %1.2f MB)" % (args[i+1], avg_usage))

# ------------------------------------------------------------------------------
