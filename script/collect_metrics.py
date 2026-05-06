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
    - Code smell density (violazioni ruff per 100 LOC)

Dipendenze:
    - radon (complessità ciclomatica)
    - ruff (code smell detection)

Uso:
  poetry run python scripts/collect_metrics.py \
    --coverage-json .coverage.json \
    --test-results test-results.xml \
    --source-dir backend/src \
    --output metrics/metrics.json
"""

import argparse
import ast
import json
import subprocess
import sys
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
            "percentage": round(totals.get("percent_covered", 0), 2),
        },
        "branch": {
            "total": totals.get("num_branches", 0),
            "covered": totals.get("num_branches", 0) - totals.get("missing_branches", 0),
            "missing": totals.get("missing_branches", 0),
            "percentage": round(float(totals.get("percent_covered_display", "0")), 2),
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
        [sys.executable, "-m", "radon", "cc", source_dir, "-s", "-j"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  ATTENZIONE: radon non trovato o errore: {result.stderr.strip()}")
        print("  Installa con: poetry add --group dev radon")
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
# Coupling e Instability (analisi AST a livello di classi)
# ===========================================================================

def extract_classes(filepath: Path) -> list[str]:
    """Estrae i nomi delle classi definite in un file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except SyntaxError:
        return []

    return [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]


