"""
Raccoglie tutte le metriche di qualità e manutenibilità dai report
generati dalla CI e produce un unico JSON leggibile da Typst.

Metriche prodotte:
  Qualità:
    - Statement coverage e branch coverage
    - Risultati test (passati, falliti, skippati, pass rate)
    - Failure density (test falliti / KLOC)

  Manutenibilità:
    - Complessità ciclomatica (per funzione, per file, globale)
    - Coupling efferente (Ce) e afferente (Ca) per modulo
    - Indice di instabilità per modulo: Ce / (Ce + Ca)

Dipendenze:
    - radon (complessità ciclomatica)

Uso:
  python scripts/collect_metrics.py \
    --coverage-json .coverage.json \
    --test-results test-results.xml \
    --source-dir backend/src \
    --output metrics/metrics.json
"""

import argparse
import ast
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


# ===========================================================================
# Conteggio righe sorgente
# ===========================================================================

def count_source_lines(source_dir: str) -> dict:
    """Conta le righe di codice Python (escluse righe vuote e commenti)."""
    src = Path(source_dir)
    file_lines = {}
    total = 0

    for py_file in sorted(src.rglob("*.py")):
        count = 0
        with open(py_file, encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    count += 1
        rel = str(py_file.relative_to(src))
        file_lines[rel] = count
        total += count

    return {"files": file_lines, "total": total}


# ===========================================================================
# Coverage (statement + branch)
# ===========================================================================

def parse_coverage_json(coverage_json_path: str) -> dict:
    """Estrae statement e branch coverage dal report JSON di coverage.py."""
    with open(coverage_json_path, encoding="utf-8") as f:
        data = json.load(f)

    totals = data.get("totals", {})

    files = {}
    for filepath, file_data in data.get("files", {}).items():
        summary = file_data.get("summary", {})
        files[filepath] = {
            "statements": summary.get("num_statements", 0),
            "missing": summary.get("missing_lines", 0),
            "branches": summary.get("num_branches", 0),
            "branches_missing": summary.get("missing_branches", 0),
            "statement_coverage_pct": summary.get("percent_covered", 0),
        }

    return {
        "statement": {
            "total": totals.get("num_statements", 0),
            "covered": totals.get("covered_lines", 0),
            "missing": totals.get("missing_lines", 0),
            "percentage": totals.get("percent_covered", 0),
        },
        "branch": {
            "total": totals.get("num_branches", 0),
            "covered": totals.get("num_branches", 0) - totals.get("missing_branches", 0),
            "missing": totals.get("missing_branches", 0),
            "percentage": float(totals.get("percent_covered_display", "0")),
        },
        "per_file": files,
    }


# ===========================================================================
# Risultati test (JUnit XML)
# ===========================================================================

def parse_test_results(test_results_path: str) -> dict:
    """Estrae i risultati dei test dal JUnit XML."""
    tree = ET.parse(test_results_path)
    root = tree.getroot()

    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]

    total = 0
    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    failures_list = []

    for suite in suites:
        for testcase in suite.findall("testcase"):
            total += 1
            failure = testcase.find("failure")
            error = testcase.find("error")
            skip = testcase.find("skipped")

            if failure is not None:
                failed += 1
                failures_list.append({
                    "test": f"{testcase.get('classname', '')}.{testcase.get('name', '')}",
                    "message": failure.get("message", ""),
                })
            elif error is not None:
                errors += 1
                failures_list.append({
                    "test": f"{testcase.get('classname', '')}.{testcase.get('name', '')}",
                    "message": error.get("message", ""),
                })
            elif skip is not None:
                skipped += 1
            else:
                passed += 1

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "pass_rate_pct": round((passed / total) * 100, 2) if total > 0 else 0,
        "failures": failures_list,
    }


# ===========================================================================
# Failure density
# ===========================================================================

def compute_failure_density(test_results: dict, loc: dict) -> dict:
    """Failure density: test falliti per KLOC."""
    total_loc = loc["total"]
    failed = test_results["failed"] + test_results["errors"]
    kloc = total_loc / 1000 if total_loc > 0 else 1

    return {
        "failed_tests": failed,
        "source_loc": total_loc,
        "source_kloc": round(kloc, 2),
        "failure_density_per_kloc": round(failed / kloc, 4),
    }


# ===========================================================================
# Complessità ciclomatica (radon)
# ===========================================================================

