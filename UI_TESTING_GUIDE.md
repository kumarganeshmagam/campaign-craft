# CampaignCraft - Playwright UI Testing Guide

## 🎬 Overview

This guide explains how to run comprehensive Playwright UI tests in **HEADED MODE** with screenshots. This allows you to visually watch the tests execute and identify any UI bugs in real-time.

### ✨ Key Features

- ✅ **Headed Mode Browser**: See the browser window open and watch tests run
- 📸 **Automatic Screenshots**: Every major step captures a screenshot for debugging
- 📝 **Detailed Logging**: Console and file logging with timestamps
- 🎯 **10 Comprehensive Tests**:
  1. Backend health check
  2. API endpoint validation
  3. Frontend landing page rendering
  4. Input field validation
  5. Full campaign submission flow
  6. Tab navigation
  7. Generate content button
  8. Responsive design (mobile, tablet, desktop)
  9. Error handling
  10. Page load performance

---

## 🚀 Quick Start

### Option 1: Batch File (Easiest)
```powershell
cd e:\AI\campaign-craft
run_ui_tests.bat
```

### Option 2: PowerShell Script (Direct)
```powershell
cd e:\AI\campaign-craft
.\run_ui_tests.ps1
```

### Option 3: Manual Python Command
```powershell
cd e:\AI\campaign-craft\backend
python -m pytest test_ui_headed.py -v -s
```

---

## 📊 What Happens During Testing

### Phase 1: Startup (30 seconds)
1. ✅ Kills any existing backend/frontend processes
2. ✅ Starts FastAPI backend on http://127.0.0.1:8000
3. ✅ Starts Vite frontend on http://localhost:3000
4. ✅ Waits for both services to be fully ready

### Phase 2: Automated Tests (3-5 minutes)
Browser window opens and you'll see:
- Landing page loads
- Campaign form interaction
- Button clicks and submissions
- Real-time data streaming
- Tab navigation
- Responsive layout checks

### Phase 3: Results (Automatic)
- ✅ All tests complete
- 📸 Screenshots saved to `logs/screenshots/`
- 📝 Detailed logs saved to `logs/ui_tests.log`
- 🔄 Services keep running for manual testing

---

## 📸 Screenshots

All screenshots are automatically saved to:
```
e:\AI\campaign-craft\logs\screenshots\
```

Screenshot naming format:
```
YYYYMMDD_HHMMSS_test_name.png
```

Example screenshots:
- `20251114_143022_01_landing_page.png` - Initial landing page
- `20251114_143032_05_form_filled.png` - Form with input
- `20251114_143035_05_campaign_results.png` - Campaign results with tabs
- `20251114_143051_08_responsive_Mobile.png` - Mobile responsive test

---

## 📝 Logs

### Main Test Log
```
e:\AI\campaign-craft\logs\ui_tests.log
```

View recent test results:
```powershell
Get-Content "e:\AI\campaign-craft\logs\ui_tests.log" -Tail 50
```

### Service Logs
- **Backend**: `logs\backend_startup.log`
- **Backend Errors**: `logs\backend_error.log`
- **Frontend**: `logs\frontend_startup.log`
- **Frontend Errors**: `logs\frontend_error.log`

---

## 🔍 Test Details

### Test 1: Backend Health Check
- **What**: Verifies backend API is responding
- **How**: Makes GET request to `http://127.0.0.1:8000/docs`
- **Success**: HTTP 200 response
- **Duration**: < 1 second

### Test 2: Start Campaign API
- **What**: Tests campaign creation endpoint
- **How**: POSTs JSON payload with campaign topic
- **Checks**: Response includes `campaign_id` and `stream_url`
- **Duration**: < 2 seconds

### Test 3: Frontend Landing Page
- **What**: Verifies frontend loads and displays landing page
- **How**: Navigates to http://localhost:3000
- **Checks**:
  - Main title visible
  - Input field present
  - Start Campaign button present
  - Suggestions text visible
- **Screenshot**: `01_landing_page.png`
- **Duration**: 2-3 seconds

