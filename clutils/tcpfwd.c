/* Copyright (c) 2016 Matus Chochlik
 */
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <fcntl.h>
#include <signal.h>
#include <string.h>
#include <assert.h>

// program_state
struct program_state 
{
	fd_set active_fds;
	fd_set client_fds;
	const char* input_path;
	const char* output_path;
	int input;
	int output;
	int server;
	int port_no;
	int num_clients;
	int max_clients;
	int max_fds;
	int verbosity;
	int keep_running;
} state = {
	.input_path = "-",
	.output_path = "-",
	.input = 0,
	.output = 1,
	.server = -1,
	.port_no = 10281,
	.num_clients = 0,
	.max_clients = 2,
	.max_fds = FD_SETSIZE,
	.verbosity = 0,
	.keep_running = 1
};

int parse_arguments(int argc, const char** argv);
int initialize(void);
int run(void);
void discontinue(void);
int cleanup(void);
void on_interrupt(int signum);
void print_state(FILE*);

// main
int main(int argc, const char** argv)
{
	int err = 0;

	if((err = parse_arguments(argc, argv)))
	{
		discontinue();
	}

	if(state.keep_running)
	{
		if((err = initialize()) == 0)
		{
			if(state.verbosity > 1)
			{
				print_state(stderr);
			}
			err = run();
		}

	}

	err = cleanup();

	if(state.verbosity > 1)
	{
		fprintf(stderr, "Done. Code `%d`\n", err);
	}

	return err;
}

int init_server_socket(void);
int accept_client(void);
int disconnect_client(int fd);

int handle_read(int fd);
int handle_except(int fd);

// run
int run(void)
{
	if(state.verbosity > 2)
	{
		fprintf(stderr, "Starting loop\n");
	}

	int res;
	fd_set read_fds, except_fds;

	struct timespec timeout = {
		.tv_sec = 1,
		.tv_nsec = 0
	};

	while(state.keep_running)
	{
		if(state.verbosity > 6)
		{
			fprintf(stderr, "Waiting for input\n");
		}
		read_fds = state.active_fds;
		except_fds = state.active_fds;
		res = pselect(state.max_fds, &read_fds, NULL, &except_fds, &timeout, NULL);
		if(res < 0)
		{
			perror("Select");
			discontinue();
			return 4;
		}
		else if(res > 0)
		{
			int fd;
			for(fd=0; fd<state.max_fds; ++fd)
			{
				if(FD_ISSET(fd, &read_fds))
				{
					handle_read(fd);
				}
				if(FD_ISSET(fd, &except_fds))
				{
					handle_except(fd);
				}
			}
		}
		else if(state.verbosity > 6)
		{
			fprintf(stderr, "Timed-out\n");
		}
	}

	return 0;
}

// read_nohang
ssize_t read_nohang(int fd, char* buffer, size_t size)
{
	struct timespec timeout = {
		.tv_sec = 0,
		.tv_nsec = 10000000
	};
	fd_set fds;
	FD_ZERO(&fds);
	FD_SET(fd, &fds);
	int res = pselect(state.max_fds, &fds, NULL, NULL, &timeout, NULL);
	if(res < 0)
	{
		perror("Select");
		return res;
	}
	else if(res > 0)
	{
		assert(FD_ISSET(fd, &fds));
		if(state.verbosity > 3)
		{
			fprintf(stderr, "Reading from FD `%d`\n", fd);
		}
		ssize_t done = read(fd, buffer, size);
		if(state.verbosity > 2)
		{
			fprintf(stderr, "Read `%ld` bytes from FD `%d`\n", done, fd);
		}

		return done;
	}
	return 0;
}

void send_to_clients(const char* buffer, size_t size)
{
	int fd;
	for(fd=0; fd<state.max_fds; ++fd)
	{
		if(FD_ISSET(fd, &state.client_fds))
		{
			if(state.verbosity > 3)
			{
				fprintf(stderr, "Writing `%lu` bytes to FD `%d`\n", size, fd);
			}
			write(fd, buffer, size);
		}
	}
}

