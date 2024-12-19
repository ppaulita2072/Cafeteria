CREATE TABLE property (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    person_id INT NOT NULL,
    quantity INT NOT NULL,
    symbol TEXT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES users(id)
);
