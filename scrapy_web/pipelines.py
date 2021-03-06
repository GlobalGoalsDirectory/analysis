import os
import datetime
import traceback
from models.Database import Database, Field
from helpers.get_html_asset_path import get_html_asset_path
from helpers.write_gzipped_asset import write_gzipped_asset


class WriteWebsitePipeline(object):
    def process_item(self, item, spider):
        item_class = type(item).__name__

        db = Database(spider.database_name)
        id = spider.url_id
        url = spider.url
        domain_id = spider.domain_id
        domain = spider.domain
        level = spider.level

        if item_class == "Website":
            try:
                with db.start_transaction() as transaction:
                    # Get HTML asset path
                    html_file = get_html_asset_path(id)

                    # Add scraped HTML to the database
                    db.table("url").set(
                        html_file=html_file,
                        scraped_at=datetime.datetime.utcnow(),
                    ).where(Field("id") == id).execute(transaction=transaction)

                    # Add collected links to the database
                    table = db.table("url")
                    for link in item["links"]:
                        table.insert(
                            url=link,
                            domain_id=domain_id,
                            level=level + 1,
                        ).on_conflict(table.url).do_nothing().execute(
                            transaction=transaction
                        )

                    # Write HTML asset
                    write_gzipped_asset(path=html_file, content=item["html"])

            except Exception as error:
                traceback_str = "".join(traceback.format_tb(error.__traceback__))
                failure = repr(str(error) + "\n" + traceback_str)
                print(failure)
                db.table("url").set(
                    error=failure, scraped_at=datetime.datetime.utcnow()
                ).where(Field("id") == id).execute()

        # Add error to the database
        elif item_class == "Error":
            print(item["message"])
            db.table("url").set(
                error=item["message"], scraped_at=datetime.datetime.utcnow()
            ).where(Field("id") == id).execute()

        # Return nothing
        # With large arrays, we run into an issue when trying to pass it from
        # one process to another.
        return None
