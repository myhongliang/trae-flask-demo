/* 设备状态页前端逻辑
 * - 拉取设备信息 / 模块卡片 / 日志
 * - 下发配置 / 触发固件升级（演示用）
 */

(function () {
    'use strict';

    const moduleCardsEl = document.getElementById('moduleCards');
    const logsListEl = document.getElementById('logsList');
    const refreshLogsBtn = document.getElementById('refreshLogsBtn');
    const clearLogsBtn = document.getElementById('clearLogsBtn');
    const configForm = document.getElementById('configForm');
    const upgradeForm = document.getElementById('upgradeForm');
    const curVerInput = document.getElementById('curVer');

    // ---------- 设备信息 ----------
    function loadDeviceInfo() {
        fetch('/api/device/info').then(r => r.json()).then(info => {
            moduleCardsEl.innerHTML = '';
            const cards = [
                { title: 'MCU', value: info.mcu, meta: info.hw_revision },
                { title: '通讯方式', value: info.link, meta: info.connected ? '已连接' : '已断开' },
                { title: '固件版本', value: info.firmware, meta: `Buffer ${info.buffer}B` },
                { title: '采样率', value: `${info.sample_rate} Hz`, meta: `电压 ${info.voltage.toFixed(2)}V` },
                { title: '温度', value: `${info.temperature.toFixed(1)} °C`, meta: '内部传感器' },
                { title: '连接状态', value: info.connected ? '在线' : '离线', meta: 'live' },
            ];
            cards.forEach(c => {
                const el = document.createElement('div');
                el.className = 'module-card';
                el.innerHTML = `
                    <div class="mc-title">${c.title}</div>
                    <div class="mc-value">${c.value}</div>
                    <div class="mc-meta">${c.meta}</div>
                `;
                moduleCardsEl.appendChild(el);
            });
            curVerInput.value = info.firmware;
            configForm.sample_rate.value = info.sample_rate;
            configForm.link.value = info.link;
        });
    }
    loadDeviceInfo();

    // ---------- 日志 ----------
    function loadLogs() {
        fetch('/api/device/logs').then(r => r.json()).then(items => {
            logsListEl.innerHTML = '';
            items.slice(-100).reverse().forEach(l => {
                const row = document.createElement('div');
                row.className = 'log-row';
                row.innerHTML = `
                    <span class="log-ts">${l.ts}</span>
                    <span class="log-level-${l.level}">[${l.level}]</span>
                    <span>${l.msg}</span>
                `;
                logsListEl.appendChild(row);
            });
        });
    }
    loadLogs();
    setInterval(loadLogs, 3000);

    refreshLogsBtn.addEventListener('click', loadLogs);
    clearLogsBtn.addEventListener('click', () => {
        fetch('/api/device/logs/clear', { method: 'POST' }).then(loadLogs);
    });

    // ---------- 配置下发 ----------
    configForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const fd = new FormData(configForm);
        const payload = {
            link: fd.get('link'),
            sample_rate: parseInt(fd.get('sample_rate')),
            matrix_enabled: fd.get('matrix_enabled') === 'on',
        };
        fetch('/api/device/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(r => r.json()).then(() => {
            loadDeviceInfo();
            loadLogs();
        });
    });

    // ---------- 固件升级 ----------
    upgradeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const fd = new FormData(upgradeForm);
        const ver = fd.get('version');
        if (!ver) { alert('请填写目标版本号'); return; }
        if (!confirm(`确认将固件升级到 ${ver}？此操作不可逆。`)) return;
        upgradeForm.querySelector('button[type=submit]').disabled = true;
        fetch('/api/device/upgrade', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ version: ver })
        }).then(r => r.json()).then(res => {
            upgradeForm.querySelector('button[type=submit]').disabled = false;
            if (res.ok) {
                loadDeviceInfo();
                loadLogs();
            } else {
                alert(res.error || '升级失败');
            }
        }).catch(() => {
            upgradeForm.querySelector('button[type=submit]').disabled = false;
        });
    });

})();