// handle_read
int handle_read(int fd)
{
	if(fd == state.server)
	{
		// new client
		accept_client();
	}
	else if(fd == state.input)
	{
		// input -> clients
		char buffer[BUFSIZ];
		
		ssize_t done = read_nohang(fd, buffer, BUFSIZ);
		if(done > 0)
		{
			send_to_clients(buffer, done);
			while((done = read_nohang(fd, buffer, BUFSIZ)) > 0)
			{
				send_to_clients(buffer, done);
			}
		}
		else
		{
			discontinue();
		}
	}
	else
	{
		// client -> output
		assert(fd != state.output);
		char buffer[BUFSIZ];
		
		ssize_t done = read_nohang(fd, buffer, BUFSIZ);
		if(done > 0)
		{
			write(state.output, buffer, done);
			while((done = read_nohang(fd, buffer, BUFSIZ)) > 0)
			{
				write(state.output, buffer, done);
			}
		}
		else
		{
			disconnect_client(fd);
		}
	}

	return 0;
}

// handle_except
int handle_except(int fd)
{
	return disconnect_client(fd);
}

// initialize
int initialize(void)
{
	int tmp = 0;

	if(state.verbosity > 4)
	{
		fprintf(stderr, "Setting up signal handlers\n");
	}

	if(signal(SIGINT, &on_interrupt) == SIG_ERR)
	{
		perror("Signal");
		return 1;
	}
	if(signal(SIGTERM, &on_interrupt) == SIG_ERR)
	{
		perror("Signal");
		return 1;
	}

	if((strcmp(state.input_path, "-")!=0) && (strlen(state.input_path)>0))
	{
		if(state.verbosity > 4)
		{
			fprintf(
				stderr,
				"Opening input file '%s'\n",
				state.input_path
			);
		}
		if((tmp = open(state.input_path, O_EXCL)) < 0)
		{
			perror(state.input_path);
			return 2;
		}
		state.input = tmp;
	}

	if((strcmp(state.output_path, "-")!=0) && (strlen(state.output_path)>0))
	{
		if(state.verbosity > 4)
		{
			fprintf(
				stderr,
				"Opening output file '%s'\n",
				state.output_path
			);
		}
		if((tmp = open(state.output_path, O_CREAT|O_EXCL, 0600)) < 0)
		{
			perror(state.output_path);
			return 3;
		}
		state.output = tmp;
	}

	if((tmp = init_server_socket()))
	{
		return tmp;
	}

	const int extra_nfd = 6; // 0+1+2+i+o+s

	if(state.max_clients > FD_SETSIZE-extra_nfd)
	{
		state.max_clients = FD_SETSIZE-extra_nfd;
	}

	if(state.max_fds > state.max_clients+extra_nfd)
	{
		state.max_fds = state.max_clients+extra_nfd;
	}

	FD_ZERO(&state.active_fds);
	FD_SET(state.server, &state.active_fds);
	FD_SET(state.input, &state.active_fds);

	return 0;
}

// cleanup
int cleanup(void)
{
	if(state.input >= 0)
	{
		if(state.verbosity > 5)
		{
			fprintf(
				stderr,
				"Closing input FD `%d`\n",
				state.input
			);
		}
		close(state.input);
	}
	if(state.output >= 0)
	{
		if(state.verbosity > 5)
		{
			fprintf(
				stderr,
				"Closing output FD `%d`\n",
				state.output

			);
		}
		close(state.output);
	}
	if(state.server >= 0)
	{
		if(state.verbosity > 5)
		{
			fprintf(
				stderr,
				"Closing server FD `%d`\n",
				state.server

			);
		}
		close(state.server);
	}

	return 0;
}

int init_server_socket_in(void);
int accept_client_in(void);

int init_server_socket(void)
{
	return init_server_socket_in();
}

int accept_client(void)
{
	return accept_client_in();
}

int disconnect_client(int fd)
{
	if(state.verbosity > 3)
	{
		fprintf(
			stderr,
			"Disconnecting client FD `%d`\n",
			fd

		);
	}
	state.num_clients--;
	if(state.verbosity > 4)
	{
		fprintf(
			stderr,
			"Currently serving `%d` clients (`%d` max)\n",
			state.num_clients,
			state.max_clients
		);
	}
	FD_CLR(fd, &state.active_fds);
	FD_CLR(fd, &state.client_fds);
	return close(fd);
}

