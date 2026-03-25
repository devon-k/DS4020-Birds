from pathlib import Path
import pandas as pd

CONFIDENCE_THRESHOLD = 0.80

def make_occupancy_table(
    master_csv_path: Path,
    output_dir: Path,
    confidence_threshold: float = CONFIDENCE_THRESHOLD
):
    master_csv_path = Path(master_csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(master_csv_path)

    required_cols = ["confidence", "common_name", "location", "date", "formatted_filename"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[df["confidence"] >= confidence_threshold].copy()

    if df.empty:
        empty_out = output_dir / "occupancy_table_80.csv"
        pd.DataFrame().to_csv(empty_out, index=False)
        print(f"No detections at or above {confidence_threshold}. Wrote empty file to {empty_out}")
        return

    # Presence indicator
    df["occupied"] = 1

    # Collapse repeated detections within the same recording
    grouped = (
        df.groupby(["location", "date", "formatted_filename", "common_name"], as_index=False)["occupied"]
        .max()
    )

    # Pivot to wide occupancy table
    occupancy_table = grouped.pivot_table(
        index=["location", "date", "formatted_filename"],
        columns="common_name",
        values="occupied",
        fill_value=0
    ).reset_index()

    occupancy_table.columns.name = None

    out_path = output_dir / "occupancy_table_80.csv"
    occupancy_table.to_csv(out_path, index=False)

    print(f"Occupancy table saved to: {out_path}")
    print(f"Rows: {len(occupancy_table)}")
    print(f"Species columns: {len(occupancy_table.columns) - 3}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).absolute().parent.parent
    make_occupancy_table(
        master_csv_path=BASE_DIR / "compiled" / "birdnet_master.csv",
        output_dir=BASE_DIR / "compiled",
        confidence_threshold=0.80
    )