### Test 4: Input Validation
- **What**: Tests form input field behavior
- **How**: Tests enable/disable state of submit button
- **Checks**:
  - Button disabled when input empty
  - Button enabled when text entered
  - Button disabled when input cleared
- **Duration**: 1-2 seconds

### Test 5: Campaign Submission Flow (Long Running)
- **What**: Full end-to-end campaign creation
- **How**: 
  - Fills input with campaign topic
  - Clicks Start Campaign button
  - Waits for streaming responses
  - Checks for campaign results
- **Timeout**: 30 seconds
- **Screenshots**:
  - `05_form_filled.png` - After form input
  - `05_after_submit.png` - After button click
  - `05_campaign_results.png` - Campaign dashboard
- **Duration**: 15-30 seconds

### Test 6: Tab Navigation
- **What**: Tests campaign dashboard tab switching
- **How**: Clicks each tab (Plan, Use Cases, Target, Proposals)
- **Checks**: Tabs are clickable and content displays
- **Screenshots**: One per tab
- **Duration**: 3-5 seconds

### Test 7: Generate Content Button
- **What**: Tests content generation button
- **How**: Locates and clicks "Generate Campaign Content" button
- **Duration**: 1-2 seconds

### Test 8: Responsive Design
- **What**: Tests UI at different viewport sizes
- **Sizes Tested**:
  - Mobile: 375×667
  - Tablet: 768×1024
  - Desktop: 1400×900
- **Checks**: All elements render correctly at each size
- **Duration**: 5-10 seconds

### Test 9: Error Handling
- **What**: Checks for JavaScript errors
- **How**: Monitors browser console for errors
- **Duration**: 2-3 seconds

### Test 10: Page Load Performance
- **What**: Measures frontend load time
- **Threshold**: Must load in < 5 seconds
- **Duration**: 2-5 seconds

---

## 🐛 Debugging Failed Tests

### If Tests Fail:

1. **Check the screenshots**:
   ```
   open e:\AI\campaign-craft\logs\screenshots\
   ```
   Look for error screenshots (ending in `_error.png`)

2. **Review the logs**:
   ```powershell
   Get-Content "e:\AI\campaign-craft\logs\ui_tests.log" | Select-String "ERROR|FAILED"
   ```

3. **Check service logs**:
   ```powershell
   # Backend errors
   Get-Content "e:\AI\campaign-craft\logs\backend_error.log" -Tail 20
   
   # Frontend errors
   Get-Content "e:\AI\campaign-craft\logs\frontend_error.log" -Tail 20
   ```

4. **Run with Debug output**:
   ```powershell
   .\run_ui_tests.ps1 -Debug
   ```

### Common Issues:

| Issue | Solution |
|-------|----------|
| **Port already in use** | Script auto-kills processes, but if error persists: `taskkill /F /IM python.exe` |
| **Backend not starting** | Check Python installed: `python --version` |
| **Frontend not starting** | Check Node installed: `node --version` |
| **Tests timeout** | Services may be slow, check logs for errors |
| **No screenshots** | Check that `logs/screenshots/` directory was created |

---

## 🎛️ Advanced Usage

### Run Only Specific Tests
```powershell
cd e:\AI\campaign-craft\backend

# Run only landing page test
pytest test_ui_headed.py::TestCampaignCraftUI::test_03_frontend_landing_page -v -s

# Run only campaign submission test
pytest test_ui_headed.py::TestCampaignCraftUI::test_05_campaign_submission_flow -v -s
```

### Run in Headless Mode
```powershell
# Edit test_ui_headed.py and change:
# HEADED = False  # instead of True
```

### Slow Down Execution
```powershell
# Edit test_ui_headed.py and increase:
# SLOW_MO = 1000  # milliseconds (default 500)
```

### Run with Coverage
```powershell
cd e:\AI\campaign-craft\backend
pytest test_ui_headed.py --cov --cov-report=html
```

---

## 📋 Manual Testing While Services Run

After tests complete, services remain running. You can manually test:

### Test Backend API
```powershell
curl.exe http://127.0.0.1:8000/docs
```

### Test Frontend
Open browser to: **http://localhost:3000**