// init_server_socket_in
int init_server_socket_in(void)
{
	if(state.verbosity > 4)
	{
		fprintf(stderr, "Creating TCP/IPv4 socket\n");
	}

	int sock = socket(AF_INET, SOCK_STREAM, 0);

	if(sock < 0)
	{
		perror("Socket");
	}
	else
	{
		struct sockaddr_in addr;
		bzero(&addr, sizeof(addr));
		addr.sin_family = AF_INET;
		addr.sin_port = htons(state.port_no);
		addr.sin_addr.s_addr = htonl(INADDR_ANY);

		if(state.verbosity > 3)
		{
			fprintf(
				stderr,
				"Binding socket to port `%d`\n",
				state.port_no
			);
		}

		if(bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0)
		{
			perror("Bind");
			close(sock);
			sock = -1;
		}
		else if(listen(sock, state.max_clients) < 0)
		{
			perror("Listen");
			close(sock);
			sock = -1;
		}
	}

	if(sock < 0)
	{
		return 1;
	}

	state.server = sock;
	return 0;
}

// accept_client_in
int accept_client_in(void)
{
	struct sockaddr_in addr;
	socklen_t alen = sizeof(addr);

	if(state.verbosity > 4)
	{
		fprintf(stderr, "Accepting TCP/IPv4 client connection\n");
	}

	int client = accept(state.server, (struct sockaddr*)&addr, &alen);
	if(client < 0)
	{
		perror("Accept");
	}
	else
	{
		if(state.num_clients < state.max_clients)
		{
			state.num_clients++;
			FD_SET(client, &state.active_fds);
			FD_SET(client, &state.client_fds);

			if(state.verbosity > 3)
			{
				fprintf(
					stderr,
					"Accepted client connection fd `%d`\n",
					client
				);
			}
			if(state.verbosity > 4)
			{
				fprintf(
					stderr,
					"Currently serving `%d` clients (`%d` max)\n",
					state.num_clients,
					state.max_clients
				);
			}
		}
		else
		{
			if(state.verbosity > 4)
			{
				fprintf(
					stderr,
					"Too many client connections `%d`\n",
					state.num_clients
				);
			}
			close(client);
			if(state.verbosity > 3)
			{
				fprintf(
					stderr,
					"Refused client connection fd `%d`\n",
					client
				);
			}
			client = -1;
		}
	}
	return client;
}

void print_usage(FILE* output);

const char* parse_string(
	int* arg,
	int argc, const char** argv,
	int opos, const char* sopt, const char* lopt
);

int parse_num(
	int* arg,
	int argc, const char** argv,
	int opos, const char* sopt, const char* lopt
);

int parse_opt(
	int* arg,
	int argc, const char** argv,
	int opos, const char* sopt, const char* lopt
);

// parse_argument
int parse_arguments(int argc, const char** argv)
{
	int arg = 1;
	int ofs = 0;
	while(arg < argc)
	{
		const char* tmp_str = argv[arg];
		int tmp_int = -1;

		if(strcmp(tmp_str, "-h") == 0 || strcmp(tmp_str, "--help") == 0)
		{
			print_usage(stdout);
			discontinue();
			break;
		}
		else if((tmp_str = parse_string(&arg,argc,argv, ofs+1,"i","input")))
		{
			state.input_path = tmp_str;
		} 
		else if((tmp_str = parse_string(&arg,argc,argv, ofs+2,"o","output")))
		{
			state.output_path = tmp_str;
		} 
		else if((tmp_int = parse_num(&arg,argc,argv, ofs+3,"p","port")) > 0)
		{
			state.port_no = tmp_int;
		} 
		else if((tmp_int = parse_num(&arg,argc,argv, ofs+4,"m","max-clients")) > 0)
		{
			state.max_clients = tmp_int;
		} 
		else if((tmp_int = parse_num(&arg,argc,argv, -1,"V","verbosity")) > 0)
		{
			state.verbosity += tmp_int;
			fprintf(
				stderr,
				"Increasing verbosity by `%d`, to: `%d`\n",
				tmp_int,
				state.verbosity
			);
		} 
		else if(parse_opt(&arg,argc,argv, -1,"v","verbose") == 0)
		{
			state.verbosity++;
			ofs++;
			fprintf(
				stderr,
				"Incrementing verbosity to: `%d`\n",
				state.verbosity
			);
		} 
		else
		{
			fprintf(
				stderr,
				"Invalid option '%s' specified\n",
				argv[arg]
			);
			print_usage(stderr);
			return 1;
		}
		++arg;
	}

	return 0;
}

const char* get_arg_value_str(
	int* arg,
	int argc, const char** argv,
	int opos, const char* stag, const char* ltag
);

// parse_string
const char* parse_string(
	int* arg,
	int argc, const char** argv,
	int opos, const char* stag, const char* ltag
)
{
	return get_arg_value_str(arg, argc, argv, opos, stag, ltag);
}

