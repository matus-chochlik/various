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
	int bat_tz_id;
	int cpu_tz_id;
	int max_count;
	int max_total_procs;
	float max_bat_temp;
	float max_cpu_temp;
	float max_cpu_load1;
	float max_cpu_load5;
	float max_used_ram;
	float max_used_swap;
	float max_io_ops;
	bool ipc_remove;
	bool check_total_procs;
	bool check_bat_temp;
	bool check_cpu_temp;
	bool check_cpu_load1;
	bool check_cpu_load5;
	bool check_used_ram;
	bool check_used_swap;
	bool check_io_ops;
};
//------------------------------------------------------------------------------
static float cpu_temperature(struct options* opts);
static float bat_temperature(struct options* opts);
static int io_ops_count();
//------------------------------------------------------------------------------
static bool overloaded(struct options* opts) {
	struct sysinfo si;
	sysinfo(&si);

	if(opts->check_used_ram) {
		const float current_used_ram =
		  100.f * (1.f - ((float)si.freeram) / ((float)si.totalram));
		if(opts->max_used_ram < current_used_ram) {
			return true;
		}
	}

	if(opts->check_used_swap) {
		const float current_used_swap =
		  100.f * (1.f - ((float)si.freeswap) / ((float)si.totalswap));
		if(opts->max_used_swap < current_used_swap) {
			return true;
		}
	}

	if(opts->check_cpu_load1) {
		const float current_cpu_load1 =
		  ((float)si.loads[0]) / ((float)(1U << (SI_LOAD_SHIFT)));
		if(opts->max_cpu_load1 < current_cpu_load1) {
			return true;
		}
	}

	if(opts->check_cpu_load5) {
		const float current_cpu_load5 =
		  ((float)si.loads[1]) / ((float)(1U << (SI_LOAD_SHIFT)));
		if(opts->max_cpu_load5 < current_cpu_load5) {
			return true;
		}
	}

	if(opts->check_total_procs) {
		if(opts->max_total_procs < (int)si.procs) {
			return true;
		}
	}

	if(opts->check_cpu_temp) {
		const float current_cpu_temp = cpu_temperature(opts);
		if(opts->max_cpu_temp < current_cpu_temp) {
			return true;
		}
	}

	if(opts->check_bat_temp) {
		const float current_bat_temp = bat_temperature(opts);
		if(opts->max_bat_temp < current_bat_temp) {
			return true;
		}
	}

	if(opts->check_io_ops) {
		const int current_io_ops = io_ops_count();
		if(opts->max_io_ops < current_io_ops) {
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
	if(argc > 1) {
		struct options opts = {.path = NULL,
		  .bat_tz_id = -1,
		  .cpu_tz_id = -1,
		  .sep_arg = 0,
		  .max_count = 1,
		  .max_bat_temp = 100,
		  .check_bat_temp = false,
		  .max_cpu_temp = 100,
		  .check_cpu_temp = false,
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
		  .max_io_ops = 100,
		  .check_io_ops = false,
		  .ipc_remove = false};

		result = parse_args(argc, argv, &opts);

		overloaded(&opts);

		if(result == 0) {
			if(opts.sep_arg > 0 && opts.sep_arg + 1 < argc) {
				return execute(
				  &opts, argc - opts.sep_arg - 1, argv + opts.sep_arg + 1);
			}
		}
	}
	return result;
}
//------------------------------------------------------------------------------
static bool is_executable(const char* path) {
	struct stat sb;
	return (stat(path, &sb) == 0) && (sb.st_mode & S_IXUSR)
		   && S_ISREG(sb.st_mode);
}
//------------------------------------------------------------------------------
static bool is_file(const char* path) {
	struct stat sb;
	return (stat(path, &sb) == 0) && (sb.st_mode & S_IRUSR)
		   && S_ISREG(sb.st_mode);
}
//------------------------------------------------------------------------------
union atmost_semun {
	int val;
};
//------------------------------------------------------------------------------
static int execute(struct options* opts, int argc, const char** argv) {
	const char* executable = canonical_path(argv[0]);
	if(strlen(executable) > 0) {
		key_t ky = ftok(opts->path ? opts->path : executable, 0xA73057);
		int sems = semget(ky, 1, 0666 | IPC_CREAT | IPC_EXCL);

		if(sems < 0) {
			sems = semget(ky, 1, 0);
			if(sems < 0) {
				perror("atmost: ");
				return 3;
			}
		} else {
			union atmost_semun su = {.val = opts->max_count};
			if(semctl(sems, 0, SETVAL, su) < 0) {
				perror("atmost: ");
				return 4;
			}
		}

		if(opts->ipc_remove) {
			if(semctl(sems, 0, IPC_RMID) < 0) {
				perror("atmost: ");
				return 5;
			} else {
				return 0;
			}
		} else {
			struct sembuf sb = {
			  .sem_num = 0, .sem_op = -1, .sem_flg = SEM_UNDO};

			if(semop(sems, &sb, 1) < 0) {
				perror("atmost: ");
				return 5;
			}

			while(overloaded(opts)) {
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
	for(int a = 1; a < argc; ++a) {
		if(strcmp(argv[a], "-n") == 0) {
			if(argv[a + 1]) {
				opts->max_count = atoi(argv[a + 1]);
				if(opts->max_count <= 0) {
					fprintf(stderr,
					  "atmost: invalid max count '%s' after -n\n",
					  argv[a + 1]);
					return 1;
				}
			} else {
				fprintf(stderr, "atmost: missing max count after -n\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-l") == 0) {
			if(argv[a + 1]) {
				opts->max_cpu_load1 = atof(argv[a + 1]);
				if(opts->max_cpu_load1 <= 0.f) {
					fprintf(stderr,
					  "atmost: invalid max CPU load '%s' after -l\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_cpu_load1 = true;
			} else {
				fprintf(
				  stderr, "atmost: missing max CPU load value after -l\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-L") == 0) {
			if(argv[a + 1]) {
				opts->max_cpu_load5 = atof(argv[a + 1]);
				if(opts->max_cpu_load5 <= 0.f) {
					fprintf(stderr,
					  "atmost: invalid max CPU load '%s' after -L\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_cpu_load5 = true;
			} else {
				fprintf(
				  stderr, "atmost: missing max CPU load value after -L\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-m") == 0) {
			if(argv[a + 1]) {
				opts->max_used_ram = atof(argv[a + 1]);
				if(opts->max_used_ram <= 0.f) {
					fprintf(stderr,
					  "atmost: invalid max used RAM '%s' after -m\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_used_ram = true;
			} else {
				fprintf(
				  stderr, "atmost: missing max used RAM value after -m\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-s") == 0) {
			if(argv[a + 1]) {
				opts->max_used_swap = atof(argv[a + 1]);
				if(opts->max_used_swap <= 0.f) {
					fprintf(stderr,
					  "atmost: invalid max used swap '%s' after -s\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_used_swap = true;
			} else {
				fprintf(
				  stderr, "atmost: missing max used swap value after -s\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-p") == 0) {
			if(argv[a + 1]) {
				opts->max_total_procs = atoi(argv[a + 1]);
				if(opts->max_total_procs <= 0) {
					fprintf(stderr,
					  "atmost: invalid max processes '%s' after -p\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_total_procs = true;
			} else {
				fprintf(
				  stderr, "atmost: missing max processes value after -p\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-tc") == 0) {
			if(argv[a + 1]) {
				opts->max_cpu_temp = atof(argv[a + 1]);
				if(opts->max_cpu_temp <= 0.f) {
					fprintf(stderr,
					  "atmost: invalid CPU temperature '%s' after -tc\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_cpu_temp = true;
			} else {
				fprintf(
				  stderr, "atmost: missing CPU temperature value after -tc\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-tb") == 0) {
			if(argv[a + 1]) {
				opts->max_bat_temp = atof(argv[a + 1]);
				if(opts->max_bat_temp <= 0.f) {
					fprintf(stderr,
					  "atmost: invalid battery temperature '%s' after -tb\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_bat_temp = true;
			} else {
				fprintf(stderr,
				  "atmost: missing battery temperature value after -tb\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-io") == 0) {
			if(argv[a + 1]) {
				opts->max_io_ops = atoi(argv[a + 1]);
				if(opts->max_io_ops <= 0) {
					fprintf(stderr,
					  "atmost: invalid max I/O count '%s' after -io\n",
					  argv[a + 1]);
					return 1;
				}
				opts->check_io_ops = true;
			} else {
				fprintf(
				  stderr, "atmost: missing max I/O count value after -io\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-f") == 0) {
			if(argv[a + 1]) {
				opts->path = argv[a + 1];
				if(!is_file(opts->path)) {
					fprintf(
					  stderr, "atmost: invalid file path '%s'\n", argv[a + 1]);
					return 1;
				}
			} else {
				fprintf(stderr, "atmost: missing file path after -f\n");
				return 1;
			}
			++a;
		} else if(strcmp(argv[a], "-r") == 0) {
			opts->ipc_remove = true;
		} else if(strcmp(argv[a], "--") == 0) {
			if(opts->sep_arg < 1) {
				opts->sep_arg = a;
				break;
			}
		}
	}
	return 0;
}
//------------------------------------------------------------------------------
static const char* make_exe_path(char* temp,
  const char* path,
  const char* name,
  ptrdiff_t p,
  ptrdiff_t i,
  size_t l) {
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

	if(is_executable(arg)) {
		strncpy(temp, arg, PATH_MAX);
	} else {
		const char* path = getenv("PATH");
		if(path) {
			const size_t l = strlen(arg);
			ptrdiff_t p = 0;
			ptrdiff_t i = 0;
			while(true) {
				if(path[i] == '\0') {
					if(i < p) {
						if(is_executable(
							 make_exe_path(temp, path, arg, p, i, l))) {
							break;
						}
					}
					break;
				} else if(path[i] == ':') {
					if(is_executable(make_exe_path(temp, path, arg, p, i, l))) {
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
static int find_thermal_zone_id(const char* pattern) {
	char buffer[PATH_MAX];
	for(int id = 0; id < 50; ++id) {
		bool is_cpu_tz = false;
		sprintf(buffer, "/sys/class/thermal/thermal_zone%d/device/path", id);
		FILE* path_file = fopen(buffer, "rt");
		if(!path_file) {
			break;
		}
		if(fgets(buffer, PATH_MAX - 1, path_file) >= 0) {
			if(strstr(buffer, pattern) != NULL) {
				is_cpu_tz = true;
			}
		}
		fclose(path_file);
		if(is_cpu_tz) {
			return id;
		}
	}
	return -1;
}
//------------------------------------------------------------------------------
static float thermal_zone_temperature(int tz_id) {
	static char buffer[PATH_MAX];
	if(tz_id >= 0) {
		sprintf(buffer, "/sys/class/thermal/thermal_zone%d/temp", tz_id);
		FILE* tz_temp_file = fopen(buffer, "rt");
		if(tz_temp_file) {
			int mdegc = 0;
			if(fscanf(tz_temp_file, "%d", &mdegc) == 1) {
				return mdegc * 0.001f;
			}
		}
	}

	return 0.f;
}
//------------------------------------------------------------------------------
static float get_tz_temperature(int* ptz_id, const char* pattern) {
	if(*ptz_id < 0) {
		*ptz_id = find_thermal_zone_id(pattern);
	}
	if(*ptz_id >= 0) {
		return thermal_zone_temperature(*ptz_id);
	}
	return 0.f;
}
//------------------------------------------------------------------------------
static float cpu_temperature(struct options* opts) {
	return get_tz_temperature(&opts->cpu_tz_id, "CPU");
}
//------------------------------------------------------------------------------
static float bat_temperature(struct options* opts) {
	return get_tz_temperature(&opts->bat_tz_id, "BAT");
}
//------------------------------------------------------------------------------
static int io_ops_count() {
	static char buffer[1024];
	FILE* dsf = fopen("/proc/diskstats", "rt");
	if(dsf) {
		int iosum = 0;
		int count = 0;
		while(fgets(buffer, sizeof(buffer), dsf)) {
			sscanf(buffer, "%*d%*d%*s%*d%*d%*d%*d%*d%*d%*d%*d%d", &count);
			iosum += count;
		}
		fclose(dsf);

		return iosum;
	}
	return 0;
}
//------------------------------------------------------------------------------
