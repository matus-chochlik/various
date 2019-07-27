import os
import pickle
import multiprocessing

_1MiB = 1024.0*1024.0
# ------------------------------------------------------------------------------
class ProcessData(object):
    # --------------------------------------------------------------------------
    def __init__(self, args):
        self._max_mu_values = 8
        self.memory_usage = list()
        self.args = [a for a in args]
        self.output = None
        for i in xrange(1, len(args)):
            if args[i] in ["-o", "--output"]:
                self.output = args[i+1]

    # --------------------------------------------------------------------------
    def is_temporary(self):
        return self.output is None or self.output.startswith("cmTC_")

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
    def fix_before_save(self):
        self._processes = {
            k: v for (k, v) in self._processes.items() if not v.is_temporary()
        }

    # --------------------------------------------------------------------------
    def process_data(self, proc):
        strl = [s for s in proc.args()[1:] if not s.startswith("-plugin-opt=")]
        strl = sorted(strl)
        uid = proc.string_list_hash(strl)
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
    try:
        user_data.fix_before_save()
        pickle.dump(user_data, open('atmost.ld.data', 'w'))
    except Exception as err:
        print(err)

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
        witp = procs.waiting()
        pd = user_data.process_data(proc)
        let_go = False
        avg_usage = None
        if len(actp) < 1:
            let_go = True
        else:
            avg_usage = pd.avg_memory_usage()
            try:
                avail_mem  = procs.total_memory()
                for other in actp:
                    opd = user_data.process_data(other)
                    avail_mem -= opd.avg_memory_usage()
                avail_mem = (avail_mem + procs.available_memory()) * 0.45

                if avail_mem > avg_usage:
                    let_go = True
            except: pass

        if let_go:
            if pd.output is not None:
                    print("linking|a=%d|w=%d|: %s%s" % (
                        1+len(actp),
                        0+len(witp),
                        pd.output,
                        "" if avg_usage is None else " (uses %1.2f MB)" % (
                            avg_usage / _1MiB
                        )
                    ))
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
                avg_usage = pd.avg_memory_usage() / _1MiB
                print("linked: %s (used %1.2f MB)" % (args[i+1], avg_usage))

# ------------------------------------------------------------------------------
