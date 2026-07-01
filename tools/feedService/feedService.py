#!/usr/bin/python3

# feedService - Domain & IP feed automation for BIG-IP
# Version: 1.0.0
# Last Modified: June 30, 2026
# Author: Regan Anderson, F5 Inc.
# Portions of this script were adopted from the great work in sslo_o365_update
# (https://github.com/f5devcentral/sslo-o365-update/)
#
#-----------------------------------------------------------------------
# This sample software is provided for illustrative purposes only and is
# supplied "AS IS" without warranties or support of any kind, express or
# implied.
#
# The author assumes no responsibility or liability for the use of this
# software and conveys no license or rights under any patent, copyright,
# mask work right, or other intellectual property except as may be stated
# in the applicable license.
#
# Portions of this script were adapted from the project referenced above.
# Any use or redistribution should preserve any attribution, notices, and
# license terms required by the original source.
#
# This script should be reviewed, tested, and modified as needed before it
# is used in any production or customer environment.
#-----------------------------------------------------------------------

import json, base64, os, fnmatch, re, ipaddress, time, datetime, sys, ssl, hashlib, argparse, csv, http.client, io
import subprocess as shell
from urllib import request as urlrequest
from urllib import parse as urlparse


class TLSOverTLSSocket:

    ##-----------------------------------------------------------------------
    ## Init function
    ##  Purpose: initialize a TLS-over-TLS wrapper around an existing transport socket
    ##  Parameters:
    ##      transport_socket = underlying connected socket
    ##      context          = SSL context for the nested TLS session
    ##      server_hostname  = hostname to use for SNI and certificate validation
    ##-----------------------------------------------------------------------
    def __init__(self, transport_socket, context, server_hostname):
        self._transport_socket = transport_socket
        self._incoming = ssl.MemoryBIO()
        self._outgoing = ssl.MemoryBIO()
        self._ssl_object = context.wrap_bio(self._incoming, self._outgoing, server_hostname=server_hostname)

    ##-----------------------------------------------------------------------
    ## _flush_outgoing function
    ##  Purpose: write pending encrypted TLS bytes from the outgoing BIO to the transport socket
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def _flush_outgoing(self):
        while True:
            encrypted_data = self._outgoing.read()
            if not encrypted_data:
                break
            self._transport_socket.sendall(encrypted_data)

    ##-----------------------------------------------------------------------
    ## _recv_into_incoming function
    ##  Purpose: read encrypted bytes from the transport socket into the incoming BIO
    ##  Parameters: None
    ##  Returns:
    ##      boolean         = True when data was received, False on EOF
    ##-----------------------------------------------------------------------
    def _recv_into_incoming(self):
        encrypted_data = self._transport_socket.recv(16384)
        if not encrypted_data:
            self._incoming.write_eof()
            return False
        self._incoming.write(encrypted_data)
        return True

    ##-----------------------------------------------------------------------
    ## do_handshake function
    ##  Purpose: complete the nested TLS handshake over the wrapped transport socket
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def do_handshake(self):
        while True:
            try:
                self._ssl_object.do_handshake()
                self._flush_outgoing()
                return
            except ssl.SSLWantWriteError:
                self._flush_outgoing()
            except ssl.SSLWantReadError:
                self._flush_outgoing()
                if not self._recv_into_incoming():
                    raise OSError("Nested TLS handshake failed: unexpected EOF.")

    ##-----------------------------------------------------------------------
    ## send function
    ##  Purpose: send plaintext bytes through the nested TLS session
    ##  Parameters:
    ##      data            = plaintext bytes to send
    ##  Returns:
    ##      integer         = number of plaintext bytes written
    ##-----------------------------------------------------------------------
    def send(self, data):
        while True:
            try:
                bytes_sent = self._ssl_object.write(data)
                self._flush_outgoing()
                return bytes_sent
            except ssl.SSLWantWriteError:
                self._flush_outgoing()
            except ssl.SSLWantReadError:
                self._flush_outgoing()
                if not self._recv_into_incoming():
                    raise OSError("Nested TLS write failed: unexpected EOF.")

    ##-----------------------------------------------------------------------
    ## sendall function
    ##  Purpose: send all supplied plaintext bytes through the nested TLS session
    ##  Parameters:
    ##      data            = plaintext bytes to send
    ##-----------------------------------------------------------------------
    def sendall(self, data):
        total_sent = 0
        data_len = len(data)
        while total_sent < data_len:
            bytes_sent = self.send(data[total_sent:])
            if bytes_sent <= 0:
                raise OSError("Nested TLS write failed: zero bytes sent.")
            total_sent += bytes_sent

    ##-----------------------------------------------------------------------
    ## recv function
    ##  Purpose: receive plaintext bytes from the nested TLS session
    ##  Parameters:
    ##      bufsize         = maximum number of plaintext bytes to read
    ##  Returns:
    ##      bytes           = plaintext bytes read from the TLS session
    ##-----------------------------------------------------------------------
    def recv(self, bufsize):
        while True:
            try:
                return self._ssl_object.read(bufsize)
            except ssl.SSLWantReadError:
                self._flush_outgoing()
                if not self._recv_into_incoming():
                    return b""
            except ssl.SSLWantWriteError:
                self._flush_outgoing()

    ##-----------------------------------------------------------------------
    ## recv_into function
    ##  Purpose: read plaintext bytes from the nested TLS session into a caller buffer
    ##  Parameters:
    ##      buffer          = destination buffer
    ##      nbytes          = optional maximum number of bytes to read
    ##  Returns:
    ##      integer         = number of bytes copied into the buffer
    ##-----------------------------------------------------------------------
    def recv_into(self, buffer, nbytes=0):
        if nbytes <= 0:
            nbytes = len(buffer)
        data = self.recv(nbytes)
        data_len = len(data)
        buffer[:data_len] = data
        return data_len

    ##-----------------------------------------------------------------------
    ## makefile function
    ##  Purpose: expose a buffered file-like interface over the nested TLS session
    ##  Parameters:
    ##      mode            = file mode string
    ##      buffering       = optional buffer size
    ##  Returns:
    ##      object          = file-like wrapper around the TLS session
    ##-----------------------------------------------------------------------
    def makefile(self, mode="r", buffering=None):
        if buffering is None:
            buffering = io.DEFAULT_BUFFER_SIZE

        raw_io = TLSOverTLSRawIO(self, mode)
        if "r" in mode and "w" in mode:
            return io.BufferedRWPair(raw_io, raw_io, buffering)
        if "r" in mode:
            return io.BufferedReader(raw_io, buffering)
        if "w" in mode:
            return io.BufferedWriter(raw_io, buffering)
        return raw_io

    ##-----------------------------------------------------------------------
    ## settimeout function
    ##  Purpose: set the timeout on the underlying transport socket
    ##  Parameters:
    ##      value           = socket timeout value
    ##-----------------------------------------------------------------------
    def settimeout(self, value):
        self._transport_socket.settimeout(value)

    ##-----------------------------------------------------------------------
    ## gettimeout function
    ##  Purpose: get the timeout from the underlying transport socket
    ##  Parameters: None
    ##  Returns:
    ##      object          = current socket timeout value
    ##-----------------------------------------------------------------------
    def gettimeout(self):
        return self._transport_socket.gettimeout()

    ##-----------------------------------------------------------------------
    ## fileno function
    ##  Purpose: return the file descriptor of the underlying transport socket
    ##  Parameters: None
    ##  Returns:
    ##      integer         = socket file descriptor
    ##-----------------------------------------------------------------------
    def fileno(self):
        return self._transport_socket.fileno()

    ##-----------------------------------------------------------------------
    ## close function
    ##  Purpose: close the nested TLS session and underlying transport socket
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def close(self):
        try:
            self._ssl_object.unwrap()
            self._flush_outgoing()
        except Exception:
            pass
        self._transport_socket.close()


class TLSOverTLSRawIO(io.RawIOBase):

    ##-----------------------------------------------------------------------
    ## Init function
    ##  Purpose: initialize a raw I/O adapter over a TLSOverTLSSocket instance
    ##  Parameters:
    ##      tls_socket      = TLSOverTLSSocket instance to wrap
    ##      mode            = file mode string
    ##-----------------------------------------------------------------------
    def __init__(self, tls_socket, mode):
        super().__init__()
        self._tls_socket = tls_socket
        self._mode = mode
        self._closed = False

    ##-----------------------------------------------------------------------
    ## readable function
    ##  Purpose: report whether the wrapped stream supports reads
    ##  Parameters: None
    ##  Returns:
    ##      boolean         = True when the mode allows reading
    ##-----------------------------------------------------------------------
    def readable(self):
        return "r" in self._mode

    ##-----------------------------------------------------------------------
    ## writable function
    ##  Purpose: report whether the wrapped stream supports writes
    ##  Parameters: None
    ##  Returns:
    ##      boolean         = True when the mode allows writing
    ##-----------------------------------------------------------------------
    def writable(self):
        return "w" in self._mode

    ##-----------------------------------------------------------------------
    ## readinto function
    ##  Purpose: read bytes from the TLS socket into a supplied buffer
    ##  Parameters:
    ##      b               = destination buffer
    ##  Returns:
    ##      integer         = number of bytes copied into the buffer
    ##-----------------------------------------------------------------------
    def readinto(self, b):
        if self._closed:
            return 0
        if not self.readable():
            raise OSError("Stream is not readable")

        data = self._tls_socket.recv(len(b))
        if not data:
            return 0

        data_len = len(data)
        b[:data_len] = data
        return data_len

    ##-----------------------------------------------------------------------
    ## write function
    ##  Purpose: write bytes to the wrapped TLS socket
    ##  Parameters:
    ##      b               = bytes-like object to write
    ##  Returns:
    ##      integer         = number of bytes written
    ##-----------------------------------------------------------------------
    def write(self, b):
        if self._closed:
            raise OSError("I/O operation on closed stream")
        if not self.writable():
            raise OSError("Stream is not writable")

        data = bytes(b)
        self._tls_socket.sendall(data)
        return len(data)

    ##-----------------------------------------------------------------------
    ## fileno function
    ##  Purpose: return the file descriptor of the wrapped TLS socket
    ##  Parameters: None
    ##  Returns:
    ##      integer         = socket file descriptor
    ##-----------------------------------------------------------------------
    def fileno(self):
        return self._tls_socket.fileno()

    ##-----------------------------------------------------------------------
    ## close function
    ##  Purpose: mark the raw I/O wrapper as closed
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def close(self):
        if not self._closed:
            self._closed = True
        super().close()


class HTTPSProxyTunnelConnection(http.client.HTTPSConnection):

    ##-----------------------------------------------------------------------
    ## Init function
    ##  Purpose: initialize an HTTPS connection that can establish CONNECT tunnels through an HTTPS proxy
    ##  Parameters:
    ##      host            = proxy hostname
    ##      port            = proxy port
    ##      timeout         = connection timeout
    ##      source_address  = optional local bind address
    ##      context         = SSL context for the origin connection
    ##      proxy_context   = SSL context for the proxy connection
    ##-----------------------------------------------------------------------
    def __init__(self, host, port=None, timeout=None, source_address=None, context=None, proxy_context=None):
        super().__init__(host, port=port, timeout=timeout, source_address=source_address, context=context)
        self._proxy_context = proxy_context if proxy_context is not None else context

    ##-----------------------------------------------------------------------
    ## _send_https_tunnel function
    ##  Purpose: send a CONNECT request across the HTTPS proxy and validate the proxy response
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def _send_https_tunnel(self):
        tunnel_host = self._tunnel_host
        tunnel_port = self._tunnel_port
        if tunnel_port is None:
            tunnel_port = 443

        connect_target = f"{tunnel_host}:{tunnel_port}"
        tunnel_headers = dict(getattr(self, "_tunnel_headers", {}) or {})

        if not any(str(header).lower() == "host" for header in tunnel_headers):
            tunnel_headers["Host"] = connect_target
        if not any(str(header).lower() == "proxy-connection" for header in tunnel_headers):
            tunnel_headers["Proxy-Connection"] = "Keep-Alive"

        connect_lines = [f"CONNECT {connect_target} HTTP/1.1"]
        for header_name, header_value in tunnel_headers.items():
            connect_lines.append(f"{header_name}: {header_value}")
        connect_lines.append("")
        connect_lines.append("")
        connect_request = "\r\n".join(connect_lines)

        self.send(connect_request.encode("ascii"))

        response = self.response_class(self.sock, method=self._method)
        version, status_code, status_message = response._read_status()

        while True:
            line = response.fp.readline(http.client._MAXLINE + 1)
            if len(line) > http.client._MAXLINE:
                raise http.client.LineTooLong("header line")
            if line in (b"\r\n", b"\n", b""):
                break

        if status_code != 200:
            self.close()
            raise OSError(f"Tunnel connection failed: {status_code} {status_message.strip()}")

    ##-----------------------------------------------------------------------
    ## connect function
    ##  Purpose: connect to the HTTPS proxy, establish an optional CONNECT tunnel, and wrap the origin TLS session
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def connect(self):
        self.sock = self._create_connection((self.host, self.port), self.timeout, self.source_address)

        proxy_context = self._proxy_context
        if proxy_context is None:
            proxy_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

        self.sock = proxy_context.wrap_socket(self.sock, server_hostname=self.host)

        if self._tunnel_host:
            self._send_https_tunnel()

            origin_context = self._context
            if origin_context is None:
                origin_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

            # Prefer stdlib SSLTransport for TLS-in-TLS tunneling when available.
            ssl_transport_cls = getattr(ssl, "SSLTransport", None)
            if ssl_transport_cls is not None:
                self.sock = ssl_transport_cls(self.sock, origin_context, server_hostname=self._tunnel_host)
            else:
                self.sock = TLSOverTLSSocket(self.sock, origin_context, self._tunnel_host)
                self.sock.do_handshake()

