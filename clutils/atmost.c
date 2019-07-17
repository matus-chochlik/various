/* Copyright (c) 2019 Matus Chochlik
 */
#include <assert.h>
#include <fcntl.h>
#include <ifaddrs.h>
#include <limits.h>
#include <net/if.h>
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
#include <sys/wait.h>
#include <unistd.h>

//------------------------------------------------------------------------------
#define MODIFIER_COUNT 3
static const char* modifier_flags[MODIFIER_COUNT] = {"-batt", "-slnw", "-nonw"};
static const char* modifier_descriptions[MODIFIER_COUNT] = {
  "on battery", "slow network", "no network"};
//------------------------------------------------------------------------------
struct resource_limit {
	const char* description;
	float value;
	float modifiers[MODIFIER_COUNT];
	bool check;
};
//------------------------------------------------------------------------------
struct options;
static bool runs_on_battery(struct options* opts);
static bool slow_network_conn(struct options* opts);
static bool no_network_conn(struct options* opts);
//------------------------------------------------------------------------------
static float current_limit_value(
  struct resource_limit* limit, struct options* opts) {
	float result = limit->value;

	if(runs_on_battery(opts)) {
		result += limit->modifiers[0];
	}

	if(slow_network_conn(opts)) {
		result += limit->modifiers[1];
	}

	if(no_network_conn(opts)) {
		result += limit->modifiers[2];
	}

	return result;
}
//------------------------------------------------------------------------------
struct options {
	const char* path;
	int verbose;
	int sep_arg;
	int bat_tz_id;
	int gpu_tz_id;
	int cpu_tz_id;
	float slow_network_speed;

