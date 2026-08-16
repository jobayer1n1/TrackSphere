# Strategy Pattern

In TrackSphere, the Strategy pattern is used to encapsulate delivery assignment algorithms behind a common interface.

## Intent

Choose a delivery assignment algorithm at runtime without changing the assignment workflow.

## Implementation

- `app.application.assignments.strategy.AssignmentStrategy` defines the strategy interface.
- `NearestDriverStrategy`, `LeastBusyDriverStrategy`, and `CapacityBasedStrategy` are concrete strategies.
- `app.application.assignments.assignment_service.AssignmentService` receives a strategy instance and delegates driver selection to it.

## Benefits

- Assignment logic is decoupled from the service layer.
- New strategies can be added without modifying existing assignment code.
- The service can switch strategies at runtime using `set_strategy()`.

## Example

```python
from app.application.assignments import AssignmentService, LeastBusyDriverStrategy
from app.repositories.assignments import AssignmentRepository

service = AssignmentService(LeastBusyDriverStrategy(), AssignmentRepository(db_session))
assignment = service.assign(delivery, available_drivers)
```
