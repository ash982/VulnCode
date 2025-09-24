# CGI Programs in C++

This project contains example CGI programs written in C++.

## Structure

- `src/` - Source code files
- `bin/` - Compiled executables
- `config/` - Web server configuration
- `docs/` - Documentation
- `Makefile` - Build configuration
- `install.sh` - Installation script

## Programs

### hello.cpp
Simple CGI program that displays request information and a basic form.

### form_handler.cpp
Advanced CGI program with form processing capabilities, handles both GET and POST requests.

## Building

### Manual compilation:
```bash
make compile
```

### Install to web server:
```bash
sudo ./install.sh install
```

### Test locally:
```bash
./install.sh test
```

## Requirements

- g++ compiler with C++11 support
- Web server with CGI support (Apache, Nginx, etc.)
- Appropriate permissions for CGI directory

## Usage

After installation, access the programs via:
- http://your-server/cgi-bin/hello
- http://your-server/cgi-bin/form_handler

## Web Server Setup

For Apache, ensure CGI module is enabled and include the configuration from `config/apache.conf`.

For Nginx, configure CGI support with fcgiwrap or similar.
```

To set up the project structure:

```bash
mkdir -p cgi-project/{src,bin,docs,config}
```

```bash
cd cgi-project
```

```bash
chmod +x install.sh
```

```bash
./install.sh compile
