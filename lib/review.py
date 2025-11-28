from __init__ import CONN, CURSOR
from employee import Employee

class Review:

    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee ID: {self.employee_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    # ---------------------------
    # PROPERTY VALIDATION
    # ---------------------------

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if type(value) is not int or value < 2000:
            raise ValueError("Year must be an integer >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if type(value) is not str or len(value.strip()) == 0:
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError("Employee must exist before using its id")
        self._employee_id = value

    # ---------------------------
    # ORM METHODS
    # ---------------------------

    def save(self):
        """Insert into DB and update id"""
        CURSOR.execute("""
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """, (self.year, self.summary, self.employee_id))

        CONN.commit()
        self.id = CURSOR.lastrowid
        Review.all[self.id] = self
        return self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review_id, year, summary, employee_id = row

        if review_id in cls.all:
            review = cls.all[review_id]
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        else:
            review = cls(year, summary, employee_id, review_id)
            cls.all[review_id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM reviews").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def update(self):
        CURSOR.execute("""
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """, (self.year, self.summary, self.employee_id, self.id))

        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()

        del Review.all[self.id]
        self.id = None