### Test Campaign Creation
```powershell
$body = @{
    topic = "Your campaign topic here"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/start-campaign" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

---

## 🛑 Stopping Services

Press **Ctrl+C** in the terminal to:
1. Stop the test run
2. Stop the backend server
3. Stop the frontend server

All services will shut down gracefully.

---

## 📊 Expected Output

```
======================================================================
🎬 STARTING CAMPAIGNCRAFT UI TEST SUITE - HEADED MODE
======================================================================
📸 Screenshots will be saved to: e:\AI\campaign-craft\logs\screenshots
📝 Logs will be saved to: e:\AI\campaign-craft\logs\ui_tests.log
======================================================================

[14:30:22] 🧹 CLEANUP: Killing old processes...
[14:30:24] ✅ Cleanup complete

[14:30:24] 🚀 STARTING BACKEND SERVER...
[14:30:25] Backend process started (PID: 12345)
[14:30:27] ✅ Backend is ready (http://127.0.0.1:8000)

[14:30:27] 🚀 STARTING FRONTEND SERVER...
[14:30:31] ✅ Frontend is ready (http://localhost:3000)

[14:30:31] 🎬 RUNNING PLAYWRIGHT UI TESTS - HEADED MODE
[14:30:32] 📸 Screenshots will be saved to: ./logs/screenshots
[14:30:32] Starting test execution...

===== test session starts =====
collected 10 items

test_ui_headed.py::TestCampaignCraftUI::test_01_backend_health PASSED
test_ui_headed.py::TestCampaignCraftUI::test_02_start_campaign_api PASSED
test_ui_headed.py::TestCampaignCraftUI::test_03_frontend_landing_page PASSED
test_ui_headed.py::TestCampaignCraftUI::test_04_input_validation PASSED
test_ui_headed.py::TestCampaignCraftUI::test_05_campaign_submission_flow PASSED
test_ui_headed.py::TestCampaignCraftUI::test_06_tab_navigation PASSED
test_ui_headed.py::TestCampaignCraftUI::test_07_generate_content_button PASSED
test_ui_headed.py::TestCampaignCraftUI::test_08_responsive_design PASSED
test_ui_headed.py::TestCampaignCraftUI::test_09_error_handling PASSED
test_ui_headed.py::TestCampaignCraftUI::test_10_page_load_performance PASSED

===== 10 passed in 234.56s =====

======================================================================
✅ TEST EXECUTION COMPLETE
✅ All tests PASSED!
📸 Screenshots directory: e:\AI\campaign-craft\logs\screenshots
📝 Test log file: e:\AI\campaign-craft\logs\ui_tests.log
======================================================================

🔄 KEEPING SERVICES RUNNING FOR MANUAL TESTING

Backend running on: http://127.0.0.1:8000
Frontend running on: http://localhost:3000
API Docs on: http://127.0.0.1:8000/docs

Press Ctrl+C to stop all services
```

---

## 🎯 Next Steps

1. ✅ Run tests: `run_ui_tests.bat` or `.\run_ui_tests.ps1`
2. ✅ Watch the browser execute tests automatically
3. ✅ Review screenshots in `logs/screenshots/`
4. ✅ Check logs in `logs/ui_tests.log`
5. ✅ Fix any bugs found
6. ✅ Re-run tests to verify fixes
7. ✅ Manually test in the open browser while services run

---

## 📞 Support

If tests fail:
1. Check the error screenshots in `logs/screenshots/`
2. Review `logs/ui_tests.log` for detailed error messages
3. Check `logs/backend_error.log` for backend issues
4. Check `logs/frontend_error.log` for frontend issues
5. Verify ports 8000 and 3000 are available
6. Run with `-Debug` flag for more verbose output

---

## 🎓 Learning Resources

- [Playwright Documentation](https://playwright.dev/)
- [Pytest with Playwright](https://playwright.dev/python/docs/pytest)
- [Async Testing in Python](https://docs.pytest.org/en/stable/how-to/fixtures.html#async-fixtures)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)

---

**Ready to test? Run:** `run_ui_tests.bat` 🚀