	union {
		struct {
			struct resource_limit max_instances;
			struct resource_limit max_total_procs;
			struct resource_limit max_bat_temp;
			struct resource_limit max_gpu_temp;
			struct resource_limit max_cpu_temp;
			struct resource_limit max_cpu_load1;
			struct resource_limit max_cpu_load5;
			struct resource_limit max_io_ops;
			struct resource_limit min_avail_ram;
			struct resource_limit min_free_ram;
			struct resource_limit min_free_swap;
			struct resource_limit min_nw_speed;
		};
		struct resource_limit limits[12];
	};
	bool ipc_remove;
	bool print_current;
	bool print_all_current;
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
static float difference_to_limit(
  struct limit_check* info, struct check_context* context, float mult) {
	if(info->limit->check) {
		const float current_value = info->value_getter(context);
		const float limit_value =
		  current_limit_value(info->limit, context->opts);
		const float diff = (current_value - limit_value) * mult;
		if(context->opts->verbose) {
			if(diff > 0.f) {
				printf("atmost: %s value %3.1f is %s limit %3.1f\n",
				  info->limit->description,
				  current_value,
				  (mult > 0.f ? "over" : "under"),
				  limit_value);
			} else if(context->opts->verbose > 1) {
				printf("atmost: %s value %3.1f is within limit %3.1f\n",
				  info->limit->description,
				  current_value,
				  limit_value);
			}
		}
		return diff;
	}
	return 0.f;
}
//------------------------------------------------------------------------------
static bool is_over_limit(
  struct limit_check* info, struct check_context* context) {
	return difference_to_limit(info, context, +1.f) > 0.f;
}
//------------------------------------------------------------------------------
static bool is_under_limit(
  struct limit_check* info, struct check_context* context) {
	return difference_to_limit(info, context, -1.f) > 0.f;
}
//------------------------------------------------------------------------------
static float total_proc_count(struct check_context*);
static float available_ram_perc(struct check_context*);
static float free_ram_perc(struct check_context*);
static float free_swap_perc(struct check_context*);
static float cpu_load1(struct check_context*);
static float cpu_load5(struct check_context*);
static float cpu_temperature(struct check_context*);
static float gpu_temperature(struct check_context*);
static float bat_temperature(struct check_context*);
static float io_ops_count(struct check_context*);
static float network_speed(struct check_context* ctx);
//------------------------------------------------------------------------------
static bool is_overloaded(struct options* opts) {
	struct sysinfo si;
	sysinfo(&si);

	struct check_context context;
	context.opts = opts;
	context.si = &si;

	struct limit_check max_limits[] = {
	  {.value_getter = total_proc_count, .limit = &opts->max_total_procs},
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

	struct limit_check min_limits[] = {
	  {.value_getter = available_ram_perc, .limit = &opts->min_avail_ram},
	  {.value_getter = free_ram_perc, .limit = &opts->min_free_ram},
	  {.value_getter = free_swap_perc, .limit = &opts->min_free_swap},
	  {.value_getter = network_speed, .limit = &opts->min_nw_speed}};

	for(size_t l = 0; l < sizeof(min_limits) / sizeof(min_limits[0]); ++l) {
		if(is_under_limit(&min_limits[l], &context)) {
			return true;
		}
	}

	return false;
}
//------------------------------------------------------------------------------
void print_current_value(struct check_context* ctx, struct limit_check* info) {
	if(ctx->opts->print_all_current
	   || (ctx->opts->print_current && info->limit->check)) {
		printf("atmost: current value of %s is %3.1f\n",
		  info->limit->description,
		  info->value_getter(ctx));
	}
}
//------------------------------------------------------------------------------
void print_current_values(struct options* opts) {
	if(opts->print_all_current || opts->print_current) {
		struct limit_check limits[] = {
		  {.value_getter = total_proc_count, .limit = &opts->max_total_procs},
		  {.value_getter = cpu_load1, .limit = &opts->max_cpu_load1},
		  {.value_getter = cpu_load5, .limit = &opts->max_cpu_load5},
		  {.value_getter = cpu_temperature, .limit = &opts->max_cpu_temp},
		  {.value_getter = gpu_temperature, .limit = &opts->max_gpu_temp},
		  {.value_getter = bat_temperature, .limit = &opts->max_bat_temp},
		  {.value_getter = io_ops_count, .limit = &opts->max_io_ops},
		  {.value_getter = available_ram_perc, .limit = &opts->min_avail_ram},
		  {.value_getter = free_ram_perc, .limit = &opts->min_free_ram},
		  {.value_getter = free_swap_perc, .limit = &opts->min_free_swap},
		  {.value_getter = network_speed, .limit = &opts->min_nw_speed}};

		struct sysinfo si;
		sysinfo(&si);

		struct check_context context;
		context.opts = opts;
		context.si = &si;

		for(size_t l = 0; l < sizeof(limits) / sizeof(limits[0]); ++l) {
			print_current_value(&context, &limits[l]);
		}
	}
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

			print_current_values(&opts);
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

		int sems = -1;
		if(opts->max_instances.check || opts->ipc_remove) {
			key_t ky = ftok(opts->path ? opts->path : executable, 0xA73057);
			sems = semget(ky, 1, 0666 | IPC_CREAT | IPC_EXCL);

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
		}

		if(opts->ipc_remove) {
			if(semctl(sems, 0, IPC_RMID) < 0) {
				perror("atmost: semctl failed: ");
				return 5;
			} else {
				return 0;
			}
		} else {
			if(opts->max_instances.check) {
				struct sembuf sb = {
				  .sem_num = 0, .sem_op = -1, .sem_flg = SEM_UNDO};

				if(semop(sems, &sb, 1) < 0) {
					perror("atmost: semop failed: ");
					return 5;
				}
			}

			while(is_overloaded(opts)) {
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
	opts->verbose = 0;
	opts->sep_arg = 0;
	opts->bat_tz_id = -1;
	opts->gpu_tz_id = -1;
	opts->cpu_tz_id = -1;
	opts->slow_network_speed = 1.f;

	for(int l = 0; l < (sizeof(opts->limits) / sizeof(opts->limits[0])); ++l) {
		struct resource_limit* limit = &opts->limits[l];
		limit->check = false;
		for(int m = 0; m < MODIFIER_COUNT; ++m) {
			limit->modifiers[m] = 0.f;
		}
	}

	opts->max_instances.description = "maximum concurrent instance count";
	opts->max_instances.value = 2;
	opts->max_bat_temp.description = "maximum battery temperature";
	opts->max_bat_temp.value = 60;
	opts->max_gpu_temp.description = "maximum GPU temperature";
	opts->max_gpu_temp.value = 80;
	opts->max_cpu_temp.description = "maximum CPU temperature";
	opts->max_cpu_temp.value = 80;
	opts->max_cpu_load1.description = "maximum 1 minute average CPU load";
	opts->max_cpu_load1.value = 30;
	opts->max_cpu_load5.description = "maximum 5 minutes average CPU load";
	opts->max_cpu_load5.value = 15;
	opts->min_avail_ram.description = "minimum available RAM percentage";
	opts->min_avail_ram.value = 20;
	opts->min_free_ram.description = "minimum free RAM percentage";
	opts->min_free_ram.value = 10;
	opts->min_free_swap.description = "minimum free swap space percentage";
	opts->min_free_swap.value = 50;
	opts->max_total_procs.description = "maximum number of running processes";
	opts->max_total_procs.value = 2000;
	opts->max_io_ops.description = "maximum number of I/O operations";
	opts->max_io_ops.value = 100;
	opts->min_nw_speed.description = "minimum network speed in Mb/s";
	opts->min_nw_speed.value = 10;

	opts->ipc_remove = false;
	opts->print_current = false;
	opts->print_all_current = false;
}
//------------------------------------------------------------------------------
static bool arg_is(const char* arg, const char* what) {
	return strcmp(arg, what) == 0;
}
//------------------------------------------------------------------------------
static bool parse_float_arg(int* a,
  int argc,
  const char** argv,
  const char* flag,
  const char* description,
  struct options* opts,
  float* value) {
	if(*a < argc) {
		if(arg_is(argv[*a], flag)) {
			if(argv[*a + 1]) {
				if(sscanf(argv[*a + 1], "%f", value)) {
					++(*a);
					if(opts->verbose) {
						printf("atmost: parsed value %3.1f for %s\n",
						  *value,
						  description);
					}
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
}
//------------------------------------------------------------------------------
static bool parse_limit_arg(int* a,
  int argc,
  const char** argv,
  const char* flag,
  struct options* opts,
  struct resource_limit* limit) {
	if(*a < argc) {
		if(strcmp(argv[*a], flag) == 0) {
			if(argv[*a + 1]) {
				if(sscanf(argv[*a + 1], "%f", &limit->value)) {
					limit->check = true;
					++(*a);
					if(opts->verbose) {
						printf("atmost: parsed value %3.1f for %s\n",
						  limit->value,
						  limit->description);
					}
				} else {
					fprintf(stderr,
					  "atmost: invalid %s value '%s' after %s\n",
					  limit->description,
					  argv[*a + 1],
					  argv[*a]);
					return false;
				}

				bool found_modifier;

				do {
					found_modifier = false;
					if(argv[*a + 1]) {
						for(int m = 0; m < MODIFIER_COUNT; ++m) {
							if(strcmp(argv[*a + 1], modifier_flags[m]) == 0) {
								if(argv[*a + 2]) {
									if(sscanf(argv[*a + 2],
										 "%f",
										 &limit->modifiers[m])) {
										++(*a);
										found_modifier = true;
										if(opts->verbose) {
											printf(
											  "atmost: parsed %s modifier "
											  "value %f for %s\n",
											  modifier_descriptions[m],
											  limit->modifiers[m],
											  limit->description);
										}
									} else {
										fprintf(stderr,
										  "atmost: invalid value '%s' after "
										  "%s\n",
										  argv[*a + 2],
										  argv[*a + 1]);
										return false;
									}
								} else {
									fprintf(stderr,
									  "atmost: missing modifier value after "
									  "%s\n",
									  argv[*a + 1]);
									return false;
								}
							}
						}
					}
				} while(found_modifier);
			} else {
				fprintf(stderr,
				  "atmost: missing %s value after %s\n",
				  limit->description,
				  argv[*a]);
				return false;
			}
			return true;
		}
	}
	return false;
}
//------------------------------------------------------------------------------
static void print_help();
//------------------------------------------------------------------------------
static int parse_args(int argc, const char** argv, struct options* opts) {
	for(int a = 1; a < argc; ++a) {
		if(arg_is(argv[a], "--")) {
			break;
		} else if((arg_is(argv[a], "-v")) || (arg_is(argv[a], "--verbose"))) {
			opts->verbose += 1;
		} else if((arg_is(argv[a], "-h")) || (arg_is(argv[a], "--help"))) {
			print_help();
			return 0;
		}
	}

	for(int a = 1; a < argc; ++a) {
		if(parse_limit_arg(&a, argc, argv, "-n", opts, &opts->max_instances)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-l", opts, &opts->max_cpu_load1)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-L", opts, &opts->max_cpu_load5)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-m", opts, &opts->min_avail_ram)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-M", opts, &opts->min_free_ram)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-S", opts, &opts->min_free_swap)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-p", opts, &opts->max_total_procs)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-tc", opts, &opts->max_cpu_temp)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-tg", opts, &opts->max_gpu_temp)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-tb", opts, &opts->max_bat_temp)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-io", opts, &opts->max_io_ops)) {
		} else if(parse_limit_arg(
					&a, argc, argv, "-nw", opts, &opts->min_nw_speed)) {
		} else if(parse_float_arg(&a,
					argc,
					argv,
					"-snw",
					"slow network speed",
					opts,
					&opts->slow_network_speed)) {
		} else if(arg_is(argv[a], "-f")) {
			if(argv[a + 1]) {
				opts->path = argv[a + 1];
				if(!is_file(opts->path)) {
					fprintf(stderr,
					  "atmost: invalid token file path '%s' after -f\n",
					  argv[a + 1]);
					return 1;
				}
			} else {
				fprintf(stderr, "atmost: missing token file path after -f\n");
				return 1;
			}
			++a;
		} else if(arg_is(argv[a], "-r")) {
			opts->ipc_remove = true;
		} else if(arg_is(argv[a], "-c")) {
			opts->print_current = true;
		} else if(arg_is(argv[a], "-C")) {
			opts->print_all_current = true;
		}

		if(arg_is(argv[a], "--")) {
			if(opts->sep_arg < 1) {
				opts->sep_arg = a;
				break;
			}
		}
	}
	return 0;
}
//------------------------------------------------------------------------------
static void print_help();
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
static bool runs_on_battery(struct options* opts) {
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
static bool slow_network_conn(struct options* opts) {
	struct check_context context;
	context.opts = opts;
	return network_speed(&context) <= opts->slow_network_speed;
}
//------------------------------------------------------------------------------

static bool no_network_conn(struct options* opts) {
	struct check_context context;
	context.opts = opts;
	return network_speed(&context) <= 0.f;
}
//------------------------------------------------------------------------------
static float total_proc_count(struct check_context* ctx) {
	return (float)ctx->si->procs;
}
//------------------------------------------------------------------------------
static float available_ram_perc(struct check_context* ctx) {
	FILE* file = fopen("/proc/meminfo", "rt");
	if(file) {
		char buffer[1024];
		bool has_total = false;
		bool has_avail = false;
		float total = 1.f;
		float avail = 1.f;
		while(
		  !(has_total && has_avail) && fgets(buffer, sizeof(buffer), file)) {
			if(sscanf(buffer, "MemTotal:%f", &total)) {
				has_total = true;
			} else if(sscanf(buffer, "MemAvailable:%f", &avail)) {
				has_avail = true;
			}
		}
		fclose(file);
		if(has_total && has_avail) {
			if(total > 0.f) {
				return 100.f * avail / total;
			}
		}
	}
	return 100.f;
}
//------------------------------------------------------------------------------
static float free_ram_perc(struct check_context* ctx) {
	return 100.f * (((float)ctx->si->freeram) / ((float)ctx->si->totalram));
}
//------------------------------------------------------------------------------
static float free_swap_perc(struct check_context* ctx) {
	return 100.f * (((float)ctx->si->freeswap) / ((float)ctx->si->totalswap));
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
static float network_speed(struct check_context* ctx) {
	float total = 0.f;
	struct ifaddrs *addrs, *addr;
	getifaddrs(&addrs);
	addr = addrs;
	while(addr) {
		if(addr->ifa_addr && addr->ifa_addr->sa_family == AF_PACKET) {
			if((addr->ifa_flags & IFF_LOOPBACK) != IFF_LOOPBACK) {
				if((addr->ifa_flags & IFF_RUNNING) == IFF_RUNNING) {
					if((addr->ifa_flags & IFF_UP) == IFF_UP) {
						char buffer[PATH_MAX];
						snprintf(buffer,
						  PATH_MAX,
						  "/sys/class/net/%s/speed",
						  addr->ifa_name);
						FILE* file = fopen(buffer, "rt");
						if(file) {
							float speed = 0.f;
							if(fscanf(file, "%f", &speed)) {
								total += speed;
							}
							fclose(file);
						}
					}
				}
			}
		}
		addr = addr->ifa_next;
	}
	freeifaddrs(addrs);
	return total;
}
//------------------------------------------------------------------------------
static void print_help() {

#include "atmost.inl"
	int input_pipe[2];
	if(pipe(input_pipe) < 0) {
		perror("atmost: pipe failed: ");
		return;
	}

	int pid = fork();
	if(pid < 0) {
		perror("atmost: fork failed: ");
		return;
	}

	if(pid > 0) {
		close(input_pipe[0]);
		write(input_pipe[1], _res_atmost, sizeof(_res_atmost));
		close(input_pipe[1]);
		waitpid(pid, NULL, 0);
	} else {
		close(input_pipe[1]);
		dup2(input_pipe[0], 0);
		execlp("man", "man", "-l", "-", NULL);
	}
}
//------------------------------------------------------------------------------

