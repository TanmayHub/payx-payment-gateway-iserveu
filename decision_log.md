# iSUpayX Decision Log

## Approach & Prioritization

The assessment had a broad payment-gateway specification, so I prioritized the
requirements that directly affect transaction correctness and the supplied
assessment tests.

Priority order:

1. Transaction API
2. Five-layer validation pipeline
3. Database/domain modeling
4. Authentication
5. Idempotency
6. Compliance and risk
7. Event publishing
8. Concurrency controls

The implementation uses Python, FastAPI and SQLite because the organizers
confirmed during the hackathon that candidates could use a comfortable
technology stack instead of spending time installing the prescribed Elixir
environment.

## AI Interaction Log

### Example 1
AI initially suggested using the prescribed Elixir/Phoenix stack.
I clarified that the organizers had explicitly allowed candidates to use
their own technology stack. I therefore chose Python/FastAPI.

### Example 2
AI initially suggested PowerShell commands such as `New-Item`.
My environment was Windows Command Prompt, so I changed file creation to
CMD-compatible commands.

### Example 3
The first idempotency test appeared to bypass the business-rule validation.
Investigation showed that the same Idempotency-Key was reused, so the API
correctly returned the previously processed transaction.

### Example 4
SQLite was initially treated as something that needed separate installation.
I verified that Python already included SQLite support through the sqlite3
module.

### Example 5
The database file appeared as an untracked Git file.
I added SQLite database files to `.gitignore` so generated local state is not
committed.

## Validation Layer Analysis

The transaction pipeline contains:

1. Schema
2. Entity
3. Business Rules
4. Compliance
5. Risk

The first validation failure stops further processing.

Schema validates request structure and data types.

Entity validates merchant existence, merchant status, KYC and the enabled
merchant/payment-method relationship.

Business rules validate payment-method and merchant amount limits.

Compliance flags transactions requiring review without necessarily rejecting
them.

Risk evaluates transaction velocity.

## Contradictions Found

### KYC status compatibility

The supplied data contains both `approved` and legacy `verified` KYC states.
The implementation accepts both as valid KYC states.

### Timeout configuration

The specification contains different timeout values in different contexts.
The implementation would treat timeout as configuration rather than hardcoding
an environment-specific value.

### Payment-method relationship

The merchant/payment-method relationship is many-to-many and the association
contains business attributes such as custom fee, enabled state and priority.
Therefore it is modeled as a first-class entity.

## Hidden Dependencies

Merchant and PaymentMethod have a many-to-many relationship through
MerchantPaymentMethod.

The association contains:

- custom_fee_percent
- is_enabled
- priority

These fields affect whether a transaction can use a payment method and how
the payment method is configured for a merchant.

## Architecture Decisions

FastAPI was selected for a lightweight API-only implementation.

SQLite was selected because the assessment is designed around a local database
simulation.

SQLAlchemy provides the persistence layer and keeps database operations
separate from API logic.

Validation is separated into individual modules to make the five-layer
pipeline explicit.

## What I Would Do Differently

With more time I would add a complete event retry queue, dead-letter queue,
distributed locking abstraction, richer transaction state transitions,
structured logging and comprehensive automated concurrency tests.

## Known Limitations

This implementation is an assessment-focused payment simulation rather than a
production payment gateway.

The event bus is in-process rather than distributed.

Retry/DLQ behavior is simplified.

Risk state is maintained in process.

The supplied Elixir test suite cannot directly execute against this Python
implementation; equivalent behavior is implemented and tested using Python.