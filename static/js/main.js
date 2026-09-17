/* 心电监测系统 - 主监测页前端逻辑
 * - SSE 订阅实时数据
 * - Canvas 滚动绘制 4 路 ECG + 2 路压电
 * - 4×4 矩阵热力图（电阻 / 压力两种模式）
 * - 心率 / 推送速率显示
 * - 记录开始/停止 / CSV 回放 / PNG 导出 / 通道互换
 */

(function () {
    'use strict';

    // ---------- DOM 引用 ----------
    const ecgCanvas = document.getElementById('ecgCanvas');
    const ecgCtx = ecgCanvas.getContext('2d');
    const piezoCanvas = document.getElementById('piezoCanvas');
    const piezoCtx = piezoCanvas.getContext('2d');
    const matrixWrap = document.getElementById('matrixWrap');
    const matrixModeSel = document.getElementById('matrixMode');
    const swapBtn = document.getElementById('swapBtn');
    const hrValueEl = document.getElementById('hrValue');
    const fpsValueEl = document.getElementById('fpsValue');
    const srValueEl = document.getElementById('srValue');
    const recStateEl = document.getElementById('recState');
    const recFileEl = document.getElementById('recFile');
    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');
    const importBtn = document.getElementById('importBtn');
    const csvInput = document.getElementById('csvInput');
    const playbackSelect = document.getElementById('playbackSelect');
    const playBtn = document.getElementById('playBtn');
    const stopPlayBtn = document.getElementById('stopPlayBtn');
    const exportPngBtn = document.getElementById('exportPngBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const connPill = document.getElementById('connPill');

    // ---------- 状态 ----------
    const CH = 4;
    const BUF_LEN = 1500;            // ECG 滚动缓冲长度（约 3s @500Hz）
    const PIEZO_BUF_LEN = 800;
    const ecgBufs = Array.from({ length: CH }, () => new Float32Array(BUF_LEN));
    const piezoBufs = [new Float32Array(PIEZO_BUF_LEN), new Float32Array(PIEZO_BUF_LEN)];
    let matrixMode = 'resistance';
    let isRecording = false;
    let lastHr = 0;
    let evtCount = 0;
    let lastFpsTs = performance.now();

    // ---------- 矩阵 cells ----------
    const cells = [];
    for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
            const ch = r * 4 + c;
            const cell = document.createElement('div');
            cell.className = 'matrix-cell';
            cell.dataset.ch = ch;
            cell.innerHTML = `<div class="ch-label">CH${ch + 1}</div><div class="val">--</div>`;
            matrixWrap.appendChild(cell);
            cells.push(cell);
        }
    }

    // ---------- 通道映射互换 UI ----------
    let swapMode = false;
    let firstSwapTarget = null;

    swapBtn.addEventListener('click', () => {
        swapMode = !swapMode;
        firstSwapTarget = null;
        swapBtn.textContent = swapMode ? '✓ 点击两个格子完成互换' : '互换位置';
        cells.forEach(c => c.classList.toggle('swap-target', false));
    });

    matrixWrap.addEventListener('click', (e) => {
        if (!swapMode) return;
        const cell = e.target.closest('.matrix-cell');
        if (!cell) return;
        if (!firstSwapTarget) {
            firstSwapTarget = cell;
            cell.classList.add('swap-target');
        } else if (firstSwapTarget !== cell) {
            // 取当前映射
            fetch('/api/matrix/map').then(r => r.json()).then(data => {
                const map = data.mapping;
                const a = map.find(m => m.ch === parseInt(firstSwapTarget.dataset.ch));
                const b = map.find(m => m.ch === parseInt(cell.dataset.ch));
                // 互换两个通道的显示位置
                const newMap = map.map(m => {
                    if (m.ch === a.ch) return { ch: a.ch, row: b.row, col: b.col };
                    if (m.ch === b.ch) return { ch: b.ch, row: a.row, col: a.col };
                    return m;
                });
                fetch('/api/matrix/map', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newMap)
                }).then(() => {
                    firstSwapTarget.classList.remove('swap-target');
                    firstSwapTarget = null;
                    swapMode = false;
                    swapBtn.textContent = '互换位置';
                });
            });
        }
    });

    // ---------- 矩阵模式切换 ----------
    matrixModeSel.addEventListener('change', () => {
        matrixMode = matrixModeSel.value;
        fetch('/api/matrix/mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: matrixMode })
        });
    });

    // ---------- Canvas 适配 HiDPI ----------
    function fitCanvas(canvas) {
        const dpr = window.devicePixelRatio || 1;
        const w = canvas.clientWidth;
        const h = canvas.clientHeight || parseInt(canvas.getAttribute('height'));
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.getContext('2d').scale(dpr, dpr);
    }
    fitCanvas(ecgCanvas);
    fitCanvas(piezoCanvas);
    window.addEventListener('resize', () => { fitCanvas(ecgCanvas); fitCanvas(piezoCanvas); });

    // ---------- ECG 绘制 ----------
    const ECG_COLORS = ['#6d4aff', '#00c2a8', '#f79009', '#1f8fff'];

    function pushEcg(samples) {
        for (let i = 0; i < samples.length; i++) {
            const s = samples[i].ecg;
            for (let ch = 0; ch < CH; ch++) {
                const buf = ecgBufs[ch];
                buf.copyWithin(0, 1, BUF_LEN);
                buf[BUF_LEN - 1] = s[ch];
            }
        }
    }
    function pushPiezo(samples) {
        for (let i = 0; i < samples.length; i++) {
            const p = samples[i].piezo;
            for (let ch = 0; ch < 2; ch++) {
                const buf = piezoBufs[ch];
                buf.copyWithin(0, 1, PIEZO_BUF_LEN);
                buf[PIEZO_BUF_LEN - 1] = p[ch];
            }
        }
    }

    function drawEcg() {
        const w = ecgCanvas.clientWidth;
        const h = ecgCanvas.clientHeight || 320;
        ecgCtx.clearRect(0, 0, w, h);
        // 背景
        ecgCtx.fillStyle = '#f6f4fb';
        ecgCtx.fillRect(0, 0, w, h);
        // 网格
        ecgCtx.strokeStyle = '#e7e2f0';
        ecgCtx.lineWidth = 1;
        for (let x = 0; x < w; x += 50) {
            ecgCtx.beginPath(); ecgCtx.moveTo(x, 0); ecgCtx.lineTo(x, h); ecgCtx.stroke();
        }
        const trackH = h / CH;
        for (let i = 1; i < CH; i++) {
            ecgCtx.beginPath();
            ecgCtx.moveTo(0, i * trackH);
            ecgCtx.lineTo(w, i * trackH);
            ecgCtx.stroke();
        }
        // 4 路波形
        for (let ch = 0; ch < CH; ch++) {
            const buf = ecgBufs[ch];
            const yMid = trackH * (ch + 0.5);
            const amp = trackH * 0.4;
            ecgCtx.strokeStyle = ECG_COLORS[ch];
            ecgCtx.lineWidth = 1.4;
            ecgCtx.beginPath();
            for (let i = 0; i < BUF_LEN; i++) {
                const x = (i / (BUF_LEN - 1)) * w;
                const y = yMid - buf[i] * amp;
                if (i === 0) ecgCtx.moveTo(x, y);
                else ecgCtx.lineTo(x, y);
            }
            ecgCtx.stroke();
            // 通道标签
            ecgCtx.fillStyle = ECG_COLORS[ch];
            ecgCtx.font = '11px sans-serif';
            ecgCtx.fillText(`CH${ch + 1}`, 6, trackH * ch + 14);
        }
    }

    function drawPiezo() {
        const w = piezoCanvas.clientWidth;
        const h = piezoCanvas.clientHeight || 180;
        piezoCtx.clearRect(0, 0, w, h);
        piezoCtx.fillStyle = '#f6f4fb';
        piezoCtx.fillRect(0, 0, w, h);
        piezoCtx.strokeStyle = '#e7e2f0';
        piezoCtx.lineWidth = 1;
        piezoCtx.beginPath();
        piezoCtx.moveTo(0, h / 2); piezoCtx.lineTo(w, h / 2); piezoCtx.stroke();

        const COLORS = ['#6d4aff', '#00c2a8'];
        for (let ch = 0; ch < 2; ch++) {
            const buf = piezoBufs[ch];
            const yMid = h * (ch === 0 ? 0.3 : 0.7);
            const amp = h * 0.25;
            piezoCtx.strokeStyle = COLORS[ch];
            piezoCtx.lineWidth = 1.4;
            piezoCtx.beginPath();
            for (let i = 0; i < PIEZO_BUF_LEN; i++) {
                const x = (i / (PIEZO_BUF_LEN - 1)) * w;
                const y = yMid - buf[i] * amp;
                if (i === 0) piezoCtx.moveTo(x, y);
                else piezoCtx.lineTo(x, y);
            }
            piezoCtx.stroke();
            piezoCtx.fillStyle = COLORS[ch];
            piezoCtx.font = '11px sans-serif';
            piezoCtx.fillText(`Piezo ${ch + 1}`, 6, yMid - amp - 2);
        }
    }

    function updateMatrix(matrixArr, mode) {
        // matrixArr 长度 16，按当前通道映射的显示位置排列
        // 实际显示位置由后端按通道映射后给出（这里 samples 中 matrix 字段就是按映射后的 16 个值）
        const minV = mode === 'resistance' ? 25 : 0;
        const maxV = mode === 'resistance' ? 32 : 5;
        for (let i = 0; i < 16; i++) {
            const v = matrixArr[i];
            const t = Math.max(0, Math.min(1, (v - minV) / (maxV - minV)));
            const color = interpolateColor(t);
            const cell = cells[i];
            cell.style.background = color;
            const label = mode === 'resistance' ? `${v.toFixed(1)} kΩ` : `${v.toFixed(2)} kPa`;
            cell.querySelector('.val').textContent = label;
        }
    }
    function interpolateColor(t) {
        // 从 #2c2750 (44,39,80) 到 #6d4aff (109,74,255)
        const r = Math.round(44 + (109 - 44) * t);
        const g = Math.round(39 + (74 - 39) * t);
        const b = Math.round(80 + (255 - 80) * t);
        return `rgb(${r},${g},${b})`;
    }

    // ---------- 渲染循环 ----------
    function render() {
        drawEcg();
        drawPiezo();
        // FPS
        evtCount++;
        const now = performance.now();
        if (now - lastFpsTs > 1000) {
            fpsValueEl.textContent = evtCount;
            evtCount = 0;
            lastFpsTs = now;
        }
        requestAnimationFrame(render);
    }
    requestAnimationFrame(render);

    // ---------- SSE 实时数据 ----------
    let evtSource = null;
    function startStream() {
        evtSource = new EventSource('/stream');
        evtSource.addEventListener('sample', (e) => {
            const data = JSON.parse(e.data);
            const samples = data.samples;
            if (!samples || !samples.length) return;
            pushEcg(samples);
            pushPiezo(samples);
            const last = samples[samples.length - 1];
            // 矩阵：取最后一个采样点的 16 个值
            updateMatrix(last.matrix, data.matrix_mode || matrixMode);
            // 心率
            if (last.hr != null && last.hr > 0) {
                lastHr = last.hr;
                hrValueEl.textContent = lastHr;
            }
            // 记录状态
            if (data.is_recording !== isRecording) {
                isRecording = data.is_recording;
                recStateEl.textContent = isRecording ? '记录中' : '就绪';
                recStateEl.style.color = isRecording ? '#f04438' : '';
                recFileEl.textContent = data.record_file || '--';
            }
        });
        evtSource.onopen = () => {
            connPill.classList.add('connected');
            connPill.querySelector('.conn-text').textContent = '已连接';
        };
        evtSource.onerror = () => {
            connPill.classList.remove('connected');
            connPill.querySelector('.conn-text').textContent = '已断开';
        };
    }
    startStream();

    // ---------- 记录控制 ----------
    recordBtn.addEventListener('click', () => {
        fetch('/api/record/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        }).then(r => r.json()).then(res => {
            if (res.ok) {
                recStateEl.textContent = '记录中';
                recStateEl.style.color = '#f04438';
                recFileEl.textContent = res.filename;
                isRecording = true;
                refreshRecordList();
            } else {
                alert(res.error || '无法开始记录');
            }
        });
    });
    stopBtn.addEventListener('click', () => {
        fetch('/api/record/stop', { method: 'POST' })
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    recStateEl.textContent = '就绪';
                    recStateEl.style.color = '';
                    isRecording = false;
                    refreshRecordList();
                }
            });
    });

    // ---------- 记录列表 ----------
    function refreshRecordList() {
        fetch('/api/records').then(r => r.json()).then(items => {
            playbackSelect.innerHTML = '<option value="">— 选择记录文件 —</option>';
            items.forEach(it => {
                const opt = document.createElement('option');
                opt.value = it.filename;
                opt.textContent = `${it.filename} · ${it.rows} 行 · ${it.mtime}`;
                playbackSelect.appendChild(opt);
            });
        });
    }
    refreshRecordList();
    setInterval(refreshRecordList, 5000);

    // ---------- CSV 导入回放 ----------
    importBtn.addEventListener('click', () => csvInput.click());
    csvInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const text = ev.target.result;
            playbackFromCsvText(text);
        };
        reader.readAsText(file);
    });

    // ---------- 后端 CSV 回放 ----------
    playBtn.addEventListener('click', () => {
        const fn = playbackSelect.value;
        if (!fn) { alert('请先选择记录文件'); return; }
        stopStreamForPlayback();
        fetch('/api/playback/' + encodeURIComponent(fn))
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    playbackFromRows(res.rows);
                } else {
                    alert(res.error || '回放失败');
                    startStream();
                }
            });
    });

    stopPlayBtn.addEventListener('click', () => {
        if (evtSource) evtSource.close();
        startStream();
    });

    function stopStreamForPlayback() {
        if (evtSource) evtSource.close();
    }

    // 把回放数据按节奏塞进缓冲
    function playbackFromRows(rows) {
        let i = 0;
        const step = 10;
        const tick = () => {
            if (i >= rows.length) return;
            const batch = rows.slice(i, i + step);
            i += step;
            const samples = batch.map(r => ({
                ecg: [parseFloat(r.ecg1), parseFloat(r.ecg2), parseFloat(r.ecg3), parseFloat(r.ecg4)],
                matrix: Array.from({ length: 16 }, (_, k) => parseFloat(r['m' + k])),
                piezo: [parseFloat(r.piezo1), parseFloat(r.piezo2)],
                hr: parseInt(r.hr) || 0,
            }));
            pushEcg(samples);
            pushPiezo(samples);
            updateMatrix(samples[samples.length - 1].matrix, matrixMode);
            if (samples[samples.length - 1].hr > 0) {
                hrValueEl.textContent = samples[samples.length - 1].hr;
            }
            setTimeout(tick, 20);
        };
        tick();
    }

    function playbackFromCsvText(text) {
        const lines = text.trim().split(/\r?\n/);
        if (lines.length < 2) return;
        const header = lines[0].split(',');
        const rows = lines.slice(1).map(line => {
            const cols = line.split(',');
            const obj = {};
            header.forEach((h, i) => obj[h] = cols[i]);
            return obj;
        });
        stopStreamForPlayback();
        playbackFromRows(rows);
    }

    // ---------- 导出 ----------
    exportPngBtn.addEventListener('click', () => {
        // 把 ECG + Piezo + 矩阵 拼到一张 PNG
        const w = Math.max(ecgCanvas.clientWidth, 900);
        const h = ecgCanvas.clientHeight + piezoCanvas.clientHeight + 40;
        const tmp = document.createElement('canvas');
        tmp.width = w; tmp.height = h;
        const ctx = tmp.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(ecgCanvas, 0, 0, w, ecgCanvas.clientHeight);
        ctx.drawImage(piezoCanvas, 0, ecgCanvas.clientHeight, piezoCanvas.clientWidth, piezoCanvas.clientHeight);
        const link = document.createElement('a');
        link.download = `ecg_export_${Date.now()}.png`;
        link.href = tmp.toDataURL('image/png');
        link.click();
    });

    exportCsvBtn.addEventListener('click', () => {
        // 如果正在记录 -> 提示停止后下载；否则下载列表里最新一个
        if (isRecording) {
            alert('请先停止记录，再导出 CSV。');
            return;
        }
        const fn = playbackSelect.value || playbackSelect.options[1]?.value;
        if (!fn) { alert('暂无可导出的 CSV 记录，请先开始记录。'); return; }
        window.location.href = '/data/' + encodeURIComponent(fn);
    });

})();
