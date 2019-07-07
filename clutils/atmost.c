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
#include <sys/types.h>
#include <unistd.h>

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

static bool is_executable(const char* path) {
	struct stat sb;
	return (stat(path, &sb) == 0) && (sb.st_mode & S_IXUSR);
}

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

static const char* canonical_path(const char* arg) {
	static char temp[PATH_MAX] = {'\0'};

	return realpath(which(arg), temp);
}

struct options {
	int sep_arg;
	int max_count;
};

union atmost_semun {
	int val;
};

static int execute(struct options opts, int argc, const char** argv) {
	const char* executable = canonical_path(argv[0]);
	if(strlen(executable) > 0) {

		key_t ky = ftok(executable, 0xA73057);
		int sems = semget(ky, 1, 0666 | IPC_CREAT | IPC_EXCL);

		if(sems < 0) {
			sems = semget(ky, 1, 0);
			if(sems < 0) {
				perror("atmost: ");
				return 3;
			}
		} else {
			union atmost_semun su = {.val = opts.max_count};
			if(semctl(sems, 0, SETVAL, su) < 0) {
				perror("atmost: ");
				return 4;
			}
		}

		struct sembuf sb = {.sem_num = 0, .sem_op = -1, .sem_flg = SEM_UNDO};

		if(semop(sems, &sb, 1) < 0) {
			perror("atmost: ");
			return 5;
		}

		return execv(argv[0], (char* const*)argv);
	}
	fprintf(stderr, "atmost: could not find executable '%s'\n", argv[0]);
	return 2;
}

int main(int argc, const char** argv) {
	if(argc > 1) {
		struct options opts = {.sep_arg = 0, .max_count = 1};

		for(int a = 1; a < argc; ++a) {
			if(strcmp(argv[a], "-n") == 0) {
				if(argv[a + 1]) {
					opts.max_count = atoi(argv[a + 1]);
					if(opts.max_count < 0) {
						fprintf(stderr,
						  "atmost: invalid max count '%s'\n",
						  argv[a + 1]);
						return 1;
					}
				} else {
					fprintf(stderr, "atmost: missing max count value\n");
					return 1;
				}
				++a;
			} else if(strcmp(argv[a], "--") == 0) {
				opts.sep_arg = a;
			}
		}
		if(opts.sep_arg > 0 && opts.sep_arg + 1 < argc) {
			return execute(
			  opts, argc - opts.sep_arg - 1, argv + opts.sep_arg + 1);
		}
	}
	return 0;
}
