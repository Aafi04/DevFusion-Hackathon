# Enterprise Data Dictionary

## Table: `Album`
**Rows:** 347 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `AlbumId` | INTEGER | 0% | 0% | Unique identifier for the album. | System |
| `Title` | NVARCHAR(160) | 0% | 0% | Title of the album. |  |
| `ArtistId` | INTEGER | 0% | 0% | Foreign key referencing the Artist table, indicating the artist of the album. | System |

---
## Table: `Artist`
**Rows:** 275 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `ArtistId` | INTEGER | 0% | 0% | Unique identifier for the artist. | System |
| `Name` | NVARCHAR(120) | 0% | 0% | Name of the artist. |  |

---
## Table: `Customer`
**Rows:** 59 | **Health Score:** 92.5/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `CustomerId` | INTEGER | 0% | 0% | Unique identifier for the customer. | System |
| `FirstName` | NVARCHAR(40) | 0% | 0% | First name of the customer. | PII |
| `LastName` | NVARCHAR(20) | 0% | 0% | Last name of the customer. | PII |
| `Company` | NVARCHAR(80) | 0% | 0% | Company name of the customer. | PII |
| `Address` | NVARCHAR(70) | 0% | 0% | Street address of the customer. | PII |
| `City` | NVARCHAR(40) | 0% | 0% | City of the customer's address. | PII |
| `State` | NVARCHAR(40) | 0% | 0% | State of the customer's address. | PII |
| `Country` | NVARCHAR(40) | 0% | 0% | Country of the customer's address. | PII |
| `PostalCode` | NVARCHAR(10) | 0% | 0% | Postal code of the customer's address. | PII |
| `Phone` | NVARCHAR(24) | 0% | 0% | Phone number of the customer. | PII |
| `Fax` | NVARCHAR(24) | 0% | 0% | Fax number of the customer. | PII |
| `Email` | NVARCHAR(60) | 0% | 0% | Email address of the customer. | PII |
| `SupportRepId` | INTEGER | 0% | 0% | Foreign key referencing the Employee table, indicating the support representative for the customer. | System |

---
## Table: `Employee`
**Rows:** 8 | **Health Score:** 97.5/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `EmployeeId` | INTEGER | 0% | 0% | Unique identifier for the employee. | System |
| `LastName` | NVARCHAR(20) | 0% | 0% | Last name of the employee. | PII |
| `FirstName` | NVARCHAR(20) | 0% | 0% | First name of the employee. | PII |
| `Title` | NVARCHAR(30) | 0% | 0% | Job title of the employee. |  |
| `ReportsTo` | INTEGER | 0% | 0% | Foreign key referencing the Employee table itself, indicating the manager of the employee. | System |
| `BirthDate` | DATETIME | 0% | 0% | Date of birth of the employee. | PII |
| `HireDate` | DATETIME | 0% | 0% | Date when the employee was hired. |  |
| `Address` | NVARCHAR(70) | 0% | 0% | Street address of the employee. | PII |
| `City` | NVARCHAR(40) | 0% | 0% | City of the employee's address. | PII |
| `State` | NVARCHAR(40) | 0% | 0% | State of the employee's address. | PII |
| `Country` | NVARCHAR(40) | 0% | 0% | Country of the employee's address. | PII |
| `PostalCode` | NVARCHAR(10) | 0% | 0% | Postal code of the employee's address. | PII |
| `Phone` | NVARCHAR(24) | 0% | 0% | Phone number of the employee. | PII |
| `Fax` | NVARCHAR(24) | 0% | 0% | Fax number of the employee. | PII |
| `Email` | NVARCHAR(60) | 0% | 0% | Email address of the employee. | PII |

---
## Table: `Genre`
**Rows:** 25 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `GenreId` | INTEGER | 0% | 0% | Unique identifier for the music genre. | System |
| `Name` | NVARCHAR(120) | 0% | 0% | Name of the music genre. |  |

