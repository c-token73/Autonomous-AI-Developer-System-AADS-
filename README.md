# Autonomous AI Developer System (AADS)

## 🚀 Ringkasan

Project ini adalah prototipe **Autonomous AI Developer System** untuk:
- Distribusi modul multi-agen (planner, programmer, reviewer, backend/frontend/test agents)
- Jalur self-evolving (task generator, critic, evolution loop)
- Redesain adaptif resource-aware (architecture engine, governor, stability controller)
- Integrasi UI dengan Streamlit sebagai control center

Tujuan: Menghasilkan kode, melakukan validasi, review, dan commit otomatis dengan monitoring kualitas, stabilitas, dan konsumsi sumber daya.

## 🧩 Struktur Repository

- `core/` : inti orkestrasi dan komponen sistem
  - `orchestrator.py` : flow task end-to-end, dispatch, auto-improvement, gerakan evolusi
  - `memory.py` : penyimpanan history, status tugas, metrik
  - `task_decomposer.py` / `coordinator.py` / `aggregator.py` : orchestrasi terdistribusi
  - `task_generator.py` / `system_critic.py` / `evolution_loop.py` : engine self-evolution
  - `architecture_engine.py` / `resource_governor.py` / `agent_generator.py` / `stability_controller.py` : autos-kelola desain & robustness
- `agents/` : agen hi-level
  - `planner.py`, `programmer.py`, `reviewer.py` : pipeline inti
  - `backend_agent.py`, `frontend_agent.py`, `test_agent.py` : mode terdistribusi specialized micro-workload
- `app.py` : Streamlit dashboard, UI end-to-end, controls, commit/approval workflow
- `README.md` : dokumentasi ini

## 🛠️ Setup dan dependensi

1. Buat virtualenv (direkomendasikan):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Pasang dep

```bash
pip install -r requirements.txt
# Jika requirements belum tersedia, pasang minimal:
pip install streamlit
```

3. Jalankan cek sintaks (opsional):

```bash
python -m py_compile core/*.py app.py
```

## ▶️ Menjalankan dashboard

```bash
streamlit run app.py
```

Akses di browser: `http://localhost:8501`

## 🔧 Alur kerja fitur utama

1. Input task di UI
2. Planner buat rencana terstruktur
3. Programmer draft kode otomatis
4. Reviewer melakukan quality scoring, security check, improvement
5. Validator jalankan lint/syntax
6. Iterasi sampai kualitas threshold terpenuhi
7. Mode distributed (opsional): backend/frontend/test agents parallel
8. Mode autonomous evolution (opsional): generator tugas + critic + refactor loop
9. Commit otomatis ke repo setelah approval

## 🧠 Handling impor & runtime

- `streamlit` dicek dengan `try/except ImportError` untuk memperjelas peringatan
- Agen terdistribusi diimpor secara dinamis lewat `safe_import_agent` agar tidak crash bila modul belum ada
- `pyright: reportMissingImports=false` ditambahkan untuk menghindari false-positive analis statis di lingkungan CI non-streamlit

## 🧪 Validasi dan testing

- `python -m py_compile core/*.py app.py`
- `get_errors` (VS Code Pylance) untuk mengonfirmasi 0 error
- Jalankan ticket workflow di UI secara manual untuk konfirmasi end-to-end

## 📝 Catatan tambahan

- Pastikan versi Python `>=3.10`
- Update `requirements.txt` setelah menambah fitur baru
- Untuk `git commit` otomatis, sistem menggunakan `TaskOrchestrator.stage_for_approval` + `execute_commit`

---

Terima kasih sudah mengembangkan sistem ini; silakan lanjutkan ke pengujian runtime di `streamlit run app.py`.