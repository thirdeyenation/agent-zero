from python.helpers.extension import Extension
import os
import psutil


class SystemResourcesCheck(Extension):
    async def execute(self, banners: list = [], frontend_context: dict = {}, **kwargs):
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
        except Exception:
            cpu_percent = None

        load_avg = self._get_load_average()

        try:
            vm = psutil.virtual_memory()
            ram_percent = vm.percent
        except Exception:
            ram_percent = None

        disk_percent, disk_path = self._get_disk_usage_percent()

        try:
            net = psutil.net_io_counters()
            net_sent = self._format_bytes(net.bytes_sent)
            net_recv = self._format_bytes(net.bytes_recv)
        except Exception:
            net_sent = "N/A"
            net_recv = "N/A"

        load_value = "N/A"
        if load_avg:
            la1, la5, la15 = load_avg
            load_value = f"{la1:.2f} / {la5:.2f} / {la15:.2f}"

        disk_value = "N/A"
        if disk_percent is not None:
            disk_value = f"{disk_percent:.0f}% ({disk_path})"

        cpu_value = "N/A" if cpu_percent is None else f"{cpu_percent:.0f}%"
        ram_value = "N/A" if ram_percent is None else f"{ram_percent:.0f}%"

        cpu_bar = self._bar_html(cpu_percent)
        ram_bar = self._bar_html(ram_percent)
        disk_bar = self._bar_html(disk_percent)

        banners.append({
            "id": "system-resources",
            "type": "info",
            "priority": 10,
            "title": "System Resources",
            "html": (
                "<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:12px 14px;\">"
                "<div style=\"grid-column:1 / -1;display:grid;grid-template-columns:max-content 1fr;gap:6px 14px;align-items:center;\">"
                f"<div style=\"font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7\">CPU</div>"
                f"<div style=\"display:flex;gap:10px;align-items:center;\"><div style=\"font-weight:700\">{cpu_value}</div>{cpu_bar}</div>"
                f"<div style=\"font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7\">RAM</div>"
                f"<div style=\"display:flex;gap:10px;align-items:center;\"><div style=\"font-weight:700\">{ram_value}</div>{ram_bar}</div>"
                f"<div style=\"font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7\">Disk</div>"
                f"<div style=\"display:flex;gap:10px;align-items:center;\"><div style=\"font-weight:700\">{disk_value}</div>{disk_bar}</div>"
                "</div>"
                f"<div style=\"padding-top:2px;\"><div style=\"font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7;margin-bottom:4px;\">Load (1/5/15)</div><div style=\"font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;opacity:.85\">{load_value}</div></div>"
                f"<div style=\"padding-top:2px;\"><div style=\"font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.7;margin-bottom:4px;\">Net (since boot)</div><div style=\"font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;opacity:.85\">{net_sent} sent / {net_recv} recv</div></div>"
                "</div>"
            ),
            "dismissible": False,
            "source": "backend",
        })

    def _bar_html(self, percent: float | None) -> str:
        if percent is None:
            return ""

        p = max(0.0, min(100.0, float(percent)))
        if p >= 85:
            color = "#ef4444"
        elif p >= 70:
            color = "#f59e0b"
        else:
            color = "#22c55e"

        return (
            "<div style=\"flex:1;min-width:120px;max-width:220px;height:8px;border-radius:999px;"
            "background:rgba(255,255,255,.10);overflow:hidden;\">"
            f"<div style=\"height:100%;width:{p:.0f}%;background:{color};border-radius:999px;\"></div>"
            "</div>"
        )

    def _get_load_average(self) -> tuple[float, float, float] | None:
        try:
            return os.getloadavg()
        except Exception:
            return None

    def _get_disk_usage_percent(self) -> tuple[float | None, str]:
        for path in ["/", os.path.expanduser("~")]:
            try:
                usage = psutil.disk_usage(path)
                return usage.percent, path
            except Exception:
                continue
        return None, "/"

    def _format_bytes(self, value: int) -> str:
        size = float(value)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} EB"
