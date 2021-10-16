#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result
to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path, index_col="id")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    logger.info(
        "Filtering price column by the values ​​agreed with the business team: %s-%s",
        args.min_price, args.max_price)
    df['last_review'] = pd.to_datetime(df['last_review'])
    logger.info("Transforming last_review column as date type.")

    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(
        40.5, 41.2)
    df = df[idx].copy()

    df.to_csv("clean_sample.csv")
    logger.info("Save dataset clean")

    #update wandb
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")

    logger.info("Upload dataset clean wandb")
    run.log_artifact(artifact)

    os.remove('clean_sample.csv')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument("--input_artifact",
                        type=str,
                        help='Input artifact name',
                        required=True)

    parser.add_argument("--output_artifact",
                        type=str,
                        help='Output artifact description',
                        required=True)

    parser.add_argument("--output_type",
                        type=str,
                        help='Output artifact type',
                        required=True)

    parser.add_argument("--output_description",
                        type=str,
                        help='Output artifact description',
                        required=True)

    parser.add_argument("--min_price",
                        type=int,
                        help='Minimum price limit',
                        required=True)

    parser.add_argument("--max_price",
                        type=int,
                        help='Maximum price limit',
                        required=True)

    args = parser.parse_args()

    go(args)
