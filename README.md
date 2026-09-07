# BidFax Parser

## Overview

**BidFax Parser** is a system for automated collection of vehicle data from [BidFax](https://bidfax.info).

The primary purpose of the project is to collect structured vehicle data that can later be used to build a dataset.

The data collection process is divided into three main stages:

```text
Manufacturer Parser
        │
        ▼
brands_models.json
        │
        ▼
URL Parser
        │
        ▼
PostgreSQL
(lot URLs)
        │
        ▼
Car Lot Parser
        │
        ▼
PostgreSQL
(vehicle data)
```

At the current stage, the project implements the complete pipeline from obtaining the list of manufacturers and models to collecting and storing information about individual vehicle lots.

In the future, this project is intended to become a **data acquisition module** for a larger system, potentially based on an AI agent. The exact architecture and purpose of that future system have not yet been defined.

---

# Pipeline

The data collection pipeline consists of three main components:

1. `manufacturer_parse`
2. `url_parser`
3. `car_lot_parser`

Each component performs a separate task and passes its results to the next stage.

---

## 1. Manufacturer Parser

The Manufacturer Parser is responsible for building a dictionary of vehicle manufacturers and their models.

The script analyzes the structure of BidFax directly and generates a JSON file with the following structure:

```json
{
    "Toyota": [
        "Camry",
        "Corolla",
        "Land Cruiser"
    ],
    "BMW": [
        "3 Series",
        "5 Series"
    ]
}
```

Where:

* the key represents a vehicle manufacturer;
* the value is a list of models belonging to that manufacturer.

### Purpose

The generated JSON file is used by the next stage, `url_parser`.

The Manufacturer Parser is normally executed **once to generate the initial structure**.

A ready-to-use `brands_models.json` file is already included in the project.

If necessary, the file can be:

* manually extended with additional models;
* manually modified;
* completely regenerated using the Manufacturer Parser.

The JSON file therefore acts as a persistent reference structure for building model URLs.

---

# 2. URL Parser

The URL Parser is responsible for discovering individual vehicle lot URLs on BidFax.

It uses `brands_models.json` to sequentially process manufacturers and their models.

For example:

```text
Toyota
   │
   ▼
Camry
   │
   ▼
https://bidfax.info/toyota/camry/
```

The parser then uses pagination to iterate through the pages of the selected model:

```text
https://bidfax.info/toyota/camry/page/1/
https://bidfax.info/toyota/camry/page/2/
https://bidfax.info/toyota/camry/page/3/
...
```

A BidFax page contains up to 10 links to individual vehicle lots.

Therefore, each successful page iteration can produce multiple individual lot URLs.

---

## URL Parser Modes

The URL Parser supports several execution modes.

### All Manufacturers and Models

The parser sequentially processes the entire `brands_models.json` file:

```text
Toyota
 ├── Camry
 ├── Corolla
 ├── RAV4
 └── ...

BMW
 ├── X5
 ├── X3
 └── ...
```

### Specific Manufacturer and Model

The parser can also be limited to a specific manufacturer and model.

For example:

```text
Toyota → Camry
```

This mode is useful for testing or reprocessing a specific model.

---

## URL Parser Stop Conditions

The URL Parser supports several mechanisms for controlling when execution stops.

### Stop Page

A specific page limit can be configured.

For example:

```text
Start page: 1
Stop page: 100
```

In this case, the parser will process pages up to the configured limit.

### End of JSON

When running in full mode, the parser finishes after processing all manufacturers and models defined in `brands_models.json`.

### No More Lots

The primary mechanism for detecting that the current model has no more available lots is based on the result of processing a page.

If a page returns `None` instead of a list of discovered lots, the parser retries **the same page**.

A maximum of three attempts is performed for the same page.

For example:

```text
Page N
   ↓
lots found
   ↓
continue

Page N + 1
   ↓
None
   ↓
retry 1
   ↓
Page N + 1
   ↓
None
   ↓
retry 2
   ↓
Page N + 1
   ↓
None
   ↓
retry 3
   ↓
Page N + 1
   ↓
None
   ↓
STOP
```

Three consecutive unsuccessful attempts to retrieve the same page are treated as an indication that processing of the current model should stop.

After this condition is reached, the parser either:

* moves to the next model if the current execution mode allows the pipeline to continue;
* or terminates the entire pipeline if the configured global stop condition has been reached.

The retry mechanism therefore applies to **one specific page**, not to three consecutive pages.

This mechanism is currently heuristic. In the future, the parser may determine the end of pagination directly from the HTML structure of the page instead.

---

## Database Insertion

The URL Parser creates a `Car` object for every discovered lot.

At this stage, the object contains the URL and system fields such as:

* `status`;
* `created_at`.

Conceptually:

```text
Lot URL
   │
   ▼
Car
 ├── id
 ├── url
 ├── status
 └── created_at
```

The object is then stored in PostgreSQL and becomes available for the next stage of the pipeline.

---

## Duplicate URLs

The URL Parser may encounter a lot URL that already exists in the database.

Duplicate handling is delegated to the database configuration.

If an attempt is made to insert an already existing URL, the database ignores the duplicate entry.

This allows the URL Parser to safely process large numbers of pages without maintaining a separate in-memory collection of all previously discovered URLs.

---

# 3. Car Lot Parser

After the URL Parser has collected individual lot URLs, the Car Lot Parser processes the actual vehicle pages.

The Car Lot Parser retrieves a `Car` object from the database and uses its stored URL to obtain the corresponding BidFax page.

The general flow is:

```text
PostgreSQL
    │
    ▼
Car
    │
    ▼
URL
    │
    ▼
Page
    │
    ▼
HTML
    │
    ▼
Parser
    │
    ▼
Structured Data
    │
    ▼
Car
    │
    ▼
PostgreSQL
```

The parser extracts the available information from the vehicle page and writes the resulting data back to the `Car` object.

The initial database record:

```text
Car
 ├── id
 ├── url
 ├── status
 └── created_at
```

is therefore populated with the available vehicle information during this stage.

---

# Parallel Processing

Car lot processing is performed in parallel.

An `Orchestrator` is responsible for starting and managing multiple independent `Worker` processes.

The general architecture is:

```text
                    Orchestrator
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       Worker 1       Worker 2       Worker N
          │              │              │
          ▼              ▼              ▼
        Batch          Batch          Batch
          │              │              │
          ▼              ▼              ▼
        Parser         Parser         Parser
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                     PostgreSQL
```

Each Worker independently retrieves a batch of cars for processing.

This allows the workload to be distributed between multiple processes and significantly increases the processing speed when working with large numbers of lots.

---

# Batch Processing

The project uses batch processing to handle large amounts of data.

Workers do not load all available database records into memory at once.

Instead, records are processed in smaller batches:

```text
Database
   │
   ▼
Batch
   │
   ▼
Processing
   │
   ▼
Database
   │
   ▼
Next Batch
```

The batch size is configurable.

This approach prevents the application from keeping a large amount of data in memory and allows the pipeline to process large datasets without an artificial limit on the total number of records.

As long as new records are available and the data source is accessible, the system can continue processing them.

---

# Data Acquisition Client

Page retrieval is separated from the parsing logic.

The project currently contains a fully implemented client for **GoLogin**.

Its responsibility is to provide the application with the HTML content of a requested page.

Conceptually:

```text
Car URL
   │
   ▼
GoLogin Client
   │
   ▼
HTML
   │
   ▼
Car Lot Parser
```

The project itself only implements the interaction with the GoLogin API required to obtain the page.

GoLogin profile configuration, proxies, browser settings, and other profile-specific parameters are managed externally and are not part of the parser configuration.

---

## Alternative Data Acquisition Client

The project also contains a client implementation for **Bright Data**.

This allows the page acquisition mechanism to be replaced independently of the parsing logic.

Additional documentation describing how to switch between acquisition clients may be added separately.

---

# Error Handling

A Worker processes each individual lot URL separately.

If an error occurs while processing a specific URL, the original vehicle data is not intentionally discarded.

In case of an unsuccessful processing attempt, a minimal result is returned:

```
{
    "id": car_id,
    "url": url,
}
```

The `Car` object is still rewritten using this result.

This ensures that:

* the original URL is preserved;
* the vehicle ID is preserved;
* the processing operation does not intentionally delete the existing record;
* the pipeline can continue processing other vehicles.

The mechanism for automatically retrying or refreshing already processed vehicle records is currently not implemented.

---

# Database

The project uses **PostgreSQL** for persistent storage.

The database is **not created automatically by the project**.

A PostgreSQL database with the required schema must already exist before the application is started.

The project works with the existing database rather than provisioning a new one.

Conceptually, the database acts as the shared state between the URL collection and vehicle data collection stages:

```text
URL Parser
    │
    ▼
PostgreSQL
    │
    ▼
Car Lot Parser
    │
    ▼
PostgreSQL
```

The database schema is also used to coordinate parallel processing between Workers.

Tests include functionality for checking whether the existing database structure corresponds to the structure expected by the application.

---

# Current Limitations

Although the current pipeline is fully functional, several features are intentionally left for future development.

### Data Updates

There is currently no dedicated mechanism for periodically updating information for previously processed lots.

The current pipeline primarily focuses on collecting and storing the available data.

### Pagination End Detection

The URL Parser currently uses three failed attempts to retrieve the same page as an indication that the current model has no more available lots.

This is a heuristic and may later be replaced with direct detection based on the page's HTML structure.

### Database Provisioning

The project does not create or configure the PostgreSQL database automatically.

Database provisioning and initial schema creation are handled separately.

### Single Data Source

The current implementation is focused on BidFax.

The architecture, however, keeps data acquisition separate from parsing so that additional sources can potentially be integrated later.

---

# Project Structure

The project is logically divided into several independent areas:

```text
BidFax Parser
│
├── manufacturer_parse
│   └── Build manufacturer/model reference
│
├── url_parser
│   └── Discover individual vehicle lot URLs
│
├── car_lot_parser
│   └── Retrieve and parse vehicle information
│
├── workers
│   └── Parallel vehicle processing
│
├── orchestrator
│   └── Worker management
│
├── database
│   └── Database models and PostgreSQL interaction
│
├── data acquisition clients
│   ├── GoLogin
│   └── Bright Data
│
└── tests
    └── Component tests and database schema validation
```

The exact repository structure may change as the project evolves.

---

# Technology Stack

The main technologies used by the project are:

* **Python** — primary programming language
* **BeautifulSoup** — HTML parsing
* **SQLAlchemy** — PostgreSQL interaction
* **PostgreSQL** — persistent data storage
* **GoLogin** — page acquisition
* **Bright Data** — alternative page acquisition client
* **JSON** — manufacturer/model reference data

---

# Project Status

**Current status: Fully functional.**

All major stages of the current pipeline are implemented:

* [x] Manufacturer and model discovery
* [x] `brands_models.json` generation
* [x] Model URL generation
* [x] Pagination processing
* [x] Individual lot URL discovery
* [x] Lot URL storage in PostgreSQL
* [x] Database-level duplicate handling
* [x] Vehicle page retrieval
* [x] Vehicle data parsing
* [x] Vehicle data storage
* [x] Parallel processing
* [x] Batch processing
* [x] GoLogin client
* [x] Bright Data client
* [x] Component testing
* [x] Database schema validation

---

# Future Development

The current goal of the project is to provide a reliable and scalable mechanism for collecting structured vehicle data for dataset creation.

In the future, the BidFax Parser is expected to become one of the **data acquisition tools** within a larger AI-based system.

The general concept is:

```text
                 Future AI System
                        │
                        ▼
                Data Acquisition
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       BidFax        Source 2       Source N
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  Data Processing
                        │
                        ▼
                     Storage
                        │
                        ▼
                     Dataset
```

The exact architecture, capabilities, and purpose of the future AI agent have not yet been defined.

Therefore, the current project does not depend on any particular AI-agent implementation.

The immediate goal is to maintain a reliable and scalable data acquisition pipeline that can later be integrated into a larger system.

---

# Project Purpose

The primary purpose of **BidFax Parser** is to automatically collect structured vehicle information from BidFax for the creation of a dataset.

The complete current pipeline can be summarized as:

```text
BidFax
  │
  ▼
Manufacturers & Models
  │
  ▼
Model Pages
  │
  ▼
Individual Lot URLs
  │
  ▼
Vehicle Pages
  │
  ▼
Structured Vehicle Data
  │
  ▼
PostgreSQL
  │
  ▼
Dataset
```

The parser is not intended to be the final product.

It is a **data acquisition component** that currently solves one specific problem: collecting and structuring vehicle auction data from BidFax in a scalable and reusable way.

Its future role will be determined as the larger AI-agent system is designed.