def compute_cyclomatic_complexity(source_dir: str) -> dict:
    """Usa radon per calcolare la complessità ciclomatica."""
    result = subprocess.run(
        ["python", "-m", "radon", "cc", source_dir, "-s", "-j"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Errore radon: {result.stderr}")
        return {"files": {}, "summary": {}}

    raw = json.loads(result.stdout) if result.stdout.strip() else {}

    files = {}
    all_complexities = []

    for filepath, functions in raw.items():
        rel_path = (
            str(Path(filepath).relative_to(source_dir))
            if filepath.startswith(source_dir)
            else filepath
        )
        file_functions = []

        for func in functions:
            entry = {
                "name": func.get("name", ""),
                "type": func.get("type", ""),
                "complexity": func.get("complexity", 0),
                "rank": func.get("rank", ""),
                "lineno": func.get("lineno", 0),
            }
            file_functions.append(entry)
            all_complexities.append(func.get("complexity", 0))

        file_avg = (
            round(sum(f["complexity"] for f in file_functions) / len(file_functions), 2)
            if file_functions
            else 0
        )

        files[rel_path] = {
            "functions": file_functions,
            "average_complexity": file_avg,
        }

    total_avg = (
        round(sum(all_complexities) / len(all_complexities), 2)
        if all_complexities
        else 0
    )

    rank_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for c in all_complexities:
        if c <= 5:
            rank_counts["A"] += 1
        elif c <= 10:
            rank_counts["B"] += 1
        elif c <= 15:
            rank_counts["C"] += 1
        elif c <= 20:
            rank_counts["D"] += 1
        elif c <= 25:
            rank_counts["E"] += 1
        else:
            rank_counts["F"] += 1

    return {
        "files": files,
        "summary": {
            "total_functions": len(all_complexities),
            "average_complexity": total_avg,
            "max_complexity": max(all_complexities) if all_complexities else 0,
            "rank_distribution": rank_counts,
        },
    }


# ===========================================================================
# Coupling e Instability (analisi AST)
# ===========================================================================

def find_internal_modules(source_dir: str) -> dict[str, Path]:
    """Mappa nome_modulo -> path per tutti i moduli Python interni."""
    src = Path(source_dir)
    modules = {}

    for py_file in src.rglob("*.py"):
        rel = py_file.relative_to(src)
        parts = list(rel.parts)

        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].removesuffix(".py")

        if parts:
            module_name = ".".join(parts)
            modules[module_name] = py_file

    return modules


def extract_imports(filepath: Path) -> set[str]:
    """Estrae tutti i nomi dei moduli importati da un file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except SyntaxError:
        return set()

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
                imports.add(node.module)

    return imports


def compute_coupling(source_dir: str) -> dict:
    """
    Calcola Ce, Ca e Instability per ogni modulo top-level.

    Ce (efferent coupling): moduli interni da cui questo modulo dipende
    Ca (afferent coupling): moduli interni che dipendono da questo modulo
    Instability = Ce / (Ce + Ca)  ->  0 = stabile, 1 = instabile
    """
    src = Path(source_dir)

    # Identifica package/moduli top-level
    internal_top_level = set()
    for item in src.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            internal_top_level.add(item.name)
        elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
            internal_top_level.add(item.stem)

    # Per ogni file, trova da quali moduli top-level importa
    module_depends_on: dict[str, set[str]] = {m: set() for m in internal_top_level}

    for py_file in src.rglob("*.py"):
        rel = py_file.relative_to(src)
        owner_module = rel.parts[0].removesuffix(".py") if rel.parts else None

        if owner_module not in internal_top_level:
            continue

        imports = extract_imports(py_file)

        for imp in imports:
            top = imp.split(".")[0]
            if top in internal_top_level and top != owner_module:
                module_depends_on[owner_module].add(top)

    # Calcola Ce, Ca, Instability
    modules_metrics = {}
    for module in sorted(internal_top_level):
        ce = len(module_depends_on[module])
        ca = sum(
            1 for other, deps in module_depends_on.items()
            if module in deps and other != module
        )
        total = ce + ca
        instability = round(ce / total, 4) if total > 0 else 0.0

        modules_metrics[module] = {
            "efferent_coupling_Ce": ce,
            "afferent_coupling_Ca": ca,
            "instability_index": instability,
            "depends_on": sorted(module_depends_on[module]),
            "depended_by": sorted(
                other for other, deps in module_depends_on.items()
                if module in deps and other != module
            ),
        }

    all_ce = [m["efferent_coupling_Ce"] for m in modules_metrics.values()]
    all_ca = [m["afferent_coupling_Ca"] for m in modules_metrics.values()]
    all_inst = [m["instability_index"] for m in modules_metrics.values()]

    return {
        "modules": modules_metrics,
        "summary": {
            "total_modules": len(modules_metrics),
            "average_efferent_coupling": round(sum(all_ce) / len(all_ce), 2) if all_ce else 0,
            "average_afferent_coupling": round(sum(all_ca) / len(all_ca), 2) if all_ca else 0,
            "average_instability": round(sum(all_inst) / len(all_inst), 4) if all_inst else 0,
        },
    }


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Raccoglie metriche di qualità e manutenibilità per Typst"
    )
    parser.add_argument("--coverage-json", default=".coverage.json")
    parser.add_argument("--test-results", default="test-results.xml")
    parser.add_argument("--source-dir", default="backend/src")
    parser.add_argument("--output", default="metrics/metrics.json")
    args = parser.parse_args()

    print(f"Raccolta metriche da {args.source_dir}...\n")

    # --- Qualità ---
    loc = count_source_lines(args.source_dir)
    coverage = parse_coverage_json(args.coverage_json)
    test_results = parse_test_results(args.test_results)
    failure_density = compute_failure_density(test_results, loc)

    # --- Manutenibilità ---
    complexity = compute_cyclomatic_complexity(args.source_dir)
    coupling = compute_coupling(args.source_dir)

    # --- JSON finale ---
    metrics = {
        "quality": {
            "coverage": coverage,
            "tests": test_results,
            "failure_density": failure_density,
            "source_lines": loc,
        },
        "maintainability": {
            "cyclomatic_complexity": complexity,
            "coupling_and_instability": coupling,
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # --- Riepilogo ---
    cc = complexity["summary"]
    cs = coupling["summary"]
    print(f"Metriche salvate in {output_path}\n")
    print("  QUALITÀ")
    print(f"    Statement coverage:  {coverage['statement']['percentage']}%")
    print(f"    Branch coverage:     {coverage['branch']['percentage']}%")
    print(f"    Test passati:        {test_results['passed']}/{test_results['total']}")
    print(f"    Failure density:     {failure_density['failure_density_per_kloc']} / KLOC")
    print()
    print("  MANUTENIBILITÀ")
    print(f"    Complessità media:   {cc.get('average_complexity', 0)}")
    print(f"    Complessità massima: {cc.get('max_complexity', 0)}")
    print(f"    Moduli analizzati:   {cs.get('total_modules', 0)}")
    print(f"    Instabilità media:   {cs.get('average_instability', 0)}")


if __name__ == "__main__":
    main()
