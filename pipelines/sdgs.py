from pathlib import Path
import json
from bs4 import BeautifulSoup
import pandas as pd
from database import Database, Column, Field, Order
from helpers.get_scraped_database import get_scraped_database
from helpers.find_sdg_keywords_in_text import find_sdg_keywords_in_text
from helpers.save_result import save_result

PIPELINE = Path(__file__).stem


def aggregate_rows_by_domain(row):
    d = {}

    for column in row.columns:
        if column.endswith("_matches_count") or column == "word_count":
            d[column] = row[column].sum()

    return pd.Series(d)


def run_pipeline(domain, url, reset):
    # Create database
    db = Database("sdgs")
    db.create(
        Column("id", "integer", nullable=False),
        Column("domain", "text", nullable=False),
        Column("url", "text", nullable=False),
        Column("matches", "JSON"),
        Column("word_count", "integer", nullable=False),
        Column("CHECK(domain <> '')"),
        Column("CHECK(url <> '')"),
    ).if_not_exists().unique("url").primary_key("id").execute()

    # Clear records for domain/url
    if reset:
        db.delete().where(
            Field("domain").glob_unless_none(domain)
            & Field("url").glob_unless_none(url)
        ).execute()

    # Fetch IDs for domain/url from scrape database
    scraped_db = get_scraped_database()
    ids_of_scraped_records = (
        scraped_db.select("id")
        .where(
            Field("domain").glob_unless_none(domain)
            & Field("url").glob_unless_none(url)
            & Field("html").notnull()
        )
        .orderby("domain", order=Order.desc)
        .orderby("id")
        .fetch_values()
    )

    # Fetch analyzed URLs
    analyzed_urls = db.select("url").fetch_values()

    # Analyze each HTML snippet in database
    for scraped_record_id in ids_of_scraped_records:
        scraped_record = (
            scraped_db.select("id", "domain", "url", "html")
            .where(Field("id") == scraped_record_id)
            .fetch()
        )
        id = scraped_record["id"]
        domain = scraped_record["domain"]
        url = scraped_record["url"]
        html = scraped_record["html"]

        # If this URL has already been analyzed, let's skip it.
        if analyzed_urls.count(url) >= 1:
            continue

        print(
            "Searching for keywords in scraped HTML for", url, end=" ... ", flush=True
        )

        # Prepare text extraction from HTML
        soup = BeautifulSoup(html, "html.parser")
        word_count = len(soup.get_text(separator=" ", strip=True).split())

        # Search for matches in the HTML
        # After an item is parsed/searced, we remove the item with decompose(),
        # so that we avoid duplicates (if one tag is nested inside another, for
        # example)
        matches = {}

        # Search page title
        title = soup.head.find("title")
        find_sdg_keywords_in_text(
            title.get_text(separator=" ").strip(), matches, tag="title"
        )
        title.decompose()

        # Search page meta description
        description = soup.head.select_one('meta[name="description"]')
        find_sdg_keywords_in_text(
            description["content"].strip(), matches, tag="meta description"
        )
        description.decompose()

        # Search body
        SEARCH_TAGS = [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
        ]
        for tag in SEARCH_TAGS:
            for item in soup.body.find_all(tag):
                find_sdg_keywords_in_text(
                    item.get_text(separator=" ").strip(), matches, tag
                )
                item.decompose()

        find_sdg_keywords_in_text(
            soup.get_text(separator=" ").strip(), matches, tag="other"
        )

        # Write matches to database
        db.insert(
            domain=domain,
            url=url,
            matches=json.dumps(matches),
            word_count=word_count,
        ).execute()

        print("Done")

    # Combine by domain
    df = db.to_pandas_dataframe("domain", "url", "matches", "word_count")

    # Get and count matches for each SDG of each row
    sdg_keys = list("sdg" + str(i) for i in range(1, 18))
    for key in ["sdgs", *sdg_keys]:
        df[key + "_matches"] = df.apply(
            lambda row: json.loads(row["matches"]).get(key, []), axis=1
        )
        df[key + "_matches_count"] = df.apply(
            lambda row: len(row[key + "_matches"]), axis=1
        )

    # Drop matches column
    df = df.drop(columns=["matches"])

    # Sort
    df = df.sort_values(by=["domain", "url"])

    # Save as JSON
    save_result(PIPELINE, "urls", df.to_dict(orient="records"))

    # Aggregate by domain
    df = df.groupby(by=["domain"]).apply(aggregate_rows_by_domain)
    df = df.reset_index()

    # Sort
    df = df.sort_values(by=["domain"])

    # Save as JSON
    save_result(PIPELINE, "domains", df.to_dict(orient="records"))
