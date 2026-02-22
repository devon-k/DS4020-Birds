from pathlib import Path
import pandas as pd

from ARU_DataHelper import ARUDataHelper


def consolidate_outputs(
    outputs_dir: Path,
    compiled_dir: Path,
    min_confidence: float = 0.0
):
    """
    Consolidate BirdNET output CSV files into a single master dataset.

    This function assumes:
    - CSV filenames follow the formatted naming convention created by copy_inputs
    - Metadata is parsed exclusively using ARUDataHelper
    """

    outputs_dir = Path(outputs_dir)
    compiled_dir = Path(compiled_dir)
    compiled_dir.mkdir(parents=True, exist_ok=True)

    master_csv = compiled_dir / "birdnet_master.csv"

    all_dfs = []
    csv_files = list(outputs_dir.glob("*.csv"))

    print(f"Found {len(csv_files)} BirdNET output files.")

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Skipping {csv_file.name}: {e}")
            continue

        # Load metadata via helper
        helper = ARUDataHelper()
        helper.input_formatted_filename(csv_file.name)

        # Attach metadata columns
        df["location"] = helper.location
        df["location_type"] = helper.location_type
        df["date"] = helper.date
        df["year"] = helper.year
        df["month"] = helper.month
        df["day"] = helper.day
        df["formatted_filename"] = helper.formatted_filename

        # Optional datetime column (useful later)
        df["recording_date"] = helper.to_datetime()

        # Optional confidence filter
        #if min_confidence > 0 and "Confidence" in df.columns:
        #    df = df[df["Confidence"] >= min_confidence]

        all_dfs.append(df)

    if not all_dfs:
        raise RuntimeError("No BirdNET outputs were successfully processed.")

    # Combine into master dataframe
    master_df = pd.concat(all_dfs, ignore_index=True)

    # Standardize column names (BirdNET + metadata)
    master_df.columns = (
        master_df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[()]", "", regex=True)
    )

    master_df.to_csv(master_csv, index=False)

    print(f"Master CSV written to: {master_csv}")
    print(f"Total detections: {len(master_df)}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).absolute().parent.parent

    consolidate_outputs(
        outputs_dir=BASE_DIR / "outputs",
        compiled_dir=BASE_DIR / "compiled",
        min_confidence=0.5
    )