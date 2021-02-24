from pathlib import Path
from pymaybe import maybe
from bs4 import BeautifulSoup
import pandas as pd
from models.Database import Database, Table, Column, Field, Order
from models import PipelineProgressBar
from helpers.get_urls_table_from_scraped_database import (
    get_urls_table_from_scraped_database,
)
from helpers.update_analysis_database import update_analysis_database
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("summaries")

    db.table("domains").create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("summary", "text", nullable=True),
    ).primary_key("id").unique("domain").if_not_exists().execute()

    # Clear records for domain/url
    if reset:
        db.table("domains").delete().where(
            Field("domain").glob_unless_none(domain)
        ).execute()

    # Fetch IDs for level-0 domain from scrape database, ignoring URLs already
    # scraped
    print(
        "Skipping",
        db.table("domains").count("id").value(),
        "domains already analyzed...",
    )

    scraped_urls = get_urls_table_from_scraped_database()
    with scraped_urls.database.start_transaction() as transaction:
        scraped_urls.database.attach(db, name="analysis", transaction=transaction)

        ids_of_scraped_records = (
            scraped_urls.select("id")
            .where(
                Field("domain").glob_unless_none(domain)
                & (Field("level") == 0)
                & (Field("html").notnull())
                & Field("domain").notin(
                    db.table("domains").schema("analysis").select("domain")
                )
            )
            .orderby("domain", order=Order.desc)
            .orderby("id")
            .values(transaction=transaction)
        )

    # Analyze each HTML snippet in database
    progress = PipelineProgressBar(PIPELINE)
    analyzed_domains = []
    for scraped_record_id in progress.iterate(ids_of_scraped_records):
        scraped_record = (
            scraped_urls.select("id", "domain", "url", "html")
            .where(Field("id") == scraped_record_id)
            .first()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        url = scraped_record["url"]
        html = scraped_record["html"]

        progress.set_current_url(url)

        # If this domain has already been analyzed, let's skip it.
        if analyzed_domains.count(domain) >= 1:
            progress.print("Skipping", domain, "...", "Already done")
            continue

        # Prepare text extraction from HTML
        soup = BeautifulSoup(html, "lxml")

        # Search for meta description in HTML
        # NOTE: In the future, we may use NPL algorithms to extract a summary
        # based on word frequency across all URLs of each domain

        # Search page meta description
        description = (
            maybe(soup.head)
            .select_one('meta[name="description"]')["content"]
            .strip()
            .or_else(None)
        )

        # Search meta og:description
        if not description:
            description = (
                maybe(soup.head)
                .select_one('meta[property="og:description"]')["content"]
                .strip()
                .or_else(None)
            )

        # Search meta og:description
        if not description:
            description = (
                maybe(soup.head)
                .select_one('meta[name="twitter:description"]')["content"]
                .strip()
                .or_else(None)
            )

        # Write summary to database
        db.table("domains").insert(
            domain=domain, summary=(description or None)
        ).execute()

        # NOTE: We currently have duplicate domains in our scraped dataset, so
        # we need to add finished domains here, so we skip them on the second
        # round (otherwise, we get a non-unique domain error).
        analyzed_domains.append(domain)

    # Get data
    df = (
        db.table("domains")
        .select(
            "domain",
            "summary",
        )
        .to_dataframe()
    )

    # Sort
    df = df.sort_values(by=["domain"])

    print("Found", df["summary"].count(), "/", len(df.index), "summaries")

    # Write to analysis database
    update_analysis_database(df[["domain", "summary"]])

    # Save as JSON
    save_result(PIPELINE, df)