// parse_num
int parse_num(
	int* arg,
	int argc, const char** argv,
	int opos, const char* stag, const char* ltag
)
{
	const char* tmp_str = NULL;
	if((tmp_str = get_arg_value_str(arg, argc, argv, opos, stag, ltag)))
	{
		return atoi(tmp_str);
	}
	return 0;
}

const char* parse_arg_tag(
	int* arg,
	int argc, const char** argv,
	const char* stag, const char* ltag, const char* vsep
);

// parse_opt
int parse_opt(
	int* arg,
	int argc, const char** argv,
	int opos, const char* stag, const char* ltag
)
{
	const char* tmp_str = NULL;

	if((tmp_str = parse_arg_tag(arg, argc, argv, stag, ltag, "")))
	{
		return strlen(tmp_str);
	}
	return 1;
}

// get_arg_value_str
const char* get_arg_value_str(
	int* arg,
	int argc, const char** argv,
	int opos, const char* stag, const char* ltag
)
{
	const char* tmp_str = NULL;

	if((tmp_str = parse_arg_tag(arg, argc, argv, stag, ltag, "=")))
	{
		if(strlen(tmp_str) > 0)
		{
			return tmp_str;
		}
		else
		{
			fprintf(
				stderr,
				"Missing value after '%s'\n",
				tmp_str
			);
		}
	}
	else if((*arg == opos) && (argv[*arg][0] != '-'))
	{
		return argv[*arg];
	}
	return NULL;
}

// do_parse_arg_tag
const char* do_parse_arg_tag(
	int* arg,
	int argc, const char** argv,
	int plen, const char* pfx, const char* tag, const char* vsep
)
{
	const char* tmp_str = argv[*arg];

	if(strncmp(tmp_str, pfx, plen) == 0)
	{
		int tlen = strlen(tag);
		if(strncmp(tmp_str+plen, tag, tlen) == 0)
		{
			int slen = strlen(vsep);
			if(strncmp(tmp_str+plen+tlen, vsep, slen) == 0)
			{
				return tmp_str+plen+tlen+slen;
			}
			else if(strlen(tmp_str+plen+tlen) == 0)
			{
				if((*arg)+1 < argc)
				{
					++(*arg);
					return argv[*arg];
				}
			}
		}
	}
	return NULL;
}

// parse_arg_tag
const char* parse_arg_tag(
	int* arg,
	int argc, const char** argv,
	const char* stag, const char* ltag, const char* vsep
)
{
	const char* tmp_str = NULL;
	if((tmp_str = do_parse_arg_tag(arg,argc,argv, 2,"--", ltag, vsep)))
	{
		return tmp_str;
	}
	else if((tmp_str = do_parse_arg_tag(arg,argc,argv, 1,"-", stag, vsep)))
	{
		return tmp_str;
	}
	else if((tmp_str = do_parse_arg_tag(arg,argc,argv, 1,"-", stag, "")))
	{
		return tmp_str;
	}
	return NULL;
}

// print_usage
void print_usage(FILE* output)
{
	fprintf(
		output,
		"Usage: tcptty "
		"[-h|--help]|"
		"[[-i|--input][=]input-path] "
		"[[-o|--output][=]output-path]"
		"[[-p|--port][=]port-number]"
		"[[-m|--max-clients][=]number]"
		"\n"
	);
}

// print_state
void print_state(FILE* output)
{
	fprintf(output, "InputPath:  '%s'\n", state.input_path);
	fprintf(output, "OutputPath: '%s'\n", state.output_path);
	fprintf(output, "InputFD:  `%d %s`\n", state.input, (state.input==0?"(stdin)":""));
	fprintf(output, "OutputFD: `%d %s`\n", state.output, (state.output==1?"(stdout)":""));
	fprintf(output, "ServerFD: `%d`\n", state.server);
	fprintf(output, "PortNumber: `%d`\n", state.port_no);
	fprintf(output, "MaxClients: `%d`\n", state.max_clients);
	fprintf(output, "MaxFDs: `%d`\n", state.max_fds);
}

// on_interrupt
void on_interrupt(int signum)
{
	state.keep_running = 0;
}

void discontinue(void)
{
	if(state.verbosity > 2)
	{
		fprintf(stderr, "Discontinuing execution\n");
		state.keep_running = 0;
	}
}
