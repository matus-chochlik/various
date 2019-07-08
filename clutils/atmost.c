/* Copyright (c) 2019 Matus Chochlik
 */
#include <assert.h>
#include <fcntl.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <sys/sysinfo.h>
#include <sys/types.h>
#include <unistd.h>

//------------------------------------------------------------------------------
struct options {
    const char* path;
    int sep_arg;
    int max_count;
    int max_total_procs;
    float max_cpu_load1;
    float max_cpu_load5;
    float max_used_ram;
    float max_used_swap;
    bool ipc_remove;
    bool check_cpu_load1;
    bool check_cpu_load5;
    bool check_used_ram;
    bool check_used_swap;
    bool check_total_procs;
};
//------------------------------------------------------------------------------
static bool overloaded(struct options* opts) {
    struct sysinfo si;
    sysinfo(&si);

    if (opts->check_used_ram) {
        const float current_used_ram =
            100.f * (1.f - ((float)si.freeram) / ((float)si.totalram));
        if (opts->max_used_ram < current_used_ram) {
            return true;
        }
    }

    if (opts->check_used_swap) {
        const float current_used_swap =
            100.f * (1.f - ((float)si.freeswap) / ((float)si.totalswap));
        if (opts->max_used_swap < current_used_swap) {
            return true;
        }
    }

    if (opts->check_cpu_load1) {
        const float current_cpu_load1 =
            ((float)si.loads[0]) / ((float)(1U << (SI_LOAD_SHIFT)));
        if (opts->max_cpu_load1 < current_cpu_load1) {
            return true;
        }
    }

    if (opts->check_cpu_load5) {
        const float current_cpu_load5 =
            ((float)si.loads[1]) / ((float)(1U << (SI_LOAD_SHIFT)));
        if (opts->max_cpu_load5 < current_cpu_load5) {
            return true;
        }
    }

    if (opts->check_total_procs) {
        if (opts->max_total_procs < (int)si.procs) {
            return true;
        }
    }

    return false;
}
//------------------------------------------------------------------------------
static int parse_args(int argc, const char** argv, struct options* opts);
static int execute(struct options* opts, int argc, const char** argv);
static const char* canonical_path(const char* arg);
//------------------------------------------------------------------------------
int main(int argc, const char** argv) {
    int result = 0;
    if (argc > 1) {
        struct options opts = {.path = NULL,
                               .sep_arg = 0,
                               .max_count = 1,
                               .max_cpu_load1 = 100,
                               .check_cpu_load1 = false,
                               .max_cpu_load5 = 100,
                               .check_cpu_load5 = false,
                               .max_used_ram = 100,
                               .check_used_ram = false,
                               .max_used_swap = 50,
                               .check_used_swap = false,
                               .max_total_procs = 1000,
                               .check_total_procs = false,
                               .ipc_remove = false};

        result = parse_args(argc, argv, &opts);

        overloaded(&opts);

        if (result == 0) {
            if (opts.sep_arg > 0 && opts.sep_arg + 1 < argc) {
                return execute(&opts, argc - opts.sep_arg - 1,
                               argv + opts.sep_arg + 1);
            }
        }
    }
    return result;
}
//------------------------------------------------------------------------------
static bool is_executable(const char* path) {
    struct stat sb;
    return (stat(path, &sb) == 0) && (sb.st_mode & S_IXUSR) &&
           S_ISREG(sb.st_mode);
}
//------------------------------------------------------------------------------
static bool is_file(const char* path) {
    struct stat sb;
    return (stat(path, &sb) == 0) && (sb.st_mode & S_IRUSR) &&
           S_ISREG(sb.st_mode);
}
//------------------------------------------------------------------------------
union atmost_semun {
    int val;
};
//------------------------------------------------------------------------------
static int execute(struct options* opts, int argc, const char** argv) {
    const char* executable = canonical_path(argv[0]);
    if (strlen(executable) > 0) {
        key_t ky = ftok(opts->path ? opts->path : executable, 0xA73057);
        int sems = semget(ky, 1, 0666 | IPC_CREAT | IPC_EXCL);

        if (sems < 0) {
            sems = semget(ky, 1, 0);
            if (sems < 0) {
                perror("atmost: ");
                return 3;
            }
        } else {
            union atmost_semun su = {.val = opts->max_count};
            if (semctl(sems, 0, SETVAL, su) < 0) {
                perror("atmost: ");
                return 4;
            }
        }

        if (opts->ipc_remove) {
            if (semctl(sems, 0, IPC_RMID) < 0) {
                perror("atmost: ");
                return 5;
            } else {
                return 0;
            }
        } else {
            struct sembuf sb = {
                .sem_num = 0, .sem_op = -1, .sem_flg = SEM_UNDO};

            if (semop(sems, &sb, 1) < 0) {
                perror("atmost: ");
                return 5;
            }

            while (overloaded(opts)) {
                usleep(100000);
            }

            return execv(executable, (char* const*)argv);
        }
    }
    fprintf(stderr, "atmost: could not find executable '%s'\n", argv[0]);
    return 2;
}
//------------------------------------------------------------------------------
static int parse_args(int argc, const char** argv, struct options* opts) {
    for (int a = 1; a < argc; ++a) {
        if (strcmp(argv[a], "-n") == 0) {
            if (argv[a + 1]) {
                opts->max_count = atoi(argv[a + 1]);
                if (opts->max_count <= 0) {
                    fprintf(stderr, "atmost: invalid max count '%s' after -n\n",
                            argv[a + 1]);
                    return 1;
                }
            } else {
                fprintf(stderr, "atmost: missing max count after -n\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-l") == 0) {
            if (argv[a + 1]) {
                opts->max_cpu_load1 = atof(argv[a + 1]);
                if (opts->max_cpu_load1 <= 0.f) {
                    fprintf(stderr,
                            "atmost: invalid max CPU load '%s' after -l\n",
                            argv[a + 1]);
                    return 1;
                }
                opts->check_cpu_load1 = true;
            } else {
                fprintf(stderr,
                        "atmost: missing max CPU load value after -l\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-L") == 0) {
            if (argv[a + 1]) {
                opts->max_cpu_load5 = atof(argv[a + 1]);
                if (opts->max_cpu_load5 <= 0.f) {
                    fprintf(stderr,
                            "atmost: invalid max CPU load '%s' after -L\n",
                            argv[a + 1]);
                    return 1;
                }
                opts->check_cpu_load5 = true;
            } else {
                fprintf(stderr,
                        "atmost: missing max CPU load value after -L\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-m") == 0) {
            if (argv[a + 1]) {
                opts->max_used_ram = atof(argv[a + 1]);
                if (opts->max_used_ram <= 0.f) {
                    fprintf(stderr,
                            "atmost: invalid max used RAM '%s' after -m\n",
                            argv[a + 1]);
                    return 1;
                }
                opts->check_used_ram = true;
            } else {
                fprintf(stderr,
                        "atmost: missing max used RAM value after -m\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-s") == 0) {
            if (argv[a + 1]) {
                opts->max_used_swap = atof(argv[a + 1]);
                if (opts->max_used_swap <= 0.f) {
                    fprintf(stderr,
                            "atmost: invalid max used swap '%s' after -s\n",
                            argv[a + 1]);
                    return 1;
                }
                opts->check_used_swap = true;
            } else {
                fprintf(stderr,
                        "atmost: missing max used swap value after -s\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-p") == 0) {
            if (argv[a + 1]) {
                opts->max_total_procs = atoi(argv[a + 1]);
                if (opts->max_total_procs <= 0) {
                    fprintf(stderr,
                            "atmost: invalid max processes '%s' after -p\n",
                            argv[a + 1]);
                    return 1;
                }
                opts->check_total_procs = true;
            } else {
                fprintf(stderr,
                        "atmost: missing max processes value after -p\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-f") == 0) {
            if (argv[a + 1]) {
                opts->path = argv[a + 1];
                if (!is_file(opts->path)) {
                    fprintf(stderr, "atmost: invalid file path '%s'\n",
                            argv[a + 1]);
                    return 1;
                }
            } else {
                fprintf(stderr, "atmost: missing file path after -f\n");
                return 1;
            }
            ++a;
        } else if (strcmp(argv[a], "-r") == 0) {
            opts->ipc_remove = true;
        } else if (strcmp(argv[a], "--") == 0) {
            if (opts->sep_arg < 1) {
                opts->sep_arg = a;
                break;
            }
        }
    }
    return 0;
}
//------------------------------------------------------------------------------
static const char* make_exe_path(char* temp, const char* path, const char* name,
                                 ptrdiff_t p, ptrdiff_t i, size_t l) {
    assert(i - p + 1 < PATH_MAX);
    strncpy(temp, path + p, i - p);
    assert(i - p + l + 2 < PATH_MAX);
    temp[i - p] = '/';
    strncpy(temp + i - p + 1, name, l);
    temp[i - p + l + 1] = '\0';
    return temp;
}
//------------------------------------------------------------------------------
static const char* which(const char* arg) {
    static char temp[PATH_MAX] = {'\0'};

    if (is_executable(arg)) {
        strncpy(temp, arg, PATH_MAX);
    } else {
        const char* path = getenv("PATH");
        if (path) {
            const size_t l = strlen(arg);
            ptrdiff_t p = 0;
            ptrdiff_t i = 0;
            while (true) {
                if (path[i] == '\0') {
                    if (i < p) {
                        if (is_executable(
                                make_exe_path(temp, path, arg, p, i, l))) {
                            break;
                        }
                    }
                    break;
                } else if (path[i] == ':') {
                    if (is_executable(
                            make_exe_path(temp, path, arg, p, i, l))) {
                        break;
                    }
                    p = i + 1;
                }
                ++i;
            }
        }
    }
    return temp;
}
//------------------------------------------------------------------------------
static const char* canonical_path(const char* arg) {
    static char temp[PATH_MAX] = {'\0'};

    return realpath(which(arg), temp);
}
//------------------------------------------------------------------------------
