---
name: decode-profile
description: Profile vLLM decode-time GPU kernel hot spots on gfx1030/gfx1100 using venv-7.14.0 rocprofv3 --run mode. Use when investigating "where is decode time going?", analyzing per-kernel dispatch timing under FPP/PYNCCL/RDNA-FA stacks, or building evidence for kernel optimization priorities. Triggers: 'profile decode', 'kernel hot spots', 'rocprofv3', 'gpu kernel timing', 'what's slow on this stack', 'decode latency breakdown'.
---

# Decode-Time GPU Profile on gfx1030 / RDNA2

Profile live vLLM serving to find which GPU kernels dominate decode time. Output is a per-kernel dispatch breakdown (count, total ms, avg µs) plus per-second histogram identifying the steady-state decode window.

## Why this skill exists

The standard tools have known failure modes on gfx1030:

- **System `/opt/rocm/bin/rocprofv3`** is ROCm 7.2 — wrong SDK, dispatch attach fails.
- **System `/opt/rocm/core-7.14/bin/rocprofv3`** has a hardcoded path conflict: when called, it loads `librocprofiler-sdk-rocattach.so` from `/opt/rocm-7.2.0/core-7.14/lib/` (both `/opt/rocm/core-7.14` and `/opt/rocm-7.2.0/core-7.14` are symlinks to the same dir, but the binary picks the 7.2 path). Use `--rocm-root /opt/rocm/core-7.14` to override, but the venv-7.14.0 Python `rocpd2csv` requires Python 3.12 (venv's python) and only works against the venv sdk.
- **`torch.profiler` in workers** is bypassed by cudagraph replay per `rdna-kernel-debug` skill; only captures Python attribution, not the captured kernels.
- **`vllm bench throughput` + `VLLM_DBG_STEP_TIMING`** only measures Python per-step overhead (5 ms total — not the bottleneck).
- **`LD_PRELOAD=librocprofiler-sdk.so`** crashes Python at startup (`Illegal instruction` on EPYC 7452, Zen 2 — pre-AVX-512; the ld cannot handle some path). Symptom: `bash: line 1: SIGABRT`.
- **`rocprof-sys-run --rocm=kernel`** also crashes with SIGILL on this CPU. Use rocprofv3 only.
- **rocprofv3 `--attach`** requires `rocp-bg-attach` thread in target (not present in non-register builds of torch). Bypassed.

**Working path**: wrap vLLM from birth with venv's bundled rocprofv3 (`/home/chenco_adm/Apps/vllm/venv-7.14.0/bin/rocprofv3`). It uses the AMD pip wheel's embedded ROCm 7.14 SDK which is ABI-compatible with torch 2.12.0+rocm7.14. No LLVM clash.

## Quick start

```bash
ssh -i ~/.ssh/id_ed25519_ansible chenco_adm@192.168.1.176
# 1. Edit /tmp/profile_decode/launch_venv_rocprofv3.sh — set MODEL, PORT, env.
#    Use the canonical launcher from opengfx1030_vllm-rdna/scripts/serve_gfx1030_full.sh.
# 2. Launch under rocprofv3 (wraps from birth — kernel capture covers entire run):
cd /tmp && bash /tmp/profile_decode/launch_venv_rocprofv3.sh > /tmp/serve.log 2>&1 &
# 3. Wait for server up (~3-4 min for cold init + cudagraph capture).
for i in $(seq 1 60); do curl -sf http://127.0.0.1:$PORT/v1/models >/dev/null && break; sleep 5; done
# 4. Send warmup request (puts workers in steady state).
python /tmp/profile_decode/warmup.py
# 5. Mark c1_start, run c=1 measurement (1k/512):
date +%s.%N > c1_start.txt && python c1_1k_512.py && date +%s.%N > c1_end.txt
# 6. Mark c8_start, run c=8 measurement:
date +%s.%N > c8_start.txt && python c8_1k_512.py && date +%s.%N > c8_end.txt
# 7. Kill the launcher with SIGTERM (rocprofv3 catches it, waits for workers, finalizes CSV).
kill -TERM <LAUNCHER_PID>
# 8. Wait for CSV to land in /tmp/profile_decode/run6/prof_kernel_trace.csv (~5-10s).
ls -la /tmp/profile_decode/run6/*.csv
# 9. Analyze with the included script:
python /tmp/profile_decode/scripts/analyze_phase3.py
```

## Output format

`prof_kernel_trace.csv` (one row per kernel dispatch, ~1.3M rows for a 3-min run, ~555 MB):
- `Kind`, `Agent_Id`, `Queue_Id`, `Stream_Id`, `Thread_Id`, `Dispatch_Id`, `Kernel_Id`
- `Kernel_Name`, `Start_Timestamp`, `End_Timestamp` (GPU nanoseconds since GPU init)
- `Workgroup_Size_X/Y/Z`, `Grid_Size_X/Y/Z`
- `LDS_Block_Size`, `VGPR_Count`, `SGPR_Count`

`prof_rccl_api_trace.csv`: RCCL collective timings (all-reduce, all-gather).
`prof_agent_info.csv`: device + queue metadata.

**Phase mapping** (GPU-time seconds since first kernel):
- `t=0..50s` — cold init (model load + cudagraph capture + warmup dispatch)
- `t=55..63s` — warmup request (2k prompt + 16 generated tokens)
- `t=100..140s` — c=1 measurement decode window (1k/512, ~80 actual decode tokens)
- `t=145..185s` — c=8 prefill (8 × 1k prompt)
- `t=185..200s` — c=8 decode (80 tokens × 8 = 640 tokens aggregated)

**Key kernels** (under FA-RDNA2 + AWQ RDNA2 + HIP GDN + PYNCCL FPP):
- `vllm::gptq_rdna2_prefill::gemm_dynamic_kernel<…>` — the W4A16 GEMM, runs at multiple template instantiations (small M=1/M=2 decode, large M prefill)
- `vllm::cross_device_reduce_1stage<__half, 2>(…)` — vLLM's cross-device reduce (used for custom all-reduce and PYNCCL)
- `ncclDevKernel_Generic_4(…)` — NCCL/RCCL ring all-reduce (PYNCCL path)
- `vllm::gptq_rdna2::gemm_q4_kernel_rdna2<__half, N>(…)` — manual W4A16 decode GEMM at M=N (N=1, 2, 4, 8)
- `fa_decode_paged_splitk_kernel_256<__half, false, false>(…)` — FA-RDNA2 decode attention
- `fa_prefill_paged_varlen_kernel_256<__half, false>(…)` — FA-RDNA2 prefill attention
- `gdn_prefill_{delta_h, o, kkt, solve_wy, prep}_rdna2_kernel` — HIP GDN prefill chain (5 kernels)
- `gdn_decode_packed_rdna2_kernel` — HIP GDN decode (one fused kernel)
- `rocblas_gemvt_kernel<false, 256, …>` — GEMV (M=1) for LM head
- `at::native::reduce_kernel<…>` — torch reductions (look for any heavy ones)
- `Cijk_Alik_Bljk_HHS_BH_MT…` — rocBLAS/hcc compiled GEMMs (one per shape from TunableOp autotune)

## Interpretation rules

**Report PP and TG separately, always.** Every profile result must state
**PP** (prompt processing / prefill, tok/s), **TG** (token generation /
decode, tok/s) and **TTFT** — never decode alone. Derive aggregate PP as
`total_input_tokens / mean_TTFT`, per-request PP as
`input_len / mean_TTFT`, and TG as the output tok/s. A profile that only
reports TG is incomplete: at higher concurrency these stacks are usually
**prefill-dominated**, and the two phases have entirely different fixes.

Diagnostic pattern: if aggregate PP is **flat or regressing** while
per-request PP collapses as concurrency rises, the bottleneck is
chunked-prefill serialization (chunks from different requests interleave,
so each prefill takes longer while total prefill throughput stays put) —
profile the **prefill** window and look at the chunk scheduler, not the
GEMM.

**Decode GPU utilization** (% of wall time the GPU has kernels queued) is the single most diagnostic number:
- >70% — GPU-bound, optimize the hot kernel directly
- 30-50% — launch/CPU-overhead-bound, reduce per-step Python overhead or capture more in cudagraph
- <30% — serious launch overhead; cudagraph likely broken or many small kernels

**c=1 vs c=8 comparison**: c=1 decode is bandwidth-bound; c=8 should be 4-8× aggregate tok/s. If c=8 throughput is only 1.5-2× c=1, the bottleneck is per-step serialization (Python or GDN dispatch), not bandwidth.

## Common gotchas

- **Output files appear in `/tmp/.rocprofv3/` as `.dat`** during the run; only after rocprofv3 detaches (child exits) does it merge and write `.csv` to your `--output-file` path. **Always kill cleanly with SIGTERM and wait** — KILL drops the CSV.
- **rocprofv3 --attach mode requires torch built with `ROCPROFILER_REGISTER_BUILD_DEFAULT_ATTACHMENT=ON`** — torch 2.12+rocm7.14 wheel is NOT register-built. **Always use --run mode.**
- **GPU timestamps are nanoseconds since GPU init**, NOT Unix epoch. To map to wall-clock phases: use a known anchor (e.g., first kernel after cold init) or just histogram by GPU-second buckets.
- **Cold init + cudagraph capture fires ~1M kernels** before the workload starts. Filter by time window to isolate decode.
- **`vllm::gptq_rdna2_prefill::gemm_dynamic_kernel`** runs at MANY template instantiations — different M values get different compile-time templates. Each instantiation is a separate kernel name.
- **TunableOp autotunes during warmup** — many `Cijk_*` kernels fire ONCE with various sizes during cold init, then never again. They show up at the top of "total time" but they're not decode kernels.
- **`__amd_rocclr_copyBuffer` and `__amd_rocclr_fillBufferAligned`** are HIP allocator activity. They're not on the critical path but balloon counts.

## Bundled scripts

- `scripts/launch_venv_rocprofv3.sh` — wraps serve60 under rocprofv3 from birth
- `scripts/warmup.py` — single 2k/16 warmup request
- `scripts/c1_1k_512.py` — single 1k/512 measurement (returns wall + completion tokens)
- `scripts/c8_1k_512.py` — 8 concurrent 1k/512 requests
- `scripts/analyze_phase3.py` — phase-windowed kernel aggregation (cold/warmup/c1_decode/c8_prefill/c8_decode)
- `scripts/analyze_phase2.py` — full-run kernel histogram by GPU-second (useful for visually finding decode bursts)

## Reference

- `rdna-kernel-debug` skill — the parent skill with the canonical launch command, TORCH_CHECK guard pattern, standalone-probe template, and rocprof location matrix. Use `~/.config/opencode/skills/rdna-kernel-debug/scripts/check_gpu_clean.sh` to confirm clean GPU state before launching.
- `csrc/rocm/q_gemm_rdna2_awq_*.cu` — the AWQ W4A16 kernel sources (decode hot path)
- `csrc/rocm/fa_rdna2.cu` — the FA-RDNA2 attention kernel sources
- `csrc/rocm/causal_conv1d_rdna2.cu` — the GDN conv1d kernel sources