class feedService:

    ## Init function (set local variables)
    def __init__(self):
        self.runtime_config_data = []
        self.runtime_log_file = ""
        self.runtime_start_time = ""
        self.runtime_working_dir = ""
        self.runtime_proxy_host = None
        self.runtime_proxy_port = None
        self.runtime_proxy_scheme = "http"
        self.runtime_proxy_auth = False
        self.runtime_proxy_username = ""
        self.runtime_proxy_password = ""
        self.runtime_cafile = ""
        self.runtime_force = False
        self.runtime_offline_update = False
        self.runtime_feed_cache_file = ""
        self.system_schedule_day = ""
        self.system_schedule_time = ""
        self.system_schedule_frequency = ""
        self.system_log_level = ""
        self.system_log_max_bytes = 5 * 1024 * 1024
        self.system_log_backup_count = 5
        self.system_exceptions_delta_value = 0
        self.system_exceptions_delta_action = ""
        self.system_network_attempts = 0
        self.system_network_delay = 0
        self.system_network_cafile = ""
        self.system_sync_update = False
        self.feed_name = ""
        self.feed_list = {}
        self.feed_endpoint_method = ""
        self.feed_endpoint_url = ""
        self.feed_endpoint_auth_type = ""
        self.feed_endpoint_auth_credentials_username = ""
        self.feed_endpoint_auth_credentials_password = ""
        self.feed_endpoint_auth_credentials_token = ""
        self.feed_endpoint_headers = {}
        self.feed_endpoint_body = ""
        self.feed_source_format = ""
        self.feed_source_csv_position = 0
        self.feed_source_csv_has_header = False
        self.feed_source_delimiter = ""
        self.feed_source_regex = ""
        self.feed_source_json_mode = "pointers"
        self.feed_source_json_pointers = []
        self.feed_source_json_pointer_strict = False
        self.feed_import_ip_exclusions = []
        self.feed_import_url_exclusions = []
        self.feed_export_url_category = ""
        self.feed_export_url_cataction = ""
        self.feed_export_url_datagroup = ""
        self.feed_export_url_include = ""
        self.feed_export_ip_datagroup = ""
        self.feed_export_ip_combine = False
        self.feed_export_ip_include = []
        self.lastrun_lastchange = ""
        self.lastrun_hash = ""
        self.lastrun_result = ""
        self.lastrun_detail = ""
        self.lastrun_count = 0
        self.lastrun_rejected = []
        self.lastrun_datagroup_name = ""
        self.feed_sets = {}
        self.reset_feed_collections()

    ##-----------------------------------------------------------------------
    ## reset_feed_collections function
    ##  Purpose: initialize/reset feed item collections as list+set pairs
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def reset_feed_collections(self):
        self.feed_list = {
            "IPv4": [],
            "IPv6": [],
            "DOMAIN": [],
            "WDOMAIN": [],
            "DOMAINW": [],
            "WDOMAINW": [],
            "REJECT": [],
        }
        self.feed_sets = {key: set() for key in self.feed_list.keys()}

    ##-----------------------------------------------------------------------
    ## add_feed_item function
    ##  Purpose: add a normalized item to a feed category using O(1) set checks
    ##  Parameters:
    ##      category       = feed category key (IPv4/DOMAIN/etc)
    ##      item           = normalized item value
    ##  Returns:
    ##      boolean        = True when item was added, False when duplicate/invalid
    ##-----------------------------------------------------------------------
    def add_feed_item(self, category, item):
        if category not in self.feed_list:
            return False

        if item in self.feed_sets[category]:
            return False

        self.feed_sets[category].add(item)
        self.feed_list[category].append(item)
        return True

    ##-----------------------------------------------------------------------
    ## remove_feed_item function
    ##  Purpose: remove a feed item while keeping list and set in sync
    ##  Parameters:
    ##      category       = feed category key (IPv4/DOMAIN/etc)
    ##      item           = normalized item value
    ##  Returns:
    ##      boolean        = True when item existed and was removed
    ##-----------------------------------------------------------------------
    def remove_feed_item(self, category, item):
        if category not in self.feed_list:
            return False

        if item not in self.feed_sets[category]:
            return False

        self.feed_sets[category].remove(item)
        self.feed_list[category].remove(item)
        return True

    ##-----------------------------------------------------------------------
    ## remove_feed_items_by_match function
    ##  Purpose: remove all items in a category that satisfy a predicate
    ##  Parameters:
    ##      category       = feed category key (IPv4/DOMAIN/etc)
    ##      matcher        = callable(item) -> bool
    ##  Returns:
    ##      list           = removed item values
    ##-----------------------------------------------------------------------
    def remove_feed_items_by_match(self, category, matcher):
        if category not in self.feed_list:
            return []

        removed = [item for item in self.feed_list[category] if matcher(item)]
        if not removed:
            return []

        removed_set = set(removed)
        self.feed_sets[category].difference_update(removed_set)
        self.feed_list[category] = [item for item in self.feed_list[category] if item not in removed_set]
        return removed

    ##-----------------------------------------------------------------------
    ## rotate_log_file function
    ##  Purpose: rotates the log file when it reaches a certain size
    ##  Parameters:
    ##      None
    ##  Example:
    ##      self.rotate_log_file()
    ##-----------------------------------------------------------------------
    def rotate_log_file(self):
        if self.system_log_max_bytes <= 0 or self.system_log_backup_count <= 0:
            return

        if not os.path.exists(self.runtime_log_file):
            return

        if os.path.getsize(self.runtime_log_file) < self.system_log_max_bytes:
            return

        # Shift backups up one slot and discard the oldest backup.
        for index in range(self.system_log_backup_count, 0, -1):
            src = f"{self.runtime_log_file}.{index}"
            dst = f"{self.runtime_log_file}.{index + 1}"

            if index == self.system_log_backup_count:
                if os.path.exists(src):
                    os.remove(src)
                continue

            if os.path.exists(src):
                os.replace(src, dst)

        os.replace(self.runtime_log_file, f"{self.runtime_log_file}.1")

    ##-----------------------------------------------------------------------
    ## log function
    ##  Purpose: sends a message to the log file
    ##  Parameters:
    ##      lev         = level of this message
    ##      log_lev     = user configured logging level
    ##      msg         = log message
    ##  Example:
    ##      self.log(1, self.system_log_level, "Attempting to download feed data...")
    ##-----------------------------------------------------------------------
    def log(self, lev, log_lev, msg):
        ## Create the log file if it doesn't exist
        try:
            if not os.path.exists(self.runtime_log_file):
                with open(self.runtime_log_file, "w", encoding="utf-8") as f:
                    log_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Log initialized.\n"
                    f.write(log_string)
        except OSError as e:
            self.event_log(1, 1, f"Cannot create log file {self.runtime_log_file}: {e}")
            sys.exit(1)

        ## Log the message (only if user-defined "log_lev" >= log message "lev")
        try:
            if int(log_lev) >= int(lev):
                self.rotate_log_file()
                log_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg.encode('unicode_escape').decode() + "\n"
                with open(self.runtime_log_file, "a", encoding="utf-8") as f:
                    f.write(log_string)
        except Exception as e:
            self.event_log(1, 1, f"Cannot write to log file: {e}")
            sys.exit(1)
    
    ##-----------------------------------------------------------------------
    ## event_log function
    ##  Purpose: sends a message using logger to /var/log/ltm
    ##  Parameters:
    ##      lev         = level of this message
    ##      log_lev     = user configured logging level
    ##      msg         = log message
    ##  Example:
    ##      self.event_log(2, self.system_log_level, "VERSION request to MS web service was successful.")
    ##-----------------------------------------------------------------------
    def event_log(self, lev, log_lev, msg):
        ## For event logs 1 -> error, 2 -> notice
        level = "error" if lev == 1 else "notice"

        if int(log_lev) >= int(lev):

            shell.run(
                ["/usr/bin/logger", "-p", f"local0.{level}", f"[fS] {self.feed_name}.app: {msg}"],
                capture_output=True,
            )

    ##-----------------------------------------------------------------------
    ## mask_sensitive_headers function
    ##  Purpose: mask sensitive request header values before writing debug logs
    ##  Parameters:
    ##      headers         = header dictionary to sanitize for logging
    ##  Returns:
    ##      dict            = copied header dictionary with sensitive values masked
    ##-----------------------------------------------------------------------
    def mask_sensitive_headers(self, headers):
        masked_headers = {}
        sensitive_header_names = {
            "authorization",
            "proxy-authorization",
            "cookie",
            "set-cookie",
        }
        sensitive_header_keywords = ("token", "secret", "key", "password", "auth")

        for header_name, header_value in (headers or {}).items():
            header_name_text = str(header_name)
            header_name_lower = header_name_text.lower()

            if (
                header_name_lower in sensitive_header_names
                or any(keyword in header_name_lower for keyword in sensitive_header_keywords)
            ):
                value_text = str(header_value)
                prefix = value_text.split()[0] if " " in value_text else "***"
                masked_headers[header_name_text] = f"{prefix} ***"
            else:
                masked_headers[header_name_text] = header_value

        return masked_headers

    ##-----------------------------------------------------------------------
    ## summarize_request_payload function
    ##  Purpose: summarize request payload metadata without logging sensitive body contents
    ##  Parameters:
    ##      payload         = raw request body value
    ##  Returns:
    ##      string          = redacted summary containing payload length and short hash
    ##-----------------------------------------------------------------------
    def summarize_request_payload(self, payload):
        if not payload:
            return "<empty>"

        payload_text = str(payload)
        payload_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()[:12]
        return f"<redacted; length={len(payload_text)} chars; sha256={payload_hash}>"

    ##-----------------------------------------------------------------------
    ## get_hash function
    ##  Purpose: return the hash value of a supplied parameter
    ##  Parameters:
    ##      input           = supplied parameter to be hashed
    ##-----------------------------------------------------------------------
    def get_hash(self, input):
        return hashlib.md5(str(input).encode('utf-8')).hexdigest()

    ##-----------------------------------------------------------------------
    ## to_canonical_json function
    ##  Purpose: serialize Python objects in a deterministic JSON representation
    ##  Parameters:
    ##      value           = Python object to serialize
    ##  Returns:
    ##      string          = canonical JSON string (sorted keys, compact separators)
    ##-----------------------------------------------------------------------
    def to_canonical_json(self, value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    ##-----------------------------------------------------------------------
    ## normalize_source_item function
    ##  Purpose: remove surrounding whitespace and matching quote wrappers from extracted feed values
    ##  Parameters:
    ##      item            = extracted feed value to normalize
    ##  Returns:
    ##      string          = normalized value (or empty string)
    ##-----------------------------------------------------------------------
    def normalize_source_item(self, item):
        if item is None:
            return ""

        normalized_item = str(item).strip()
        normalized_item = normalized_item.lstrip("\ufeff").strip()
        if len(normalized_item) >= 2 and normalized_item[0] == normalized_item[-1] and normalized_item[0] in ('"', "'"):
            normalized_item = normalized_item[1:-1].strip()

        return normalized_item

    ##-----------------------------------------------------------------------
    ## get_normalized_feed_snapshot function
    ##  Purpose: build a deterministic, sorted snapshot of processed feed contents
    ##  Returns:
    ##      dict            = feed snapshot keyed by entry type with sorted string values
    ##-----------------------------------------------------------------------
    def get_normalized_feed_snapshot(self):
        normalized_feed = {}
        for key in sorted(self.feed_list.keys()):
            normalized_feed[key] = sorted(str(item) for item in self.feed_list[key])
        return normalized_feed

    ##-----------------------------------------------------------------------
    ## get_feed_content_hash function
    ##  Purpose: return hash of normalized/sorted feed contents
    ##  Returns:
    ##      string          = MD5 hash of canonicalized feed snapshot
    ##-----------------------------------------------------------------------
    def get_feed_content_hash(self):
        normalized_json = self.to_canonical_json(self.get_normalized_feed_snapshot())
        return hashlib.md5(normalized_json.encode('utf-8')).hexdigest()

    ##-----------------------------------------------------------------------
    ## get_importable_categories function
    ##  Purpose: return feed categories that are mapped to active export targets
    ##  Returns:
    ##      list            = ordered category keys that can be imported
    ##-----------------------------------------------------------------------
    def get_importable_categories(self):
        categories = []

        if self.feed_export_ip_datagroup:
            categories.extend(["IPv4", "IPv6"])

        if self.feed_export_url_datagroup:
            categories.extend(["DOMAIN", "WDOMAINW", "DOMAINW", "WDOMAIN"])

        if self.feed_export_url_category:
            categories.extend(["DOMAIN", "DOMAINW", "WDOMAIN", "WDOMAINW"])

        # Preserve order while removing duplicates.
        return list(dict.fromkeys(categories))

    ##-----------------------------------------------------------------------
    ## reset_force_option function
    ##  Purpose: Reset iApp force_update variable back to "no" after a forced run.
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def reset_force_option(self):
        app_service = f"{self.feed_name}.app/{self.feed_name}"

        cmd = f'modify sys application service {app_service} variables modify {{ force_update__force {{ value "no" }} }}'

        success, result = self.run_tmsh_commands([cmd])
        if not success:
            self.log(1, 1, f"ERROR: Failed to reset force_update option: {result}")
            self.event_log(1, 1, f"Failed to reset force_update option: {result}")

    ##-----------------------------------------------------------------------
    ## config_sync function
    ##  Purpose: Runs a ConfigSync operation to the sync-failover device group
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def config_sync(self):
        try:
            result = shell.run(
                ["tmsh", "-a", "list", "cm", "device-group", "one-line"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error_text = (result.stderr or result.stdout or "Unknown error").strip()
                return False, f"Unable to inspect device groups for ConfigSync: {error_text}"

            device_group = None

            for line in (result.stdout or "").splitlines():
                line = line.strip()
                if " type sync-failover " not in f" {line} ":
                    continue

                match = re.search(r"^cm device-group\s+(\S+)\s+\{", line)
                if match:
                    device_group = match.group(1)
                    break

            if not device_group:
                return True, "No sync-failover device group found; BIG-IP appears to be standalone. ConfigSync skipped."

            # Check if auto-sync is enabled for the device group; if so, skip manual sync.
            autosync_result = shell.run(
                ["tmsh", "-a", "list", "cm", "device-group", device_group, "auto-sync"],
                capture_output=True,
                text=True,
            )
            if autosync_result.returncode == 0 and "auto-sync enabled" in autosync_result.stdout:
                return True, f"ConfigSync skipped for device group '{device_group}'; auto-sync is enabled."

            sync_result = shell.run(
                ["tmsh", "-a", "run", "cm", "config-sync", "to-group", device_group],
                capture_output=True,
                text=True
            )

            if sync_result.returncode != 0:
                error_text = (sync_result.stderr or sync_result.stdout or "Unknown error").strip()
                return False, f"ConfigSync to '{device_group}' failed: {error_text}"

            output_text = (sync_result.stdout or "").strip()
            if output_text:
                self.log(2, self.system_log_level, f"ConfigSync output: {output_text}")

            return True, f"ConfigSync completed to device group '{device_group}'."
        except Exception as e:
            return False, f"ConfigSync operation failed with exception: {e}"

    ##-----------------------------------------------------------------------
    ## get_lastrun_datagroup_name function
    ##  Purpose: returns the internal data group name used to persist last run state
    ##  Returns:
    ##      string          = internal data group name for this feed
    ##-----------------------------------------------------------------------
    def get_lastrun_datagroup_name(self):
        if not self.lastrun_datagroup_name:
            self.lastrun_datagroup_name = f"fS_{self.feed_name}_lastrun"
        return self.lastrun_datagroup_name

    ##-----------------------------------------------------------------------
    ## tmsh_escape function
    ##  Purpose: escape values for safe use inside tmsh quoted strings
    ##  Parameters:
    ##      value           = raw value to escape
    ##  Returns:
    ##      string          = tmsh-escaped value
    ##-----------------------------------------------------------------------
    def tmsh_escape(self, value):
        text = str(value)
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        return text

    ##-----------------------------------------------------------------------
    ## tmsh_unescape function
    ##  Purpose: unescape tmsh-escaped string values
    ##  Parameters:
    ##      value           = tmsh-escaped value
    ##  Returns:
    ##      string          = unescaped value
    ##-----------------------------------------------------------------------
    def tmsh_unescape(self, value):
        text = str(value)
        text = text.replace('\\"', '"')
        text = text.replace("\\\\", "\\")
        return text

    ##-----------------------------------------------------------------------
    ## decode_tmsh_escaped_string function
    ##  Purpose: decode tmsh escaped strings (quoted values and octal escape sequences)
    ##  Parameters:
    ##      value           = raw tmsh string value (quoted or unquoted)
    ##  Returns:
    ##      string          = decoded string value
    ##-----------------------------------------------------------------------
    def decode_tmsh_escaped_string(self, value):
        text = str(value)
        if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
            text = text[1:-1]

        text = self.tmsh_unescape(text)

        # TMSH may emit escaped octal byte sequences (for example \040 for space).
        text = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), text)

        return text

    ##-----------------------------------------------------------------------
    ## run_tmsh_commands function
    ##  Purpose: run one or more tmsh commands, optionally inside a single transaction
    ##  Parameters:
    ##      commands        = list of tmsh command strings
    ##      use_transaction = run commands inside a single cli transaction when True
    ##  Returns:
    ##      tuple           = (success boolean, output/error text)
    ##-----------------------------------------------------------------------
    def run_tmsh_commands(self, commands, use_transaction=False):
        if not commands:
            return True, ""

        tmsh_script = []
        if use_transaction:
            tmsh_script.append("create cli transaction")

        tmsh_script.extend(commands)

        if use_transaction:
            tmsh_script.append("submit cli transaction")

        tmsh_input = "\n".join(tmsh_script) + "\n"

        try:
            result = shell.run(
                ["tmsh", "-a", "-q"],
                input=tmsh_input,
                capture_output=True,
                text=True,
            )
        except Exception as e:
            return False, str(e)

        stdout_text = (result.stdout or "").strip()
        stderr_text = (result.stderr or "").strip()
        combined_output = "\n".join(part for part in [stdout_text, stderr_text] if part).strip()
        transaction_failure_match = re.search(
            r"^\s*(transaction\s+failed\s*:.*)$",
            combined_output,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        transaction_failure_text = transaction_failure_match.group(1).strip() if transaction_failure_match else ""

        if result.returncode != 0:
            if use_transaction and transaction_failure_text:
                return False, transaction_failure_text
            error_text = combined_output or "Unknown tmsh error"
            return False, error_text

        # Some tmsh transaction failures are reported in output text with exit code 0.
        if use_transaction and transaction_failure_text:
            return False, transaction_failure_text

        output_text = stdout_text
        return True, output_text

    ##-----------------------------------------------------------------------
    ## tmsh_object_exists function
    ##  Purpose: check whether a tmsh object exists
    ##  Parameters:
    ##      object_path_tokens = list of tmsh path tokens (for example ["/ltm", "data-group", ...])
    ##  Returns:
    ##      boolean         = True if the object exists, else False
    ##-----------------------------------------------------------------------
    def tmsh_object_exists(self, object_path_tokens):
        try:
            result = shell.run(
                ["tmsh", "-a", "list", *object_path_tokens],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    ##-----------------------------------------------------------------------
    ## serialize_last_run_records function
    ##  Purpose: flatten last run dict to key/value records for internal data group
    ##  Parameters:
    ##      last_run_data   = last-run state dictionary
    ##  Returns:
    ##      list            = list of (key, value) tuples for data-group storage
    ##-----------------------------------------------------------------------
    def serialize_last_run_records(self, last_run_data):
        rejected_items = last_run_data.get("rejected", [])
        if not isinstance(rejected_items, list):
            rejected_items = []

        records = [
            ("lastchange", last_run_data.get("lastchange", "")),
            ("hash", last_run_data.get("hash", "")),
            ("result", last_run_data.get("result", "")),
            ("detail", last_run_data.get("detail", "")),
            ("count", int(last_run_data.get("count", 0))),
            ("rejected_count", len(rejected_items)),
        ]

        for index, item in enumerate(rejected_items, start=1):
            records.append((f"rejected_{index:06d}", item))

        return records

    ##-----------------------------------------------------------------------
    ## parse_last_run_records function
    ##  Purpose: reconstruct last run dict from key/value records
    ##  Parameters:
    ##      record_map      = flattened key/value record map loaded from data group
    ##  Returns:
    ##      dict            = normalized last-run state dictionary
    ##-----------------------------------------------------------------------
    def parse_last_run_records(self, record_map):
        if not record_map:
            return {}

        try:
            count_value = int(record_map.get("count", "0"))
        except ValueError:
            count_value = 0

        if isinstance(record_map.get("rejected"), list):
            rejected_items = record_map.get("rejected", [])
        else:
            rejected_keys = sorted(
                k for k in record_map.keys()
                if re.match(r"^rejected_\d+$", k)
            )
            rejected_items = [record_map[k] for k in rejected_keys]

        return {
            "lastchange": record_map.get("lastchange", ""),
            "hash": record_map.get("hash", ""),
            "result": record_map.get("result", ""),
            "detail": record_map.get("detail", ""),
            "count": count_value,
            "rejected": rejected_items,
        }

    ##-----------------------------------------------------------------------
    ## normalize_last_run_status function
    ##  Purpose: normalize status values persisted in last run data
    ##  Parameters:
    ##      status          = raw status value
    ##      items           = item count used to map legacy success states
    ##  Returns:
    ##      string          = normalized status (updated, nochange, error, or warning)
    ##-----------------------------------------------------------------------
    def normalize_last_run_status(self, status, items=0):
        normalized = str(status or "").strip().lower()

        if normalized in ["updated", "nochange", "error", "warning"]:
            return normalized

        if normalized == "success":
            return "updated" if int(items) > 0 else "nochange"

        if normalized.startswith("error"):
            return "error"

        if normalized in ["", "none", "null"]:
            return "nochange"

        return "warning"

    ##-----------------------------------------------------------------------
    ## sanitize_string function
    ##  Purpose: sanitize string values from data group to prevent log injection and other attacks
    ##  Parameters:
    ##      value           = raw string-like input
    ##      max_length      = maximum allowed output length before truncation
    ##      field_name      = optional field label used in warning logs
    ##  Returns:
    ##      string          = sanitized string value
    ##-----------------------------------------------------------------------
    def sanitize_string(self, value, max_length=1000, field_name=""):
        if value is None:
            return ""
        text = str(value).strip()
        if len(text) > max_length:
            self.log(2, self.system_log_level, f"WARNING: {field_name} exceeded max length {max_length}, truncating.")
            self.event_log(2, self.system_log_level, f"{field_name} exceeded max length {max_length}, truncating.")
            text = text[:max_length]
        text = text.replace('\x00', '')
        text = text.replace('\n', ' ')
        text = text.replace('\r', '')
        return text

    ##-----------------------------------------------------------------------
    ## validate_iso_timestamp function
    ##  Purpose: validate timestamp is in ISO 8601 format
    ##  Parameters:
    ##      timestamp       = timestamp string to validate
    ##  Returns:
    ##      string          = validated timestamp or empty string
    ##-----------------------------------------------------------------------
    def validate_iso_timestamp(self, timestamp):
        if not timestamp:
            return ""
        text = str(timestamp).strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$', text):
            return text
        self.log(2, self.system_log_level, f"WARNING: Invalid timestamp format in data group: {text[:50]}")
        self.event_log(2, self.system_log_level, f"Invalid timestamp format in data group: {text[:50]}")
        return ""

    ##-----------------------------------------------------------------------
    ## validate_md5_hash function
    ##  Purpose: validate hash is valid MD5 hex string
    ##  Parameters:
    ##      hash_val        = hash string to validate
    ##  Returns:
    ##      string          = validated lowercase hash or empty string
    ##-----------------------------------------------------------------------
    def validate_md5_hash(self, hash_val):
        if not hash_val:
            return ""
        text = str(hash_val).strip().lower()
        if re.match(r'^[a-f0-9]{32}$', text):
            return text
        self.log(2, self.system_log_level, f"WARNING: Invalid hash format in data group: {text[:50]}")
        self.event_log(2, self.system_log_level, f"Invalid hash format in data group: {text[:50]}")
        return ""

    ##-----------------------------------------------------------------------
    ## sanitize_rejected_items function
    ##  Purpose: sanitize rejected items list from data group
    ##  Parameters:
    ##      record_map      = data-group record map containing rejected_* keys
    ##  Returns:
    ##      list            = sanitized rejected item strings
    ##-----------------------------------------------------------------------
    def sanitize_rejected_items(self, record_map):
        rejected = []
        rejected_keys = sorted(k for k in record_map.keys() if re.match(r"^rejected_\d+$", k))
        for key in rejected_keys:
            item = self.sanitize_string(record_map[key], max_length=500, field_name=f"rejected item from {key}")
            if item:
                rejected.append(item)
        return rejected

    ##-----------------------------------------------------------------------
    ## save_last_run_datagroup function
    ##  Purpose: persist last run key/value data in an internal string data group
    ##  Parameters:
    ##      last_run_data   = last-run state dictionary to persist
    ##  Returns:
    ##      tuple           = (success boolean, error text)
    ##-----------------------------------------------------------------------
    def save_last_run_datagroup(self, last_run_data):
        dg_name = self.get_lastrun_datagroup_name()
        record_list = self.serialize_last_run_records(last_run_data)

        records_cmd = []
        for key, value in record_list:
            key_text = self.tmsh_escape(key)
            value_text = self.tmsh_escape(str(value))
            
            # Only quote if value contains spaces or special characters
            # Characters that require quoting in tmsh data values
            needs_quoting = not value_text or any(c in value_text for c in {' ', '{', '}', '"', "'", '\n', '\r', '\t', '#', '`', '$'})
            
            if needs_quoting:
                records_cmd.append(f'{key_text} {{ data "{value_text}" }}')
            else:
                records_cmd.append(f'{key_text} {{ data {value_text} }}')

        records_block = " ".join(records_cmd)

        # Check if data group exists
        try:
            result = shell.run(
                ["tmsh", "-a", "list", "/ltm", "data-group", "internal", dg_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            dg_exists = result.returncode == 0
        except Exception:
            dg_exists = False

        if dg_exists:
            modify_cmd = f'modify /ltm data-group internal {dg_name} records replace-all-with {{ {records_block} }}'
        else:
            modify_cmd = f'create /ltm data-group internal {dg_name} type string records replace-all-with {{ {records_block} }}'

        success, err = self.run_tmsh_commands([modify_cmd])
        if not success:
            return False, err

        return True, ""

    ##-----------------------------------------------------------------------
    ## load_last_run_datagroup function
    ##  Purpose: load last run data from the internal data group
    ##  Returns:
    ##      dict            = last-run state dictionary loaded from data group
    ##-----------------------------------------------------------------------
    def load_last_run_datagroup(self):
        dg_name = self.get_lastrun_datagroup_name()

        try:
            result = shell.run(
                ["tmsh", "-a", "list", "/ltm", "data-group", "internal", dg_name, "one-line"],
                capture_output=True,
                text=True,
                timeout=10
            )
            result_text = result.stdout or ""
        except Exception as e:
            result_text = str(e)

        if "was not found" in result_text or result_text == "":
            # First run bootstrap: initialize the internal data group with defaults.
            default_last_run = {
                "lastchange": "",
                "hash": "",
                "result": "nochange",
                "detail": "",
                "count": 0,
                "rejected": []
            }

            success, err = self.save_last_run_datagroup(default_last_run)
            if success:
                self.log(2, self.system_log_level, f"Initialized internal data group '{dg_name}' with default last run state.")
                return default_last_run

            self.log(2, self.system_log_level, f"WARNING: Unable to initialize internal data group '{dg_name}' during first-run load: {err}. Continuing with empty last run state.")
            self.event_log(2, self.system_log_level, f"Unable to initialize internal data group '{dg_name}' during first-run load: {err}")
            return {}

        try:
            # Extract records from one-line tmsh output.
            # Keys may be quoted and values can be quoted or unquoted.
            # Pattern matches: key { data value } or key { data "value" }
            pair_pattern = re.compile(r'("(?:\\.|[^"])*"|\S+)\s+\{\s+data\s+(?:"((?:\\.|[^"])*)"|(\S+))\s+\}')
            pairs = list(pair_pattern.finditer(result_text))
            if not pairs:
                return {}

            record_map = {}
            for match in pairs:
                key = match.group(1)
                quoted_value = match.group(2)
                unquoted_value = match.group(3)
                parsed_key = self.decode_tmsh_escaped_string(key)
                # Use quoted value if present, otherwise use unquoted value
                raw_value = quoted_value if quoted_value is not None else (unquoted_value or "")
                parsed_value = self.decode_tmsh_escaped_string(raw_value)
                record_map[parsed_key] = parsed_value

            # Sanitize and validate all data from the data group before use.
            lastchange_raw = record_map.get("lastchange", "")
            hash_raw = record_map.get("hash", "")
            result_raw = record_map.get("result", "")
            detail_raw = record_map.get("detail", "")

            sanitized_record_map = {
                "lastchange": self.validate_iso_timestamp(lastchange_raw),
                "hash": self.validate_md5_hash(hash_raw),
                "result": self.normalize_last_run_status(result_raw, record_map.get("count", 0)),
                "detail": self.sanitize_string(detail_raw, max_length=500, field_name="detail"),
                "count": record_map.get("count", 0),
                "rejected": self.sanitize_rejected_items(record_map),
            }

            return self.parse_last_run_records(sanitized_record_map)
        except Exception as e:
            self.log(1, self.system_log_level, f"ERROR: Failed to decode last run data from internal data group '{dg_name}': {e} (1116).")
            self.event_log(1, self.system_log_level, f"Failed to decode last run data from internal data group '{dg_name}': {e} (1116).")
            sys.exit(1)

    ##-----------------------------------------------------------------------
    ## update_last_run function
    ##  Purpose: Updates last run information in BIG-IP internal data group
    ##  Parameters:
    ##      hash            = hash of the feed data from the last successful run
    ##      result          = status of the last run (updated, nochange, error, warning)
    ##      items           = number of items processed in the last successful run
    ##      rejected        = list of rejected items in the last successful run
    ##      detail          = verbose status detail message
    ##-----------------------------------------------------------------------
    def update_last_run(self, hash, result, items, rejected, detail=""):

        status = self.normalize_last_run_status(result, items)
        persisted_count = items

        ## Update lastchange and preserve counters based on run status
        if status == "updated" and items > 0:
            lastchange = datetime.datetime.now(datetime.timezone.utc).isoformat()
            if rejected is None:
                rejected = []
        else:
            lastchange = self.lastrun_lastchange
            ## Don't overwrite previous counts / rejected list if there were no changes this time
            persisted_count = self.lastrun_count
            rejected = self.lastrun_rejected


        # Update the last run information
        last_run_data = {
            "lastchange": lastchange,
            "hash": hash,
            "result": status,
            "detail": str(detail or ""),
            "count": persisted_count,
            "rejected": rejected
        }

        # Only write to the data group when contents have actually changed.
        # This avoids unnecessary config mutations that would trigger ConfigSync.
        current_last_run_data = {
            "lastchange": self.lastrun_lastchange,
            "hash": self.lastrun_hash,
            "result": self.lastrun_result,
            "detail": self.lastrun_detail,
            "count": self.lastrun_count,
            "rejected": self.lastrun_rejected,
        }
        if self.to_canonical_json(last_run_data) == self.to_canonical_json(current_last_run_data):
            self.log(3, self.system_log_level, "Last run data unchanged; skipping data group write.")
            return False

        success, err = self.save_last_run_datagroup(last_run_data)
        if not success:
            dg_name = self.get_lastrun_datagroup_name()
            self.log(1, 1, f"ERROR: Failed to update last run internal data group '{dg_name}': {err} (1117).")
            self.event_log(1, 1, f"Failed to update last run internal data group '{dg_name}': {err} (1117).")
            sys.exit(1)

        self.log(3, self.system_log_level, f"Updated last run information in internal data group.")
        return True

    ##-----------------------------------------------------------------------
    ## load_last_run function
    ##  Purpose: load last run information from internal data group and set local variables accordingly
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def load_last_run(self):
        lastrun_data = self.load_last_run_datagroup()

        self.lastrun_lastchange = lastrun_data.get("lastchange", "")
        self.lastrun_result = self.normalize_last_run_status(lastrun_data.get("result", ""), lastrun_data.get("count", 0))
        self.lastrun_detail = lastrun_data.get("detail", "")
        if not self.lastrun_detail and str(lastrun_data.get("result", "")).lower().startswith("error"):
            self.lastrun_detail = lastrun_data.get("result", "")
        self.lastrun_hash = lastrun_data.get("hash", "")
        self.lastrun_count = lastrun_data.get("count", 0)
        self.lastrun_rejected = lastrun_data.get("rejected", [])

        self.log(3, self.system_log_level, "--------------------------------")
        self.log(3, self.system_log_level, "Last run information loaded:")
        self.log(3, self.system_log_level, "--------------------------------")
        self.log(3, self.system_log_level, f"lastchange={self.lastrun_lastchange}")
        self.log(3, self.system_log_level, f"result={self.lastrun_result}")
        self.log(3, self.system_log_level, f"detail={self.lastrun_detail}")
        self.log(3, self.system_log_level, f"hash={self.lastrun_hash}")
        self.log(3, self.system_log_level, f"count={self.lastrun_count}")
        self.log(3, self.system_log_level, f"rejected_count={len(self.lastrun_rejected)}")
        self.log(3, self.system_log_level, "--------------------------------")

    ##-----------------------------------------------------------------------
    ## load_config function
    ##  Purpose: load configuration parameters from JSON config file and set local variables accordingly
    ##  Parameters: None
    ##-----------------------------------------------------------------------
    def load_config(self):
        if not self.runtime_config_data:
            ifile_config = "unknown"
            self.log(3, 3, f"Loading configuration file.")
            try:
                entry_array = []
                ifile_list = os.listdir('/config/filestore/files_d/Common_d/ifile_d/')
                ifile_pattern = f"*{self.feed_name}.app:{self.feed_name}.conf*"
                for entry in ifile_list:
                    if fnmatch.fnmatch(entry, ifile_pattern):
                        entry_array.append(f"/config/filestore/files_d/Common_d/ifile_d/{entry}")

                ## Get JSON data from configuration file
                ifile_config = max(entry_array, key=os.path.getctime)
                with open(ifile_config, "r", encoding="utf-8") as f:
                    f_content = f.read()
                try:
                    self.runtime_config_data = json.loads(f_content)
                except json.JSONDecodeError as e:
                    self.log(1, 1, f"ERROR: Invalid JSON in configuration file {ifile_config}: {e.msg} (line {e.lineno}, col {e.colno}) (1102).")
                    self.event_log(1, 1, f"Invalid JSON in configuration file {ifile_config}: {e.msg} (line {e.lineno}, col {e.colno}) (1102).")
                    sys.exit(1)
                except Exception as e:
                    self.log(1, 1, f"ERROR: An error occurred while parsing configuration file ({ifile_config}): {e} (1103).")
                    self.event_log(1, 1, f"An error occurred while parsing configuration file ({ifile_config}): {e} (1103).")
                    sys.exit(1)
            except ValueError:
                self.log(1, 1, f"ERROR: No configuration file found for feed '{self.feed_name}' in /config/filestore/files_d/Common_d/ifile_d/ (1104).")
                self.event_log(1, 1, f"No configuration file found for feed '{self.feed_name}' in /config/filestore/files_d/Common_d/ifile_d/ (1104).")
                sys.exit(1)
            except FileNotFoundError:
                self.log(1, 1, f"ERROR: Configuration file ({ifile_config}) not found. Aborting (1105).")
                self.event_log(1, 1, f"Configuration file ({ifile_config}) not found. Aborting (1105).")
                sys.exit(1)
            except PermissionError:
                self.log(1, 1, f"ERROR: Permission denied when accessing configuration file ({ifile_config}). Aborting (1106).")
                self.event_log(1, 1, f"Permission denied when accessing configuration file ({ifile_config}). Aborting (1106).")
                sys.exit(1)
            except IsADirectoryError:
                self.log(1, 1, f"ERROR: Expected configuration file ({ifile_config}) is a directory. Aborting (1107).")
                self.event_log(1, 1, f"Expected configuration file ({ifile_config}) is a directory. Aborting (1107).")
                sys.exit(1)
            except Exception as e:
                self.log(1, 1, f"ERROR: An error occurred while loading configuration file ({ifile_config}): {e}. Aborting (1108).")
                self.event_log(1, 1, f"An error occurred while loading configuration file ({ifile_config}): {e}. Aborting (1108).")
                sys.exit(1)            

        try:
            ## Read system configuration parameters from the json config
            sys_log_config      = self.runtime_config_data["system"]["log"]
            sys_exc_config      = self.runtime_config_data["system"]["exceptions"]
            sys_net_config      = self.runtime_config_data["system"]["network"]

            self.system_log_level                           = sys_log_config["level"]
            self.system_log_max_bytes                       = int(sys_log_config.get("max_bytes", self.system_log_max_bytes))
            self.system_log_backup_count                    = int(sys_log_config.get("backup_count", self.system_log_backup_count))
            self.system_exceptions_delta_value              = sys_exc_config["delta_value"]
            self.system_exceptions_delta_action             = sys_exc_config["delta_action"]
            self.system_network_attempts                    = sys_net_config["attempts"]
            self.system_network_delay                       = sys_net_config["delay"]
            self.system_network_cafile                      = sys_net_config["cafile"]
            self.system_sync_update                         = self.runtime_config_data["system"]["sync_update"]

            proxy_config = sys_net_config.get("proxy", {})
            proxy_host = str(proxy_config.get("host", "")).strip()
            proxy_port = str(proxy_config.get("port", "")).strip()
            proxy_scheme = str(proxy_config.get("scheme", "")).strip()
            proxy_auth = proxy_config.get("auth", False)

            if (proxy_host and proxy_port) and proxy_scheme not in ("http", "https"):
                raise ValueError("Proxy scheme must be either 'http' or 'https'.")

            if isinstance(proxy_auth, str):
                proxy_auth = proxy_auth.strip().lower() != "none"
            else:
                proxy_auth = bool(proxy_auth)

            self.runtime_proxy_auth = proxy_auth
            self.runtime_proxy_scheme = proxy_scheme
            self.runtime_proxy_username = str(proxy_config.get("username", "")).strip()
            self.runtime_proxy_password = str(proxy_config.get("password", "")).strip()

            if proxy_host and proxy_port:
                self.runtime_proxy_host = proxy_host
                self.runtime_proxy_port = int(proxy_port)

                auth_mode = "with authentication" if self.runtime_proxy_auth else "without authentication"
                self.log(2, self.system_log_level, f"Using configured proxy: {self.runtime_proxy_scheme}://{self.runtime_proxy_host}:{self.runtime_proxy_port} ({auth_mode}).")
            elif proxy_host or proxy_port:
                raise ValueError("Proxy configuration is incomplete; both host and port are required when proxy is configured.")
            else:
                self.runtime_proxy_host = None
                self.runtime_proxy_port = None
                self.runtime_proxy_scheme = "http"
                self.runtime_proxy_auth = False
                self.runtime_proxy_username = ""
                self.runtime_proxy_password = ""

            cert_dir = "/config/filestore/files_d/Common_d/certificate_d/"
            suffix_pattern = r'_(\d+)_(\d+)$'
            bundle_pattern = re.compile(rf"{re.escape(self.system_network_cafile)}{suffix_pattern}")

            cert_matches = []

            for entry in os.listdir(cert_dir):
                if bundle_pattern.search(entry):
                    cert_matches.append(os.path.join(cert_dir, entry))

            if cert_matches:
                self.runtime_cafile = max(cert_matches, key=os.path.getctime)
            else:
                self.log(1, self.system_log_level, f"ERROR: Could not find a certificate file matching '{self.system_network_cafile}' in {cert_dir}. Aborting (1109).")
                self.event_log(1, self.system_log_level, f"Could not find a certificate file matching '{self.system_network_cafile}' in {cert_dir}. Aborting (1109).")
                sys.exit(1)
        
            self.log(3, self.system_log_level, "System configuration imported.")

            ## Read feed configuration parameters from the json config
            endpoint_config     = self.runtime_config_data["feed"]["endpoint"]
            auth_config         = endpoint_config["auth"]
            cred_config         = auth_config["credentials"]
            source_config       = self.runtime_config_data["feed"]["source"]
            import_config       = self.runtime_config_data["feed"]["import"]
            export_url_config   = self.runtime_config_data["feed"]["export"]["url"]
            export_ip_config    = self.runtime_config_data["feed"]["export"]["ip"]

            self.reset_feed_collections()
            self.feed_endpoint_method                       = endpoint_config["method"]
            self.feed_endpoint_url                          = endpoint_config["url"]
            self.feed_endpoint_auth_type                    = auth_config["type"]
            self.feed_endpoint_auth_credentials_username    = cred_config["username"]
            self.feed_endpoint_auth_credentials_password    = cred_config["password"]
            self.feed_endpoint_auth_credentials_token       = cred_config["token"]
            self.feed_endpoint_headers                      = endpoint_config["headers"]
            self.feed_endpoint_body                         = endpoint_config["body"]
            self.feed_source_format                         = source_config["format"]
            self.feed_source_csv_position                   = source_config["csv_position"]
            self.feed_source_csv_has_header                 = source_config.get("csv_has_header", False)
            self.feed_source_delimiter                      = source_config["delimiter"]
            self.feed_source_regex                          = source_config["regex"]
            self.feed_source_json_mode                      = source_config.get("json_mode", "pointers")
            self.feed_source_json_pointers                  = source_config.get("json_pointers", [])
            self.feed_source_json_pointer_strict            = source_config.get("json_pointer_strict", False)
            self.feed_import_ip_exclusions                  = import_config["ip_exclusions"]
            self.feed_import_url_exclusions                 = import_config["url_exclusions"]
            self.feed_export_url_category                   = export_url_config["category"]
            self.feed_export_url_cataction                  = export_url_config["cataction"]
            self.feed_export_url_datagroup                  = export_url_config["datagroup"]
            self.feed_export_url_include                    = export_url_config["include"]
            self.feed_export_ip_datagroup                   = export_ip_config["datagroup"]
            self.feed_export_ip_combine                     = export_ip_config["combine"]
            self.feed_export_ip_include                     = export_ip_config["include"]

            if isinstance(self.feed_source_json_pointer_strict, str):
                self.feed_source_json_pointer_strict = self.feed_source_json_pointer_strict.strip().lower() == "true"

            if not isinstance(self.feed_source_json_mode, str):
                self.feed_source_json_mode = "pointers"
            self.feed_source_json_mode = self.feed_source_json_mode.strip().lower()
            if self.feed_source_json_mode not in ["pointers", "document"]:
                self.feed_source_json_mode = "pointers"

            if isinstance(self.feed_source_csv_has_header, str):
                self.feed_source_csv_has_header = self.feed_source_csv_has_header.strip().lower() == "true"

            if not isinstance(self.feed_source_json_pointers, list):
                self.feed_source_json_pointers = [self.feed_source_json_pointers]

            self.log(3, self.system_log_level, f"Feed configuration imported.")
        except Exception as e:
            self.log(1, 1, f"ERROR: There was an error loading the configuration: {e}. Aborting (1110).")
            self.event_log(1, 1, f"There was an error loading the configuration: {e}. Aborting (1110).")
            sys.exit(1)

    ##-----------------------------------------------------------------------
    ## fetch_feed function
    ##  Purpose: generate an HTTP request to feed and return response
    ##  Parameters: None
    ##  Returns:
    ##      response/object = HTTP response object on success, None on failure
    ##-----------------------------------------------------------------------
    def fetch_feed(self):

        req_headers = dict(self.feed_endpoint_headers or {})

        # Prepare auth headers (if configured)
        if self.feed_endpoint_auth_type == "basic":
            basic_auth = f"{self.feed_endpoint_auth_credentials_username}:{self.feed_endpoint_auth_credentials_password}".encode("utf-8")
            req_headers["Authorization"] = f"Basic {base64.b64encode(basic_auth).decode('utf-8')}"
        elif self.feed_endpoint_auth_type == "bearer":
            req_headers["Authorization"] = f"Bearer {self.feed_endpoint_auth_credentials_token}"

        # Create a masked copy of headers for logging (to hide sensitive credentials)
        log_headers = self.mask_sensitive_headers(req_headers)

        self.log(3, self.system_log_level, f"REQUEST URL: {self.feed_endpoint_url}, METHOD: {self.feed_endpoint_method}, HEADERS: {log_headers}")

        # Build the request
        request = urlrequest.Request(self.feed_endpoint_url, method=self.feed_endpoint_method, headers=req_headers)

        # Add payload if it's a POST request
        if self.feed_endpoint_method == "POST" and self.feed_endpoint_body:
            request.data = self.feed_endpoint_body.encode('utf-8')
            self.log(3, self.system_log_level, f"REQUEST PAYLOAD: {self.summarize_request_payload(self.feed_endpoint_body)}")

        if self.system_network_attempts > 0:
            attempts = self.system_network_attempts - 1
        else:
            attempts = 0

        def sleep(attempts_remaining, attempt_number):
            if attempts_remaining >= 0:
                base_delay = max(float(self.system_network_delay), 0.0)
                if base_delay <= 0:
                    return

                # Exponential backoff reduces repeated hot retry loops during upstream failures.
                retry_delay = min(base_delay * (2 ** max(attempt_number - 1, 0)), 60.0)
                self.log(3, self.system_log_level, f"Retry backoff: sleeping {retry_delay:.2f}s before next attempt.")
                time.sleep(retry_delay)

        count = 1
        error = ""
        while attempts >= 0:
            attempts -= 1
            try:
                if self.runtime_proxy_host is not None and self.runtime_proxy_port is not None:
                    self.log(2, self.system_log_level, f"Using proxy {self.runtime_proxy_scheme}://{self.runtime_proxy_host}:{self.runtime_proxy_port} for feed download.")
                    self.log(2, self.system_log_level, f"Attempting to download feed data from {self.feed_endpoint_url} (Attempt {count})... ")
                    proxy_auth_header = None
                    if self.runtime_proxy_auth:
                        if not self.runtime_proxy_username or not self.runtime_proxy_password:
                            raise ValueError("Proxy authentication is enabled, but proxy username/password were not fully provided.")

                        proxy_auth = f"{self.runtime_proxy_username}:{self.runtime_proxy_password}".encode("utf-8")
                        proxy_auth_header = f"Basic {base64.b64encode(proxy_auth).decode('utf-8')}"
                        proxy_username = urlparse.quote(self.runtime_proxy_username, safe="")
                        proxy_password = urlparse.quote(self.runtime_proxy_password, safe="")
                        localproxy = f"{self.runtime_proxy_scheme}://{proxy_username}:{proxy_password}@{self.runtime_proxy_host}:{self.runtime_proxy_port}"
                    else:
                        localproxy = f"{self.runtime_proxy_scheme}://{self.runtime_proxy_host}:{self.runtime_proxy_port}"

                    if self.runtime_proxy_scheme == "https":
                        parsed_feed_url = urlparse.urlsplit(self.feed_endpoint_url)
                        if parsed_feed_url.scheme not in ["http", "https"]:
                            raise ValueError(f"Unsupported feed URL scheme '{parsed_feed_url.scheme}' for HTTPS proxy transport.")

                        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=self.runtime_cafile)
                        request_headers = dict(request.header_items())

                        if parsed_feed_url.scheme == "https":
                            proxy_headers = {}
                            for header_name in list(request_headers.keys()):
                                if header_name.lower() == "proxy-authorization":
                                    proxy_headers["Proxy-Authorization"] = request_headers.pop(header_name)

                            if "Proxy-Authorization" not in proxy_headers and proxy_auth_header:
                                proxy_headers["Proxy-Authorization"] = proxy_auth_header

                            connection = HTTPSProxyTunnelConnection(
                                self.runtime_proxy_host,
                                self.runtime_proxy_port,
                                timeout=30,
                                context=context,
                                proxy_context=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=self.runtime_cafile),
                            )
                            connection.set_tunnel(
                                parsed_feed_url.hostname,
                                parsed_feed_url.port or 443,
                                headers=proxy_headers,
                            )

                            request_path = parsed_feed_url.path or "/"
                            if parsed_feed_url.query:
                                request_path = f"{request_path}?{parsed_feed_url.query}"
                        else:
                            if not any(header_name.lower() == "proxy-authorization" for header_name in request_headers) and proxy_auth_header:
                                request_headers["Proxy-Authorization"] = proxy_auth_header

                            connection = http.client.HTTPSConnection(
                                self.runtime_proxy_host,
                                self.runtime_proxy_port,
                                timeout=30,
                                context=context,
                            )
                            request_path = self.feed_endpoint_url

                        connection.request(
                            request.get_method(),
                            request_path,
                            body=request.data,
                            headers=request_headers,
                        )
                        res = connection.getresponse()
                        res._feedservice_connection = connection
                    else:
                        proxyctl = urlrequest.ProxyHandler({'https': localproxy,'http': localproxy})
                        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=self.runtime_cafile)
                        http_handler = urlrequest.HTTPHandler()
                        https_handler = urlrequest.HTTPSHandler(context=context)
                        opener = urlrequest.build_opener(https_handler, http_handler, proxyctl)
                        urlrequest.install_opener(opener)
                        res = urlrequest.urlopen(request, timeout=30)
                else:
                    self.log(2, self.system_log_level, f"Attempting to download feed data from {self.feed_endpoint_url} (Attempt {count})... ")
                    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=self.runtime_cafile)
                    http_handler = urlrequest.HTTPHandler()
                    https_handler = urlrequest.HTTPSHandler(context=context)
                    opener = urlrequest.build_opener(https_handler, http_handler)
                    urlrequest.install_opener(opener)
                    res = urlrequest.urlopen(request, timeout=30)

            except urlrequest.URLError as e:
                self.log(1, self.system_log_level, f"ERROR: Attempt {count} to fetch {self.feed_endpoint_url} failed (1111): {str(e.reason)}")
                sys.stderr.write(f"ERROR: Attempt {count} to fetch {self.feed_endpoint_url} failed (1111): {str(e.reason)}")
                count += 1
                error = str(e.reason)
                sleep(attempts, count - 1)
                continue

            except Exception as e:
                self.log(1, self.system_log_level, f"ERROR: Attempt {count} to fetch {self.feed_endpoint_url} failed (1112): {str(e)}")
                sys.stderr.write(f"ERROR: Attempt {count} to fetch {self.feed_endpoint_url} failed (1112): {str(e)}")
                count += 1
                error = str(e)
                sleep(attempts, count - 1)
                continue

            if res.getcode() != 200:
                self.log(1, self.system_log_level, f"ERROR: Attempt {count} to fetch {self.feed_endpoint_url} failed (1113)")
                sys.stderr.write(f"ERROR: Attempt {count} to fetch {self.feed_endpoint_url} failed (1113)")
                count += 1
                error = f"HTTP {res.getcode()}"
                sleep(attempts, count - 1)
                continue
            else:
                ## Looks good - return response
                return res

        self.log(1, self.system_log_level, f"ERROR: Failed all attempts to fetch {self.feed_endpoint_url}. Aborting until next scheduled run. Details: {error}")
        self.event_log(1, self.system_log_level, f"Failed all attempts to fetch {self.feed_endpoint_url}. Aborting until next scheduled run. Details: {error}")
        self.update_last_run(
            self.lastrun_hash,
            "error",
            0,
            None,
            f"Failed all {self.system_network_attempts} attempt(s) to fetch {self.feed_endpoint_url}. Aborting until next scheduled run. Details: {error}",
        )
        sys.stderr.write(f"ERROR: Failed all attempts to fetch {self.feed_endpoint_url}. Aborting until next scheduled run. Details: {error}")
        return None

    ##-----------------------------------------------------------------------
    ## decode_feed_data function
    ##  Purpose: decode raw feed bytes and normalize data to UTF-8 text
    ##  Parameters:
    ##      raw_data      = raw feed bytes from HTTP response
    ##      response      = optional urllib response object for charset hints
    ##-----------------------------------------------------------------------
    def decode_feed_data(self, raw_data, response=None):
        if raw_data is None:
            return None

        if isinstance(raw_data, str):
            return raw_data.lstrip("\ufeff").encode("utf-8", errors="replace").decode("utf-8")

        if not isinstance(raw_data, (bytes, bytearray)):
            raw_data = str(raw_data).encode("utf-8", errors="replace")

        raw_data = bytes(raw_data)

        candidate_encodings = []

        # Respect charset from HTTP headers when provided.
        if response is not None:
            try:
                header_encoding = response.headers.get_content_charset()
                if header_encoding:
                    candidate_encodings.append(header_encoding)
            except Exception:
                pass

        # Detect common BOM markers.
        if raw_data.startswith(b"\xef\xbb\xbf"):
            candidate_encodings.append("utf-8-sig")
        elif raw_data.startswith(b"\xff\xfe"):
            candidate_encodings.append("utf-16")
        elif raw_data.startswith(b"\xfe\xff"):
            candidate_encodings.append("utf-16")

        # Add fallback encodings frequently used by feeds.
        for encoding in ["utf-8", "utf-16", "iso-8859-1", "cp1252"]:
            if encoding not in candidate_encodings:
                candidate_encodings.append(encoding)

        for encoding in candidate_encodings:
            try:
                decoded = raw_data.decode(encoding)
                normalized = decoded.encode("utf-8", errors="replace").decode("utf-8")
                normalized = normalized.lstrip("\ufeff")
                if encoding.lower() not in ["utf-8", "utf-8-sig"]:
                    self.log(2, self.system_log_level, f"Feed data decoded using '{encoding}' and normalized to UTF-8.")
                return normalized
            except UnicodeDecodeError:
                continue
            except LookupError:
                continue

        self.log(2, self.system_log_level, "WARNING: Unable to confidently decode feed data; using UTF-8 with replacement for invalid bytes.")
        self.event_log(2, self.system_log_level, "Unable to confidently decode feed data; using UTF-8 with replacement for invalid bytes.")
        return raw_data.decode("utf-8", errors="replace").lstrip("\ufeff")

    ##-----------------------------------------------------------------------
    ## resolve_json_pointer function
    ##  Purpose: resolve an RFC 6901 JSON pointer against a JSON document
    ##  Parameters:
    ##      document        = parsed JSON document
    ##      pointer         = RFC 6901 pointer string
    ##  Returns:
    ##      any             = node resolved by pointer
    ##-----------------------------------------------------------------------
    def resolve_json_pointer(self, document, pointer):
        if pointer == "":
            return document

        if not isinstance(pointer, str):
            raise ValueError("JSON pointer must be a string.")

        if not pointer.startswith("/"):
            raise ValueError("JSON pointer must start with '/'.")

        current = document
        parts = pointer.split("/")[1:]

        for raw_part in parts:
            if re.search(r'~(?![01])', raw_part):
                raise ValueError(f"Invalid escape sequence in JSON pointer token '{raw_part}'.")

            token = raw_part.replace("~1", "/").replace("~0", "~")

            if isinstance(current, list):
                if not re.match(r'^\d+$', token):
                    raise KeyError(f"List token '{token}' is not a valid array index.")
                idx = int(token)
                if idx >= len(current):
                    raise KeyError(f"Array index {idx} is out of range.")
                current = current[idx]
                continue

            if isinstance(current, dict):
                if token not in current:
                    raise KeyError(f"Object key '{token}' not found.")
                current = current[token]
                continue

            raise KeyError(f"Cannot traverse into non-container node at token '{token}'.")

        return current

    ##-----------------------------------------------------------------------
    ## flatten_json_values function
    ##  Purpose: recursively collect string values from a JSON node
    ##  Parameters:
    ##      node            = JSON node (dict/list/scalar)
    ##  Returns:
    ##      list            = recursively collected non-empty string values
    ##-----------------------------------------------------------------------
    def flatten_json_values(self, node):
        values = []

        if node is None:
            return values

        if isinstance(node, str):
            text = node.strip()
            if text:
                values.append(text)
            return values

        if isinstance(node, list):
            for item in node:
                values.extend(self.flatten_json_values(item))
            return values

        if isinstance(node, dict):
            for item in node.values():
                values.extend(self.flatten_json_values(item))
            return values

        return values

    ##-----------------------------------------------------------------------
    ## save_feed_cache function
    ##  Purpose: persist latest decoded feed payload for no-fetch refresh operations
    ##  Parameters:
    ##      feed_data       = decoded feed payload text
    ##  Returns:
    ##      tuple           = (success boolean, error text)
    ##-----------------------------------------------------------------------
    def save_feed_cache(self, feed_data):
        if feed_data is None:
            return False, "No feed data supplied."

        cache_file = self.runtime_feed_cache_file
        if not cache_file:
            cache_file = f"{self.runtime_working_dir}/{self.feed_name}.feedcache"
            self.runtime_feed_cache_file = cache_file

        try:
            payload = str(feed_data)
            cache_record = {
                "schema_version": 1,
                "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "feed_name": self.feed_name,
                "source_format": self.feed_source_format,
                "payload_hash": self.get_hash(payload),
                "payload": payload,
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(self.to_canonical_json(cache_record))
            return True, ""
        except Exception as e:
            return False, str(e)

    ##-----------------------------------------------------------------------
    ## load_feed_cache function
    ##  Purpose: load cached feed payload for no-fetch refresh operations
    ##  Parameters: None
    ##  Returns:
    ##      string/None     = cached payload text if valid, otherwise None
    ##-----------------------------------------------------------------------
    def load_feed_cache(self):
        cache_file = self.runtime_feed_cache_file
        if not cache_file:
            cache_file = f"{self.runtime_working_dir}/{self.feed_name}.feedcache"
            self.runtime_feed_cache_file = cache_file

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_raw = f.read()

            cache_record = json.loads(cache_raw)
            if not isinstance(cache_record, dict):
                self.log(1, self.system_log_level, f"ERROR: Cached feed data format is invalid in {cache_file}: expected JSON object.")
                self.event_log(1, self.system_log_level, f"Cached feed data format is invalid in {cache_file}: expected JSON object.")
                return None

            schema_version = cache_record.get("schema_version")
            if schema_version != 1:
                self.log(1, self.system_log_level, f"ERROR: Unsupported cache schema_version '{schema_version}' in {cache_file}.")
                self.event_log(1, self.system_log_level, f"Unsupported cache schema_version '{schema_version}' in {cache_file}.")
                return None

            payload = cache_record.get("payload")
            if not isinstance(payload, str):
                self.log(1, self.system_log_level, f"ERROR: Cached payload is missing or invalid in {cache_file}.")
                self.event_log(1, self.system_log_level, f"Cached payload is missing or invalid in {cache_file}.")
                return None

            payload_hash = str(cache_record.get("payload_hash", ""))
            if payload_hash and payload_hash != self.get_hash(payload):
                self.log(2, self.system_log_level, f"WARNING: Cached payload hash mismatch in {cache_file}; payload may have been modified.")
                self.event_log(2, self.system_log_level, f"Cached payload hash mismatch in {cache_file}; payload may have been modified.")

            return payload
        except Exception as e:
            self.log(1, self.system_log_level, f"ERROR: Failed reading cached feed data from {cache_file}: {e}")
            self.event_log(1, self.system_log_level, f"Failed reading cached feed data from {cache_file}: {e}")
            return None

    ##-----------------------------------------------------------------------
    ## classify_domain function
    ##  Purpose: normalize, validate, and classify domain entries from feed data
    ##  Parameters:
    ##      domain          = domain string to be normalized, validated, and classified
    ##-----------------------------------------------------------------------
    def classify_domain(self, domain):

        ## Set default domain type
        entry_type = "DOMAIN"

        ## Set fdomain variable to be normalized and validated, while preserving original domain for logging purposes in case of errors
        fdomain = domain

        ## FORMAT: Remove scheme if present (ex. http://, https://, ftp://, etc.) - convert to www.example.com
        if "://" in fdomain:
            fdomain = fdomain.split("://")[1]

        ## FORMAT: Test for www.example.com/ => convert to www.example.com
        if fdomain.endswith("/"):
            fdomain = fdomain[:-1]

        ## Check total length - cannot be less than 3 characters
        if len(fdomain) < 3:
            return "REJECT", f"'{domain}' is too short to be valid."

        ## Check total length - cannot be more than 255 characters
        if len(fdomain) > 255:
            return "REJECT", f"'{domain}' exceeds 255 characters."
        
        ## Check for two or more subsequent wildcards
        if '**' in fdomain:
            return "REJECT", f"'{domain}' cannot contain multiple subsequent wildcards."
        
        ## Check for at least one period - hostnames not permitted, must be a domain
        if '.' not in fdomain and not fdomain.startswith('*') and not fdomain.endswith('*'):
            return "REJECT", f"'{domain}' must contain at least one period (hostnames are not permitted)."

        ## Character validation - domains can only contain letters, digits, hyphens, periods, and wildcards
        if not re.match(r'^[a-z0-9-.*]+$', fdomain):
            return "REJECT", f"'{domain}' contains invalid characters."
        
        ## All wildcard entry - entries must contain more than wildcards and periods to be valid
        if re.match(r'^[.*]+$', fdomain):
            return "REJECT", f"'{domain}' cannot be composed solely of wildcards and periods."
        
        ## TLD validation - the last label (TLD) must contain at least one letter and cannot be all numeric
        if not fdomain.endswith(".") and not fdomain.endswith("*"):
            if re.match(r'^[0-9-]+$', fdomain.split('.')[-1]):
                return "REJECT", f"'{domain}' has an invalid TLD."

        ## Label validation (empty labels)
        if '..' in fdomain:
            return "REJECT", f"'{domain}' has an empty label."

        ## Label validation - domain labels cannot exceed 63 characters and must not start or end with a hyphen
        labels = fdomain.split('.')
        for label in labels:
            if ( len(label) > 63 ):
                return "REJECT", f"'{domain}' has a label that exceeds 63 characters."
            if label.startswith('-') or label.endswith('-'):
                return "REJECT", f"'{domain}' has a label that starts or ends with a hyphen."

        ## Classify as wildcard domain if leading and/or trailing period
        if (fdomain.startswith('.') or fdomain.startswith('*')) and (fdomain.endswith('.') or fdomain.endswith('*')):
            entry_type = "WDOMAINW"
        elif fdomain.startswith('.') or fdomain.startswith('*'):
            entry_type = "WDOMAIN"
        elif fdomain.endswith('.') or fdomain.endswith('*'):
            entry_type = "DOMAINW"

        return entry_type, fdomain

    ##-----------------------------------------------------------------------
    ## classify_entry function
    ##  Purpose: determine if a feed entry is an IPv4 address/subnet, IPv6 address/subnet,
    ##           or domain (including wildcard domains), and validate and normalize accordingly
    ##  Parameters:
    ##      entry          = feed entry to classify, validate, and normalize
    ##-----------------------------------------------------------------------
    def classify_entry(self, entry):

        ## Is IPv4?
        try:
            iface = ipaddress.IPv4Interface(entry)
            network = iface.network
            # Enforce strict network: for prefixes < /32, the IP must be the network address (no host bits)
            if network.prefixlen < 32 and iface.ip != network.network_address:
                raise ValueError("Invalid network: host bits are set")
            normalized_entry = str(network)  # e.g., "192.168.1.1/32" or "192.168.24.0/24"
            self.log(3, self.system_log_level, f"Classified '{normalized_entry}' as IPv4")
            return "IPv4", normalized_entry
        except ValueError as e:
            if re.match(r'^\d{1,3}(\.\d{1,3}){3}(/)?(\d)*?$', entry) or re.match(r'^[0-9./]+$', entry):
                self.log(2, self.system_log_level, f"REJECTED: '{entry}' appears to be an IPv4 address but is invalid. Reason: {str(e)}.")
                return "REJECT", f"'{entry}' appears to be an IPv4 address but is invalid. Reason: {str(e)}."
            else:
                pass

        ## Is IPv6?
        try:
            ip = ipaddress.IPv6Network(entry, strict=True)
            self.log(3, self.system_log_level, f"Classified '{entry}' as IPv6")
            if ip.compressed != entry:
                self.log(3, self.system_log_level, f"Normalized '{entry}' to '{ip.compressed}'")
            return "IPv6", ip.compressed
        except ValueError as e:
            if re.match(r'^[0-9a-fA-F:]+(/\d{1,3})?$', entry):
                self.log(2, self.system_log_level, f"REJECTED: '{entry}' appears to be an IPv6 address but is invalid. Reason: {str(e)}.")
                return "REJECT", f"'{entry}' appears to be an IPv6 address but is invalid. Reason: {str(e)}."
            else:
                pass

        ## Is Domain?
        entry_type, domain = self.classify_domain(entry)
        if ( not entry_type ):
            self.log(2, self.system_log_level, f"WARNING: Classification of {entry} resulted in an unhandled error!")
            self.event_log(2, self.system_log_level, f"Classification of '{entry}' resulted in an unhandled error. Skipping entry.")
            return "REJECT", f"Classification of {entry} resulted in an unhandled error!"
        else:
            if entry_type == "REJECT":
                self.log(2, self.system_log_level, f"REJECTED: {domain}")
            else:
                self.log(3, self.system_log_level, f"Classified '{domain}' as { {'DOMAIN': 'domain name', 'WDOMAIN': 'wildcard domain (leading)', 'DOMAINW': 'wildcard domain (trailing)', 'WDOMAINW': 'wildcard domain (bookend)', 'REJECT': 'invalid entry'}.get(entry_type, 'invalid entry') }")
            return entry_type, domain

    ##-----------------------------------------------------------------------
    ## matches_ip_pattern function
    ##  Purpose: Check if an IP address/subnet matches an exclusion pattern (supports subnet matching)
    ##  Parameters:
    ##      feed_ip        = IP address/subnet from feed (e.g., "192.168.1.1/32" or "10.0.0.0/24")
    ##      exclusion_pattern = IP exclusion pattern (e.g., "10.0.0.0/8" or "192.168.1.1/32")
    ##  Returns: True if feed_ip matches the exclusion pattern, False otherwise
    ##-----------------------------------------------------------------------
    def matches_ip_pattern(self, feed_ip, exclusion_pattern):
        try:
            feed_network = ipaddress.ip_network(feed_ip, strict=False)
            exclusion_network = ipaddress.ip_network(exclusion_pattern, strict=False)
            # Check if feed network is contained within or equals the exclusion network
            return feed_network.subnet_of(exclusion_network) or feed_network == exclusion_network
        except ValueError:
            return False

    ##-----------------------------------------------------------------------
    ## matches_domain_pattern function
    ##  Purpose: Check if a domain matches an exclusion pattern using regex
    ##  Parameters:
    ##      feed_domain    = domain from feed (e.g., "example.com" or "foo.example.com")
    ##      exclusion_pattern = domain exclusion pattern (e.g., "*.example.com" or "example.com")
    ##  Returns: True if feed_domain matches the exclusion pattern, False otherwise
    ##-----------------------------------------------------------------------
    def matches_domain_pattern(self, feed_domain, exclusion_pattern):
        # Convert glob-style wildcard patterns to regex
        # Escape special regex characters first, then convert * to .*
        regex_pattern = re.escape(exclusion_pattern).replace(r'\*', '.*')
        regex_pattern = f'^{regex_pattern}$'  # Anchor to match full domain
        
        try:
            return re.match(regex_pattern, feed_domain) is not None
        except re.error as e:
            self.log(2, self.system_log_level, f"WARNING: Invalid regex pattern '{exclusion_pattern}': {str(e)}")
            self.event_log(2, self.system_log_level, f"Invalid regex pattern '{exclusion_pattern}': {str(e)}")
            return False

    ##-----------------------------------------------------------------------
    ## process_entry function
    ##  Purpose: process feed entry based on classification (IPv4, IPv6, DOMAIN, WDOMAIN, DOMAINW) and action ("add" or "remove")
    ##           entries that fail to meet minimum requirements are skipped, and entries that fail classification are logged as errors
    ##           when action is "remove", supports pattern matching for IP subnets and wildcard domains
    ##  Parameters:
    ##      entry          = feed entry to be processed (classification, normalization, and validation)
    ##      action         = "add" or "remove" - whether this entry should be added to or removed from the feed list (default is "add")
    ##      classify       = when False, skip normal classification and treat entry as domain-pattern removal
    ##-----------------------------------------------------------------------
    def process_entry(self, entry, action="add", classify=True):

        ## FORMAT: Remove whitespace
        entry = entry.strip()
        entry = entry.lstrip("\ufeff")

        ## FORMAT: Lowercase entry for consistent processing
        entry = entry.lower()

        ## If classify is False, skip validation and classification and match pattern directly against all domain-type lists
        if not classify:
            if action == "remove":
                removed_count = 0
                for list_type in ["DOMAIN", "WDOMAIN", "DOMAINW", "WDOMAINW"]:
                    removed_items = self.remove_feed_items_by_match(
                        list_type,
                        lambda feed_entry: self.matches_domain_pattern(feed_entry, entry),
                    )
                    for feed_entry in removed_items:
                        removed_count += 1
                        self.log(3, self.system_log_level, f"REMOVED: '{feed_entry}' from the {list_type} list (matched URL exclusion pattern '{entry}').")
                if removed_count > 0:
                    return True
                else:
                    self.log(3, self.system_log_level, f"SKIPPED: No matching entries found for URL exclusion pattern '{entry}'.")
                    return None
            return None

        ## FORMAT: Replace quotes with nothing (remove quotes)
        entry = entry.replace('"', '').replace("'", "")

        ## Skip entries that are too short to be valid
        if len(entry) < 4:
            # Don't log blank lines
            if entry != "":
                self.log(3, self.system_log_level, f"Skipping '{entry}' - entry is too short.")
            return None

        ## Skip commented lines (starting with # or //)
        if entry.startswith("#"):
            self.log(3, self.system_log_level, f"Skipping comment: {entry}")
            return None
        if entry.startswith("//"):
            self.log(3, self.system_log_level, f"Skipping comment: {entry}")
            return None
        
        ## Remove inline comments (anything following a # character)
        if '#' in entry:
            entry = entry.split('#', 1)[0].strip()
        
        ## Skip lines with spaces (invalid format for domain or IP entries)
        if ' ' in entry:
            self.log(3, self.system_log_level, f"Skipping '{entry}' - entry contains spaces and is not a valid format for domain or IP entries.")
            return None

        self.log(3, self.system_log_level, f"Processing '{entry}'")


        ## Classify (and normalize) entry
        entry_type, item = self.classify_entry(entry)

        ## Update applicable list based on classification and action
        if not entry_type:
            self.log(2, self.system_log_level, f"WARNING: Classification of '{entry}' resulted in an unhandled error. Skipping entry.")
            self.event_log(2, self.system_log_level, f"Classification of '{entry}' resulted in an unhandled error. Skipping entry.")
            return None
        elif entry_type == "REJECT":
            self.add_feed_item(entry_type, item)
            return None
        else:
            if action == "add":
                if self.add_feed_item(entry_type, item):
                    _entry_in_scope = (
                        (entry_type in ("IPv4", "IPv6") and self.feed_export_ip_datagroup) or
                        (entry_type in ("DOMAIN", "WDOMAIN", "DOMAINW", "WDOMAINW") and (self.feed_export_url_datagroup or self.feed_export_url_category))
                    )
                    if _entry_in_scope:
                        self.log(3, self.system_log_level, f"ADDED: '{item}' to {entry_type} list.")
                    return True
                else:
                    self.log(3, self.system_log_level, f"SKIPPED: '{item}' is already in the {entry_type} list, nothing to add.")
                    return None
            elif action == "remove":
                removed_count = 0
                
                # Handle IP pattern matching for IPv4 and IPv6
                if entry_type in ["IPv4", "IPv6"]:
                    removed_items = self.remove_feed_items_by_match(
                        entry_type,
                        lambda feed_entry: self.matches_ip_pattern(feed_entry, item),
                    )

                    for feed_entry in removed_items:
                        removed_count += 1
                        self.log(3, self.system_log_level, f"REMOVED: '{feed_entry}' from the {entry_type} list (matched pattern '{item}').")
                
                # Handle domain pattern matching for DOMAIN, WDOMAIN, DOMAINW, WDOMAINW
                elif entry_type in ["DOMAIN", "WDOMAIN", "DOMAINW", "WDOMAINW"]:
                    removed_items = self.remove_feed_items_by_match(
                        entry_type,
                        lambda feed_entry: self.matches_domain_pattern(feed_entry, item),
                    )

                    for feed_entry in removed_items:
                        removed_count += 1
                        self.log(3, self.system_log_level, f"REMOVED: '{feed_entry}' from the {entry_type} list (matched pattern '{item}').")
                
                if removed_count > 0:
                    return True
                else:
                    self.log(3, self.system_log_level, f"SKIPPED: No matching entries found for exclusion pattern '{item}' in {entry_type} list.")
                    return None
                
        self.log(3, self.system_log_level, f"Skipping '{entry}' - not a valid domain or IP address/subnet.")

        return None

    ##-----------------------------------------------------------------------
    ## update_url_category function
    ##  Purpose: Creates/updates Custom URL Category from supplied URL information
    ##  Parameters:
    ##      url_cat          = name of the Custom URL Category
    ##      url_list         = list of URLs
    ##      cat_action       = action to perform (allow, block, or confirm)
    ##      tmsh_commands    = optional list to append staged tmsh commands instead of applying immediately
    ##-----------------------------------------------------------------------
    def update_url_category(self, url_cat, url_list, cat_action, tmsh_commands=None):

        ## Initialize the url string
        urls_to_add = ""
        seen_urls = set()

        ## Create new or clean out existing Custom URL Category - add the latest version as first entry
        create_cmd = ""
        if not self.tmsh_object_exists(["/sys", "url-db", "url-category", url_cat]):
            create_cmd = f"create /sys url-db url-category {url_cat} display-name {url_cat} urls replace-all-with {{ https://{self.runtime_start_time.split(' ')[0]}/ {{ type exact-match }} }} default-action {cat_action}"

        ## Loop through URLs and insert into Custom URL Category
        for url in url_list:

            ## Escape asterisks in the URL
            url = url.replace('*', '\\*')

            ## Add \\* (escaped asterisk) if url starts and/or ends with "."
            if url.startswith("."):
                url = "\\*" + url
            if url.endswith("."):
                url = url + "\\*"

            ## Deduplicate using set membership instead of repeatedly scanning the growing output string.
            if url in seen_urls:
                self.log(3, self.system_log_level, f"SKIPPED: '{url}' is already in the URL list for Custom URL Category '{url_cat}'.")
                continue
            seen_urls.add(url)

            ## If URL contains an asterisk, set as a glob-match URL, otherwise exact-match
            if ('*' in url):
                urls_to_add = urls_to_add + " \"https://" + url + "/\" { type glob-match } \"http://" + url + "/\" { type glob-match }"
            else:
                urls_to_add = urls_to_add + " \"https://" + url + "/\" { type exact-match } \"http://" + url + "/\" { type exact-match }"

        ## Import the URL entries
        modify_cmd = f"modify /sys url-db url-category {url_cat} urls replace-all-with {{ https://{self.runtime_start_time.split(' ')[0]}/ {{ type exact-match }} {urls_to_add} }} default-action {cat_action}"

        if tmsh_commands is not None:
            if create_cmd:
                tmsh_commands.append(create_cmd)
                self.log(2, self.system_log_level, f"Custom URL Category '{url_cat}' create action staged in transaction.")
            tmsh_commands.append(modify_cmd)
            self.log(2, self.system_log_level, f"Custom URL Category '{url_cat}' update staged in transaction.")
            return True, f"Custom URL Category '{url_cat}' update staged in transaction."

        cmd_batch = []
        if create_cmd:
            cmd_batch.append(create_cmd)

        cmd_batch.append(modify_cmd)

        success, output = self.run_tmsh_commands(cmd_batch)
        if not success:
            return False, f"Custom URL Category '{url_cat}' update failed: {output}."

        if create_cmd:
            self.log(2, self.system_log_level, f"Custom URL Category '{url_cat}' created.")

        return True, f"Custom URL Category '{url_cat}' has been updated."


    ##-----------------------------------------------------------------------
    ## update_url_datagroup function
    ##  Purpose: Create/update URL Data Group from supplied URL information
    ##  Parameters:
    ##      dg_name         = name of the URL Data Group
    ##      url_list        = list of URLs
    ##      tmsh_commands   = optional list to append staged tmsh commands instead of applying immediately
    ##      cleanup_files   = optional list to collect temporary files for caller cleanup
    ##  Example:
    ##      self.update_url_datagroup(self.feed_export_url_datagroup + "_exact", self.feed_list["DOMAIN"])
    ##-----------------------------------------------------------------------
    def update_url_datagroup(self, dg_name, url_list, tmsh_commands=None, cleanup_files=None):

        tmp_file = f"{self.runtime_working_dir}/.{dg_name}"

        ## Write data to a file for import into Data Group
        try:
            with open(tmp_file, 'w') as fout:
                for url in sorted(url_list):

                    ## If URL contains an asterisk that is not at the beginning or end of the domain, reject
                    ## the entry (asterisks are only allowed at the beginning or end of the domain for wildcard matching)
                    if '*' in url[1:-1]:
                        self.log(2, self.system_log_level, f"WARNING: '{url}' cannot be imported into {dg_name}. Please use the Custom URL Category for entries with asterisks in the middle of the domain.")
                        self.event_log(2, self.system_log_level, f"'{url}' cannot be imported into {dg_name}. Please use the Custom URL Category for entries with asterisks in the middle of the domain.")
                        continue
                    elif '*' in url:
                        ## Remove asterisk(s) from domain before import
                        url = url.replace('*', '')

                    fout.write("\"" + str(url) + "\" := \"\",\n")
        except (OSError, IOError) as e:
            return False, f"Could not write URL Data Group file {dg_name}: {e}"

        sys_file_exists = self.tmsh_object_exists(["/sys", "file", "data-group", dg_name])
        ltm_external_exists = self.tmsh_object_exists(["/ltm", "data-group", "external", dg_name])

        cmd_batch = []

        if not sys_file_exists:
            cmd_batch.append(f"create /sys file data-group {dg_name} separator \":=\" source-path file:{tmp_file} type string")

        if not ltm_external_exists:
            cmd_batch.append(f"create /ltm data-group external {dg_name} external-file-name {dg_name}")

        if sys_file_exists:
            cmd_batch.append(f"modify /sys file data-group {dg_name} source-path file:{tmp_file}")

        if tmsh_commands is not None:
            tmsh_commands.extend(cmd_batch)
            if cleanup_files is not None:
                cleanup_files.append(tmp_file)
            if not sys_file_exists:
                self.log(2, self.system_log_level, f"URL Data Group file '{dg_name}' create action staged in transaction.")
            if not ltm_external_exists:
                self.log(2, self.system_log_level, f"URL Data Group external object '{dg_name}' create action staged in transaction.")
            self.log(2, self.system_log_level, f"URL Data Group '{dg_name}' update staged in transaction.")
            return True, f"Data Group '{dg_name}' update staged in transaction."

        success, output = self.run_tmsh_commands(cmd_batch)
        if not success:
            os.remove(tmp_file)
            return False, f"Data Group '{dg_name}' update failed: {output}"

        os.remove(tmp_file)
        return True, f"Data Group '{dg_name}' has been updated."

    ##-----------------------------------------------------------------------
    ## update_ip_datagroup function
    ##  Purpose: Create/update IP Data Group using supplied IP addresses
    ##  Parameters:
    ##      dg_name         = name of IP Data Group
    ##      ip_list         = list of IP addresses
    ##      tmsh_commands   = optional list to append staged tmsh commands instead of applying immediately
    ##      cleanup_files   = optional list to collect temporary files for caller cleanup
    ##  Example:
    ##      self.update_ip_datagroup (self.feed_export_ip_datagroup + "_ipv4", self.feed_list["IPv4"])
    ##-----------------------------------------------------------------------
    def update_ip_datagroup(self, dg_name, ip_list, tmsh_commands=None, cleanup_files=None):

        tmp_file = f"{self.runtime_working_dir}/.{dg_name}"

        ## Write data to a file for import into Data Group
        try:
            with open(tmp_file, 'w') as fout:
                for ip in sorted(ip_list):
                    fout.write("network " + str(ip) + ",\n")
        except (OSError, IOError) as e:
            return False, f"Could not write to IP Data Group file {dg_name}: {e}"

        ## Create or repair IP Data Group objects in TMSH when missing.
        sys_file_exists = self.tmsh_object_exists(["/sys", "file", "data-group", dg_name])
        ltm_external_exists = self.tmsh_object_exists(["/ltm", "data-group", "external", dg_name])

        cmd_batch = []

        if not sys_file_exists:
            cmd_batch.append(f"create /sys file data-group {dg_name} source-path file:{tmp_file} type ip")

        if not ltm_external_exists:
            cmd_batch.append(f"create /ltm data-group external {dg_name} external-file-name {dg_name}")

        if sys_file_exists:
            cmd_batch.append(f"modify /sys file data-group {dg_name} source-path file:{tmp_file}")

        if tmsh_commands is not None:
            tmsh_commands.extend(cmd_batch)
            if cleanup_files is not None:
                cleanup_files.append(tmp_file)
            if not sys_file_exists:
                self.log(2, self.system_log_level, f"IP Data Group file '{dg_name}' create action staged in transaction.")
            if not ltm_external_exists:
                self.log(2, self.system_log_level, f"IP Data Group external object '{dg_name}' create action staged in transaction.")
            self.log(2, self.system_log_level, f"IP Data Group '{dg_name}' update staged in transaction.")
            return True, f"Data Group '{dg_name}' update staged in transaction."

        success, output = self.run_tmsh_commands(cmd_batch)
        if not success:
            os.remove(tmp_file)
            return False, f"Data Group '{dg_name}' update failed: {output}"

        os.remove(tmp_file)
        return True, f"Data Group '{dg_name}' has been updated."

    ##-----------------------------------------------------------------------
    ## process_feed function
    ##  Purpose: Process feed data based on feed configuration parameters, including classification, normalization,
    ##           and validation of feed entries, as well as processing of user-defined exclusions and inclusions
    ##  Parameters:
    ##      data          = raw feed data to be processed
    ##-----------------------------------------------------------------------
    def process_feed(self, data):
        ## Check if fetch failed (data is None)
        if data is None:
            self.log(1, self.system_log_level, f"ERROR: Failed to fetch data.")
            self.event_log(1, self.system_log_level, f"Failed to fetch data.")
            self.update_last_run(self.lastrun_hash, "error", 0, None, "Failed to fetch data.")
            return None

        if isinstance(data, str):
            data = data.lstrip("\ufeff")

        if self.feed_source_format == "line":
            data_list = data.splitlines()
        elif self.feed_source_format == "regex":
            try:
                regex_matches = re.findall(self.feed_source_regex, data)
            except re.error as e:
                error_msg = f"Regex feed parsing failed: {e}."
                self.log(1, self.system_log_level, f"ERROR: {error_msg}")
                self.event_log(1, self.system_log_level, error_msg)
                self.update_last_run(self.lastrun_hash, "error", 0, None, error_msg)
                return None
            # Handle grouped regex where findall() returns tuples.
            data_list = [m[0] if isinstance(m, tuple) else m for m in regex_matches]
        elif self.feed_source_format == "csv":
            data_list = []
            self.log(3, self.system_log_level, f"CSV parsing options: column={self.feed_source_csv_position}, has_header={self.feed_source_csv_has_header}, skipinitialspace=True")
            for line_num, row in enumerate(csv.reader(data.splitlines(), skipinitialspace=True), start=1):
                if self.feed_source_csv_has_header and line_num == 1:
                    self.log(3, self.system_log_level, "Skipping CSV header row.")
                    continue
                if len(row) <= self.feed_source_csv_position:
                    self.log(2, self.system_log_level, f"Skipping CSV row {line_num}: expected column index {self.feed_source_csv_position}, row has {len(row)} column(s).")
                    continue
                item = self.normalize_source_item(row[self.feed_source_csv_position])
                if item:
                    data_list.append(item)
        elif self.feed_source_format == "delimited":
            if not self.feed_source_delimiter:
                self.log(1, self.system_log_level, f"ERROR: Delimited format specified but no delimiter provided.")
                self.event_log(1, self.system_log_level, f"Delimited format specified but no delimiter provided.")
                self.update_last_run(self.lastrun_hash, "error", 0, None, "Delimited format specified but no delimiter provided.")
                return None
            data_list = []
            for line in data.splitlines():
                for part in line.split(self.feed_source_delimiter):
                    part = self.normalize_source_item(part)
                    if part:
                        data_list.append(part)
        elif self.feed_source_format == "json":
            try:
                json_document = json.loads(data)
            except json.JSONDecodeError as e:
                error_msg = f"JSON feed parsing failed: {e.msg} (line {e.lineno}, col {e.colno})."
                self.log(1, self.system_log_level, f"ERROR: {error_msg}")
                self.event_log(1, self.system_log_level, error_msg)
                self.update_last_run(self.lastrun_hash, "error", 0, None, error_msg)
                return None

            data_list = []
            if self.feed_source_json_mode == "document":
                data_list = self.flatten_json_values(json_document)
                self.log(3, self.system_log_level, f"JSON document mode yielded {len(data_list)} value(s).")
            else:
                if not self.feed_source_json_pointers:
                    self.log(1, self.system_log_level, "ERROR: JSON format with pointer mode requires one or more JSON pointers.")
                    self.event_log(1, self.system_log_level, "JSON format with pointer mode requires one or more JSON pointers.")
                    self.update_last_run(self.lastrun_hash, "error", 0, None, "JSON format with pointer mode requires one or more JSON pointers.")
                    return None

                strict_mode = bool(self.feed_source_json_pointer_strict)

                for pointer in self.feed_source_json_pointers:
                    pointer_str = str(pointer).strip()
                    if not pointer_str:
                        message = "Encountered an empty JSON pointer."
                        if strict_mode:
                            self.log(1, self.system_log_level, f"ERROR: {message}")
                            self.event_log(1, self.system_log_level, message)
                            self.update_last_run(self.lastrun_hash, "error", 0, None, message)
                            return None
                        self.log(2, self.system_log_level, f"WARNING: {message}")
                        self.event_log(2, self.system_log_level, message)
                        continue

                    try:
                        pointer_node = self.resolve_json_pointer(json_document, pointer_str)
                    except Exception as e:
                        message = f"JSON pointer '{pointer_str}' could not be resolved: {e}"
                        if strict_mode:
                            self.log(1, self.system_log_level, f"ERROR: {message}")
                            self.event_log(1, self.system_log_level, message)
                            self.update_last_run(self.lastrun_hash, "error", 0, None, message)
                            return None
                        self.log(2, self.system_log_level, f"WARNING: {message}")
                        self.event_log(2, self.system_log_level, message)
                        continue

                    extracted_values = self.flatten_json_values(pointer_node)
                    if not extracted_values:
                        message = f"JSON pointer '{pointer_str}' resolved but yielded no string values."
                        if strict_mode:
                            self.log(1, self.system_log_level, f"ERROR: {message}")
                            self.event_log(1, self.system_log_level, message)
                            self.update_last_run(self.lastrun_hash, "error", 0, None, message)
                            return None
                        self.log(2, self.system_log_level, f"WARNING: {message}")
                        self.event_log(2, self.system_log_level, message)
                        continue

                    data_list.extend(extracted_values)
                    self.log(3, self.system_log_level, f"JSON pointer '{pointer_str}' yielded {len(extracted_values)} value(s).")
        else:
            self.log(1, self.system_log_level, f"ERROR: '{self.feed_source_format}' is not a supported format.")
            self.event_log(1, self.system_log_level, f"'{self.feed_source_format}' is not a supported format.")
            self.update_last_run(self.lastrun_hash, "error", 0, None, f"'{self.feed_source_format}' is not a supported format.")
            return None

        ## Normalize parsed entries to strings before processing
        data_list = [str(entry) for entry in data_list if entry is not None]

        ## Check if any data to process after parsing feed data based on specified format, and log error if no data to process
        if len(data_list) == 0:
            self.log(1, self.system_log_level, f"ERROR: No data to process from feed.")
            self.event_log(1, self.system_log_level, f"No data to process from feed.")
            self.update_last_run(self.lastrun_hash, "error", 0, None, "No data to process from feed.")
            return None
            
        ## Process feed list entries
        for entry in data_list:
            self.process_entry(entry, action="add")

        ## Process user-defined IP exclusions
        if self.feed_export_ip_datagroup:
            self.log(3, self.system_log_level, "-------------------------------------")
            self.log(3, self.system_log_level, f"Processing user-defined IP exclusions")
            self.log(3, self.system_log_level, "-------------------------------------")
            if not self.feed_import_ip_exclusions:
                self.log(3, self.system_log_level, f"No user-defined IP exclusions to process.")
            else:
                for entry in self.feed_import_ip_exclusions:
                    result = self.process_entry(entry, action="remove")
                    if result:
                        self.log(3, self.system_log_level, f"Processed IP exclusion: '{entry}'")

        ## Process user-defined URL exclusions
        if self.feed_export_url_datagroup or self.feed_export_url_category:
            self.log(3, self.system_log_level, "--------------------------------------")
            self.log(3, self.system_log_level, f"Processing user-defined URL exclusions")
            self.log(3, self.system_log_level, "--------------------------------------")
            if not self.feed_import_url_exclusions:
                self.log(3, self.system_log_level, f"No user-defined URL exclusions to process.")
            else:
                for entry in self.feed_import_url_exclusions:
                    result = self.process_entry(entry, action="remove", classify=False)
                    if result:
                        self.log(3, self.system_log_level, f"Processed URL exclusion: '{entry}'")

        ## Process user-defined IP inclusions (inclusions run last thus take precedence over exclusions)
        if self.feed_export_ip_datagroup:
            self.log(3, self.system_log_level, "-------------------------------------")
            self.log(3, self.system_log_level, f"Processing user-defined IP inclusions")
            self.log(3, self.system_log_level, "-------------------------------------")
            if not self.feed_export_ip_include:
                self.log(3, self.system_log_level, f"No user-defined IP inclusions to process.")
            else:
                for entry in self.feed_export_ip_include:
                    self.process_entry(entry, action="add")

        ## Process user-defined URL inclusions (inclusions run last thus take precedence over exclusions)
        if self.feed_export_url_datagroup or self.feed_export_url_category:
            self.log(3, self.system_log_level, "--------------------------------------")
            self.log(3, self.system_log_level, f"Processing user-defined URL inclusions")
            self.log(3, self.system_log_level, "--------------------------------------")
            if not self.feed_export_url_include:
                self.log(3, self.system_log_level, f"No user-defined URL inclusions to process.")
            else:
                for entry in self.feed_export_url_include:
                    self.process_entry(entry, action="add")

        ## Count only entries that are mapped to enabled export targets.
        importable_categories = self.get_importable_categories()
        import_count = sum(len(self.feed_list.get(category, [])) for category in importable_categories)
        if import_count == 0:
            if not (self.feed_export_ip_datagroup or self.feed_export_url_datagroup or self.feed_export_url_category):
                message = "No export targets are configured; feed entries were processed but none are eligible for import."
            else:
                message = "No importable entries found after processing for the configured export targets. Please review feed data, exclusions, and export settings."

            self.log(1, self.system_log_level, f"ERROR: {message}")
            self.event_log(1, self.system_log_level, message)
            self.update_last_run("", "error", 0, [], message)
            return None

        ## Feed processing summary logging
        self.log(2, self.system_log_level, "---------------------------")
        self.log(2, self.system_log_level, f"- Feed Processing Summary -")
        self.log(2, self.system_log_level, "---------------------------")
        for category in importable_categories:
            self.log(2, self.system_log_level, f"{category.upper()}: {len(self.feed_list.get(category, []))}")
        self.log(2, self.system_log_level, f"-------------------------------")
        self.log(2, self.system_log_level, f"Rejected items:  {len(self.feed_list['REJECT'])}")
        self.log(2, self.system_log_level, f"Items to import: {import_count}")
        self.log(2, self.system_log_level, f"-------------------------------")

        ## Hash normalized sorted feed contents so dynamic payload metadata does not force updates.
        new_hash = self.get_feed_content_hash()
        self.log(3, self.system_log_level, f"Previous Hash: {self.lastrun_hash}")
        self.log(3, self.system_log_level, f"Current Hash:  {new_hash}")

        if not self.runtime_force and not self.runtime_offline_update and new_hash == self.lastrun_hash:
            self.log(2, self.system_log_level, f"No changes detected in normalized feed contents since last update. Skipping processing.")
            lastrun_written = self.update_last_run(self.lastrun_hash, "nochange", 0, None, "No changes detected in normalized feed contents since last update.")
            if self.system_sync_update and lastrun_written:
                sync_success, sync_message = self.config_sync()
                if sync_success:
                    self.log(2, self.system_log_level, sync_message)
                else:
                    self.log(1, self.system_log_level, f"ERROR: {sync_message}")
                    self.event_log(1, self.system_log_level, f"ERROR: {sync_message}")
            return None

        ## Detailed logging of feed contents (debug level logging)
        _ip_in_scope  = bool(self.feed_export_ip_datagroup)
        _url_in_scope = bool(self.feed_export_url_datagroup or self.feed_export_url_category)
        _scope_map = {
            "IPv4":    _ip_in_scope,
            "IPv6":    _ip_in_scope,
            "DOMAIN":  _url_in_scope,
            "WDOMAIN": _url_in_scope,
            "DOMAINW": _url_in_scope,
            "WDOMAINW":_url_in_scope,
            "REJECT":  True,
        }
        for name, lst in self.feed_list.items():
            if _scope_map.get(name, True):
                self.log(3, self.system_log_level, f"{name.upper()} contains {len(lst)} items: {', '.join(f'{item}' for item in lst)}")

        ## Check if delta between current feed data and last feed data is significantly lower based on configured threshold
        ## This is to catch potential issues with feed processing that may result in significant changes to feed data, such as
        ## changes to feed format that cause feed entries to be rejected, or other processing errors that may cause feed entries to be skipped.
        if (not self.runtime_offline_update) and import_count < self.lastrun_count and (abs(import_count - self.lastrun_count) / self.lastrun_count) > (self.system_exceptions_delta_value / 100):
            delta = f"{(abs(import_count - self.lastrun_count) / self.lastrun_count) * 100:.0f}%"
            if self.system_exceptions_delta_action == "log":
                self.log(2, self.system_log_level, f"WARNING: {delta} decrease in feed data since last update. Proceeding with import operation.")
                self.event_log(2, self.system_log_level, f"{delta} decrease in feed data since last update. Proceeding with import operation.")
            elif self.system_exceptions_delta_action == "abort":
                self.log(1, self.system_log_level, f"ERROR: {delta} decrease in feed data since last update. Import aborted. Please review feed data and processing logs to ensure feed is being processed correctly.")
                self.event_log(1, self.system_log_level, f"{delta} decrease in feed data since last update. Import aborted.")
                lastrun_written = self.update_last_run(self.lastrun_hash, "error", 0, None, f"{delta} decrease in feed data since last update. Import aborted.")
                if self.system_sync_update and lastrun_written:
                    sync_success, sync_message = self.config_sync()
                    if sync_success:
                        self.log(2, self.system_log_level, sync_message)
                    else:
                        self.log(1, self.system_log_level, f"ERROR: {sync_message}")
                        self.event_log(1, self.system_log_level, f"ERROR: {sync_message}")
                return None

        ## Initialize success variable to track overall success of feed processing and updates
        result = True
        updates_applied = False

        ## Update IP Data Groups, URL Data Groups, and URL category in one TMSH transaction.
        if self.feed_export_ip_datagroup or self.feed_export_url_datagroup or self.feed_export_url_category:
            transaction_commands = []
            cleanup_files = []
            stage_success = True

            if self.feed_export_ip_datagroup:
                if self.feed_export_ip_combine:
                    success, message = self.update_ip_datagroup(
                        self.feed_export_ip_datagroup + "_ip",
                        self.feed_list["IPv4"] + self.feed_list["IPv6"],
                        tmsh_commands=transaction_commands,
                        cleanup_files=cleanup_files,
                    )
                    if not success:
                        self.log(1, self.system_log_level, f"ERROR: {message}")
                        self.event_log(1, self.system_log_level, message)
                    stage_success &= success

                else:
                    success, message = self.update_ip_datagroup(
                        self.feed_export_ip_datagroup + "_ipv4",
                        self.feed_list["IPv4"],
                        tmsh_commands=transaction_commands,
                        cleanup_files=cleanup_files,
                    )
                    if not success:
                        self.log(1, self.system_log_level, f"ERROR: {message}")
                        self.event_log(1, self.system_log_level, message)
                    stage_success &= success

                    success, message = self.update_ip_datagroup(
                        self.feed_export_ip_datagroup + "_ipv6",
                        self.feed_list["IPv6"],
                        tmsh_commands=transaction_commands,
                        cleanup_files=cleanup_files,
                    )
                    if not success:
                        self.log(1, self.system_log_level, f"ERROR: {message}")
                        self.event_log(1, self.system_log_level, message)
                    stage_success &= success

            if self.feed_export_url_datagroup:
                success, message = self.update_url_datagroup(
                    self.feed_export_url_datagroup + "_exact",
                    self.feed_list["DOMAIN"],
                    tmsh_commands=transaction_commands,
                    cleanup_files=cleanup_files,
                )
                if not success:
                    self.log(1, self.system_log_level, f"ERROR: {message}")
                    self.event_log(1, self.system_log_level, message)
                stage_success &= success

                success, message = self.update_url_datagroup(
                    self.feed_export_url_datagroup + "_contains",
                    self.feed_list["WDOMAINW"],
                    tmsh_commands=transaction_commands,
                    cleanup_files=cleanup_files,
                )
                if not success:
                    self.log(1, self.system_log_level, f"ERROR: {message}")
                    self.event_log(1, self.system_log_level, message)
                stage_success &= success

                success, message = self.update_url_datagroup(
                    self.feed_export_url_datagroup + "_startswith",
                    self.feed_list["DOMAINW"],
                    tmsh_commands=transaction_commands,
                    cleanup_files=cleanup_files,
                )
                if not success:
                    self.log(1, self.system_log_level, f"ERROR: {message}")
                    self.event_log(1, self.system_log_level, message)
                stage_success &= success

                success, message = self.update_url_datagroup(
                    self.feed_export_url_datagroup + "_endswith",
                    self.feed_list["WDOMAIN"],
                    tmsh_commands=transaction_commands,
                    cleanup_files=cleanup_files,
                )
                if not success:
                    self.log(1, self.system_log_level, f"ERROR: {message}")
                    self.event_log(1, self.system_log_level, message)
                stage_success &= success

            if self.feed_export_url_category:
                success, message = self.update_url_category(
                    self.feed_export_url_category,
                    self.feed_list["DOMAIN"] + self.feed_list["DOMAINW"] + self.feed_list["WDOMAIN"] + self.feed_list["WDOMAINW"],
                    self.feed_export_url_cataction,
                    tmsh_commands=transaction_commands,
                )
                if not success:
                    self.log(1, self.system_log_level, f"ERROR: {message}")
                    self.event_log(1, self.system_log_level, message)
                stage_success &= success

            if not stage_success:
                result = False
                self.log(1, self.system_log_level, f"ERROR: There was an error staging the TMSH transaction. No updates have been applied.")
                self.event_log(1, self.system_log_level, f"There was an error staging the TMSH transaction. No updates have been applied.")
            elif transaction_commands:
                success, message = self.run_tmsh_commands(transaction_commands, use_transaction=True)
                if not success:
                    result = False
                    self.log(1, self.system_log_level, f"ERROR: TMSH transaction failed and was rolled back: {message}")
                    self.event_log(1, self.system_log_level, f"TMSH transaction failed and was rolled back: {message}")
                else:
                    updates_applied = True
                    self.log(2, self.system_log_level, "TMSH transaction submitted successfully.")

            for tmp_file in cleanup_files:
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass

        ## Persist last run data before optional ConfigSync so state is included when syncing.
        if result:
            final_status = "updated" if updates_applied else "nochange"
            if self.runtime_offline_update:
                final_detail = "Object refresh completed; datagroups and URL category were updated from cached feed data." if updates_applied else "Object refresh completed; no BIG-IP object changes were required."
            else:
                final_detail = "Feed processing completed; configuration objects were updated." if updates_applied else "Feed processing completed; no BIG-IP object changes were required."
            lastrun_written = self.update_last_run(new_hash, final_status, import_count, self.feed_list["REJECT"], final_detail)
        else:
            lastrun_written = self.update_last_run(self.lastrun_hash, "error", import_count, None, "Feed processing completed with errors.")

        ## Run ConfigSync when sync-on-update is enabled and either BIG-IP objects were updated or
        ## the last-run data group was written (e.g. a nochange run where the hash or status changed).
        ## updates_applied is True in exactly three cases:
        ##   1. Normal run where the feed data hash changed (data diff).
        ##   2. --force run where the hash check was bypassed.
        ##   3. --offline-update run where objects were rebuilt from cached feed data.
        ## lastrun_written is True whenever update_last_run persisted new data to the data group.
        ## This runs after update_last_run so the latest last-run state is included in the synced config.
        if self.system_sync_update and (updates_applied or lastrun_written):
            sync_success, sync_message = self.config_sync()
            if sync_success:
                self.log(2, self.system_log_level, sync_message)
            else:
                self.log(1, self.system_log_level, f"ERROR: {sync_message}")
                self.event_log(1, self.system_log_level, f"ERROR: {sync_message}")
            result &= sync_success

        ## Log final status of feed processing and updates
        if result:
            self.log(2, self.system_log_level, f"Feed processing and BIG-IP object updates all completed successfully.")
        else:
            self.log(1, self.system_log_level, f"ERROR: Feed processing resulted in one or more errors. Please review log for details.")
            self.event_log(1, self.system_log_level, f"Feed processing resulted in one or more errors. Please review {self.runtime_working_dir}/{self.feed_name}.log for details.")

    ##-----------------------------------------------------------------------
    ## update_feed function
    ##  Purpose: Main worker function to update feed based on configuration parameters, including fetching feed data and processing feed data
    ##  Parameters: None
    ##  Returns: None
    ##-----------------------------------------------------------------------
    def update_feed(self):

        if self.runtime_offline_update:
            self.log(1, 1, "Offline update mode enabled; remote fetch will be skipped and cached feed data will be used to update datagroups and URL categories.")

        if self.runtime_force:
            self.log(1, 1, "Force mode enabled; feed hash comparison will be ignored.")
            self.reset_force_option()

        self.log(1, 1, "feedService update started.")

        # Fetch the config (will use already-loaded config if passed via --config-json)
        self.load_config()

        # Fetch last run information
        self.load_last_run()

        if self.runtime_offline_update:
            cached_feed_data = self.load_feed_cache()
            if cached_feed_data is None:
                message = "Offline update requested, but no cached feed data was found. Run a normal feed update first."
                self.log(1, self.system_log_level, f"ERROR: {message}")
                self.event_log(1, self.system_log_level, message)
                self.update_last_run(self.lastrun_hash, "error", self.lastrun_count, None, message)
                self.log(1, self.system_log_level, "feedService finished.")
                return

            # Force processing of cached payload so object refresh is not blocked by unchanged hash.
            original_force_mode = self.runtime_force
            self.runtime_force = True
            self.process_feed(cached_feed_data)
            self.runtime_force = original_force_mode
            self.log(1, self.system_log_level, "feedService finished.")
            return

        ## Fetch the feed data
        res = self.fetch_feed()
    
        if res:
            raw_feed_data = res.read()
            decoded_feed_data = self.decode_feed_data(raw_feed_data, res)
            cache_saved, cache_error = self.save_feed_cache(decoded_feed_data)
            if not cache_saved:
                self.log(2, self.system_log_level, f"WARNING: Failed to update feed cache file: {cache_error}")
                self.event_log(2, self.system_log_level, f"Failed to update feed cache file: {cache_error}")
            self.process_feed(decoded_feed_data)
        else:
            self.log(1, self.system_log_level, f"ERROR: Failed to fetch data.")
            self.event_log(1, self.system_log_level, "Failed to fetch data.")

        self.log(1, self.system_log_level, "feedService finished.")

##-----------------------------------------------------------------------
## main function
##  Purpose: parse CLI arguments, initialize runtime state, and execute a feed update run
##  Parameters: None
##-----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Feed service updater")
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force update even if feed hash has not changed"
    )
    parser.add_argument(
        "--config-json",
        type=str,
        default=None,
        help="Base64-encoded JSON configuration to use instead of looking for iFile (for bootstrap operations)"
    )
    parser.add_argument(
        "--offline-update",
        action="store_true",
        help="Update BIG-IP datagroups and URL objects from cached feed data without fetching remote feed"
    )

    args = parser.parse_args()

    fS = feedService()
    
    ## Set runtime variables
    script_ref = os.path.realpath(__file__)

    ## Find feed name from script filename using regex matching for BIG-IP iFile filestore format
    filestore_match = re.search(r":Common:(?P<name>[^:]+)\.app:(?P=name)\.py(?:_\d+_\d+)?$", script_ref)

    ## Fallback for running as a normal script filename from working directory (e.g. Zoom.py)
    simple_match = re.search(r"(?P<name>[^\\/]+)\.py$", script_ref)

    if filestore_match:
        fS.feed_name = filestore_match.group("name")
    elif simple_match:
        fS.feed_name = simple_match.group("name")
    else:
        print(
            "ERROR: Script name does not match expected BIG-IP filestore format "
            "':Common:<name>.app:<name>.py_<id>_<id>' or simple '<name>.py'. Aborting (1114).",
            file=sys.stderr,
        )
        sys.exit(1)

    fS.runtime_working_dir = "/shared/feedService/" + fS.feed_name
    fS.runtime_log_file = f"{fS.runtime_working_dir}/{fS.feed_name}.log"
    fS.runtime_feed_cache_file = f"{fS.runtime_working_dir}/{fS.feed_name}.feedcache"
    fS.runtime_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fS.runtime_force = args.force
    fS.runtime_offline_update = args.offline_update

    fS.log(1, 1, "")
    fS.log(1, 1, f"{'=' * (len(f'feedService initiated for {fS.feed_name}') + 6)}")
    fS.log(1, 1, f"= feedService initiated for '{fS.feed_name}' =")
    fS.log(1, 1, f"{'=' * (len(f'feedService initiated for {fS.feed_name}') + 6)}")

    # If config JSON is provided via argument, decode it and set it directly
    if args.config_json:
        try:
            decoded_json = base64.b64decode(args.config_json).decode('utf-8')
            fS.runtime_config_data = json.loads(decoded_json)
            fS.log(1, 1, f"Running with configuration provided via --config-json argument.")
        except Exception as e:
            fS.log(1, 1, f"ERROR: Failed to decode or parse --config-json argument: {e} (1115).")
            fS.event_log(1, 1, f"Failed to decode or parse --config-json argument: {e} (1115).")
            sys.exit(1)

    try:
        fS.update_feed()
    except KeyboardInterrupt:
        raise
    except Exception as e:
        error_message = f"Unhandled exception during feed update: {e} (1116)."
        try:
            fS.log(1, 1, f"ERROR: {error_message}")
            fS.event_log(1, 1, error_message)
            fS.update_last_run(fS.lastrun_hash, "error", fS.lastrun_count, None, error_message)
        except Exception:
            pass

        print(f"ERROR: {error_message}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()