# API Documentation

## Base URL
```
http://YOUR_SERVER_IP:5000/api
```

## Authentication
Currently, the API is open (no authentication). For production, implement JWT tokens.

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 2. Register Vehicle

Register a new vehicle with passes.

**Endpoint:** `POST /api/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "plate_number": "ABC-1234",
  "car_type": "Sedan",
  "email": "john@example.com",
  "phone_number": "+20 1234567890",
  "passes": 5
}
```

**Field Validation:**
- `name`: String, min 2 characters
- `plate_number`: String, must contain letters and numbers
- `car_type`: One of: Sedan, SUV, Hatchback, Truck, Electric
- `email`: Valid email format
- `phone_number`: Valid phone number (min 10 digits)
- `passes`: Integer between 5-10

**Success Response (201):**
```json
{
  "message": "Vehicle registered successfully",
  "data": {
    "plate_number": "ABC1234",
    "name": "John Doe",
    "car_type": "Sedan",
    "email": "john@example.com",
    "phone_number": "+20 1234567890",
    "total_passes": 5,
    "remaining_passes": 5,
    "registered_at": "2025-01-15T10:30:00.000Z",
    "status": "active"
  }
}
```

**Error Responses:**

400 - Validation Error:
```json
{
  "error": "Invalid email format"
}
```

409 - Already Exists:
```json
{
  "error": "Vehicle already registered",
  "plate_number": "ABC1234"
}
```

---

### 3. Verify Vehicle

Verify if vehicle is authorized to enter (called by Raspberry Pi).

**Endpoint:** `POST /api/verify`

**Request Body:**
```json
{
  "plate_number": "ABC1234"
}
```

**Success Response (200) - Authorized:**
```json
{
  "authorized": true,
  "message": "Access granted",
  "name": "John Doe",
  "remaining_passes": 5,
  "car_type": "Sedan"
}
```

**Success Response (200) - Not Authorized:**
```json
{
  "authorized": false,
  "message": "No remaining passes",
  "name": "John Doe",
  "remaining_passes": 0
}
```

**Success Response (200) - Not Registered:**
```json
{
  "authorized": false,
  "message": "Vehicle not registered"
}
```

---

### 4. Deduct Pass

Deduct one pass after successful entry (called by Raspberry Pi).

**Endpoint:** `POST /api/deduct-pass`

**Request Body:**
```json
{
  "plate_number": "ABC1234"
}
```

**Success Response (200):**
```json
{
  "message": "Pass deducted successfully",
  "remaining_passes": 4
}
```

**Error Responses:**

404 - Vehicle Not Found:
```json
{
  "error": "Vehicle not found"
}
```

---

### 5. Get Vehicle Information

Get detailed information about a specific vehicle.

**Endpoint:** `GET /api/vehicle/{plate_number}`

**Example:** `GET /api/vehicle/ABC1234`

**Success Response (200):**
```json
{
  "data": {
    "plate_number": "ABC1234",
    "name": "John Doe",
    "car_type": "Sedan",
    "email": "john@example.com",
    "phone_number": "+20 1234567890",
    "total_passes": 5,
    "remaining_passes": 4,
    "registered_at": "2025-01-15T10:30:00.000Z",
    "status": "active"
  }
}
```

**Error Response (404):**
```json
{
  "error": "Vehicle not found"
}
```

---

### 6. List All Vehicles

Get a list of all registered vehicles.

**Endpoint:** `GET /api/vehicles`

**Success Response (200):**
```json
{
  "data": [
    {
      "plate_number": "ABC1234",
      "name": "John Doe",
      "car_type": "Sedan",
      "remaining_passes": 4,
      "status": "active"
    },
    {
      "plate_number": "XYZ5678",
      "name": "Jane Smith",
      "car_type": "SUV",
      "remaining_passes": 0,
      "status": "active"
    }
  ],
  "count": 2
}
```

---

### 7. Add Passes

Add more passes to an existing vehicle.

**Endpoint:** `POST /api/add-passes`

**Request Body:**
```json
{
  "plate_number": "ABC1234",
  "passes": 5
}
```

**Success Response (200):**
```json
{
  "message": "Passes added successfully",
  "remaining_passes": 9
}
```

**Error Responses:**

400 - Invalid Input:
```json
{
  "error": "Invalid input"
}
```

404 - Vehicle Not Found:
```json
{
  "error": "Vehicle not found"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently not implemented. Recommended for production:
- 100 requests per minute per IP
- Use Flask-Limiter

---

## CORS

CORS is enabled for all origins (*). Configure in production:
```python
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

---

## Example Usage

### cURL Examples

**Register Vehicle:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "plate_number": "ABC-1234",
    "car_type": "Sedan",
    "email": "john@example.com",
    "phone_number": "+20 1234567890",
    "passes": 5
  }'
```

**Verify Vehicle:**
```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"plate_number": "ABC1234"}'
```

**List Vehicles:**
```bash
curl http://localhost:5000/api/vehicles
```

### Python Example

```python
import requests

API_URL = "http://localhost:5000/api"

# Register vehicle
response = requests.post(f"{API_URL}/register", json={
    "name": "John Doe",
    "plate_number": "ABC-1234",
    "car_type": "Sedan",
    "email": "john@example.com",
    "phone_number": "+20 1234567890",
    "passes": 5
})

print(response.json())

# Verify vehicle
response = requests.post(f"{API_URL}/verify", json={
    "plate_number": "ABC1234"
})

print(response.json())
```

### JavaScript Example

```javascript
const API_URL = 'http://localhost:5000/api';

// Register vehicle
async function registerVehicle(data) {
  const response = await fetch(`${API_URL}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  return await response.json();
}

// Verify vehicle
async function verifyVehicle(plateNumber) {
  const response = await fetch(`${API_URL}/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ plate_number: plateNumber })
  });

  return await response.json();
}
```

---

## WebSocket Support (Future)

Real-time updates for:
- Vehicle entry/exit events
- Pass usage notifications
- System status

Implementation planned using Flask-SocketIO.
