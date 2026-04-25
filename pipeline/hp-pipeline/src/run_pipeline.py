"""Main entry point for the HP classification pipeline.

Usage:
    python -m src.run_pipeline --input data/uppgifter.jsonl --output output/full/
    python -m src.run_pipeline --input data/uppgifter_sample.jsonl --output output/sample/ --limit 10
"""
import argparse
from pathlib import Path

from .step1_describe import run_step1
from .step2_cluster import run_step2
from .step3_taxonomy import run_step3
from .step4_classify import run_step4
from .quality_check import write_quality_report


def main():
    parser = argparse.ArgumentParser(description="HP classification pipeline")
    parser.add_argument("--input", required=True, type=Path, help="Path to input JSONL file with tasks")
    parser.add_argument("--output", required=True, type=Path, help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tasks (for testing)")
    parser.add_argument("--skip-step1", action="store_true")
    parser.add_argument("--skip-step2", action="store_true")
    parser.add_argument("--skip-step3", action="store_true")
    parser.add_argument("--skip-step4", action="store_true")
    args = parser.parse_args()
    
    args.output.mkdir(parents=True, exist_ok=True)
    
    descriptions_path = args.output / "step1_descriptions.jsonl"
    clusters_path = args.output / "step2_clusters.json"
    taxonomy_path = args.output / "step3_taxonomy.json"
    classifications_path = args.output / "step4_classified.jsonl"
    quality_path = args.output / "quality_report.md"
    
    print("=" * 60)
    print("HP Classification Pipeline")
    print("=" * 60)
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    if args.limit:
        print(f"Limit:  {args.limit}")
    
    if not args.skip_step1:
        run_step1(args.input, descriptions_path, limit=args.limit)
    
    if not args.skip_step2:
        run_step2(descriptions_path, clusters_path)
    
    if not args.skip_step3:
        run_step3(clusters_path, taxonomy_path)
    
    if not args.skip_step4:
        # Limit input to step 4 if requested
        if args.limit:
            limited_input = args.output / "_limited_input.jsonl"
            with open(args.input, "r", encoding="utf-8") as src, open(limited_input, "w", encoding="utf-8") as dst:
                for i, line in enumerate(src):
                    if i >= args.limit:
                        break
                    dst.write(line)
            run_step4(limited_input, taxonomy_path, classifications_path)
        else:
            run_step4(args.input, taxonomy_path, classifications_path)
    
    write_quality_report(
        classifications_path=classifications_path,
        taxonomy_path=taxonomy_path,
        descriptions_path=descriptions_path,
        output_path=quality_path,
    )
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Read the quality report: {quality_path}")
    print("If verdict is ✅, taxonomy is ready to use.")
    print("If ⚠️ or ❌, consider running again or falling back to alternative 3 (hire pedagogue).")


if __name__ == "__main__":
    main()
