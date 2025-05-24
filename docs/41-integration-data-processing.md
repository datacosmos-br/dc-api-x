# Data Processing Integration

> *"Data is the new oil - but like oil, it needs refining to be valuable."*
> This guide explores how DCApiX integrates with powerful data processing
> libraries to transform raw data into actionable insights.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [40 - Integration: Robot Framework](40-integration-robot-framework.md) | **41 - Integration: Data Processing** | [42 - Integration: Oracle OCI](42-integration-oracle-oci.md) |

---

## 1. Overview

DCApiX provides seamless integration with industry-standard data processing libraries, enabling powerful data manipulation, analysis, and visualization capabilities. This guide covers the integration with three key libraries:

* **pandas** – For data manipulation and analysis
* **NumPy** – For numerical computing and array operations
* **numba** – For high-performance computing with just-in-time compilation

---

## 2. pandas Integration

[pandas](https://pandas.pydata.org/) is a fast, powerful, flexible, and easy-to-use open-source data analysis and manipulation tool built on top of Python. DCApiX leverages pandas for:

### 2.1 Data Transformation

```python
import pandas as pd
from dc_api_x import ApiClient

# Retrieve data from an API
client = ApiClient(url="https://api.example.com")
response = client.get("orders")

# Convert to DataFrame
df = pd.DataFrame(response.data)

# Data transformation
df['total'] = df['price'] * df['quantity']
df['order_date'] = pd.to_datetime(df['order_date'])
monthly_sales = df.resample('M', on='order_date')['total'].sum()
```

### 2.2 Data Export

```python
# Export to various formats
df.to_csv("orders.csv", index=False)
df.to_excel("orders.xlsx", sheet_name="Orders")
df.to_json("orders.json", orient="records")
```

### 2.3 Advanced Analytics

```python
# Group by and aggregate
product_analysis = df.groupby('product_id').agg({
    'total': 'sum',
    'quantity': 'sum',
    'order_id': 'count'
}).rename(columns={'order_id': 'num_orders'})

# Pivot tables
pivot = df.pivot_table(
    values='total',
    index='product_category',
    columns='region',
    aggfunc='sum',
    fill_value=0
)
```

---

## 3. NumPy Integration

[NumPy](https://numpy.org/) is the fundamental package for scientific computing in Python. DCApiX uses NumPy for:

### 3.1 Efficient Array Operations

```python
import numpy as np
from dc_api_x import get_adapter

# Get data from a database
db = get_adapter("oracle_db")
data = db.query("SELECT value FROM measurements WHERE sensor_id = :id", {"id": 1})

# Convert to NumPy array
values = np.array([row[0] for row in data])

# Statistical analysis
mean = np.mean(values)
std_dev = np.std(values)
percentile_95 = np.percentile(values, 95)

# Filtering
anomalies = values[values > mean + 2*std_dev]
```

### 3.2 Mathematical Operations

```python
# Matrix operations
matrix_a = np.array(db.query_as_list("SELECT * FROM matrix_a"))
matrix_b = np.array(db.query_as_list("SELECT * FROM matrix_b"))

# Matrix multiplication
result = np.matmul(matrix_a, matrix_b)

# Solve linear equation
solution = np.linalg.solve(matrix_a, vector_b)
```

---

## 4. numba Integration

[numba](https://numba.pydata.org/) is a JIT compiler that translates Python functions to optimized machine code at runtime. DCApiX uses numba for:

### 4.1 Accelerating Numerical Functions

```python
from numba import jit
import numpy as np

@jit(nopython=True)
def calculate_distance_matrix(points):
    """Calculate the distance matrix between all points.

    Args:
        points: Array of shape (n, d) with n points in d dimensions

    Returns:
        Distance matrix of shape (n, n)
    """
    n = len(points)
    result = np.empty((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(n):
            result[i, j] = np.sqrt(np.sum((points[i] - points[j])**2))

    return result

# Use in DCApiX
def process_locations(data):
    points = np.array(data)
    distances = calculate_distance_matrix(points)
    return distances
```

### 4.2 Parallel Processing

```python
from numba import prange, jit

@jit(nopython=True, parallel=True)
def parallel_process(data, threshold):
    """Process data in parallel using numba."""
    n = len(data)
    result = np.empty(n, dtype=np.float64)

    for i in prange(n):
        # Complex computation that benefits from parallelization
        result[i] = complex_calculation(data[i], threshold)

    return result
```

---

## 5. Integration Example: Complete ETL Pipeline

Here's a complete example of using all three libraries together in a DCApiX data processing workflow:

```python
import dc_api_x as apix
import pandas as pd
import numpy as np
from numba import jit
import matplotlib.pyplot as plt

# JIT-compiled processing function
@jit(nopython=True)
def process_time_series(data, window_size):
    """Calculate moving averages and identify anomalies."""
    n = len(data)
    result = np.zeros(n, dtype=np.float64)
    anomalies = np.zeros(n, dtype=np.bool_)

    # Calculate moving average
    for i in range(n):
        start = max(0, i - window_size)
        result[i] = np.mean(data[start:i+1])

    # Detect anomalies (values more than 3 std devs from moving avg)
    for i in range(window_size, n):
        window = data[i-window_size:i]
        std = np.std(window)
        if abs(data[i] - result[i]) > 3 * std:
            anomalies[i] = True

    return result, anomalies

# Main ETL function
def sensor_data_etl(config):
    """Extract, transform, and load sensor data."""
    # Extract: Get data from API
    client = apix.ApiClient(url=config.api_url)
    response = client.get("sensors/readings", params={
        "start_date": config.start_date,
        "end_date": config.end_date,
        "sensor_id": config.sensor_id
    })

    # Transform: Convert to DataFrame and process
    df = pd.DataFrame(response.data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index()

    # Convert to NumPy for numerical processing
    values = df['value'].to_numpy()

    # Process with numba for speed
    smoothed, anomalies = process_time_series(values, window_size=24)

    # Add processed data back to DataFrame
    df['smoothed'] = smoothed
    df['is_anomaly'] = anomalies

    # Calculate summary statistics
    hourly_stats = df.resample('H').agg({
        'value': ['mean', 'min', 'max', 'std'],
        'is_anomaly': 'sum'
    })

    # Load: Store processed data
    db = apix.get_adapter("oracle_db")

    # Save summary to database
    for idx, row in hourly_stats.iterrows():
        db.execute(
            "INSERT INTO sensor_stats VALUES (:time, :sensor, :mean, :min, :max, :std, :anomalies)",
            {
                "time": idx.isoformat(),
                "sensor": config.sensor_id,
                "mean": row[('value', 'mean')],
                "min": row[('value', 'min')],
                "max": row[('value', 'max')],
                "std": row[('value', 'std')],
                "anomalies": int(row[('is_anomaly', 'sum')])
            }
        )

    # Save anomalies for alerting
    anomaly_records = df[df['is_anomaly']].reset_index()
    for _, row in anomaly_records.iterrows():
        db.execute(
            "INSERT INTO sensor_anomalies VALUES (:time, :sensor, :value, :expected)",
            {
                "time": row['timestamp'].isoformat(),
                "sensor": config.sensor_id,
                "value": row['value'],
                "expected": row['smoothed']
            }
        )

    return {
        "total_records": len(df),
        "anomalies_detected": anomalies.sum(),
        "processing_complete": True
    }
```

---

## 6. Best Practices

When integrating data processing libraries with DCApiX:

* **Memory Management** – Use chunking for large datasets to avoid memory issues
* **Error Handling** – Implement robust error handling for data processing operations
* **Performance Optimization** – Profile your code to identify bottlenecks
* **Type Safety** – Use type hints to maintain compatibility with mypy
* **Serialization** – Be careful with custom objects that may not serialize properly

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries for data processing
* [40 - Integration: Robot Framework](40-integration-robot-framework.md) - Test automation
* [42 - Integration: Oracle OCI](42-integration-oracle-oci.md) - Oracle Cloud Integration
