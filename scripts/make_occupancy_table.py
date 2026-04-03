from pathlib import Path
import pandas as pd

CONFIDENCE_THRESHOLD = 0.80

def make_detection_table(
    master_csv_path: Path,
    output_dir: Path,
    confidence_threshold: float = CONFIDENCE_THRESHOLD
):
    master_csv_path = Path(master_csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(master_csv_path)

    required_cols = ["confidence", "common_name", "location", "location_type", "recording_date", "formatted_filename"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[df["confidence"] >= confidence_threshold].copy()
    out_path = output_dir / f"detections_table_{int(confidence_threshold*100)}.csv"

    if df.empty:
        pd.DataFrame().to_csv(out_path, index=False)
        print(f"No detections at or above {confidence_threshold}. Wrote empty file to {out_path}")
        return

    # Presence indicator
    df["occupied"] = 1

    # Collapse repeated detections within the same recording
    grouped = (
        df.groupby(["location", "location_type", "recording_date", "formatted_filename", "common_name"], as_index=False)["occupied"]
        .max()
    )

    # Pivot to wide occupancy table
    detections_table = grouped.pivot_table(
        index=["location", "location_type", "recording_date", "formatted_filename"],
        columns="common_name",
        values="occupied",
        fill_value=0
    ).reset_index()

    detections_table.columns.name = None

    detections_table.to_csv(out_path, index=False)

    print(f"Detections table saved to: {out_path}")
    print(f"Rows: {len(detections_table)}")
    print(f"Species columns: {len(detections_table.columns) - 3}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).absolute().parent.parent
    make_detection_table(
        master_csv_path=BASE_DIR / "compiled" / "birdnet_master.csv",
        output_dir=BASE_DIR / "compiled",
        confidence_threshold=0.80
    )
