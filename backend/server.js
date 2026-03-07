/**
 * Smart Agriculture AI — Node.js Express Backend
 * ================================================
 * Production-grade middleware between React frontend
 * and the Python FastAPI AI service.
 *
 * Features:
 *  - Timeout handling for all AI API calls
 *  - Structured error forwarding with clear messages
 *  - Connection error detection (AI API unreachable)
 *  - Request logging with timestamps
 *  - CORS and JSON body parsing
 *
 * Version: 3.0.0
 */

const express = require('express');
const cors = require('cors');
const axios = require('axios');
const multer = require('multer');
const FormData = require('form-data');

const app = express();
const PORT = 5000;

// ── Python AI API base URL ─────────────────────────────────
const AI_API = 'http://localhost:8000';

// ── Timeout for all AI API calls (30 seconds) ─────────────
const AI_TIMEOUT_MS = 30000;

// ── Middleware ─────────────────────────────────────────────
app.use(cors());
app.use(express.json());

// Memory storage so we never write to disk in the middleware
const upload = multer({ storage: multer.memoryStorage() });


// ══════════════════════════════════════════════════════════
// LOGGING HELPER
// ══════════════════════════════════════════════════════════

function log(level, message) {
    const ts = new Date().toISOString();
    console.log(`[${level}] ${ts} — ${message}`);
}


// ══════════════════════════════════════════════════════════
// ERROR HANDLING HELPER
// Returns a clean structured error from any axios failure
// ══════════════════════════════════════════════════════════

function handleAIError(err, res, context) {
    // 1) Python API returned an HTTP error with a body
    if (err.response) {
        const status = err.response.status;
        const detail = err.response.data?.detail;

        // detail can be an object { status, message } or a plain string
        const message = typeof detail === 'object'
            ? (detail.message || JSON.stringify(detail))
            : (detail || `AI API error (HTTP ${status})`);

        log('ERROR', `${context} — ${status}: ${message}`);
        return res.status(status).json({ status: 'error', error: message });
    }

    // 2) Network / connection error (API not reachable)
    if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET' || err.code === 'ENOTFOUND') {
        log('ERROR', `${context} — AI API not reachable (${err.code})`);
        return res.status(503).json({
            status: 'error',
            error: 'AI API not reachable. Make sure the Python server is running on port 8000.'
        });
    }

    // 3) Timeout
    if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        log('ERROR', `${context} — AI API timed out`);
        return res.status(504).json({
            status: 'error',
            error: 'AI API request timed out. The model may still be loading.'
        });
    }

    // 4) Unknown error
    log('ERROR', `${context} — Unexpected: ${err.message}`);
    return res.status(500).json({ status: 'error', error: 'Unexpected backend error.' });
}


// ══════════════════════════════════════════════════════════
// PART 9 — ENDPOINTS
// ══════════════════════════════════════════════════════════

// ── 1. Disease Detection ───────────────────────────────────
app.post('/api/disease', upload.single('file'), async (req, res) => {
    log('INFO', 'POST /api/disease');
    try {
        if (!req.file) {
            return res.status(400).json({ status: 'error', error: 'No image file uploaded' });
        }

        const form = new FormData();
        form.append('file', req.file.buffer, {
            filename: req.file.originalname,
            contentType: req.file.mimetype,
        });

        const response = await axios.post(`${AI_API}/predict-disease`, form, {
            headers: form.getHeaders(),
            timeout: AI_TIMEOUT_MS,
        });

        log('INFO', `Disease result: ${JSON.stringify(response.data)}`);
        res.json(response.data);

    } catch (err) {
        handleAIError(err, res, '/api/disease');
    }
});


// ── 2. Crop Recommendation ─────────────────────────────────
app.post('/api/crop', async (req, res) => {
    log('INFO', `POST /api/crop — ${JSON.stringify(req.body)}`);
    try {
        const response = await axios.post(`${AI_API}/predict-crop`, req.body, {
            headers: { 'Content-Type': 'application/json' },
            timeout: AI_TIMEOUT_MS,
        });

        log('INFO', `Crop result: ${JSON.stringify(response.data)}`);
        res.json(response.data);

    } catch (err) {
        handleAIError(err, res, '/api/crop');
    }
});


// ── 3. Yield Prediction ────────────────────────────────────
app.post('/api/yield', async (req, res) => {
    log('INFO', `POST /api/yield — ${JSON.stringify(req.body)}`);
    try {
        const response = await axios.post(`${AI_API}/predict-yield`, req.body, {
            headers: { 'Content-Type': 'application/json' },
            timeout: AI_TIMEOUT_MS,
        });

        log('INFO', `Yield result: ${JSON.stringify(response.data)}`);
        res.json(response.data);

    } catch (err) {
        handleAIError(err, res, '/api/yield');
    }
});


// ── 4. Yield Trends ────────────────────────────────────
app.post('/api/yield-trends', async (req, res) => {
    log('INFO', `POST /api/yield-trends — ${JSON.stringify(req.body)}`);
    try {
        const response = await axios.post(`${AI_API}/yield-trends`, req.body, {
            headers: { 'Content-Type': 'application/json' },
            timeout: AI_TIMEOUT_MS,
        });

        res.json(response.data);

    } catch (err) {
        handleAIError(err, res, '/api/yield-trends');
    }
});


// ── 5. Smart System Report ─────────────────────────────────
app.post('/api/report', upload.single('file'), async (req, res) => {
    log('INFO', 'POST /api/report');
    try {
        const form = new FormData();

        if (req.file) {
            form.append('file', req.file.buffer, {
                filename: req.file.originalname,
                contentType: req.file.mimetype,
            });
        }

        // Forward all text fields
        for (const [key, value] of Object.entries(req.body)) {
            form.append(key, String(value));
        }

        const response = await axios.post(`${AI_API}/smart-report`, form, {
            headers: form.getHeaders(),
            timeout: AI_TIMEOUT_MS,
        });

        log('INFO', 'Smart report generated successfully');
        res.json(response.data);

    } catch (err) {
        handleAIError(err, res, '/api/report');
    }
});


// ── 5. Health Proxy ────────────────────────────────────────
app.get('/api/health', async (req, res) => {
    try {
        const response = await axios.get(`${AI_API}/health`, { timeout: 5000 });
        res.json({ node: 'running', ...response.data });
    } catch (err) {
        res.status(503).json({
            node: 'running',
            python: 'unreachable',
            error: 'AI API not responding'
        });
    }
});


// ── Global error safety net ────────────────────────────────
app.use((err, req, res, next) => {
    log('ERROR', `Unhandled middleware error: ${err.message}`);
    res.status(500).json({ status: 'error', error: 'Internal server error' });
});


// ══════════════════════════════════════════════════════════
// START
// ══════════════════════════════════════════════════════════

app.listen(PORT, () => {
    log('INFO', `================================`);
    log('INFO', `  Smart Agriculture Node Backend`);
    log('INFO', `  Port    : ${PORT}`);
    log('INFO', `  AI API  : ${AI_API}`);
    log('INFO', `  Timeout : ${AI_TIMEOUT_MS / 1000}s`);
    log('INFO', `================================`);
});
