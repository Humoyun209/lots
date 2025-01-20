from datetime import datetime
import json
import sqlite3
from typing import NamedTuple


class Lot(NamedTuple):
    url: str
    description: str
    price: str
    author: str
    is_changed: bool


class HasLot(NamedTuple):
    has: bool
    is_changed: bool


class DataBase:
    def __init__(self, name) -> None:
        self.connect = sqlite3.connect(name)
        self.cursor = self.connect.cursor()

    def get_lots_json(self):
        with open("data/lots.json", "r") as f:
            lots = json.load(f)
            return lots

    def date_to_str(self, date: datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def str_to_date(self, date: str):
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    def insert_all_data(self):
        lots = self.get_lots_json()
        for lot in lots:
            with self.connect:
                self.cursor.execute(
                    "INSERT INTO lots(url, description, price) VALUES(?, ?, ?)",
                    (lot.get("url"), lot.get("description"), lot.get("price")),
                )

    def has_data(self, url: str, price: str) -> HasLot:
        with self.connect:
            cur = self.cursor.execute("SELECT * FROM lots WHERE url = ?", (url,))
            result = cur.fetchone()

            if bool(result) and result[3] == price:
                return HasLot(has=True, is_changed=False)
            elif bool(result):
                self.cursor.execute("DELETE FROM lots WHERE url = ?", (url,))
                self.connect.commit()
                return HasLot(has=False, is_changed=True)
            else:
                return HasLot(has=False, is_changed=False)

    def delete_all_data(self):
        with self.connect:
            self.cursor.executescript(
                """BEGIN TRANSACTION;
                DELETE FROM lots;
                DELETE FROM sqlite_sequence WHERE name = 'lots';
                COMMIT;"""
            )
            self.connect.commit()

    def insert_lots(self):
        lots = self.get_lots_json()
        new_lots: list[Lot] = []
        with self.connect:
            for lot in lots:
                has_lot: HasLot = self.has_data(lot.get("url"), lot.get("price"))
                if not has_lot.has:
                    self.cursor.execute(
                        "INSERT INTO lots(url, description, price, author, is_changed, created) VALUES(?, ?, ?, ?, ?, ?)",
                        (
                            lot.get("url"),
                            lot.get("description"),
                            lot.get("price"),
                            lot.get("author"),
                            int(has_lot.is_changed),
                            self.date_to_str(datetime.now()),
                        ),
                    )
                    new_lots.append(
                        Lot(
                            url=lot.get("url"),
                            description=lot.get("description"),
                            price=lot.get("price"),
                            author=lot.get("author"),
                            is_changed=has_lot.is_changed,
                        )
                    )
        return new_lots