---
## Table: `Invoice`
**Rows:** 412 | **Health Score:** 97.5/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `InvoiceId` | INTEGER | 0% | 0% | Unique identifier for the invoice. | System |
| `CustomerId` | INTEGER | 0% | 0% | Foreign key referencing the Customer table, indicating the customer associated with the invoice. | System |
| `InvoiceDate` | DATETIME | 0% | 0% | Date when the invoice was issued. |  |
| `BillingAddress` | NVARCHAR(70) | 0% | 0% | Street address for billing on the invoice. | PII |
| `BillingCity` | NVARCHAR(40) | 0% | 0% | City for billing on the invoice. | PII |
| `BillingState` | NVARCHAR(40) | 0% | 0% | State for billing on the invoice. | PII |
| `BillingCountry` | NVARCHAR(40) | 0% | 0% | Country for billing on the invoice. | PII |
| `BillingPostalCode` | NVARCHAR(10) | 0% | 0% | Postal code for billing on the invoice. | PII |
| `Total` | NUMERIC(10, 2) | 0% | 0% | Total amount of the invoice. |  |

---
## Table: `InvoiceLine`
**Rows:** 2240 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `InvoiceLineId` | INTEGER | 0% | 0% | Unique identifier for the invoice line item. | System |
| `InvoiceId` | INTEGER | 0% | 0% | Foreign key referencing the Invoice table, indicating the invoice this line item belongs to. | System |
| `TrackId` | INTEGER | 0% | 0% | Foreign key referencing the Track table, indicating the track included in this invoice line item. | System |
| `UnitPrice` | NUMERIC(10, 2) | 0% | 0% | Unit price of the track in this invoice line item. |  |
| `Quantity` | INTEGER | 0% | 0% | Quantity of the track in this invoice line item. |  |

---
## Table: `MediaType`
**Rows:** 5 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `MediaTypeId` | INTEGER | 0% | 0% | Unique identifier for the media type. | System |
| `Name` | NVARCHAR(120) | 0% | 0% | Name of the media type (e.g., MPEG audio file, Protected AAC audio file). |  |

---
## Table: `Playlist`
**Rows:** 18 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `PlaylistId` | INTEGER | 0% | 0% | Unique identifier for the playlist. | System |
| `Name` | NVARCHAR(120) | 0% | 0% | Name of the playlist. |  |

---
## Table: `PlaylistTrack`
**Rows:** 8715 | **Health Score:** 100.0/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `PlaylistId` | INTEGER | 0% | 0% | Foreign key referencing the Playlist table, part of the composite primary key for a playlist track. | System |
| `TrackId` | INTEGER | 0% | 0% | Foreign key referencing the Track table, part of the composite primary key for a playlist track. | System |

---
## Table: `Track`
**Rows:** 3503 | **Health Score:** 97.5/100

| Column | Type | Null % | Unique % | Description | Tags |
|---|---|---|---|---|---|
| `TrackId` | INTEGER | 0% | 0% | Unique identifier for the track. | System |
| `Name` | NVARCHAR(200) | 0% | 0% | Name of the track. |  |
| `AlbumId` | INTEGER | 0% | 0% | Foreign key referencing the Album table, indicating the album the track belongs to. | System |
| `MediaTypeId` | INTEGER | 0% | 0% | Foreign key referencing the MediaType table, indicating the media type of the track. | System |
| `GenreId` | INTEGER | 0% | 0% | Foreign key referencing the Genre table, indicating the genre of the track. | System |
| `Composer` | NVARCHAR(220) | 0% | 0% | Composer of the track. |  |
| `Milliseconds` | INTEGER | 0% | 0% | Length of the track in milliseconds. |  |
| `Bytes` | INTEGER | 0% | 0% | Size of the track in bytes. |  |
| `UnitPrice` | NUMERIC(10, 2) | 0% | 0% | Unit price of the track. |  |

---
