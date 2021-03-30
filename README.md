# Capturing and Streaming Data Changes from Postgres

## Create Environment Variables

```sh
cp default.env .env
```

## Docker Compose

```bash
docker-compose up -d
```

## Initialising with some data

Create brands table inside the postgres database:

```sql
CREATE TABLE brands (
    id serial PRIMARY KEY,
    name VARCHAR (50)
);
```

## Reading the logs (in another terminal)

```sh
docker logs -f postgres-cdc-stream
```

Insert some records in the brands table:

```sql
INSERT INTO brands VALUES(1, 'Brand Name 1');
INSERT INTO brands VALUES(2, 'Brand Name 2');
UPDATE brands SET name = 'New Brand Name 1' WHERE id = 1;
UPDATE brands SET name = 'New Brand Name 2' WHERE id = 2;
```
