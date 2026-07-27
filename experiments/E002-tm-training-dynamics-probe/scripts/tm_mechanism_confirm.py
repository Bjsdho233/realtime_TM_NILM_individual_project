from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tmp"))

import tm_mechanism_followup as followup  # noqa: E402
import tm_mechanism_probe as probe  # noqa: E402


OUTPUT_PATH = ROOT / "tmp" / "tm_mechanism_confirmation_results.json"


def summarize(runs):
    summary = {}
    for variant in ["baseline", "hard100", "balanced"]:
        selected = sorted(
            [run for run in runs if run["variant"] == variant], key=lambda run: run["seed"]
        )
        macro = np.asarray([run["macro_f1"] for run in selected])
        accuracy = np.asarray([run["accuracy"] for run in selected])
        summary[variant] = {
            "macro_f1_mean": float(np.mean(macro)),
            "macro_f1_std": float(np.std(macro, ddof=1)),
            "macro_f1_by_seed": macro.tolist(),
            "accuracy_mean": float(np.mean(accuracy)),
            "accuracy_std": float(np.std(accuracy, ddof=1)),
            "class_f1_mean": {
                name: float(np.mean([run["class_f1"][name] for run in selected]))
                for name in probe.CLASSES
            },
            "training_seconds_mean": float(
                np.mean([run["training_seconds"] for run in selected])
            ),
        }

    baseline = np.asarray(summary["baseline"]["macro_f1_by_seed"])
    for variant in ["hard100", "balanced"]:
        difference = np.asarray(summary[variant]["macro_f1_by_seed"]) - baseline
        summary[variant]["paired_macro_f1_delta"] = {
            "mean": float(np.mean(difference)),
            "std": float(np.std(difference, ddof=1)),
            "by_seed": difference.tolist(),
            "wins": int(np.sum(difference > 0)),
        }
    return summary


def main() -> None:
    probe.disable_progress_bars()
    x_train, y_train, x_test, y_test = probe.prepare_boolean_data()
    probe.verify_random_step(x_train, y_train)

    first = json.loads((ROOT / "tmp" / "tm_mechanism_probe_results.json").read_text())
    second = json.loads((ROOT / "tmp" / "tm_mechanism_followup_results.json").read_text())
    runs = [run for run in first["runs"] if run["variant"] in {"baseline", "hard100"}]
    runs += [run for run in second["runs"] if run["variant"] == "balanced"]

    baseline_variant = {
        "name": "baseline",
        "T": 20,
        "negative_mode": "random",
        "shuffle": False,
    }
    hard_variant = {
        "name": "hard100",
        "T": 20,
        "negative_mode": "hard",
        "shuffle": False,
    }
    balanced_variant = {
        "name": "balanced",
        "negative_mode": "random",
        "order_mode": "balanced",
    }

    for seed in [3, 4]:
        for variant in [baseline_variant, hard_variant]:
            result = probe.run_variant(
                variant, seed, x_train, y_train, x_test, y_test
            )
            runs.append(result)
            print(
                f"{result['variant']:>8} seed={seed} "
                f"acc={result['accuracy']:.4f} macro_f1={result['macro_f1']:.4f}",
                flush=True,
            )

        result = followup.run_variant(
            balanced_variant, seed, x_train, y_train, x_test, y_test
        )
        runs.append(result)
        print(
            f"{result['variant']:>8} seed={seed} "
            f"acc={result['accuracy']:.4f} macro_f1={result['macro_f1']:.4f}",
            flush=True,
        )

    output = {
        "scope": {
            "purpose": "five_seed_exploratory_confirmation",
            "formal_model_selection": False,
            "seeds": [0, 1, 2, 3, 4],
        },
        "runs": sorted(runs, key=lambda run: (run["variant"], run["seed"])),
        "summary": summarize(runs),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"saved={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
