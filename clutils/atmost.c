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

#define MODIFIER_COUNT 1
//------------------------------------------------------------------------------
struct resource_limit {
	float value;
	float modifiers[MODIFIER_COUNT];
	bool check;
};
//------------------------------------------------------------------------------
struct options {
	const char* path;
	int sep_arg;
	int bat_tz_id;
	int gpu_tz_id;
	int cpu_tz_id;

	struct resource_limit max_instances;
	struct resource_limit max_total_procs;
	struct resource_limit max_bat_temp;
	struct resource_limit max_gpu_temp;
	struct resource_limit max_cpu_temp;
	struct resource_limit max_cpu_load1;
	struct resource_limit max_cpu_load5;
	struct resource_limit max_used_ram;
	struct resource_limit max_used_swap;
	struct resource_limit max_io_ops;
	bool ipc_remove;
};
//------------------------------------------------------------------------------
struct check_context {
	struct options* opts;
	struct sysinfo* si;
};
//------------------------------------------------------------------------------
struct limit_check {
	float (*value_getter)(struct check_context*);
	struct resource_limit* limit;
};
//------------------------------------------------------------------------------
static bool is_over_limit(
  struct limit_check* info, struct check_context* context) {
	if(info->limit->check) {
		if(info->limit->value < info->value_getter(context)) {
			return true;
		}
	}
	return false;
}
//------------------------------------------------------------------------------
static float total_proc_count(struct check_context*);
static float free_ram_perc(struct check_context*);
static float free_swap_perc(struct check_context*);
static float cpu_load1(struct check_context*);
static float cpu_load5(struct check_context*);
static float cpu_temperature(struct check_context*);
static float gpu_temperature(struct check_context*);
static float bat_temperature(struct check_context*);
static float io_ops_count(struct check_context*);
//------------------------------------------------------------------------------
static bool overloaded(struct options* opts) {
	struct sysinfo si;
	sysinfo(&si);

	struct check_context context;
	context.opts = opts;
	context.si = &si;

	struct limit_check max_limits[] = {
	  {.value_getter = total_proc_count, .limit = &opts->max_total_procs},
	  {.value_getter = free_ram_perc, .limit = &opts->max_used_ram},
	  {.value_getter = free_swap_perc, .limit = &opts->max_used_swap},
	  {.value_getter = cpu_load1, .limit = &opts->max_cpu_load1},
	  {.value_getter = cpu_load5, .limit = &opts->max_cpu_load5},
	  {.value_getter = cpu_temperature, .limit = &opts->max_cpu_temp},
	  {.value_getter = gpu_temperature, .limit = &opts->max_gpu_temp},
	  {.value_getter = bat_temperature, .limit = &opts->max_bat_temp},
	  {.value_getter = io_ops_count, .limit = &opts->max_io_ops}};

	for(size_t l = 0; l < sizeof(max_limits) / sizeof(max_limits[0]); ++l) {
		if(is_over_limit(&max_limits[l], &context)) {
			return true;
		}
	}

	return false;
}
//------------------------------------------------------------------------------
static int init_opts(struct options* opts);
static int parse_args(int argc, const char** argv, struct options* opts);
static int execute(struct options* opts, int argc, const char** argv);
static const char* canonical_path(const char* arg);
//------------------------------------------------------------------------------
int main(int argc, const char** argv) {
	int result = 0;
	if(argc > 1) {
		struct options opts;

		init_opts(&opts);
		result = parse_args(argc, argv, &opts);

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
				perror("atmost: semget failed:");
				return 3;
			}
		} else {
			union atmost_semun su = {.val = (int)opts->max_instances.value};
			if(semctl(sems, 0, SETVAL, su) < 0) {
				perror("atmost: semctl failed:");
				return 4;
			}
		}

		if(opts->ipc_remove) {
			if(semctl(sems, 0, IPC_RMID) < 0) {
				perror("atmost: semctl failed: ");
				return 5;
			} else {
				return 0;
			}
		} else {
			struct sembuf sb = {
			  .sem_num = 0, .sem_op = -1, .sem_flg = SEM_UNDO};

			if(semop(sems, &sb, 1) < 0) {
				perror("atmost: semop failed: ");
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
static int init_opts(struct options* opts) {
	opts->path = NULL;
	opts->sep_arg = 0;
	opts->bat_tz_id = -1;
	opts->gpu_tz_id = -1;
	opts->cpu_tz_id = -1;

	opts->max_instances.check = true;
	opts->max_instances.value = 2;

	opts->max_bat_temp.check = false;
	opts->max_bat_temp.value = 60;

	opts->max_gpu_temp.check = false;
	opts->max_gpu_temp.value = 80;

	opts->max_cpu_temp.check = false;
	opts->max_cpu_temp.value = 80;

	opts->max_cpu_load1.check = false;
	opts->max_cpu_load1.value = 30;

	opts->max_cpu_load5.check = false;
	opts->max_cpu_load5.value = 15;

	opts->max_used_ram.check = false;
	opts->max_used_ram.value = 90;

	opts->max_used_swap.check = false;
	opts->max_used_swap.value = 50;

	opts->max_total_procs.value = 2000;
	opts->max_total_procs.check = false;

	opts->max_io_ops.check = false;
	opts->max_io_ops.value = 100;

	opts->ipc_remove = false;
}
//------------------------------------------------------------------------------
static bool parse_limit_arg(int* a,
  int argc,
  const char** argv,
  const char* flag,
  const char* description,
  struct resource_limit* limit) {
	if(*a < argc) {
		if(strcmp(argv[*a], flag) == 0) {
			if(argv[*a + 1]) {
				if(sscanf(argv[*a + 1], "%f", &limit->value)) {
					limit->check = true;
					++(*a);
				} else {
					fprintf(stderr,
					  "atmost: invalid %s value '%s' after %s\n",
					  description,
					  argv[*a + 1],
					  argv[*a]);
					return false;
				}
			} else {
				fprintf(stderr,
				  "atmost: missing %s value after %s\n",
				  description,
				  argv[*a]);
				return false;
			}
			return true;
		}
	}
	return false;
}
//------------------------------------------------------------------------------
static int parse_args(int argc, const char** argv, struct options* opts) {
	for(int a = 1; a < argc; ++a) {
		if(parse_limit_arg(&a,
			 argc,
			 argv,
			 "-n",
			 "maximum concurrent instance count",
			 &opts->max_instances)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-l",
					"maximum 1 minute average CPU load",
					&opts->max_cpu_load1)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-L",
					"maximum 5 minutes average CPU load",
					&opts->max_cpu_load5)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-m",
					"maximum used RAM percentage",
					&opts->max_used_ram)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-s",
					"maximum used swap space percentage",
					&opts->max_used_swap)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-p",
					"maximum number of running processes",
					&opts->max_total_procs)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-tc",
					"maximum CPU temperature",
					&opts->max_cpu_temp)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-tg",
					"maximum GPU temperature",
					&opts->max_gpu_temp)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-tb",
					"maximum battery temperature",
					&opts->max_bat_temp)) {
		} else if(parse_limit_arg(&a,
					argc,
					argv,
					"-io",
					"maximum number of I/O operations",
					&opts->max_io_ops)) {
		} else if(strcmp(argv[a], "-f") == 0) {
			if(argv[a + 1]) {
				opts->path = argv[a + 1];
				if(!is_file(opts->path)) {
					fprintf(stderr,
					  "atmost: invalid token file path '%s' -f\n",
					  argv[a + 1]);
					return 1;
				}
			} else {
				fprintf(stderr, "atmost: missing token file path after -f\n");
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
static bool on_battery(struct options* opts) {
	FILE* file = fopen("/sys/class/power_supply/AC/online", "rt");
	if(file) {
		int online = 1;
		fscanf(file, "%d", &online);
		fclose(file);
		return online ? false : true;
	}
	return false;
}
//------------------------------------------------------------------------------
static float total_proc_count(struct check_context* ctx) {
	return (float)ctx->si->procs;
}
//------------------------------------------------------------------------------
static float free_ram_perc(struct check_context* ctx) {
	return 100.f
		   * (1.f - ((float)ctx->si->freeram) / ((float)ctx->si->totalram));
}
//------------------------------------------------------------------------------
static float free_swap_perc(struct check_context* ctx) {
	return 100.f
		   * (1.f - ((float)ctx->si->freeswap) / ((float)ctx->si->totalswap));
}
//------------------------------------------------------------------------------
static float cpu_load1(struct check_context* ctx) {
	return ((float)ctx->si->loads[0]) / ((float)(1U << (SI_LOAD_SHIFT)));
}
//------------------------------------------------------------------------------
static float cpu_load5(struct check_context* ctx) {
	return ((float)ctx->si->loads[1]) / ((float)(1U << (SI_LOAD_SHIFT)));
}
//------------------------------------------------------------------------------
static float cpu_temperature(struct check_context* ctx) {
	return get_tz_temperature(&ctx->opts->cpu_tz_id, "CPU");
}
//------------------------------------------------------------------------------
static float gpu_temperature(struct check_context* ctx) {
	return get_tz_temperature(&ctx->opts->gpu_tz_id, "GPU");
}
//------------------------------------------------------------------------------
static float bat_temperature(struct check_context* ctx) {
	return get_tz_temperature(&ctx->opts->bat_tz_id, "BAT");
}
//------------------------------------------------------------------------------
static float io_ops_count(struct check_context* ctx) {
	static char buffer[1024];
	FILE* file = fopen("/proc/diskstats", "rt");
	if(file) {
		int iosum = 0;
		int count = 0;
		while(fgets(buffer, sizeof(buffer), file)) {
			sscanf(buffer, "%*d%*d%*s%*d%*d%*d%*d%*d%*d%*d%*d%d", &count);
			iosum += count;
		}
		fclose(file);

		return (float)iosum;
	}
	return 0.f;
}
//------------------------------------------------------------------------------
