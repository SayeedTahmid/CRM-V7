# Integration Tests with Firebase Emulator

This directory contains tests that use the Firebase emulator suite for:

1. Authentication token verification
2. Firestore operations
3. Tenant isolation testing

## Setup

1. Ensure emulators are running:
```bash
firebase emulators:start
```

2. Create test data (only needed once):
```bash
python tests/create_test_data.py
```

3. Run tests:
```bash
pytest tests/test_with_emulator.py -v
```

## Test Data

The test data script creates:

### Users
- admin@example.com (role: admin, tenant: default)
- manager@example.com (role: manager, tenant: tenant-a) 
- user@example.com (role: user, tenant: tenant-a)

All test users have password: test1234

### Customers 
- Tenant A:
  - Acme Corp
  - Beta Industries
- Tenant B:
  - Gamma Services

## Test Coverage

1. Health Check
   - Verifies emulator connection
   - Checks auth settings

2. Authentication
   - Verifies token requirement
   - Tests tenant isolation

3. Customer Operations  
   - Create/read with tenant isolation
   - Verify permissions
   - Data validation

## Tips

- Tests force emulator mode via environment variables
- Auth tokens are not validated in emulator (any token works)
- Test data persists between emulator restarts
- Clear data by restarting emulators