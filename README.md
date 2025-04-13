# Rates API

## Table of Contents

1. [Analysis](#analysis)
2. [Tech Stack](#tech-stack)
3. [ETL Process](#etl-process)
4. [API Design](#api-design)
5. [Calculation Logic](#calculation-logic)

---

## Analysis

### Data Source Evaluation

- Checked both provided websites (Pensford and Chatham Financial) for available APIs.
- Chose to use the endpoint from Pensford—which returns data in XML format—as it is more up-to-date and more reliable than downloadable spreadsheets.

### Project Structure

- Explored the option of using a **modularized structure** for maintainability and possible future scaling.
- Ultimately decided on a **flat file structure** for simplicity and due to the small project size.
- Defined classes (`Loan`, `Floating Rate`) in a separate `models.py` file for improved organization and modularity.

---

## Tech Stack

- **Database**: `SQLite`
- Lightweight, and ideal for prototypes and small-scale applications.

- **API Framework**: `FastAPI`
- Chosen as it is asynchronous and has built-in validation.
- Compared against:
    - Flask: synchronous and has less built-in features
    - Django: too heavy for small projects

---

## ETL Process

1. **Extract**
- Fetched data from an XML-based API endpoint using `requests` library.
- Used `pandas.read_xml()` for parsing.

2. **Transform**
- Standardized date formats to ensure consistency throughout the code.
- Converted percentages to decimals for rate calculations.

3. **Load**
- Created a SQLite table `fwd_curve` with the following columns (attributes derived from the XML endpoint).
    - `ResetDate`: The date on which the new rate is determined
    - `ONEMTSOFR`: 1-month Term SOFR
    - `THREEMTSOFR`: 3-month Term SOFR
    - `ONEMISDASOFR`: 1-Month ISDA SOFR
- Loaded transformed data into a SQLite table using `pandas.to_sql()`.

4. **Performance Consideration**
- Decided to use `pandas` for its ease of use as it can parse XML efficiently, and seamlessly integrate with data transformation and loading.
- Considered using a `delete + append` operation instead of `if_exists='replace'` when loading data to avoid potential slow performance with larger datasets. However ultimately decided to use `if_exists='replace'` due to the small size of the dataset, simpler implementation and lower risk of errors.

---

## API Design

### POST Endpoint

Created a POST API endpoint that accepts a JSON payload containing:
- `maturity_date`: The target end date to determine the rate calculation range
- `reference_rate`: The type of interest rate
- `rate_floor` and `rate_ceiling`: Constraints for the calculated rate
- `rate_spread`: The fixed value added to the reference rate's projected value
- `months`: The time period over which the rate is applied (optional parameter)

Response returns a list of calculated new rates for dates ranging from current month to the provided `maturity_date`.

### Request/Response Models

- Created `Loan` (request) and `Floating Rate` (response) models based on provided sample JSON structures.
- Used Pydantic models for built-in validation and clarity.

---

## Calculation Logic

1. **Filter Data**
- Extract rows from SQLite table `fwd_curve` where the `ResetDate` is less than the user-inputted `maturity_date`.

2. **Calculate New Rates**
- For each row:
    - Add the reference rate's projected value from the `fwd_curve` table to the user-inputted `rate_spread`.
    - Limit the result between `rate_floor` and `rate_ceiling`.
- Return a list of dictionaries with `date` and the new `rate`.

3. **Performance Consideration**
- Used index-based access (`row[0]`) instead of `row['column_name']` for slight performance improvement.
- Selecting only the necessary columns in the SQLite query to improve query performance.
- Added an optional `months` parameter, which defaults to 1 if not provided. The parameter maps user inputs (e.g. "1" for `months` and "sofr" for `reference_rate`) to the corresponding column in the SQLite table (e.g. selecting the `ONEMTSOFR` column when "1" and "sofr" are provided).