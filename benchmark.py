import os
import sys
import json
import subprocess
import time
import csv
import shutil
from pathlib import Path
from collections import defaultdict
import argparse
import psutil
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

VERSIONS_DIR = 'versions'
ANALYSIS_DIR = 'Analysis'
CONFIG_FILE = os.path.join(VERSIONS_DIR, 'config.json')

# Create a timestamped subfolder for this run
run_id = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
OUTPUT_DIR = os.path.join(ANALYSIS_DIR, f'benchmark_{run_id}')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Update index file in Analysis/
def update_index(run_id, out_prefix):
    index_file = os.path.join(ANALYSIS_DIR, 'index.md')
    with open(index_file, 'a', encoding='utf-8') as f:
        f.write(f'- [{run_id}]({out_prefix}_report.md)\n')

def load_versions():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def run_version(version, n, mode, repeat=1):
    results = []
    for i in range(repeat):
        cmd = [sys.executable, os.path.join(VERSIONS_DIR, version['filename'])] if version['filename'].startswith('main_') else [sys.executable, version['filename']]
        proc = None
        try:
            start = time.time()
            proc = psutil.Popen(cmd + [str(n), mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            peak_mem = 0
            # Poll memory usage while process is running
            while proc.is_running() and proc.poll() is None:
                try:
                    mem = proc.memory_info().rss
                    if mem > peak_mem:
                        peak_mem = mem
                except Exception:
                    pass
                time.sleep(0.05)
            try:
                out, err = proc.communicate(timeout=10)
            except Exception:
                out, err = '', 'Process did not produce output.'
            end = time.time()
            # Save output
            out_file = os.path.join(OUTPUT_DIR, f"{version['name'].replace(' ', '_')}_n{n}_run{i+1}.txt")
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(out)
                if err:
                    f.write('\n--- STDERR ---\n')
                    f.write(err)
            # Try to parse timing and solution count from output
            exec_time = None
            sol_count = None
            for line in out.splitlines():
                if 'Execution Time:' in line:
                    exec_time = line.split('Execution Time:')[-1].strip().split()[0]
                if 'Total permutations checked:' in line:
                    checked = line.split(':')[-1].strip().replace(',', '')
                if 'solutions' in line and 'total' in line.lower():
                    try:
                        sol_count = int(line.split(':')[-1].strip())
                    except Exception:
                        pass
            results.append({
                'stdout': out,
                'stderr': err,
                'exec_time': exec_time,
                'solutions': sol_count,
                'mem': peak_mem,
                'out_file': out_file,
                'success': proc.returncode == 0,
                'n': n,
                'version': version['name']
            })
        except Exception as e:
            if proc:
                try:
                    proc.kill()
                except Exception:
                    pass
            results.append({'stdout': '', 'stderr': str(e), 'exec_time': None, 'solutions': None, 'mem': None, 'out_file': None, 'success': False, 'n': n, 'version': version['name']})
            print(f"[FAIL] {version['name']} n={n} run={i+1}: {e}")
            break  # Fail fast for this version
    return results

def compare_solutions(outputs):
    all_solutions = set()
    for sols in outputs.values():
        all_solutions.update(sols)
    missing = defaultdict(list)
    for v, sols in outputs.items():
        missing[v] = list(all_solutions - set(sols))
    return missing

def parse_solutions_from_output(output):
    sols = set()
    for line in output.splitlines():
        if line.strip().startswith('grid') or line.strip().startswith('['):
            sols.add(line.strip())
    return sols

def export_csv(results, filename):
    if not results:
        return
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def export_json(results, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

def plot_performance(perf_data, out_prefix):
    # Aggregate by (version, n): average metrics over repeats
    if not perf_data:
        return
    versions = sorted(set(d['version'] for d in perf_data))
    ns = sorted(set(d['n'] for d in perf_data))
    metrics = ['exec_time', 'mem']
    for metric in metrics:
        plt.figure(figsize=(8,6))
        for v in versions:
            y = []
            for n in ns:
                vals = [float(d[metric]) for d in perf_data if d['version']==v and d['n']==n and d[metric] is not None]
                y.append(np.mean(vals) if vals else float('nan'))
            plt.plot(ns, y, marker='o', label=v)
        plt.xlabel('n')
        plt.ylabel(metric.replace('_',' ').title())
        plt.title(f'{metric.replace("_", " ").title()} vs n')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{out_prefix}_{metric}.png')
        plt.close()

def write_markdown_report(perf_data, missing, out_prefix):
    md = f"# Benchmark Report\n\n"
    md += "| Version | n | Exec Time (s) | Solutions | Mem (bytes) | Success |\n"
    md += "|---------|---|---------------|-----------|-------------|---------|\n"
    for d in perf_data:
        md += f"| {d['version']} | {d['n']} | {d['exec_time']} | {d['solutions']} | {d['mem']} | {d['success']} |\n"
    md += "\n## Output Diffing (Missing Solutions)\n"
    for v, miss in missing.items():
        if miss:
            md += f"- {v} missing {len(miss)} solutions\n"
    md += "\n## Performance Graphs\n"
    md += f"![Exec Time]({os.path.basename(out_prefix)}_exec_time.png)\n"
    md += f"![Memory]({os.path.basename(out_prefix)}_mem.png)\n"
    with open(f'{out_prefix}_report.md', 'w', encoding='utf-8') as f:
        f.write(md)

def main():
    parser = argparse.ArgumentParser(description='Benchmark all grid program versions.')
    parser.add_argument('--n_min', type=int, default=2, help='Minimum n')
    parser.add_argument('--n_max', type=int, default=3, help='Maximum n')
    parser.add_argument('--repeat', type=int, default=1, help='Repeats per version')
    parser.add_argument('--mode', choices=['all', 'single'], default='all', help='Solution mode')
    parser.add_argument('--out_prefix', default=os.path.join(OUTPUT_DIR, 'benchmark'), help='Output file prefix')
    args = parser.parse_args()

    versions = load_versions()
    perf_data = []
    solution_outputs = defaultdict(list)
    for n in range(args.n_min, args.n_max+1):
        for version in versions:
            print(f"\n[RUN] {version['name']} n={n}")
            results = run_version(version, n, args.mode, args.repeat)
            for i, res in enumerate(results):
                perf_data.append({
                    'version': version['name'],
                    'n': n,
                    'exec_time': res['exec_time'],
                    'solutions': res['solutions'],
                    'mem': res['mem'],
                    'success': res['success'],
                    'out_file': res['out_file']
                })
                if res['stdout']:
                    sols = parse_solutions_from_output(res['stdout'])
                    solution_outputs[version['name']].extend(sols)
    # Output diffing
    missing = compare_solutions(solution_outputs)
    # Export
    export_csv(perf_data, args.out_prefix + '.csv')
    export_json(perf_data, args.out_prefix + '.json')
    plot_performance(perf_data, args.out_prefix)
    write_markdown_report(perf_data, missing, args.out_prefix)
    update_index(run_id, args.out_prefix)
    print(f"\nBenchmarking complete. Results in {args.out_prefix}_report.md")

if __name__ == '__main__':
    main() 