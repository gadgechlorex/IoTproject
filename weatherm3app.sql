CREATE TABLE customer (
  id serial,
  email varchar(255) NOT NULL,
  name varchar(255) NOT NULL,
  PRIMARY KEY (id));

/*
 one-to-many: Book has many reviews
*/

CREATE TABLE readings (
  id serial,
  customer_id integer NOT NULL,
  temperature FLOAT(2) NOT NULL,
  humidity FLOAT(2) NOT NULL,
  reading_time timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (customer_id)
      REFERENCES customer(id)
      ON DELETE CASCADE
);