def extract_imported_names(filepath: Path) -> list[dict]:
    """
    Estrae tutti i nomi importati con il loro modulo sorgente.
    Ritorna lista di {"module": "core.domain.device", "name": "Device"}
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except SyntaxError:
        return []

    imported = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.append({"module": alias.name, "name": alias.name.split(".")[-1]})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imported.append({"module": node.module, "name": alias.name})

    return imported


def discover_packages(source_dir: str) -> dict[str, list[Path]]:
    """
    Scopre i package ricorsivamente. Un package è qualsiasi cartella
    che contiene almeno un file .py (non serve __init__.py).

    Con la struttura:
      backend/src/
        adapters/
          inbound/
            asset/
          outbound/
            compliance_standard/
        core/
          domain/
          ports/
          services/

    Produce package a tutti i livelli:
      "adapters.inbound.asset", "core.domain", "core.services", ecc.
    """
    src = Path(source_dir)
    packages: dict[str, list[Path]] = {}

    root_files = [
        f for f in src.glob("*.py")
        if f.name != "__init__.py"
    ]
    if root_files:
        packages["(root)"] = root_files

    def _scan(directory: Path, prefix: str):
        py_files = [
            f for f in directory.glob("*.py")
            if f.name != "__init__.py"
        ]

        if py_files:
            packages[prefix] = py_files

        for subdir in sorted(directory.iterdir()):
            if subdir.is_dir() and subdir.name != "__pycache__":
                has_python = any(subdir.rglob("*.py"))
                if has_python:
                    child_name = f"{prefix}.{subdir.name}"
                    _scan(subdir, child_name)

    for item in sorted(src.iterdir()):
        if item.is_dir() and item.name != "__pycache__":
            has_python = any(item.rglob("*.py"))
            if has_python:
                _scan(item, item.name)

    return packages


def compute_coupling(source_dir: str) -> dict:
    """
    Calcola Ce, Ca e Instability per ogni componente, contando le CLASSI.

    Per ogni componente:
      Ce = n. di classi ESTERNE da cui le classi del componente dipendono
      Ca = n. di classi INTERNE del componente da cui altri componenti dipendono
      Instability = Ce / (Ce + Ca)
        0.0 = massimamente stabile (tutti dipendono da me, io da nessuno)
        1.0 = massimamente instabile (io dipendo da tutti, nessuno da me)

    Un componente sano è vicino a 0 o a 1, mai a 0.5 (zona di dolore).
    """
    packages = discover_packages(source_dir)

    if not packages:
        return {"modules": {}, "summary": {}}

    # 1. Mappa: per ogni package, le classi che definisce
    #    package_classes["core.domain"] = {"Device", "Asset", "ComplianceStandard", ...}
    package_classes: dict[str, set[str]] = {}
    # Mappa inversa: classe -> package che la definisce
    class_to_package: dict[str, str] = {}

    for pkg_name, py_files in packages.items():
        classes = set()
        for py_file in py_files:
            for cls_name in extract_classes(py_file):
                classes.add(cls_name)
                class_to_package[cls_name] = pkg_name
        package_classes[pkg_name] = classes

    # 2. Per ogni package, trova le classi esterne da cui dipende (Ce)
    #    e traccia quali classi proprie sono importate da altri (per Ca)
    #
    #    Ce_classes[pkg] = set di classi esterne importate
    #    imported_from[pkg] = set di classi proprie importate da altri
    ce_classes: dict[str, set[str]] = {pkg: set() for pkg in packages}
    imported_from: dict[str, set[str]] = {pkg: set() for pkg in packages}
    # Archi unici tra componenti (per coefficient of coupling)
    dependency_edges: set[tuple[str, str]] = set()

    for pkg_name, py_files in packages.items():
        own_classes = package_classes[pkg_name]

        for py_file in py_files:
            for imp in extract_imported_names(py_file):
                name = imp["name"]
                module = imp["module"]

                # Determina a quale package appartiene il nome importato
                source_pkg = class_to_package.get(name)

                if source_pkg is None:
                    # Prova a risolvere dal modulo dell'import
                    parts = module.split(".")
                    for i in range(len(parts), 0, -1):
                        candidate = ".".join(parts[:i])
                        if candidate in packages and candidate != pkg_name:
                            source_pkg = candidate
                            break

                if source_pkg is None or source_pkg == pkg_name:
                    continue

                # Escludi relazioni parent-child
                if pkg_name.startswith(source_pkg + "."):
                    continue
                if source_pkg.startswith(pkg_name + "."):
                    continue

                # Traccia l'arco unico tra componenti
                dependency_edges.add((pkg_name, source_pkg))

                # È una classe? (inizia con maiuscola = convenzione Python)
                if name[0].isupper():
                    ce_classes[pkg_name].add(name)
                    imported_from[source_pkg].add(name)

    # 3. Calcola metriche per ogni package
    modules_metrics = {}
    for pkg in sorted(packages.keys()):
        own_classes = package_classes[pkg]
        ce = len(ce_classes[pkg])                   # classi esterne da cui dipendo
        ca = len(imported_from[pkg])                # mie classi da cui altri dipendono
        total = ce + ca
        instability = round(ce / total, 4) if total > 0 else 0.0

        # Zone secondo MPD13:
        # Ottimo: I <= 0.15 o I >= 0.85
        # Accettabile: I <= 0.30 o I >= 0.70
        # Zona di dolore: 0.30 < I < 0.70
        if instability <= 0.15 or instability >= 0.85:
            zone = "ottimo"
        elif instability <= 0.30 or instability >= 0.70:
            zone = "accettabile"
        else:
            zone = "zona di dolore"

        modules_metrics[pkg] = {
            "classes_defined": sorted(own_classes),
            "classes_count": len(own_classes),
            "efferent_coupling_Ce": ce,
            "efferent_classes": sorted(ce_classes[pkg]),
            "afferent_coupling_Ca": ca,
            "afferent_classes": sorted(imported_from[pkg]),
            "instability_index": instability,
            "zone": zone,
        }

    all_ce = [m["efferent_coupling_Ce"] for m in modules_metrics.values()]
    all_ca = [m["afferent_coupling_Ca"] for m in modules_metrics.values()]
    all_inst = [m["instability_index"] for m in modules_metrics.values()]
    n = len(modules_metrics)

    # Conta quanti sono in zona di dolore
    in_pain_zone = sum(1 for m in modules_metrics.values() if m["zone"] == "zona di dolore")

    # Coefficient of coupling = archi unici / numero componenti
    num_edges = len(dependency_edges)
    coefficient_of_coupling = round(num_edges / n, 4) if n else 0

    return {
        "modules": modules_metrics,
        "dependency_edges": sorted(
            [{"from": e[0], "to": e[1]} for e in dependency_edges],
            key=lambda x: (x["from"], x["to"]),
        ),
        "summary": {
            "total_modules": n,
            "total_dependency_edges": num_edges,
            "coefficient_of_coupling": coefficient_of_coupling,
            "coefficient_of_coupling_threshold": {
                "acceptable": 0.4,
                "optimal": 0.2,
            },
            "average_efferent_coupling": round(sum(all_ce) / n, 2) if n else 0,
            "average_afferent_coupling": round(sum(all_ca) / n, 2) if n else 0,
            "average_instability": round(sum(all_inst) / n, 4) if n else 0,
            "modules_in_pain_zone": in_pain_zone,
        },
    }


# ===========================================================================
# Code smell density (ruff)
# ===========================================================================

def compute_code_smells(source_dir: str, loc: dict) -> dict:
    """
    Usa ruff per rilevare code smell e calcola la densità
    per 100 righe di codice.

    Code smell density = violazioni totali / (LOC / 100)
    """
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", source_dir, "--output-format=json"],
        capture_output=True,
        text=True,
    )

    # ruff ritorna exit code 1 se trova violazioni — non è un errore
    if result.returncode not in (0, 1):
        print(f"  ATTENZIONE: ruff errore: {result.stderr.strip()}")
        return {"violations": [], "summary": {}}

    violations_raw = json.loads(result.stdout) if result.stdout.strip() else []

    # Raggruppa per regola
    by_rule: dict[str, int] = {}
    # Raggruppa per file
    by_file: dict[str, list[dict]] = {}

    for v in violations_raw:
        code = v.get("code", "unknown")
        by_rule[code] = by_rule.get(code, 0) + 1

        filename = v.get("filename", "")
        rel_path = (
            str(Path(filename).relative_to(source_dir))
            if filename.startswith(source_dir)
            else filename
        )

        entry = {
            "code": code,
            "message": v.get("message", ""),
            "line": v.get("location", {}).get("row", 0),
        }

        if rel_path not in by_file:
            by_file[rel_path] = []
        by_file[rel_path].append(entry)

    total_violations = len(violations_raw)
    total_loc = loc["total"]
    hectoloc = total_loc / 100 if total_loc > 0 else 1  # centinaia di LOC

    # Top regole violate (ordinate per frequenza)
    top_rules = sorted(by_rule.items(), key=lambda x: x[1], reverse=True)

    # Smell per file
    per_file_summary = {}
    for filepath, smells in by_file.items():
        file_loc = loc["files"].get(filepath, 0)
        file_hectoloc = file_loc / 100 if file_loc > 0 else 1
        per_file_summary[filepath] = {
            "violations": len(smells),
            "loc": file_loc,
            "density_per_100loc": round(len(smells) / file_hectoloc, 2),
            "details": smells,
        }

    return {
        "summary": {
            "total_violations": total_violations,
            "source_loc": total_loc,
            "density_per_100loc": round(total_violations / hectoloc, 4),
            "rules_violated": len(by_rule),
            "top_rules": [
                {"rule": code, "count": count}
                for code, count in top_rules[:10]
            ],
        },
        "per_file": per_file_summary,
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
    code_smells = compute_code_smells(args.source_dir, loc)

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
            "code_smells": code_smells,
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
    print(f"    Funzioni analizzate: {cc.get('total_functions', 0)}")
    print(f"    Moduli analizzati:   {cs.get('total_modules', 0)}")
    print(f"    Instabilità media:   {cs.get('average_instability', 0)}")
    coc = cs.get('coefficient_of_coupling', 0)
    coc_status = "ottimo" if coc <= 0.2 else ("accettabile" if coc <= 0.4 else "alto")
    print(f"    Coeff. coupling:     {coc} ({coc_status})")

    # Code smells
    sm = code_smells.get("summary", {})
    if sm:
        print()
        print("  CODE SMELLS")
        print(f"    Violazioni totali:   {sm.get('total_violations', 0)}")
        print(f"    Densità / 100 LOC:   {sm.get('density_per_100loc', 0)}")
        print(f"    Regole violate:      {sm.get('rules_violated', 0)}")
        top = sm.get("top_rules", [])
        if top:
            print("    Top violazioni:")
            for r in top[:5]:
                print(f"      {r['rule']:10s}  ×{r['count']}")

    # Dettaglio coupling
    if coupling.get("modules"):
        print("\n  COUPLING PER MODULO (a livello di classi)")
        for name, data in sorted(coupling["modules"].items()):
            if data["classes_count"] == 0 and data["efferent_coupling_Ce"] == 0:
                continue  # Salta moduli senza classi e senza dipendenze
            zone_label = f" [{data['zone']}]"
            print(
                f"    {name:45s}  Ce={data['efferent_coupling_Ce']}  "
                f"Ca={data['afferent_coupling_Ca']}  "
                f"I={data['instability_index']}{zone_label}"
            )
            if data["efferent_classes"]:
                print(f"      └─ dipende da classi: {', '.join(data['efferent_classes'])}")
            if data["afferent_classes"]:
                print(f"      └─ usato per classi:  {', '.join(data['afferent_classes'])}")

        pain = coupling["summary"].get("modules_in_pain_zone", 0)
        if pain > 0:
            print(f"\n    ⚠  {pain} modulo/i in zona di dolore (I tra 0.3 e 0.7)")


if __name__ == "__main__":
    main()